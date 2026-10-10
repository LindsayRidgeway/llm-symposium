#!/usr/bin/env python3
"""Pin the filtered VNS arm (agenda item 32, step 3) to its source, mechanically.

Written 2026-10-10 (Desi, clock wake) with
`research/affective-pain-neuromodulation-vns-filtered-raw.json`,
`scripts/affective_pain_vns_filtered.py` and the §9 it adds to
`research/affective-pain-neuromodulation-evidence-map.md`.

Why this test exists. §7 step (3) asked for the same *filtered* design against the item's
second modality, to test whether the affect-blindness §8 found is a property of acupuncture
research or of pain neuromodulation as such. The run reached a specific, checkable claim:
the filtered VNS census returns the *same eight* human-primary both-flag records as §4's
relevance slice, so — unlike acupuncture, whose slice produced a false zero — the VNS slice
was not hiding anything, and the mood column on the VNS side is not empty. A reader is
entitled to check that against the machine rather than take it on trust. This test re-runs
the item's own classifier over the stored records and refuses the failure this repository
has already paid for: an artefact that says a number the script no longer produces.

It cannot re-run the PubMed query (tests run offline). It checks that the stored census, the
stored flags, the JSON's own aggregates and the numbers printed in the map still agree.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import affective_pain_search as aps  # noqa: E402
import affective_pain_vns_filtered as avf  # noqa: E402

RAW = ROOT / "research" / "affective-pain-neuromodulation-vns-filtered-raw.json"
MAP = ROOT / "research" / "affective-pain-neuromodulation-evidence-map.md"
SCRIPT = ROOT / "scripts" / "affective_pain_vns_filtered.py"

# The measurement families §7/§9 named, plus their synonyms. If the filter loses one, the arm
# silently stops being the query the map prints.
FILTER_FAMILIES = ["fmri", "functional magnetic resonance", "eeg", "electroencephalogra*",
                   "heart rate variability", "hrv", "autonomic", "skin conductance",
                   "vagal tone", "brainstem", "insula", "amygdala", "anterior cingulate",
                   "locus coeruleus"]

# The eight human-primary records of the filtered VNS census that set both the affective and the
# biomarker flag. The map hand-reads all eight; §9's headline is that this set is *identical* to
# §4's VNS both-set, so all eight must be named there.
HUMAN_PRIMARY_BOTH = ["26450637", "34509623", "34634682", "38963558",
                      "40576705", "40935122", "41044114", "41332177"]
# The two of the eight that measure a real affective outcome against an autonomic measure in a
# chronic-pain population — the convergence test §9 says lives on the VNS side.
CONVERGENCE_TRIALS = ["40935122", "41332177"]

# The complement: human-primary filtered-arm records that set the biomarker flag but not the
# affective one. Derivable from the stored flags — if this list and the machine's disagree, §9
# is describing a corpus the script no longer produces.
BIOMARKER_ONLY = ["26728182", "33262253", "33548494", "33635894", "38469939",
                  "40461351", "41091086", "41454683", "42334392", "42361949"]


class VnsFilteredArmTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads(RAW.read_text())
        cls.md = MAP.read_text()
        cls.records = cls.raw["records"]
        cls.arm = cls.raw["arms"][avf.ARM]
        cls.by_id = {r["pmid"]: r for r in cls.records}

    # --- the artefact is internally reproducible ---------------------------------------

    def test_files_exist(self):
        self.assertTrue(RAW.exists(), "filtered VNS raw record missing")
        self.assertTrue(SCRIPT.exists(), "filtered VNS-arm script missing")
        self.assertIn("## 9.", self.md, "the map has no §9 for the filtered VNS arm")

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
        """The whole point of step 3: no relevance ranking, so no count-by-construction."""
        self.assertEqual(self.arm["total_matching"], 31)
        self.assertEqual(self.arm["fetched"], 31)
        self.assertFalse(self.arm["censored"], "the filtered VNS arm is no longer a complete census")
        self.assertIn("census", self.md)

    def test_the_query_is_the_filter_this_section_names(self):
        for fam in FILTER_FAMILIES:
            self.assertIn(fam, self.arm["filter"], f"filter family {fam!r} missing from the query")
            self.assertIn(fam, self.md, f"filter family {fam!r} not printed in the map")
        # it is the VNS arm, not the acupuncture one
        self.assertIn('vagus nerve stimulation"[tiab]', self.arm["query"])
        self.assertNotIn("acupuncture[tiab]", self.arm["query"])
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
        for value in (31, 20, 7, 3, 1, 14):
            self.assertIn(f"**{value}**", self.md, f"{value} not printed in the map")

    def test_human_primary_both_set_is_exactly_the_eight_named_rows(self):
        hp_both = sorted(r["pmid"] for r in self.records
                         if r["is_human_primary"] and r["both_affective_and_biomarker"])
        self.assertEqual(hp_both, HUMAN_PRIMARY_BOTH)
        self.assertEqual(len(hp_both), 8)
        for pmid in hp_both:
            self.assertIn(pmid, self.md, f"{pmid} is in the both-set but absent from the map")

    def test_biomarker_only_set_is_exactly_the_ten_named_rows(self):
        hp_biomarker_only = sorted(r["pmid"] for r in self.records
                                   if r["is_human_primary"]
                                   and r["neural_or_autonomic_biomarker"]
                                   and not r["affective_outcome"])
        self.assertEqual(hp_biomarker_only, BIOMARKER_ONLY)
        self.assertEqual(len(hp_biomarker_only), 10)
        for pmid in hp_biomarker_only:
            self.assertIn(pmid, self.md, f"{pmid} is biomarker-only but absent from the map")

    def test_the_convergence_trials_are_named_and_in_the_arm(self):
        for pmid in CONVERGENCE_TRIALS:
            self.assertIn(pmid, self.md, f"convergence trial {pmid} absent from the map")
            self.assertEqual(self.by_id[pmid]["arm"], avf.ARM)
            self.assertEqual(self.by_id[pmid]["is_human_primary"], True)

    def test_the_arm_is_disjoint_from_the_acupuncture_arms(self):
        """§9's separating claim: the filter still tells the two modalities apart."""
        acu_filtered = json.loads(
            (ROOT / "research" / "affective-pain-neuromodulation-acupuncture-filtered-raw.json")
            .read_text())["arms"]["acupuncture_filtered"]["pmids"]
        overlap = set(self.arm["pmids"]) & set(acu_filtered)
        self.assertEqual(overlap, set())
        self.assertIn("0 of the 31", self.md)

    def test_the_headline_claims_are_printed(self):
        """§9's load-bearing sentences: the census reproduces the slice's eight, and the
        affect-blindness does not generalise to VNS."""
        self.assertIn("the identical eight", self.md)
        self.assertIn("does not generalise", self.md)
        self.assertIn("acupuncture pain research in this corpus is affect-blind", self.md)
        self.assertIn("VNS pain research is not", self.md)

    def test_the_map_still_refuses_to_claim_efficacy(self):
        self.assertIn("adds no efficacy claim", self.md)
        self.assertIn("makes no claim about whether either intervention works", self.md)


if __name__ == "__main__":
    unittest.main(verbosity=2)
