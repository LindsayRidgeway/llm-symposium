#!/usr/bin/env python3
"""Tests for the Status 5 revisit trigger (`scripts/blocked_revisit.py`).

The thing being pinned is not "it prints a list". It is that the *verdict* is decided by evidence
and that its order is the rule, because the failure this script exists to prevent is a state no
mechanism can move out of — and a trigger that says "needs a look" for everything is exactly as
useless as one that says it for nothing.
"""
import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import blocked_revisit as br  # noqa: E402

NOW = dt.datetime(2026, 10, 19, 3, 0, tzinfo=dt.timezone.utc)


def row(item_id="r1", state="postponed", state_utc="2026-10-18T12:00:00Z", paths=(), reviewer="desi"):
    return {"id": item_id, "amigo": reviewer, "reviewer": reviewer, "state": state,
            "state_utc": state_utc, "paths": list(paths), "short_title": f"item {item_id}"}


class RevisitTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        (self.repo / "there.md").write_text("x", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def verdict(self, rows, log="", stale_days=14):
        facts = br.build(rows, log, self.repo, stale_days, now=NOW)
        return {f["id"]: f["verdict"] for f in facts}

    def test_landed_wins_over_every_other_verdict(self):
        # Old, absent, no re-look — and still "landed", because a landing is the one fact that
        # settles the item regardless of how it was parked.
        rows = [row(paths=["gone.md"], state_utc="2026-09-01T00:00:00Z")]
        log = "land(wake): work from run r1\n"
        self.assertEqual(self.verdict(rows, log), {"r1": "landed"})

    def test_stale_names_the_items_nobody_came_back_to(self):
        rows = [row(paths=["gone.md"], state_utc="2026-09-01T00:00:00Z")]
        self.assertEqual(self.verdict(rows), {"r1": "stale"})

    def test_a_later_row_about_the_same_item_stops_it_reading_as_stale(self):
        old = row(paths=["gone.md"], state_utc="2026-09-01T00:00:00Z")
        again = row(state_utc="2026-10-15T00:00:00Z", paths=["gone.md"])
        self.assertEqual(self.verdict([old, again]), {"r1": "absent"})

    def test_all_named_paths_present_is_a_look_not_a_done(self):
        # A modified file exists whether or not the change landed, so the verdict is "present",
        # never "accomplished" — the reason line says so out loud.
        self.assertEqual(self.verdict([row(paths=["there.md"])]), {"r1": "present"})

    def test_no_named_path_present_means_the_blocker_stands(self):
        self.assertEqual(self.verdict([row(paths=["gone.md", "also-gone.md"])]), {"r1": "absent"})

    def test_partial_presence_is_not_evidence_the_payload_arrived(self):
        self.assertEqual(self.verdict([row(paths=["there.md", "gone.md"])]), {"r1": "absent"})

    def test_an_item_with_no_repository_path_is_unverifiable_rather_than_guessed(self):
        self.assertEqual(self.verdict([row(paths=[])]), {"r1": "unverifiable"})

    def test_duplicate_rows_collapse_to_the_latest_postponement(self):
        rows = [row(state_utc="2026-10-01T00:00:00Z", paths=["gone.md"]),
                row(state_utc="2026-10-18T00:00:00Z", paths=["there.md"])]
        facts = br.build(rows, "", self.repo, 14, now=NOW)
        self.assertEqual(len(facts), 1)
        self.assertEqual(facts[0]["postponed_utc"], "2026-10-18T00:00:00Z")
        self.assertEqual(facts[0]["verdict"], "present")

    def test_accomplished_and_rejected_rows_are_not_in_this_queue(self):
        rows = [row(item_id="a", state="accomplished"), row(item_id="b", state="rejected")]
        self.assertEqual(self.verdict(rows), {})

    def test_counts_and_the_look_list_agree(self):
        rows = [row("landed-1", state_utc="2026-10-18T00:00:00Z", paths=["gone.md"]),
                row("stale-1", state_utc="2026-09-01T00:00:00Z", paths=["gone.md"]),
                row("absent-1", state_utc="2026-10-18T00:00:00Z", paths=["gone.md"]),
                row("present-1", state_utc="2026-10-18T00:00:00Z", paths=["there.md"])]
        facts = br.build(rows, "landed-1", self.repo, 14, now=NOW)
        c = br.counts(facts)
        self.assertEqual(c, {"landed": 1, "stale": 1, "present": 1, "absent": 1, "unverifiable": 0})
        self.assertEqual(len([f for f in facts if f["verdict"] in br.NEEDS_A_LOOK]), 3)

    def test_the_ledger_itself_is_readable_and_duplicates_do_not_double_count(self):
        rows = br.load(br.LEDGER)
        facts = br.build(rows, "", self.repo, 14, now=NOW)
        ids = [f["id"] for f in facts]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(facts), len(br.postponed(rows)))
        self.assertTrue(all(f["verdict"] in br.ORDER for f in facts))


if __name__ == "__main__":
    unittest.main()
