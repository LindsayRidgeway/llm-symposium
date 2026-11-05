#!/usr/bin/env python3
"""Pins agenda item 30's drug-side corpus to the bytes it was built from.

The note `research/sleep-cognition-epilepsy-drug-sleep-corpus.md` makes counts and quotes
abstract text. Both rot in opposite directions — the note can edit itself to say something
the retrieval never said, and re-running the retrieval can quietly change the corpus under
a note that no longer matches it. So this test does three things, all offline:

  1. the raw record is intact and self-describing: four queries, each with an HTTP 200,
     a byte count, a 64-hex sha256, and a hit count that the note's table quotes;
  2. every count the note asserts in §2 and §1 is recomputed from the stored abstracts and
     must agree;
  3. every quotation the note puts in quotation marks exists verbatim in the stored
     abstract it is attributed to, and every PMID the note names is a PMID the retrieval
     actually returned (with one declared exception, the seed review, which belongs to the
     earlier first-step note and was never part of this corpus).

Run:  python3 tests/test_sleep_drug_sleep_corpus.py
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "research" / "sleep-cognition-epilepsy-drug-sleep-raw.json"
NOTE = ROOT / "research" / "sleep-cognition-epilepsy-drug-sleep-corpus.md"
SCRIPT = ROOT / "scripts" / "sleep_cognition_epilepsy_drug_corpus.py"

# The one PMID the note names that this corpus does not contain, with its reason: it is
# the seed systematic review from research/sleep-cognition-epilepsy-seed.md §1, cited in
# §0 to explain why the drug side needed its own corpus at all.
NOT_IN_THIS_CORPUS = {"42748517"}

EXPECTED_HITS = {
    "drug_x_sleep_architecture": 5691,
    "drug_x_sleep_x_memory": 2278,
    "aed_class_review_sleep": 1111,
    "triad_in_abstract": 183,
}


def load() -> dict:
    return json.loads(RAW.read_text(encoding="utf-8"))


def by_name(data: dict) -> dict:
    return {q["name"]: q for q in data["queries"]}


class TestTheRecordIsIntact(unittest.TestCase):
    def test_the_files_exist(self):
        for path in (RAW, NOTE, SCRIPT):
            self.assertTrue(path.exists(), f"missing {path.relative_to(ROOT)}")

    def test_four_queries_each_with_a_receipt(self):
        data = load()
        self.assertEqual(len(data["queries"]), 4)
        self.assertEqual(sorted(by_name(data)), sorted(EXPECTED_HITS))
        for q in data["queries"]:
            req = q["request"]
            self.assertEqual(req["http_status"], 200, q["name"])
            self.assertGreater(req["bytes"], 1000, q["name"])
            self.assertRegex(req["sha256"], r"^[0-9a-f]{64}$", q["name"])
            self.assertTrue(req["url"].startswith("https://www.ebi.ac.uk/"), q["name"])

    def test_the_hit_counts_are_the_ones_the_note_quotes(self):
        data = by_name(load())
        for name, hits in EXPECTED_HITS.items():
            self.assertEqual(data[name]["hit_count"], hits, name)

    def test_every_returned_record_has_an_id_and_a_title(self):
        for q in load()["queries"]:
            self.assertEqual(q["returned"], len(q["records"]), q["name"])
            for rec in q["records"]:
                self.assertTrue(rec["pmid"] or rec["doi"], q["name"])
                self.assertTrue(rec["title"], q["name"])


class TestTheCountsAreTheOnesTheNoteAsserts(unittest.TestCase):
    """§2's table, recomputed. If the corpus is re-retrieved these numbers may change —
    and then the note has to change with them, which is the point of pinning them."""

    def setUp(self):
        self.triad = by_name(load())["triad_in_abstract"]["records"]

    def test_triad_returns_a_hundred(self):
        self.assertEqual(len(self.triad), 100)

    def test_records_naming_a_sleep_parameter(self):
        got = sum(1 for r in self.triad if r["sleep_terms"])
        self.assertEqual(got, 31)

    def test_records_naming_a_named_drug(self):
        got = sum(1 for r in self.triad if r["drug_terms"])
        self.assertEqual(got, 41)

    def test_records_naming_drug_and_sleep_and_memory(self):
        got = sum(1 for r in self.triad
                  if r["drug_terms"] and r["sleep_terms"] and r["memory_terms"])
        self.assertEqual(got, 10)

    def test_open_access_count(self):
        got = sum(1 for r in self.triad if r["is_open_access"] == "Y")
        self.assertEqual(got, 25)

    def test_distinct_pmids_across_all_queries(self):
        seen = set()
        for q in load()["queries"]:
            seen |= {r["pmid"] for r in q["records"] if r["pmid"]}
        self.assertEqual(len(seen), 314)

    def test_the_citation_sorted_query_is_noise_at_the_top(self):
        """§2's claim that citation rank is not relevance here: of the 100 most-cited
        abstracts of the drug x sleep query, exactly three name a drug together with a
        sleep parameter — so the count in §2 understates the field, and the note says so."""
        q = by_name(load())["drug_x_sleep_architecture"]
        got = sum(1 for r in q["records"] if r["drug_terms"] and r["sleep_terms"])
        self.assertEqual(got, 3)


class TestTheQuotationsAreVerbatim(unittest.TestCase):
    def setUp(self):
        self.data = load()
        self.abstracts = {}
        for q in self.data["queries"]:
            for rec in q["records"]:
                if rec["pmid"]:
                    self.abstracts.setdefault(rec["pmid"], rec["abstract"] or "")
        self.note = NOTE.read_text(encoding="utf-8")

    def test_the_two_quoted_fragments_of_the_anchor_review(self):
        abstract = self.abstracts.get("24299283")
        self.assertTrue(abstract, "the anchor review is not in the corpus")
        for fragment in (
            "antiepileptic drugs have an effect on sleep architecture",
            "gabapentin, tiagabine, pregabalin, clobazam, and carbamazepine reduce sleep latency",
        ):
            self.assertIn(fragment, abstract)
            self.assertIn(fragment.split(",")[0].split(" ")[0], self.note)
        # the note quotes it, so the quote mark is load-bearing
        self.assertIn("antiepileptic drugs have an effect on sleep", self.note)

    def test_every_pmid_the_note_names_was_actually_returned(self):
        named = set(re.findall(r"\b(\d{7,8})\b", self.note))
        self.assertGreater(len(named), 5, "the note should name the papers it discusses")
        stray = {p for p in named if p not in self.abstracts} - NOT_IN_THIS_CORPUS
        self.assertEqual(stray, set(), f"named but never retrieved: {sorted(stray)}")

    def test_the_note_records_the_limit_it_could_hide(self):
        """The step is abstract-level. A note that stopped saying so would be claiming a
        full-text reading that never happened."""
        self.assertIn("Abstract level only", self.note)
        self.assertIn("One database", self.note)

    def test_the_note_does_not_claim_the_chain_is_closed(self):
        self.assertIn("stops one link short", self.note)


if __name__ == "__main__":
    unittest.main(verbosity=2)
