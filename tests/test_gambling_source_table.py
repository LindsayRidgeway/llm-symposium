#!/usr/bin/env python3
"""Pin the gambling-exploitation source table (agenda item 27) to its retrieved sources, offline.

Written 2026-09-30 (Desi, clock wake), the wake after the table landed.

Why this file exists at all: `research/gambling-algorithmic-exploitation.md` ends by saying its
provenance check "is enforced by `tests/test_gambling_source_table.py`". No such test existed, so
the claim was false from the moment it landed — the same shape of defect the artifact-existence
checker was built for (a confident, specific, checkable claim stated without the check being run).
This is that test. A guard (`tests/test_evidence_table_registration.py`) now fails the build when a
research artefact names a pinning test that is absent or unregistered, so the shape cannot recur.

It does the cheap half of a stranger's check without a network:

  * every block quote in the table appears verbatim (whitespace-normalised) in an extract in the raw
    JSON — a quote cannot be invented or silently edited;
  * every extract id resolves to the record and every extract in the record is cited by the table, in
    both directions, so no id dangles in either file;
  * every extract's `source` is a declared source id;
  * each reached source carries a `sha256` and a byte count, and each unreachable source carries an
    HTTP status and a note — the measured gap stays recorded rather than being papered over;
  * the lexical-audit numbers printed in the table equal the ones in the raw JSON, and the counts
    that carry the finding stay zero.

It cannot re-fetch the documents (tests run offline); it pins provenance and the numbers a reader
would otherwise have to recompute by hand.
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "research" / "gambling-algorithmic-exploitation-raw.json"
TABLE = ROOT / "research" / "gambling-algorithmic-exploitation.md"

# The zero counts that carry the artifact's finding: a 10-K that discusses VIP programmes and
# machine learning, and never names self-exclusion, deposit limits, player protection, prediction
# or a risk model.
PINNED_ZEROS = [
    "10-K: self-exclusion",
    "10-K: deposit limit",
    "10-K: player protection",
    "10-K: predictive",
    "10-K: risk model",
]


def norm(s: str) -> str:
    """The normalisation the generator applied before storing text: collapse whitespace, and fold
    curly quotes to straight so the check is about wording, not punctuation encoding."""
    return re.sub(
        r"\s+", " ",
        s.replace("\u2019", "'").replace("\u2018", "'")
         .replace("\u201c", '"').replace("\u201d", '"'),
    ).strip()


class GamblingSourceTableTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rec = json.loads(RECORD.read_text())
        cls.md = TABLE.read_text()
        cls.sources = {s["id"]: s for s in cls.rec["sources"]}
        cls.extracts = cls.rec["extracts"]

    def test_both_files_exist(self):
        self.assertTrue(RECORD.exists(), "source record missing")
        self.assertTrue(TABLE.exists(), "source table missing")

    def test_the_table_is_not_vacuous(self):
        self.assertGreaterEqual(len(self.extracts), 15, "too few extracts to be the item's table")
        self.assertGreaterEqual(len(self.sources), 6, "too few sources to be the item's table")

    def test_every_blockquote_is_verbatim_in_an_extract(self):
        stored = norm(" ".join(
            e.get("quote", "") + " " + e.get("full", "") for e in self.extracts))
        quotes = [q for q in re.findall(r"^>\s?(.*)$", self.md, flags=re.M) if q.strip()]
        self.assertGreaterEqual(len(quotes), 15, "the evidence section lost its quotes")
        for q in quotes:
            self.assertIn(norm(q), stored,
                          msg=f"a block quote is not verbatim in any extract: {q[:90]!r}")

    def _cited_ids(self):
        """Ids the table names in code spans, e.g. `K2`, `P1`, `X3`."""
        return set(re.findall(r"`([A-Z]+\d+)`", self.md))

    def test_extract_ids_resolve_both_ways(self):
        ids = {e["id"] for e in self.extracts}
        self.assertEqual(len(ids), len(self.extracts), "duplicate extract id in the record")
        cited = self._cited_ids()
        source_ids = set(self.sources)
        missing_from_table = ids - cited
        self.assertEqual(
            missing_from_table, set(),
            f"extract(s) collected but never cited by the table: {sorted(missing_from_table)}")
        dangling = cited - ids - source_ids
        self.assertEqual(dangling, set(), f"table cites ids that resolve to nothing: {sorted(dangling)}")

    def test_every_extract_names_a_declared_source(self):
        for e in self.extracts:
            self.assertIn(e["source"], self.sources,
                          msg=f"extract {e['id']} points at undeclared source {e['source']!r}")

    def test_gap_between_reached_and_unreachable_is_recorded(self):
        for s in self.rec["sources"]:
            if s["id"].startswith("X"):
                self.assertIn("UNREACHABLE", s["type"].upper())
                self.assertIn("note", s, f"unreachable source {s['id']} carries no note")
                self.assertIn("http_status", s)
            else:
                self.assertIn("sha256_html", s, f"reached source {s['id']} stores no sha256")
                self.assertGreater(s["bytes_html"], 0, f"reached source {s['id']} stores no bytes")
                self.assertIn(s["id"], self.md, f"reached source {s['id']} is not in the table")
        # each unreachable attempt is named in the table with its code
        for s in self.rec["sources"]:
            if s["id"].startswith("X"):
                self.assertIn(str(s["http_status"]), self.md,
                              f"HTTP {s['http_status']} for {s['id']} is not in the table")

    def test_lexical_audit_matches_the_record_and_pinned_zeros_hold(self):
        audit = self.rec["lexical_audit"]
        for key, value in audit.items():
            m = re.search(r"\|\s*" + re.escape(key) + r"\s*\|\s*(\d+)\s*\|", self.md)
            self.assertIsNotNone(m, f"lexical count {key!r} is not printed in the table")
            self.assertEqual(int(m.group(1)), value,
                             f"table prints {key}={m.group(1)}, record holds {value}")
        for key in PINNED_ZEROS:
            self.assertEqual(audit.get(key), 0, f"lexical audit {key!r} is no longer zero")
        # and the contrast the finding rests on is still present, not zeroed out
        self.assertGreaterEqual(audit["10-K: VIP"], 1)
        self.assertGreaterEqual(audit["10-K: lifetime value"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
