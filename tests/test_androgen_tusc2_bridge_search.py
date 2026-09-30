#!/usr/bin/env python3
"""Pin the androgen-TUSC2 bridge search (agenda item 28, step 2) to its recorded sources, offline.

Written 2026-09-30 (Desi, clock wake) with `research/androgen-tusc2-bridge-search.md` and
`research/androgen-tusc2-bridge-search-raw.json` — the second step of agenda item 28, which asks the
whole indexed literature (not just the two anchor papers) whether anything connects the androgen axis
to TUSC2 / mitochondrial calcium in the brain.

This test does the cheap half of a stranger's check without a network:

  * the intersection the artifact turns on is empty — the strict TUSC2 x androgen counts are 0 on
    both databases — and it is pinned *together with its controls*, so the zero cannot be read as a
    dead query and cannot silently become "some hits" later;
  * the false-positive story stays true: the unrestricted full-text count is > 0 while the strict
    count is 0 (that gap is the finding, so both numbers are pinned);
  * every quoted extract appears character-for-character (whitespace-normalised) in the stored
    source text, so a quote cannot be invented or edited;
  * every extract id is referenced by the markdown, and vice versa;
  * the measured gaps — the GEO name collision (Fus1 vs FUS) and the uncheckable PROSPERO protocol —
    stay recorded rather than quietly dropped.

It cannot re-run the searches (tests run offline); it pins provenance and the arithmetic a reader
would otherwise have to recompute by hand.
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "research" / "androgen-tusc2-bridge-search-raw.json"
TABLE = ROOT / "research" / "androgen-tusc2-bridge-search.md"

# The manuscript's identifiers (the two anchor papers it is a bridge *between*, plus its own model rows).
ANCHOR_IDENTIFIERS = ["42763063", "42763064", "10.1016/j.mad.2026.112253", "10.1016/j.mad.2026.112257"]
# The query ids the artifact's argument cannot do without.
KEY_QUERY_IDS = ["E1", "E2", "E10", "P1", "E6", "E11", "E12", "E13", "E14", "P3", "E9"]
# Counts that carry the finding: an empty strict intersection, with live controls around it.
PINNED_COUNTS = {
    "strict_titleabstract_tusc2_androgen_europepmc": 0,
    "strict_titleabstract_tusc2_androgen_pubmed": 0,
    "control_tusc2_all_europepmc": 518,
    "control_tusc2_estrogen_strict_europepmc": 1,
    "control_tusc2_estrogen_strict_pubmed": 1,
    "control_tusc2_mitochondria_strict_europepmc": 11,
    "ar_mitochondrial_calcium_strict": 3,
    "ar_hippocampus_aging_strict": 10,
    "androgen_mitocalcium_brain_pubmed": 1,
}
# The papers the nearest-hit table is built from, by PMID.
NEAREST_PMIDS = ["23959938", "37991884", "41685091", "31219567", "39092288", "36746942", "40058147"]


def norm(s: str) -> str:
    """Same normalization the generator applied before storing the text."""
    return re.sub(
        r"\s+", " ",
        s.replace("\u2019", "'").replace("\u2018", "'")
         .replace("\u201c", '"').replace("\u201d", '"'),
    ).strip()


class AndrogenTusc2BridgeSearchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rec = json.loads(RECORD.read_text())
        cls.md = TABLE.read_text()
        cls.by_id = {q["id"]: q for q in cls.rec["queries"]}
        cls.extracts = cls.rec["extracts"]
        cls.nearest_text = norm(cls.rec["nearest_source"]["text"])

    def test_both_files_exist(self):
        self.assertTrue(RECORD.exists(), "source record missing")
        self.assertTrue(TABLE.exists(), "bridge-search table missing")

    def test_anchor_identifiers_are_cited(self):
        blob = json.dumps(self.rec)
        for ident in ANCHOR_IDENTIFIERS:
            # the two anchor papers are the thing the bridge is between; they must be reachable from here
            self.assertIn(ident, blob, f"{ident} not in the source record")

    def test_every_key_query_is_recorded_and_named_in_the_table(self):
        for qid in KEY_QUERY_IDS:
            self.assertIn(qid, self.by_id, f"query {qid} is missing from the record")
            self.assertIn(qid, self.md, f"query {qid} is never named in the table")
            q = self.by_id[qid]
            self.assertTrue(q.get("url"), f"{qid} has no re-runnable url")
            self.assertTrue(q.get("sha256_raw"), f"{qid} stores no response hash")
            self.assertIsInstance(q.get("hit_count"), int, f"{qid} has no integer hit_count")

    def test_intersection_is_empty_and_controls_are_live(self):
        derived = self.rec["derived"]
        for key, want in PINNED_COUNTS.items():
            self.assertEqual(derived[key], want, f"derived count {key} is no longer {want}")
        # the finding is the *gap*: full-text co-occurrence > 0, strict co-occurrence == 0
        self.assertGreater(derived["europepmc_fulltext_tusc2_androgen_unrestricted"], 0)
        self.assertEqual(derived["strict_titleabstract_tusc2_androgen_europepmc"], 0)
        self.assertEqual(derived["strict_titleabstract_tusc2_androgen_pubmed"], 0)
        # and the counts pinned in the record agree with the queries they were derived from
        self.assertEqual(derived["strict_titleabstract_tusc2_androgen_europepmc"],
                         self.by_id["E10"]["hit_count"])
        self.assertEqual(derived["strict_titleabstract_tusc2_androgen_pubmed"],
                         self.by_id["P1"]["hit_count"])
        self.assertEqual(derived["control_tusc2_all_europepmc"],
                         self.by_id["E6"]["hit_count"])
        # a live control, not a dead index
        self.assertGreater(derived["control_tusc2_all_europepmc"], 0)

    def test_every_extract_is_verbatim_in_the_stored_text(self):
        for e in self.extracts:
            self.assertTrue(e.get("verbatim_in_stored_text"),
                            f"extract {e['id']} was not verified at generation time")
            self.assertIn(
                norm(e["quote"]), self.nearest_text,
                msg=f"extract {e['id']} is not verbatim in the stored source text",
            )

    def _cited_ids(self):
        """Every id inside a bracketed citation group, e.g. [N1] and [N1,N2,N3] -> {N1, N2, N3}."""
        used = set()
        for group in re.findall(r"\[([^\]]*)\]", self.md):
            for tok in group.split(","):
                if re.fullmatch(r"N\d+", tok.strip()):
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

    def test_nearest_hits_cover_the_stated_pmids(self):
        got = {h["pmid"] for h in self.rec["nearest_hits"]}
        for pmid in NEAREST_PMIDS:
            self.assertIn(pmid, got, f"nearest-hit PMID {pmid} is missing from the record")
            self.assertIn(pmid, self.md, f"nearest-hit PMID {pmid} is not named in the table")

    def test_measured_gaps_stay_recorded(self):
        # GEO name collision (Fus1 the mitochondrial protein vs FUS the RNA-binding protein)
        self.assertIn("GSE36153", self.md, "the GEO name-collision example is not recorded")
        self.assertIn("FUS", self.md)
        geo = self.rec["geo"]
        self.assertGreater(geo.get("hit_count", 0), 0)
        # PROSPERO could not be read, and that is stated rather than hidden
        self.assertIn("UNREACHABLE", json.dumps(self.rec["prospero"]).upper())
        self.assertIn("PROSPERO", self.md)
        # the step-1 paywall block is carried, not silently dropped
        gaps = " ".join(self.rec["measured_gaps"])
        self.assertIn("paywalled", gaps.lower())

    def test_the_two_decisive_readouts_are_named(self):
        # the item's hypothesis needs both objects in one experiment; the table must say so
        self.assertIn("TUSC2", self.md)
        self.assertIn("mitochondrial calcium", self.md.lower())
        # and at least one nearest paper must be a genuinely reachable (open-access) next step
        self.assertIn("PMC3800758", json.dumps(self.rec))


if __name__ == "__main__":
    unittest.main(verbosity=2)
