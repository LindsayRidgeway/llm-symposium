#!/usr/bin/env python3
"""The friction pass: a trigger, not a clock, and it must not overwrite or re-trigger itself.

Written 2026-09-26 with `scripts/friction_pass.py`. The three things pinned here are the three
defects that retired the previous runner:

1. it ran on a clock, so it spent four model calls on unchanged material;
2. it wrote `discussions/*-review.md` in mode "w", so a week of runs left one copy;
3. (the new one) a pass that reviews landed work *is itself* landed work — if its own outputs
   count, the first pass makes every later pass think new work exists, and the "trigger" becomes
   the clock again with extra steps.

The git checks run against real throwaway repositories: a trigger's whole job is to read history,
and stubbing git here would test the stub.
"""

import contextlib
import datetime
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import friction_pass as fp  # noqa: E402


def _git(repo, *args):
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True).stdout.strip()


class _Repo:
    """A throwaway git repository with an identity, so the test does not depend on the machine."""

    def __init__(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name)
        _git(self.path, "init", "-q", "-b", "main")
        _git(self.path, "config", "user.email", "t@example.com")
        _git(self.path, "config", "user.name", "test")

    def commit(self, rel, text="x", message="work"):
        f = self.path / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text, encoding="utf-8")
        _git(self.path, "add", rel)
        _git(self.path, "commit", "-q", "-m", message)
        return fp.head_sha(self.path)

    def close(self):
        self.dir.cleanup()


class TriggerTests(unittest.TestCase):
    """A clock run and a no-op run must be distinguishable, and the second run must be a no-op."""

    def setUp(self):
        self.r = _Repo()
        self.addCleanup(self.r.close)

    def test_no_reviews_and_one_commit_is_due(self):
        self.r.commit("docs/page.html", "<p>landed</p>")
        v = fp.due(self.r.path)
        self.assertTrue(v["due"])
        self.assertEqual(v["paths"], ["docs/page.html"])
        self.assertEqual(v["since"], "")           # no predecessor pass: everything is unreviewed
        self.assertIn("never run", v["reason"])

    def test_a_second_pass_on_an_unchanged_tree_is_not_due(self):
        sha = self.r.commit("docs/page.html")
        fp.save_state(self.r.path, {"last_sha": sha})
        v = fp.due(self.r.path)
        self.assertFalse(v["due"])
        self.assertIn("nothing landed", v["reason"])

    def test_work_that_lands_after_a_pass_makes_the_next_pass_due(self):
        first = self.r.commit("docs/page.html")
        fp.save_state(self.r.path, {"last_sha": first})
        self.r.commit("scripts/thing.py", "print(1)")
        v = fp.due(self.r.path)
        self.assertTrue(v["due"])
        self.assertEqual(v["paths"], ["scripts/thing.py"])

    def test_nothing_is_due_in_a_repository_with_no_commits(self):
        v = fp.due(self.r.path)
        self.assertFalse(v["due"])
        self.assertIn("no commits", v["reason"])

    def test_a_marker_that_no_longer_exists_does_not_wedge_the_pass(self):
        """A rewritten history must not turn the trigger into a permanent no-op."""
        self.r.commit("docs/page.html")
        fp.save_state(self.r.path, {"last_sha": "0" * 40})
        v = fp.due(self.r.path)
        self.assertTrue(v["due"])                  # the dead marker was replaced, not obeyed
        self.assertNotEqual(v["since"], "0" * 40)
        self.assertIn("docs/page.html", v["paths"])


class SelfTriggerGuardTests(unittest.TestCase):
    """The pass's own output is not work, and must not make the next pass fire."""

    def setUp(self):
        self.r = _Repo()
        self.addCleanup(self.r.close)

    def test_review_files_and_run_markers_are_excluded(self):
        for rel in fp.REVIEW_FILES:
            self.assertTrue(fp.is_self_output(rel), rel)
        self.assertTrue(fp.is_self_output("runs/friction-pass.json"))
        self.assertTrue(fp.is_self_output("discussions/friction/2026-09-26-abcd1234.md"))
        self.assertTrue(fp.is_self_output("tests/last-verification.txt"))

    def test_real_work_is_not_excluded(self):
        for rel in ("docs/index.html", "scripts/disease_screen.py",
                    "discussions/2026-09-24-the-execution-ratchet-and-the-great-filter.md",
                    "channels/tasks.md"):
            self.assertFalse(fp.is_self_output(rel), rel)

    def test_a_commit_of_only_review_files_is_not_new_work(self):
        sha = self.r.commit("docs/page.html")
        fp.save_state(self.r.path, {"last_sha": sha})
        self.r.commit("discussions/gemini-review.md", "# a review", "review")
        v = fp.due(self.r.path)
        self.assertFalse(v["due"])
        self.assertIn("own output", v["reason"])


class ArchiveTests(unittest.TestCase):
    """Two passes must never share a path, and a pass that reached no model must not advance."""

    def setUp(self):
        self.r = _Repo()
        self.addCleanup(self.r.close)
        for rel in fp.REVIEW_FILES:
            p = self.r.path / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(f"# review of {rel}\n", encoding="utf-8")

    def _stub_steps(self):
        """Replace the two subprocess steps: this test is about the archive, not about the models."""
        self.calls = []

        class _R:
            returncode = 0

        def fake(cmd, cwd):
            self.calls.append(cmd)
            return 0

        fp._run = fake                                    # noqa: SLF001 — the seam the design needs
        return self.calls

    def test_a_pass_archives_one_dated_file_and_records_the_marker(self):
        sha = self.r.commit("docs/page.html")
        self._stub_steps()
        res = fp.run_pass(self.r.path, when=datetime.date(2026, 9, 26))
        self.assertTrue(res["ran"])
        self.assertEqual(res["sections"], 4)
        self.assertEqual(res["archive"], f"discussions/friction/2026-09-26-{fp.short_sha(sha)}.md")
        body = (self.r.path / res["archive"]).read_text(encoding="utf-8")
        self.assertIn(fp.head_sha(self.r.path), body)
        self.assertIn("docs/page.html", body)
        self.assertIn("## gemini", body)
        self.assertEqual(fp.load_state(self.r.path)["last_sha"], fp.head_sha(self.r.path))

    def test_the_archive_path_is_unique_per_commit(self):
        day = datetime.date(2026, 9, 26)
        a = fp.archive_path(self.r.path, day, "a" * 40)
        b = fp.archive_path(self.r.path, day, "b" * 40)
        self.assertNotEqual(a, b)
        self.assertEqual(a, fp.archive_path(self.r.path, day, "a" * 40))

    def test_it_invokes_the_runner_and_the_matrix_and_does_not_reimplement_them(self):
        self.r.commit("docs/page.html")
        calls = self._stub_steps()
        fp.run_pass(self.r.path, when=datetime.date(2026, 9, 26))
        joined = [" ".join(c) for c in calls]
        self.assertTrue(any(fp.RUNNER in c for c in joined), joined)
        self.assertTrue(any(fp.MATRIX in c for c in joined), joined)

    def test_a_pass_that_reached_no_model_does_not_advance_the_marker(self):
        self.r.commit("docs/page.html")
        for rel in fp.REVIEW_FILES:                       # the runner failed: nothing written
            (self.r.path / rel).write_text("", encoding="utf-8")
        self._stub_steps()
        res = fp.run_pass(self.r.path, when=datetime.date(2026, 9, 26))
        self.assertTrue(res["ran"])
        self.assertEqual(res["archive"], "")
        self.assertIn("marker not advanced", res["reason"])
        self.assertNotIn("last_sha", fp.load_state(self.r.path))
        self.assertTrue(fp.due(self.r.path)["due"])        # so the next pass tries again

    def test_dry_run_changes_nothing(self):
        self.r.commit("docs/page.html")
        res = fp.run_pass(self.r.path, dry_run=True, when=datetime.date(2026, 9, 26))
        self.assertFalse(res["ran"])
        self.assertEqual(res["archive"], "")
        self.assertFalse((self.r.path / "discussions" / "friction").exists())
        self.assertFalse((self.r.path / fp.STATE_PATH).exists())

    def test_nothing_to_do_is_not_an_error(self):
        sha = self.r.commit("docs/page.html")
        fp.save_state(self.r.path, {"last_sha": sha})
        res = fp.run_pass(self.r.path, when=datetime.date(2026, 9, 26))
        self.assertFalse(res["ran"])
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):     # a no-op pass must exit 0, not raise or shout
            self.assertEqual(fp.main(["--repo", str(self.r.path)]), 0)
            self.assertEqual(fp.main(["--repo", str(self.r.path), "--check"]), 0)


class CheckModeTests(unittest.TestCase):
    def setUp(self):
        self.r = _Repo()
        self.addCleanup(self.r.close)

    def test_check_reports_and_writes_nothing(self):
        self.r.commit("docs/page.html")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = fp.main(["--repo", str(self.r.path), "--check"])
        self.assertEqual(code, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["due"])
        self.assertEqual(payload["paths"], ["docs/page.html"])
        self.assertFalse((self.r.path / "discussions" / "friction").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
