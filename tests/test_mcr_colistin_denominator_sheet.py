#!/usr/bin/env python3
"""Pin the colistin denominator sheet to its counts, offline.

Written 2026-11-21 (Dmitri, clock wake) with `research/mcr-colistin-denominator-sheet.md` and
`research/mcr-colistin-denominator-frames.json`. The value-queue item asked for one thing this chest
be able to fail on: that the numbers in the sheet are recomputed from counts rather than re-read as
prose. So:

  * two printed percentages are recomputed from their own counts (rows 18 and 21) — the item's own
    example of what a reader would check;
  * all placed rows are recomputed, and exactly one fails its own counts — row 17 (a), the
    documented cell — so a new transcription slip fails here instead of joining the prose;
  * the eight frames' names and their rows are the eight the sheet lists, and the coverage figures
    (31 rows, 34,376 isolates, 90.9%) are the seed's counts, not the sheet's memory;
  * the eight Ewers country rows placed on 2026-11-21 22:50Z are in frame 1 and two of them are zero
    cells, so the row-level range starts at 0.00% and the sheet says so;
  * the range the sheet quotes is the frame range, and the two numbers in the quotable sentence are
    the ones arithmetic produces;
  * the two caveats found on 2026-11-22 02:50Z and landed on 2026-11-23 are pinned: frame 4's 31.69% is
    a pool of two units and lies between its rows' own rates, and the placed pool has two values —
    counts 6.43%, printed percentages 6.23% — whose gap is row 17 (a).

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
    "isolates screened for a phenotype, genotyped only in a subset",
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
            if m["denominator_basis"] == "as printed":
                self.assertEqual((m["N"], m["n"]), (r["n_isolates"], r["mcr_positive"]), row)
            else:
                # the one placeable class of exception, and it keeps the printed cell beside it
                self.assertEqual(m["N_printed"], r["n_isolates"], row)
                self.assertEqual(m["n"], r["mcr_positive"], row)
                self.assertNotEqual(m["N"], r["n_isolates"], row)
            self.assertEqual(m["pct_printed"], r["prevalence_pct_reported"], row)
            self.assertAlmostEqual(m["pct_from_counts"], 100 * m["n"] / m["N"], places=5)
            # agreement is a claim about the TABLE's pair, so a replaced row is checked on its printed N
            N_printed = m["N"] if m["denominator_basis"] == "as printed" else m["N_printed"]
            self.assertEqual(m["agrees_with_own_counts"], agrees(m["pct_printed"], 100 * m["n"] / N_printed), row)

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
             "17 (h)", "17 (i)", "17 (j)", "17 (k)", "19", "7", "12", "28", "21", "22", "18", "5", "20", "25", "1", "23",
             "15", "11", "14", "27", "24", "26"]
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

    def test_row_7_bangladesh_joins_frame_1_and_the_sheet_states_its_weight_caveat(self):
        """1,200 = twenty colonies picked per pooled faecal sample, 60 samples (§5j).

        The row is an isolate screen, so it belongs to frame 1 on what its N counts — but its sampling
        unit is the sample, which is why the sheet carries a third caveat rather than a ninth frame.
        """
        gene = next(f for f in self.record["frames"] if f["frame"] == "isolates screened for the gene")
        self.assertIn("7", gene["rows"])
        self.assertEqual((self.members["7"]["N"], self.members["7"]["n"]), (1200, 305))
        self.assertTrue(self.members["7"]["agrees_with_own_counts"])
        self.assertAlmostEqual(gene["pooled_pct"], 100 * gene["n"] / gene["N"], places=5)
        self.assertEqual(self.record["frame_count"], 8)
        self.assertIn(f"{gene['pooled_pct']:.2f}%", self.sheet)
        self.assertIn("twenty *E. coli* colonies picked per pooled faecal sample", self.sheet)

    def test_row_12_japan_joins_frame_1_as_a_nested_subset(self):
        """684 of 967 swine-pathogenic strains, kept by serogroup; 90 mcr-1, 309 colistin-resistant (§5k).

        The row is an isolate screen (frame 1), but it is 71% of its own collection rather than a
        sample of it, and the same page prints the phenotype — 90 of 309 = 29.1% of the resistance is
        mcr-1. Both facts are pinned here because the sheet leans on both.
        """
        gene = next(f for f in self.record["frames"] if f["frame"] == "isolates screened for the gene")
        self.assertIn("12", gene["rows"])
        self.assertEqual((self.members["12"]["N"], self.members["12"]["n"]), (684, 90))
        self.assertTrue(self.members["12"]["agrees_with_own_counts"])
        self.assertAlmostEqual(self.members["12"]["pct_from_counts"], 100 * 90 / 684, places=4)
        # the nested subset: 684 of the 967 strains the primary analysed
        self.assertAlmostEqual(100 * 684 / 967, 70.73, places=2)
        # and the phenotype the same page prints
        self.assertAlmostEqual(100 * 90 / 309, 29.13, places=2)
        self.assertIn("71% of its own collection", self.sheet)
        self.assertIn("90 of 309 = 29.1%", self.sheet)

    def test_three_abstract_read_rows_and_the_floor_they_moved(self):
        """Rows 15, 11 and 14 read from their primaries' abstracts on 2026-11-24 (§5l).

        The point of pinning them is the number that moved: frame 2 held only Canada, so a single row
        was setting the low end of the quoted range; India joins it and the floor goes 0.04% -> 0.12%.
        """
        by_frame = {f["frame"]: f["rows"] for f in self.record["frames"]}
        self.assertIn("15", by_frame["isolates screened for the gene"])
        self.assertIn("11", by_frame["isolates screened for a phenotype, genotyped only in a subset"])
        self.assertIn("14", by_frame["colistin-resistant isolates, genotyped for the gene"])
        pheno = next(f for f in self.record["frames"]
                     if f["frame"].startswith("isolates screened for a phenotype"))
        self.assertEqual((pheno["N"], pheno["n"], pheno["rows"]), (6107, 12, ["28", "11", "27", "26"]))
        self.assertAlmostEqual(pheno["pooled_pct"], 100 * 12 / 6107, places=5)
        self.assertGreater(pheno["pooled_pct"], 100 * 2 / 5571)  # the singleton it replaced as the floor
        self.assertIn("11", self.record["read_basis_notes"])
        self.assertIn("abstract", self.record["read_basis_notes"]["11"])
        self.assertIn("caveat 4", self.sheet)

    def test_row_26_south_africa_joins_frame_2_and_the_name_was_widened_for_it(self):
        """Only 8 of the row's 50 isolates were PCR-tested, and not because any was positive (§5n).

        The row is a lower bound (frame 2's arithmetic) but the frame's old name — "genotyped only if
        positive" — was Canada's selection rule, not this row's: its eight were chosen for maximum
        colistin MIC on farms with no prior colistin use, and every one of them was susceptible. So the
        placement and the rename have to happen together, and this test fails if either is undone.
        """
        pheno = next(f for f in self.record["frames"]
                     if f["frame"].startswith("isolates screened for a phenotype"))
        self.assertEqual(pheno["frame"], "isolates screened for a phenotype, genotyped only in a subset")
        self.assertIn("26", pheno["rows"])
        m = self.members["26"]
        self.assertEqual((m["N"], m["n"]), (50, 1))
        self.assertEqual(m["denominator_basis"], "as printed")
        self.assertAlmostEqual(m["pct_from_counts"], 2.0, places=6)
        self.assertEqual((pheno["N"], pheno["n"]), (6107, 12))
        self.assertAlmostEqual(pheno["pooled_pct"], 100 * 12 / 6107, places=4)
        # the tested denominator, which is not the row's and not a prevalence either
        self.assertAlmostEqual(100 * 1 / 8, 12.5, places=4)
        self.assertIn("PMC8654743", self.record["read_basis_notes"]["26"])
        self.assertNotIn("26", self.record["unplaced"]["rows"])
        self.assertIn("only in a subset", self.sheet)

    # --- the recalculated range, and the coverage it is a range over ---

    def test_coverage_is_the_seeds_own_counts(self):
        placed = self.record["placed"]
        self.assertEqual(placed["rows"], 31)
        self.assertEqual(placed["N"], 34376)
        # placed N is the placed counts, which for the one replaced row are the primary's, not the seed's
        self.assertEqual(placed["N"], sum(m["N"] for m in self.members.values()))
        self.assertEqual(sum(self.rows[r]["n_isolates"] for r in self.members), 34819)
        self.assertAlmostEqual(placed["share_of_table_N_pct"], 100 * 34376 / 37816, places=3)
        self.assertEqual(self.record["table"]["N"], self.seed["derived"]["sum_isolates"])
        self.assertIn("34,376", self.sheet)
        self.assertIn("90.9%", self.sheet)

    def test_the_range_quoted_is_the_frame_range(self):
        r = self.record["range"]
        rates = [f["pooled_pct"] for f in self.record["frames"]]
        self.assertAlmostEqual(r["low_pct"], min(rates), places=5)
        self.assertAlmostEqual(r["high_pct"], max(rates), places=5)
        self.assertAlmostEqual(r["low_pct"], 100 * 12 / 6107, places=4)     # rows 28 + 11 + 27 + 26, phenotype-first
        self.assertAlmostEqual(r["high_pct"], 100 * 393 / 1240, places=4)   # rows 18 + 5
        self.assertGreater(r["fold_spread"], 160)
        # The sheet's quotable sentence carries the same two endpoints, to its own rounding.
        self.assertIn("0.20%", self.sheet)
        self.assertIn("31.7%", self.sheet)
        self.assertIn("eight different quantities", self.sheet)

    def test_pooling_the_placed_rows_does_not_give_seven_percent(self):
        self.assertAlmostEqual(self.record["placed"]["pooled_pct"], 100 * 2210 / 34376, places=4)
        self.assertLess(self.record["placed"]["pooled_pct"], 6.5)
        # And the France correction is recorded rather than silently folded in.
        self.assertAlmostEqual(self.record["gene_frame_with_france_corrected_pct"],
                               100 * 1588 / 23198, places=4)

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
        """Counts pool 6.43% against printed-percentage pool 6.24%; the gap is row 17 (a)."""
        placed = [m for f in self.record["frames"] for m in f["members"]]
        N = sum(m["N"] for m in placed)
        counts_pool = 100 * sum(m["n"] for m in placed) / N
        # the printed percentage is a percentage of the PRINTED N, so row 27 weighs 676 here, not 233
        printed_pool = 100 * sum(m.get("N_printed", m["N"]) * m["pct_printed"] / 100 for m in placed) / N
        self.assertAlmostEqual(counts_pool, 6.4289, places=3)
        self.assertAlmostEqual(printed_pool, 6.2342, places=3)
        # The whole gap is the one cell whose printed percentage is not its own counts.
        r17a = self.rows["17 (a)"]
        gap = 100 * (r17a["mcr_positive"] - r17a["n_isolates"] * r17a["prevalence_pct_reported"] / 100) / N
        self.assertAlmostEqual(counts_pool - printed_pool, gap, places=2)
        self.assertGreater(gap, 0.19)  # 0.195 now: the pool grew by 688 isolates, the cell did not
        self.assertIn("6.43%", self.sheet)
        self.assertIn("6.23%", self.sheet)

    def test_row_27_is_placed_on_the_primaries_denominator_and_the_printed_cell_is_kept(self):
        """§5g's method decision, made as a rule: 676 is withdrawn, 233 is the primary's own count.

        The row was read in full on 2026-11-23 and could not enter the record until the record had a way
        to say "the printed denominator is a number the study never reports". The assertions here are the
        rule's whole content: one such row, both cells on it, a written reason, and the substitution
        counted at the record's top level so a second one cannot be added quietly.
        """
        pheno = next(f for f in self.record["frames"]
                     if f["frame"].startswith("isolates screened for a phenotype"))
        self.assertIn("27", pheno["rows"])
        m = self.members["27"]
        self.assertEqual((m["N"], m["n"]), (233, 4))
        self.assertEqual(m["N_printed"], 676)
        self.assertEqual(m["denominator_basis"], "replaced by the primary's")
        self.assertAlmostEqual(m["pct_from_counts"], 100 * 4 / 233, places=4)
        self.assertAlmostEqual(m["pct_from_printed_counts"], 100 * 4 / 676, places=4)
        self.assertIn("denominator_replaced_why", m)
        self.assertIn("Table 2", m["denominator_replaced_why"])
        repl = self.record["denominator_replaced"]
        self.assertEqual(repl["rows"], ["27"])
        self.assertEqual(repl["printed_isolates_withdrawn"], 676 - 233)
        # the frame rate it produces, and the quoted floor, both recomputed here
        self.assertAlmostEqual(pheno["pooled_pct"], 100 * 12 / 6107, places=4)
        self.assertAlmostEqual(self.record["range"]["low_pct"], 100 * 12 / 6107, places=4)
        self.assertIn("233", self.sheet)
        self.assertIn("DENOMINATOR_FROM_PRIMARY", self.sheet)

    def test_sheet_states_its_own_limits(self):
        self.assertEqual(self.record["placed"]["unplaced_rows"], len(self.rows) - 31)
        self.assertIn(f"{len(self.rows) - 30} of the 38 rows", self.sheet)
        self.assertIn("Not a population prevalence anywhere", self.sheet)
        self.assertIn("mcr-colistin-denominator-frames.json", self.sheet)
        self.assertIn("mcr-colistin-harmonisation.md", self.sheet)


class TheOpenSetIsData(unittest.TestCase):
    """The rows with no frame are a block in the record, not a subtraction every wake repeats.

    Added 2026-11-24 with the `unplaced` block. The point is narrow and worth a test: the set of open
    rows used to exist only as the difference between thirty-eight seed rows and eight frames' members,
    so each colistin wake re-derived it by hand, and one wake then spent its budget suspecting the
    frames file's ids (`17 (a)`) did not match the seed's — they do. What this class pins is that the
    set is computed from the seed rather than remembered, that it is disjoint from the placed rows,
    that every row in it says why it is still open, and that the generator fails rather than build a
    stale list.
    """

    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(RECORD.read_text())
        cls.seed = json.loads(SEED.read_text())
        cls.rows = {str(r["sl"]): r for r in cls.seed["rows"]}
        cls.unplaced = cls.record["unplaced"]

    def test_the_open_set_is_the_seed_minus_the_placed_rows(self):
        placed = {m["row"] for f in self.record["frames"] for m in f["members"]}
        self.assertEqual(len(placed), 31)
        open_rows = set(self.rows) - placed
        self.assertEqual(set(self.unplaced["rows"]), open_rows)
        self.assertEqual(len(self.unplaced["rows"]), 7)
        self.assertEqual(self.record["placed"]["unplaced_rows"], 7)

    def test_nothing_is_both_placed_and_open_and_nothing_is_lost(self):
        placed = {m["row"] for f in self.record["frames"] for m in f["members"]}
        self.assertFalse(placed & set(self.unplaced["rows"]))
        self.assertEqual(len(placed) + len(self.unplaced["rows"]), len(self.rows))
        # and the open rows' own counts are the seed's, recomputed here
        self.assertEqual(self.unplaced["N"], sum(self.rows[k]["n_isolates"] for k in self.unplaced["rows"]))
        self.assertEqual(self.unplaced["n"], sum(self.rows[k]["mcr_positive"] for k in self.unplaced["rows"]))
        self.assertEqual(self.unplaced["N"], 2997)
        self.assertEqual(self.unplaced["n"], 437)
        self.assertAlmostEqual(
            self.unplaced["share_of_table_N_pct"],
            round(100 * 2997 / self.seed["derived"]["sum_isolates"], 4),
            places=4,
        )

    def test_every_open_row_says_why_it_is_open(self):
        allowed = {"not read", "unreadable from here", "read, cannot be placed"}
        for m in self.unplaced["members"]:
            self.assertIn(m["read_status"], allowed, m["row"])
            self.assertTrue(m["why"].strip(), m["row"])
            self.assertEqual(m["N"], self.rows[m["row"]]["n_isolates"])
        unreadable = [m["row"] for m in self.unplaced["members"] if m["read_status"] == "unreadable from here"]
        self.assertEqual(unreadable, ["2"], "only China 1,611 is refused by its source")
        self.assertEqual(self.unplaced["read_status_counts"], {"not read": 6, "unreadable from here": 1})

    def test_the_read_order_is_the_one_the_working_names(self):
        self.assertEqual(self.unplaced["rows"], ["2", "3", "4", "8", "9", "10", "16"])
        self.assertEqual([m["read_order"] for m in self.unplaced["members"]], list(range(1, 8)))
        harmonisation = (ROOT / "research" / "mcr-colistin-harmonisation.md").read_text()
        self.assertIn("China 1,611 (row 2), then", harmonisation)
        self.assertIn("Nigeria 35 (row 24)", harmonisation)
        sheet = SHEET.read_text()
        self.assertIn("`unplaced`", sheet)

    def test_the_generator_refuses_a_stale_open_list(self):
        """A placement that leaves the list untouched must fail the build, not pass quietly."""
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import mcr_colistin_denominator_frames as mod
        finally:
            sys.path.pop(0)
        saved = list(mod.UNPLACED_READ_ORDER)
        try:
            mod.UNPLACED_READ_ORDER = saved + ["26"]
            with self.assertRaises(SystemExit) as ctx:
                mod.build()
            self.assertIn("UNPLACED_READ_ORDER is out of date", str(ctx.exception))
        finally:
            mod.UNPLACED_READ_ORDER = saved
        self.assertEqual(mod.build()["unplaced"]["rows"], saved)


class ScriptRuns(unittest.TestCase):
    def test_show_reports_the_frames_and_the_range(self):
        out = subprocess.run(
            [sys.executable, str(SCRIPT), "--show"], capture_output=True, text=True, timeout=60
        )
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("frames: 8", out.stdout)
        self.assertIn("placed rows: 31 of 38", out.stdout)
        self.assertIn("17 (a)", out.stdout)


if __name__ == "__main__":
    unittest.main()
