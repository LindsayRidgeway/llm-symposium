#!/usr/bin/env python3
"""Tests for `scripts/retirement_watch.py`. Offline — no network, no clock.

Why these exist. The instrument's only value is that a red build means "a route is about to
stop answering" and a green one means "it is not" — so every way it could say green wrongly is
pinned here:

  * the calendar table changing shape (a reader that silently parses zero rows would report
    "nothing to act on" forever, which is the failure mode of every watcher nobody watches);
  * a row without an impact cell (unclassified must be loud, not skipped);
  * prefix confusion between `claude-sonnet-4-5` and `claude-sonnet-4-5-20250929` — telling
    those apart is the difference between "the swap was done" and "it was not";
  * and the direction of the exit code: a `cost` row must never fail the build, because a
    watcher that cries about price moves is a watcher people learn to ignore before the day it
    matters.

The real document is also parsed, so moving or re-shaping `research/hosts-watch.md`'s calendar
reds this test rather than quietly disarming the script.
"""
import sys
import json
import subprocess
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import retirement_watch as rw  # noqa: E402

SETTINGS = """
| Claude / Anthropic | `ANTHROPIC_MODEL` | `claude-sonnet-4-5` | Daily review |
| Claude / Anthropic | mail | `claude-sonnet-4-6` | Mail replies |
"""

CAL = """
| Date | Event | Whose route it touches | Impact |
|---|---|---|---|
| 2026-11-21 | promo rate ends | Tarik | cost |
| 2026-11-30 | `claude-sonnet-4-5` retired (replacement `claude-sonnet-5-5`) | Claude | route |
| 2027-04-01 | `gpt-5.1` retired | nobody | — |
"""


class ParseTest(unittest.TestCase):
    def test_rows_come_back_with_their_impact_and_models(self):
        rows = rw.parse_calendar(CAL)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[1]["date"], date(2026, 11, 30))
        self.assertEqual(rows[1]["impact"], "route")
        self.assertEqual(rows[1]["models"], ["claude-sonnet-4-5", "claude-sonnet-5-5"])

    def test_a_row_with_no_impact_cell_is_kept_and_unclassified(self):
        text = "| 2026-11-30 | `claude-sonnet-4-5` retired | Claude |\n"
        rows = rw.parse_calendar(text)
        self.assertEqual(len(rows), 1)
        self.assertIsNone(rows[0]["impact"])
        self.assertEqual(rw.verdict(rows), 2, "an unclassified calendar must not pass as green")

    def test_a_moved_table_is_not_green(self):
        rows = rw.parse_calendar("no table here at all\n")
        self.assertEqual(rows, [])
        self.assertEqual(rw.verdict(rows), 2)

    def test_a_row_keeps_its_models_when_the_shape_changes(self):
        """The 2026-10-22 regression, pinned.

        A patch that added line numbers to these rows replaced the dict literal and dropped
        `models` with it. `assess` reads `r["models"][0]`, so seven tests died on `KeyError`
        and the landing was refused — the row's shape is a contract with the caller, not a
        private matter of this function.
        """
        rows = rw.parse_calendar(CAL)
        self.assertEqual(rows[1]["models"], ["claude-sonnet-4-5", "claude-sonnet-5-5"])
        self.assertEqual(rw.assess(rows, SETTINGS, date(2026, 10, 22), 30, 365)[1]["models"],
                         ["claude-sonnet-4-5", "claude-sonnet-5-5"])

    def test_each_row_can_be_traced_to_its_line(self):
        rows = rw.parse_calendar(CAL)
        self.assertEqual([r["line"] for r in rows], [4, 5, 6])
        self.assertIn("2026-11-30", rows[1]["raw"])
        self.assertEqual(rows[1]["fourth"], "route")


class UnclassifiedMessageTest(unittest.TestCase):
    """The message a refusal carries. Named rows or it is not a diagnosis."""

    # The real failure, reproduced: a human-readable summary table pasted under the calendar.
    # Its second column ("days out") is read as the event, so the row has no Impact cell.
    DOC_WITH_SUMMARY = CAL + """
| Date | Days out | Action |
|---|---|---|
| 2026-11-30 | 39 | swap Claude's model |
| 2026-12-01 | 40 | nothing |
"""

    def test_a_healthy_calendar_produces_no_message(self):
        self.assertEqual(rw.describe_unclassified(rw.parse_calendar(CAL)), "")

    def test_a_summary_table_beside_the_calendar_names_its_own_lines(self):
        rows = rw.parse_calendar(self.DOC_WITH_SUMMARY)
        bad = rw.unclassified(rows)
        self.assertEqual(len(bad), 2, "the summary table's rows are read as calendar rows")
        msg = rw.describe_unclassified(rows)
        self.assertIn("2 line(s)", msg)
        self.assertIn("line 10:", msg)
        self.assertIn("line 11:", msg)
        self.assertIn("2026-11-30", msg)
        self.assertIn("stop the row starting with a date", msg)

    def test_a_missing_fourth_cell_is_named_differently_from_a_wrong_one(self):
        nothing = rw.parse_calendar("| 2026-11-30 | `claude-sonnet-4-5` retired | Claude |\n")
        wrong = rw.parse_calendar("| 2026-11-30 | `claude-sonnet-4-5` retired | Claude | 39 |\n")
        self.assertEqual(rw.unclassified(nothing), rw.unclassified(nothing))
        self.assertIn("line 1: no fourth cell at all", rw.describe_unclassified(nothing))
        self.assertIn("line 1: fourth cell is '39'", rw.describe_unclassified(wrong))

    def test_the_rendered_report_carries_the_lines_not_just_a_count(self):
        rows = rw.assess(rw.parse_calendar(self.DOC_WITH_SUMMARY), SETTINGS, date(2026, 10, 22), 30, 365)
        text = rw.render(rows, date(2026, 10, 22), 30, 180)
        self.assertIn("UNCLASSIFIED (2):", text)
        self.assertIn("line 10:", text)


class IsSetTest(unittest.TestCase):
    def test_exact_name_is_set(self):
        self.assertTrue(rw.is_set("claude-sonnet-4-5", SETTINGS))

    def test_a_snapshot_is_not_the_same_route(self):
        self.assertFalse(rw.is_set("claude-sonnet-4-5-20250929", SETTINGS))

    def test_name_inside_a_longer_name_does_not_count(self):
        self.assertFalse(rw.is_set("deepseek-chat", "| x | `deepseek/deepseek-chat` | y |"))


class AssessTest(unittest.TestCase):
    def _assess(self, as_of, settings=SETTINGS):
        return {r["event"]: r for r in
                rw.assess(rw.parse_calendar(CAL), settings, as_of, 30, 180)}

    def test_a_route_inside_the_window_is_due(self):
        rows = self._assess(date(2026, 11, 10))
        self.assertEqual(rows["`claude-sonnet-4-5` retired (replacement `claude-sonnet-5-5`)"]["status"], "due")
        self.assertEqual(rw.verdict(list(rows.values())), 1)

    def test_a_cost_row_inside_the_window_is_not_a_failure(self):
        rows = self._assess(date(2026, 11, 10))
        self.assertEqual(rows["promo rate ends"]["status"], "soon")
        # only the route row fails the build; drop it and the code goes green
        self.assertEqual(rw.verdict([r for r in rows.values() if r["impact"] == "cost"]), 0)

    def test_the_swap_clears_the_row(self):
        swapped = "| Claude | `ANTHROPIC_MODEL` | `claude-sonnet-5-5` |\n"
        rows = self._assess(date(2026, 11, 29), swapped)
        self.assertEqual(rows["`claude-sonnet-4-5` retired (replacement `claude-sonnet-5-5`)"]["status"], "resolved")
        self.assertEqual(rw.verdict(list(rows.values())), 0)

    def test_a_date_already_past_is_marked_past_not_due(self):
        rows = self._assess(date(2026, 12, 5))
        self.assertEqual(rows["`claude-sonnet-4-5` retired (replacement `claude-sonnet-5-5`)"]["status"], "past")

    def test_not_ours_rows_are_never_resolved_and_never_fail(self):
        rows = self._assess(date(2026, 11, 10))
        not_ours = rows["`gpt-5.1` retired"]
        self.assertEqual(not_ours["impact"], "—")
        self.assertFalse(not_ours["resolved"],
                         "a row marked '—' must not read as resolved: nobody did that work")
        self.assertEqual(rw.verdict([not_ours]), 0)


class DeadlineCliTest(unittest.TestCase):
    """Actual isolated processes: overdue and malformed rows cannot give false green."""

    def run_cli(self, calendar, settings=SETTINGS, *options):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            doc, config = root / "calendar.md", root / "settings.md"
            doc.write_text(calendar, encoding="utf-8")
            config.write_text(settings, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(ROOT / "scripts/retirement_watch.py"),
                 "--doc", str(doc), "--settings", str(config),
                 "--as-of", "2026-12-01", *options],
                capture_output=True, text=True, timeout=10)

    def test_overdue_route_remains_actionable_even_with_zero_view(self):
        result = self.run_cli(CAL, SETTINGS, "--window", "0")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("ACT: 2026-11-30 (-1d)", result.stdout)
        self.assertIn("overdue", result.stdout)
        self.assertNotIn("nothing to act on", result.stdout)

    def test_overdue_json_keeps_past_status_and_failing_exit(self):
        result = self.run_cli(CAL, SETTINGS, "--json")
        self.assertEqual(result.returncode, 1, result.stderr)
        route = next(r for r in json.loads(result.stdout)["rows"] if r["impact"] == "route")
        self.assertEqual((route["status"], route["days"], route["resolved"]),
                         ("past", -1, False))

    def test_swapped_overdue_route_clears_but_past_cost_and_unowned_rows_do_not_fail(self):
        result = self.run_cli(CAL, "`claude-sonnet-5-5`")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("resolved", result.stdout)
        self.assertNotIn("ACT:", result.stdout)

    def test_invalid_date_beside_valid_rows_refuses_text_and_json(self):
        for value in ("2026-99-30", "2026-02-30", "2026-1-02", "2026-11-30oops"):
            for options in ((), ("--json",)):
                with self.subTest(date=value, options=options):
                    calendar = CAL + f"| {value} | `still-set` retires | somebody | route |\n"
                    result = self.run_cli(calendar, "`replacement`", *options)
                    self.assertEqual(result.returncode, 2)
                    self.assertIn("line 7:", result.stderr)
                    self.assertIn(value, result.stderr)
                    self.assertEqual(result.stdout, "")

    def test_incomplete_dated_row_refuses_instead_of_disappearing(self):
        result = self.run_cli(CAL + "| 2026-12-02 | truncated |\n")
        self.assertEqual(result.returncode, 2)
        self.assertIn("line 7: incomplete dated calendar row", result.stderr)

    def test_bad_date_in_library_is_an_explicit_error(self):
        with self.assertRaisesRegex(ValueError, "line 7: invalid calendar date"):
            rw.parse_calendar(CAL + "| 2026-02-30 | event | owner | route |\n")


class RealDocumentTest(unittest.TestCase):
    """The shipped calendar must still parse — this is the drift guard."""

    def test_the_repository_calendar_parses_fully(self):
        rows = rw.parse_calendar(rw.DOC.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(rows), 8, "the calendar shrank or changed shape")
        # Named lines, not a count: "a row lost its Impact cell" is what a wake was told on
        # 2026-10-22 while editing this document, and it could not find the row to fix.
        bad = rw.unclassified(rows)
        self.assertTrue(not bad, "a row lost its Impact cell\n" + rw.describe_unclassified(bad))

    def test_the_document_still_names_the_route_this_instrument_tests(self):
        settings = rw.SETTINGS.read_text(encoding="utf-8")
        self.assertTrue(rw.is_set("claude-sonnet-4-5", settings) or
                        rw.is_set("claude-sonnet-5-5", settings),
                        "Claude's daily route is neither the retiring model nor its replacement")

    def test_today_is_reported_with_a_usable_exit_code(self):
        settings = rw.SETTINGS.read_text(encoding="utf-8")
        rows = rw.assess(rw.parse_calendar(rw.DOC.read_text(encoding="utf-8")),
                         settings, date.today(), 30, 180)
        self.assertIn(rw.verdict(rows), (0, 1))


if __name__ == "__main__":
    unittest.main(verbosity=2)
