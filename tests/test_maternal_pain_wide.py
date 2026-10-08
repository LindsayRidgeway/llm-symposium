#!/usr/bin/env python3
"""Offline integrity checks for the item-24 *widened* maternal-pain search. No network.

Written 2026-10-08 (Dmitri, clock wake) with `scripts/maternal_pain_search_wide.py`,
`research/maternal-chronic-pain-substance-use-wide.json`, and the §"The widened search" section of
`research/maternal-chronic-pain-substance-use.md`.

The claim this pins is narrow and load-bearing: that widening the item-24 query (a) reaches records the
strict query cannot, (b) grows class B, and (c) leaves the **retention-against-pain** cell empty. The
failure guarded against is the quiet one this repository has paid for — a write-up that says a number the
machine no longer produces, or names a record that is no longer in the snapshot.

Nothing here re-queries PubMed; tests run offline. It asserts the snapshot, the script, and the map agree
with each other, and it pins the one fact that is the finding: the targeted cell probe returned exactly
two records, both non-matching.
"""
import importlib.util
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "maternal_pain_search_wide.py"
RAW = ROOT / "research" / "maternal-chronic-pain-substance-use-wide.json"
MAP = ROOT / "research" / "maternal-chronic-pain-substance-use.md"

spec = importlib.util.spec_from_file_location("maternal_pain_search_wide", SCRIPT)
mpsw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mpsw)

# Records the widened query surfaced that the strict query never returned, and that the write-up
# classifies as genuine class-B additions. If one vanishes from the snapshot, the claim moved.
NEW_CLASS_B = ["25123962", "42090338", "37037203"]
# The targeted, unfielded probe for the retention-against-pain cell. Both records match the query
# but, on reading, neither measures the cell; that negative is the item's output, so it is pinned.
CELL_PMIDS = {"22786449", "36889439"}


class QueryShapeTests(unittest.TestCase):
    def test_widening_terms_are_present(self):
        # The next action named exactly these additions; if one is dropped, "widened" stops meaning
        # what the map says it means.
        for fragment in ("opioid-exposed pregnancy", "analgesia", "retention",
                         "prenatal opioid exposure", "opioid tapering"):
            self.assertIn(fragment, mpsw.WIDE_QUERY, f"widened query lost: {fragment}")

    def test_mesh_headings_are_added(self):
        for fragment in ("pregnancy[MeSH]", '"chronic pain"[MeSH]',
                         '"opioid-related disorders"[MeSH]'):
            self.assertIn(fragment, mpsw.WIDE_QUERY, f"widened query lost MeSH heading: {fragment}")

    def test_cell_probe_is_unfielded_and_narrow(self):
        # The whole point of the probe is that it is built from the two concepts alone, with no
        # "treatment" arm and no [tiab] fielding, so it reaches what the conjunction cannot.
        self.assertNotIn("[tiab]", mpsw.CELL_QUERY)
        self.assertNotIn("[MeSH]", mpsw.CELL_QUERY)
        for fragment in ("retention", '"chronic pain"', "buprenorphine"):
            self.assertIn(fragment, mpsw.CELL_QUERY)

    def test_strict_query_is_unchanged_from_item_24(self):
        # The strict block exists to show the index was stable between the two runs; it must be the
        # original query verbatim, not a silent edit.
        for fragment in ('pregnancy[tiab]', '"chronic pain"[tiab]',
                         '"opioid use disorder"[tiab]', '"medication retention"[tiab]'):
            self.assertIn(fragment, mpsw.STRICT_QUERY)


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(RAW.read_text())
        self.blocks = self.data["blocks"]

    def test_three_blocks_present(self):
        self.assertEqual(set(self.blocks), {"strict", "wide", "cell"})

    def test_snapshot_queries_are_the_script_queries(self):
        self.assertEqual(self.blocks["strict"]["query"], mpsw.STRICT_QUERY)
        self.assertEqual(self.blocks["wide"]["query"], mpsw.WIDE_QUERY)
        self.assertEqual(self.blocks["cell"]["query"], mpsw.CELL_QUERY)

    def test_returned_counts_match_the_record_lists(self):
        for name, blk in self.blocks.items():
            self.assertEqual(blk["returned"], len(blk["records"]),
                             f"{name} block's returned count disagrees with its records")

    def test_widening_reaches_more_than_strict(self):
        strict = {r["pmid"] for r in self.blocks["strict"]["records"]}
        wide = {r["pmid"] for r in self.blocks["wide"]["records"]}
        self.assertGreater(self.blocks["wide"]["total_matching"],
                           self.blocks["strict"]["total_matching"],
                           "the widened query did not return more than the strict query")
        self.assertGreater(len(wide - strict), 0,
                           "widening surfaced nothing the strict query had not already returned")

    def test_cell_probe_returned_exactly_the_two_known_records(self):
        got = {r["pmid"] for r in self.blocks["cell"]["records"]}
        self.assertEqual(got, CELL_PMIDS,
                         "the targeted cell probe no longer returns the two records the write-up names")

    def test_new_class_b_records_are_in_wide_and_absent_from_strict(self):
        strict = {r["pmid"] for r in self.blocks["strict"]["records"]}
        wide = {r["pmid"] for r in self.blocks["wide"]["records"]}
        for pmid in NEW_CLASS_B:
            self.assertIn(pmid, wide, f"{pmid} left the widened snapshot")
            self.assertNotIn(pmid, strict, f"{pmid} is no longer a *new* widened record")


class MapAgreesWithSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.text = MAP.read_text()
        self.blocks = json.loads(RAW.read_text())["blocks"]

    def test_map_has_the_widened_section(self):
        self.assertIn("The widened search", self.text)

    def test_map_prints_the_three_totals(self):
        for name in ("strict", "wide", "cell"):
            self.assertIn(str(self.blocks[name]["total_matching"]), self.text,
                          f"map omits the {name} block's total")

    def test_map_names_the_new_class_b_records_and_the_cell_pmids(self):
        for pmid in NEW_CLASS_B + sorted(CELL_PMIDS):
            self.assertIn(pmid, self.text, f"map no longer names {pmid}")

    def test_map_states_the_cell_is_empty(self):
        flat = re.sub(r"\s+", " ", self.text).lower()
        self.assertIn("stays empty", flat)
        self.assertIn("2 records", flat)


if __name__ == "__main__":
    unittest.main(verbosity=2)
