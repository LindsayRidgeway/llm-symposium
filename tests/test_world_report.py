#!/usr/bin/env python3
"""Tests for scripts/world_report.py — six kinds of good, each with its own proof.

History in two steps, both 2026-10-25:
  1. the founder asked for a measure of real-world productivity; the first version counted only
     "corrections sent to the owner of someone else's document";
  2. he objected that this is a ridiculously narrow definition of good — art, discovery, money raised,
     company given and physical work all count. The narrowness had a cause worth pinning: it was the
     only kind a script could grep for.

So these tests guard the two ways this page can go wrong: collapsing every kind into one number, and
counting something we did for ourselves, or something nobody outside has acknowledged, as good.
"""
import datetime as dt
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts import world_report as wr  # noqa: E402

ZERO = {k: 0 for k in wr.GOOD + ("obtained",)}


class KindTest(unittest.TestCase):
    def test_all_six_kinds_exist_and_none_is_a_synonym_of_another(self):
        self.assertEqual(len(set(wr.GOOD)), 6)
        self.assertIn("art", wr.GOOD)
        self.assertIn("care", wr.GOOD)
        self.assertIn("handwork", wr.GOOD)
        self.assertNotIn("obtained", wr.GOOD)      # ours, not the world's

    def test_the_old_names_still_land_somewhere(self):
        # two entries predate the rewrite; losing them silently would be its own small dishonesty
        self.assertEqual(wr.kind_of({"kind": "repaired"}), "repair")
        self.assertEqual(wr.kind_of({"kind": "reported"}), "discovery")
        self.assertEqual(wr.kind_of({"kind": "helped_us"}), "obtained")

    def test_art_counts_as_good(self):
        k = dict(ZERO, art=3)
        real = wr.effects
        wr.effects = lambda: [{"kind": "art", "who": "a named reader", "answer": "it helped"}
                              for _ in range(3)]
        try:
            self.assertEqual(wr.by_kind()["art"], 3)
            self.assertIn("named person", wr.verdict(k))
        finally:
            wr.effects = real

    def test_something_obtained_for_ourselves_is_never_world_good(self):
        self.assertTrue(wr.verdict(dict(ZERO, obtained=4)).startswith("Nothing"))


class WitnessTest(unittest.TestCase):
    def test_an_entry_nobody_answered_is_not_a_witness(self):
        real = wr.effects
        wr.effects = lambda: [{"kind": "art", "who": "someone", "answer": ""},
                              {"kind": "art", "who": "someone else", "answer": "yes, it moved me"}]
        try:
            self.assertEqual(wr.named_witnesses("art"), 1)
        finally:
            wr.effects = real

    def test_an_entry_with_no_named_person_is_an_intention(self):
        real = wr.effects
        wr.effects = lambda: [{"kind": "funds", "what": "a grant application", "answer": "awarded"}]
        try:
            self.assertEqual(wr.named_witnesses("funds"), 0)
        finally:
            wr.effects = real

    def test_only_repairs_is_called_the_narrowest_kind(self):
        kinds = dict(ZERO, repair=2)
        self.assertIn("narrowest", wr.verdict(kinds))

    def test_a_plural_record_stops_calling_itself_narrow(self):
        kinds = dict(ZERO, repair=1, art=2, care=1)
        text = wr.verdict(kinds)
        self.assertIn("different kinds of good", text)


class LineTest(unittest.TestCase):
    def test_the_line_shows_every_kind_so_none_can_hide(self):
        real_s = wr.strangers
        wr.strangers = lambda: []
        try:
            text = wr.line(dt.datetime(2026, 10, 25, tzinfo=dt.timezone.utc))
        finally:
            wr.strangers = real_s
        for kind in ("art", "discovery", "money", "company", "repair", "handwork"):
            self.assertIn(kind, text, kind)


if __name__ == "__main__":
    unittest.main()
