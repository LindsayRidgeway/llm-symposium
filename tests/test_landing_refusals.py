#!/usr/bin/env python3
"""Tests for scripts/landing_refusals.py — the reconciliation of refused landings.

Written 2026-10-19 (Dmitri) after finding a refusal on disk (`landing_failed.txt`) whose eight
claimed paths were all on `main`: the file is a verdict that nothing updates, so a later reader
cannot tell a refusal that was made good from one that still stands. These tests hold the four
classifications and the two parsing rules that decide them.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import scripts.landing_refusals as lr  # noqa: E402


class ClaimedPathsTest(unittest.TestCase):
    def test_reads_the_paths_off_a_land_line(self):
        self.assertEqual(
            lr.claimed_paths("STARTING: x\nLAND: a.md, b/c.py\n"),
            ["a.md", "b/c.py"],
        )

    def test_placeholders_are_not_paths(self):
        for text in ("LAND: (none yet)", "LAND: (pending)", "LAND: (nothing yet)", "LAND:"):
            self.assertEqual(lr.claimed_paths(text), [], text)

    def test_the_last_land_line_wins(self):
        # A report is rewritten as the run proceeds, so the last line is what the run finished with.
        text = "LAND: a.md\nLICENSE: x\nLAND: a.md, b.md\n"
        self.assertEqual(lr.claimed_paths(text), ["a.md", "b.md"])

    def test_backticks_and_trailing_full_stop_are_stripped(self):
        self.assertEqual(lr.claimed_paths("LAND: `a.md`, b.md."), ["a.md", "b.md"])

    def test_no_land_line_is_no_claim(self):
        self.assertEqual(lr.claimed_paths("STARTING: thinking\n"), [])


class ClassifyTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        self.run_dir = Path(self.tmp.name) / "desi-bot" / "tick-state" / "runs" / "20260101T000000Z-abc"
        self.run_dir.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def refuse(self, reason="new failures: test_x.py", land=None):
        (self.run_dir / "landing_failed.txt").write_text(reason + "\n")
        if land is not None:
            (self.run_dir / "report.txt").write_text(land + "\n")

    def touch_repo(self, *paths):
        for p in paths:
            full = self.repo / p
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text("x")

    def test_every_claimed_path_on_main_is_reconciled(self):
        self.refuse(land="LAND: a.md, b.md")
        self.touch_repo("a.md", "b.md")
        row = lr.classify(self.run_dir, self.repo)
        self.assertEqual(row["state"], "reconciled")
        self.assertEqual((row["on_main"], row["claimed"]), (2, 2))

    def test_some_on_main_is_partial_and_names_what_is_missing(self):
        self.refuse(land="LAND: a.md, b.md")
        self.touch_repo("a.md")
        row = lr.classify(self.run_dir, self.repo)
        self.assertEqual(row["state"], "partial")
        self.assertEqual(row["missing"], ["b.md"])

    def test_none_on_main_is_open(self):
        self.refuse(land="LAND: a.md")
        row = lr.classify(self.run_dir, self.repo)
        self.assertEqual(row["state"], "open")

    def test_a_refusal_with_nothing_named_is_no_claim(self):
        self.refuse(land="LAND: (none yet)")
        row = lr.classify(self.run_dir, self.repo)
        self.assertEqual(row["state"], "no-claim")

    def test_the_reason_is_carried_so_an_open_row_is_actionable(self):
        self.refuse(reason="new failures: test_drive_bridge_status.py", land="LAND: a.md")
        row = lr.classify(self.run_dir, self.repo)
        self.assertIn("test_drive_bridge_status.py", row["reason"])


class SurveyTest(unittest.TestCase):
    def test_only_run_directories_that_carry_a_refusal_are_counted(self):
        with tempfile.TemporaryDirectory() as tmp:
            runs = Path(tmp) / "desi-bot" / "tick-state" / "runs"
            refused = runs / "20260101T000000Z-aaa"
            refused.mkdir(parents=True)
            (refused / "landing_failed.txt").write_text("new failures: t.py\n")
            (refused / "report.txt").write_text("LAND: a.md\n")
            clean = runs / "20260101T010000Z-bbb"
            clean.mkdir(parents=True)
            (clean / "report.txt").write_text("LAND: a.md\n")
            repo = Path(tmp) / "repo"
            repo.mkdir()
            (repo / "a.md").write_text("x")

            facts = lr.survey([Path(tmp)], repo)
            self.assertEqual(facts["refusals"], 1)
            self.assertEqual(facts["counts"], {"reconciled": 1})
            self.assertEqual(facts["rows"][0]["bot"], "desi-bot")

    def test_strict_exits_non_zero_while_an_open_refusal_stands(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp) / "dmitri-bot" / "tick-state" / "runs" / "20260101T000000Z-ccc"
            run.mkdir(parents=True)
            (run / "landing_failed.txt").write_text("new failures: t.py\n")
            (run / "report.txt").write_text("LAND: gone.md\n")
            repo = Path(tmp) / "repo"
            repo.mkdir()
            self.assertEqual(lr.main(["--runs-root", tmp, "--repo", str(repo), "--strict"]), 1)
            (repo / "gone.md").write_text("x")
            self.assertEqual(lr.main(["--runs-root", tmp, "--repo", str(repo), "--strict"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
