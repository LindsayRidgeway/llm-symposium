#!/usr/bin/env python3
"""Pin the MCR colistin primary-source verification to its record, offline.

Written 2026-10-08 (Desi, clock wake) with `research/mcr-colistin-primary-verification.md` and
`research/mcr-colistin-primary-verification.json`, the check of agenda item 23's eight named rows
against the primary studies the seed review cites for them.

The JSON stores each primary study's own numbers as transcribed or read this wake (Ewers et al.
2022 Table 1 was transcribed cell-by-cell from the open-access JATS XML, PMC9780603; the other seven
from the studies' abstracts or full text). This test re-derives, from that stored data, the four
things a stranger should be able to recompute by hand:

  * the review's 17(a)-(k) block and the primary Ewers table differ by exactly the stated amounts,
    and the per-country defects are the ones named;
  * the subtotal reconciliation closes — the isolate gap is the dropped "Other countries" row and
    the positive gap is Germany +2, Belgium +9, Spain +1;
  * the three rows called "match" really do match their primary N and n;
  * the review still reproduces the primary's own totals once the four defects are corrected.

It cannot re-fetch the sources (tests run offline); it pins the comparison to the stored record so a
later edit to either side fails here rather than silently.
"""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "research" / "mcr-colistin-primary-verification.json"
PAPER = ROOT / "research" / "mcr-colistin-primary-verification.md"

# The primary's own totals for Ewers 2022 Table 1 (2010-2017 cohort).
EWERS_TOTAL_ISOLATES = 7614
EWERS_TOTAL_MCR1 = 793
# The review's summed 17(a)-(k) sub-rows, as printed in the seed.
REVIEW_17X_ISOLATES = 7582
REVIEW_17X_MCR1 = 805
# The review's "Other countries" row is dropped; the rest of the isolate gap is that row.
EWERS_OTHER_ISOLATES = 32


class McrPrimaryVerificationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rec = json.loads(RECORD.read_text())
        cls.md = PAPER.read_text()

    def test_both_files_exist_and_cite_sources(self):
        self.assertTrue(RECORD.exists(), "verification record missing")
        self.assertTrue(PAPER.exists(), "verification write-up missing")
        blob = json.dumps(self.rec)
        for pmid in ["26603172", "28056227", "27855068", "38674671", "36569100", "36687643", "28018876"]:
            self.assertIn(pmid, blob, f"primary PMID {pmid} not in the record")
        self.assertIn("42750694", blob, "seed review PMID not in the record")

    def test_eight_rows_verified(self):
        rows = self.rec["rows_verified"]
        self.assertEqual(len(rows), 7, "expected seven single-row entries (17h/17i handled in ewers block)")
        labels = {r["review_row"] for r in rows}
        self.assertEqual(labels, {"1", "6", "13", "16", "17 (a)", "19", "28"})

    def test_the_three_named_matches_really_match(self):
        by = {r["review_row"]: r for r in self.rec["rows_verified"]}
        for label in ["1", "6", "13", "16", "28"]:
            r = by[label]
            self.assertEqual(r["review"]["n"], r["primary"]["n"], f"row {label} N")
            self.assertEqual(r["review"]["n_pos"], r["primary"]["n_pos"], f"row {label} n")
            self.assertEqual(r["verdict"], "match", f"row {label} verdict")

    def test_the_two_flagged_rows_are_mismatches(self):
        by = {r["review_row"]: r for r in self.rec["rows_verified"]}
        for label in ["17 (a)", "19"]:
            self.assertEqual(by[label]["verdict"], "mismatch", f"row {label} should be a mismatch")
        # 17(a): isolates match, numerator is +2, printed pct is the study total.
        a = by["17 (a)"]
        self.assertEqual(a["review"]["n"], a["primary"]["n"])
        self.assertEqual(a["primary"]["n_pos"], 707)
        self.assertEqual(a["review"]["n_pos"], 709)
        # 19: the numerator lost a leading digit; 49/1701 passed the review's own n/N check.
        f = by["19"]
        self.assertEqual(f["primary"]["n_pos"], 149)
        self.assertEqual(f["review"]["n_pos"], 49)
        self.assertEqual(f["review"]["n"], 1701)

    def test_ewers_country_block_reproduces_the_primary_defects(self):
        comp = {c["review_row"]: c for c in self.rec["ewers_review_comparison"]}
        # The three countries that should NOT match.
        mismatches = {k for k, c in comp.items() if not c["match"]}
        self.assertEqual(mismatches, {"Germany", "Belgium", "Spain"})
        self.assertEqual(comp["Germany"]["review_mcr_positive"], 709)
        self.assertEqual(comp["Germany"]["primary_mcr_positive"], 707)
        self.assertEqual(comp["Belgium"]["review_mcr_positive"], 20)
        self.assertEqual(comp["Belgium"]["primary_mcr_positive"], 11)
        self.assertEqual(comp["Spain"]["review_mcr_positive"], 17)
        self.assertEqual(comp["Spain"]["primary_mcr_positive"], 16)
        # Portugal is the genuine 28/17/60.7 row the Spain row was copied from.
        self.assertTrue(comp["Portugal"]["match"])
        self.assertEqual(comp["Portugal"]["primary_mcr_positive"], 17)

    def test_subtotal_reconciliation_closes(self):
        rec = self.rec["ewers_subtotal_reconciliation"]
        self.assertEqual(rec["review_17x_isolates"], REVIEW_17X_ISOLATES)
        self.assertEqual(rec["review_17x_mcr_positive"], REVIEW_17X_MCR1)
        self.assertEqual(rec["primary_table_isolates"], EWERS_TOTAL_ISOLATES)
        self.assertEqual(rec["primary_table_mcr_positive"], EWERS_TOTAL_MCR1)
        # isolate gap == dropped "Other countries" row exactly.
        self.assertEqual(EWERS_TOTAL_ISOLATES - REVIEW_17X_ISOLATES, EWERS_OTHER_ISOLATES)
        # positive gap == Germany(+2) + Belgium(+9) + Spain(+1)
        self.assertEqual(REVIEW_17X_MCR1 - EWERS_TOTAL_MCR1, 2 + 9 + 1)

    def test_primary_table_sums_to_its_own_total(self):
        table = self.rec["ewers_table_1_2010_2017"]
        iso = sum(c["isolates"] for c in table["countries"])
        pos = sum(c["mcr1_positive"] for c in table["countries"])
        self.assertEqual(iso, EWERS_TOTAL_ISOLATES)
        self.assertEqual(pos, EWERS_TOTAL_MCR1)

    def test_four_defects_are_recorded_with_both_sides(self):
        defects = self.rec["defects"]
        self.assertEqual(len(defects), 4)
        for d in defects:
            self.assertIn("review", d)
            self.assertIn("primary", d)
            self.assertIn("explanation", d)

    def test_harmonisation_columns_are_present_for_each_row(self):
        for r in self.rec["rows_verified"]:
            for key in ["collection_year", "mcr_variant", "detection_method", "sampling_design", "citation"]:
                self.assertIn(key, r, f"row {r['review_row']} missing {key}")
                self.assertTrue(str(r[key]).strip(), f"row {r['review_row']} has empty {key}")

    def test_markdown_names_each_defect_and_cites_the_test(self):
        for token in ["17(a)", "Belgium", "Spain", "149", "707"]:
            self.assertIn(token, self.md, f"write-up does not mention {token}")
        self.assertIn("tests/test_mcr_colistin_primary_verification.py", self.md)
        self.assertIn("7,614", self.md)
        self.assertIn("7,582", self.md)


if __name__ == "__main__":
    unittest.main(verbosity=2)
