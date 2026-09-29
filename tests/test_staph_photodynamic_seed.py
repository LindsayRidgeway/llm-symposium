#!/usr/bin/env python3
"""Pin the household-LED photodynamic seed table to its source, mechanically.

Written 2026-09-29 (Desi, clock wake) with `research/staph-photodynamic-seed.md` and
`research/staph-photodynamic-seed.json`, the seed evidence table for agenda item 31.

The table is a reading of one paper — Misba L, Akhtar F, Mujahid S, Khan AU, *J Biophotonics*
2026;19(9):e70358 (PMID 42773775, DOI 10.1002/jbio.70358) — whose full text is paywalled, so the
source record stores the raw abstract exactly as PubMed returned it. This test does the cheap half of
a stranger's check: it fails if a headline figure in the markdown drifts from the machine-readable
record, if the "these tokens are absent from the abstract" claim stops being true, or if the
citation stops matching the one printed in the table.

It cannot re-fetch the paper (tests run offline); it pins internal consistency between artefact and
transcribed source, and pins the abstract-level numbers against the abstract text itself.
"""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "research" / "staph-photodynamic-seed.json"
TABLE = ROOT / "research" / "staph-photodynamic-seed.md"

# Headline figures the table uses, and the identifiers a stranger needs.
HEADLINE_FIGURES = ["4.85", "4.26", "96.22", "48.98", "10 min", "15 min"]
IDENTIFIERS = ["42773775", "10.1002/jbio.70358", "e70358"]
COMPARISON_PMIDS = ["37142073", "42704220", "41763793", "42508329", "42196526", "42256523"]


class StaphPhotodynamicSeedTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rec = json.loads(RECORD.read_text())
        cls.md = TABLE.read_text()

    def test_both_files_exist(self):
        self.assertTrue(RECORD.exists(), "source record missing")
        self.assertTrue(TABLE.exists(), "evidence table missing")

    def test_citation_matches_between_table_and_record(self):
        for ident in IDENTIFIERS:
            self.assertIn(ident, self.md, f"{ident} not cited in the table")
            self.assertIn(ident, json.dumps(self.rec), f"{ident} not in the source record")

    def test_headline_figures_appear_in_the_markdown(self):
        for token in HEADLINE_FIGURES:
            self.assertIn(token, self.md, f"headline figure {token!r} missing from the table")

    def test_headline_figures_are_present_in_the_raw_abstract(self):
        abstract = self.rec["seed"]["abstract_plain"]
        for token in ["4.85", "4.26", "96.22", "48.98"]:
            self.assertIn(token, abstract,
                          f"{token} is used in the table but is not in the raw abstract")

    def test_extraction_agrees_with_the_table(self):
        ext = self.rec["seed"]["extraction"]
        self.assertEqual(ext["exposure_time_min"], {"TBO": 10, "CUR": 15})
        self.assertIn("4.85", ext["log_reduction"]["TBO"])
        self.assertIn("4.26", ext["log_reduction"]["CUR"])
        eps = ext["other_endpoints"]["extracellular_polymeric_substance_reduction_percent"]
        self.assertEqual(eps, {"TBO": 96.22, "CUR": 48.98})
        # The six transferability parameters the table claims are missing must be null.
        for key in ("wavelength_nm", "irradiance_mW_cm2", "fluence_J_cm2",
                    "lamp_to_sample_distance_cm", "temperature_measurement_reported"):
            self.assertIsNone(ext[key], f"{key} is expected to be unstated, got {ext[key]!r}")

    def test_the_absence_claim_is_still_true(self):
        """The core finding is that none of these tokens occurs in the abstract. If a
        later copy of the record smuggled one in, the finding would be false."""
        abstract = self.rec["seed"]["abstract_plain"].lower()
        terms = self.rec["seed"]["terms_absent_from_abstract"]
        self.assertTrue(terms, "the absence claim must name the tokens it checked")
        for t in terms:
            self.assertNotIn(t.lower(), abstract,
                             f"{t!r} is claimed absent but occurs in the abstract")

    def test_comparison_rows_are_all_cited_in_the_table(self):
        rows = self.rec["comparison_rows"]
        self.assertEqual(len(rows), len(COMPARISON_PMIDS))
        self.assertEqual({r["pmid"] for r in rows}, set(COMPARISON_PMIDS))
        for pmid in COMPARISON_PMIDS:
            self.assertIn(pmid, self.md, f"comparison PMID {pmid} missing from the table")

    def test_seed_is_listed_as_closed_access(self):
        """The whole reason the row is incomplete is that the full text is not reachable."""
        self.assertFalse(self.rec["seed"]["is_open_access"])
        self.assertFalse(self.rec["seed"]["in_europe_pmc"])
        self.assertFalse(self.rec["seed"]["full_text_available_here"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
