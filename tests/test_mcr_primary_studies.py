#!/usr/bin/env python3
"""Pin the MCR primary-study pull (agenda item 23) to its numbers, offline.

Written 2026-10-07 (Desi, clock wake) with `research/mcr-colistin-primary-studies.md`,
`research/mcr-primary-studies.json` and `research/mcr-primary-studies-raw.json`.

The seed review publishes only 4 of the 9 harmonisation columns the item asks for and prints two rows
that disagree with themselves. This pull recovers the missing columns from the primary papers and
records the divergences between the seed and the primary source. Tests run offline, so this file
cannot re-fetch Europe PMC; instead it pins:

  * the six distinct primary papers behind the eight key rows, by PMID, and the raw fetch carrying
    each one;
  * the numbers the write-up asserts from the Ewers 2022 Table 1 full text -- including that the
    per-country rows are internally consistent (sum to the printed total) except where the write-up
    says Spain and Portugal differ; and
  * that each recorded divergence still matches BOTH the live seed table it corrects and the primary
    value it corrects it to, so a later repair of the seed cannot leave this artefact quietly wrong.
"""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "research" / "mcr-colistin-seed.json"
REC = ROOT / "research" / "mcr-primary-studies.json"
RAW = ROOT / "research" / "mcr-primary-studies-raw.json"
MD = ROOT / "research" / "mcr-colistin-primary-studies.md"

DISTINCT_PMIDS = {"26603172", "28056227", "27855068", "36569100", "36687643", "28018876"}
REQUIRED_KEYS = {
    "row", "pmid", "citation", "collection_years", "mcr_variants",
    "detection_method", "sampling_design", "denominator_unit", "verdict",
}
# Primary paper values the write-up asserts from Ewers Table 1 (full text) and Treilles's text.
EWERS = {"isolates": 7614, "mcr1": 793, "mcr2": 12, "germany_mcr1": 707, "spain_mcr1": 16,
         "portugal_mcr1": 17, "belgium_mcr1": 11, "belgium_mcr2": 9}
TREILLES_POSITIVE = 149  # 65 breeding + 84 fattening


class McrPrimaryStudiesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rec = json.loads(REC.read_text())
        cls.raw = json.loads(RAW.read_text())
        cls.seed = json.loads(SEED.read_text())
        cls.md = MD.read_text()
        cls.seed_rows = {r["sl"]: r for r in cls.seed["rows"]}

    def test_files_exist(self):
        for p in (REC, RAW, MD, SEED):
            self.assertTrue(p.exists(), f"missing {p.name}")

    def test_six_distinct_primaries_behind_the_eight_rows(self):
        papers = self.rec["papers"]
        self.assertEqual(len(papers), 7, "seven row-targets (17a and 17h/17i share one paper)")
        self.assertEqual({p["pmid"] for p in papers}, DISTINCT_PMIDS)
        self.assertEqual(len({p["pmid"] for p in papers}), 6, "six distinct primary papers")

    def test_distinct_primaries_are_present_in_the_raw_fetch(self):
        raw_pmids = {r["pmid"] for r in self.raw["records"]}
        self.assertEqual(raw_pmids, DISTINCT_PMIDS)

    def test_every_paper_row_is_complete(self):
        for p in self.rec["papers"]:
            missing = REQUIRED_KEYS - set(p)
            self.assertFalse(missing, f"row {p.get('row')} missing keys {missing}")

    def test_ewers_table1_reconciles_to_its_printed_total(self):
        t = self.rec["ewers_table1"]
        rows = t["rows"]
        self.assertEqual(sum(r[1] for r in rows), EWERS["isolates"])
        self.assertEqual(sum(r[2] for r in rows), EWERS["mcr1"])
        self.assertEqual(sum(r[4] for r in rows), EWERS["mcr2"])
        self.assertEqual(t["totals"]["isolates"], EWERS["isolates"])
        self.assertEqual(t["totals"]["mcr1_n"], EWERS["mcr1"])

    def test_ewers_germany_and_iberia_numbers_are_as_asserted(self):
        by = {r[0]: r for r in self.rec["ewers_table1"]["rows"]}
        self.assertEqual(by["Germany"][2], EWERS["germany_mcr1"])
        self.assertEqual(by["Spain"][2], EWERS["spain_mcr1"])
        self.assertEqual(by["Portugal"][2], EWERS["portugal_mcr1"])
        self.assertEqual(by["Belgium"][2], EWERS["belgium_mcr1"])
        self.assertEqual(by["Belgium"][4], EWERS["belgium_mcr2"])
        # the whole point of the anomaly: the two rows are NOT identical in the primary
        self.assertNotEqual(by["Spain"][2], by["Portugal"][2])

    def test_seed_carries_the_defective_values_this_artefact_corrects(self):
        # If the seed is later repaired, these assertions fail on purpose: update the artefact too.
        self.assertEqual(self.seed_rows["17 (a)"]["mcr_positive"], 709)
        self.assertEqual(self.seed_rows["17 (a)"]["n_isolates"], 6158)
        self.assertEqual(self.seed_rows["17 (h)"]["mcr_positive"], 17)  # Spain, copies Portugal
        self.assertEqual(self.seed_rows["17 (i)"]["mcr_positive"], 17)  # Portugal
        self.assertEqual(self.seed_rows["17 (e)"]["mcr_positive"], 20)  # Belgium = 11 + 9
        self.assertEqual(self.seed_rows["19"]["mcr_positive"], 49)
        self.assertEqual(self.seed_rows["19"]["n_isolates"], 1701)

    def test_divergences_pair_seed_and_primary_values(self):
        div = self.rec["divergences"]
        self.assertEqual(len(div), 6)
        got = {(d["row"], d["field"]): (d["seed"], d["primary"]) for d in div}
        self.assertEqual(got[("17 (a)", "numerator")], (709, 707))
        self.assertEqual(got[("17 (a)", "prevalence_pct")], (10.42, 11.5))
        self.assertEqual(got[("17 (h)", "numerator")], (17, 16))
        self.assertEqual(got[("17 (e)", "numerator")], (20, 11))
        self.assertEqual(got[("19", "numerator")], (49, TREILLES_POSITIVE))
        self.assertEqual(got[("19", "denominator_unit")], ("isolates", "animals"))

    def test_coverage_counts(self):
        c = self.rec["coverage"]
        self.assertEqual(c["mcr_variant_recovered"], 6)
        self.assertEqual(c["detection_method_recovered"], 6)
        self.assertEqual(c["sampling_design_recovered"], 6)
        self.assertEqual(c["collection_year_recovered_from_abstract"], 3)
        self.assertEqual(c["collection_year_still_missing"], ["6", "13"])

    def test_markdown_states_the_resolved_numbers(self):
        for needle in ("707", "11.5", "16", "57.1", "60.7", "149", "1701", "10.4"):
            self.assertIn(needle, self.md, f"{needle} not stated in the write-up")
        # the write-up must name the primary identifiers it depends on
        for pmid in DISTINCT_PMIDS:
            self.assertIn(pmid, self.md, f"PMID {pmid} not cited in the write-up")


if __name__ == "__main__":
    unittest.main(verbosity=2)
