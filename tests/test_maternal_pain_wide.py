#!/usr/bin/env python3
"""Offline integrity checks for the item-24 widened re-run. No network.

The artefact `research/maternal-chronic-pain-substance-use-wide.md` reports two PubMed queries run on
one day, the two result sets they returned (`research/maternal-chronic-pain-substance-use-wide-raw.json`),
and three findings drawn from them: the retention-against-pain cell stays empty, widening the query
displaces the item's two subject-matter records below the reachable window (ranks 103 and 128 of 164),
and one new subject-matter record (33275857) surfaces at rank 17.

The failure this guards against is the one the commons has paid for before: the write-up and the data
behind it drifting apart, so the map quietly stops describing what the search returned. So these tests
pin the joins and the numbers that a reader would otherwise recompute by hand. They never assert a
*fixed* PubMed count against the live service — that would break the moment the literature moves. They
assert that the script, the snapshot and the map agree with each other, and that the specific
displacement/cell claims the map makes are the ones the snapshot supports.
"""
import importlib.util
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "maternal_pain_search_wide.py"
RAW = ROOT / "research" / "maternal-chronic-pain-substance-use-wide-raw.json"
MAP = ROOT / "research" / "maternal-chronic-pain-substance-use-wide.md"

spec = importlib.util.spec_from_file_location("maternal_pain_search_wide", SCRIPT)
mpw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mpw)

# The two records the strict map found as class B, displaced in the widened order.
DISPLACED = {"34403125": "103", "36069812": "128"}
# The one class-B candidate the widened order surfaces.
NEW_B = "33275857"
# The two records the cell probe returns, neither of which is the cell.
CELL_RECORDS = {"31274509", "22786449"}


class QueryShapeTests(unittest.TestCase):
    def test_widened_query_keeps_every_strict_term(self):
        # The whole point is that the widened query is a *superset* of the strict one; if a strict
        # term were dropped, "every strict record still matches" would be false and Finding 2 void.
        for fragment in ("pregnancy[tiab]", '"chronic pain"[tiab]', '"opioid use disorder"[tiab]',
                         '"medication retention"[tiab]', '"integrated care"[tiab]'):
            self.assertIn(fragment, mpw.WIDE_QUERY, f"widened query lost a strict term: {fragment}")

    def test_widened_query_adds_the_missed_phrasing_and_mesh(self):
        for fragment in ("analgesia[tiab]", '"opioid-exposed pregnancy"[tiab]',
                         '"Chronic Pain"[MeSH]', '"Opioid-Related Disorders"[MeSH]',
                         '"Medication Adherence"[MeSH]'):
            self.assertIn(fragment, mpw.WIDE_QUERY, f"widened query is missing: {fragment}")

    def test_cell_probe_is_a_retention_probe(self):
        for fragment in ("retention[tiab]", "adherence[tiab]", '"retention in care"[tiab]',
                         '"Retention in Care"[MeSH]'):
            self.assertIn(fragment, mpw.CELL_QUERY, f"cell probe is missing: {fragment}")
        # The cell probe must carry the other three concepts too, or it is not the cell.
        for fragment in ("postpartum[tiab]", '"chronic pain"[tiab]', '"opioid use disorder"[tiab]'):
            self.assertIn(fragment, mpw.CELL_QUERY, f"cell probe lost a concept: {fragment}")


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(RAW.read_text())

    def test_both_blocks_present_and_queries_are_the_script(self):
        self.assertEqual(self.data["wide"]["query"], mpw.WIDE_QUERY)
        self.assertEqual(self.data["cell"]["query"], mpw.CELL_QUERY)

    def test_returned_counts_match_the_records(self):
        self.assertEqual(self.data["wide"]["returned"], len(self.data["wide"]["records"]))
        self.assertEqual(self.data["cell"]["returned"], len(self.data["cell"]["records"]))
        self.assertEqual(self.data["wide"]["returned"], 50)

    def test_records_have_the_fields_the_table_uses(self):
        for r in self.data["wide"]["records"]:
            for key in ("pmid", "title", "journal", "pubdate", "pubtypes", "abstract"):
                self.assertIn(key, r)


class MapAgreesWithSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.text = MAP.read_text()
        self.data = json.loads(RAW.read_text())

    def test_map_prints_both_queries(self):
        flat = re.sub(r"\s+", " ", self.text)
        self.assertIn(re.sub(r"\s+", " ", mpw.WIDE_QUERY), flat)
        self.assertIn(re.sub(r"\s+", " ", mpw.CELL_QUERY), flat)

    def test_map_states_the_snapshot_totals(self):
        self.assertIn(str(self.data["wide"]["total_matching"]), self.text)
        self.assertIn(str(self.data["cell"]["total_matching"]), self.text)

    def test_every_wide_record_is_in_the_title_table(self):
        for r in self.data["wide"]["records"]:
            self.assertIn(r["pmid"], self.text)
        # PMIDs reach back to 6 digits (e.g. 187095), so the width bound must admit them.
        rows = re.findall(r"^\|\s*\d+\s*\|\s*(\d{6,8})\s*\|", self.text, re.MULTILINE)
        self.assertEqual(len(rows), len(self.data["wide"]["records"]),
                         "the title table and the snapshot disagree on row count")
        self.assertEqual(sorted(rows), sorted(r["pmid"] for r in self.data["wide"]["records"]))

    def test_displaced_records_are_named_with_their_ranks(self):
        # Finding 2 is the load-bearing one. The snapshot's 50-row window cannot itself prove the
        # ranks (they are measured against the full 164), but it *must* show the two records absent
        # from that window, and the map must name each record with its rank.
        index = [r["pmid"] for r in self.data["wide"]["records"]]
        self.assertNotIn("34403125", index)  # displaced out of the top-50 window
        self.assertNotIn("36069812", index)
        for pmid, rank in DISPLACED.items():
            self.assertIn(pmid, self.text, f"displaced record {pmid} is not named in the map")
            self.assertIn(rank, self.text, f"rank {rank} for {pmid} is not stated in the map")

    def test_new_class_b_candidate_is_named(self):
        self.assertIn(NEW_B, self.text)

    def test_cell_records_are_the_ones_named(self):
        cell_snapshot = {r["pmid"] for r in self.data["cell"]["records"]}
        self.assertEqual(cell_snapshot, CELL_RECORDS)
        for pmid in CELL_RECORDS:
            self.assertIn(pmid, self.text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
