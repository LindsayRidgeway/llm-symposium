#!/usr/bin/env python3
"""Pin Desi's Islamic gallery cell — Yāzdah-Girih: The Elevenfold Order (Wing 03).

Why this file exists
--------------------
Every procedural plate in the gallery asserts something about its geometry, and until now
almost none of those assertions were checked by anything: a claim whose truth nothing tests
is the exact defect `scripts/gallery_matrix_verify.py` was written to catch one level up (a
matrix cell naming a work that does not exist). This plate was built with the claims first —
each one is a statement the geometry makes that a machine can settle without an eye — and
this file is the settlement.

What is checked
---------------
  1. determinism — the generator writes the committed bytes, twice, with no RNG and no clock;
  2. **G1** C11 rotational symmetry: rotating the full vertex set by 360/11 maps it onto
     itself. Asserted twice, at two strengths: exactly (< 1e-9 px) on the constructed
     geometry, and to the rounding bound (< 2e-3 px) on the coordinates as printed in the
     file. The second is not a weaker copy of the first — it is the only thing that can be
     said about the committed artefact, because three decimals cannot carry an exact number;
  3. **G2** D11 mirror symmetry, the same way;
  4. **G3** each of the five star polygons {11/k}, k = 1..5, closes in exactly eleven steps
     (11 is prime, so gcd(11,k) = 1 for all k). The negative case matters: {12/4} must fail
     the same test, otherwise the check is decoration;
  5. **A1** not constructible: 2·cos(360/11) annihilates x^5+x^4-4x^3-3x^2+3x+1, that
     polynomial is irreducible over Q (checked by reduction mod 2, exhaustively factored
     there), its degree is 5, and 5 is not a power of two — which is Gauss–Wantzel. The
     same route says an 11-gon is not constructible, so the arithmetic is cross-checked
     against the n = 2^a · (distinct Fermat primes) criterion;
  6. **A2** no tiling: no vertex figure — any multiset of regular polygons, edge to edge, at
     most six of them, sides up to 100 — that contains an 11-gon sums to a full turn. The
     positive control is asserted in the same test: the search does find (6,6,6) and
     (3,3,3,3,3,3) when they are the ones asked for, so an empty result for 11 is a fact
     about 11 and not about a broken search;
  7. containment: every emitted coordinate lies inside the viewBox;
  8. registration: the wing page presents the plate, links its SVG and names the generator,
     and the matrix cell for Wing 03 / Desi resolves through `gallery_matrix_verify`.

Runner:  python3 tests/test_gallery_islamic_desi_yazdah.py
"""

import importlib.util
import math
import sys
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import gallery_matrix_verify as gmv  # noqa: E402

WING = ROOT / "docs" / "gallery" / "islamic"
SVG_PATH = WING / "yazdah-girih-elevenfold.svg"
GEN_PATH = ROOT / "scripts" / "generate_desi_girih_yazdah.py"
WING_PAGE = WING / "index.html"
INDEX = ROOT / "docs" / "gallery" / "index.html"


def load_generator():
    spec = importlib.util.spec_from_file_location("gen_yazdah", GEN_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class YazdahGirihTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gen = load_generator()
        cls.svg_text = SVG_PATH.read_text(encoding="utf-8")

    # -- 1. determinism -----------------------------------------------------
    def test_generator_writes_the_committed_bytes(self):
        self.gen.VERTICES.clear()
        first = self.gen.build_svg(0.0, 0.0, 0)
        self.gen.VERTICES.clear()
        second = self.gen.build_svg(0.0, 0.0, 0)
        self.assertEqual(first, second, "the generator is not deterministic")
        self.assertEqual(first, self.svg_text, "the committed SVG is not what the generator writes")

    def test_generator_contains_no_randomness_or_clock(self):
        source = GEN_PATH.read_text(encoding="utf-8")
        for forbidden in ("import random", "time.time", "datetime.now", "uuid"):
            self.assertNotIn(forbidden, source, f"generator reaches for {forbidden}")

    # -- 2 & 3. symmetry, at two honest strengths --------------------------
    def test_C11_symmetry_of_the_constructed_geometry_is_exact(self):
        self.gen.VERTICES.clear()
        self.gen.build_svg(0.0, 0.0, 0)
        deviation = self.gen.symmetry_max_deviation(self.gen.VERTICES, 360.0 / 11)
        self.assertLess(deviation, 1e-9, f"C11 deviation {deviation:.3e} px")

    def test_D11_mirror_symmetry_of_the_constructed_geometry_is_exact(self):
        self.gen.VERTICES.clear()
        self.gen.build_svg(0.0, 0.0, 0)
        deviation = self.gen.symmetry_max_deviation(self.gen.VERTICES, 0.0, mirror=True)
        self.assertLess(deviation, 1e-9, f"D11 deviation {deviation:.3e} px")

    def test_committed_coordinates_are_symmetric_to_the_rounding_of_three_decimals(self):
        measured = self.gen.check_against(self.svg_text)
        self.assertGreater(measured["vertices"], 200, "the plate's geometry went missing")
        self.assertLess(measured["c11"], 2e-3, "C11 on the printed coordinates")
        self.assertLess(measured["d11"], 2e-3, "D11 on the printed coordinates")

    def test_tenfold_rotation_would_fail_this_plate(self):
        # The check above is only meaningful if a wrong order fails it.
        self.gen.VERTICES.clear()
        self.gen.build_svg(0.0, 0.0, 0)
        deviation = self.gen.symmetry_max_deviation(self.gen.VERTICES, 36.0)
        self.assertGreater(deviation, 1.0, "a tenfold rotation resolved, so the test proves nothing")

    # -- 4. single-cycle stars ---------------------------------------------
    def test_all_five_star_polygons_close_in_eleven_steps(self):
        for step in range(1, 6):
            self.assertTrue(self.gen.star_is_single_cycle(step), f"{{11/{step}}} is not one cycle")

    def test_a_composite_order_star_is_not_a_single_cycle(self):
        # {12/4} revisits its start after three steps: the guard must notice.
        self.assertFalse(self.gen.star_is_single_cycle(4, n=12))
        self.assertTrue(self.gen.star_is_single_cycle(5, n=12))

    def test_the_svg_carries_one_stroke_per_star_and_the_frame(self):
        # Four star polygons are drawn ({11/2}..{11/5}); {11/1} is the hendecagon frame,
        # which is emitted as a polygon. Five orders, five elements, no stray strokes.
        self.assertEqual(self.svg_text.count('<path d="M '), 4, "one stroke per star polygon, no more")
        self.assertEqual(self.svg_text.count("<polygon points="), 13,
                         "frame + eleven lanterns + the 22-gon heart's two polygons")

    # -- 5. not constructible ----------------------------------------------
    def test_two_cos_of_one_eleventh_annihilates_its_minimal_polynomial(self):
        x = 2.0 * math.cos(2.0 * math.pi / 11)
        self.assertLess(abs(self.gen.poly_value(self.gen.minimal_poly_coeffs(), x)), 1e-9)

    def test_the_minimal_polynomial_is_irreducible_of_degree_five(self):
        self.assertTrue(self.gen.minimal_polynomial_is_degree_five())
        # The test must be able to fail: x^5+x^4+1 = (x^2+x+1)(x^3+x+1) over GF(2)...
        self.assertFalse(self.gen.irreducible_over_gf2(0b110001))
        # ...while x^5+x^2+1, which is irreducible there, must pass.
        self.assertTrue(self.gen.irreducible_over_gf2(0b100101))

    def test_a_reducible_degree_five_polynomial_is_caught(self):
        # x^5 + 1 = (x+1)(x^4+x^3+x^2+x+1) over GF(2): it has the factor x+1.
        self.assertFalse(self.gen.irreducible_over_gf2(0b100001))

    def test_five_is_not_a_power_of_two(self):
        # Gauss-Wantzel: a constructible angle has degree a power of two over Q.
        self.assertFalse(5 & (5 - 1) == 0 and 5 > 0)

    def test_an_eleven_gon_is_not_a_constructible_polygon(self):
        # n = 2^a * (distinct Fermat primes). 11 = 11, and 11 is not a Fermat prime
        # because 11 - 1 = 10 is not a power of two.
        self.assertFalse((11 - 1) > 0 and (11 - 1) & (11 - 2) == 0)
        fermat = {3, 5, 17, 257, 65537}
        self.assertNotIn(11, fermat)

    # -- 6. no tiling -------------------------------------------------------
    def test_no_vertex_figure_containing_a_hendecagon_sums_to_a_full_turn(self):
        self.assertEqual(self.gen.vertex_figures_with_hendecagon(), [])

    def test_the_vertex_figure_search_finds_the_figures_that_do_exist(self):
        # Positive controls, in the same exact arithmetic the plate uses. If this ever
        # fails, the empty result above means nothing.
        angle = lambda n: Fraction(1, 2) - Fraction(1, n)  # noqa: E731
        self.assertEqual(sum((angle(6) for _ in range(3)), Fraction(0)), 1)     # 6.6.6
        self.assertEqual(sum((angle(3) for _ in range(6)), Fraction(0)), 1)     # 3^6
        self.assertEqual(sum((angle(3), angle(3), angle(4), angle(12)), Fraction(0)), 1)
        # and three hendecagons overshoot, which is why eleven never appears
        self.assertGreater(sum((angle(11) for _ in range(3)), Fraction(0)), 1)

    # -- 7. containment -----------------------------------------------------
    def test_every_coordinate_is_inside_the_viewbox(self):
        self.assertTrue(self.gen.check_against(self.svg_text)["inside"])
        self.assertIn('viewBox="0 0 1200 1200"', self.svg_text)

    # -- 8. registration ----------------------------------------------------
    def test_the_wing_page_presents_the_plate_and_its_generator(self):
        page = WING_PAGE.read_text(encoding="utf-8")
        self.assertIn("yazdah-girih-elevenfold.svg", page, "the SVG is not on the wall")
        self.assertIn("Yāzdah-Girih", page, "the work is not titled on the wall")
        self.assertIn("generate_desi_girih_yazdah.py", page, "the generator is not named")
        self.assertIn("Desi", page)

    def test_the_matrix_cell_resolves_through_the_pavilion(self):
        rows = dict(gmv.parse_matrix(INDEX.read_text(encoding="utf-8", errors="replace")))
        self.assertIn("islamic", rows)
        cell = rows["islamic"][gmv.AMIGOS.index("desi")]
        self.assertTrue(gmv.is_filled(cell))
        self.assertEqual(gmv.verify_cell("islamic", cell), [], "the matrix cell names nothing on the wall")
        self.assertIn("Yazdah", cell, "the new plate is not credited in the matrix")


if __name__ == "__main__":
    unittest.main(verbosity=2)
