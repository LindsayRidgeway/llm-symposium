#!/usr/bin/env python3
"""The landing record must be checked against the diff, not believed.

`scripts/landing_reconcile.py` exists because the wake orientation tells each run which paths a
previous wake "claimed" and did not reach `main` — and that claim list is the run's own LAND line,
which the wake instructions require a run to write *early*, before the files exist. A run cut off at
its action cap therefore leaves a LAND line naming files it never wrote, and every later wake reads
those as work that is missing.

Measured on 2026-10-17 over this repository's history: 177 `land(wake)` commits, 22 of which carry a
"Paths this run changed:" line that disagrees with the commit's own diff; of the 155 paths named by
the 37 runs of 10-16 and 10-17, 132 (85%) are at HEAD and the 23 that are not are overwhelmingly
tests and reports — the tail of a run's plan, not lost work.

This test pins the four verdicts on a throwaway git repository, offline, so the tool cannot rot into
a second opinion that nobody checks.
"""

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import landing_reconcile as lr  # noqa: E402

GIT_ENV = {
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@llm-symposium.local",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@llm-symposium.local",
}


def git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        env={**os.environ, **GIT_ENV},
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def land(repo: Path, run_id: str, claimed: list[str]) -> None:
    """Commit the current tree with the lander's message shape."""
    body = "Paths this run changed: " + ", ".join(claimed) + "\n\nArchitecture: Test (Fake)"
    git(repo, "commit", "-q", "--allow-empty", "-a", "-m", f"land(wake): work from run {run_id}", "-m", body)


class LandingReconcileTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.runs = Path(self.tmp.name) / "LLM"
        self.repo.mkdir()
        git(self.repo, "init", "-q", "-b", "main")
        write(self.repo / "a.html", "<html></html>")
        write(self.repo / "keep.txt", "x")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "base")

    def tearDown(self):
        self.tmp.cleanup()

    def report(self, bot: str, run_id: str, land_line: str) -> Path:
        p = self.runs / f"{bot}-bot" / "tick-state" / "runs" / run_id / "report.txt"
        write(p, textwrap.dedent(f"""\
            Working.
            LAND: {land_line}
            Done."""))
        return p

    def test_a_true_record_and_a_false_one_are_told_apart(self):
        # Run 1: the commit lands a.html and its record says so. True record.
        write(self.repo / "a.html", "<html>changed</html>")
        git(self.repo, "add", "-A")
        land(self.repo, "20261017T000000Z-aaaaaaaa", ["a.html"])
        self.report("desi", "20261017T000000Z-aaaaaaaa", "a.html")

        # Run 2: the record claims a test the run never wrote, and the commit landed something else.
        write(self.repo / "b.html", "<html>b</html>")
        git(self.repo, "add", "-A")
        land(self.repo, "20261017T010000Z-bbbbbbbb", ["tests/test_ghost.py", "b.html"])
        self.report("desi", "20261017T010000Z-bbbbbbbb", "tests/test_ghost.py, b.html")

        out = lr.reconcile(self.repo, self.runs)
        self.assertEqual(out["landing_commits"], 2)
        self.assertEqual(out["commits_with_false_record"], 1)
        detail = out["commits_with_false_record_detail"][0]
        self.assertEqual(detail["run_id"], "20261017T010000Z-bbbbbbbb")
        self.assertEqual(detail["claimed_not_landed"], ["tests/test_ghost.py"])

        verdicts = {r["run_id"]: r["verdict"] for r in out["runs"]}
        self.assertEqual(verdicts["20261017T000000Z-aaaaaaaa"], "landed")
        # b.html is on disk, the ghost test is not: partial, which is not the same as missing.
        self.assertEqual(verdicts["20261017T010000Z-bbbbbbbb"], "partial")

    def test_a_path_that_reached_main_under_another_commit_still_counts_as_landed(self):
        # The tree at HEAD is the ground truth, so a path landed by hand or by another run's
        # commit is delivered even when this run's landing commit never touched it.
        self.report("claude", "20261017T020000Z-cccccccc", "a.html, keep.txt")
        out = lr.reconcile(self.repo, self.runs)
        self.assertEqual(out["runs"][0]["verdict"], "landed")

    def test_placeholders_are_not_paths(self):
        for i, line in enumerate(["tbd", "pending", "(not yet decided)", "<filling, in>", "will, follow"]):
            self.report("gemini", f"20261017T03000{i}Z-dddddddd", line)
        out = lr.reconcile(self.repo, self.runs)
        self.assertEqual({r["verdict"] for r in out["runs"]}, {"no-claim"})
        self.assertEqual(out["tally"]["no-claim"], 5)

    def test_a_note_in_the_land_line_is_prose_and_not_a_claimed_path(self):
        """`LAND: a.html (the render check for logo.png)` claims one path, not two.

        Before 2026-11-11 `_norm` split the body on commas and spaces and kept every chunk holding a
        dot, so the note's `logo.png)` was counted as a claim and the run was then accused of naming a
        file it never touched. Desi found this in run 20261109T040837Z-4358d827 and measured two honest
        runs wrongly accused out of 384; he left the fix alone because this script is the engine every
        wake runs through, and it was still live at HEAD two wakes later.
        """
        self.assertEqual(lr._norm("a/b.md (the render check for logo.png)"), ["a/b.md"])
        self.assertEqual(lr._norm("a/b.md [see notes.md], c/d.py"), ["a/b.md", "c/d.py"])
        # An unbalanced note cannot be recognised as one, and must not become a path either.
        self.assertEqual(lr._norm("a/b.md (the render check for logo.png"), ["a/b.md"])
        # The placeholders the 2026-11-07 repair relied on are still placeholders.
        self.assertEqual(lr._norm("(none yet)"), [])

        write(self.repo / "a.html", "<html>changed</html>")
        git(self.repo, "add", "-A")
        land(self.repo, "20261111T050000Z-ffffffff", ["a.html"])
        self.report("gwen", "20261111T050000Z-ffffffff", "a.html (the render check for logo.png)")

        write(self.repo / "keep.txt", "y")
        git(self.repo, "add", "-A")
        land(self.repo, "20261111T050001Z-99999999", ["keep.txt"])
        self.report("gwen", "20261111T050001Z-99999999", "keep.txt [the note names ghost.py]")

        out = lr.reconcile(self.repo, self.runs)
        by_run = {r["run_id"]: r for r in out["runs"]}
        self.assertEqual(by_run["20261111T050000Z-ffffffff"]["verdict"], "landed")
        self.assertEqual(by_run["20261111T050001Z-99999999"]["verdict"], "landed")
        self.assertEqual(out["commits_with_false_record"], 0)

    def test_a_run_with_no_landing_commit_is_unlanded_and_check_fails(self):
        self.report("tarik", "20261017T040000Z-eeeeeeee", "docs/music/never-written.html")
        out = lr.reconcile(self.repo, self.runs)
        self.assertEqual(out["runs"][0]["verdict"], "unlanded")
        with contextlib.redirect_stdout(io.StringIO()):
            rc = lr.main(["--repo", str(self.repo), "--runs-root", str(self.runs), "--check", "--json"])
        self.assertEqual(rc, 1)

    def test_the_real_history_is_measurable(self):
        """Not a fixture: the tool must run against this checkout without a network."""
        out = lr.reconcile(ROOT, Path(os.environ.get("HOME", "~")) / "LLM")
        self.assertGreater(out["landing_commits"], 100)
        self.assertIn("landed", out["tally"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
