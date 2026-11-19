#!/usr/bin/env python3
"""Tests for scripts/route_deadline_alert.py — the caller R-011 said was missing.

The point of these tests is not that the script runs. It is that the two properties the risk row
needs actually hold: it speaks only about **route** deadlines (a price change is a cost row, not an
outage), and it does not repeat itself every morning until someone does something.
"""
import datetime
import importlib.util
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("route_alert", REPO / "scripts" / "route_deadline_alert.py")
alert = importlib.util.module_from_spec(spec)
spec.loader.exec_module(alert)


class SelectionTests(unittest.TestCase):
    def test_cost_rows_are_not_alerts(self):
        """A pricing date is worth a calendar, not an email at 16:00."""
        rows = alert.route_rows(21)
        self.assertTrue(rows, "the calendar should have at least one route row inside 21 days")
        for row in rows:
            self.assertEqual(row.get("impact"), "route", row)

    def test_rows_are_inside_the_window_and_not_past(self):
        for row in alert.route_rows(21):
            self.assertGreaterEqual(row["days"], 0, row)
            self.assertLessEqual(row["days"], 21, row)

    def test_the_known_route_is_found(self):
        """claude-sonnet-4-5 is the row R-011 was written about; if it resolves, this test should
        fail loudly rather than quietly pass on an empty list."""
        subjects = {row.get("subject") for row in alert.route_rows(21)}
        self.assertIn("claude-sonnet-4-5", subjects)

    def test_slug_is_stable_and_filename_safe(self):
        row = {"subject": "`claude-sonnet-4-5`", "event": "x"}
        self.assertEqual(alert.slug(row), "claude-sonnet-4-5")
        self.assertEqual(alert.slug({"event": "GPT-5.6 / Sol — pricing"}), "gpt-5-6-sol-pricing")


class QuietTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self._state, self._out = alert.STATE, alert.OUTBOUND
        alert.STATE = base / "state"
        alert.OUTBOUND = base / "outbound"

    def tearDown(self):
        alert.STATE, alert.OUTBOUND = self._state, self._out
        self.tmp.cleanup()

    def test_it_speaks_once_then_stays_quiet(self):
        self.assertEqual(alert.main(), 0)
        first = sorted(p.name for p in alert.OUTBOUND.glob("*.md"))
        self.assertTrue(first, "first run should draft one mail")
        self.assertEqual(alert.main(), 0)
        self.assertEqual(sorted(p.name for p in alert.OUTBOUND.glob("*.md")), first,
                         "a second run the same day must not draft a second mail")

    def test_it_is_silent_when_the_window_is_narrow(self):
        """With a zero-day warning window nothing is due, and no mail may be drafted."""
        old = alert.WARN_DAYS
        alert.WARN_DAYS = 0
        try:
            self.assertEqual(alert.main(), 0)
            self.assertFalse(list(alert.OUTBOUND.glob("*.md")) if alert.OUTBOUND.is_dir() else [])
        finally:
            alert.WARN_DAYS = old

    def test_state_files_stop_a_repeat_within_the_repeat_window(self):
        today = datetime.date.today().isoformat()
        alert.STATE.mkdir(parents=True, exist_ok=True)
        for row in alert.route_rows(alert.WARN_DAYS):
            (alert.STATE / ("%s-%s.md" % (alert.slug(row), today))).write_text("x")
        self.assertEqual(alert.main(), 0)
        self.assertFalse(list(alert.OUTBOUND.glob("*.md")) if alert.OUTBOUND.is_dir() else [])


if __name__ == "__main__":
    unittest.main()
