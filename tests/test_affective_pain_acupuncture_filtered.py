#!/usr/bin/env python3
"""Pin the filtered acupuncture arm (agenda item 32, step 2) to its source, mechanically.

Written 2026-10-04 (Desi, clock wake) with
`research/affective-pain-neuromodulation-acupuncture-filtered-raw.json`,
`scripts/affective_pain_acupuncture_filtered.py` and the §7 it adds to
`research/affective-pain-neuromodulation-evidence-map.md`.

Why this test exists. §6 of the first map asked for a *filtered* acupuncture search, because
the first arm's "0 of 38 human-primary papers set both flags" was measured on a top-80
relevance slice of 791 matches — a slice that could produce the zero by construction. The
filtered arm finds candidates that the slice did not surface, so the corrected claim is a
different claim, and a reader is entitled to check it against the machine rather than take
it on trust. This test re-runs the item's own classifier over the stored records and refuses
the failure this repository has already paid for: an artefact that says a number the script
no longer produces.

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
import affective_pain_acupuncture_filtered as af  # noqa: E402

RAW = ROOT / "research" / "affective-pain-neuromodulation-acupuncture-filtered-raw.json"
MAP = ROOT / "research" / "affective-pain-neuromodulation-evidence-map.md"
SCRIPT = ROOT / "scripts" / "affective_pain_acupuncture_filtered.py"

# The measurement families §6 named, plus their synonyms. If the filter loses one, the arm
# silently stops being the query the map prints.
FILTER_FAMILIES = ["fmri", "functional magnetic resonance", "eeg", "electroencephalogra*",
                   "heart rate variability", "hrv", "autonomic", "skin conductance",
                   "vagal tone", "brainstem", "insula", "amygdala", "anterior cingulate",
                   "locus coeruleus"]

# The five human-primary records of the filtered census that set both the affective and the
# biomarker flag. Two are trials in a chronic-pain population; one is a hypothesis paper
# reporting a correlation between change in pain and change in mood; two are not
# pain-population affective-outcome studies. The map hand-reads all five, so all five must
# be named there.
HUMAN_PRIMARY_BOTH = ["24728839", "26025590", "26594625", "26787729", "37609769"]
PAIN_POPULATION_TRIALS = ["26787729", "37609769"]  # both fibromyalgia, both measure both

# The complement §8 hand-classifies (run 2026-10-06): the human-primary filtered-arm records that
# set the biomarker flag but not the affective one. Derivable from the stored flags — if this list
# and the machine's disagree, the map's §8 is describing a corpus the script no longer produces.
BIOMARKER_ONLY = ["27741200", "29325883", "30137262", "31176295", "31521794", "31922698",
                  "31964691", "32377180", "33314799", "35633164", "38897810", "39089662",
                  "40634927", "41086064", "41830820", "42309066"]


class AcupunctureFilteredArmTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads(RAW.read_text())
        cls.md = MAP.read_text()
        cls.records = cls.raw["records"]
        cls.arm = cls.raw["arms"][af.ARM]
        cls.by_id = {r["pmid"]: r for r in cls.records}

    # --- the artefact is internally reproducible ---------------------------------------

    def test_files_exist(self):
        self.assertTrue(RAW.exists(), "filtered raw record missing")
        self.assertTrue(SCRIPT.exists(), "filtered-arm script missing")
        self.assertIn("## 7.", self.md, "the map has no §7 for the filtered arm")

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
        """The whole point of step 2: no relevance ranking, so no count-by-construction."""
        self.assertEqual(self.arm["total_matching"], 40)
        self.assertEqual(self.arm["fetched"], 40)
        self.assertFalse(self.arm["censored"], "the filtered arm is no longer a complete census")
        self.assertIn("census", self.md)

    def test_the_query_is_the_filter_step_2_named(self):
        for fam in FILTER_FAMILIES:
            self.assertIn(fam, self.arm["filter"], f"filter family {fam!r} missing from the query")
            self.assertIn(fam, self.md, f"filter family {fam!r} not printed in the map")
        self.assertIn('acupuncture[tiab]', self.arm["query"])
        self.assertIn("humans[MeSH Terms]", self.arm["query"])

    # --- the map says what the machine says --------------------------------------------

    def test_composition_numbers_are_in_the_map(self):
        t = self.raw["tallies"]
        self.assertEqual(t["n_records"], 40)
        self.assertEqual(t["n_human_primary"], 21)
        self.assertEqual(t["n_review"], 12)
        self.assertEqual(t["n_protocol"], 2)
        self.assertEqual(t["n_animal_subject"], 11)
        self.assertEqual(t["n_both_affective_and_biomarker"], 18)
        self.assertEqual(t["n_neither"], 0)
        for value in (40, 21, 12, 11, 18):
            self.assertIn(f"**{value}**", self.md, f"{value} not printed in the map")

    def test_human_primary_both_set_is_exactly_the_five_named_rows(self):
        hp_both = sorted(r["pmid"] for r in self.records
                         if r["is_human_primary"] and r["both_affective_and_biomarker"])
        self.assertEqual(hp_both, HUMAN_PRIMARY_BOTH)
        for pmid in hp_both:
            self.assertIn(pmid, self.md, f"{pmid} is in the both-set but absent from the map")
        self.assertIn("5 of 21", self.md)
        for pmid in PAIN_POPULATION_TRIALS:
            self.assertEqual(self.by_id[pmid]["arm"], af.ARM)

    def test_biomarker_only_set_is_exactly_the_sixteen_named_rows(self):
        """§8: the complement of §7's both-set, re-derived from the stored flags, not re-listed."""
        hp_biomarker_only = sorted(r["pmid"] for r in self.records
                                   if r["is_human_primary"]
                                   and r["neural_or_autonomic_biomarker"]
                                   and not r["affective_outcome"])
        self.assertEqual(hp_biomarker_only, BIOMARKER_ONLY)
        self.assertEqual(len(hp_biomarker_only), 16)
        for pmid in hp_biomarker_only:
            self.assertIn(pmid, self.md, f"{pmid} is biomarker-only but absent from the map")
        self.assertIn("## 8.", self.md, "the map has no §8 for the biomarker-only records")
        self.assertIn("the brain and the pain, but not the mood", self.md)

    def test_the_correction_to_the_slice_claim_is_printed(self):
        """§4's '0 of 38' was a slice artefact; the map must say so, not quietly drop it."""
        self.assertIn("0 of the 38", self.md)          # the first map's claim is preserved
        self.assertIn("was the slice, not the literature", self.md)

    def test_the_map_still_refuses_to_claim_efficacy(self):
        self.assertIn("makes no claim about whether either intervention works", self.md)
        self.assertIn("hypothesis-generating", self.md)


if __name__ == "__main__":
    unittest.main(verbosity=2)
