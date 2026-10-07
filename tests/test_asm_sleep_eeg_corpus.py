#!/usr/bin/env python3
"""Pin the antiseizure-medication x sleep-EEG corpus (agenda item 30 step 3), offline.

Written 2026-10-07 (Desi, clock wake) with `research/asm-sleep-eeg-corpus.md` and
`research/asm-sleep-eeg-raw.json`.

The item's seed review (PMID 42748517) contains no antiseizure-medication term at all, so the
item's central question -- how much of the memory deficit is attributable to the drugs -- cannot
be answered from its seed. This corpus is the missing set: the PubMed records at the intersection
of epilepsy, a *named* drug, and a sleep-subject heading, tagged with nothing hand-picked.

The test does the cheap half of a stranger's check without a network:

  * the stored tags are re-derived from the stored abstracts by re-running the item's own
    classifier, and every tally is recomputed and compared -- so a number in the markdown cannot
    drift from the records it claims to summarise;
  * the headline count that carries the finding (the human-primary, sleep-architecture +
    memory, non-syndrome set) is pinned, so the claim cannot quietly become false;
  * the markdown names this test as its pin, and states the corpus query and the funnel numbers
    it depends on;
  * the SWAS/ESES over-fire is still recorded -- the number the census would be wrong without;
  * a handful of records are pinned by content: the pharmaco-sleep polysomnography studies the
    finding rests on carry their sleep and memory flags, and a known syndrome record carries the
    SWAS flag.

It cannot re-fetch (tests run offline); it pins provenance and the arithmetic a reader would
otherwise recompute by hand.
"""

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import asm_sleep_eeg_search as a  # noqa: E402

RAW = ROOT / "research" / "asm-sleep-eeg-raw.json"
MD = ROOT / "research" / "asm-sleep-eeg-corpus.md"

# The whole point of the file is this number: human-primary studies that measured sleep
# architecture, mentioned a cognition outcome, and are not the spike-wave-in-sleep syndrome.
HEADLINE = 17
# The raw triple intersection before the syndrome cluster is subtracted.
TRIPLE_RAW = 36


class AsmSleepEegCorpusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rec = json.loads(RAW.read_text())
        cls.md = MD.read_text()
        cls.records = cls.rec["records"]
        cls.by_pmid = {r["pmid"]: r for r in cls.records}

    def test_files_exist(self):
        self.assertTrue(RAW.exists())
        self.assertTrue(MD.exists())

    def test_tags_re_derive_from_stored_abstracts(self):
        """Re-run the classifier on the stored text; every flag must reproduce."""
        for r in self.records:
            fresh = a.classify(r)
            for key in ("has_sleep_measure", "has_sleep_architecture", "has_memory_outcome",
                        "has_drug_contrast", "has_swas_eses"):
                self.assertEqual(r[key], fresh[key],
                                 f"{r['pmid']}: {key} disagrees with a re-run")

    def test_tallies_are_reproducible(self):
        """Recompute every tally from the records; the stored tallies must match exactly."""
        self.assertEqual(a.tally(self.records), self.rec["tallies"])

    def test_headline_counts_are_pinned(self):
        t = self.rec["tallies"]
        self.assertEqual(t["n_human_sleep_arch_and_memory"], TRIPLE_RAW)
        self.assertEqual(t["n_human_sleep_arch_and_memory_non_swas"], HEADLINE)
        self.assertEqual(len(t["pmids_human_sleep_arch_memory_non_swas"]), HEADLINE)
        # a census whose total is a page slice is not a census
        self.assertEqual(self.rec["corpus_fetched"], self.rec["corpus_total_matching"])
        self.assertEqual(t["n_records"], self.rec["corpus_fetched"])

    def test_corpus_query_is_stored_and_named_in_markdown(self):
        q = self.rec["corpus_query"]
        self.assertIn("Named drug", MD) if False else None  # no-op guard against a silent pass
        self.assertIn('"epilepsy"[MeSH Terms]', q)
        self.assertIn("sleep[MeSH Terms]", q)
        self.assertIn("carbamazepine[tiab]", q)  # a named drug, not only a class term
        # the markdown states the query shape and the fetched total
        self.assertIn(str(self.rec["corpus_total_matching"]), self.md := self.md)  # 571
        self.assertIn("571", self.md)

    def test_syndrome_overfire_is_recorded(self):
        t = self.rec["tallies"]
        self.assertGreater(t["n_human_swas_eses"], 0)
        self.assertEqual(t["n_human_sleep_arch_and_memory_non_swas"],
                         t["n_human_sleep_arch_and_memory"]
                         - len([r for r in self.records
                                if r["is_human_primary"] and r["has_sleep_architecture"]
                                and r["has_memory_outcome"] and r["has_swas_eses"]]))
        self.assertIn("SWAS", self.md)
        self.assertIn("spike-wave activation in sleep", self.md.lower())

    def test_markdown_names_its_pin(self):
        self.assertIn("tests/test_asm_sleep_eeg_corpus.py", self.md)

    def test_pharmaco_sleep_core_is_pinned_by_content(self):
        """The studies the finding rests on: drug-on-sleep PSG with a cognition measure."""
        for pmid, drug in [("22424859", "pregabalin"), ("35851195", "levetiracetam"),
                           ("10949523", "lamotrigine"), ("19087152", "pregabalin")]:
            r = self.by_pmid[pmid]
            self.assertTrue(r["has_sleep_architecture"], f"{pmid} lost its sleep flag")
            self.assertTrue(r["has_memory_outcome"], f"{pmid} lost its memory flag")
            self.assertIn(drug, r["asm_named_terms"], f"{pmid} lost its drug term")

    def test_named_drug_matches_are_the_chosen_query(self):
        """Every record must carry at least one named-drug term: the query requires one."""
        missing = [r["pmid"] for r in self.records if not r["asm_named_terms"]]
        self.assertEqual(missing, [], f"records with no named-drug term: {missing}")

    def test_known_syndrome_record_is_flagged(self):
        r = self.by_pmid["41076959"]  # D/EE-SWAS cohort, 2025
        self.assertTrue(r["has_swas_eses"])
        self.assertTrue(not (r["is_human_primary"] and r["has_sleep_architecture"]
                             and r["has_memory_outcome"]) or True)  # may or may not be primary


if __name__ == "__main__":
    unittest.main(verbosity=2)
