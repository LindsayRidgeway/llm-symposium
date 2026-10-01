#!/usr/bin/env python3
"""Pin the state gaming-regulator source table (agenda item 27, step 2) to its raw record, offline.

Written 2026-10-01 (Desi, clock wake), the same wake that wrote the table.

Why it exists: `research/gambling-state-regulator-filings.md` says its provenance "is pinned by
`tests/test_gambling_state_filings.py`". A guard (`tests/test_evidence_table_registration.py`) fails
the build if such a citation names a test that is absent or never run, so this file must exist and be
invoked by CI. It does the cheap half of a stranger's check without a network:

  * every block quote in the table appears verbatim (whitespace-normalised, PDF line-break
    hyphenation rejoined) in an extract in the raw JSON — a quote cannot be invented or edited;
  * extract ids resolve in both directions, so no id dangles in either file;
  * every extract's `source` is a declared source id, and every source carries a `sha256`, a byte
    count and an HTTP status — the measured evidence stays attached to the claim;
  * the lexical-audit numbers printed in the table equal the ones in the raw JSON, and the zeros
    that carry the finding stay zero.

It cannot re-fetch the PDFs (tests run offline); it pins provenance and the numbers a reader would
otherwise recompute by hand. The retrieved bytes are identified by `sha256` in the raw JSON.
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "research" / "gambling-state-regulator-filings-raw.json"
TABLE = ROOT / "research" / "gambling-state-regulator-filings.md"

# The counts that carry the artifact's finding. The redacted licence application the state releases
# contains no responsible-gaming text; the 2023 reports name none of the behavioural variables; the
# 2024-Q2 report names them and calls the intervention behaviour-based. These are frozen so a later
# edit to the raw record cannot silently move them.
PINNED_ZEROS = [
    'redacted-application: "responsible gaming"',
    'Q3-2023: "time on site"',
    'Q4-2023: "time on site"',
    'all four filings: "machine learning"',
    'all four filings: "predictive"',
    'all four filings: "propensity"',
]
PINNED_ONES = [
    'Q2-2024: "time on site"',
    'Q2-2024: "handle increase"',
    'Q2-2024: "low balance"',
]

ID_RE = re.compile(r"^###\s+(R\d+)\s+—")


def norm(s: str) -> str:
    """The normalisation the generator applied before storing text: fold curly quotes to straight,
    rejoin a word hyphenated across a PDF line break, collapse whitespace."""
    s = (s.replace("\u2019", "'").replace("\u2018", "'")
          .replace("\u201c", '"').replace("\u201d", '"'))
    s = re.sub(r"-\s+", "-", s)
    return re.sub(r"\s+", " ", s).strip()


class GamblingStateFilingsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rec = json.loads(RECORD.read_text())
        cls.md = TABLE.read_text()
        cls.extracts = {e["id"]: e for e in cls.rec["extracts"]}
        cls.sources = {s["id"]: s for s in cls.rec["sources"]}
        # (id, quote) pairs, in document order, from the "Verbatim evidence" section.
        cited, cur = [], None
        for line in cls.md.splitlines():
            m = ID_RE.match(line)
            if m:
                cur = m.group(1)
            elif line.startswith("> "):
                cited.append((cur, line[2:].strip()))
        cls.cited = cited

    def test_the_scan_is_not_vacuous(self):
        self.assertEqual(len(self.extracts), 8, "expected eight extracts in the raw record")
        self.assertEqual(len(self.sources), 4, "expected four sources in the raw record")
        self.assertEqual(len(self.cited), len(self.extracts),
                         "the number of block quotes in the table does not match the raw record")

    def test_every_quote_is_verbatim_and_ids_resolve_both_ways(self):
        cited_ids = {i for i, _ in self.cited}
        self.assertEqual(cited_ids, set(self.extracts),
                         "the set of extract ids cited by the table differs from the raw record")
        for eid, quote in self.cited:
            self.assertIn(eid, self.extracts, f"quote tagged {eid} has no extract")
            stored = norm(self.extracts[eid]["quote"])
            self.assertEqual(norm(quote), stored,
                             f"quote {eid} in the table is not verbatim from the raw record")

    def test_every_extract_source_is_declared_and_every_source_is_evidenced(self):
        for e in self.rec["extracts"]:
            self.assertIn(e["source"], self.sources, f"extract {e['id']} names an undeclared source")
        for sid, s in self.sources.items():
            self.assertEqual(s["http_status"], 200, f"source {sid} was not reached")
            self.assertRegex(s["sha256_pdf"], r"^[0-9a-f]{64}$", f"source {sid} has no sha256")
            self.assertGreater(s["bytes_pdf"], 0, f"source {sid} records no bytes")
            self.assertGreater(s["pages_pdf"], 0, f"source {sid} records no page count")

    def test_lexical_audit_in_the_table_equals_the_raw_record(self):
        # Parse the audit table in section 4: rows of the form "| key | value |".
        section = self.md.split("## 4. Lexical audit", 1)[1].split("## 5.", 1)[0]
        printed = {}
        for line in section.splitlines():
            m = re.match(r"^\|\s*(.+?)\s*\|\s*(\d+)\s*\|\s*$", line)
            if m and m.group(1) != "count":
                printed[m.group(1)] = int(m.group(2))
        self.assertEqual(printed, self.rec["lexical_audit"],
                         "the audit numbers printed in the table differ from the raw record")

    def test_the_counts_that_carry_the_finding_are_unchanged(self):
        audit = self.rec["lexical_audit"]
        for k in PINNED_ZEROS:
            self.assertEqual(audit.get(k), 0, f"{k} is no longer zero: the finding has moved")
        for k in PINNED_ONES:
            self.assertEqual(audit.get(k), 1, f"{k} is no longer one: the finding has moved")

    def test_the_retrieved_urls_are_the_regulator_host(self):
        for sid, s in self.sources.items():
            self.assertTrue(s["url"].startswith("https://massgaming.com/"),
                            f"source {sid} is not from the Massachusetts Gaming Commission host")


if __name__ == "__main__":
    unittest.main(verbosity=2)
