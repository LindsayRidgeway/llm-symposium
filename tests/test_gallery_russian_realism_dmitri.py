#!/usr/bin/env python3
"""The Sunbreak plate's claims, asserted (Dmitri, 2026-10-19).

`docs/gallery/russian-realism/generate-dmitri-sunbreak.py` opens by saying that "every claim
below is asserted in `tests/test_gallery_russian_realism_dmitri.py`". Until 2026-10-19 that
file did not exist, so the generator cited its own verification into being — the same defect
the evidence register spent 2026-10-17 counting, one document at a time. This is that test.

Two kinds of assertion, and the difference matters:

  * **The arithmetic.** The plate's whole argument is that the edge of the light is set by
    three numbers — solar elevation, cloud base, angular size of the sun — and by nothing
    else. Those are checkable in closed form, and the numbers printed on the page
    (W = 13.06 m, edges at -5.2 m and 20.8 m) are checked against the code, not against the
    prose.
  * **The bytes.** The SVG in the wing directory is regenerated in a temp file and compared
    byte for byte. A plate that no longer matches its generator is a picture whose stated
    method is false, whatever its arithmetic says.

What this test deliberately does not assert: that the plate is *exhibited*. It is not. It
carries a written exemption in `scripts/gallery_unwired_works.py` (a study, not an exhibition
piece — the image does not carry the arithmetic), and the last test below pins that state so
that a later wake cannot quietly delete the exemption and leave the work unreachable, nor
exhibit it without deleting the exemption and saying why.
"""

import importlib.util
import math
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WING = ROOT / "docs" / "gallery" / "russian-realism"
GENERATOR = WING / "generate-dmitri-sunbreak.py"
PLATE = WING / "the-edge-of-the-sunbreak.svg"
INDEX = ROOT / "docs" / "gallery" / "index.html"
PAGE = WING / "index.html"

sys.path.insert(0, str(ROOT / "scripts"))


def _load_generator():
    spec = importlib.util.spec_from_file_location("sunbreak", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gen = _load_generator()


class SunbreakArithmeticTest(unittest.TestCase):
    """The three numbers the picture is made of, checked in closed form."""

    def test_sun_elevation_is_latitude_minus_declination(self):
        self.assertAlmostEqual(gen.SUN_ELEVATION, 90.0 - 55.75 - 9.2, places=9)
        self.assertAlmostEqual(gen.SUN_ELEVATION, 25.05, places=6)

    def test_centre_ray_offset_matches_the_page(self):
        # h_c * cot(e), the distance at which the sun's centre ray meets the deck.
        self.assertAlmostEqual(gen.shadow_offset(), 250.0 / math.tan(math.radians(25.05)), places=6)
        self.assertAlmostEqual(gen.shadow_offset(), 535.2, delta=0.05)

    def test_penumbra_width_is_the_page_thirteen_metres(self):
        # The only softness in the picture: the band the solar disc paints on the ground.
        h_c, e, theta = 250.0, math.radians(25.05), math.radians(15.99 / 60.0)
        expected = h_c * (1.0 / math.tan(e - theta) - 1.0 / math.tan(e + theta))
        self.assertAlmostEqual(gen.penumbra_width(), expected, places=9)
        self.assertAlmostEqual(gen.penumbra_width(), 13.06, delta=0.01)

    def test_lit_edges_are_where_the_docstring_says(self):
        near, far = gen.lit_edges()
        self.assertAlmostEqual(near, -5.2, delta=0.1)
        self.assertAlmostEqual(far, 20.8, delta=0.1)
        self.assertAlmostEqual(far - near, gen.penumbra_width() + (gen.HOLE_FAR - gen.HOLE_NEAR),
                               places=6)

    def test_the_hole_is_just_wide_enough_for_the_sun(self):
        # 556 - 530 = 26 m of deck; the sun's disc paints 2 * h_c * tan(theta) across it.
        painted = 2.0 * gen.CLOUD_BASE * math.tan(math.radians(gen.THETA_SUN))
        span = gen.HOLE_FAR - gen.HOLE_NEAR
        self.assertGreater(span, painted, "the hole must be wider than the disc, or no sun shows")
        self.assertLess(span / painted, 1.2, "a hole barely wider than the disc is the claim")


class SunbreakLightTest(unittest.TestCase):
    """The circular-segment function that every value on the field comes from."""

    def test_half_the_disc_at_the_geometric_edge(self):
        self.assertAlmostEqual(gen.chord_fraction(0.0), 0.5, places=12)

    def test_none_and_all(self):
        self.assertEqual(gen.chord_fraction(1.0), 0.0)
        self.assertEqual(gen.chord_fraction(-1.0), 1.0)
        self.assertEqual(gen.chord_fraction(3.0), 0.0)
        self.assertEqual(gen.chord_fraction(-3.0), 1.0)

    def test_symmetry_about_the_edge(self):
        for u in (0.1, 0.25, 0.6, 0.9):
            self.assertAlmostEqual(gen.chord_fraction(u) + gen.chord_fraction(-u), 1.0, places=12)

    def test_monotone_from_shadow_into_light(self):
        samples = [gen.chord_fraction(-1.0 + 0.05 * i) for i in range(41)]
        self.assertEqual(samples, sorted(samples), "the disc fraction must not oscillate")

    def test_field_is_lit_inside_and_dark_beyond(self):
        near, far = gen.lit_edges()
        self.assertAlmostEqual(gen.sun_fraction(near + 0.5), 1.0, places=12)
        self.assertAlmostEqual(gen.sun_fraction(0.0), 1.0, places=12)   # behind the camera
        self.assertAlmostEqual(gen.sun_fraction(far + 30.0), 0.0, places=12)
        self.assertAlmostEqual(gen.sun_fraction(far), 0.5, places=9)    # the edge itself

    def test_light_and_shadow_are_not_the_same_grey(self):
        # The plate's claim to carry its arithmetic is that the field's value *differs*
        # across the edge. Measured in encoded sRGB, mid-field, so it is a property of the
        # colours actually written into the SVG.
        depth = 12.0
        lit = gen._encode(gen.ground_radiance(1.0, depth)[0])
        dark = gen._encode(gen.ground_radiance(0.0, depth)[0])
        self.assertGreater(lit - dark, 0.20, f"only {lit - dark:.3f} of sRGB value across the edge")
        self.assertGreater(lit, dark)

    def test_projection_round_trips(self):
        for depth in (2.0, 12.0, 40.0, 1200.0):
            self.assertAlmostEqual(gen.ground_depth(gen.ground_row(depth)), depth, places=6)


class SunbreakPlateTest(unittest.TestCase):
    """The artefact on disk, and its state in the wing."""

    def test_plate_exists_and_is_standalone_svg(self):
        self.assertTrue(PLATE.exists(), "the plate named in the wing is missing")
        head = PLATE.read_text(encoding="utf-8")[:400]
        self.assertTrue(head.startswith("<svg"), head[:80])
        self.assertNotIn("<image", PLATE.read_text(encoding="utf-8"),
                         "standalone means no embedded raster")
        self.assertNotIn("href=\"http", PLATE.read_text(encoding="utf-8"),
                         "standalone means no external asset")

    def test_generator_reproduces_the_plate_byte_for_byte(self):
        on_disk = PLATE.read_text(encoding="utf-8")
        self.assertEqual(gen.build_svg(), on_disk,
                         "the plate on the wall no longer matches its generator")

    def test_generator_is_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(gen.build_svg(), gen.build_svg())

    def test_docstrings_citation_of_this_file_now_resolves(self):
        # The generator claimed this test existed before it did. Keep the claim checkable.
        doc = GENERATOR.read_text(encoding="utf-8")
        self.assertIn("tests/test_gallery_russian_realism_dmitri.py", doc)
        self.assertTrue(Path(__file__).resolve().exists())

    def test_exhibited_or_exempted_but_never_silently_unreachable(self):
        import gallery_unwired_works as gate  # noqa: E402

        key = "russian-realism/the-edge-of-the-sunbreak.svg"
        unexplained, explained = gate.exempt(gate.unexhibited(["russian-realism"]))
        page = PAGE.read_text(encoding="utf-8")
        exhibited = "the-edge-of-the-sunbreak" in page
        if exhibited:
            self.assertNotIn((("russian-realism"), "the-edge-of-the-sunbreak.svg"), unexplained,
                             "the page exhibits it, so it cannot also be unexplained")
        else:
            self.assertIn(key, gate.EXHIBITION_EXEMPT,
                          "not on the wall and not exempted with a reason: unreachable work")
            self.assertIn(key, [f"{w}/{n}" for w, n in explained])

    def test_matrix_cell_agrees_with_the_page(self):
        import gallery_unwired_works as gate  # noqa: E402

        conflicts = gate.matrix_conflicts()
        page = PAGE.read_text(encoding="utf-8")
        exhibits = "Dmitri S. Pravdin" in page
        self.assertEqual(("07", "russian-realism") in conflicts, exhibits,
                         "the front table and the pavilion page must say the same thing")


if __name__ == "__main__":
    unittest.main()
