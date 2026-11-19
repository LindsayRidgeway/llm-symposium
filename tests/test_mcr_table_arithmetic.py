#!/usr/bin/env python3
"""Pin the Table 1 arithmetic audit to its numbers, offline.

Written 2026-11-19 (Desi, clock wake) with `research/mcr-colistin-table-arithmetic-audit.md` and
`scripts/mcr_table_arithmetic_audit.py`. These assertions are the ones a reader would use to check
the claim in the prose, so they are the ones worth breaking loudly:

  * exactly one row of the 38 fails its own printed counts;
  * the rounding convention is read off the rows that discriminate, and every one of them says
    rounding — so a change of convention upstream must fail here rather than silently re-judge the
    table;
  * the one failing cell's printed value matches the Ewers study-wide rate and neither pooled rate
    this table can compute — the attribution is evidence, not a guess;
  * no other row carries that study-wide rate;
  * the pooled figures quoted in §4 are the ones the counts produce.
"""

import json
import math
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTEFACT = ROOT / "research" / "mcr-colistin-table-arithmetic-audit.md"
RECORD = ROOT / "research" / "mcr-colistin-table-arithmetic.json"
SCRIPT = ROOT / "scripts" / "mcr_table_arithmetic_audit.py"
SEED = ROOT / "research" / "mcr-colistin-seed.json"


class AuditRecord(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(RECORD.read_text())
        cls.rows = cls.record["rows"]

    def test_row_count_is_the_review_table(self):
        self.assertEqual(len(self.rows), 38)
        self.assertEqual(self.record["row_count"], 38)

    def test_exactly_one_row_fails_its_own_counts(self):
        failing = [r for r in self.rows if not r["consistent_with_rounding"]]
        self.assertEqual([f["row"] for f in failing], ["17 (a)"])
        self.assertEqual(self.record["rows_failing_own_counts"], 1)
        self.assertEqual(self.record["failing_rows"], ["17 (a) Germany"])

    def test_the_failing_cell_is_the_known_one(self):
        row = next(r for r in self.rows if r["row"] == "17 (a)")
        self.assertEqual((row["N"], row["n"], row["printed_pct"]), (6158, 709, 10.42))
        self.assertAlmostEqual(row["exact_pct"], 100 * 709 / 6158, places=5)
        # 11.51 is what the two-decimal convention requires; the printed 10.42 is 1.09 pp low.
        self.assertAlmostEqual(row["error_pp"], 10.42 - 100 * 709 / 6158, places=5)
        self.assertGreater(abs(row["error_pp"]), 1.0)

    def test_convention_is_read_off_discriminating_rows_not_assumed(self):
        conv = self.record["convention"]
        self.assertEqual(conv["convention_inferred"], "rounding")
        self.assertGreaterEqual(len(conv["rows_that_discriminate"]), 10)
        for r in conv["rows_that_discriminate"]:
            self.assertEqual(r["reads_as"], "rounding", r)
        # Row 6 is the sharpest witness: 2.3176 prints 2.32, so the table rounds up.
        self.assertIn("6", [r["row"] for r in conv["rows_that_discriminate"]])

    def test_consistency_uses_the_printed_precision(self):
        """A one-decimal cell must not be judged against a two-decimal tolerance."""
        for r in self.rows:
            if r["consistent_with_rounding"]:
                tol = 0.5 * 10 ** -r["decimals_printed"] + 1e-9
                self.assertLessEqual(abs(r["error_pp"]), tol + 1e-6, r)

    def test_attribution_matches_ewers_and_not_either_pool(self):
        finding = self.record["attribution"]["rows_failing_own_counts"]
        self.assertEqual(len(finding), 1)
        candidates = {c["candidate"]: c for c in finding[0]["candidate_sources"]}
        self.assertTrue(candidates["Ewers et al. study-wide mcr-1 rate"]["matches_printed"])
        self.assertFalse(candidates["own sector pool (this table's counts)"]["matches_printed"])
        self.assertFalse(candidates["whole-table pool (this table's counts)"]["matches_printed"])

    def test_no_other_row_prints_the_study_wide_rate(self):
        carriers = self.record["attribution"]["rows_printing_the_study_wide_rate"]
        self.assertEqual([c["row"] for c in carriers], ["17 (a)"])

    def test_pooled_figures_are_the_counts(self):
        pools = self.record["pools"]
        self.assertEqual((pools["sum_N"], pools["sum_n"]), (37816, 2647))
        self.assertAlmostEqual(pools["pooled_pct_from_counts"], 100 * 2647 / 37816, places=3)
        livestock = next(s for s in self.record["printed_percentages_vs_counts"] if s["sector"] == "Livestock")
        self.assertEqual(livestock["sum_N"], 27132)
        self.assertAlmostEqual(livestock["pooled_from_counts_pct"], 100 * 2226 / 27132, places=3)
        # The gap between the two ways of reading the same table is the single cell, to 3 dp.
        self.assertLess(abs(livestock["gap_pp"] - livestock["gap_attributed_to_failing_rows_pp"]), 0.005)
        self.assertAlmostEqual(livestock["gap_pp"], -0.248, places=3)

    def test_france_row_passes_self_check_and_is_not_claimed_as_reconciled(self):
        """Row 19 is internally perfect (49/1,701 = 2.88) and wrong against its primary — the audit
        must pass it, and the artefact must say so rather than imply a clean table."""
        france = next(r for r in self.rows if r["row"] == "19")
        self.assertTrue(france["consistent_with_rounding"])
        text = ARTEFACT.read_text()
        self.assertIn("mcr-colistin-france-trace.json", text)
        self.assertIn("149", text)

    def test_artefact_names_the_one_cell_and_the_rule(self):
        text = ARTEFACT.read_text()
        self.assertIn("11.51", text)
        self.assertIn("10.42", text)
        self.assertIn("2,647", text)
        self.assertIn("mcr-colistin-table-arithmetic.json", text)


class ScriptRuns(unittest.TestCase):
    def test_show_runs_and_reports_the_failure(self):
        out = subprocess.run(
            [sys.executable, str(SCRIPT), "--show"], capture_output=True, text=True, timeout=60
        )
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("rows audited: 38", out.stdout)
        self.assertIn("failing own counts: 1", out.stdout)
        self.assertIn("17 (a)", out.stdout)


if __name__ == "__main__":
    unittest.main()
