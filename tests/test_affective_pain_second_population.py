#!/usr/bin/env python3
"""Pin the second-population arm (agenda item 32, step 3) to its source, mechanically.

Written 2026-10-08 (Dmitri, clock wake) with
`research/affective-pain-neuromodulation-second-population-raw.json`,
`scripts/affective_pain_second_population.py` and §9 of
`research/affective-pain-neuromodulation-evidence-map.md`.

Why this test exists. §9 answers item 32's generalisation step: it runs the *same* filtered design
(the step-2 measurement filter, imported not re-typed) against a *second* pain population — chronic
low back pain — and reports that §8's affect-blindness does not carry. That claim rests on a set of
counts (`76 of 165`, `77 of 165`, `18` title restatements, `15` named affect instruments), and a
reader is entitled to check them against the stored census rather than take them on trust. This test
re-derives every number §9 prints and refuses the failure this repository has already paid for: an
artefact that says a number the script no longer produces.

It cannot re-run the PubMed query (tests run offline). It checks that the stored census, the stored
flags, the JSON's own aggregates, the query's filter, and the numbers printed in §9 still agree.
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
import affective_pain_second_population as asp  # noqa: E402

RAW = ROOT / "research" / "affective-pain-neuromodulation-second-population-raw.json"
MAP = ROOT / "research" / "affective-pain-neuromodulation-evidence-map.md"
SCRIPT = ROOT / "scripts" / "affective_pain_second_population.py"

# The measurement families the step-2 filter names. §9 must reuse the *same* filter object, so the
# test pins identity against `af.MEASUREMENT` below rather than re-listing the families.
FILTER_FAMILIES = ["fmri", "functional magnetic resonance", "eeg", "heart rate variability", "hrv",
                   "autonomic", "insula", "amygdala", "anterior cingulate", "brainstem",
                   "locus coeruleus"]

# Tally facts §9 prints. If the census changes, these fail and §9 must be rewritten, not edited.
CENSUS = 197
HUMAN_PRIMARY = 165
BOTH = 96
REVIEWS = 20
PROTOCOLS = 12
ANIMALS = 4
HP_AFFECTIVE = 77
HP_BOTH = 76
HP_CO_MENTION = 45

# The two corrections §9 prints beside the headline. Re-derived here with the same rules the run used.
TITLE_RESTATEMENTS = 18
NAMED_AFFECT_INSTRUMENTS = 15
INSTRUMENT_PMIDS = ["27168362", "27771534", "30839429", "31252090", "34378878", "34633449",
                    "35080703", "37306031", "38049905", "38285031", "40343412", "40403861",
                    "40785007", "40945096", "42419415"]

_INSTR = re.compile(
    r"\b(stai|state[- ]trait anxiety|beck depression|bdi|hads|hospital anxiety|phq|"
    r"hamilton (depression|rating)|hdrs|hamd|ces[- ]?d|dass|pain catastrophizing|pcs\b|"
    r"depression (score|scale|questionnaire)|anxiety (score|scale|inventory|questionnaire)|"
    r"mood (scale|score)|promis)", re.I)


def _norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def _title_restatement(rec):
    a = _norm(rec["affective"]["sentence"])
    t = _norm(rec["title"])
    return a.startswith(t) or (len(t) > 25 and t[:60] in a)


class SecondPopulationArmTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads(RAW.read_text())
        cls.md = MAP.read_text()
        cls.records = cls.raw["records"]
        cls.arm = cls.raw["arms"][asp.ARM]
        cls.by_id = {r["pmid"]: r for r in cls.records}
        cls.hp = [r for r in cls.records if r["is_human_primary"]]
        cls.hp_both = [r for r in cls.hp if r["both_affective_and_biomarker"]]

    # --- the artefact is internally reproducible ---------------------------------------

    def test_files_exist(self):
        self.assertTrue(RAW.exists(), "second-population raw record missing")
        self.assertTrue(SCRIPT.exists(), "second-population script missing")
        self.assertIn("## 9.", self.md, "the map has no §9 for the second-population arm")

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
        self.assertFalse(self.arm["censored"], "the second-population arm is no longer a census")
        self.assertIn("**197 — census**", self.md)

    def test_the_filter_is_the_step2_filter_unchanged(self):
        """The whole claim is 'the same filtered design'; the filter must be the same object."""
        self.assertEqual(self.arm["filter"], af.MEASUREMENT,
                         "the second arm re-typed the filter instead of importing it")
        for fam in FILTER_FAMILIES:
            self.assertIn(fam, self.arm["filter"], f"filter family {fam!r} missing from the query")
        self.assertIn('"chronic low back pain"[tiab]', self.arm["query"])
        self.assertIn("humans[MeSH Terms]", self.arm["query"])
        self.assertIn("low back pain", self.md)

    # --- the counts §9 prints are the counts the machine holds -------------------------

    def test_composition_numbers_are_in_the_map(self):
        t = self.raw["tallies"]
        self.assertEqual(t["n_records"], CENSUS)
        self.assertEqual(t["n_human_primary"], HUMAN_PRIMARY)
        self.assertEqual(t["n_both_affective_and_biomarker"], BOTH)
        self.assertEqual(t["n_review"], REVIEWS)
        self.assertEqual(t["n_protocol"], PROTOCOLS)
        self.assertEqual(t["n_animal_subject"], ANIMALS)
        for value in (CENSUS, HUMAN_PRIMARY, BOTH, REVIEWS, PROTOCOLS, ANIMALS):
            self.assertIn(f"**{value}**", self.md, f"{value} not printed in the map")

    def test_human_primary_counts_are_in_the_map(self):
        self.assertEqual(len(self.hp), HUMAN_PRIMARY)
        self.assertEqual(sum(1 for r in self.hp if r["affective_outcome"]), HP_AFFECTIVE)
        self.assertEqual(len(self.hp_both), HP_BOTH)
        self.assertEqual(sum(1 for r in self.hp if r.get("co_mention_sentence")), HP_CO_MENTION)
        self.assertIn("**5 (24%)**", self.md)          # the acupuncture arm's rate
        self.assertIn("**77 (47%)**", self.md)         # this arm's affect rate
        self.assertIn("**76 (46%)**", self.md)         # this arm's both rate
        self.assertIn("**45 (27%)**", self.md)         # this arm's same-sentence co-mention

    def test_the_result_is_the_non_generalisation(self):
        self.assertIn("the affect-blindness does not generalise", self.md)
        self.assertIn("the brain and the pain, but not the mood", self.md)  # §8's claim, quoted

    def test_the_two_corrections_are_re_derivable(self):
        tr = [r for r in self.hp_both if _title_restatement(r)]
        self.assertEqual(len(tr), TITLE_RESTATEMENTS,
                         "the title-restatement count §9 prints no longer matches the census")
        instr = sorted(r["pmid"] for r in self.hp_both if _INSTR.search(r["affective"]["sentence"]))
        self.assertEqual(instr, INSTRUMENT_PMIDS,
                         "the named-instrument set §9 prints no longer matches the census")
        self.assertEqual(len(instr), NAMED_AFFECT_INSTRUMENTS)
        for pmid in instr:
            self.assertIn(pmid, self.md, f"{pmid} names an affect instrument but is absent from the map")

    def test_the_confound_is_stated_not_hidden(self):
        self.assertIn("The confound, stated plainly", self.md)
        self.assertIn("intervention", self.md)

    def test_the_map_still_refuses_to_claim_efficacy(self):
        self.assertIn("makes no claim about whether either intervention works", self.md)


if __name__ == "__main__":
    unittest.main(verbosity=2)
