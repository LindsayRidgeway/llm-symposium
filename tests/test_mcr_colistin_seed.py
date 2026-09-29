#!/usr/bin/env python3
"""Pin the mcr-colistin seed evidence table to its source, mechanically.

Written 2026-09-29 (Desi, clock wake) with `research/mcr-colistin-seed.md` and
`research/mcr-colistin-seed.json`, the seed evidence table for agenda item 23 (MCR Colistin
Resistance Evidence Map).

The table is a transcription of the single included-studies table in the seed review —
Joy FU, Mouree TZ, Das M, Kabir A, *Public Health Challenges* 2026;5(3):e70376 (PMID 42750694,
DOI 10.1002/puh2.70376). The publisher page returns HTTP 403 to this session; Europe PMC's
`fullTextXML` endpoint served the complete article, and the JSON stores the raw table rows exactly
as extracted from that JATS XML.

This test does the cheap half of a stranger's check, offline:

  * every study row obeys n <= N, and the printed prevalence equals n/N — **except the one row the
    artefact names as anomalous**, which is pinned as a mismatch so the defect cannot be silently
    repaired or silently forgotten;
  * the totals the markdown states match the machine-readable record;
  * the two identical rows (Spain / Portugal) stay flagged;
  * the coverage claim — 5 of the item's 9 harmonisation columns are absent from the seed — stays
    true against the record.

It cannot re-fetch the review (tests run offline); it pins internal consistency and the numbers
that a reader would otherwise have to recompute by hand.
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "research" / "mcr-colistin-seed.json"
TABLE = ROOT / "research" / "mcr-colistin-seed.md"

IDENTIFIERS = ["42750694", "10.1002/puh2.70376", "PMC13577934", "Public Health Challenges"]
# The single row whose printed prevalence does not equal its own n/N. Pinned, not hidden.
ARITHMETIC_ANOMALY_ROW = "17 (a)"
# The two rows that are byte-identical (Spain and Portugal).
DUPLICATE_ROWS = ["17 (h)", "17 (i)"]
TOTAL_ISOLATES = 37816
TOTAL_POSITIVE = 2647


class McrColistinSeedTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rec = json.loads(RECORD.read_text())
        cls.md = TABLE.read_text()
        cls.rows = cls.rec["rows"]

    def test_both_files_exist(self):
        self.assertTrue(RECORD.exists(), "source record missing")
        self.assertTrue(TABLE.exists(), "seed table missing")

    def test_citation_matches_between_table_and_record(self):
        blob = json.dumps(self.rec)
        for ident in IDENTIFIERS:
            self.assertIn(ident, self.md, f"{ident} not cited in the table")
            self.assertIn(ident, blob, f"{ident} not in the source record")

    def test_row_count_and_shape(self):
        self.assertEqual(len(self.rows), 38, "seed table should hold 38 data rows")
        for r in self.rows:
            self.assertLessEqual(
                r["mcr_positive"], r["n_isolates"],
                f"row {r['sl']}: positive count exceeds isolate count",
            )
            self.assertGreater(r["n_isolates"], 0, f"row {r['sl']}: zero denominator")

    def test_prevalence_equals_numerator_over_denominator_except_the_named_row(self):
        for r in self.rows:
            calc = round(100 * r["mcr_positive"] / r["n_isolates"], 2)
            if r["sl"] == ARITHMETIC_ANOMALY_ROW:
                # This row is deliberately inconsistent in the source; it must NOT match.
                self.assertNotAlmostEqual(
                    r["prevalence_pct_reported"], calc, delta=0.5,
                    msg="the anomaly row now agrees with its own arithmetic; update the artefact",
                )
                continue
            self.assertAlmostEqual(
                r["prevalence_pct_reported"], calc, delta=0.06,
                msg=f"row {r['sl']} printed prevalence disagrees with n/N",
            )

    def test_totals_are_pinned(self):
        self.assertEqual(sum(r["n_isolates"] for r in self.rows), TOTAL_ISOLATES)
        self.assertEqual(sum(r["mcr_positive"] for r in self.rows), TOTAL_POSITIVE)
        self.assertEqual(self.rec["derived"]["sum_isolates"], TOTAL_ISOLATES)
        self.assertEqual(self.rec["derived"]["sum_mcr_positive"], TOTAL_POSITIVE)
        # The review's headline claim is "more than 36,000 isolates" — verify it holds.
        self.assertGreater(TOTAL_ISOLATES, 36000)

    def test_study_count_note_reconciles_rows_and_studies(self):
        self.assertEqual(self.rec["review_headline_claims"]["included_studies"], 28)
        subs = [r for r in self.rows if r["is_multi_country_subrow"]]
        self.assertEqual(len(subs), 11, "the Ewers multi-country study should be 11 sub-rows")
        # 11 sub-rows + row 16 (separate German study) + the 16 other rows = 28 studies.
        self.assertEqual(38 - 11 + 1, 28)

    def test_duplicate_rows_stay_flagged(self):
        got = [a for a in self.rec["anomalies"] if a["kind"] == "duplicate_numeric_row"]
        self.assertEqual(len(got), 1, "the Spain/Portugal duplicate should be recorded once")
        self.assertEqual(sorted(got[0]["rows"]), sorted(DUPLICATE_ROWS))

    def test_arithmetic_anomaly_is_recorded_with_numbers(self):
        got = [a for a in self.rec["anomalies"] if a["kind"] == "arithmetic"]
        self.assertEqual(len(got), 1)
        a = got[0]
        self.assertEqual(a["row"], ARITHMETIC_ANOMALY_ROW)
        self.assertEqual(a["mcr_positive"], 709)
        self.assertEqual(a["n_isolates"], 6158)
        self.assertEqual(a["reported_pct"], 10.42)
        self.assertEqual(a["recomputed_pct"], 11.51)

    def test_coverage_gap_is_as_claimed(self):
        cv = self.rec["coverage_vs_agenda_item"]
        self.assertEqual(len(cv["columns_the_item_asks_for"]), 9)
        self.assertEqual(len(cv["present_in_seed"]), 4)
        self.assertEqual(len(cv["absent_from_seed"]), 5)
        joined = " ".join(cv["absent_from_seed"]).lower()
        for term in ["collection year", "mcr variant", "detection method", "sampling design"]:
            self.assertIn(term, joined, f"coverage claim should name the missing {term!r}")

    def test_markdown_table_has_every_row(self):
        # Each data row is a markdown table line beginning with "| <sl> ".
        table_lines = [
            ln for ln in self.md.splitlines()
            if re.match(r"^\|\s*\d", ln) or re.match(r"^\|\s*17\s*\([a-k]\)", ln)
        ]
        self.assertEqual(len(table_lines), 38, "markdown table should carry all 38 rows")

    def test_markdown_names_both_anomalies(self):
        self.assertIn("11.51", self.md, "recomputed value for the anomaly row missing")
        self.assertIn("10.42", self.md, "printed value for the anomaly row missing")
        self.assertIn("Spain", self.md)
        self.assertIn("Portugal", self.md)


if __name__ == "__main__":
    unittest.main(verbosity=2)
