#!/usr/bin/env python3
"""Pin the item-30 full-text measurement table to its retrieved sources, offline.

Written 2026-10-07 (Dmitri, clock wake) with `research/sleep-cognition-epilepsy-ied-fulltext.md`
and `research/sleep-cognition-epilepsy-ied-fulltext-raw.json` — agenda item 30, step (2): turn the
seed's abstract-level comparison set into measurements.

The raw record stores, per paper, the HTTP status, byte count and `sha256` of the bytes retrieved
from Europe PMC, plus short verbatim extracts. It does **not** store the full text (licence), so
this test cannot re-fetch or re-hash the papers; what it pins offline is the half a stranger can
still check without a network:

  * every extract the record marks `verbatim` appears character-for-character in the markdown, so
    no quotation in the table can be invented or silently edited;
  * the three reachable papers recorded HTTP 200 with a well-formed `sha256`, and the fourth is
    recorded as *not* reachable, so the correction cannot quietly disappear;
  * the "not open" paper keeps its Europe PMC flags (`isOpenAccess=N`, `inPMC=N`) and the
    publisher's withhold-full-text note, so the correction stays grounded in the record;
  * all four PMIDs are named by the markdown.
"""

import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "research" / "sleep-cognition-epilepsy-ied-fulltext-raw.json"
TABLE = ROOT / "research" / "sleep-cognition-epilepsy-ied-fulltext.md"

REACHABLE_PMIDS = ["41298465", "42021788", "27111281"]
UNREACHABLE_PMID = "42378289"
ALL_PMIDS = REACHABLE_PMIDS + [UNREACHABLE_PMID]
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class Item30FullText(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(RECORD.read_text(encoding="utf-8"))
        cls.md = TABLE.read_text(encoding="utf-8")
        cls.papers = {p["pmid"]: p for p in cls.doc["papers"]}

    def test_record_has_all_four_papers(self):
        self.assertEqual(sorted(self.papers), sorted(ALL_PMIDS))

    def test_reachable_papers_have_http_and_hash(self):
        for pmid in REACHABLE_PMIDS:
            p = self.papers[pmid]
            self.assertEqual(p["http"], 200, pmid)
            self.assertGreater(p["bytes"], 0, pmid)
            self.assertRegex(p["sha256"], SHA256_RE, pmid)

    def test_every_recorded_extract_is_verbatim_in_the_markdown(self):
        for pmid in REACHABLE_PMIDS:
            extracts = self.papers[pmid]["extracts"]
            self.assertTrue(extracts, f"{pmid} has no extracts")
            for e in extracts:
                self.assertTrue(e["verbatim"], f"{pmid} extract {e['n']} not flagged verbatim")
                self.assertIn(e["text"], self.md,
                              f"{pmid} extract {e['n']} missing from the markdown table")

    def test_unreachable_paper_is_recorded_as_not_open(self):
        u = self.papers[UNREACHABLE_PMID]
        self.assertFalse(u["reachable_as_fulltext"])
        self.assertEqual(u["isOpenAccess"], "N")
        self.assertEqual(u["inPMC"], "N")
        self.assertTrue(u["publisher_withholds_fulltext_note_present"])

    def test_markdown_names_all_four_pmids(self):
        for pmid in ALL_PMIDS:
            self.assertIn(pmid, self.md, pmid)

    def test_markdown_carries_the_recorded_hashes(self):
        # A reader can re-fetch and confirm the quotes come from the same bytes.
        for pmid in REACHABLE_PMIDS:
            h = self.papers[pmid]["sha256"]
            self.assertIn(h[:16], self.md, f"sha256 of {pmid} not cited in the markdown")


if __name__ == "__main__":
    unittest.main(verbosity=2)
