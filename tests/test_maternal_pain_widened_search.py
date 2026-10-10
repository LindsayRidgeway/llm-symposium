#!/usr/bin/env python3
"""Offline integrity checks for the item-24 *widened* maternal-pain search. No network.

The widened run (2026-10-07) is what the item's own next action asked for: loosen the query once and
test whether the retention-against-pain cell fills. Its products are three files that must agree:

  * `scripts/maternal_pain_widened_search.py` — the two queries and the lexical screen;
  * `research/maternal-chronic-pain-widened-raw.json` — the snapshot it wrote;
  * `research/maternal-chronic-pain-substance-use.md` — the section that reports it.

The failure this guards against is the one the commons has paid for: a write-up that quietly stops
describing the data behind it. So these tests pin the joins and the load-bearing finding — not the
prose, and not a fixed PubMed count (which would break the day the literature moves), but that the
query printed in the map is the query the script runs, that the snapshot totals are the ones stated,
and that the record the map says corrects its own gap claim is really in the retention×pain set.
"""
import importlib.util
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/maternal_pain_widened_search.py"
STRICT_SCRIPT = ROOT / "scripts/maternal_pain_search.py"
RAW = ROOT / "research/maternal-chronic-pain-widened-raw.json"
MAP = ROOT / "research/maternal-chronic-pain-substance-use.md"

spec = importlib.util.spec_from_file_location("maternal_pain_widened_search", SCRIPT)
mpw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mpw)

spec2 = importlib.util.spec_from_file_location("maternal_pain_search", STRICT_SCRIPT)
mps = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(mps)


def _flat(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


class QueryShapeTests(unittest.TestCase):
    def test_widened_query_carries_the_two_loosenings_the_item_named(self):
        # The item said: add MeSH terms, and add the phrasing the strict query misses. Both must be
        # present, or the run is not the run the map describes.
        for fragment in ('"opioid-exposed pregnancy"[tiab]', "analgesia[tiab]",
                         '"Chronic Pain"[MeSH Terms]', '"Opioid-Related Disorders"[MeSH Terms]',
                         "retention[tiab]"):
            self.assertIn(fragment, mpw.WIDENED_QUERY, f"loosening lost: {fragment}")

    def test_widened_query_is_strictly_wider(self):
        # Every strict term survives into the widened query; the widening only adds. If a strict term
        # were dropped, "54 -> N" would not be a loosening of the same search.
        self.assertNotEqual(mps.QUERY, mpw.WIDENED_QUERY)
        for fragment in ("pregnancy[tiab]", '"chronic pain"[tiab]', '"substance use disorder"[tiab]',
                         '"medication retention"[tiab]'):
            self.assertIn(fragment, mpw.WIDENED_QUERY)

    def test_strict_query_is_identical_to_the_first_map_script(self):
        # The comparison is only honest if the "before" number is the one the first map printed.
        self.assertEqual(mpw.STRICT_QUERY, mps.QUERY)


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(RAW.read_text())

    def test_snapshot_queries_are_the_script_queries(self):
        self.assertEqual(self.data["strict"]["query"], mpw.STRICT_QUERY)
        self.assertEqual(self.data["widened"]["query"], mpw.WIDENED_QUERY)

    def test_snapshot_totals_and_returned(self):
        self.assertGreater(self.data["strict"]["total_matching"], 0)
        self.assertGreater(self.data["widened"]["total_matching"], 0)
        self.assertEqual(self.data["widened"]["returned"], len(self.data["records"]))
        # The widening must actually be wider, on the day it ran, than the strict query.
        self.assertGreater(self.data["widened"]["total_matching"],
                           self.data["strict"]["total_matching"])

    def test_records_carry_title_and_abstract(self):
        for r in self.data["records"]:
            for key in ("pmid", "title", "abstract", "screen"):
                self.assertIn(key, r)

    def test_screen_counts_agree_with_the_records(self):
        c = self.data["screen_counts"]
        self.assertEqual(c["returned"], len(self.data["records"]))
        self.assertEqual(c["retention_x_pain"], len(self.data["retention_x_pain_pmids"]))
        self.assertEqual(c["retention_x_chronic_pain"],
                         len(self.data["retention_x_chronic_pain_pmids"]))
        for r in self.data["records"]:
            if r["pmid"] in self.data["retention_x_pain_pmids"]:
                self.assertTrue(r["screen"]["retention"] and r["screen"]["pain"])


class MapAgreesWithSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.text = MAP.read_text()
        self.data = json.loads(RAW.read_text())

    def test_map_prints_the_widened_query(self):
        self.assertIn(_flat(mpw.WIDENED_QUERY), _flat(self.text),
                      "the map must print the widened query it says is re-runnable")

    def test_map_states_the_totals(self):
        self.assertIn(str(self.data["widened"]["total_matching"]), self.text)
        self.assertIn(str(self.data["strict"]["total_matching"]), self.text)


class FindingIsPinnedTests(unittest.TestCase):
    """The load-bearing claim: the widened net did not fill the cell, and it corrected the map."""

    def setUp(self):
        self.text = MAP.read_text()
        self.data = json.loads(RAW.read_text())

    def test_correction_record_is_in_the_retention_by_pain_set(self):
        # 37096126 is the record the map says breaks the old claim "no record measures retention
        # against a pain variable". If it were not in the retention×pain set, the correction would
        # be unsupported by the snapshot.
        self.assertIn("37096126", self.data["retention_x_pain_pmids"])

    def test_map_names_the_correction_record_and_the_superseded_claim(self):
        self.assertIn("37096126", self.text)
        self.assertIn("superseded", self.text)
        self.assertIn("chronic-pain → retention", self.text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
