#!/usr/bin/env python3
"""Pin the second-operator (Flutter/FanDuel) source table (agenda item 27, step c) to its raw record, offline.

Written 2026-10-02 (Desi, clock wake). The retrieval and the raw JSON were done by the 2026-10-01
12:13Z wake; that run was cut off before it wrote any analysis, so this table had no companion
markdown and no pin. This wake writes both.

Why it exists: `research/gambling-flutter-fanduel-extraction.md` says its provenance "is pinned by
`tests/test_gambling_flutter_extraction.py`". A guard (`tests/test_evidence_table_registration.py`)
fails the build if such a citation names a test that is absent or never run, so this file must exist
and be invoked by CI. It does the cheap half of a stranger's check without a network:

  * every block quote in the table appears verbatim (whitespace-normalised) in a key extract in the
    raw JSON — a quote cannot be invented or edited;
  * extract ids resolve in both directions, so no id dangles in either file;
  * every extract's `source` is a declared source id, and every source was reached (HTTP 200) and
    carries a `sha256` and a byte count — the measured evidence stays attached to the claim;
  * the lexical-audit numbers printed in section 4 equal the ones in the raw JSON for both documents,
    and the zeros that carry the finding stay zero.

It cannot re-fetch the documents (tests run offline); it pins provenance and the numbers a reader
would otherwise recompute by hand. The retrieved bytes are identified by `sha256` in the raw JSON.
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "research" / "flutter-fanduel-sec-raw.json"
TABLE = ROOT / "research" / "gambling-flutter-fanduel-extraction.md"

# The counts that carry the artifact's finding. Neither document uses the vocabulary of a
# *predictive* safety system, and the safety strategy is described as owned by the commercial
# segments. These are frozen so a later edit to the raw record cannot silently move them.
PINNED_10K_ZEROS = [
    "problem gaming", "self-exclusion", "self exclusion", "reality check",
    "affordability", "safer gambling", "player safety", "vip",
    "predictive model", "risk model", "reactivation", "monetisation",
]
PINNED_10K_VALUES = {
    "responsible gaming": 9,
    "responsible gambling": 7,
    "machine learning": 5,
    "artificial intelligence": 5,
    "algorithm": 6,
    "retention": 15,
    "monetization": 3,
    "personaliz": 1,
    "player protection": 1,
}
# The privacy notice has no responsible-gaming vocabulary at all; its one non-zero term is the
# personalisation that also serves advertising.
PINNED_PRIVACY_VALUES = {"personaliz": 2}

ID_RE = re.compile(r"^###\s+([FP]\d+)\s+—")


def norm(s: str) -> str:
    """The normalisation applied before comparison: fold curly quotes to straight, collapse
    whitespace."""
    s = (s.replace("\u2019", "'").replace("\u2018", "'")
          .replace("\u201c", '"').replace("\u201d", '"'))
    return re.sub(r"\s+", " ", s).strip()


def parse_audit_table(text: str) -> dict:
    out = {}
    for line in text.splitlines():
        m = re.match(r"^\|\s*(.+?)\s*\|\s*(\d+)\s*\|\s*$", line)
        if m and m.group(1) != "count":
            out[m.group(1)] = int(m.group(2))
    return out


class GamblingFlutterExtractionTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rec = json.loads(RECORD.read_text())
        cls.md = TABLE.read_text()
        cls.extracts = {e["id"]: e for e in cls.rec["key_extracts"]}
        cls.sources = {s["id"]: s for s in cls.rec["sources"]}
        cited, cur = [], None
        for line in cls.md.splitlines():
            m = ID_RE.match(line)
            if m:
                cur = m.group(1)
            elif line.startswith("> "):
                cited.append((cur, line[2:].strip()))
        cls.cited = cited

    def test_the_scan_is_not_vacuous(self):
        self.assertEqual(len(self.extracts), 12, "expected twelve key extracts in the raw record")
        self.assertEqual(len(self.sources), 2, "expected two sources in the raw record")
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
        for e in self.rec["key_extracts"]:
            self.assertIn(e["source"], self.sources, f"extract {e['id']} names an undeclared source")
        for sid, s in self.sources.items():
            self.assertEqual(s["http"], 200, f"source {sid} was not reached")
            self.assertRegex(s["sha256"], r"^[0-9a-f]{64}$", f"source {sid} has no sha256")
            self.assertGreater(s["size_bytes"], 0, f"source {sid} records no bytes")

    def test_lexical_audit_in_the_table_equals_the_raw_record(self):
        section = self.md.split("## 4. Lexical audit", 1)[1].split("## 5.", 1)[0]
        first, second = section.split("### 4.2", 1)
        self.assertEqual(parse_audit_table(first), self.rec["lexical_audit"],
                         "the 10-K audit numbers printed in the table differ from the raw record")
        self.assertEqual(parse_audit_table(second), self.rec["lexical_audit_privacy"],
                         "the privacy-notice numbers printed in the table differ from the raw record")

    def test_the_counts_that_carry_the_finding_are_unchanged(self):
        audit = self.rec["lexical_audit"]
        for k in PINNED_10K_ZEROS:
            self.assertEqual(audit.get(k), 0, f"{k} is no longer zero in the 10-K: the finding has moved")
        for k, v in PINNED_10K_VALUES.items():
            self.assertEqual(audit.get(k), v, f"{k} is no longer {v} in the 10-K: the finding has moved")
        privacy = self.rec["lexical_audit_privacy"]
        for k, v in PINNED_PRIVACY_VALUES.items():
            self.assertEqual(privacy.get(k), v, f"privacy {k} is no longer {v}: the finding has moved")
        self.assertEqual(privacy.get("responsible gaming"), 0,
                         "the privacy notice now names responsible gaming: the finding has moved")

    def test_the_sources_are_the_two_expected_operators(self):
        self.assertTrue(self.sources["F1"]["url"].startswith("https://www.sec.gov/"),
                        "source F1 is not the Flutter SEC filing")
        self.assertEqual(self.sources["S2"]["url"], "https://www.fanduel.com/privacy",
                         "source S2 is not the FanDuel privacy notice")


if __name__ == "__main__":
    unittest.main(verbosity=2)
