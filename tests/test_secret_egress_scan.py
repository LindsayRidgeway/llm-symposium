#!/usr/bin/env python3
"""Pins the RT-4 pre-delivery secret-egress scanner (`scripts/secret_egress_scan.py`).

The point of the scanner is narrow and the tests are written to keep it narrow:

1. it must fire on the *exact bytes* of a configured secret value and on nothing else;
2. it must not fire on a placeholder, a short value, or an unrelated variable;
3. **the alarm must not be the leak** — no value may appear in the console output or the
   JSON report, only the variable name, its length and a digest prefix;
4. the git integration is exercised against a real throwaway repository, because a gate
   whose whole job is to read what git says it changed should be tested against git and
   not against a stub of it.

Written 2026-09-28 (Desi). The last of these is the boundary the deadbolt item asked for
and did not have: the mail adapter redacts, but nothing checked the artefact about to be
published.
"""

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import secret_egress_scan as ses  # noqa: E402

# A generated-looking value with no meaning anywhere; 22 chars, over the 12-char floor.
LEAK = "sk-" + "0123456789abcdef0123"


def _git(repo, *args):
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


class ValueSelectionTests(unittest.TestCase):
    """What counts as a secret is the whole false-positive budget."""

    def test_long_value_under_secret_name_is_considered(self):
        got = ses.secret_values_from_env({"DEMO_API_KEY": LEAK})
        self.assertEqual(got, {"DEMO_API_KEY": LEAK})

    def test_short_value_is_ignored(self):
        self.assertEqual(ses.secret_values_from_env({"DEMO_API_KEY": "abc"}), {})

    def test_unrelated_variable_name_is_ignored(self):
        self.assertEqual(ses.secret_values_from_env({"DEMO_SETTING": LEAK}), {})

    def test_placeholder_is_ignored_even_when_long_and_secret_named(self):
        for placeholder in ("change-me", "<your-token-here>", "xxxxxxxxxxxx", "------------"):
            with self.subTest(placeholder=placeholder):
                self.assertEqual(ses.secret_values_from_env({"DEMO_API_KEY": placeholder}), {})

    def test_include_names_forces_a_mismatched_variable(self):
        got = ses.secret_values_from_env({"MY_PRIVATE": LEAK}, include_names=["MY_PRIVATE"])
        self.assertEqual(got, {"MY_PRIVATE": LEAK})

    def test_fingerprint_is_stable_and_is_not_the_value(self):
        a = ses.fingerprint(LEAK)
        self.assertEqual(a, ses.fingerprint(LEAK))
        self.assertNotIn(LEAK, a)
        self.assertEqual(len(a), 8)


class ScanTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_finds_exact_value_and_reports_name_only(self):
        (self.root / "leaky.txt").write_text(f"before {LEAK} after\n")
        (self.root / "clean.txt").write_text("nothing here\n")
        result = ses.scan([str(self.root)], {"DEMO_API_KEY": LEAK}, root=self.root)
        self.assertFalse(result["clean"])
        self.assertEqual([h["name"] for h in result["hits"]], ["DEMO_API_KEY"])
        blob = json.dumps(result)
        self.assertNotIn(LEAK, blob, "the report itself leaked the value")
        self.assertIn("DEMO_API_KEY", blob)

    def test_clean_tree_is_clean(self):
        (self.root / "a.txt").write_text("ordinary text\n")
        result = ses.scan([str(self.root)], {"DEMO_API_KEY": LEAK}, root=self.root)
        self.assertTrue(result["clean"])
        self.assertEqual(result["hits"], [])

    def test_skips_vcs_and_cache_directories(self):
        buried = self.root / ".git" / "objects"
        buried.mkdir(parents=True)
        (buried / "packed").write_text(LEAK)
        result = ses.scan([str(self.root)], {"DEMO_API_KEY": LEAK}, root=self.root)
        self.assertTrue(result["clean"], "a value inside .git must not fire the gate")

    def test_counts_repeated_occurrences(self):
        (self.root / "twice.txt").write_text(f"{LEAK}\n{LEAK}\n")
        result = ses.scan([str(self.root)], {"DEMO_API_KEY": LEAK}, root=self.root)
        self.assertEqual(result["hits"][0]["occurrences"], 2)


class CliTests(unittest.TestCase):
    """The gate has to be usable as one: exit 1 on a hit, and a written JSON either way."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def _run(self, argv, env):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.dict(os.environ, env, clear=False):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = ses.main(["--root", str(self.root), *argv])
        return code, out.getvalue(), err.getvalue()

    def test_exit_zero_and_json_written_when_clean(self):
        (self.root / "clean.txt").write_text("hello\n")
        target = self.root / "report.json"
        code, _, _ = self._run(["--json", str(target), "clean.txt"], {"DEMO_API_KEY": LEAK})
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(target.read_text())["clean"])

    def test_exit_one_and_no_value_on_stderr_when_hit(self):
        (self.root / "leaky.txt").write_text(f"oops {LEAK}\n")
        code, out, err = self._run(["leaky.txt"], {"DEMO_API_KEY": LEAK})
        self.assertEqual(code, 1)
        self.assertIn("DEMO_API_KEY", err)
        self.assertNotIn(LEAK, out)
        self.assertNotIn(LEAK, err)

    def test_git_changed_mode_catches_an_untracked_leak(self):
        _git(self.root, "init", "-q", "-b", "main")
        _git(self.root, "config", "user.email", "t@example.com")
        _git(self.root, "config", "user.name", "test")
        (self.root / "landed.txt").write_text("already in the tree\n")
        _git(self.root, "add", "landed.txt")
        _git(self.root, "commit", "-q", "-m", "landed")
        (self.root / "about-to-be-delivered.txt").write_text(f"leak {LEAK}\n")
        code, _, err = self._run(["--git-changed"], {"DEMO_API_KEY": LEAK})
        self.assertEqual(code, 1)
        self.assertIn("about-to-be-delivered.txt", err)
        self.assertNotIn(LEAK, err)


class LiveTreeTests(unittest.TestCase):
    """The pre-delivery gate run for real over this repository and this process environment.

    It is a genuine test rather than a fixture: on a machine that holds the commons' secrets,
    a secret that reached a file fails here, at the moment the tests run — which is the moment
    before the work is published. When no secret-like variable is in the environment (a fork,
    a PR, a CI job without the secrets) there is nothing to look for and the test says so and
    passes, rather than pretending to have checked.
    """

    def test_repository_tree_contains_no_environment_secret(self):
        secrets = ses.secret_values_from_env()
        if not secrets:
            self.skipTest("no secret-like variable in this environment")
        result = ses.scan([str(ROOT)], secrets, root=ROOT)
        self.assertTrue(
            result["clean"],
            "a configured secret value is present in a tracked file: "
            + ", ".join(f"{h['name']} in {h['path']}" for h in result["hits"]),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
