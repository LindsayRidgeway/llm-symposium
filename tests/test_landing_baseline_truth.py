#!/usr/bin/env python3
"""Does the recorded baseline tell the truth about main? (2026-11-27, Desi)

The value-queue item `red-tests-on-main` names four closing conditions. Three are met: the
failures were measured live, the one real failure was fixed, and the baseline was re-recorded at
a named commit. The fourth — *a registered test fails when main carries a failure the baseline
does not name* — had no consumer at all until this file: `grep -rn landing-baseline` found the
preflight script and its own tests, and nothing else, so a baseline could name anything and no
landing could notice.

Three things are asserted here, all of them cheap (fixture repositories, a handful of one-line
test files, no real suite run):

  * `--verify-baseline --against REV` names every failure on REV the baseline does not name, and
    exits 1 — proven on a fixture whose "main" carries exactly that (the guard can fail);
  * a name without a recorded reason excuses nothing: the baseline is reported unusable and the
    failure is named. This is the item's "red as weather" defect in its smallest form, and it is
    why `write_baseline()` writes an empty reason for a newly red file rather than absolving it;
  * the baseline committed in this repository passes those checks — no dead names, no unreasoned
    names — so the file on main is held to the contract, not just the machinery.

Run directly:  python3 tests/test_landing_baseline_truth.py
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "landing_suite_check_baseline", ROOT / "scripts" / "landing_suite_check.py"
)
lsc = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(lsc)

PASSING = (
    "import unittest\n\n\nclass T(unittest.TestCase):\n    def test_ok(self):\n        pass\n\n\n"
    "if __name__ == '__main__':\n    unittest.main()\n"
)
FAILING = (
    "import unittest\n\n\nclass T(unittest.TestCase):\n    def test_bad(self):\n"
    "        self.assertEqual(1, 2)\n\n\nif __name__ == '__main__':\n    unittest.main()\n"
)


def fixture(main_b=FAILING):
    """A repository whose tag `them` stands in for main.

    `tests/test_a.py` is PASSING and stays untouched; `tests/test_b.py` carries `main_b` at
    `them` and is left alone afterwards, because every test here measures `them`, not HEAD.
    """
    repo = Path(tempfile.mkdtemp(prefix="landing-baseline-truth-"))
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]

    def run(*args):
        return subprocess.run([*git, *args], cwd=str(repo), capture_output=True, text=True)

    run("init", "-q")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_a.py").write_text(PASSING, encoding="utf8")
    (repo / "tests" / "test_b.py").write_text(main_b, encoding="utf8")
    run("add", "-A")
    run("commit", "-q", "-m", "them")
    run("tag", "them")
    return repo


def baseline_file(repo, failures, reasons=None, commit="them"):
    path = repo / "baseline.json"
    data = {"commit": commit, "measured_at": "2026-11-27T00:00:00Z", "files": 2,
            "seconds": 1.0, "failures": list(failures),
            "reasons": {name: (reasons or {}).get(name, "") for name in failures}}
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf8")
    return path


def invoke(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = lsc.main(argv)
    return code, out.getvalue(), err.getvalue()


def verify(repo, baseline):
    code, out, err = invoke([
        "--verify-baseline", "--against", "them", "--repo", str(repo),
        "--tests-dir", str(repo / "tests"), "--baseline", str(baseline), "--json",
    ])
    return code, (json.loads(out) if out.strip() else None), out, err


class VerifyBaselineCanFailTest(unittest.TestCase):
    """The fourth closing condition, driven end to end on a repository whose main is red."""

    def test_a_failure_on_main_the_baseline_does_not_name_is_refused(self):
        repo = fixture()
        code, report, out, _ = verify(repo, baseline_file(repo, []))
        self.assertEqual(code, 1, "an unnamed failure on main must refuse, not read as weather")
        self.assertEqual(report["failures"], ["test_b.py"])
        self.assertEqual(report["new_failures"], ["test_b.py"])

    def test_the_refusal_names_the_file_rather_than_counting_it(self):
        repo = fixture()
        code, out, _ = invoke([
            "--verify-baseline", "--against", "them", "--repo", str(repo),
            "--tests-dir", str(repo / "tests"),
            "--baseline", str(baseline_file(repo, [])),
        ])
        self.assertEqual(code, 1)
        self.assertIn("test_b.py", out)  # the complaint the item records: a count, no names

    def test_a_named_failure_with_a_reason_is_excused(self):
        repo = fixture()
        baseline = baseline_file(repo, ["test_b.py"], {"test_b.py": "closed-access fixture, re-measure 12-01"})
        code, report, _, _ = verify(repo, baseline)
        self.assertEqual(code, 0)
        self.assertEqual(report["new_failures"], [])
        self.assertEqual(report["baseline_defects"], [])

    def test_a_named_failure_without_a_reason_is_not_excused(self):
        repo = fixture()
        baseline = baseline_file(repo, ["test_b.py"])  # name, but no reason
        code, report, _, _ = verify(repo, baseline)
        self.assertEqual(code, 1)
        self.assertEqual(report["new_failures"], ["test_b.py"])
        self.assertTrue(any("no recorded reason" in p for p in report["baseline_defects"]))

    def test_a_baseline_naming_a_missing_file_is_a_defect_and_excuses_nothing(self):
        repo = fixture(main_b=PASSING)
        baseline = baseline_file(repo, ["test_gone.py"], {"test_gone.py": "was red once"})
        code, report, _, _ = verify(repo, baseline)
        self.assertEqual(code, 0)  # main is clean here, so nothing is unnamed
        self.assertTrue(any("no such test file" in p for p in report["baseline_defects"]))

    def test_no_baseline_means_every_failure_on_main_is_unnamed(self):
        repo = fixture()
        code, report, _, _ = verify(repo, repo / "absent.json")
        self.assertEqual(code, 1)
        self.assertEqual(report["new_failures"], ["test_b.py"])

    def test_a_clean_main_with_no_baseline_is_not_a_failure(self):
        repo = fixture(main_b=PASSING)
        code, report, _, _ = verify(repo, repo / "absent.json")
        self.assertEqual(code, 0)
        self.assertEqual(report["failures"], [])

    def test_stale_baseline_names_are_reported_not_hidden(self):
        repo = fixture(main_b=PASSING)
        baseline = baseline_file(repo, ["test_b.py"], {"test_b.py": "reason on record"})
        code, out, _ = invoke([
            "--verify-baseline", "--against", "them", "--repo", str(repo),
            "--tests-dir", str(repo / "tests"), "--baseline", str(baseline),
        ])
        self.assertEqual(code, 0)
        self.assertIn("stale", out)
        self.assertIn("test_b.py", out)

    def test_verify_without_a_revision_to_verify_is_a_setup_error(self):
        repo = fixture()
        code, _, err = invoke(["--verify-baseline", "--tests-dir", str(repo / "tests"),
                               "--baseline", str(baseline_file(repo, []))])
        self.assertEqual(code, 2)
        self.assertIn("--against", err)


class ExcusedNamesArePrintedTest(unittest.TestCase):
    """The gate's own refusal hides the names it holds; the repository mirror must not.

    Measured 2026-11-27 in `~/LLM/desi-bot/land_runs.py:884,1107`: `len(before)` is formatted and
    `before` — a set of file names — is thrown away. That file is the bot's and a wake may not
    edit it, so the readable half is kept here: a tree that is red for reasons main shares now
    says which files, by name.
    """

    def test_a_failure_main_shares_is_printed_by_name_and_not_only_counted(self):
        repo = fixture(main_b=FAILING)
        # HEAD equals `them` in this fixture, so the tree's own red file is also theirs.
        code, out, _ = invoke(["--against", "them", "--repo", str(repo),
                               "--tests-dir", str(repo / "tests")])
        self.assertEqual(code, 0)
        self.assertIn("excused by name", out)
        self.assertIn("test_b.py", out)


class CommittedBaselineHoldsTheContractTest(unittest.TestCase):
    """The file on main, held to the rule the machinery is tested against."""

    def test_there_is_a_baseline_and_it_names_a_commit(self):
        data = lsc.load_baseline(ROOT / "tests" / "landing-baseline.json")
        self.assertIsNotNone(data, "tests/landing-baseline.json is missing or unreadable")
        self.assertTrue(str(data.get("commit", "")).strip())

    def test_every_name_it_carries_has_a_reason_and_a_file(self):
        data = lsc.load_baseline(ROOT / "tests" / "landing-baseline.json")
        self.assertIsNotNone(data)
        self.assertEqual(lsc.baseline_defects(data, ROOT / "tests"), [])

    def test_a_name_added_without_a_reason_would_fail_this_check(self):
        # The guard's own teeth: the same function, fed the defect, must report it.
        data = {"commit": "x", "failures": ["test_landing_suite_check.py"], "reasons": {}}
        problems = lsc.baseline_defects(data, ROOT / "tests")
        self.assertTrue(any("no recorded reason" in p for p in problems))


class WriteBaselineKeepsReasonsTest(unittest.TestCase):
    def test_a_reason_on_file_survives_a_re_record(self):
        repo = fixture()
        path = baseline_file(repo, ["test_b.py"], {"test_b.py": "known: fixture"})
        rows = [{"file": "test_b.py", "rc": 1, "seconds": 0.1, "tail": ""},
                {"file": "test_a.py", "rc": 0, "seconds": 0.1, "tail": ""}]
        lsc.write_baseline(rows, "them", path)
        data = json.loads(path.read_text(encoding="utf8"))
        self.assertEqual(data["failures"], ["test_b.py"])
        self.assertEqual(data["reasons"]["test_b.py"], "known: fixture")

    def test_a_newly_red_file_is_written_with_no_reason_so_it_excuses_nothing(self):
        repo = fixture()
        path = baseline_file(repo, [])
        rows = [{"file": "test_b.py", "rc": 1, "seconds": 0.1, "tail": ""}]
        lsc.write_baseline(rows, "them", path)
        data = json.loads(path.read_text(encoding="utf8"))
        self.assertEqual(data["reasons"]["test_b.py"], "")
        self.assertTrue(lsc.baseline_defects(data, repo / "tests"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
