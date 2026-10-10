#!/usr/bin/env python3
"""Tests for the assignment algorithm — who reviews an item, and why.

The three things that would make the rule a lie, and are therefore pinned here:
  1. the cost cache names a *band*, not a single winner — otherwise the random branch has no pool;
  2. a draw is frozen once made — a later price change cannot re-roll an item already in flight;
  3. the author is never assigned its own work, on either branch.

Plus the two things the rule states in prose and must therefore also be true in code: a competence
match outranks cost, and a competence assignment must carry its one-line reason.
"""
import datetime as dt
import random
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from channels import review_assignment as ra  # noqa: E402


def band_of(band, as_of="2026-10-09"):
    return {"as_of": as_of, "band": list(band)}


class TestBand(unittest.TestCase):
    def test_the_band_is_every_tie_not_a_single_winner(self):
        # desi and dmitri tied cheapest; a single-winner band would collapse the random branch.
        prices = {"claude": 1.15, "desi": 0.01, "gemini": 0.59, "tarik": 1.86, "dmitri": 0.01}
        self.assertEqual(ra.least_expensive_band(prices), ["desi", "dmitri"])

    def test_a_genuine_single_cheapest_is_allowed(self):
        prices = {"claude": 1.0, "desi": 0.5, "gemini": 2.0}
        self.assertEqual(ra.least_expensive_band(prices), ["desi"])

    def test_an_empty_or_negative_price_set_is_refused(self):
        with self.assertRaises(ValueError):
            ra.least_expensive_band({})
        with self.assertRaises(ValueError):
            ra.least_expensive_band({"desi": -1.0, "claude": 1.0})

    def test_build_band_keeps_prices_and_the_date(self):
        b = ra.build_band({"desi": 0.01, "claude": 1.0}, as_of="2026-10-09")
        self.assertEqual(b["as_of"], "2026-10-09")
        self.assertEqual(b["band"], ["desi"])
        self.assertEqual(b["prices"], {"claude": 1.0, "desi": 0.01})

    def test_stale_band_is_detected_against_its_date(self):
        fresh = band_of(["desi"], as_of="2026-10-09")
        self.assertFalse(ra.band_is_stale(fresh, today=dt.date(2026, 10, 20)))
        old = band_of(["desi"], as_of="2026-01-01")
        self.assertTrue(ra.band_is_stale(old, today=dt.date(2026, 10, 20)))
        self.assertEqual(ra.band_age_days(old, today=dt.date(2026, 10, 20)), 292)


class TestChoose(unittest.TestCase):
    def test_competence_outranks_cost_and_needs_a_reason(self):
        # claude is not the cheapest; branch (a) still picks claude.
        d = ra.choose_reviewer("gemini", ["desi", "dmitri"], best="claude",
                               best_reason="only Claude has reviewed this literature")
        self.assertEqual(d["method"], "competence")
        self.assertEqual(d["reviewer"], "claude")

    def test_a_competence_claim_without_a_reason_is_refused(self):
        with self.assertRaises(ValueError):
            ra.choose_reviewer("gemini", ["desi"], best="claude")
        with self.assertRaises(ValueError):
            ra.choose_reviewer("gemini", ["desi"], best="claude", best_reason="   ")

    def test_the_author_is_never_assigned_its_own_work(self):
        # desi is in the band and is the author; the pool must drop it.
        rng = random.Random(0)
        for _ in range(50):
            d = ra.choose_reviewer("desi", ["desi", "dmitri"], rng=rng)
            self.assertNotEqual(d["reviewer"], "desi")
            self.assertEqual(d["reviewer"], "dmitri")

    def test_best_suited_but_is_the_author_falls_to_the_cost_draw(self):
        rng = random.Random(1)
        d = ra.choose_reviewer("desi", ["desi", "dmitri"], best="desi",
                               best_reason="author knows it best", rng=rng)
        self.assertEqual(d["method"], "cost-draw")
        self.assertEqual(d["reviewer"], "dmitri")
        self.assertIn("excluded", d["reason"])

    def test_a_band_of_only_the_author_is_refused_not_silently_picked(self):
        with self.assertRaises(ValueError):
            ra.choose_reviewer("desi", ["desi"])

    def test_the_draw_is_uniform_over_the_whole_pool(self):
        # Every eligible band member must be reachable, and roughly evenly.
        pool = ["claude", "desi", "gemini", "tarik"]
        rng = random.Random(12345)
        counts = {n: 0 for n in pool}
        for _ in range(4000):
            counts[ra.choose_reviewer("dmitri", pool, rng=rng)["reviewer"]] += 1
        self.assertEqual(set(counts), set(pool))
        for n, c in counts.items():
            self.assertGreater(c, 600, f"{n} under-drawn: {c}")
            self.assertLess(c, 1400, f"{n} over-drawn: {c}")


class TestFreeze(unittest.TestCase):
    def test_an_assignment_does_not_re_roll_when_the_band_changes(self):
        with tempfile.TemporaryDirectory() as t:
            store = Path(t) / "assignments.jsonl"
            first = ra.assign("run-x", "desi", band_of(["desi", "dmitri"]),
                              rng=random.Random(0), path=store)
            # A later call, with a completely different band and a different best, must not move it.
            again = ra.assign("run-x", "desi", band_of(["claude", "tarik"]),
                              best="claude", best_reason="changed my mind",
                              rng=random.Random(9), path=store)
            self.assertEqual(first["reviewer"], again["reviewer"])
            self.assertEqual(again["band"], first["band"])
            self.assertEqual(again["assigned_utc"], first["assigned_utc"])

    def test_the_store_is_append_only_and_last_line_wins(self):
        with tempfile.TemporaryDirectory() as t:
            store = Path(t) / "assignments.jsonl"
            ra.assign("a", "desi", band_of(["dmitri", "claude"]), rng=random.Random(0), path=store)
            ra.assign("b", "desi", band_of(["dmitri", "claude"]), rng=random.Random(0), path=store)
            recs = ra.read_assignments(store)
            self.assertEqual(set(recs), {"a", "b"})
            self.assertTrue(store.read_text().strip().count("\n") == 1)  # two lines, append-only

    def test_a_frozen_record_carries_the_band_date_and_a_timestamp(self):
        with tempfile.TemporaryDirectory() as t:
            store = Path(t) / "assignments.jsonl"
            rec = ra.assign("run-y", "claude", band_of(["desi", "dmitri"], as_of="2026-10-09"),
                            rng=random.Random(3), path=store)
            self.assertEqual(rec["band_as_of"], "2026-10-09")
            self.assertEqual(rec["author"], "claude")
            self.assertIn("assigned_utc", rec)
            self.assertEqual(rec["method"], "cost-draw")


if __name__ == "__main__":
    unittest.main(verbosity=2)
