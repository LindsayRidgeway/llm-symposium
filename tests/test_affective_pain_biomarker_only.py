#!/usr/bin/env python3
"""Pin §8 of the affective-pain evidence map (agenda item 32, §6 step 2b) to its source, mechanically.

Written 2026-10-06 (Dmitri, clock wake) with
`research/affective-pain-neuromodulation-acupuncture-filtered-raw.json`,
`scripts/affective_pain_biomarker_only_classify.py` and the §8 it adds to
`research/affective-pain-neuromodulation-evidence-map.md`.

Why this test exists. §7 of the map ranked the filtered acupuncture census by flag and found 5 of 21
human-primary records set both flags. §8 classifies the complement: the records that set the
biomarker flag and not the affective flag. That number (16) and that list are what the section's whole
argument rests on, so a reader is entitled to check them against the machine rather than take them on
trust. As with §7's test, this refuses the failure this repository has already paid for: an artefact
that says a number its script no longer produces.

It cannot re-run the PubMed query (tests run offline). It re-derives the flags from title+abstract with
the item's own classifier and checks that the stored census, the script's own summary, and the numbers
the map prints still agree.
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import affective_pain_search as aps  # noqa: E402
import affective_pain_biomarker_only_classify as boc  # noqa: E402

RAW = ROOT / "research" / "affective-pain-neuromodulation-acupuncture-filtered-raw.json"
MAP = ROOT / "research" / "affective-pain-neuromodulation-evidence-map.md"
SCRIPT = ROOT / "scripts" / "affective_pain_biomarker_only_classify.py"

# The 16 human-primary, biomarker-only records of the filtered acupuncture census, as §8 lists them.
BIOMARKER_ONLY = [
    "27741200", "29325883", "30137262", "31176295", "31521794", "31922698",
    "31964691", "32377180", "33314799", "35633164", "38897810", "39089662",
    "40634927", "41086064", "41830820", "42309066",
]
# The 5 whose both-flags reading §7 owns; §8 must not swallow them.
HUMAN_PRIMARY_BOTH = ["24728839", "26025590", "26594625", "26787729", "37609769"]


class BiomarkerOnlyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads(RAW.read_text())
        cls.md = MAP.read_text()
        cls.records = cls.raw["records"]

    def test_files_exist(self):
        self.assertTrue(RAW.exists(), "filtered raw record missing")
        self.assertTrue(SCRIPT.exists(), "biomarker-only script missing")
        self.assertIn("## 8.", self.md, "the map has no §8 for the biomarker-only records")

    def test_recomputed_flags_match_the_stored_census(self):
        """An offline re-tag must reproduce the stored flags, or §7/§8 rest on stale booleans."""
        drift = []
        for r in self.records:
            fresh = aps.classify(r)
            fresh.update(aps.classify_subject(r))
            for key in ("affective_outcome", "neural_or_autonomic_biomarker",
                        "both_affective_and_biomarker", "is_human_primary"):
                if bool(fresh[key]) != (str(r[key]) == "True"):
                    drift.append((r["pmid"], key, r[key], fresh[key]))
        self.assertEqual(drift, [], f"stored flags no longer reproduce from title+abstract: {drift}")

    def test_biomarker_only_selection(self):
        rows, n_human, n_both = boc.select(self.raw)
        self.assertEqual(n_human, 21, "human-primary count drifted")
        self.assertEqual(n_both, 5, "human-primary both-flags count drifted")
        self.assertEqual(len(rows), 16, "biomarker-only count drifted")
        self.assertEqual(sorted(r["pmid"] for r, _ in rows), sorted(BIOMARKER_ONLY))
        # none of the 16 may set the affective flag, or it is not biomarker-*only*
        for r, f in rows:
            self.assertFalse(f["affective_outcome"], f"{r['pmid']} sets the affective flag")
            self.assertTrue(f["neural_or_autonomic_biomarker"], f"{r['pmid']} sets no biomarker flag")

    def test_script_json_summary_agrees(self):
        out = subprocess.run([sys.executable, str(SCRIPT), "--json"],
                             capture_output=True, text=True, check=True)
        data = json.loads(out.stdout)
        self.assertEqual(data["n_human_primary"], 21)
        self.assertEqual(data["n_human_primary_both"], 5)
        self.assertEqual(data["n_biomarker_only"], 16)
        self.assertEqual(sorted(data["pmids"]), sorted(BIOMARKER_ONLY))

    def test_map_names_every_biomarker_only_record(self):
        for pmid in BIOMARKER_ONLY:
            self.assertIn(pmid, self.md, f"§8 does not name biomarker-only record {pmid}")

    def test_map_states_the_biomarker_only_count(self):
        self.assertIn("**16** human-primary records that set the biomarker flag and **not**", self.md,
                      "§8 no longer states the 16 it classifies")


if __name__ == "__main__":
    unittest.main(verbosity=2)
