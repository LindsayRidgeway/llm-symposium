#!/usr/bin/env python3
"""Offline integrity checks for the item-24 maternal-pain evidence map. No network.

The map in `research/maternal-chronic-pain-substance-use.md` is a table of 50 PubMed records, and the
records themselves are the snapshot in `research/maternal-chronic-pain-substance-use-raw.json`. The
failure this guards against is the quiet one the commons has paid for before: the write-up and the data
behind it drifting apart, so the table quietly stops describing what the search actually returned.

So these tests pin the joins, not the prose: the script's query is the query printed in the map; every
PMID in the snapshot appears in the table; and the map's stated total is the snapshot's total. Nothing
here asserts a fixed PubMed count, which would break the moment the literature changes — it asserts that
the four files agree with each other.
"""
import importlib.util
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/maternal_pain_search.py"
RAW = ROOT / "research/maternal-chronic-pain-substance-use-raw.json"
MAP = ROOT / "research/maternal-chronic-pain-substance-use.md"

spec = importlib.util.spec_from_file_location("maternal_pain_search", SCRIPT)
mps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mps)


class QueryShapeTests(unittest.TestCase):
    def test_four_concepts_present(self):
        # The query is the reproducible half of the artifact; if a concept is dropped, the map's
        # numbers stop meaning what the map says they mean.
        for fragment in ("pregnancy[tiab]", "postpartum[tiab]", '"chronic pain"[tiab]',
                         '"opioid use disorder"[tiab]', "treatment[tiab]",
                         '"medication retention"[tiab]'):
            self.assertIn(fragment, mps.QUERY, f"query lost a concept: {fragment}")

    def test_every_concept_is_fielded(self):
        # An unfielded term would silently widen the search to MeSH and passing mentions; the map
        # says all four concepts are title/abstract, so the tag must be on each OR-clause group.
        self.assertNotIn("All Fields", mps.QUERY)


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(RAW.read_text())

    def test_query_in_snapshot_is_the_script_query(self):
        self.assertEqual(self.data["query"], mps.QUERY)

    def test_snapshot_has_records_and_a_total(self):
        self.assertGreater(self.data["total_matching"], 0)
        self.assertEqual(self.data["returned"], len(self.data["records"]))
        self.assertEqual(self.data["returned"], 50)

    def test_records_have_the_fields_the_table_uses(self):
        for r in self.data["records"]:
            for key in ("pmid", "title", "journal", "pubdate", "pubtypes"):
                self.assertIn(key, r)


class MapAgreesWithSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.text = MAP.read_text()
        self.data = json.loads(RAW.read_text())

    def test_map_prints_the_same_query(self):
        # The map tells the reader they can re-run this exact string; that must be the real one. The
        # map wraps the query across lines for readability, so compare modulo whitespace.
        flat = re.sub(r"\s+", " ", self.text)
        self.assertIn(re.sub(r"\s+", " ", mps.QUERY), flat)

    def test_map_states_the_snapshot_total(self):
        self.assertIn(str(self.data["total_matching"]), self.text)

    def test_every_snapshot_pmid_is_in_the_table(self):
        for r in self.data["records"]:
            self.assertIn(r["pmid"], self.text,
                          f"record {r['pmid']} is in the snapshot but not in the map")

    def test_table_has_one_row_per_record(self):
        rows = re.findall(r"^\|\s*\d+\s*\|\s*(\d{7,8})\s*\|", self.text, re.MULTILINE)
        self.assertEqual(len(rows), len(self.data["records"]),
                         "the evidence table and the snapshot disagree on row count")
        self.assertEqual(sorted(rows), sorted(r["pmid"] for r in self.data["records"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
