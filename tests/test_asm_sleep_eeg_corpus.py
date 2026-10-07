#!/usr/bin/env python3
"""Offline integrity checks for the item-30 antiseizure-medication x sleep-EEG corpus. No network.

The corpus in `research/antiseizure-sleep-eeg-corpus.md` is a screen of a PubMed snapshot in
`research/antiseizure-sleep-eeg-raw.json`. The failure this guards against is the quiet one the
commons has paid for: the write-up and the data behind it drifting apart, so the table stops
describing what the search actually returned, and a headline number lives on in a file after the
records that produced it are gone.

So these tests pin the joins and the arithmetic, not the prose: the script's query is the query in
the snapshot and in the map; every snapshot PMID appears in the map; and the map's headline
intersection count is *recomputed here from the stored abstracts* and must equal what the map
prints. Nothing asserts a fixed PubMed total (which would break when the literature changes); it
asserts that the files agree with each other and with the tagging rule.
"""
import importlib.util
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "asm_sleep_eeg_search.py"
RAW = ROOT / "research" / "antiseizure-sleep-eeg-raw.json"
MAP = ROOT / "research" / "antiseizure-sleep-eeg-corpus.md"

spec = importlib.util.spec_from_file_location("asm_sleep_eeg_search", SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class QueryShapeTests(unittest.TestCase):
    def test_both_concepts_present(self):
        # The query is the reproducible half; if the drug concept or the sleep concept is dropped,
        # the corpus stops being the intersection item 30 needs.
        for fragment in ("carbamazepine[tiab]", "levetiracetam[tiab]", "ASM[tiab]",
                         "sleep[tiab]", "polysomnograph*[tiab]", "spindle*[tiab]"):
            self.assertIn(fragment, m.QUERY, f"query lost a concept: {fragment}")

    def test_every_term_is_fielded(self):
        # An unfielded term would widen the search to MeSH and passing mentions; the map tells the
        # reader the corpus is a title/abstract intersection.
        self.assertNotIn("All Fields", m.QUERY)


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(RAW.read_text())

    def test_query_in_snapshot_is_the_script_query(self):
        self.assertEqual(self.data["query"], m.QUERY)

    def test_snapshot_has_a_total_and_the_returned_records(self):
        self.assertGreater(self.data["total_matching"], 0)
        self.assertEqual(self.data["returned"], len(self.data["records"]))
        self.assertEqual(self.data["returned"], 78)

    def test_records_carry_the_fields_the_table_uses(self):
        for r in self.data["records"]:
            for key in ("pmid", "title", "journal", "year", "abstract", "pubtypes"):
                self.assertIn(key, r)

    def test_snapshot_pmids_are_unique(self):
        pmids = [r["pmid"] for r in self.data["records"]]
        self.assertEqual(len(pmids), len(set(pmids)))


class MapAgreesWithSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.text = MAP.read_text()
        self.data = json.loads(RAW.read_text())

    def test_map_prints_the_query(self):
        flat = re.sub(r"\s+", " ", self.text)
        self.assertIn(re.sub(r"\s+", " ", m.QUERY), flat)

    def test_map_states_the_snapshot_total(self):
        self.assertIn(str(self.data["total_matching"]), self.text)

    def test_every_snapshot_pmid_is_in_the_map(self):
        for r in self.data["records"]:
            self.assertIn(r["pmid"], self.text,
                          f"record {r['pmid']} is in the snapshot but not in the map")


class HeadlineNumberTests(unittest.TestCase):
    """The map's headline intersection count must be recomputed, not trusted."""

    def setUp(self):
        self.text = MAP.read_text()
        self.data = json.loads(RAW.read_text())
        self.rows = m.build(self.data)

    def _intersection(self):
        def has(r, g):
            return bool(r["flags"][g])
        return sum(has(r, "asm") and has(r, "sleep_eeg") and has(r, "cognition")
                   for r in self.rows)

    def test_intersection_is_recomputable_and_printed(self):
        n = self._intersection()
        self.assertGreater(n, 0)
        self.assertIn(f"**{n} of {len(self.rows)}** returned records", self.text)

    def test_every_cognition_record_also_names_a_drug(self):
        # If a record reached the "cognition" set without a drug term, the corpus would not be the
        # drug x cognition intersection it claims to be.
        for r in self.rows:
            if r["flags"]["cognition"]:
                self.assertTrue(r["flags"]["asm"],
                                f"PMID {r['record']['pmid']} names cognition but no drug")

    def test_flags_carry_the_sentence_that_set_them(self):
        # Token screens are only auditable if each flag carries its evidence sentence.
        for r in self.rows:
            for group in ("asm", "sleep_eeg", "cognition", "design"):
                for f in r["flags"][group]:
                    self.assertTrue(f["sentence"].strip(),
                                    f"PMID {r['record']['pmid']} flag {group}::{f['name']} has no sentence")


if __name__ == "__main__":
    unittest.main(verbosity=2)
