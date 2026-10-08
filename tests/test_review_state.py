#!/usr/bin/env python3
"""Tests for the review-state reporter — the six letters the human defined on 2026-10-07.

The three things that would make the reading a lie, and are therefore pinned here:
  1. the classification reads reasons *already on disk* and adds no field — an item with no reason
     must read as W (waiting), never as P (postponed by decision);
  2. the two partitions cover every item exactly once, so `N + V` and `A + P + W + R` are the whole
     set counted two ways and a drift between them is a bug, not a reading;
  3. the daily delta is recovered from the append-only ledger's own timestamps, so an item reviewed
     yesterday counts as waiting at yesterday's snapshot and accomplished today.
"""
import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts import review_state as rs  # noqa: E402


def write_lines(path: Path, recs: list[dict]) -> None:
    path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in recs), encoding="utf-8")


def base(item_id: str, filed: str, amigo: str = "desi", scope: str = "internal") -> dict:
    return {"id": item_id, "filed_utc": filed, "amigo": amigo, "scope": scope,
            "title": "something performed", "state": None, "state_utc": None,
            "reason": None, "reviewer": None}


class TestClassification(unittest.TestCase):
    def test_no_reason_is_waiting_not_postponed(self):
        # The 13:55 rule: P only if the reason is written; otherwise it is W no matter how it is
        # labelled. A postponed item with no reason is the exact failure the split exists to catch.
        rec = dict(base("x", "2026-10-01T00:00:00Z"), state="postponed", reason="")
        self.assertEqual(rs.outcome(rec), "W")

    def test_postponed_with_a_written_reason_is_p(self):
        rec = dict(base("x", "2026-10-01T00:00:00Z"), state="postponed",
                   reason="closed access; needs a reader with a library")
        self.assertEqual(rs.outcome(rec), "P")

    def test_land_verified_item_needs_no_review(self):
        rec = dict(base("x", "2026-10-01T00:00:00Z"), state="accomplished",
                   state_utc="2026-10-02T00:00:00Z", reviewer="auto:land",
                   reason="landed on main (lander's test gate passed)")
        self.assertEqual(rs.needed_review(rec), "N")
        self.assertEqual(rs.outcome(rec), "A")

    def test_unreviewed_item_needs_review(self):
        rec = base("x", "2026-10-01T00:00:00Z")
        self.assertEqual(rs.needed_review(rec), "V")
        self.assertEqual(rs.outcome(rec), "W")

    def test_reviewed_accomplishment_needs_review(self):
        rec = dict(base("x", "2026-10-01T00:00:00Z"), state="accomplished",
                   state_utc="2026-10-02T00:00:00Z", reviewer="claude", reason="reviewed, fine")
        self.assertEqual(rs.needed_review(rec), "V")
        self.assertEqual(rs.outcome(rec), "A")


class TestPartitions(unittest.TestCase):
    def test_both_partitions_cover_every_item_once(self):
        recs = [
            base("a", "2026-10-01T00:00:00Z"),
            dict(base("b", "2026-10-01T00:00:00Z"), state="postponed", state_utc="2026-10-02T00:00:00Z",
                 reason="not now, and here is why"),
            dict(base("c", "2026-10-01T00:00:00Z"), state="accomplished",
                 state_utc="2026-10-02T00:00:00Z", reviewer="auto:land",
                 reason="landed on main (lander's test gate passed)"),
            dict(base("d", "2026-10-01T00:00:00Z"), state="rejected",
                 state_utc="2026-10-02T00:00:00Z", reason="out of scope"),
        ]
        c = rs.counts(recs)
        self.assertEqual(c["N"] + c["V"], c["total"])
        self.assertEqual(c["A"] + c["P"] + c["W"] + c["R"], c["total"])
        self.assertEqual((c["N"], c["V"], c["A"], c["P"], c["W"], c["R"]),
                         (1, 3, 1, 1, 1, 1))
        self.assertEqual(c["V"] - c["W"], 2)  # P and R drained; the waiting item has not


class TestHistory(unittest.TestCase):
    def test_the_delta_is_recovered_from_the_ledgers_own_timestamps(self):
        with tempfile.TemporaryDirectory() as t:
            path = Path(t) / "items.jsonl"
            # filed 10-05 unreviewed, then reviewed and accomplished by another amigo on 10-07.
            write_lines(path, [
                base("x", "2026-10-05T00:00:00Z"),
                dict(base("x", "2026-10-05T00:00:00Z"), state="accomplished",
                     state_utc="2026-10-07T00:00:00Z", reviewer="claude",
                     reason="reviewed; it holds"),
            ])
            before = rs.counts(rs.state_as_of(path, dt.datetime(2026, 10, 6, tzinfo=dt.timezone.utc)))
            after = rs.counts(rs.state_as_of(path, dt.datetime(2026, 10, 8, tzinfo=dt.timezone.utc)))
            self.assertEqual((before["W"], before["A"]), (1, 0))
            self.assertEqual((after["W"], after["A"]), (0, 1))
            # The item is waiting at one snapshot and needed-review-accomplished at the next.
            self.assertEqual(before["V"] - before["W"], 0)
            self.assertEqual(after["V"] - after["W"], 1)

    def test_an_item_filed_after_the_snapshot_is_absent(self):
        with tempfile.TemporaryDirectory() as t:
            path = Path(t) / "items.jsonl"
            write_lines(path, [base("x", "2026-10-05T00:00:00Z")])
            early = rs.state_as_of(path, dt.datetime(2026, 10, 1, tzinfo=dt.timezone.utc))
            self.assertEqual(early, [])
            self.assertEqual(len(rs.state_as_of(path, dt.datetime(2026, 10, 8,
                                                                    tzinfo=dt.timezone.utc))), 1)

    def test_duplicate_lines_do_not_double_count(self):
        with tempfile.TemporaryDirectory() as t:
            path = Path(t) / "items.jsonl"
            row = base("x", "2026-10-05T00:00:00Z")
            write_lines(path, [row, row, row])
            self.assertEqual(rs.counts(rs.state_as_of(path)).get("total"), 1)


class TestVerdict(unittest.TestCase):
    def test_zero_delta_while_waiting_grows_is_broken(self):
        self.assertEqual(rs.verdict(0, 5), "broken — inflow with no drainage")

    def test_drain_with_faster_inflow_is_capacity_not_brokenness(self):
        self.assertEqual(rs.verdict(3, 4), "capacity — draining, but inflow is faster")

    def test_real_drain_reads_as_draining(self):
        self.assertEqual(rs.verdict(2, 0), "draining")


if __name__ == "__main__":
    unittest.main()
