#!/usr/bin/env python3
"""Pin §8 — the biomarker-only human-primary records (agenda item 32, §6 step 2) — offline.

Written 2026-10-04 (Desi, clock wake) with
`scripts/affective_pain_biomarker_only.py` and the §8 it adds to
`research/affective-pain-neuromodulation-evidence-map.md`.

Why this test exists. §7's claim — that the acupuncture pain literature that names a
brain/autonomic measurement keeps measuring the brain and not the mood — rested on the five
human-primary records that set *both* flags. §6 step (2) asked for the other 16, the
biomarker-only human-primary records, so the claim could hold across the arm rather than
across a hand-picked five. This test re-derives the selection and the category counts from
the stored census, refuses a hand verdict that does not cover exactly the records the census
holds, and checks the numbers printed in §8 against the machine.

It cannot re-run PubMed (tests run offline). It checks that the stored census, the script's
selection and widened-net, and the map's §8 still agree.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import affective_pain_biomarker_only as bo  # noqa: E402

MAP = ROOT / "research" / "affective-pain-neuromodulation-evidence-map.md"

# The 16 human-primary records of the filtered census that set the biomarker flag only,
# hand-classified in §8. If the census changes, this set and §8 must change with it.
BIOMARKER_ONLY = [
    "27741200", "29325883", "30137262", "31176295", "31521794", "31922698", "31964691",
    "32377180", "33314799", "35633164", "38897810", "39089662", "40634927", "41086064",
    "41830820", "42309066",
]
CATEGORY_COUNTS = {"M": 7, "C": 6, "R": 2, "X": 1}
# The one record whose patient-centred affective-side outcome rides on QoL vocabulary the
# item's affective term list cannot catch. This is §8's whole point: a screen defect, named.
SCREEN_MISS = "27741200"


class BiomarkerOnlyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads(bo.RAW.read_text())
        cls.md = MAP.read_text()
        cls.rows = bo.biomarker_only(cls.raw["records"])
        cls.pmids = [r["pmid"] for r in cls.rows]

    # --- the artefact exists and is internally consistent ------------------------------

    def test_files_exist(self):
        self.assertTrue(bo.RAW.exists(), "filtered census missing")
        self.assertTrue((ROOT / "scripts" / "affective_pain_biomarker_only.py").exists())
        self.assertIn("## 8.", self.md, "the map has no §8 for the biomarker-only records")

    def test_selection_is_exactly_the_sixteen_named(self):
        self.assertEqual(self.pmids, sorted(BIOMARKER_ONLY))
        self.assertEqual(len(self.pmids), 16)
        # and they are genuinely human-primary, biomarker set, affective clear
        for r in self.rows:
            self.assertTrue(r["is_human_primary"], r["pmid"])
            self.assertTrue(r["neural_or_autonomic_biomarker"], r["pmid"])
            self.assertFalse(r["affective_outcome"], r["pmid"])

    def test_every_selected_record_has_a_hand_verdict_and_none_extra(self):
        self.assertEqual(sorted(bo.VERDICTS), sorted(BIOMARKER_ONLY))
        for pmid, v in bo.VERDICTS.items():
            self.assertIn(v["cat"], CATEGORY_COUNTS, f"{pmid} has an unknown category")
            self.assertTrue(v["note"].strip(), f"{pmid} has an empty verdict note")

    def test_category_counts(self):
        by_cat = {}
        for r in self.rows:
            by_cat[bo.VERDICTS[r["pmid"]]["cat"]] = by_cat.get(bo.VERDICTS[r["pmid"]]["cat"], 0) + 1
        self.assertEqual(by_cat, CATEGORY_COUNTS)
        self.assertEqual(sum(by_cat.values()), 16)

    def test_arm_arithmetic_holds(self):
        """5 both + 16 biomarker-only = the 21 human-primary records §7 reports."""
        human_primary = [r for r in self.raw["records"] if r.get("is_human_primary")]
        both = [r for r in human_primary if r.get("both_affective_and_biomarker")]
        self.assertEqual(len(human_primary), 21)
        self.assertEqual(len(both), 5)
        self.assertEqual(len(both) + len(self.rows), len(human_primary))

    # --- the widened net is the reason this section exists -----------------------------

    def test_widened_net_re_tags_exactly_two_and_only_one_is_patient_outcome(self):
        tagged = {r["pmid"]: bo.widened_hits(r) for r in self.rows if bo.widened_hits(r)}
        self.assertEqual(sorted(tagged), ["27741200", "35633164"])
        self.assertIn("quality of life", tagged[SCREEN_MISS])
        self.assertIn("mental", tagged[SCREEN_MISS])
        # 35633164's 'mental' is a disorder class in a mapping paper, not a patient outcome
        self.assertIn("35633164", tagged)

    # --- the map says what the machine says --------------------------------------------

    def test_map_prints_the_section_and_every_number(self):
        for value in (16, 7, 6, 2, 1):
            self.assertIn(f"**{value}**", self.md, f"count {value} not printed in §8")
        self.assertIn("set biomarker only", self.md)
        for pmid in BIOMARKER_ONLY:
            self.assertIn(pmid, self.md, f"{pmid} absent from the map's §8 table")
        self.assertIn(SCREEN_MISS, self.md)

    def test_map_names_the_defect_not_a_counterexample(self):
        self.assertIn("screen defect, not a counterexample", self.md)
        self.assertIn("quality of life", self.md)
        self.assertIn("measures the brain and not the mood", self.md)

    def test_map_still_refuses_to_claim_efficacy(self):
        self.assertIn("makes no claim about whether either intervention works", self.md)


if __name__ == "__main__":
    unittest.main(verbosity=2)
