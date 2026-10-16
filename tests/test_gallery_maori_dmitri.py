#!/usr/bin/env python3
"""Pin Dmitri's Māori gallery cell — Unaunahi: The Unbroken Scale (Wing 04).

Why this file exists
--------------------
The generator `docs/gallery/maori/generate-dmitri-unaunahi.py` has cited this test by name
since the work landed on 2026-10-15 (run 20261015T210905Z-af5d3007) — *"pinned by
tests/test_gallery_maori_dmitri.py"* — but the file was never written. A citation of a guard
that does not exist is the same defect the gallery matrix checker was built to catch: a claim
whose truth nothing checks. This is the guard,, written the same day the omission was found.

It also guards the *registration* half of the same defect. This work — like the pen-and-ink
Catenoid and the watercolor Backrun before it — landed on `main` but was never entered in its
wing page or the matrix, so the fifth-column cell read "open" while the art sat one directory
away. The last three tests assert the registration, so a fourth lapse fails here.

What is checked, and why each is a real risk, not decoration
-----------------------------------------------------------
  1. the generator is deterministic and writes the committed bytes — no RNG, no clock;
  2. exactly one element carries `id="unaunahi-ribbon"`, it is a `<path>`, and it has no
     `stroke` — the "one filled shape" claim;
  3. that path's `d` holds exactly one `M` and one `Z` — the "never lifted / one subpath"
     claim, which is the whole formal commitment of the piece;
  4. crest amplitude is capped below the fold: the local radius of curvature at the sweeps'
     extremes stays greater than half the ribbon's greatest width, so the band never
     self-intersects;
  5. the wing page presents the work and the matrix credits the fifth-column cell.

Runner:  python3 tests/test_gallery_maori_dmitri.py
"""

import importlib.util
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GALLERY = ROOT / "docs" / "gallery"
WING = GALLERY / "maori"
GEN_PATH = WING / "generate-dmitri-unaunahi.py"
SVG_PATH = WING / "unaunahi-the-unbroken-scale.svg"
WING_PAGE = WING / "index.html"
INDEX = GALLERY / "index.html"

sys.path.insert(0, str(ROOT / "scripts"))
import gallery_matrix_verify as gmv  # noqa: E402


def load_generator():
    spec = importlib.util.spec_from_file_location("gen_unaunahi", GEN_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class UnaunahiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gen = load_generator()
        cls.svg = SVG_PATH.read_text(encoding="utf-8")
        cls.wing_page = WING_PAGE.read_text(encoding="utf-8", errors="replace")

    # -- 1. the artefact regenerates to the committed bytes -------------------------------

    def test_generator_reproduces_the_committed_svg_byte_for_byte(self):
        self.assertEqual(
            self.gen.build_svg(),
            self.svg,
            "the on-disk SVG differs from what the generator writes: the artefact is stale, "
            "the generator has drifted, or a non-deterministic source (RNG/clock) was added",
        )

    def test_generator_declares_no_randomness_or_clock(self):
        source = GEN_PATH.read_text(encoding="utf-8")
        for forbidden in ("random", "datetime", "time.time", "uuid"):
            self.assertNotIn(
                forbidden, source, f"generator must be deterministic; found {forbidden!r}"
            )

    # -- 2. exactly one filled path, no stroke --------------------------------------------

    def test_exactly_one_element_carries_the_ribbon_id(self):
        self.assertEqual(
            self.svg.count('id="unaunahi-ribbon"'), 1, "the ribbon id must be unique"
        )

    def test_exactly_one_path_element_exists(self):
        self.assertEqual(
            len(re.findall(r"<path\b", self.svg)), 1, "there must be exactly one <path>"
        )

    def test_the_ribbon_is_a_path_with_no_stroke(self):
        match = re.search(r'<path\b[^>]*id="unaunahi-ribbon"[^>]*>', self.svg)
        self.assertIsNotNone(match, "no <path id='unaunahi-ribbon'> found")
        tag = match.group(0)
        self.assertNotIn(
            "stroke", tag, "the ribbon is a filled shape and must declare no stroke"
        )
        self.assertIn("fill", tag, "the ribbon must carry a fill")

    # -- 3. one subpath: exactly one M and one Z ------------------------------------------

    def test_the_ribbon_d_holds_exactly_one_subpath(self):
        d = re.search(r'id="unaunahi-ribbon"[^>]*\bd="([^"]+)"', self.svg)
        self.assertIsNotNone(d, "the ribbon path has no d attribute")
        commands = d.group(1)
        self.assertEqual(
            len(re.findall(r"[Mm]", commands)), 1, "one subpath means exactly one M command"
        )
        self.assertEqual(
            len(re.findall(r"[Zz]", commands)), 1, "one subpath means exactly one Z command"
        )

    # -- 4. the crest amplitude never lets the band fold ----------------------------------

    def test_crest_amplitude_is_capped_below_self_intersection(self):
        gen = self.gen
        x0, x1, _y0, row_h = gen._rows_geometry()
        amp = gen.AMP_FRAC * row_h
        wavelength = (x1 - x0) / gen.COLS
        k = 2.0 * 3.141592653589793 / wavelength
        radius = 1.0 / (amp * k * k)  # local radius of curvature at a crest
        self.assertGreater(
            radius,
            gen.WMAX / 2.0,
            f"crest radius {radius:.2f}px is not greater than half the max half-width "
            f"{gen.WMAX / 2.0}px: the ribbon can fold on itself",
        )

    # -- 5. the work is actually registered (the repeat-offence guard) --------------------

    def test_wing_page_presents_the_work(self):
        self.assertIn("unaunahi-the-unbroken-scale.svg", self.wing_page)
        self.assertIn("Unaunahi", self.wing_page)

    def test_matrix_credits_the_fifth_column_cell(self):
        rows = dict(gmv.parse_matrix(INDEX.read_text(encoding="utf-8", errors="replace")))
        self.assertIn("maori", rows)
        fifth = rows["maori"][4]
        self.assertTrue(gmv.is_filled(fifth), "the maori fifth-column cell still reads open")
        missing = gmv.verify_cell("maori", fifth)
        self.assertEqual(
            missing, [], f"the matrix name is not present in the wing page: {missing}"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
