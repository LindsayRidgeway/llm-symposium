#!/usr/bin/env python3
"""Pin the colistin correction sheet to its own counts, offline.

Written 2026-11-21 (Desi, clock wake) with `research/mcr-colistin-denominator-correction-sheet.md`,
`research/mcr-colistin-denominator-frames.json` and `scripts/mcr_colistin_denominator_frames.py`:
the one-page sheet that says the review's pooled 7.0% divides a mixed numerator by seven different
denominators.

What it checks, all offline (tests cannot re-fetch Europe PMC, so they pin what is on disk):

  * the seven frames are exactly seven, every row named in a frame exists in the seed table, and the
    rows with a *read* primary are all accounted for — so a frame cannot quietly lose a row;
  * two printed percentages are **recomputed from their own counts** (33/128 and 8/103), plus 1.36
    and 60.7, against the seed's printed cells — the arithmetic the sheet rests on;
  * the recorded JSON is what the script derives today: if either the seed table or a frame changes,
    the stale record fails rather than being read as fact;
  * the recalculated range in the JSON is the range of the recorded pools, the widest per-row spread
    really is row 28 at more than 400x, and the read-twelve / unread twenty-six split is reproduced;
  * the prose carries the numbers it claims (4.24, 7.27, 464x, seven frames) — a sheet that drifts
    from its own record is the failure this file exists to catch.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import mcr_colistin_denominator_frames as frames_mod  # noqa: E402

RECORD = ROOT / "research" / "mcr-colistin-denominator-frames.json"
SHEET = ROOT / "research" / "mcr-colistin-denominator-correction-sheet.md"
SEED = ROOT / "research" / "mcr-colistin-seed.json"


def _seed_rows():
    return {r["sl"]: r for r in json.loads(SEED.read_text())["rows"]}


class TestFramesAreSevenAndComplete(unittest.TestCase):
    def test_there_are_exactly_seven_frames(self):
        d = json.loads(RECORD.read_text())
        self.assertEqual(d["frame_count"], 7)
        self.assertEqual(len(d["frames"]), 7)
        self.assertEqual([f["id"] for f in d["frames"]], list(range(1, 8)))

    def test_every_frame_names_rows_that_exist_in_the_seed_table(self):
        d = json.loads(RECORD.read_text())
        seed = _seed_rows()
        for f in d["frames"]:
            self.assertTrue(f["rows"], f"frame {f['id']} names no rows")
            for label in f["rows"]:
                self.assertIn(label, seed, f"frame {f['id']} names row {label!r}, absent from the seed")

    def test_every_read_row_is_in_at_least_one_frame(self):
        d = json.loads(RECORD.read_text())
        framed = {label for f in d["frames"] for label in f["rows"]}
        for label in frames_mod.ALTERNATIVES:
            self.assertIn(label, framed, f"read row {label!r} sits in no frame")

    def test_the_seven_frames_are_not_silently_the_same_thing(self):
        # A frame set that collapsed to one definition would defeat the whole sheet.
        d = json.loads(RECORD.read_text())
        self.assertEqual(len({f["frame"] for f in d["frames"]}), 7)


class TestPrintedPercentagesRecomputeFromCounts(unittest.TestCase):
    """The item's own closing condition: recompute printed percentages from their own counts."""

    def _frame_entry(self, row, counts_substring):
        d = json.loads(RECORD.read_text())
        for entry in d["per_row_frames"]:
            if entry["row"] != row:
                continue
            for f in entry["frames"]:
                if counts_substring in f["counts"]:
                    return f
        self.fail(f"no frame for row {row!r} counting {counts_substring!r}")

    def test_row18_percentage_recomputes_from_products_and_pcr_positives(self):
        seed = _seed_rows()
        f = self._frame_entry("18", "PCR-positive cultures")
        self.assertEqual((f["numerator"], f["denominator"]), (33, 128))
        self.assertEqual(seed["18"]["mcr_positive"], 33)
        self.assertEqual(seed["18"]["n_isolates"], 128)
        self.assertAlmostEqual(round(100 * 33 / 128, 2), seed["18"]["prevalence_pct_reported"])
        self.assertAlmostEqual(f["pct"], 25.78125)

    def test_row25_percentage_recomputes_from_selected_isolates(self):
        seed = _seed_rows()
        f = self._frame_entry("25", "colistin-selected isolates")
        self.assertEqual((f["numerator"], f["denominator"]), (8, 103))
        self.assertAlmostEqual(round(100 * 8 / 103, 2), seed["25"]["prevalence_pct_reported"])
        self.assertAlmostEqual(f["pct"], 7.766990, places=5)

    def test_row20_and_row17h_also_recompute(self):
        seed = _seed_rows()
        f20 = self._frame_entry("20", "colistin non-wild-type")
        self.assertAlmostEqual(round(100 * 2 / 147, 2), seed["20"]["prevalence_pct_reported"])
        self.assertAlmostEqual(f20["pct"], 1.360544, places=5)
        f17h = self._frame_entry("17 (h)", "any-mcr isolates")
        self.assertAlmostEqual(round(100 * 17 / 28, 1), seed["17 (h)"]["prevalence_pct_reported"])
        self.assertEqual(f17h["denominator"], seed["17 (h)"]["n_isolates"])

    def test_the_frame_alternatives_use_the_studys_own_counts_not_the_reviews(self):
        # Row 19's primary reports 65 + 84 = 149 mcr-1-positive; the review prints 49. Row 20's
        # primary reports three mcr-1 isolates against a printed two. If someone "tidies" either
        # alternative back to the printed cell, the sheet loses the finding.
        f19 = self._frame_entry("19", "mcr-1-positive isolates")
        self.assertEqual(f19["numerator"], 149)
        self.assertEqual(65 + 84, 149)
        f20 = self._frame_entry("20", "the primary's own gene figure")
        self.assertEqual(f20["numerator"], 3)


class TestRecordMatchesItsGenerator(unittest.TestCase):
    def test_record_is_what_the_script_derives_today(self):
        self.assertEqual(json.loads(RECORD.read_text()), json.loads(json.dumps(frames_mod.derive())))

    def test_recalculated_range_is_the_range_of_the_recorded_pools(self):
        d = json.loads(RECORD.read_text())
        p = d["pools"]
        lo, hi = d["recalculated_range_pct"]
        self.assertAlmostEqual(lo, min(p["as_printed"]["pct"], p["read_twelve_as_printed"]["pct"]), places=4)
        self.assertAlmostEqual(hi, p["gene_corrected"]["pct"], places=4)
        self.assertLess(lo, 5.0)          # the read twelve pool below 5
        self.assertGreater(hi, 7.0)       # the corrected whole-table pool above 7
        self.assertLess(hi - lo, 4.0)     # but this is a range, not a free-for-all

    def test_the_reviews_own_pooled_figure_is_reproduced_exactly(self):
        d = json.loads(RECORD.read_text())
        ap = d["pools"]["as_printed"]
        self.assertEqual((ap["numerator"], ap["denominator"]), (2647, 37816))
        self.assertAlmostEqual(ap["pct"], 6.9997, places=4)   # the printed 7.0%

    def test_the_size_split_is_the_finding_and_is_reproduced(self):
        d = json.loads(RECORD.read_text())
        p = d["pools"]
        self.assertEqual(p["read_twelve_as_printed"]["rows"], 12)
        self.assertEqual(p["unread_twenty_six"]["rows"], 26)
        self.assertAlmostEqual(d["size_split"]["read_twelve_share_of_N"], 75.04, places=2)
        # light rows pool ~3.6x the heavy rows
        ratio = p["unread_twenty_six"]["pct"] / p["read_twelve_as_printed"]["pct"]
        self.assertAlmostEqual(ratio, 3.61, places=1)

    def test_widest_spread_is_row28_and_the_spreads_are_ranked(self):
        d = json.loads(RECORD.read_text())
        self.assertEqual(d["widest_spread"]["row"], "28")
        self.assertGreater(d["widest_spread"]["factor"], 400)
        self.assertEqual(d["narrowest_spread"]["row"], "21")
        self.assertAlmostEqual(d["narrowest_spread"]["factor"], 1.4166, places=3)
        self.assertEqual(d["rows_whose_rate_moves_between_frames"], 7)


class TestTheSheetCarriesItsOwnNumbers(unittest.TestCase):
    def setUp(self):
        self.md = SHEET.read_text()
        self.d = json.loads(RECORD.read_text())

    # One keyword per frame, checked against the prose. Not a slice of the frame string: the
    # sheet may phrase a frame with a comma where the record has none, and a test that fails on
    # punctuation teaches the next wake to edit the test rather than the fact.
    FRAME_KEYWORDS = {
        1: "isolates screened for the gene",
        2: "genotyped only if positive",
        3: "hosts",
        4: "samples or products",
        5: "one recovered isolate per positive sample",
        6: "colistin-selected",
        7: "a sum across sampling frames",
    }

    def test_sheet_exists_and_names_the_seven_frames(self):
        self.assertEqual(set(self.FRAME_KEYWORDS), set(range(1, 8)))
        for fid, keyword in self.FRAME_KEYWORDS.items():
            self.assertIn(keyword.lower(), self.md.lower(),
                          f"sheet does not name frame {fid} ({keyword!r})")

    def test_sheet_quotes_the_range_and_the_pool(self):
        self.assertIn("4.24", self.md)
        self.assertIn("7.27", self.md)
        self.assertIn("7.0%", self.md)
        self.assertIn("464", self.md)

    def test_sheet_has_a_quotable_sentence_section(self):
        self.assertIn("## 5. The sentence a reader can quote", self.md)
        self.assertIn("at least seven", self.md)

    def test_sheet_admits_what_it_does_not_say(self):
        self.assertIn("## 6. What this sheet does not say", self.md)
        self.assertIn("Twenty-six rows", self.md)


if __name__ == "__main__":
    unittest.main()
