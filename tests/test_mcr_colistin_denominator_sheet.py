#!/usr/bin/env python3
"""Pin the colistin denominator sheet to its counts, offline.

Written 2026-11-21 (Dmitri, clock wake) with `research/mcr-colistin-denominator-sheet.md` and
`research/mcr-colistin-denominator-frames.json`. The value-queue item asked for one thing this chest
be able to fail on: that the numbers in the sheet are recomputed from counts rather than re-read as
prose. So:

  * two printed percentages are recomputed from their own counts (rows 18 and 21) — the item's own
    example of what a reader would check;
  * all twenty-three placed rows are recomputed, and exactly one fails its own counts — row 17 (a), the
    documented cell — so a new transcription slip fails here instead of joining the prose;
  * the eight frames' names and their rows are the eight the sheet lists, and the coverage figures
    (23 rows, 31,486 isolates, 83.3%) are the seed's counts, not the sheet's memory;
  * the eight Ewers country rows placed on 2026-11-21 22:50Z are in frame 1 and two of them are zero
    cells, so the row-level range starts at 0.00% and the sheet says so;
  * the range the sheet quotes is the frame range, and the two numbers in the quotable sentence are
    the ones arithmetic produces;
  * the two caveats found on 2026-11-22 02:50Z and landed on 2026-11-23 are pinned: frame 4's 31.69% is
    a pool of two units and lies between its rows' own rates, and the placed pool has two values —
    counts 5.26%, printed percentages 5.04% — whose gap is row 17 (a).

What this does NOT do: re-read a primary study, fetch anything, or claim any row is a population
prevalence. It reads `research/mcr-colistin-seed.json`, the table's own transcription, and the
frame assignments recorded from §5c–§5e.
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHEET = ROOT / "research" / "mcr-colistin-denominator-sheet.md"
RECORD = ROOT / "research" / "mcr-colistin-denominator-frames.json"
SEED = ROOT / "research" / "mcr-colistin-seed.json"
SCRIPT = ROOT / "scripts" / "mcr_colistin_denominator_frames.py"

EIGHT_FRAMES = [
    "isolates screened for the gene",
    "isolates screened for a phenotype, genotyped only if positive",
    "hosts (animals and humans enrolled)",
    "samples or products",
    "one recovered isolate per positive sample",
    "colistin-selected mixed-species isolates",
    "a sum across sampling frames",
    "colistin-resistant isolates, genotyped for the gene",
]


def decimals(printed: float) -> int:
    text = repr(float(printed))
    return len(text.split(".")[1]) if "." in text else 0


def agrees(printed: float, computed: float) -> bool:
    """The table's convention: printed to its own decimals, rounded (see the arithmetic audit)."""
    return abs(computed - printed) <= 0.5 * 10 ** -decimals(printed) + 1e-9


class DenominatorSheet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(RECORD.read_text())
        cls.seed = json.loads(SEED.read_text())
        cls.rows = {str(r["sl"]): r for r in cls.seed["rows"]}
        cls.sheet = SHEET.read_text()
        cls.members = {
            m["row"]: m for f in cls.record["frames"] for m in f["members"]
        }

    # --- the item's own closing condition: two printed percentages from their own counts ---

    def test_two_printed_percentages_recompute_from_their_counts(self):
        """Row 18 (33/128) and row 21 (12/227) — read from the seed, not from the sheet."""
        for row, n, N, printed in (("18", 33, 128, 25.78), ("21", 12, 227, 5.29)):
            r = self.rows[row]
            self.assertEqual((r["mcr_positive"], r["n_isolates"]), (n, N), row)
            self.assertTrue(agrees(printed, 100 * n / N), row)
        self.assertAlmostEqual(100 * 33 / 128, 25.78125, places=5)
        self.assertAlmostEqual(100 * 12 / 227, 5.28634, places=5)

    def test_all_printed_cells_in_the_record_follow_from_the_seed(self):
        """The record may not carry a number the seed does not produce."""
        for row, m in self.members.items():
            r = self.rows[row]
            self.assertEqual((m["N"], m["n"]), (r["n_isolates"], r["mcr_positive"]), row)
            self.assertEqual(m["pct_printed"], r["prevalence_pct_reported"], row)
            self.assertAlmostEqual(m["pct_from_counts"], 100 * m["n"] / m["N"], places=5)
            self.assertEqual(m["agrees_with_own_counts"], agrees(m["pct_printed"], 100 * m["n"] / m["N"]), row)

    def test_exactly_one_placed_row_fails_its_own_counts_and_it_is_17a(self):
        failures = [
            m["row"] for m in self.members.values() if not m["agrees_with_own_counts"]
        ]
        self.assertEqual(failures, ["17 (a)"])
        self.assertEqual(self.record["arithmetic_failures_among_placed_rows"],
                         [["isolates screened for the gene", "17 (a)"]])
        # 709 / 6,158 = 11.51, not the printed 10.42 — the sheet says both.
        self.assertAlmostEqual(100 * 709 / 6158, 11.51348, places=4)
        self.assertIn("11.51", self.sheet)
        self.assertIn("10.42", self.sheet)

    # --- eight frames, and the rows the sheet gives them ---

    def test_eight_frames_in_the_sheets_order(self):
        self.assertEqual(self.record["frame_count"], 8)
        self.assertEqual([f["frame"] for f in self.record["frames"]], EIGHT_FRAMES)
        for name in EIGHT_FRAMES:
            self.assertIn(name, self.sheet, name)

    def test_the_two_zero_cells_are_placed_and_the_row_range_says_zero(self):
        """17 (d) Switzerland 0/129 and 17 (g) Austria 0/73 — the first placed rows with no positives."""
        gene = next(f for f in self.record["frames"] if f["frame"].startswith("isolates screened for the gene"))
        self.assertIn("17 (d)", gene["rows"])
        self.assertIn("17 (g)", gene["rows"])
        for row in ("17 (d)", "17 (g)"):
            self.assertEqual((self.members[row]["N"], self.members[row]["n"]), (129 if row == "17 (d)" else 73, 0))
            self.assertEqual(self.members[row]["pct_from_counts"], 0.0)
            self.assertTrue(self.members[row]["agrees_with_own_counts"], row)
        self.assertEqual(self.record["range"]["row_level_range_pct"][0], 0.0)
        self.assertIn("0.00%", self.sheet)

    def test_every_frame_pools_only_its_own_members(self):
        for f in self.record["frames"]:
            self.assertEqual(f["N"], sum(m["N"] for m in f["members"]), f["frame"])
            self.assertEqual(f["n"], sum(m["n"] for m in f["members"]), f["frame"])
            self.assertAlmostEqual(f["pooled_pct"], 100 * f["n"] / f["N"], places=5)

    def test_row_to_frame_assignment_is_one_frame_per_row(self):
        placed = [m["row"] for f in self.record["frames"] for m in f["members"]]
        self.assertEqual(len(placed), len(set(placed)))
        self.assertEqual(sorted(placed), sorted(
            ["13", "6", "17 (a)", "17 (b)", "17 (c)", "17 (d)", "17 (e)", "17 (f)", "17 (g)",
             "17 (h)", "17 (i)", "17 (j)", "17 (k)", "19", "28", "21", "22", "18", "5", "20", "25", "1", "23"]
        ))
        # The rows the harmonisation file established each frame on.
        by_frame = {f["frame"]: f["rows"] for f in self.record["frames"]}
        self.assertIn("5", by_frame["samples or products"])
        self.assertIn("21", by_frame["hosts (animals and humans enrolled)"])

    def test_row_22_argentina_joins_the_hosts_frame_it_was_read_for(self):
        """140 is pigs swabbed on six farms, not isolates (§5i), so the row lands in frame 3.

        Read on 2026-11-23 19:4xZ and left placeable-not-placed; placed here, in one change, rather
        than founding a ninth frame on a denominator type that already had one.
        """
        hosts = next(f for f in self.record["frames"] if f["frame"] == "hosts (animals and humans enrolled)")
        self.assertEqual(hosts["rows"], ["21", "22"])
        self.assertEqual((self.members["22"]["N"], self.members["22"]["n"]), (140, 23))
        self.assertTrue(self.members["22"]["agrees_with_own_counts"])
        self.assertEqual((hosts["N"], hosts["n"]), (367, 35))
        self.assertAlmostEqual(hosts["pooled_pct"], 100 * 35 / 367, places=5)
        self.assertEqual(self.record["frame_count"], 8)
        self.assertIn("9.54%", self.sheet)
        self.assertIn("Argentina's 140 are pigs swabbed", self.sheet)

    # --- the recalculated range, and the coverage it is a range over ---

    def test_coverage_is_the_seeds_own_counts(self):
        placed = self.record["placed"]
        self.assertEqual(placed["rows"], 23)
        self.assertEqual(placed["N"], 31486)
        self.assertEqual(placed["N"], sum(self.rows[r]["n_isolates"] for r in self.members))
        self.assertAlmostEqual(placed["share_of_table_N_pct"], 100 * 31486 / 37816, places=3)
        self.assertEqual(self.record["table"]["N"], self.seed["derived"]["sum_isolates"])
        self.assertIn("31,486", self.sheet)
        self.assertIn("83.3%", self.sheet)

    def test_the_range_quoted_is_the_frame_range(self):
        r = self.record["range"]
        rates = [f["pooled_pct"] for f in self.record["frames"]]
        self.assertAlmostEqual(r["low_pct"], min(rates), places=5)
        self.assertAlmostEqual(r["high_pct"], max(rates), places=5)
        self.assertAlmostEqual(r["low_pct"], 100 * 2 / 5571, places=4)      # row 28, phenotype-first
        self.assertAlmostEqual(r["high_pct"], 100 * 393 / 1240, places=4)   # rows 18 + 5
        self.assertGreater(r["fold_spread"], 800)
        # The sheet's quotable sentence carries the same two endpoints, to its own rounding.
        self.assertIn("0.04%", self.sheet)
        self.assertIn("31.7%", self.sheet)
        self.assertIn("eight different quantities", self.sheet)

    def test_pooling_the_placed_rows_does_not_give_seven_percent(self):
        self.assertAlmostEqual(self.record["placed"]["pooled_pct"], 100 * 1655 / 31486, places=4)
        self.assertLess(self.record["placed"]["pooled_pct"], 6.0)
        # And the France correction is recorded rather than silently folded in.
        self.assertAlmostEqual(self.record["gene_frame_with_france_corrected_pct"],
                               100 * 1047 / 20919, places=4)

    def test_frame_four_is_mixed_unit_and_the_sheet_says_so(self):
        """33 positive products + 360 positive isolates, over 128 products + 1,112 samples.

        The caveat found on 2026-11-22 02:50Z and unpinned until 2026-11-23: frame 4's 31.69% is a
        pool of two different units, so it lies between its rows' own rates and is neither.
        """
        f4 = next(f for f in self.record["frames"] if f["frame"] == "samples or products")
        self.assertEqual((f4["N"], f4["n"]), (128 + 1112, 33 + 360))
        self.assertAlmostEqual(f4["pooled_pct"], 100 * 393 / 1240, places=4)
        products, isolates = 100 * 33 / 128, 100 * 360 / 1112
        self.assertLess(products, f4["pooled_pct"])
        self.assertGreater(isolates, f4["pooled_pct"])
        self.assertIn("mixed-unit", self.sheet)
        self.assertIn("25.78", self.sheet)
        self.assertIn("32.37", self.sheet)

    def test_the_two_pooling_methods_and_the_gap_that_is_row_17a(self):
        """Counts pool 5.26% against printed-percentage pool 5.04%; the gap is row 17 (a)."""
        placed = [m for f in self.record["frames"] for m in f["members"]]
        N = sum(m["N"] for m in placed)
        counts_pool = 100 * sum(m["n"] for m in placed) / N
        printed_pool = 100 * sum(m["N"] * m["pct_printed"] / 100 for m in placed) / N
        self.assertAlmostEqual(counts_pool, 5.2563, places=3)
        self.assertAlmostEqual(printed_pool, 5.0436, places=3)
        # The whole gap is the one cell whose printed percentage is not its own counts.
        r17a = self.rows["17 (a)"]
        gap = 100 * (r17a["mcr_positive"] - r17a["n_isolates"] * r17a["prevalence_pct_reported"] / 100) / N
        self.assertAlmostEqual(counts_pool - printed_pool, gap, places=2)
        self.assertGreater(gap, 0.2)
        self.assertIn("5.26%", self.sheet)
        self.assertIn("5.04%", self.sheet)

    def test_sheet_states_its_own_limits(self):
        self.assertEqual(self.record["placed"]["unplaced_rows"], len(self.rows) - 23)
        self.assertIn(f"{len(self.rows) - 23} of the 38 rows", self.sheet)
        self.assertIn("Not a population prevalence anywhere", self.sheet)
        self.assertIn("mcr-colistin-denominator-frames.json", self.sheet)
        self.assertIn("mcr-colistin-harmonisation.md", self.sheet)


class ScriptRuns(unittest.TestCase):
    def test_show_reports_the_frames_and_the_range(self):
        out = subprocess.run(
            [sys.executable, str(SCRIPT), "--show"], capture_output=True, text=True, timeout=60
        )
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("frames: 8", out.stdout)
        self.assertIn("placed rows: 23 of 38", out.stdout)
        self.assertIn("17 (a)", out.stdout)


if __name__ == "__main__":
    unittest.main()
