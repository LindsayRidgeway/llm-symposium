#!/usr/bin/env python3
"""Pin the gambling regulator-filings table (agenda item 27, leg 2) to its retrieved sources, offline.

Written 2026-10-01 (Desi, clock wake). The artefact is `research/gambling-regulator-filings.md`; the
record is `research/gambling-regulator-filings-raw.json`. Unlike the item's first source table, this
record stores the **whole normalised text** of both filed documents, so the checks below can recompute
what the table claims rather than merely re-read it.

It does, with no network:

  * every block quote in the table appears verbatim (whitespace/ligature/quote-normalised) in an
    extract in the raw JSON — a quote cannot be invented or silently edited;
  * every extract id is cited by the table and every id the table cites resolves to an extract, in
    both directions, so nothing dangles;
  * every extract's `source` is a declared source id; every reached source carries a `sha256` and a
    byte count; every unreached or thin source carries an HTTP status and a note;
  * the lexical-audit numbers are **recomputed from the stored text** and must equal the recorded
    ones — this is the check that would have caught a hand-typed count;
  * the counts that carry the finding stay zero: the two documents the operator files with the state
    never use the vocabulary of prediction (*algorithm*, *personalization*, *VIP*, *machine learning*,
    *artificial intelligence*, *predictive*, *propensity*, *risk model*).

It cannot re-fetch the documents (tests run offline); the stored text and per-source sha256 are what
let a later reader confirm a quote against the PDF they hold.
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "research" / "gambling-regulator-filings-raw.json"
TABLE = ROOT / "research" / "gambling-regulator-filings.md"

# The zero counts that carry the artefact's finding: the state filings never use the vocabulary of
# prediction that the SEC filing used to describe the same operator's money engine.
PINNED_ZERO_TERMS = [
    "algorithm", "personaliz", "VIP", "machine learning",
    "artificial intelligence", "predictive", "propensity", "risk model",
]
ID_RE = re.compile(r"(?<![A-Za-z0-9])([RH][0-9]+)(?![A-Za-z0-9])")

_LIG = {"\ufb00": "ff", "\ufb01": "fi", "\ufb02": "fl", "\ufb03": "ffi", "\ufb04": "ffl",
        "\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-", "\u00a0": " "}


def norm(s: str) -> str:
    """The normalisation the generator applied before storing text."""
    s = "".join(_LIG.get(ch, ch) for ch in s)
    return re.sub(r"\s+", " ", s).strip()


class GamblingRegulatorFilingsTest(unittest.TestCase):
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
        self.assertGreaterEqual(len(self.extracts), 10, "too few extracts to be the item's table")
        self.assertGreaterEqual(len(self.sources), 4, "too few sources to be the item's table")

    def test_every_blockquote_is_verbatim_in_an_extract(self):
        stored = norm(" ".join(e.get("quote", "") for e in self.extracts))
        quotes = [q for q in re.findall(r"^>\s?(.*)$", self.md, flags=re.M) if q.strip()]
        self.assertGreaterEqual(len(quotes), 10, "the evidence section lost its quotes")
        for q in quotes:
            self.assertIn(norm(q), stored, f"quote not found verbatim in any extract: {q[:70]!r}")

    def test_extract_ids_resolve_both_ways(self):
        ids = {e["id"] for e in self.extracts}
        cited = set(ID_RE.findall(self.md))
        self.assertEqual(ids - cited, set(), "an extract is never cited by the table")
        self.assertEqual(cited - ids, set(), "the table cites an id that is not an extract")

    def test_every_extract_source_is_declared(self):
        for e in self.extracts:
            self.assertIn(e["source"], self.sources, f"extract {e['id']} names an undeclared source")

    def test_reached_sources_are_pinned_unreached_are_recorded(self):
        for sid, s in self.sources.items():
            if s.get("sha256"):
                self.assertRegex(s["sha256"], r"^[0-9a-f]{64}$", f"{sid} sha256 malformed")
                self.assertTrue(s.get("bytes"), f"{sid} reached but has no byte count")
            else:
                self.assertIn("http", s, f"{sid} unreached/thin but carries no HTTP status")
                self.assertTrue(s.get("note"), f"{sid} unreached/thin but carries no note")

    def test_lexical_audit_recomputes_from_stored_text(self):
        full = self.rec["full_text"]
        self.assertTrue(full, "no stored text to recompute the audit from")
        recorded = self.rec["lexical"]
        for sid, text in full.items():
            self.assertIn(sid, recorded, f"{sid} has stored text but no recorded counts")
            for term, n in recorded[sid].items():
                got = len(re.findall(re.escape(term), text, flags=re.I))
                self.assertEqual(got, n, f"{sid}: recorded '{term}'={n} but recomputed {got}")

    def test_the_finding_zeros_stay_zero(self):
        for sid, counts in self.rec["lexical"].items():
            for term in PINNED_ZERO_TERMS:
                self.assertEqual(
                    counts.get(term, 0), 0,
                    f"{sid} now contains '{term}' — the filing's vocabulary changed; revisit the finding")

    def test_the_table_names_this_test_as_its_pin(self):
        self.assertIn("tests/test_gambling_regulator_filings.py", self.md)


if __name__ == "__main__":
    unittest.main(verbosity=2)
