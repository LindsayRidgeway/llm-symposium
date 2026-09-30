#!/usr/bin/env python3
"""Pin the androgen-TUSC2 source table (agenda item 28) to its retrieved sources, offline.

Written 2026-09-30 (Desi, clock wake) with `research/androgen-tusc2-axis.md` and
`research/androgen-tusc2-axis-raw.json`, the first-step source table for agenda item 28.

Both source papers are closed access (Europe PMC records them `isOpenAccess=N`, no PMC deposit;
the ScienceDirect page returns HTTP 403 to this session), so the table is built from the PubMed
abstract records only and says so. This test does the cheap half of a stranger's check without a
network:

  * every quoted extract appears character-for-character in the retrieved text stored in the
    record — so a quote cannot be invented or silently edited;
  * every extract id is referenced by the markdown, and vice versa, so no id dangles;
  * the lexical audit re-derives from the stored text and matches, and the counts that carry the
    finding (the Tusc2 abstract never says "androgen"; the androgen review never says "TUSC2",
    "mitochondri-", "calcium" or "hippocamp") are pinned — the artifact's headline claim cannot
    quietly become false;
  * the measured gap (paywall / no deposit) stays recorded.

It cannot re-fetch the abstracts (tests run offline); it pins provenance and the numbers a reader
would otherwise have to recompute by hand.
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "research" / "androgen-tusc2-axis-raw.json"
TABLE = ROOT / "research" / "androgen-tusc2-axis.md"

IDENTIFIERS = ["42763063", "42763064", "10.1016/j.mad.2026.112253", "10.1016/j.mad.2026.112257"]
# The counts that carry the artifact's finding: neither paper contains the other's subject matter.
PINNED_ZEROS = {
    "tusc2_paper_fn_androgen": 0,
    "tusc2_paper_fn_testosterone": 0,
    "tusc2_paper_fn_DHEA": 0,
    "androgen_review_fn_TUSC2": 0,
    "androgen_review_fn_mitochondri": 0,
    "androgen_review_fn_calcium": 0,
    "androgen_review_fn_hippocamp": 0,
}
# The item's nine columns; every one must be named by the markdown table.
ITEM_COLUMNS = [
    "Species", "Ages", "Sexes", "Tissues",
    "Hormone measured or manipulated", "Cognitive outcomes", "TUSC2 effects",
    "Mitochondrial-calcium findings", "Stated mechanism",
]


def norm(s: str) -> str:
    """Same normalization the generator applied before storing the text."""
    return re.sub(
        r"\s+", " ",
        s.replace("\u2019", "'").replace("\u2018", "'")
         .replace("\u201c", '"').replace("\u201d", '"'),
    ).strip()


def count(text: str, needle: str) -> int:
    return len(re.findall(re.escape(needle), text, flags=re.I))


class AndrogenTusc2SourceTableTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rec = json.loads(RECORD.read_text())
        cls.md = TABLE.read_text()
        cls.sources = {s["id"]: s for s in cls.rec["sources"]}
        cls.extracts = cls.rec["extracts"]

    def test_both_files_exist(self):
        self.assertTrue(RECORD.exists(), "source record missing")
        self.assertTrue(TABLE.exists(), "source table missing")

    def test_citation_matches_between_table_and_record(self):
        blob = json.dumps(self.rec)
        for ident in IDENTIFIERS:
            self.assertIn(ident, blob, f"{ident} not in the source record")
        for pmid in IDENTIFIERS[:2]:
            self.assertIn(pmid, self.md, f"PMID {pmid} not cited in the table")

    def test_every_extract_is_verbatim_in_its_source_text(self):
        for e in self.extracts:
            src = self.sources[e["source"]]
            self.assertIn("text", src, f"source {e['source']} stores no text to check against")
            self.assertIn(
                norm(e["quote"]), norm(src["text"]),
                msg=f"extract {e['id']} is not verbatim in source {e['source']}",
            )

    def _cited_ids(self):
        """Every id inside a bracketed citation group, e.g. [T1] and [A1,A3] -> {T1, A1, A3}."""
        used = set()
        for group in re.findall(r"\[([^\]]*)\]", self.md):
            for tok in group.split(","):
                if re.fullmatch(r"[TA]\d+", tok.strip()):
                    used.add(tok.strip())
        return used

    def test_extract_ids_resolve_both_ways(self):
        ids = {e["id"] for e in self.extracts}
        self.assertEqual(len(ids), len(self.extracts), "duplicate extract id")
        used = self._cited_ids()
        self.assertTrue(used, "the table references no extract ids at all")
        for i in ids - used:
            self.fail(f"extract {i} is never referenced by the table")
        self.assertEqual(used - ids, set(), f"table cites unknown extract ids: {used - ids}")

    def test_lexical_audit_re_derives_and_pinned_zeros_hold(self):
        audit = self.rec["lexical_audit"]
        # Re-derive the two headline counts straight from the stored text, and compare.
        text = norm(self.sources["S1"]["text"])
        # split the two records the same way the generator did
        parts = re.split(r"(?=\b[12]\. Mech Ageing Dev\.)", text)
        tusc2 = next(p for p in parts if re.match(r"1\. Mech Ageing Dev\.", p))
        androgen = next(p for p in parts if re.match(r"2\. Mech Ageing Dev\.", p))
        self.assertEqual(audit["tusc2_paper_fn_androgen"], count(tusc2, "androgen"))
        self.assertEqual(audit["tusc2_paper_fn_testosterone"], count(tusc2, "testosterone"))
        self.assertEqual(
            audit["androgen_review_fn_TUSC2"],
            count(androgen, "TUSC2") + count(androgen, "Tusc2"),
        )
        self.assertEqual(
            audit["androgen_review_fn_mitochondri"], count(androgen, "mitochondri"))
        for key, want in PINNED_ZEROS.items():
            self.assertEqual(audit[key], want, f"lexical audit {key} is no longer {want}")
        # the Tusc2 paper *does* name the other hormone, which is the point of the finding
        self.assertGreaterEqual(audit["tusc2_paper_fn_estrogen"], 1)

    def test_every_item_column_is_named_in_the_table(self):
        for col in ITEM_COLUMNS:
            self.assertIn(col, self.md, f"the table fails to report the item's column: {col!r}")

    def test_measured_gap_is_recorded(self):
        self.assertIn("403", self.md, "the paywall code is not recorded")
        blob = json.dumps(self.rec)
        self.assertIn("403", blob)
        for s in self.rec["sources"]:
            if s["id"].startswith("X"):
                self.assertIn("UNREACHABLE", s["type"].upper())
        # the abstract-only limit must be stated, not hidden
        self.assertIn("Abstract-only", self.md)


if __name__ == "__main__":
    unittest.main(verbosity=2)
