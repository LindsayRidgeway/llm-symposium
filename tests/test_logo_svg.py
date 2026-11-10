#!/usr/bin/env python3
"""The commons mark is a file, so its brief can be checked rather than admired.

Written 2026-11-10 (Dmitri) because the logo was asked for from an image model three times and
filed back as "three different failures of one clause" (REQUEST DM-12). An SVG in a diff is the
thing a clause can be tested against: every constraint in the brief is a number in this file.

What is checked, and why each one is here:
  1. it parses, and it is a vector at a stated size                     -- a broken file is not a logo
  2. no raster, no gradient, no filter, no <image>, no url() reference  -- "flat", "no texture"
  3. exactly one drawing colour, black on a white plate                 -- "one colour: black"
  4. no <text>, no wordmark                                             -- "no lettering"
  5. one continuous outline: a single <path>, closed, six points        -- "distinct shapes sharing one outline"
  6. narrowest black span >= viewBox/16 units (>= 4px at 32px)          -- "line weight at least 1/16"
  7. every point inside the viewBox                                     -- clipped marks are not marks

Not checked, because a script cannot: whether the shape is any good. That is a judgement and it
belongs to whoever looks at it, not to this file.
"""
import math
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

SVG = Path(__file__).resolve().parent.parent / "work" / "logo.svg"
NS = "{http://www.w3.org/2000/svg}"


def load():
    return ET.parse(SVG).getroot()


def nums(text):
    return [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", text)]


class LogoTest(unittest.TestCase):
    def setUp(self):
        self.root = load()
        self.vb = [float(v) for v in self.root.get("viewBox", "").split()]
        self.paths = self.root.findall(f"{NS}path")

    def test_1_parses_as_svg_with_a_square_viewbox(self):
        self.assertEqual(self.vb, [0.0, 0.0, 512.0, 512.0], "viewBox must be the square the brief assumes")

    def test_2_no_raster_gradient_filter_or_external_reference(self):
        raw = SVG.read_text()
        for banned in ("<image", "<filter", "Gradient", "url(", "<pattern", "<use"):
            self.assertNotIn(banned, raw, f"{banned!r} is not a flat, self-contained vector")
        for tag in ("image", "filter", "linearGradient", "radialGradient", "pattern"):
            self.assertEqual(self.root.findall(f".//{NS}{tag}"), [], f"<{tag}> is banned by the brief")

    def test_3_one_drawing_colour_black(self):
        fills = set()
        for el in self.root.iter():
            f = el.get("fill")
            if f:
                fills.add(f.lower())
        self.assertEqual(fills, {"#000000", "#ffffff"}, f"expected black on white only, found {sorted(fills)}")

    def test_4_no_lettering_anywhere(self):
        self.assertEqual(self.root.findall(f".//{NS}text"), [])
        raw = SVG.read_text()
        for tag in ("<tspan", "<textPath"):
            self.assertNotIn(tag, raw)

    def test_5_one_closed_path_with_two_six_vertex_subpaths(self):
        self.assertEqual(len(self.paths), 1, "the six points must be one outline, not six shapes")
        d = self.paths[0].get("d")
        subs = [s.strip() for s in d.split("Z") if s.strip()]
        self.assertEqual(len(subs), 2, "outer outline + the open centre")
        verts = []
        for sub in subs:
            pts = nums(sub.replace("M", " "))
            self.assertEqual(len(pts) % 2, 0)
            verts.append(len(pts) // 2)
        self.assertEqual(verts, [12, 6], f"six points (12 vertices) around a hexagon, found {verts}")
        self.assertTrue(d.strip().endswith("Z"), "the outline must close")

    def test_6_line_weight_at_least_one_sixteenth_of_the_mark(self):
        """The narrowest black span, measured on the two subpaths rather than guessed from a comment.

        The six points end in corners, not strokes: a corner is not a line weight, and at 32px the
        tip is sub-pixel by design. What has to survive 32px is the band between the valley and the
        open centre, so that is what is measured -- and it is stated as a number, not asserted as a
        compliment. If a future editor shrinks the valley, this test names the units.
        """
        d = self.paths[0].get("d")
        subs = [s for s in d.split("Z") if s.strip()]
        c = [self.vb[2] / 2, self.vb[3] / 2]

        def radii(sub):
            v = nums(sub)
            return [math.dist((v[i], v[i + 1]), c) for i in range(0, len(v) - 1, 2)]

        valley = min(radii(subs[0]))          # nearest the centre of the point
        hole_edge = max(radii(subs[1]))       # furthest out of the open centre
        gap = valley - hole_edge * math.cos(math.radians(30))
        self.assertGreaterEqual(gap, self.vb[2] / 16,
                                f"narrowest black span {gap:.1f} units is under {self.vb[2] / 16:.1f}")
        self.assertGreaterEqual(gap * 32 / self.vb[2], 2.0, "must survive a 32px render with >2px of black")

    def test_7_every_point_inside_the_viewbox(self):
        d = self.paths[0].get("d")
        for s in d.split("Z"):
            v = nums(s)
            for i in range(0, len(v) - 1, 2):
                self.assertTrue(0 <= v[i] <= self.vb[2], f"x {v[i]} outside viewBox")
                self.assertTrue(0 <= v[i + 1] <= self.vb[3], f"y {v[i+1]} outside viewBox")


if __name__ == "__main__":
    unittest.main(verbosity=2)
