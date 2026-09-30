#!/usr/bin/env python3
"""Pin the sleep-and-epilepsy source table (agenda item 30) to its retrieved sources, offline.

Written 2026-09-30 (Desi, clock wake) with `research/sleep-cognition-epilepsy-seed.md` and
`research/sleep-cognition-epilepsy-seed.json`, the first-step source table for agenda item 30.

The seed systematic review (PMID 42748517, *Epilepsy Behav* 2026;185:111269) is closed access —
Europe PMC records it `isOpenAccess=N`, no PMC deposit, and the publisher page returns HTTP 403 to
this session — so the table is built from the PubMed abstract record plus a small open-access
comparison set, and says so. This test does the cheap half of a stranger's check without a network:

  * every quoted extract appears character-for-character in the retrieved text stored in the
    record — so a quote cannot be invented or silently edited;
  * every extract id is referenced by the markdown, and vice versa, so no id dangles;
  * each source's stored text re-hashes to the `sha256_raw` recorded at fetch time, so the text a
    quote is checked against cannot be swapped out under it;
  * the lexical audit re-derives from the stored text and matches, and the count that carries the
    finding — the seed review never says *antiseizure*, *antiepileptic*, *medication*, *drug* or
    any common drug name, so its stated total is 0 — is pinned, so the headline claim cannot
    quietly become false;
  * the measured gap (paywall / no deposit) stays recorded, and the item's seven columns stay
    named.

It cannot re-fetch the abstracts (tests run offline); it pins provenance and the numbers a reader
would otherwise have to recompute by hand.
"""

import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "research" / "sleep-cognition-epilepsy-seed.json"
TABLE = ROOT / "research" / "sleep-cognition-epilepsy-seed.md"

IDENTIFIERS = ["42748517", "10.1016/j.yebeh.2026.111269"]
# The item's seven columns; every one must be named by the markdown table.
ITEM_COLUMNS = [
    "Epilepsy syndrome", "Antiseizure medications", "Nocturnal epileptiform activity",
    "Objective sleep measures", "Memory task", "Timing of testing", "Reported association",
]
# The finding: the seed review contains no antiseizure-medication vocabulary at all.
ASM_TERMS = [
    "antiseizure", "anti-seizure", "antiepileptic", "anti-epileptic", "medication",
    "medications", "drug", "drugs", "AED", "carbamazepine", "levetiracetam", "valproate",
    "lamotrigine",
]
OTHER_TERMS = [
    "interictal", "epileptic", "discharge", "discharges", "sleep", "cognition", "cognitive",
    "memory", "spindle", "spindles", "slow", "architecture", "syndrome",
]
EXTRACT_REF = re.compile(r"\[((?:[TC]\d+(?:,\s*)?)+)\]")


def norm(s: str) -> str:
    """Same normalization the generator applied before storing the text."""
    return re.sub(r"\s+", " ", s).strip()


def count(text: str, needle: str) -> int:
    return len(re.findall(r"\b" + re.escape(needle) + r"\b", text, flags=re.I))


class SleepCognitionEpilepsySourceTableTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rec = json.loads(RECORD.read_text())
        cls.md = TABLE.read_text()
        cls.sources = {s["id"]: s for s in cls.rec["sources"]}
        cls.extracts = cls.rec["extracts"]
        cls.ids = {e["id"] for e in cls.extracts}
        # every extract id the markdown cites, split out of [T1,C2,...] groups
        cls.md_refs = set()
        for group in EXTRACT_REF.findall(cls.md):
            for tok in group.split(","):
                cls.md_refs.add(tok.strip())

    def test_both_files_exist(self):
        self.assertTrue(RECORD.exists(), "source record missing")
        self.assertTrue(TABLE.exists(), "source table missing")

    def test_citation_matches_between_table_and_record(self):
        blob = json.dumps(self.rec)
        for ident in IDENTIFIERS:
            self.assertIn(ident, blob, f"{ident} missing from the record")
            self.assertIn(ident, self.md, f"{ident} missing from the markdown")

    def test_scan_is_not_vacuous(self):
        self.assertGreaterEqual(len(self.sources), 4, "expected at least four sources")
        self.assertGreaterEqual(len(self.extracts), 20, "expected at least twenty extracts")
        self.assertGreaterEqual(len(self.md_refs), 20, "markdown cites too few extract ids")
        self.assertIn("42748517", self.sources["S1"]["text"], "seed abstract text not stored")

    def test_every_extract_quotes_stored_text_verbatim(self):
        problems = []
        for e in self.extracts:
            src = self.sources.get(e["source"])
            if src is None:
                problems.append(f"{e['id']}: names unknown source {e['source']}")
                continue
            if norm(e["quote"]) not in norm(src["text"]):
                problems.append(
                    f"{e['id']}: quote not found character-for-character in {e['source']}")
        self.assertEqual(problems, [], "\n".join(problems))

    def test_stored_text_rehashes_to_recorded_sha256(self):
        problems = []
        for sid, src in self.sources.items():
            if "sha256_raw" not in src:
                continue
            got = hashlib.sha256(src["text"].encode("utf-8")).hexdigest()
            if got != src["sha256_raw"]:
                problems.append(f"{sid}: stored text hashes {got[:12]}…, record says "
                                f"{src['sha256_raw'][:12]}…")
        self.assertEqual(problems, [], "\n".join(problems))

    def test_extract_ids_and_markdown_references_agree(self):
        self.assertEqual(self.ids - self.md_refs, set(), "extract ids never cited by the markdown")
        self.assertEqual(self.md_refs - self.ids, set(), "markdown cites ids with no extract")

    def test_lexical_audit_rederives_and_pins_the_finding(self):
        seed = norm(self.sources["S1"]["text"])
        audit = self.rec["lexical_audit"]
        recomputed_asm = {t: count(seed, t) for t in ASM_TERMS}
        recomputed_other = {t: count(seed, t) for t in OTHER_TERMS}
        self.assertEqual(audit["seed_asm_terms"], recomputed_asm,
                         "ASM term counts disagree with the stored seed text")
        self.assertEqual(audit["seed_other_terms"], recomputed_other,
                         "other term counts disagree with the stored seed text")
        total = sum(recomputed_asm.values())
        self.assertEqual(total, 0, "the seed review now contains ASM vocabulary — the finding broke")
        self.assertEqual(audit["seed_asm_total"], total)
        self.assertEqual(len(re.findall(r"interictal epileptic discharges", seed, flags=re.I)), 1,
                         "the seed should name the IED phrase exactly once")

    def test_item_columns_and_the_measured_gap_stay_named(self):
        for col in ITEM_COLUMNS:
            self.assertIn(col, self.md, f"item column '{col}' not named by the table")
        self.assertIn("isOpenAccess=N", self.md, "the open-access flag is no longer recorded")
        self.assertIn("403", self.md, "the paywall HTTP status is no longer recorded")


if __name__ == "__main__":
    unittest.main(verbosity=2)
