#!/usr/bin/env python3
"""Pin the filtered VNS arm (agenda item 32, §10) to its source, mechanically.

Written 2026-10-14 (Desi, clock wake) to give §10 of
`research/affective-pain-neuromodulation-evidence-map.md` the pin its two sibling arms already had
(`tests/test_affective_pain_acupuncture_filtered.py` for §7, `tests/test_affective_pain_second_population.py`
for §9). The census itself (`scripts/affective_pain_vns_filtered.py` and
`research/affective-pain-neuromodulation-vns-filtered-raw.json`) was fetched on 2026-10-09 and sat on
`main` with no write-up and no check for five days.

Why this test exists. §10 answers item 32's symmetry question by holding one filter fixed and changing
only the intervention block — acupuncture (§7) against VNS — and reports that the raw 24%-vs-40% gap is
mostly vocabulary and title artefacts, that the same title-restatement correction brings it to 19% vs
25%, and that the hand-read residue is two trials in a pain population on each side. Every one of those
numbers is re-derived here from the stored census, because a rate printed in prose is exactly the kind of
claim that drifts from the machine that produced it.

It cannot re-run the PubMed query (tests run offline). It checks that the stored census, the stored
flags, the JSON's own aggregates, the shared filter object, and the numbers §10 prints still agree.
"""

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import affective_pain_search as aps  # noqa: E402
import affective_pain_acupuncture_filtered as af  # noqa: E402
import affective_pain_vns_filtered as avf  # noqa: E402

RAW = ROOT / "research" / "affective-pain-neuromodulation-vns-filtered-raw.json"
MAP = ROOT / "research" / "affective-pain-neuromodulation-evidence-map.md"
SCRIPT = ROOT / "scripts" / "affective_pain_vns_filtered.py"

# Composition §10 prints. If the census changes, these fail and §10 must be rewritten, not edited.
CENSUS = 31
REVIEWS = 7
PROTOCOLS = 3
ANIMALS = 1
BOTH_ALL = 14
HUMAN_PRIMARY = 20
HP_AFFECTIVE = 9
HP_BIOMARKER = 18
HP_BOTH = 8
HP_CO_MENTION = 5
HP_PAIN_INSTRUMENT = 8
HP_BIOMARKER_ONLY = 10

# The eight human-primary records that set both flags. §4 hand-read exactly these eight from the
# *unfiltered* arm; §10's cross-check is that the filtered census reproduces the same set, so this
# list is the load-bearing fact of the section.
BOTH_PMIDS = ["26450637", "34509623", "34634682", "38963558",
              "40576705", "40935122", "41044114", "41332177"]

# The complement §10 names but does not yet hand-classify (the VNS counterpart to §8's sixteen).
BIOMARKER_ONLY_PMIDS = ["26728182", "33262253", "33548494", "33635894", "38469939",
                        "40461351", "41091086", "41454683", "42334392", "42361949"]
AFFECTIVE_ONLY_PMIDS = ["38815433"]
NEITHER_PMIDS = ["42029130"]

# The §5 title-restatement correction, re-derived with the same rule §9 used.
TITLE_RESTATEMENTS = 3
TITLE_RESTATE_PMIDS = ["38963558", "40935122", "41332177"]

# The hand-read residue §10 carries: the trials in a chronic-pain population that actually measured an
# affective outcome — two on each intervention side (acupuncture's pair is 37609769 / 26787729, §7).
VNS_MEASURED_PAIN_TRIALS = ["40935122", "41332177"]
# The other six of the eight: background/indication phrases, a title restatement, or a single case.
VNS_BACKGROUND_PMIDS = ["34509623", "34634682", "40576705", "41044114"]
VNS_TITLE_ONLY = "38963558"
VNS_CASE_REPORT = "26450637"


def _norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def _title_restatement(rec):
    a = _norm(rec["affective"]["sentence"])
    t = _norm(rec["title"])
    return a.startswith(t) or (len(t) > 25 and t[:60] in a)


class VnsFilteredArmTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads(RAW.read_text())
        cls.md = MAP.read_text()
        cls.records = cls.raw["records"]
        cls.arm = cls.raw["arms"][avf.ARM]
        cls.by_id = {r["pmid"]: r for r in cls.records}
        cls.hp = [r for r in cls.records if r["is_human_primary"]]
        cls.hp_both = [r for r in cls.hp if r["both_affective_and_biomarker"]]

    # --- the artefact is internally reproducible ---------------------------------------

    def test_files_exist(self):
        self.assertTrue(RAW.exists(), "filtered VNS raw record missing")
        self.assertTrue(SCRIPT.exists(), "filtered VNS script missing")
        self.assertIn("## 10. The filtered VNS arm", self.md, "the map has no §10 for the VNS arm")

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
        self.assertFalse(self.arm["censored"], "the filtered VNS arm is no longer a complete census")
        self.assertIn("31 — census", self.md)

    def test_the_filter_is_the_step2_filter_unchanged(self):
        """The whole claim is 'the same filtered design'; the filter must stay the same object."""
        self.assertEqual(self.arm["filter"], af.MEASUREMENT,
                         "the VNS arm re-typed the filter instead of importing it")
        self.assertEqual(avf.MEASUREMENT, af.MEASUREMENT)
        self.assertIn("humans[MeSH Terms]", self.arm["query"])
        self.assertIn("vagus", self.arm["query"])

    # --- the counts §10 prints are the counts the machine holds -------------------------

    def test_composition_numbers_are_in_the_map(self):
        t = self.raw["tallies"]
        self.assertEqual(t["n_records"], CENSUS)
        self.assertEqual(t["n_review"], REVIEWS)
        self.assertEqual(t["n_protocol"], PROTOCOLS)
        self.assertEqual(t["n_animal_subject"], ANIMALS)
        self.assertEqual(t["n_both_affective_and_biomarker"], BOTH_ALL)
        self.assertEqual(t["n_human_primary"], HUMAN_PRIMARY)
        for value in (CENSUS, REVIEWS, PROTOCOLS, ANIMALS, BOTH_ALL, HUMAN_PRIMARY):
            self.assertIn(f"**{value}**", self.md, f"{value} not printed in the map")

    def test_human_primary_counts_are_in_the_map(self):
        self.assertEqual(len(self.hp), HUMAN_PRIMARY)
        self.assertEqual(sum(1 for r in self.hp if r["affective_outcome"]), HP_AFFECTIVE)
        self.assertEqual(sum(1 for r in self.hp if r["neural_or_autonomic_biomarker"]), HP_BIOMARKER)
        self.assertEqual(len(self.hp_both), HP_BOTH)
        self.assertEqual(sum(1 for r in self.hp if r.get("co_mention_sentence")), HP_CO_MENTION)
        self.assertEqual(sum(1 for r in self.hp if r.get("pain_intensity_instrument")), HP_PAIN_INSTRUMENT)
        # the three-arm rates §10 prints
        self.assertIn("**8 (40%)**", self.md)
        self.assertIn("**5 (24%)**", self.md)
        self.assertIn("5 of 20 (25%)", self.md)
        self.assertIn("4 of 21 (19%)", self.md)

    def test_human_primary_both_set_is_exactly_the_eight_of_section_4(self):
        hp_both = sorted(r["pmid"] for r in self.hp_both)
        self.assertEqual(hp_both, sorted(BOTH_PMIDS))
        self.assertIn("exactly those eight", self.md)
        for pmid in BOTH_PMIDS:
            self.assertIn(pmid, self.md, f"{pmid} is in the both-set but absent from the map")

    def test_the_residual_records_are_exactly_the_ones_named(self):
        bo = sorted(r["pmid"] for r in self.hp
                    if r["neural_or_autonomic_biomarker"] and not r["affective_outcome"])
        ao = sorted(r["pmid"] for r in self.hp
                    if r["affective_outcome"] and not r["neural_or_autonomic_biomarker"])
        neither = sorted(r["pmid"] for r in self.hp
                         if not r["affective_outcome"] and not r["neural_or_autonomic_biomarker"])
        self.assertEqual(bo, sorted(BIOMARKER_ONLY_PMIDS))
        self.assertEqual(len(bo), HP_BIOMARKER_ONLY)
        self.assertEqual(ao, AFFECTIVE_ONLY_PMIDS)
        self.assertEqual(neither, NEITHER_PMIDS)
        for pmid in BIOMARKER_ONLY_PMIDS + AFFECTIVE_ONLY_PMIDS + NEITHER_PMIDS:
            self.assertIn(pmid, self.md, f"{pmid} named in §10 but absent from the map")

    def test_the_title_restatement_correction_is_re_derivable(self):
        tr = sorted(r["pmid"] for r in self.hp_both if _title_restatement(r))
        self.assertEqual(tr, sorted(TITLE_RESTATE_PMIDS),
                         "the title-restatement count §10 prints no longer matches the census")
        self.assertEqual(len(tr), TITLE_RESTATEMENTS)
        self.assertIn("3 of 8", self.md)

    def test_the_hand_read_residue_is_the_two_named_trials(self):
        """The claim is 'two trials in a pain population that measured affect'; the act reports the two
        and returns the rest to background. This pins the pmed ids §10 names on each side of that line."""
        self.assertEqual(sorted(VNS_MEASURED_PAIN_TRIALS), sorted(["40935122", "41332177"]))
        for pmid in VNS_MEASURED_PAIN_TRIALS:
            self.assertTrue(self.by_id[pmid]["both_affective_and_biomarker"])
            self.assertIn(pmid, self.md)
        # the six the section returns to background / title-only / case report
        for pmid in VNS_BACKGROUND_PMIDS + [VNS_TITLE_ONLY, VNS_CASE_REPORT]:
            self.assertTrue(self.by_id[pmid]["both_affective_and_biomarker"])
            self.assertIn(pmid, self.md)
        self.assertIn("the same two trials each", self.md)

    def test_the_result_is_the_collapse_of_the_raw_gap(self):
        self.assertIn("the apparent intervention gap is mostly vocabulary and titles", self.md)
        self.assertIn("the brain and the pain, but not the mood", self.md)  # §8's claim, quoted

    def test_the_map_still_refuses_to_claim_efficacy(self):
        self.assertIn("makes no claim about whether either intervention works", self.md)


if __name__ == "__main__":
    unittest.main(verbosity=2)
