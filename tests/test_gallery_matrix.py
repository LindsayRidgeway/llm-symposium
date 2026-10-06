#!/usr/bin/env python3
"""Pin the Gallery 4x7 Amigo Matrix to reality (Dmitri, 2026-10-06).

`scripts/gallery_matrix_verify.py` is the checker; this test is the reason it exists —
registration in `.github/workflows/test-and-report.yml` is where the commons records
what runs on every landing. The negative cases matter more than the positive one: a
checker that cannot fail is decoration, and the failure this guards against is a matrix
cell naming a work that is nowhere in its pavilion.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import gallery_matrix_verify as gmv  # noqa: E402


class GalleryMatrixTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index_html = gmv.INDEX.read_text(encoding="utf-8", errors="replace")
        cls.rows = gmv.parse_matrix(cls.index_html)

    def test_table_shape_is_seven_wings_by_four_amigos(self):
        self.assertEqual(len(self.rows), 7, "the matrix must have seven wing rows")
        for wing, cells in self.rows:
            self.assertEqual(len(cells), 4, f"{wing} row must have four amigo cells")

    def test_all_twenty_eight_cells_are_filled(self):
        empties = [
            f"{wing}/{amigo}"
            for wing, cells in self.rows
            for amigo, cell in zip(gmv.AMIGOS, cells)
            if not gmv.is_filled(cell)
        ]
        self.assertEqual(empties, [], f"cells missing their fill mark: {empties}")

    def test_every_cell_names_a_work_present_in_its_wing(self):
        unresolved = [
            f"{wing}/{amigo}: {cell} (missing {gmv.verify_cell(wing, cell)})"
            for wing, cells in self.rows
            for amigo, cell in zip(gmv.AMIGOS, cells)
            if gmv.verify_cell(wing, cell)
        ]
        self.assertEqual(unresolved, [], f"matrix cells with no work behind them: {unresolved}")

    def test_a_fabricated_cell_is_caught(self):
        # The exact failure that started this line of work: a specific, checkable claim
        # of a work that does not exist. It must not resolve.
        fabricated = "✓ Mangopare Koru Phantom Study"
        self.assertTrue(gmv.is_filled(fabricated))
        self.assertTrue(
            gmv.verify_cell("maori", fabricated),
            "a fabricated work name must fail verification",
        )

    def test_an_empty_cell_is_not_filled(self):
        self.assertFalse(gmv.is_filled(""))
        self.assertFalse(gmv.is_filled("   "))

    def test_checker_reports_pass_on_the_real_gallery(self):
        self.assertEqual(gmv.main(), 0, "the repository's own gallery must verify clean")


if __name__ == "__main__":
    unittest.main(verbosity=2)
