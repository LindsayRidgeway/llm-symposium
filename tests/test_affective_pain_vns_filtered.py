#!/usr/bin/env python3
"""Pin the filtered vagus-nerve arm (agenda item 32, §7 step 3) to its source, mechanically.

Written 2026-10-08 (Desi, clock wake) with
`research/affective-pain-neuromodulation-vns-filtered-raw.json`,
`scripts/affective_pain_vns_filtered.py` and the §9 it adds to
`research/affective-pain-neuromodulation-evidence-map.md`.

Why this test exists. §8 found the filtered *acupuncture* arm measures the brain and the pain but
not the mood, and named the open question: is that a property of acupuncture or of pain
neuromodulation generally? §9 answers it by running the *identical* filter against the item's other
intervention (VNS). A comparison like that is exactly the kind of claim a reader should be able to
check against the machine rather than take on trust — especially the cross-arm counts, which are
the whole point. This test re-runs the item's own classifier over both stored censuses and refuses
the failure this repository has already paid for: an artefact that says a number the script no
longer produces, or a comparison whose two sides have drifted apart.

It cannot re-run the PubMed query (tests run offline). It checks that the stored census, the stored
flags, the JSON's own aggregates and the numbers printed in §9 still agree.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import affective_pain_search as aps  # noqa: E402
import affective_pain_vns_filtered as vf  # noqa: E402

RAW = ROOT / "research" / "affective-pain-neuromodulation-vns-filtered-raw.json"
RAW_ACU = ROOT / "research" / "affective-pain-neuromodulation-acupuncture-filtered-raw.json"
MAP = ROOT / "research" / "affective-pain-neuromodulation-evidence-map.md"
SCRIPT = ROOT / "scripts" / "affective_pain_vns_filtered.py"

# The §7 measurement families, which §9 keeps byte-for-byte so the only changed clause is the
# intervention. If the VNS filter loses one, the arms stop being comparable.
FILTER_FAMILIES = ["fmri", "functional magnetic resonance", "eeg", "electroencephalogra*",
                   "heart rate variability", "hrv", "autonomic", "skin conductance",
                   "vagal tone", "brainstem", "insula", "amygdala", "anterior cingulate",
                   "locus coeruleus"]

# The eight human-primary records of the VNS filtered census that set both the affective and the
# biomarker flag. Hand-read in §9: three are in a patient pain population (all fibromyalgia), five
# are not. All eight must be named in the map.
HUMAN_PRIMARY_BOTH = ["26450637", "34509623", "34634682", "38963558",
                      "40576705", "40935122", "41044114", "41332177"]
PAIN_POPULATION_BOTH = ["40576705", "40935122", "41332177"]  # all fibromyalgia, hand-read

# The complement §9 hand-classifies: the human-primary filtered-arm records that set the biomarker
# flag but not the affective one. Derivable from the stored flags.
BIOMARKER_ONLY = ["26728182", "33262253", "33548494", "33635894", "38469939",
                  "40461351", "41091086", "41454683", "42334392", "42361949"]


class VnsFilteredArmTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads(RAW.read_text())
        cls.raw_acu = json.loads(RAW_ACU.read_text())
        cls.md = MAP.read_text()
        cls.records = cls.raw["records"]
        cls.arm = cls.raw["arms"][vf.ARM]
        cls.by_id = {r["pmid"]: r for r in cls.records}

    # --- the artefact is internally reproducible ---------------------------------------

    def test_files_exist(self):
        self.assertTrue(RAW.exists(), "filtered raw record missing")
        self.assertTrue(SCRIPT.exists(), "filtered-arm script missing")
        self.assertIn("## 9.", self.md, "the map has no §9 for the VNS filtered arm")

    def test_stored_flags_match_the_script_classifier(self):
        drift = []
        for r in self.records:
            fresh = dict(aps.classify(r), **aps.classify_subject(r))
            for key, val in fresh.items():
                if key in ("affective", "biomarker", "intensity"):
                    val, have = bool(val), bool(r.get(key))
                else:
                    have = r.get(key)
                if have != val:
                    drift.append((r["pmid"], key, have, val))
        self.assertEqual(drift, [], f"stored flags drifted from the classifier: {drift[:5]}")

    def test_stored_tallies_match_a_recomputation(self):
        self.assertEqual(aps.tally(self.records), self.raw["tallies"])

    def test_the_arm_is_a_census_not_a_slice(self):
        """The whole point of the filtered design: no relevance ranking, so no count by construction."""
        self.assertEqual(self.arm["total_matching"], 31)
        self.assertEqual(self.arm["fetched"], 31)
        self.assertFalse(self.arm["censored"], "the filtered arm is no longer a complete census")
        self.assertIn("census", self.md)

    def test_the_query_is_the_filter_§7_named_plus_the_vns_block(self):
        for fam in FILTER_FAMILIES:
            self.assertIn(fam, self.arm["filter"], f"filter family {fam!r} missing from the query")
            self.assertIn(fam, self.md, f"filter family {fam!r} not printed in the map")
        self.assertIn("auricular vagus", self.arm["query"])
        self.assertIn("humans[MeSH Terms]", self.arm["query"])

    # --- the map says what the machine says --------------------------------------------

    def test_composition_numbers_are_in_the_map(self):
        t = self.raw["tallies"]
        self.assertEqual(t["n_records"], 31)
        self.assertEqual(t["n_human_primary"], 20)
        self.assertEqual(t["n_review"], 7)
        self.assertEqual(t["n_protocol"], 3)
        self.assertEqual(t["n_animal_subject"], 1)
        self.assertEqual(t["n_both_affective_and_biomarker"], 14)
        for value in (31, 20, 7, 14):
            self.assertIn(f"**{value}**", self.md, f"{value} not printed in the map")

    def test_human_primary_both_set_is_exactly_the_eight_named_rows(self):
        hp_both = sorted(r["pmid"] for r in self.records
                         if r["is_human_primary"] and r["both_affective_and_biomarker"])
        self.assertEqual(hp_both, HUMAN_PRIMARY_BOTH)
        self.assertEqual(len(hp_both), 8)
        for pmid in hp_both:
            self.assertIn(pmid, self.md, f"{pmid} is in the both-set but absent from the map")
        self.assertIn("8 of 20", self.md)
        for pmid in PAIN_POPULATION_BOTH:
            self.assertEqual(self.by_id[pmid]["arm"], vf.ARM)

    def test_biomarker_only_set_is_exactly_the_ten_named_rows(self):
        """§9: the complement of the both-set, re-derived from the stored flags, not re-listed."""
        hp_biomarker_only = sorted(r["pmid"] for r in self.records
                                   if r["is_human_primary"]
                                   and r["neural_or_autonomic_biomarker"]
                                   and not r["affective_outcome"])
        self.assertEqual(hp_biomarker_only, BIOMARKER_ONLY)
        self.assertEqual(len(hp_biomarker_only), 10)
        for pmid in hp_biomarker_only:
            self.assertIn(pmid, self.md, f"{pmid} is biomarker-only but absent from the map")
        self.assertIn("10 of 20", self.md)

    def test_the_cross_arm_comparison_is_recomputable_from_both_censuses(self):
        """The one number that carries §9: the two arms' rates, recomputed from both raw files."""
        def hp(rec):
            return [r for r in rec["records"] if r["is_human_primary"]]

        def both(rec):
            return [r for r in hp(rec) if r["both_affective_and_biomarker"]]

        vns_hp, acu_hp = hp(self.raw), hp(self.raw_acu)
        vns_both, acu_both = both(self.raw), both(self.raw_acu)
        self.assertEqual((len(vns_hp), len(vns_both)), (20, 8))
        self.assertEqual((len(acu_hp), len(acu_both)), (21, 5))
        # the rates §9 prints must be the rates the two censuses actually produce
        self.assertIn("8 of 20", self.md)
        self.assertIn("5 of 21", self.md)
        self.assertIn("16 of 21", self.md)   # acupuncture biomarker-only share, §8's set
        self.assertIn("10 of 20", self.md)   # VNS biomarker-only share
        # the finding the comparison supports, and the hedge that must travel with it
        self.assertIn("cleanly generalise", self.md)
        self.assertIn("fibromyalgia", self.md)

    def test_the_map_still_refuses_to_claim_efficacy(self):
        self.assertIn("makes no claim about whether either intervention works", self.md)


if __name__ == "__main__":
    unittest.main(verbosity=2)
