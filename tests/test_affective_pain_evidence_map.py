#!/usr/bin/env python3
"""Pin the affective-pain evidence map (agenda item 32) to its source, mechanically.

Written 2026-09-29 (Desi, clock wake) with `research/affective-pain-neuromodulation-evidence-map.md`
and `research/affective-pain-neuromodulation-raw.json`.

The map's load-bearing numbers are counts of things the script can re-derive offline: how many
records came back, how many are reviews / protocols / animal-subject / human-primary, how many set
the affective and biomarker flags, and which human-primary records set both. This test re-runs the
script's own classifier over the stored records and fails if the stored tallies, the JSON's own
aggregates, or a number printed in the markdown has drifted apart.

It cannot re-run the PubMed query (tests run offline). What it can do is refuse the failure this
repository has already paid for: an artefact that says a number the machine no longer produces.
"""

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import affective_pain_search as aps  # noqa: E402

RAW = ROOT / "research" / "affective-pain-neuromodulation-raw.json"
MAP = ROOT / "research" / "affective-pain-neuromodulation-evidence-map.md"

# The two trials in a chronic-pain population the hand-read section turns on, and the
# dissociation figures quoted for them.
PAIN_POPULATION_TRIALS = ["41332177", "40935122"]
DISSOCIATION_FIGURES = {
    "41332177": [".365", ".776", "0.87", "0.94"],
    "40935122": ["0.070", "69.12", "62.24"],
}
# identifiers a stranger needs in the map
SEARCH_TERMS = ['acupuncture[tiab]', 'electroacupuncture[tiab]', '"vagus nerve stimulation"[tiab]',
                'humans[MeSH Terms]', '"chronic pain"[tiab]']


class AffectivePainEvidenceMapTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads(RAW.read_text())
        cls.md = MAP.read_text()
        cls.records = cls.raw["records"]
        cls.by_id = {r["pmid"]: r for r in cls.records}

    # --- the artefact is internally reproducible ---------------------------------------

    def test_both_files_exist(self):
        self.assertTrue(RAW.exists(), "raw source record missing")
        self.assertTrue(MAP.exists(), "evidence map missing")

    def test_stored_flags_match_the_script_classifier(self):
        """Every stored flag is what the script would produce today from the stored abstract."""
        drift = []
        for r in self.records:
            fresh = dict(aps.classify(r), **aps.classify_subject(r))
            for key, val in fresh.items():
                if key in ("affective", "biomarker", "intensity"):
                    val = bool(val)
                    have = bool(r.get(key))
                else:
                    have = r.get(key)
                if have != val:
                    drift.append((r["pmid"], key, have, val))
        self.assertEqual(drift, [], f"stored flags drifted from the classifier: {drift[:5]}")

    def test_stored_tallies_match_a_recomputation(self):
        self.assertEqual(aps.tally(self.records), self.raw["tallies"])

    def test_every_the_paper_cited_appears_in_the_raw_record(self):
        for pmid, figures in DISSOCIATION_FIGURES.items():
            rec = self.by_id[pmid]
            abstract = rec["abstract_plain"]
            for fig in figures:
                self.assertIn(fig, abstract, f"{fig} quoted for {pmid} is not in its abstract")

    # --- the map says what the machine says --------------------------------------------

    def test_composition_numbers_are_in_the_map(self):
        t = self.raw["tallies"]
        for label, value in [
            ("records", t["n_records"]), ("reviews", t["n_review"]),
            ("protocols", t["n_protocol"]), ("animal", t["n_animal_subject"]),
            ("human primary", t["n_human_primary"]), ("neither", t["n_neither"]),
            ("both terms", t["n_both_affective_and_biomarker"]),
        ]:
            self.assertIn(f"**{value}**", self.md, f"{label}={value} not printed in the map")

    def test_arm_counts_are_in_the_map(self):
        for arm, expected_total, expected_fetched in [("acupuncture", 791, 80), ("vns", 75, 75)]:
            a = self.raw["arms"][arm]
            self.assertEqual(a["total_matching"], expected_total)
            self.assertEqual(a["fetched"], expected_fetched)
            self.assertIn(str(expected_total), self.md, f"{arm} total {expected_total} missing")
        self.assertIn("complete census", self.md)

    def test_zero_acupuncture_human_primary_records_set_both_flags(self):
        acu = [r for r in self.records if r["arm"] == "acupuncture" and r["is_human_primary"]]
        both = [r for r in acu if r["both_affective_and_biomarker"]]
        self.assertEqual(both, [], "the map's '0 of the 38' claim no longer holds")
        self.assertIn("0 of the 38", self.md)

    def test_human_primary_both_set_is_exactly_the_eight_named_rows(self):
        hp_both = sorted(r["pmid"] for r in self.records
                         if r["is_human_primary"] and r["both_affective_and_biomarker"])
        self.assertEqual(len(hp_both), 8, f"expected 8, got {len(hp_both)}: {hp_both}")
        for pmid in hp_both:
            self.assertIn(pmid, self.md, f"{pmid} is in the both-set but absent from the map")
            self.assertEqual(self.by_id[pmid]["arm"], "vns",
                             f"{pmid} is not a VNS-arm record but the map says the set is all VNS")
        self.assertIn("8 of 73", self.md)

    def test_the_two_wide_limit_trials_are_in_the_map_with_their_figures(self):
        for pmid, figures in DISSOCIATION_FIGURES.items():
            self.assertIn(pmid, self.md, f"{pmid} missing from the map")
            for fig in figures:
                self.assertIn(fig, self.md, f"figure {fig} for {pmid} not printed in the map")

    def test_title_restatement_count_in_the_map_is_recomputable(self):
        def title_fired(rec, kind):
            hit = rec.get(kind)
            if not hit:
                return False
            sentence = hit["sentence"].rstrip(".")
            return sentence[:70].lower() == rec["title"].rstrip(".").lower()[:70]

        inflated = [r["pmid"] for r in self.records if r["both_affective_and_biomarker"]
                    and (title_fired(r, "affective") or title_fired(r, "biomarker"))]
        self.assertEqual(len(inflated), 15, f"title-restatement count moved: {len(inflated)}")
        self.assertIn("15 of the 25", self.md)
        self.assertIn("16 records", self.md)

    def test_the_search_is_printed_in_the_map(self):
        for term in SEARCH_TERMS:
            self.assertIn(term, self.md, f"search term {term!r} not recorded in the map")
        for arm, a in self.raw["arms"].items():
            self.assertIn('"chronic pain"[tiab]', a["query"])
            self.assertIn("humans[MeSH Terms]", a["query"])

    def test_map_still_declines_to_claim_efficacy(self):
        """The map must not be read as a verdict on efficacy; keep the disclaimer pinned."""
        self.assertIn("makes no claim about whether either intervention works", self.md)


if __name__ == "__main__":
    unittest.main(verbosity=2)
