#!/usr/bin/env python3
"""Tests for scripts/world_report.py — a generator, two columns, and no closed list of goods.

Three corrections arrived in one afternoon (2026-10-25), and each one is pinned here because each
was a way of being confidently wrong:

  1. corrections to other people's documents are not the definition of good — that was a grep artefact;
  2. a list of six kinds was still just the founder's examples in ten seconds — so the kinds are
     free text and the *generator* (four questions) is what the page prints;
  3. "a manuscript nobody has met is a manuscript" was wrong about value: Bach lost nothing in a
     century of being unplayed. Value and confirmation are two columns, and neither may stand in for
     the other.
"""
import datetime as dt
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts import world_report as wr  # noqa: E402


def with_effects(rows):
    def deco(fn):
        def wrapper(*a, **kw):
            real = wr.effects
            wr.effects = lambda: rows
            try:
                return fn(*a, **kw)
            finally:
                wr.effects = real
        return wrapper
    return deco


class GeneratorTest(unittest.TestCase):
    def test_the_page_prints_the_questions_not_a_list_of_kinds(self):
        text = wr.page(dt.datetime(2026, 10, 25, tzinfo=dt.timezone.utc))
        for question in ("Who is worse off", "What limits them",
                         "would not otherwise happen", "worse off"):
            self.assertIn(question, text)
        self.assertNotIn("six kinds", text)


class FreeTextKindTest(unittest.TestCase):
    @with_effects([{"kind": "chores for a housebound neighbour", "who": "A", "answer": "yes"},
                   {"kind": "litter picked from a beach", "who": "B", "answer": ""},
                   {"kind": "security for a vulnerable person", "who": "C", "answer": "they slept"}])
    def test_a_kind_nobody_listed_still_counts(self):
        k = wr.by_kind()
        self.assertEqual(k["chores for a housebound neighbour"], 1)
        self.assertEqual(wr.columns(), (3, 2))

    @with_effects([{"kind": "obtained", "who": "a vendor", "answer": "sent it"},
                   {"kind": "helped_us", "who": "a vendor", "answer": "sent it"}])
    def test_what_we_got_for_ourselves_is_not_world_good(self):
        self.assertEqual(wr.columns(), (0, 0))
        self.assertTrue(wr.verdict().startswith("Nothing in the world column"))


class TwoColumnsTest(unittest.TestCase):
    @with_effects([{"kind": "a string quartet nobody has played", "who": "future listeners",
                    "value_basis": "written and finished; it exists", "answer": ""}])
    def test_value_without_recognition_is_not_called_worthless(self):
        """Bach, 1723-1900: unplayed, unappreciated, and not one iota less good."""
        value, confirmed = wr.columns()
        self.assertEqual((value, confirmed), (1, 0))
        self.assertIn("Unconfirmed is not worthless", wr.page())
        self.assertNotIn("Nothing in the world column", wr.verdict())

    @with_effects([{"kind": "a poem given to one reader", "who": "one reader",
                    "value_basis": "it was written for her", "answer": "she read it twice"}])
    def test_recognition_does_not_inflate_value(self):
        self.assertEqual(wr.columns(), (1, 1))

    @with_effects([{"kind": "a repair", "who": "a maintainer", "answer": "merged"},
                   {"kind": "a repair", "who": "a maintainer", "answer": ""}])
    def test_partial_confirmation_is_stated_as_partial(self):
        self.assertIn("waiting", wr.verdict())


class LineTest(unittest.TestCase):
    def test_the_line_carries_both_columns(self):
        real = wr.strangers
        wr.strangers = lambda: []
        try:
            text = wr.line(dt.datetime(2026, 10, 25, tzinfo=dt.timezone.utc))
        finally:
            wr.strangers = real
        self.assertIn("confirmed", text)
        self.assertIn("—", text)      # no stranger ever is a dash, not a zero


if __name__ == "__main__":
    unittest.main()
