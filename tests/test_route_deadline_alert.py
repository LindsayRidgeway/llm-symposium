#!/usr/bin/env python3
"""Tests for scripts/route_deadline_alert.py — the caller R-011 said was missing.

The point of these tests is not that the script runs. It is that the two properties the risk row
needs actually hold: it speaks only about **route** deadlines (a price change is a cost row, not an
outage), and it does not repeat itself every morning until someone does something.
"""
import datetime
import importlib.util
import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("route_alert", REPO / "scripts" / "route_deadline_alert.py")
alert = importlib.util.module_from_spec(spec)
spec.loader.exec_module(alert)


FIXTURE_JSON = {
    "rows": [
        {"date": "2026-11-30", "event": "`claude-sonnet-4-5` retired", "subject": "claude-sonnet-4-5",
         "impact": "route", "days": 10, "resolved": False, "owner": "Claude, daily"},
        {"date": "2026-12-01", "event": "Gemini pricing doubles", "subject": "gemini-3.8-flash",
         "impact": "cost", "days": 11, "resolved": False, "owner": "any"},
        {"date": "2026-11-29", "event": "`claude-sonnet-4-5` retired", "subject": "claude-sonnet-4-5",
         "impact": "route", "days": 9, "resolved": True, "owner": "Claude, daily"},
        {"date": "2026-11-01", "event": "`gpt-5.1` retired", "subject": "gpt-5.1",
         "impact": "route", "days": -19, "resolved": False, "owner": "Tarik"},
    ]
}


class _FakeRun:
    def __init__(self, payload):
        self.stdout = json.dumps(payload)
        self.stderr = ""
        self.returncode = 1


class SelectionTests(unittest.TestCase):
    """The filter, on a fixture.

    These three tests used to run against the live repository and they failed the day the swap
    landed — which is the same shape as a test that passes because nothing invokes it, pointing the
    other way: a test whose subject is today's state goes red when the state improves. The filter is
    what needs holding down, so the calendar arrives as a fixture and today's calendar is asserted
    separately, in the direction that matters (see RepositoryStateTests).
    """

    def setUp(self):
        self._run = alert.subprocess.run
        alert.subprocess.run = lambda *a, **k: _FakeRun(FIXTURE_JSON)

    def tearDown(self):
        alert.subprocess.run = self._run

    def test_cost_rows_are_not_alerts(self):
        """A pricing date is worth a calendar, not an email at 16:00."""
        rows = alert.route_rows(21)
        self.assertTrue(rows, "the fixture has a route row inside the window")
        for row in rows:
            self.assertEqual(row.get("impact"), "route", row)

    def test_rows_are_inside_the_window_and_not_past(self):
        for row in alert.route_rows(21):
            self.assertGreaterEqual(row["days"], 0, row)
            self.assertLessEqual(row["days"], 21, row)

    def test_an_already_resolved_row_is_not_an_alert(self):
        subjects = [(r["subject"], r["days"]) for r in alert.route_rows(21)]
        self.assertNotIn(("claude-sonnet-4-5", 9), subjects,
                         "the resolved duplicate must be dropped even though it is inside the window")

    def test_the_known_route_is_found(self):
        subjects = {row.get("subject") for row in alert.route_rows(21)}
        self.assertIn("claude-sonnet-4-5", subjects)

    def test_slug_is_stable_and_filename_safe(self):
        row = {"subject": "`claude-sonnet-4-5`", "event": "x"}
        self.assertEqual(alert.slug(row), "claude-sonnet-4-5")
        self.assertEqual(alert.slug({"event": "GPT-5.6 / Sol — pricing"}), "gpt-5-6-sol-pricing")


class RepositoryStateTests(unittest.TestCase):
    """Today's repo, asserted in the direction a regression would move it.

    The swap landed 2026-11-20. If someone restores the retiring id to
    `governance/model-settings.md`, the row stops being resolved and the alert starts mailing the
    human again — so this is the test that would catch a quiet revert of the repair.
    """

    def rows(self):
        out = alert.subprocess.run(
            [sys.executable, str(alert.WATCH), "--json", "--warn", "21", "--window", "180"],
            capture_output=True, text=True, cwd=str(alert.REPO))
        return json.loads(out.stdout)["rows"]

    def test_the_route_the_row_was_written_about_is_now_resolved(self):
        row = [r for r in self.rows() if r.get("subject") == "claude-sonnet-4-5"]
        self.assertTrue(row, "the calendar row R-011 was written about has vanished")
        self.assertTrue(row[0].get("resolved"),
                        "the retiring id is back in governance/model-settings.md — the alert would "
                        "now mail the human weekly about a swap that has already been made")

    def test_the_repo_has_nothing_due_this_week(self):
        self.assertEqual(alert.route_rows(7), [],
                         "a route deadline is inside a week and nobody has been told — either swap it "
                         "or record why not")


class QuietTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self._state, self._out = alert.STATE, alert.OUTBOUND
        self._rows, alert.route_rows = alert.route_rows, (lambda warn: [FIXTURE_JSON["rows"][0]])
        alert.STATE = base / "state"
        alert.OUTBOUND = base / "outbound"

    def tearDown(self):
        alert.STATE, alert.OUTBOUND = self._state, self._out
        alert.route_rows = self._rows
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
        alert.route_rows = lambda warn: []
        try:
            self.assertEqual(alert.main(), 0)
            self.assertFalse(list(alert.OUTBOUND.glob("*.md")) if alert.OUTBOUND.is_dir() else [])
        finally:
            alert.WARN_DAYS = old

    def test_state_files_stop_a_repeat_within_the_repeat_window(self):
        today = datetime.date.today().isoformat()
        alert.STATE.mkdir(parents=True, exist_ok=True)
        for row in [FIXTURE_JSON["rows"][0]]:   # the row the patched route_rows returns
            (alert.STATE / ("%s-%s.md" % (alert.slug(row), today))).write_text("x")
        self.assertEqual(alert.main(), 0)
        self.assertFalse(list(alert.OUTBOUND.glob("*.md")) if alert.OUTBOUND.is_dir() else [])


if __name__ == "__main__":
    unittest.main()
