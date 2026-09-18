#!/usr/bin/env python3
"""Offline tests for the disease-target screen: no network, synthetic counts only.

The band that matters on a dense disease — components co-mentioned but never named together in a
title or abstract — was missing from the first version of the summary, so the screen printed
"(none)" while 26 targets sat in exactly that band. These tests pin the classification so it
cannot silently disappear again, and pin the rule that a failed query (-1) is not read as a zero.
"""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/disease_screen.py"
spec = importlib.util.spec_from_file_location("disease_screen", SCRIPT)
ds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ds)


class VerdictTests(unittest.TestCase):
    def test_failed_query_is_not_a_zero(self):
        self.assertIn("QUERY FAILED", ds.verdict(-1, 0))
        self.assertNotIn("unjoined", ds.verdict(-1, 0).lower())

    def test_strict_join_is_prior_work(self):
        self.assertIn("already published together", ds.verdict(9, 1))

    def test_true_zero_is_a_candidate_not_a_finding(self):
        v = ds.verdict(0, 0)
        self.assertIn("unjoined", v)
        self.assertIn("NOT a finding", v)

    def test_incidental_band_says_read_them(self):
        self.assertIn("incidental", ds.verdict(3, 0))

    def test_co_mentioned_band_is_named(self):
        self.assertIn("discussed", ds.verdict(50, 0))


class SummaryBandTests(unittest.TestCase):
    def _run(self, rows):
        """Feed synthetic counts through run() by stubbing every network call."""
        counts = {sym: (a, s) for sym, a, s in rows}
        ds.any_field = lambda sym, dis: counts[sym][0]
        ds.strict = lambda sym, dis: counts[sym][1]
        ds.epmc = lambda term: 10
        ds.trials = lambda cond: 5
        ds.ot_disease = lambda name: ("EFO:0001065", "endometriosis")
        ds.ot_score = lambda sym, efo: None
        targets = [{"category": "t", "symbol": sym} for sym, _, _ in rows]
        return ds.run("endometriosis", targets, use_ot=False)

    def test_all_four_bands_are_separated(self):
        res = self._run([
            ("JOINED", 500, 40),   # title/abstract join -> prior work
            ("ZERO", 0, 0),        # nothing anywhere -> candidate
            ("INC", 3, 0),         # incidental only
            ("THIN", 25, 0),       # co-mentioned, never studied  <-- the band that was hidden
        ])
        self.assertEqual(res["joined_in_title_or_abstract"], ["JOINED"])
        self.assertEqual(res["unjoined"], ["ZERO"])
        self.assertEqual(res["incidental_any_field_only"], ["INC"])
        self.assertEqual(res["no_strict_join_but_discussed"], ["THIN"])
        self.assertEqual(res["no_title_abstract_join"], ["ZERO", "INC", "THIN"])

    def test_empty_candidate_band_is_reported_as_empty_not_omitted(self):
        res = self._run([("JOINED", 100, 9)])
        self.assertEqual(res["unjoined"], [])
        self.assertEqual(res["no_title_abstract_join"], [])


class AliasTests(unittest.TestCase):
    """A condition has more than one spelling and the counts move with spelling.

    `SLC19A3 × ME/CFS` was 0 under one spelling and 1 under the union of three, so a
    single-name query can return a false zero — which in this program becomes a novelty claim.
    These pin the union query and the fact that a one-spelling condition is unchanged.
    """

    def test_single_name_is_unchanged(self):
        self.assertEqual(ds.disease_names("endometriosis"), ["endometriosis"])

    def test_pipe_separated_spellings_split(self):
        self.assertEqual(
            ds.disease_names("pudendal neuralgia|pudendal nerve entrapment"),
            ["pudendal neuralgia", "pudendal nerve entrapment"])

    def test_a_list_is_accepted(self):
        self.assertEqual(ds.disease_names(["a", "b"]), ["a", "b"])

    def _capture(self, fn, *a):
        seen = []
        real = ds.epmc
        ds.epmc = lambda term: (seen.append(term), 0)[1]
        try:
            fn(*a)
        finally:
            ds.epmc = real
        return seen[0]

    def test_one_spelling_query_matches_the_original_form(self):
        q = self._capture(ds.strict, "PDHA1", "endometriosis")
        self.assertEqual(q, '(TITLE:"PDHA1" OR ABSTRACT:"PDHA1") AND '
                            '(TITLE:"endometriosis" OR ABSTRACT:"endometriosis")')
        self.assertEqual(self._capture(ds.any_field, "PDHA1", "endometriosis"),
                         '"PDHA1" AND "endometriosis"')

    def test_several_spellings_become_an_or_group_in_both_fields(self):
        q = self._capture(ds.strict, "SCN9A", "pudendal neuralgia|pudendal neuropathy")
        self.assertIn('TITLE:("pudendal neuralgia" OR "pudendal neuropathy")', q)
        self.assertIn('ABSTRACT:("pudendal neuralgia" OR "pudendal neuropathy")', q)
        self.assertIn('TITLE:"SCN9A"', q)
        self.assertIn('ABSTRACT:"SCN9A"', q)
        self.assertEqual(self._capture(ds.any_field, "SCN9A", "pudendal neuralgia|pudendal neuropathy"),
                         '"SCN9A" AND ("pudendal neuralgia" OR "pudendal neuropathy")')


if __name__ == "__main__":
    unittest.main()
