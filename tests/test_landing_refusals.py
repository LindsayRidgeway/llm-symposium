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
from unittest import mock

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


class RecheckTest(unittest.TestCase):
    """The half of the file that was dead from 2026-10-23 to 2026-11-05.

    `recheck()` and `named_tests()` were written, documented and never reachable from the command
    line: no `--recheck` in the parser, `survey()` called without it, no column in `render()`, and
    no test naming any of them. Twelve green tests covered `classify` and `claimed_paths` and could
    not see it, exactly as twelve green tests covered `channels/retention.py` with no caller. So the
    tests below assert the wiring, not just the functions: a flag that stops being passed fails here.
    """

    def _refused_run(self, tmp, reason="this run's diff introduced new failures: test_a.py"):
        run = Path(tmp) / "dmitri-bot" / "tick-state" / "runs" / "20260101T000000Z-ddd"
        run.mkdir(parents=True)
        (run / "landing_failed.txt").write_text(reason + "\n")
        (run / "report.txt").write_text("LAND: gone.md\n")
        repo = Path(tmp) / "repo"
        (repo / "tests").mkdir(parents=True)
        return run, repo

    def test_the_cli_flag_reaches_survey(self):
        seen = {}

        def fake_survey(roots, repo, recheck_tests=False, recheck_runner=None):
            seen["recheck_tests"] = recheck_tests
            return {"repo": str(repo), "refusals": 0, "counts": {}, "rows": [],
                    "recheck_counts": {}}

        with mock.patch.object(lr, "survey", fake_survey):
            lr.main(["--runs-root", "/tmp", "--repo", "/tmp", "--recheck"])
        self.assertTrue(seen["recheck_tests"])

    def test_without_the_flag_no_test_is_run(self):
        calls = []

        def runner(path, repo):
            calls.append(path.name)
            return 0, "OK"

        with tempfile.TemporaryDirectory() as tmp:
            _, repo = self._refused_run(tmp)
            (repo / "tests" / "test_a.py").write_text("# x\n")
            facts = lr.survey([Path(tmp)], repo, recheck_tests=False, recheck_runner=runner)
        self.assertEqual(calls, [])
        self.assertNotIn("recheck_counts", facts)
        self.assertNotIn("recheck", facts["rows"][0])

    def test_a_blamed_test_that_passes_here_is_green_now(self):
        def runner(path, repo):
            self.assertEqual(path.name, "test_a.py")
            return 0, "Ran 3 tests in 0.1s\n\nOK"

        with tempfile.TemporaryDirectory() as tmp:
            _, repo = self._refused_run(tmp)
            (repo / "tests" / "test_a.py").write_text("# x\n")
            facts = lr.survey([Path(tmp)], repo, recheck_tests=True, recheck_runner=runner)
        row = facts["rows"][0]
        self.assertEqual(row["recheck"], "green-now")
        self.assertEqual(row["tests"], ["test_a.py"])
        self.assertEqual(facts["recheck_counts"], {"green-now": 1})

    def test_a_blamed_test_that_still_fails_is_red_now_and_keeps_its_reason(self):
        def runner(path, repo):
            return 1, "FAIL: test_thing (tests.test_a.Thing)\n---\nRan 3 tests\nFAILED (failures=1)"

        with tempfile.TemporaryDirectory() as tmp:
            _, repo = self._refused_run(tmp)
            (repo / "tests" / "test_a.py").write_text("# x\n")
            facts = lr.survey([Path(tmp)], repo, recheck_tests=True, recheck_runner=runner)
        row = facts["rows"][0]
        self.assertEqual(row["recheck"], "red-now")
        self.assertEqual(row["recheck_detail"][0][1], "red-now")
        self.assertIn("FAIL", row["recheck_detail"][0][2])

    def test_a_blamed_test_that_no_longer_exists_is_gone_without_running_anything(self):
        def runner(path, repo):
            raise AssertionError("a missing test file must not be run")

        with tempfile.TemporaryDirectory() as tmp:
            _, repo = self._refused_run(tmp)
            facts = lr.survey([Path(tmp)], repo, recheck_tests=True, recheck_runner=runner)
        self.assertEqual(facts["rows"][0]["recheck"], "gone")

    def test_a_refusal_naming_no_test_is_untested(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, repo = self._refused_run(tmp, reason="the tree was dirty when the gate looked")
            facts = lr.survey([Path(tmp)], repo, recheck_tests=True)
        self.assertEqual(facts["rows"][0]["recheck"], "untested")

    def test_the_rendered_line_carries_the_recheck_verdict(self):
        facts = {
            "repo": "r", "refusals": 1, "counts": {"open": 1},
            "rows": [{"run": "20260101T000000Z-ddd", "bot": "dmitri-bot", "state": "open",
                      "reason": "new failures: test_a.py", "claimed": 1, "on_main": 0,
                      "missing": ["gone.md"], "tests": ["test_a.py"], "recheck": "red-now",
                      "recheck_detail": [("test_a.py", "red-now", "FAILED (failures=1)")]}],
            "recheck_counts": {"red-now": 1},
        }
        out = lr.render(facts)
        self.assertIn("recheck: red-now", out)
        self.assertIn("test_a.py (red-now): FAILED", out)
        self.assertIn("recheck: red-now 1", out)

    def test_a_mixed_row_names_the_test_that_is_gone(self):
        # The live case that made this test exist: a refusal blaming two tests, one green here and
        # one no longer in the tree, is labelled `green-now` by the precedence in recheck(). Printed
        # without the state word it read as "green" next to a sentence about a missing file.
        facts = {
            "repo": "r", "refusals": 1, "counts": {"open": 1},
            "rows": [{"run": "20261019T010846Z-95b9aa77", "bot": "desi-bot", "state": "open",
                      "reason": "new failures: test_item_ledger.py, test_status_census.py",
                      "claimed": 1, "on_main": 0, "missing": ["x.md"],
                      "tests": ["test_item_ledger.py", "test_status_census.py"],
                      "recheck": "green-now",
                      "recheck_detail": [("test_item_ledger.py", "green-now", "OK"),
                                         ("test_status_census.py", "gone", "not in this checkout")]}],
            "recheck_counts": {"green-now": 1},
        }
        out = lr.render(facts)
        self.assertIn("recheck: green-now", out)
        self.assertIn("test_status_census.py (gone)", out)
        self.assertNotIn("test_item_ledger.py (", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
