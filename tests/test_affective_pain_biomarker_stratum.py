#!/usr/bin/env python3
"""Pin the biomarker-only stratum of the filtered acupuncture arm (agenda item 32, step 2).

Written 2026-10-06 (Dmitri, clock wake) with §8 of
`research/affective-pain-neuromodulation-evidence-map.md`.

Why this test exists. §7 hand-read the 5 human-primary filtered-arm records that set *both* the
affective and the biomarker flag, but left the 16 that set the biomarker flag *only* unread — and
§7's claim ("the acupuncture literature measures the brain and not the mood") rests on them. §8
reads all 16 and sorts them into five kinds; this test re-runs the item's own classifier over the
stored records offline and refuses the failure this repository has already paid for: an artefact
that says a number the machine no longer produces.

It checks that the 16-PMID set is what the classifier produces today, that the map names all 16
and prints the counts, and it re-checks the two instrument findings §8 records — the review
detector that misses `Meta-Analysis`, and the census record that carries no acupuncture token.
"""

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import affective_pain_search as aps  # noqa: E402

RAW = ROOT / "research" / "affective-pain-neuromodulation-acupuncture-filtered-raw.json"
MAP = ROOT / "research" / "affective-pain-neuromodulation-evidence-map.md"

# The 16 human-primary filtered-arm records that set the biomarker flag and not the affective flag.
BIOMARKER_ONLY = [
    "27741200", "29325883", "30137262", "31176295", "31521794", "31922698", "31964691",
    "32377180", "33314799", "35633164", "38897810", "39089662", "40634927", "41086064",
    "41830820", "42309066",
]

# §8 sorts those 16 into five kinds; the counts are pinned here and printed in the map.
BRAIN_CHRONIC_PAIN = ["41830820", "41086064", "40634927", "39089662", "33314799", "32377180",
                      "31964691", "31922698", "31176295", "29325883"]           # 10
HEALTHY_OR_EXPERIMENTAL = ["31521794", "30137262"]                             # 2
NOT_PRIMARY = ["38897810", "35633164"]                                         # 2
NOT_ACUPUNCTURE = ["42309066"]                                                 # 1
PSYCHOTHERAPY_RCT = ["27741200"]                                               # 1


class BiomarkerOnlyStratumTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads(RAW.read_text())
        cls.md = MAP.read_text()
        cls.records = cls.raw["records"]
        cls.by_id = {r["pmid"]: r for r in cls.records}

    def _recomputed(self):
        """Re-derive human-primary + biomarker-only from the stored abstracts via the script."""
        out = []
        for r in self.records:
            flags = dict(aps.classify(r), **aps.classify_subject(r))
            if flags["is_human_primary"] and flags["neural_or_autonomic_biomarker"] \
                    and not flags["affective_outcome"]:
                out.append(r["pmid"])
        return sorted(out)

    # --- the set is what the machine produces ---------------------------------------------

    def test_the_stratum_is_exactly_the_sixteen_named_records(self):
        self.assertEqual(self._recomputed(), sorted(BIOMARKER_ONLY))

    def test_the_five_kinds_partition_the_sixteen(self):
        parts = [BRAIN_CHRONIC_PAIN, HEALTHY_OR_EXPERIMENTAL, NOT_PRIMARY,
                 NOT_ACUPUNCTURE, PSYCHOTHERAPY_RCT]
        flat = [p for part in parts for p in part]
        self.assertEqual(sorted(flat), sorted(BIOMARKER_ONLY), "kinds do not partition the set")
        self.assertEqual(len(flat), len(set(flat)), "a record is in two kinds")
        self.assertEqual([len(p) for p in parts], [10, 2, 2, 1, 1])

    def test_the_stratum_is_the_human_primary_minus_the_both_set(self):
        hp = sorted(r["pmid"] for r in self.records if r["is_human_primary"])
        both = sorted(r["pmid"] for r in self.records
                      if r["is_human_primary"] and r["both_affective_and_biomarker"])
        self.assertEqual(len(hp), 21)
        self.assertEqual(sorted(set(hp) - set(both)), sorted(BIOMARKER_ONLY))

    # --- the map says what the machine says ------------------------------------------------

    def test_the_map_has_the_section_and_names_every_record(self):
        self.assertIn("## 8.", self.md)
        for pmid in BIOMARKER_ONLY:
            self.assertIn(pmid, self.md, f"{pmid} is in the stratum but absent from the map")

    def test_the_map_prints_the_counts(self):
        for phrase in ["16 of 21", "10 of 16", "2 of 16", "1 of 16", "zero of the 16"]:
            self.assertIn(phrase, self.md, f"count phrase {phrase!r} not printed in the map")
        self.assertIn("12 of the 16", self.md)

    # --- the two instrument findings §8 records --------------------------------------------

    def test_the_review_detector_misses_meta_analysis(self):
        """`is_review` only tests publication types for the substring 'review', so a
        Meta-Analysis record (38897810) is counted human-primary. The map must say so."""
        rec = self.by_id["38897810"]
        self.assertIn("Meta-Analysis", rec["publication_types"])
        self.assertFalse(aps.classify_subject(rec)["is_review"],
                         "the review detector no longer misses this record — update §8")
        self.assertTrue(aps.classify_subject(rec)["is_human_primary"])
        self.assertIn("misses syntheses", self.md)

    def test_one_census_record_carries_no_acupuncture_token(self):
        rec = self.by_id["42309066"]
        blob = " ".join([rec["title"], rec.get("abstract_plain") or "",
                         " ".join(rec.get("mesh") or [])])
        self.assertIsNone(re.search(r"acu", blob, re.I),
                          "42309066 now carries an acupuncture token — update §8")
        self.assertIn("no acupuncture token", self.md)


if __name__ == "__main__":
    unittest.main(verbosity=2)
