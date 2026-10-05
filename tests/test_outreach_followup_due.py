#!/usr/bin/env python3
"""The Monday outreach item must be checkable, not a judgement.

Written 2026-10-05 with `scripts/outreach_followup_due.py`. The outreach to-do item asks, in
prose, to "draft follow-ups to anyone quiet 10+ days"; on 2026-10-04 a wake passed the item
over ("the date has not arrived") while the trigger lived only inside the sentence. This pins
the reader that turns "who is overdue a follow-up" into a command's output: it counts days from
each prospect's `sent_date`, treats `replied: true` as closed, and treats a `follow_up` whose
leading date is itself inside the threshold as handled this cycle.

The last test pins the *real* ledger, so the state the Monday item depends on cannot silently
drift: on 2026-10-05 both 2026-09-17 contacts are 18 days quiet and both carry a follow-up
staged that day, so the reader reports them handled and `--check` exits 0.
"""

import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import outreach_followup_due as due  # noqa: E402


def _ledger(prospects):
    return {"_what": "test", "prospects": prospects}


class RowsTests(unittest.TestCase):
    def test_quiet_past_threshold_needs_action(self):
        led = _ledger([{"id": "a", "sent_date": "2026-09-17"}])
        r = due.rows(led, dt.date(2026, 10, 5), 10)
        self.assertEqual(len(r), 1)
        self.assertTrue(r[0]["needs"])
        self.assertEqual(r[0]["quiet"], 18)

    def test_recent_send_not_listed(self):
        led = _ledger([{"id": "a", "sent_date": "2026-09-30"}])
        self.assertEqual(due.rows(led, dt.date(2026, 10, 5), 10), [])

    def test_replied_is_closed(self):
        led = _ledger([{"id": "a", "sent_date": "2026-09-17", "replied": True}])
        r = due.rows(led, dt.date(2026, 10, 5), 10)
        self.assertEqual(len(r), 1)
        self.assertFalse(r[0]["needs"])
        self.assertTrue(r[0]["replied"])

    def test_fresh_follow_up_counts_as_handled(self):
        led = _ledger([{"id": "a", "sent_date": "2026-08-01",
                        "follow_up": "2026-10-05 — staged this cycle"}])
        r = due.rows(led, dt.date(2026, 10, 5), 10)
        self.assertTrue(r[0]["handled"])
        self.assertFalse(r[0]["needs"])

    def test_stale_follow_up_still_needs_action(self):
        led = _ledger([{"id": "a", "sent_date": "2026-08-01",
                        "follow_up": "2026-09-01 — an old nudge"}])
        r = due.rows(led, dt.date(2026, 10, 5), 10)
        self.assertFalse(r[0]["handled"])
        self.assertTrue(r[0]["needs"])

    def test_prospect_without_sent_date_is_skipped(self):
        led = _ledger([{"id": "staged-only"}])
        self.assertEqual(due.rows(led, dt.date(2026, 10, 5), 10), [])

    def test_leading_date_parses_and_rejects(self):
        self.assertEqual(due.leading_date("2026-10-05 — x"), dt.date(2026, 10, 5))
        self.assertIsNone(due.leading_date("no date here"))
        self.assertIsNone(due.leading_date("2026-13-40"))
        self.assertIsNone(due.leading_date(None))


class CheckExitTests(unittest.TestCase):
    def _write(self, prospects):
        tmp = tempfile.TemporaryDirectory()
        p = Path(tmp.name) / "pipeline.json"
        p.write_text(json.dumps(_ledger(prospects)))
        self.addCleanup(tmp.cleanup)
        return str(p)

    def test_check_exits_one_when_action_needed(self):
        path = self._write([{"id": "a", "sent_date": "2026-08-01"}])
        self.assertEqual(due.main(["--ledger", path, "--as-of", "2026-10-05", "--check"]), 1)

    def test_check_exits_zero_when_all_handled(self):
        path = self._write([{"id": "a", "sent_date": "2026-09-17",
                             "follow_up": "2026-10-05 — staged"}])
        self.assertEqual(due.main(["--ledger", path, "--as-of", "2026-10-05", "--check"]), 0)


class RealLedgerTests(unittest.TestCase):
    def test_real_ledger_is_consistent_on_2026_10_05(self):
        ledger = ROOT / "channels" / "outreach" / "pipeline.json"
        data = json.loads(ledger.read_text(encoding="utf-8"))
        as_of = dt.date(2026, 10, 5)
        r = due.rows(data, as_of, 10)
        by = {x["id"]: x for x in r}
        # The two 2026-09-17 cold contacts are 18 days quiet and were each given a follow-up
        # staged on 2026-10-05, so neither should read as needing action that day.
        for pid in ("retraction-watch", "me-cfs-metabolism"):
            self.assertIn(pid, by, f"{pid} should be quiet >= 10d on {as_of}")
            self.assertEqual(by[pid]["quiet"], 18)
            self.assertTrue(by[pid]["handled"], f"{pid} should be handled by its staged follow-up")
            self.assertFalse(by[pid]["needs"])
        self.assertFalse([x for x in r if x["needs"]], "no prospect should need action on 2026-10-05")


if __name__ == "__main__":
    unittest.main(verbosity=2)
