#!/usr/bin/env python3
"""Pin the MCR primary-study pull behind agenda item 23 to its own numbers, offline.

Written 2026-10-07 (Desi, clock wake) with `scripts/mcr_colistin_primary_pull.py`,
`research/mcr-colistin-primary-raw.json`, `research/mcr-colistin-primary-studies.md` and
`research/mcr-colistin-primary-reconciliation.json`.

The pull reconciles the six largest-N rows of the MCR seed table against the primary studies they
cite. Four of the six match their source to the isolate; two do not, and the primary full text fixes
both — row 17a (Ewers 2022) is 707/6,158 = 11.5%, not the seed's 709/10.42%, and the seed's Spain
row is Portugal's row duplicated (the primary's Spain is 28/16 = 57.1%); and a third, unflagged
discrepancy is found (row 19, 149/1,701 not 49/1,701).

This test does the cheap half of a stranger's check, with no network:

  * the six records the script claims to fetch are the six the raw file holds, and each has a real
    abstract;
  * every reconciliation row's stated percentage equals its own n/N — so a corrected cell cannot
    drift from its arithmetic;
  * the four rows the artefact calls matches really are seed-equals-primary, and the two it calls
    mismatches really are not — so a mismatch cannot be quietly repaired and a match cannot be
    quietly broken;
  * exactly one of the six rows is phenotype-first (the human row) and the rest are not, which is
    the confounder the write-up rests on;
  * the corrected figures the prose asserts are present in the prose.

It cannot re-fetch the primaries (tests run offline); it pins internal consistency and the claims a
reader would otherwise have to recompute by hand.
"""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "research" / "mcr-colistin-primary-raw.json"
RECON = ROOT / "research" / "mcr-colistin-primary-reconciliation.json"
SCRIPT = ROOT / "scripts" / "mcr_colistin_primary_pull.py"
WRITEUP = ROOT / "research" / "mcr-colistin-primary-studies.md"

EXPECT_PMIDS = {"27855068", "36569100", "28018876", "26603172", "28056227", "36687643"}
# Rows the artefact calls a clean match to the primary; the complement (19, 17a) are the mismatches.
MATCH_ROWS = {"1", "6", "13", "28"}
MISMATCH_ROWS = {"19", "17a"}


def load(path):
    return json.loads(path.read_text())


class McrPrimaryPull(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = load(RAW)
        cls.recon = load(RECON)
        cls.targets = {r["pmid"]: r for r in cls.raw["targets"]}
        cls.rows = {r["seed_rows"][0]: r for r in cls.recon["rows"]}

    def test_raw_holds_exactly_the_six_targets(self):
        self.assertEqual(set(self.targets), EXPECT_PMIDS)
        for pmid, t in self.targets.items():
            self.assertTrue(t["found"], f"{pmid} not found in pull")
            self.assertTrue(t["title"], f"{pmid} has no title")
            self.assertGreaterEqual(len(t["abstract_plain"] or ""), 80,
                                    f"{pmid} abstract too short to be real")

    def test_script_names_the_same_six_pmids(self):
        text = SCRIPT.read_text()
        for pmid in EXPECT_PMIDS:
            self.assertIn(pmid, text)

    def test_reconciliation_rows_cover_the_same_six(self):
        self.assertEqual(set(self.rows), {r[0] for r in
                         (x["seed_rows"] for x in self.recon["rows"])})
        self.assertEqual({r["pmid"] for r in self.recon["rows"]}, EXPECT_PMIDS)

    def test_every_stated_percentage_equals_its_own_arithmetic(self):
        for key, row in self.rows.items():
            p = row["primary"]
            self.assertGreater(p["n"], 0, key)
            self.assertLessEqual(p["mcr_positive"], p["n"], key)
            pct = 100.0 * p["mcr_positive"] / p["n"]
            self.assertAlmostEqual(pct, p["pct"], delta=0.1,
                                   msg=f"row {key}: stored pct {p['pct']} != {pct:.3f}")

    def test_matches_really_match_and_mismatches_really_do_not(self):
        for key, row in self.rows.items():
            s, p = row["seed"], row["primary"]
            if key in MATCH_ROWS:
                self.assertEqual(s["n"], p["n"], key)
                self.assertEqual(s["mcr_positive"], p["mcr_positive"], key)
                self.assertIn("match", row["verdict"].lower(), key)
            else:
                self.assertIn(key, MISMATCH_ROWS)
                differs = (s["n"] != p["n"]) or (s["mcr_positive"] != p["mcr_positive"])
                self.assertTrue(differs, f"row {key} called a mismatch but matches")
                self.assertNotIn("matches exactly", row["verdict"].lower(), key)

    def test_the_two_corrected_cells_are_the_ones_the_prose_asserts(self):
        # row 17a -> 707/6158 = 11.5%; row 19 -> 149/1701 = 8.76%
        self.assertEqual(self.rows["17a"]["primary"]["mcr_positive"], 707)
        self.assertEqual(self.rows["17a"]["primary"]["n"], 6158)
        self.assertEqual(self.rows["19"]["primary"]["mcr_positive"], 149)
        self.assertEqual(self.rows["19"]["primary"]["n"], 1701)

    def test_exactly_one_row_is_phenotype_first(self):
        first = [r["seed_rows"][0] for r in self.recon["harmonisation_columns"]
                 if "phenotype-first" in r["detection_method"]]
        self.assertEqual(first, ["28"],
                         "the phenotype-first confounder must sit on the one human row")

    def test_both_anomalies_are_resolved_with_a_fix(self):
        self.assertEqual(len(self.recon["anomalies_resolved"]), 2)
        text = json.dumps(self.recon["anomalies_resolved"])
        self.assertIn("707", text)
        self.assertIn("11.5", text)
        self.assertIn("28/16", text)

    def test_harmonisation_columns_are_filled_for_all_six(self):
        cols = {r["seed_rows"][0]: r for r in self.recon["harmonisation_columns"]}
        self.assertEqual(set(cols), set(self.rows))
        for key, c in cols.items():
            for field in ("collection_year", "mcr_variant", "detection_method", "sampling_design"):
                self.assertTrue(c.get(field), f"row {key} missing {field}")

    def test_writeup_carries_the_corrected_figures(self):
        md = WRITEUP.read_text()
        for phrase in ("707 / 6,158 = 11.5%", "149 / 1,701 = 8.76%", "Spain = 28 / 16 = 57.1%"):
            self.assertIn(phrase, md, f"write-up missing: {phrase}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
