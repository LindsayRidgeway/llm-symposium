#!/usr/bin/env python3
"""Tests for the reviewer-assignment algorithm — who reviews a waiting item, decided once.

The four things that make an assignment real rather than a label, and are therefore pinned here:
  1. the author is never the reviewer, in either branch;
  2. branch (a) carries a written reason, because an unnamed judgement is a mood;
  3. branch (b) draws only from the band (the least expensive eligible set), and the draw is recorded;
  4. the draw is frozen — an item that already carries a name is never re-drawn.

No network. Run: python3 tests/test_review_assignment.py
"""
import datetime as dt
import json
import random
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from channels import item_ledger as il  # noqa: E402
from channels import review_assignment as ra  # noqa: E402

NOW = dt.datetime(2026, 10, 9, 16, 40, tzinfo=dt.timezone.utc)
BAND = {"band": ["desi", "dmitri"], "prices": {"desi": 0.01, "dmitri": 0.01, "gemini": 0.59},
        "generated_utc": "2026-10-09T16:40:00Z", "max_age_days": 45}


def item(i, amigo, filed="2026-10-01T00:00:00Z", **kw):
    return dict({"id": i, "amigo": amigo, "scope": "internal", "state": None,
                 "title": i, "filed_utc": filed}, **kw)


class TestTheBand(unittest.TestCase):
    def test_the_band_is_the_whole_minimum_set_not_one_winner(self):
        # A tie is the normal case (Desi and Dmitri share a model), and a single winner collapses
        # the random branch back into "always the cheapest" — branch (a) wearing a price list.
        self.assertEqual(ra.least_expensive({"desi": 0.01, "dmitri": 0.01, "gemini": 0.59}),
                         ["desi", "dmitri"])

    def test_a_lone_cheapest_is_still_a_set_of_one(self):
        self.assertEqual(ra.least_expensive({"desi": 0.01, "gemini": 0.59}), ["desi"])

    def test_a_band_that_disagrees_with_its_prices_is_a_problem(self):
        bad = dict(BAND, band=["gemini"])
        self.assertTrue(any("least expensive" in p for p in ra.band_problems(bad)))

    def test_an_empty_or_unpriced_band_is_a_problem(self):
        self.assertTrue(ra.band_problems({"band": [], "prices": {}}))
        self.assertTrue(any("empty" in p for p in ra.band_problems(
            {"band": [], "prices": {"desi": 0.01}, "generated_utc": "2026-10-09T16:40:00Z"})))

    def test_an_unknown_amigo_in_the_band_is_a_problem(self):
        bad = {"band": ["desi", "claude", "ghost"], "prices": {"desi": 0.01, "claude": 0.01},
               "generated_utc": "2026-10-09T16:40:00Z"}
        self.assertTrue(any("ghost" in p for p in ra.band_problems(bad)))

    def test_a_consistent_band_has_no_problems(self):
        good = {"band": ["desi", "dmitri"], "prices": {"desi": 0.01, "dmitri": 0.01},
                "generated_utc": "2026-10-09T16:40:00Z", "max_age_days": 45}
        self.assertEqual(ra.band_problems(good), [])

    def test_age_and_staleness(self):
        fresh = {"generated_utc": "2026-10-01T00:00:00Z", "max_age_days": 45}
        old = {"generated_utc": "2026-08-01T00:00:00Z", "max_age_days": 45}
        self.assertFalse(ra.band_is_stale(fresh, NOW))
        self.assertTrue(ra.band_is_stale(old, NOW))
        # An unreadable date is stale, not fresh: it cannot be shown to be current.
        self.assertTrue(ra.band_is_stale({"generated_utc": None}))

    def test_build_and_refresh_derive_the_band_from_the_prices(self):
        band = ra.build_band({"desi": 0.01, "dmitri": 0.01, "gemini": 0.59}, source="s", now=NOW)
        self.assertEqual(band["band"], ["desi", "dmitri"])
        self.assertEqual(band["generated_utc"], "2026-10-09T16:40:00Z")
        with tempfile.TemporaryDirectory() as t:
            path = Path(t) / "band.json"
            path.write_text(json.dumps(dict(band, band=["gemini"], generated_utc=None)),
                            encoding="utf-8")
            out = ra.refresh_band(path, now=NOW)
            self.assertEqual(out["band"], ["desi", "dmitri"])       # recomputed from prices
            self.assertEqual(ra.band_problems(ra.load_band(path)), [])

    def test_the_shipped_cache_is_consistent_and_names_two_cheapest(self):
        band = ra.load_band()
        self.assertEqual(ra.band_problems(band), [])
        self.assertEqual(band["band"], ["desi", "dmitri"])


class TestBranchA(unittest.TestCase):
    def test_a_best_suited_amigo_is_assigned_with_a_reason(self):
        a = ra.choose_reviewer(item("x", "claude"), band=BAND, best_suited="gemini",
                               reason="only Gemini has read the source", now=NOW)
        self.assertEqual(a["assigned_reviewer"], "gemini")
        self.assertEqual(a["branch"], "a")
        self.assertEqual(a["assign_reason"], "only Gemini has read the source")
        self.assertEqual(a["assigned_utc"], "2026-10-09T16:40:00Z")

    def test_the_author_is_refused_even_when_best_suited(self):
        with self.assertRaises(ValueError):
            ra.choose_reviewer(item("x", "gemini"), band=BAND, best_suited="gemini",
                               reason="obviously me", now=NOW)

    def test_branch_a_without_a_written_reason_is_refused(self):
        with self.assertRaises(ValueError):
            ra.choose_reviewer(item("x", "claude"), band=BAND, best_suited="gemini",
                               reason="   ", now=NOW)


class TestBranchB(unittest.TestCase):
    def test_it_draws_only_from_the_band(self):
        for _ in range(50):
            a = ra.choose_reviewer(item("x", "claude"), band=BAND,
                                   rng=random.Random(), now=NOW)
            self.assertIn(a["assigned_reviewer"], ["desi", "dmitri"])
            self.assertEqual(a["branch"], "b")
            self.assertEqual(a["pool"], ["desi", "dmitri"])
            self.assertEqual(a["assign_reason"],
                             "drawn from the least expensive at assignment time (['desi', 'dmitri'])")

    def test_the_author_is_never_drawn(self):
        # An item Desi performed cannot be assigned to Desi, even though Desi is in the band.
        for _ in range(50):
            a = ra.choose_reviewer(item("x", "desi"), band=BAND, rng=random.Random(), now=NOW)
            self.assertEqual(a["assigned_reviewer"], "dmitri")
            self.assertEqual(a["pool"], ["dmitri"])

    def test_it_falls_back_to_everyone_else_when_the_band_leaves_no_one(self):
        # The whole band is the author -> the band cannot supply a reviewer, so the pool widens.
        for _ in range(20):
            a = ra.choose_reviewer(item("x", "desi"), band={"band": ["desi"]},
                                   rng=random.Random(), now=NOW)
            self.assertNotEqual(a["assigned_reviewer"], "desi")
            self.assertEqual(a["pool"], sorted(["claude", "gemini", "tarik", "dmitri"]))
            self.assertIn("no eligible reviewer", a["assign_reason"])

    def test_with_no_band_it_draws_from_everyone_else(self):
        a = ra.choose_reviewer(item("x", "tarik"), band=None, rng=random.Random(0), now=NOW)
        self.assertNotEqual(a["assigned_reviewer"], "tarik")
        self.assertIn("no usable band", a["assign_reason"])

    def test_a_fixed_seed_reproduces_the_draw(self):
        one = ra.choose_reviewer(item("x", "claude"), band=BAND, rng=random.Random(7), now=NOW)
        two = ra.choose_reviewer(item("x", "claude"), band=BAND, rng=random.Random(7), now=NOW)
        self.assertEqual(one["assigned_reviewer"], two["assigned_reviewer"])

    def test_an_authorless_item_is_refused_rather_than_reviewed_by_itself(self):
        with self.assertRaises(ValueError):
            ra.choose_reviewer({"id": "x"}, band=BAND, now=NOW)


class TestTheFreeze(unittest.TestCase):
    def setUp(self):
        self.items = {
            "old": item("old", "gemini", "2026-09-15T00:00:00Z"),
            "new": item("new", "claude", "2026-10-01T00:00:00Z"),
            "done": item("done", "tarik", "2026-09-01T00:00:00Z",
                         state="accomplished", assigned_reviewer="desi"),
        }

    def test_only_unassigned_waiting_items_are_pending(self):
        self.assertEqual([r["id"] for r in ra.unassigned_waiting(self.items)],
                         ["old", "new"])

    def test_an_already_assigned_item_is_not_reassigned(self):
        rows = ra.assign_pending(self.items, band=BAND, limit=5, rng=random.Random(1), now=NOW)
        self.assertEqual([r["id"] for r in rows], ["old", "new"])
        for rec in rows:                      # fold the assignments back in
            self.items[rec["id"]] = rec
        self.assertEqual(ra.assign_pending(self.items, band=BAND, limit=5, now=NOW), [])

    def test_assigned_to_is_the_reviewers_own_queue(self):
        rows = ra.assign_pending(self.items, band=BAND, limit=5, rng=random.Random(1), now=NOW)
        for rec in rows:
            self.items[rec["id"]] = rec
        for who in ("desi", "dmitri"):
            for rec in ra.assigned_to(self.items, who):
                self.assertEqual(rec["assigned_reviewer"], who)
        total = sum(len(ra.assigned_to(self.items, w)) for w in ("desi", "dmitri"))
        self.assertEqual(total, len(rows))

    def test_the_assignment_appends_and_the_ledger_collapses_it(self):
        with tempfile.TemporaryDirectory() as t:
            path = Path(t) / "items.jsonl"
            il.append([item("old", "gemini", "2026-09-15T00:00:00Z")], path)
            rows = ra.assign_pending(il.load(path), band=BAND, limit=5, rng=random.Random(1), now=NOW)
            ra.apply(rows, path)
            lines = path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 2)                 # one filing, one assignment line
            back = il.load(path)["old"]
            self.assertEqual(back["assigned_reviewer"], back["assigned_reviewer"])
            self.assertEqual(back["branch"], "b")


class TestTheShippedFile(unittest.TestCase):
    def test_every_amigo_has_a_price(self):
        band = ra.load_band()
        for who in ra.AMIGOS:
            self.assertIn(who, band["prices"], f"{who} has no price in the cache")

    def test_the_source_is_named_so_a_stale_file_is_visible(self):
        self.assertTrue(ra.load_band()["source"].strip())


if __name__ == "__main__":
    unittest.main(verbosity=2)
