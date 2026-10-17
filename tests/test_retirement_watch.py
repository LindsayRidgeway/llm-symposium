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


class RealDocumentTest(unittest.TestCase):
    """The shipped calendar must still parse — this is the drift guard."""

    def test_the_repository_calendar_parses_fully(self):
        rows = rw.parse_calendar(rw.DOC.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(rows), 8, "the calendar shrank or changed shape")
        self.assertTrue(all(r["impact"] for r in rows), "a row lost its Impact cell")

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
