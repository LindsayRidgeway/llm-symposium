#!/usr/bin/env python3
"""Pin the DDAH1-arginine evidence table to its source, mechanically.

Written 2026-09-29 (Desi, clock wake) with
`research/ddah1-arginine-ukbiobank-evidence-table.md`. The table is a reading of one
paper — Lehrer & Rheinstein, *Cureus* 2026;18(8):e114415 (PMID 42729959, PMC13564308) —
and its whole value is that a stranger can check every number against the article.
This test does the cheap half of that check: it fails if the headline figures in the
markdown drift away from the machine-readable source record, and it fails if the record's
citation stops matching the one printed in the table.

It cannot re-fetch the paper (tests run offline), so it pins internal consistency between
the artefact and the transcribed source, and it pins the abstract-level numbers against
the abstract text itself, which is stored raw in the record.
"""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "research" / "ddah1-ukbiobank-source-record.json"
TABLE = ROOT / "research" / "ddah1-arginine-ukbiobank-evidence-table.md"


class Ddah1EvidenceTableTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rec = json.loads(RECORD.read_text())
        cls.md = TABLE.read_text()

    def test_both_files_exist(self):
        self.assertTrue(RECORD.exists(), "source record missing")
        self.assertTrue(TABLE.exists(), "evidence table missing")

    def test_citation_matches_between_table_and_record(self):
        for ident in ("42729959", "PMC13564308", "10.7759/cureus.114415"):
            self.assertIn(ident, self.md, f"{ident} not cited in the table")
            flat = json.dumps(self.rec)
            self.assertIn(ident, flat, f"{ident} not in the source record")

    def test_abstract_level_numbers_are_in_the_raw_abstract(self):
        abs_text = self.rec["abstract"]
        for token in ("50,988", "0.604", "0.0033", "1.431", "0.000108",
                      "Olink Explore 3072"):
            self.assertIn(token, abs_text,
                          f"{token} is used in the table but is not in the raw abstract")

    def test_headline_figures_appear_in_the_markdown(self):
        for token in ("50,988", "271", "11,003", "1,976",
                      "0.604", "0.0033", "1.431", "0.000108",
                      "2.53", "0.012", "-3.22", "-3.07", "0.1399", "0.0396",
                      "3.00", "8.27", "0.928", "0.147", "-0.052", "0.016"):
            self.assertIn(token, self.md, f"headline figure {token} missing from the table")

    def test_record_extraction_agrees_with_markdown_claims(self):
        c = self.rec["full_text_extraction"]
        self.assertEqual(c["cohort"]["headline_n"], 50988)
        self.assertEqual(c["cohort"]["ad_cases"], 271)
        self.assertEqual(c["cohort"]["arginine_available"], 11003)
        self.assertEqual(c["cohort"]["imaging_subset_n"], 1976)
        ml = c["multivariable_logistic"]
        self.assertEqual(ml["arginine_main"]["OR"], 0.604)
        self.assertEqual(ml["arginine_main"]["p"], 0.0033)
        self.assertEqual(ml["ddah1_x_arginine"]["OR"], 1.431)
        self.assertEqual(ml["ddah1_x_arginine"]["p"], 0.000108)
        self.assertEqual(ml["ddah1_main"]["p"], 0.147)
        self.assertEqual(ml["apoe_e4_heterozygote"]["OR"], 3.00)
        self.assertEqual(ml["apoe_e4_homozygote"]["OR"], 8.27)
        self.assertEqual(ml["education_per_year"]["OR"], 0.928)
        self.assertEqual(c["mri"]["hippocampal"]["beta_ddah1"], -0.052)
        self.assertEqual(c["mri"]["hippocampal"]["p_ddah1"], 0.016)

    def test_the_inconsistency_finding_is_complete(self):
        """The table claims the same DDAH1 case-control comparison is reported four ways.
        If the record does not hold four distinct reports, the finding is wrong."""
        reports = self.rec["full_text_extraction"]["ddah1_case_control_reported_four_ways"]
        self.assertEqual(len(reports), 4, "expected four divergent reports")
        places = {r["where"] for r in reports}
        self.assertEqual(places, {"Table 1", "results body text",
                                  "Figure 1 caption", "abstract"})
        tvals = {r["t"] for r in reports if r["t"] is not None}
        self.assertEqual(tvals, {2.53, -3.22, -3.07})


if __name__ == "__main__":
    unittest.main(verbosity=2)
