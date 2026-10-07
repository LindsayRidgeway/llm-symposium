#!/usr/bin/env python3
"""Pin the filtered VNS arm (agenda item 32, step 3) to its source, mechanically.

Written 2026-10-07 (Desi, clock wake) with
`research/affective-pain-neuromodulation-vns-filtered-raw.json`,
`scripts/affective_pain_vns_filtered.py` and the §9 it adds to
`research/affective-pain-neuromodulation-evidence-map.md`.

Why this test exists. §8 sharpened §7 to "the brain and the pain, but not the mood" from the
acupuncture records alone. Step 3 asks whether that affect-blindness generalises beyond
acupuncture, so §9 runs the same filtered design against the item's second intervention, VNS,
as a 31-record census. A census that claims the omitted column is acupuncture-specific has to
be checkable against the machine, not taken on trust: this test re-runs the item's own
classifier over the stored records and refuses the failure this repository has already paid
for -- an artefact that prints a number the script no longer produces.

It cannot re-run the PubMed query (tests run offline). It checks that the stored census, the
stored flags, the JSON's own aggregates and the numbers printed in §9 still agree.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import affective_pain_search as aps  # noqa: E402
import affective_pain_acupuncture_filtered as af  # noqa: E402
import affective_pain_vns_filtered as vf  # noqa: E402

RAW = ROOT / "research" / "affective-pain-neuromodulation-vns-filtered-raw.json"
MAP = ROOT / "research" / "affective-pain-neuromodulation-evidence-map.md"
SCRIPT = ROOT / "scripts" / "affective_pain_vns_filtered.py"

# The 8 human-primary records of the VNS filtered census that set both the affective and the
# biomarker flag. This set is identical to the 8 that §4 hand-read from the first corpus -- the
# filtered census reproduces the slice's both-set, so if the two ever diverge one of them is
# describing a corpus the script no longer produces.
HUMAN_PRIMARY_BOTH = ["26450637", "34509623", "34634682", "38963558",
                      "40576705", "40935122", "41044114", "41332177"]

# The 10 human-primary records that set the biomarker flag but no affect term.
BIOMARKER_ONLY = ["26728182", "33262253", "33548494", "33635894", "38469939",
                  "40461351", "41091086", "41454683", "42334392", "42361949"]

# §9's sharpest single case: it names the item's own brainstem hubs (NTS, locus coeruleus,
# raphe) in a chronic-pain population and measures no affective outcome. Cited by name in §9.
PATHWAY_WITHOUT_AFFECT = "41091086"


class VnsFilteredArmTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(RAW.read_text())
        cls.records = cls.record["records"]
        cls.by_id = {r["pmid"]: r for r in cls.records}
        cls.t = cls.record["tallies"]
        cls.md = MAP.read_text()
        cls.script = SCRIPT.read_text()

    def test_arm_is_a_census_not_a_slice(self):
        a = self.record["arms"][vf.ARM]
        self.assertFalse(a["censored"], "the VNS filtered arm is a census; it must not be censored")
        self.assertEqual(a["fetched"], 31)
        self.assertEqual(a["total_matching"], 31)
        self.assertEqual(len(self.records), 31)

    def test_composition_is_what_the_map_prints(self):
        t = self.t
        self.assertEqual(t["n_records"], 31)
        self.assertEqual(t["n_human_primary"], 20)
        self.assertEqual(t["n_both_affective_and_biomarker"], 14)
        self.assertEqual(t["n_neither"], 1)
        for value in (31, 20, 8, 10):
            self.assertIn(str(value), self.md, f"{value} not printed in the map")

    def test_human_primary_both_set_is_exactly_the_eight_named_rows(self):
        hp_both = sorted(r["pmid"] for r in self.records
                         if r["is_human_primary"] and r["both_affective_and_biomarker"])
        self.assertEqual(hp_both, HUMAN_PRIMARY_BOTH)
        self.assertEqual(len(hp_both), 8)
        for pmid in hp_both:
            self.assertIn(pmid, self.md, f"{pmid} is in the both-set but absent from the map")
        self.assertIn("8 of 20", self.md)

    def test_biomarker_only_set_is_exactly_the_ten_named_rows(self):
        hp_biomarker_only = sorted(r["pmid"] for r in self.records
                                   if r["is_human_primary"]
                                   and r["neural_or_autonomic_biomarker"]
                                   and not r["affective_outcome"])
        self.assertEqual(hp_biomarker_only, BIOMARKER_ONLY)
        self.assertEqual(len(hp_biomarker_only), 10)
        for pmid in hp_biomarker_only:
            self.assertIn(pmid, self.md, f"{pmid} is biomarker-only but absent from the map")
        self.assertIn("10 of 20", self.md)
        self.assertIn(PATHWAY_WITHOUT_AFFECT, self.md)

    def test_the_section_and_its_headline_finding_are_printed(self):
        self.assertIn("## 9. The filtered VNS arm", self.md)
        self.assertIn("acupuncture-specific", self.md)
        self.assertIn("shared pathway", self.md)

    def test_the_filter_is_the_identical_acupuncture_arm_filter(self):
        # imported, not re-typed, so a difference between the arms is the papers, not the query
        self.assertEqual(vf.MEASUREMENT, af.MEASUREMENT)
        self.assertIn("vagus nerve stimulation", vf.QUERY)
        self.assertIn("humans[MeSH Terms]", vf.QUERY)
        self.assertIn("import affective_pain_acupuncture_filtered as apf", self.script)
        self.assertIn("MEASUREMENT = apf.MEASUREMENT", self.script)

    def test_the_map_still_refuses_to_claim_efficacy(self):
        self.assertIn("makes no claim about whether either intervention works", self.md)


if __name__ == "__main__":
    unittest.main(verbosity=2)
