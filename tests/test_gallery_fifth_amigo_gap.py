#!/usr/bin/env python3
"""Pin the fifth-amigo gallery gap to reality (Dmitri, 2026-10-07).

`scripts/gallery_fifth_amigo_gap.py` reports the arithmetic in
`research/gallery-floor-at-five.md`: the matrix is 4 columns x 7 wings (28 cells, all filled),
the amendment of 2026-10-05 made the commons five, so the same floor is 5 x 7 = 35 and seven
cells -- one per wing -- are the fifth amigo's. This test is the reason the script exists: it
fails if the gallery is extended without that note being updated, so the claim cannot quietly
go stale in either direction.

The negative cases matter as much as the positive one: a script that cannot see a filled
fifth column is not measuring the gap, it is printing a constant.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import gallery_fifth_amigo_gap as gap  # noqa: E402


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

    def test_matrix_is_seven_wings_of_four_columns(self):
        self.assertEqual(self.result["wings"], 7)
        self.assertEqual(self.result["columns"], 4)
        self.assertEqual(self.result["filled"], 28)

    def test_floor_numbers_are_28_and_35(self):
        self.assertEqual(self.result["floor_at_four"], 28)
        self.assertEqual(self.result["floor_at_five"], 35)

    def test_gap_is_one_cell_per_wing_all_the_fifth_amigos(self):
        self.assertEqual(self.result["gap"], 7)
        self.assertEqual(
            [amigo for _, amigo in self.result["gap_cells"]],
            [gap.FIFTH_AMIGO] * 7,
        )
        self.assertEqual(len({wing for wing, _ in self.result["gap_cells"]}), 7)

    def test_fifth_amigo_is_not_named_in_the_gallery_page(self):
        self.assertFalse(self.result["fifth_named_in_page"])

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
