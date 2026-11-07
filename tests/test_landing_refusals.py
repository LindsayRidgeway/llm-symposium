#!/usr/bin/env python3
"""Tests for scripts/landing_refusals.py — the reconciliation of refused landings.

Written 2026-10-19 (Dmitri) after finding a refusal on disk (`landing_failed.txt`) whose eight
claimed paths were all on `main`: the file is a verdict that nothing updates, so a later reader
cannot tell a refusal that was made good from one that still stands. These tests hold the four
classifications and the two parsing rules that decide them.
"""

import io
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

    def test_a_space_separated_land_line_is_several_paths_not_one(self):
        # 2026-11-06: the wake template writes `LAND: <paths>`, so a run with four paths fills it
        # with four words. Read as one path, the line is absent from every tree and the row reads
        # `open 0/1 on main` — the real paths are never checked, and 64 rows that had been made good
        # later were recorded as work still missing.
        self.assertEqual(
            lr.claimed_paths("LAND: research/x.json research/x.md agenda/07-disease.md\n"),
            ["research/x.json", "research/x.md", "agenda/07-disease.md"],
        )

    def test_a_mixed_line_splits_on_both(self):
        self.assertEqual(
            lr.claimed_paths("LAND: a.md b/c.py, d.md,  e/f.html\n"),
            ["a.md", "b/c.py", "d.md", "e/f.html"],
        )

    def test_prose_and_bare_words_are_not_paths(self):
        # Splitting on whitespace makes a sentence into several tokens; none of them is a path.
        self.assertEqual(
            lr.claimed_paths("LAND: a.md and the note will follow (R-006 marked Done)\n"),
            ["a.md"],
        )
        self.assertEqual(lr.claimed_paths("LAND: Makefile\n"), [])

    def test_duplicates_are_dropped_and_order_kept(self):
        self.assertEqual(lr.claimed_paths("LAND: b.md a.md b.md a.md\n"), ["b.md", "a.md"])

    def test_a_whole_line_is_not_a_path(self):
        # The exact shape of the bug, as a value: no token may contain a space.
        for p in lr.claimed_paths("LAND: channels/items.jsonl channels/ledger-verdicts/x.md\n"):
            self.assertNotIn(" ", p)
            self.assertTrue(p.startswith("channels/"), p)


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

    def test_a_space_separated_line_can_be_reconciled_rather_than_open(self):
        # The load-bearing consequence of the parse: the same run, the same tree, two verdicts.
        self.refuse(land="LAND: a.md b.md")
        self.touch_repo("a.md", "b.md")
        row = lr.classify(self.run_dir, self.repo)
        self.assertEqual((row["state"], row["on_main"], row["claimed"]), ("reconciled", 2, 2))

    def test_a_space_separated_line_can_be_partial_and_name_what_is_missing(self):
        self.refuse(land="LAND: a.md b.md")
        self.touch_repo("a.md")
        row = lr.classify(self.run_dir, self.repo)
        self.assertEqual((row["state"], row["missing"]), ("partial", ["b.md"]))


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


class CrashTest(unittest.TestCase):
    """Runs that failed before the gate spoke (added 2026-11-06, Dmitri).

    `landing_failed.txt` is the test gate's file. A lander crash writes no file at all, so this
    survey counted 139 refusals while 20 more runs carried `landing_error` in `result.json`, filed
    no item, and sat in no queue. These tests hold the second source of truth.
    """

    def _run(self, tmp, name="20260101T000000Z-eee"):
        run = Path(tmp) / "dmitri-bot" / "tick-state" / "runs" / name
        run.mkdir(parents=True)
        return run

    def test_a_crash_with_no_gate_file_is_found_and_its_land_text_is_the_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = self._run(tmp)
            (run / "result.json").write_text('{"land": "landing_error: name \'a\' is not defined"}')
            (run / "report.txt").write_text("LAND: gone.md\n")
            repo = Path(tmp) / "repo"; repo.mkdir()
            facts = lr.survey([Path(tmp)], repo)
        self.assertEqual(facts["refusals"], 1)
        self.assertEqual(facts["sources"], {"landing_error": 1})
        row = facts["rows"][0]
        self.assertEqual(row["state"], "open")
        self.assertEqual(row["source"], "landing_error")
        self.assertIn("not defined", row["reason"])

    def test_a_landed_run_is_not_a_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = self._run(tmp)
            (run / "result.json").write_text('{"land": "landed"}')
            repo = Path(tmp) / "repo"; repo.mkdir()
            facts = lr.survey([Path(tmp)], repo)
        self.assertEqual(facts["refusals"], 0)

    def test_the_gate_source_still_reads_the_file_and_can_be_asked_for_alone(self):
        with tempfile.TemporaryDirectory() as tmp:
            gated = self._run(tmp, "20260101T000000Z-gate")
            (gated / "landing_failed.txt").write_text("new failures: test_x.py\n")
            (gated / "report.txt").write_text("LAND: a.md\n")
            crash = self._run(tmp, "20260101T010000Z-crash")
            (crash / "result.json").write_text('{"land": "conflict"}')
            repo = Path(tmp) / "repo"; repo.mkdir(); (repo / "a.md").write_text("x")
            both = lr.survey([Path(tmp)], repo)
            gate_only = lr.survey([Path(tmp)], repo, source="gate")
        self.assertEqual(both["refusals"], 2)
        self.assertEqual(gate_only["refusals"], 1)
        self.assertEqual(gate_only["rows"][0]["source"], "gate")
        self.assertEqual(both["counts"], {"reconciled": 1, "no-claim": 1})


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

        def fake_survey(roots, repo, recheck_tests=False, recheck_runner=None, source=""):
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


class UnfiledTest(unittest.TestCase):
    """Added 2026-11-06 (Dmitri): seeing a crashed landing is only half of it — the other half is
    whether any queue can hold it. `--unfiled` is the set difference between the survey and the
    ledger, and these tests hold both halves of it."""

    def row(self, run, state="open", source="conflict", claimed=1, on_main=0, missing=("a.md",)):
        return {"run": run, "bot": "desi-bot", "state": state, "source": source,
                "claimed": claimed, "on_main": on_main, "missing": list(missing), "reason": "x"}

    def test_a_run_the_ledger_names_is_not_unfiled(self):
        rows = [self.row("20260101T000000Z-aaa"), self.row("20260101T000000Z-bbb")]
        ledger = '{"id": "20260101T000000Z-aaa", "summary": "x"}\n'
        self.assertEqual([r["run"] for r in lr.unfiled(rows, ledger)], ["20260101T000000Z-bbb"])

    def test_the_id_counts_wherever_it_appears_not_only_as_a_key(self):
        # A row is filed if the run is named anywhere in the ledger: `id`, `source_run`, or inside a
        # reason string. A field-by-field scan would call this run unfiled and hand it out twice.
        rows = [self.row("20260101T000000Z-aaa")]
        ledger = '{"id": "other", "reason": "recovered from 20260101T000000Z-aaa by hand"}\n'
        self.assertEqual(lr.unfiled(rows, ledger), [])

    def test_an_empty_ledger_names_nothing(self):
        rows = [self.row("20260101T000000Z-aaa")]
        self.assertEqual(len(lr.unfiled(rows, "")), 1)

    def test_actionable_only_drops_what_no_one_can_act_on(self):
        rows = [self.row("r-open", state="open"), self.row("r-partial", state="partial"),
                self.row("r-reconciled", state="reconciled"),
                self.row("r-noclaim", state="no-claim", claimed=0, missing=()),
                self.row("r-open-noclaim", state="open", claimed=0, missing=())]
        got = [r["run"] for r in lr.unfiled(rows, "", actionable_only=True)]
        self.assertEqual(got, ["r-open", "r-partial"])

    def test_the_cli_prints_the_never_named_runs_and_says_when_there_are_none(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        repo = root / "repo"
        (repo / "channels").mkdir(parents=True)
        run = root / "desi-bot" / "tick-state" / "runs" / "20260101T000000Z-aaa"
        run.mkdir(parents=True)
        (run / "result.json").write_text('{"land": "conflict: rebase"}')
        (run / "report.txt").write_text("LAND: a.md\n")
        out = io.StringIO()
        with mock.patch("sys.stdout", out):
            lr.main(["--runs-root", str(root), "--repo", str(repo), "--unfiled"])
        self.assertIn("20260101T000000Z-aaa", out.getvalue())
        self.assertIn("never named in", out.getvalue())
        self.assertIn("0/1 on main  via conflict", out.getvalue())

        # Now file it: the same command has to stop naming it, or the report is noise forever.
        (repo / "channels" / "items.jsonl").write_text('{"id": "20260101T000000Z-aaa"}\n')
        out = io.StringIO()
        with mock.patch("sys.stdout", out):
            lr.main(["--runs-root", str(root), "--repo", str(repo), "--unfiled"])
        self.assertIn("every failed landing on disk is in the ledger", out.getvalue())

    def test_the_actionable_header_counts_against_its_own_total(self):
        # Recorded defect 2026-11-07 (Desi): `--actionable-only` printed "<actionable> of
        # <surveyed>", which reads as "4 of 608 were never named" when 12 were. The filtered count
        # belongs in the numerator only against the never-named total it was filtered from.
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        repo = root / "repo"
        (repo / "channels").mkdir(parents=True)
        runs = root / "desi-bot" / "tick-state" / "runs"
        for run_id, report in (("20260101T000000Z-aaa", "LAND: a.md\n"),
                               ("20260101T000000Z-bbb", "LAND: b.md\n"),
                               ("20260101T000000Z-ccc", "nothing was named\n")):
            d = runs / run_id
            d.mkdir(parents=True)
            (d / "result.json").write_text('{"land": "conflict: rebase"}')
            (d / "report.txt").write_text(report)
        out = io.StringIO()
        with mock.patch("sys.stdout", out):
            lr.main(["--runs-root", str(root), "--repo", str(repo), "--unfiled",
                     "--actionable-only"])
        self.assertIn("2 actionable of 3 never named", out.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
