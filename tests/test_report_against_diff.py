#!/usr/bin/env python3
"""Tests for scripts/report_against_diff.py.

The number this script prints is quoted in a report and acted on, so each test pins one
thing that could make it wrong: a blank line counted as a record, a one-line report read as
an account, a run with no patch counted as work, a runner under a different bot directory.

Run: python3 tests/test_report_against_diff.py   (or `python3 -m unittest tests.test_report_against_diff`)
"""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import report_against_diff as rad  # noqa: E402


def _run(root: Path, bot: str, run_id: str, report: str | None, patch_bytes: int) -> Path:
    run = root / bot / "tick-state" / "runs" / run_id
    run.mkdir(parents=True, exist_ok=True)
    if report is not None:
        (run / "report.txt").write_text(report, encoding="utf-8")
    if patch_bytes:
        (run / "changes.patch").write_text("x" * patch_bytes, encoding="utf-8")
    return run


class NonEmptyLines(unittest.TestCase):
    def test_blank_lines_are_not_a_record(self):
        self.assertEqual(rad.nonempty_lines("\n\n  \n"), [])

    def test_strips_and_keeps_order(self):
        self.assertEqual(rad.nonempty_lines(" a \n\n b\n"), ["a", "b"])


class Classify(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.report = self.tmp / "report.txt"

    def tearDown(self):
        (self.report.unlink() if self.report.exists() else None)

    def test_missing(self):
        self.assertEqual(rad.classify_report(self.report), "missing")

    def test_one_line_is_silent(self):
        self.report.write_text("Started: about to check my queue.\n", encoding="utf-8")
        self.assertEqual(rad.classify_report(self.report), "silent")

    def test_blank_file_is_silent(self):
        self.report.write_text("\n \n", encoding="utf-8")
        self.assertEqual(rad.classify_report(self.report), "silent")

    def test_two_lines_without_land_is_an_account(self):
        self.report.write_text("Done: read two items.\nBoth real.\n", encoding="utf-8")
        self.assertEqual(rad.classify_report(self.report), "account")

    def test_land_line_makes_it_landed(self):
        self.report.write_text("Done: wrote the file.\nLAND: docs/x.md\n", encoding="utf-8")
        self.assertEqual(rad.classify_report(self.report), "landed")

    def test_land_must_start_the_line(self):
        self.report.write_text("Done.\nmy LAND: docs/x.md is not a LAND line\n", encoding="utf-8")
        self.assertEqual(rad.classify_report(self.report), "account")


class Census(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_reads_every_bot_and_ignores_files(self):
        _run(self.tmp, "a-bot", "r1", "Started: x\n", 10)
        _run(self.tmp, "b-bot", "r2", "Done: y\nLAND: p\n", 20)
        (self.tmp / "a-bot" / "tick-state" / "runs" / "not-a-run.txt").write_text("x")
        rows = rad.census(self.tmp)
        self.assertEqual([r["id"] for r in rows], ["r1", "r2"])
        self.assertEqual(rows[0]["bot"], "a-bot")
        self.assertEqual(rows[1]["report"], "landed")

    def test_patch_size_is_read_and_absence_is_zero(self):
        _run(self.tmp, "a-bot", "r1", "Started: x\n", 0)
        _run(self.tmp, "a-bot", "r2", "Started: x\n", 37)
        rows = {r["id"]: r for r in rad.census(self.tmp)}
        self.assertEqual(rows["r1"]["patch_bytes"], 0)
        self.assertEqual(rows["r2"]["patch_bytes"], 37)

    def test_first_line_is_carried_for_listing(self):
        _run(self.tmp, "a-bot", "r1", "\n  Started: checking the queue.\n", 5)
        self.assertEqual(rad.census(self.tmp)[0]["first_line"], "Started: checking the queue.")


class Summary(unittest.TestCase):
    def test_counts_and_share_use_patched_runs_as_the_denominator(self):
        rows = [
            {"id": "a", "bot": "x", "patch_bytes": 10, "report": "silent", "first_line": ""},
            {"id": "b", "bot": "x", "patch_bytes": 10, "report": "landed", "first_line": ""},
            {"id": "c", "bot": "x", "patch_bytes": 0, "report": "silent", "first_line": ""},
            {"id": "d", "bot": "x", "patch_bytes": 0, "report": "missing", "first_line": ""},
        ]
        stats = rad.summarise(rows)
        self.assertEqual(stats["runs"], 4)
        self.assertEqual(stats["runs_with_a_patch"], 2)
        self.assertEqual(stats["silent_with_work"], 1)
        self.assertEqual(stats["silent_with_work_share_of_patched"], 50.0)
        self.assertEqual(stats["by_report"], {"missing": 1, "silent": 2, "account": 0, "landed": 1})

    def test_empty_input_does_not_divide_by_zero(self):
        stats = rad.summarise([])
        self.assertEqual(stats["silent_with_work_share_of_patched"], 0.0)
        self.assertEqual(stats["landed_share_of_patched"], 0.0)


class Cli(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        _run(self.tmp, "a-bot", "r-silent", "Started: looking.\n", 12)
        _run(self.tmp, "b-bot", "r-landed", "Done.\nLAND: p\n", 12)

    def _run_cli(self, *argv):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = rad.main(list(argv))
        return code, buf.getvalue()

    def test_summary_names_the_cell_that_matters(self):
        code, out = self._run_cli("--root", str(self.tmp))
        self.assertEqual(code, 0)
        self.assertIn("silent record, real work   1 of 2", out)

    def test_show_lists_only_that_class(self):
        code, out = self._run_cli("--root", str(self.tmp), "--show", "silent")
        self.assertEqual(code, 0)
        self.assertIn("r-silent", out)
        self.assertNotIn("r-landed", out)

    def test_json_is_parseable_and_carries_the_rows(self):
        code, out = self._run_cli("--root", str(self.tmp), "--json")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(data["summary"]["runs"], 2)
        self.assertEqual({r["id"] for r in data["rows"]}, {"r-silent", "r-landed"})

    def test_missing_root_exits_two(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = rad.main(["--root", str(self.tmp / "nope")])
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main(verbosity=1)
