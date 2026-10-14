#!/usr/bin/env python3
"""Pin the confound arm (agenda item 32, §11) to its source, mechanically.

Written 2026-10-14 (Desi, clock wake) with
`research/affective-pain-neuromodulation-confound-arm-raw.json`,
`scripts/affective_pain_confound_arm.py` and §11 of
`research/affective-pain-neuromodulation-evidence-map.md`.

Why this test exists. §11 closes the confound §9 named: it runs the *same* filtered design over the
**low-back-pain population restricted to acupuncture**, holding population and intervention fixed at
once, and reports that the affective column goes to **zero** (0 of 3 human-primary) where §9's wider
low-back-pain arm had it at 76 of 165. A zero is the count most easily mistaken for a broken query, so
the number matters more, not less: a reader is entitled to check that the census still holds five
records, that three are human-primary, and that none of the three names an affect term — against the
stored census, rather than take it on trust.

It cannot re-run the PubMed query (tests run offline). It checks that the stored census, the stored
flags, the JSON's own aggregates, the query's blocks, and the numbers printed in §11 still agree.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import affective_pain_search as aps  # noqa: E402
import affective_pain_acupuncture_filtered as apf  # noqa: E402
import affective_pain_second_population as asp  # noqa: E402
import affective_pain_confound_arm as aca  # noqa: E402

RAW = ROOT / "research" / "affective-pain-neuromodulation-confound-arm-raw.json"
MAP = ROOT / "research" / "affective-pain-neuromodulation-evidence-map.md"
SCRIPT = ROOT / "scripts" / "affective_pain_confound_arm.py"

# The census facts §11 prints. If the census changes, these fail and §11 must be rewritten, not edited.
CENSUS = 5
HUMAN_PRIMARY = 3
REVIEWS = 2
PROTOCOLS = 0
ANIMALS = 1
BOTH_FLAG = 2          # both are the reviews
HP_BOTH = 0            # the number that carries the claim
HP_PMIDS = ["29343693", "31176295", "31964691"]
BOTH_PMIDS = ["25796668", "42670051"]

# The measurement families the step-2 filter names; §11 must reuse the *same* filter object.
FILTER_FAMILIES = ["fmri", "functional magnetic resonance", "eeg", "heart rate variability", "hrv",
                   "autonomic", "insula", "amygdala", "anterior cingulate", "brainstem",
                   "locus coeruleus"]


class ConfoundArmTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads(RAW.read_text())
        cls.md = MAP.read_text()
        cls.records = cls.raw["records"]
        cls.arm = cls.raw["arms"][aca.ARM]
        cls.by_id = {r["pmid"]: r for r in cls.records}
        cls.hp = [r for r in cls.records if r["is_human_primary"]]
        cls.hp_both = [r for r in cls.hp if r["both_affective_and_biomarker"]]

    # --- the artefact is internally reproducible ---------------------------------------

    def test_files_exist(self):
        self.assertTrue(RAW.exists(), "confound-arm raw record missing")
        self.assertTrue(SCRIPT.exists(), "confound-arm script missing")
        self.assertIn("## 11.", self.md, "the map has no §11 for the confound arm")

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
        self.assertEqual(self.arm["total_matching"], CENSUS)
        self.assertEqual(self.arm["fetched"], CENSUS)
        self.assertFalse(self.arm["censored"], "the confound arm is no longer a census")

    # --- the query holds BOTH blocks fixed ---------------------------------------------

    def test_the_filter_is_the_step2_filter_unchanged(self):
        self.assertEqual(self.arm["filter"], apf.MEASUREMENT,
                         "the confound arm re-typed the filter instead of importing it")
        for fam in FILTER_FAMILIES:
            self.assertIn(fam, self.arm["filter"], f"filter family {fam!r} missing from the query")

    def test_both_blocks_are_present_and_the_generic_pain_block_is_not(self):
        q = self.arm["query"]
        # population block = §9's own object
        self.assertEqual(self.arm["population_block"], asp.POPULATIONS["low_back_pain"])
        # intervention block = §7's own object
        self.assertEqual(self.arm["intervention_block"], aps.ARMS["acupuncture"])
        self.assertIn('"chronic low back pain"[tiab]', q)
        self.assertIn("acupuncture[tiab]", q)
        self.assertIn("humans[MeSH Terms]", q)
        # the whole point: the *generic* pain block is not there, the named population stands in for it
        self.assertNotIn(aps.PAIN, q,
                         "the confound arm must replace the generic PAIN block with the named population")

    # --- the counts §11 prints are the counts the machine holds ------------------------

    def test_composition_numbers(self):
        t = self.raw["tallies"]
        self.assertEqual(t["n_records"], CENSUS)
        self.assertEqual(t["n_human_primary"], HUMAN_PRIMARY)
        self.assertEqual(t["n_review"], REVIEWS)
        self.assertEqual(t["n_protocol"], PROTOCOLS)
        self.assertEqual(t["n_animal_subject"], ANIMALS)
        self.assertEqual(t["n_both_affective_and_biomarker"], BOTH_FLAG)

    def test_the_result_is_the_zero(self):
        self.assertEqual(len(self.hp), HUMAN_PRIMARY)
        self.assertEqual(sorted(r["pmid"] for r in self.hp), sorted(HP_PMIDS))
        self.assertEqual(self.hp_both, [], "a human-primary record now sets both flags — §11's zero is stale")
        self.assertEqual(len(self.hp_both), HP_BOTH)
        # the both-flag records are reviews, not trials
        self.assertEqual(sorted(r["pmid"] for r in self.records
                                if r["both_affective_and_biomarker"]), sorted(BOTH_PMIDS))
        for pmid in BOTH_PMIDS:
            self.assertTrue(self.by_id[pmid]["is_review"], f"{pmid} should be the review that sets both")

    def test_the_map_prints_the_zero_and_the_census(self):
        self.assertIn("**5 — census**", self.md)
        self.assertIn("**human primary** | **3**", self.md)
        self.assertIn("**human-primary both** | **0**", self.md)
        self.assertIn("0 of 3", self.md)
        self.assertIn("low_back_pain_acupuncture_filtered", self.md)
        for pmid in HP_PMIDS:
            self.assertIn(pmid, self.md, f"{pmid} is human-primary but absent from §11")

    def test_the_confound_is_declared_closed(self):
        self.assertIn("closed, from both sides", self.md)
        self.assertIn("absence, and it must be read as one", self.md)

    def test_the_map_still_refuses_to_claim_efficacy(self):
        self.assertIn("makes no claim about whether either intervention works", self.md)


if __name__ == "__main__":
    unittest.main(verbosity=2)
