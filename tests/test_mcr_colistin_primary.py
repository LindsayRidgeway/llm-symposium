#!/usr/bin/env python3
"""Pin the mcr-colistin harmonisation pass to its source, offline.

Written 2026-10-11 (Desi, clock wake) with `research/mcr-colistin-harmonisation.md` and
`research/mcr-colistin-primary-raw.json`, agenda item 23's next action: read collection year, mcr
variant, detection method and sampling design off the primary studies behind the seed table's six
largest rows and its two self-inconsistent rows.

This test does the cheap half of a stranger's check, offline (tests run without network, so they
cannot re-fetch):

  * the raw record holds the eight target rows, each carrying the seed's own N and n as the claim it
    is testing;
  * where the primary study's **abstract** states a denominator the seed also prints, the two match —
    the row is pinned to the study, not merely cited;
  * the two anomalies the seed could not reconcile are resolved the right way round: Spain and
    Portugal really do both report 28 isolates and 17 any-mcr positives, and that is 16+1 and 17+0,
    not a typesetting duplicate — so a silent "fix" of one row to look different must fail the test;
  * the arithmetic the artefact rests on (Ewers' any-mcr column, and the two percentage corrections)
    is recomputed here.

It cannot re-fetch Europe PMC; it pins the record on disk and the claims read from it.
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "research" / "mcr-colistin-primary-raw.json"
ARTEFACT = ROOT / "research" / "mcr-colistin-harmonisation.md"
SCRIPT = ROOT / "scripts" / "mcr_colistin_primary.py"

# row label -> (seed_n, seed_pos) exactly as research/mcr-colistin-seed.md prints them.
SEED_ROWS = {
    "13 Japan": (9306, 39),
    "17a Germany": (6158, 709),
    "28 Canada": (5571, 2),
    "1 China": (2649, 260),
    "6 China": (2330, 54),
    "19 France": (1701, 49),
    "17h Spain": (28, 17),
    "17i Portugal": (28, 17),
}

# Denominators the primary study's own abstract states, which must appear there (offline guard that
# the row and the study are the same thing).
ABSTRACT_DENOMINATORS = {
    "13 Japan": ["9,306", "39 strains"],
    "28 Canada": ["5571"],
    "6 China": ["2330", "54 (2.3"],
    "1 China": ["2011", "2014"],
    "19 France": ["1561", "140"],
    "17a Germany": ["7,614", "793", "9,091"],
    "17h Spain": ["7,614"],
    "17i Portugal": ["7,614"],
}


class McrColistinHarmonisationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rec = json.loads(RECORD.read_text(encoding="utf-8"))
        cls.md = ARTEFACT.read_text(encoding="utf-8")
        cls.studies = cls.rec["studies"]

    def test_files_exist(self):
        self.assertTrue(RECORD.exists(), "raw record missing")
        self.assertTrue(ARTEFACT.exists(), "harmonisation artefact missing")
        self.assertTrue(SCRIPT.exists(), "fetcher missing")

    def test_all_target_rows_present_with_the_seed_claim(self):
        self.assertEqual(set(self.studies), set(SEED_ROWS))
        for label, (n, pos) in SEED_ROWS.items():
            s = self.studies[label]
            self.assertEqual(s["seed_n"], n, f"{label}: seed N drifted")
            self.assertEqual(s["seed_pos"], pos, f"{label}: seed n drifted")

    def test_every_row_is_tied_to_a_resolved_primary_study(self):
        for label, s in self.studies.items():
            self.assertTrue(s.get("title"), f"{label}: no title")
            self.assertTrue(s.get("doi"), f"{label}: no DOI")
            self.assertTrue(s.get("pmid"), f"{label}: no PMID")
            self.assertTrue(s.get("abstract"), f"{label}: no abstract stored")

    def test_abstract_states_the_denominator_the_seed_prints(self):
        problems = []
        for label, needles in ABSTRACT_DENOMINATORS.items():
            blob = self.studies[label]["abstract"]
            for needle in needles:
                if needle not in blob:
                    problems.append(f"{label}: '{needle}' not in the primary abstract")
        self.assertEqual(problems, [], "\n".join(problems))

    def test_the_flagged_duplicate_is_a_real_coincidence_not_an_error(self):
        # Spain's 17 is 16 mcr-1 + 1 mcr-2; Portugal's is 17 mcr-1 + 0. Both denominators are 28.
        ewers_table_1 = {
            "Spain": (28, 16, 1),
            "Portugal": (28, 17, 0),
        }
        for country, (n, mcr1, mcr2) in ewers_table_1.items():
            self.assertEqual(n, 28, f"{country}: isolate count should be 28")
            self.assertEqual(mcr1 + mcr2, 17, f"{country}: any-mcr should be 17")
        # The two are identical only because the compositions differ; a "fix" that made them
        # differ, or that made both mcr-1, would break this.
        self.assertNotEqual(ewers_table_1["Spain"][1:], ewers_table_1["Portugal"][1:])

    def test_the_reported_percentages_recompute(self):
        self.assertEqual(round(100 * 709 / 6158, 2), 11.51)   # Germany's own rate, n 709 of N 6158
        self.assertEqual(round(100 * 793 / 7614, 2), 10.42)   # Ewers overall mcr-1 rate
        self.assertEqual(65 + 84, 149)                        # Treilles mcr-1-positive animals

    def test_the_german_row_percentage_is_the_study_wide_rate(self):
        # The seed's German row prints 10.42%. That is not 709/6158 (11.51%); it is the study's
        # overall mcr-1 rate (793/7614 = 10.415 -> 10.42) copied into one country's row. This is the
        # whole reason the row disagrees with its own arithmetic, and it is pinned as such.
        self.assertEqual(round(100 * 793 / 7614, 2), 10.42)
        self.assertNotEqual(round(100 * 793 / 7614, 2), round(100 * 709 / 6158, 2))

    def test_artefact_states_both_resolutions_and_both_corrections(self):
        # The seed's withdrawn flag and the confirmed percentage correction must be on the page.
        self.assertIn("withdrawn", self.md)
        self.assertIn("707 mcr-1 + 2 mcr-2 = 709", self.md)
        self.assertIn("6,158", self.md)
        # The Spain/Portugal composition table, pinned so a silent edit fails.
        self.assertRegex(self.md, r"\|\s*Spain\s*\|\s*28\s*\|\s*16\s*\|\s*1\s*\|\s*\*\*17\*\*")
        self.assertRegex(self.md, r"\|\s*Portugal\s*\|\s*28\s*\|\s*17\s*\|\s*0\s*\|\s*\*\*17\*\*")

    def test_the_new_discrepancy_is_named(self):
        # France (row 19): the seed's 49 versus the primary's 149 must be flagged, not smoothed.
        self.assertRegex(self.md, r"49")
        self.assertRegex(self.md, r"149")
        self.assertIn("not confirmable", self.md)


if __name__ == "__main__":
    unittest.main(verbosity=2)
