#!/usr/bin/env python3
"""Pin the fifth-amigo gallery gap to reality (Dmitri, 2026-10-07; updated 2026-10-14).

`scripts/gallery_fifth_amigo_gap.py` reports the arithmetic in
`research/gallery-floor-at-five.md`: the matrix is 4 columns x 7 wings (28 cells, all filled),
the amendment of 2026-10-05 made the commons five, so the same floor is 5 x 7 = 35 and seven
cells -- one per wing -- were the fifth amigo's. Four of them are now filled: on 2026-10-13
(islamic, "Noh-Girih: The Ninefold Rosette"), on 2026-10-14 (pen-and-ink, "Hatching the
Catenoid" -- a work that had already landed on 2026-10-13 but was never registered in its
pavilion or the matrix, so it counted as empty), on 2026-10-14 (watercolor, "Backrun and
the Drying Ring" -- the same defect a third time: it landed on main earlier that day and was
never registered, so the cell read open while the art sat one directory away), and on
2026-10-16 (maori, "Unaunahi: The Unbroken Scale" -- the same defect a FOURTH time: its SVG
and generator landed on main on 2026-10-15 and were never registered, so this run added the
wing entry, the matrix cell, and the test the generator had been citing by name but that was
never written), and on 2026-10-18 (impressionism, "The Fusion Threshold" -- the defect a
FIFTH time: its SVG and generator landed on 2026-10-15 and were never registered).

None remain. The last two closed on 2026-10-21, and not by the old defect: the two cells were
filled by *REQUEST DM-2*, the commission filed on 2026-10-18 because a wing of painted oils is
not served by a vector study -- sumi-e got "The Bleed Front" and russian-realism got "Twelve
Metres of Penumbra", both Mage diffusion, both exhibited in the same pass that landed them.
The withheld vector study in wing 07 (*The Edge of the Sunbreak*) was not deleted and not
forced onto a wall to move a number: it was archived to `studies/dmitri/`, where studies live,
so `scripts/gallery_unwired_works.py` now passes with an empty exemption list. The column is
7 of 7 and gap = 0; this test pins that, so a future wing added without a fifth column fails
here first.
This test is the reason the
script exists: it fails if the gallery is extended without that note being updated, so the
claim cannot quietly go stale in either direction.

The negative cases matter as much as the positive one: a script that cannot see a filled
fifth column is not measuring the gap, it is printing a constant.
"""

import sys
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import gallery_fifth_amigo_gap as gap  # noqa: E402

FILLED_FIFTH_CELLS = 7  # islamic (10-13), pen-and-ink (10-14), watercolor (10-14), maori (10-16),
# impressionism (10-18), sumi-e (10-21), russian-realism (10-21)
REMAINING_GAPS = 7 - FILLED_FIFTH_CELLS


def _row(num: str, cells: list[str]) -> str:
    tds = "".join(f"<td>{c}</td>" for c in cells)
    return f"<tr><td>{num} wing</td>{tds}</tr>"


def _table(rows: list[str]) -> str:
    return "<table>" + "".join(rows) + "</table>"


class GalleryFifthAmigoGapTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index_html = gap.INDEX.read_text(encoding="utf-8", errors="replace")
        cls.result = gap.compute(cls.index_html)

    def test_matrix_is_seven_wings_of_five_columns(self):
        self.assertEqual(self.result["wings"], 7)
        self.assertIn(self.result["columns"], (5, 6))
        self.assertEqual(self.result["filled"], 28 + FILLED_FIFTH_CELLS)

    def test_floor_numbers_are_28_and_35(self):
        self.assertEqual(self.result["floor_at_four"], 28)
        self.assertEqual(self.result["floor_at_five"], 35)

    def test_gap_is_the_fifth_amigos_remaining_cells(self):
        self.assertEqual(self.result["gap"], REMAINING_GAPS)
        self.assertEqual(
            [amigo for _, amigo in self.result["gap_cells"]],
            [gap.FIFTH_AMIGO] * REMAINING_GAPS,
        )
        self.assertEqual(len({wing for wing, _ in self.result["gap_cells"]}), REMAINING_GAPS)
        # The cells filled so far must no longer read as gaps.
        self.assertNotIn("islamic", {wing for wing, _ in self.result["gap_cells"]})
        self.assertNotIn("pen-and-ink", {wing for wing, _ in self.result["gap_cells"]})
        self.assertNotIn("watercolor", {wing for wing, _ in self.result["gap_cells"]})
        self.assertNotIn("maori", {wing for wing, _ in self.result["gap_cells"]})
        self.assertNotIn("impressionism", {wing for wing, _ in self.result["gap_cells"]})
        self.assertNotIn("sumi-e", {wing for wing, _ in self.result["gap_cells"]})
        self.assertNotIn("russian-realism", {wing for wing, _ in self.result["gap_cells"]})

    def test_fifth_amigo_is_named_in_the_gallery_page(self):
        self.assertTrue(self.result["fifth_named_in_page"])

    def test_a_filled_fifth_column_closes_the_gap(self):
        # Same seven wings, but now five amigo columns, the fifth filled in every row.
        rows = [
            _row(f"{i:02d}", ["\u2713 w1", "\u2713 w2", "\u2713 w3", "\u2713 w4", "\u2713 w5"])
            for i in range(1, 8)
        ]
        r = gap.compute(_table(rows))
        self.assertEqual(r["columns"], 5)
        self.assertEqual(r["filled"], 35)
        self.assertEqual(r["gap"], 0)

    def test_an_empty_fifth_column_is_seven_gaps(self):
        rows = [
            _row(f"{i:02d}", ["\u2713 w1", "\u2713 w2", "\u2713 w3", "\u2713 w4", ""])
            for i in range(1, 8)
        ]
        r = gap.compute(_table(rows))
        self.assertEqual(r["columns"], 5)
        self.assertEqual(r["filled"], 28)
        self.assertEqual(r["gap"], 7)

    def test_unparseable_index_is_an_error_not_a_silent_zero(self):
        with self.assertRaises(ValueError):
            gap.compute("<html>no table here</html>")


class GalleryGapCliTest(unittest.TestCase):
    """Exercise the actual --check process with its own temporary repository tree."""

    def run_check(self, index_html):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / "scripts/gallery_fifth_amigo_gap.py"
            index = root / "docs/gallery/index.html"
            script.parent.mkdir(parents=True)
            index.parent.mkdir(parents=True)
            script.write_bytes((ROOT / "scripts/gallery_fifth_amigo_gap.py").read_bytes())
            index.write_text(index_html, encoding="utf-8")
            before = index.read_bytes()
            proc = subprocess.run([sys.executable, str(script), "--check"],
                                  capture_output=True, text=True)
            self.assertEqual(index.read_bytes(), before, "--check must not rewrite the matrix")
            return proc

    def test_completed_real_gallery_passes_cli(self):
        proc = self.run_check(gap.INDEX.read_text(encoding="utf-8"))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("CHECK PASSED", proc.stdout)

    def test_missing_fifth_cell_fails_cli(self):
        rows = [_row(f"{i:02d}", ["✓ w1", "✓ w2", "✓ w3", "✓ w4",
                                  "" if i == 1 else "✓ w5"])
                for i in range(1, 8)]
        proc = self.run_check(_table(rows))
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("CHECK FAILED", proc.stdout)

    def test_missing_wing_fails_cli_even_with_no_fifth_gap(self):
        rows = [_row(f"{i:02d}", ["✓ w1", "✓ w2", "✓ w3", "✓ w4", "✓ w5"])
                for i in range(1, 7)]
        proc = self.run_check(_table(rows))
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("CHECK FAILED", proc.stdout)

    def test_empty_founding_cell_fails_cli_even_with_no_fifth_gap(self):
        rows = [_row(f"{i:02d}", ["" if i == 1 else "✓ w1", "✓ w2", "✓ w3",
                                  "✓ w4", "✓ w5"])
                for i in range(1, 8)]
        proc = self.run_check(_table(rows))
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("CHECK FAILED", proc.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
