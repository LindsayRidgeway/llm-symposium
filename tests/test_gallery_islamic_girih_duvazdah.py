#!/usr/bin/env python3
"""Pin Desi's Islamic gallery cell — Girih-i Duvāzdah: The Twelve-Pointed Star (Wing 03).

Why this file exists
--------------------
The plate (`docs/gallery/islamic/12-point-girih-star.svg`) has been on the wall since
2026-09-07 and its prose has made an arithmetic claim since then: a hero ring of twelve
regular hexagons "whose opposite flat edges bridge adjacent star tips with exact
trigonometric precision". Nothing measured that. The generator could not even be compared
to the plate: the two had drifted apart in the caption block (three elements the script no
longer produced), so no reader could tell whether the artwork on the wall was the program's
output or a hand-edit. Both defects are repaired in the same file that reports them.

What is checked, and why each is a real risk, not decoration
-----------------------------------------------------------
  1. the generator reproduces the committed SVG byte for byte, and running it from another
     directory writes nothing there — the old version wrote its output into whatever
     directory it was launched from, so `python3 docs/gallery/islamic/generate-girih.py`
     from the repository root dropped a stray copy at the root and refreshed nothing;
  2. the star is a genuine twelvefold figure: 24 vertices alternating between the tip radius
     and the valley radius, tips every 30 deg, valleys every 30 deg offset by 15;
  3. it is equilateral — all 24 edges the same length, which is what makes the interlaced
     second pass read as woven rather than skewed — and its interior angles match the closed
     form from the law of cosines, summing to the (24-2)*180 the polygon identity requires;
  4. **the bridging claim, measured on the drawing rather than recomputed from the same
     constants**: for every one of the twelve chords joining adjacent tips, some hexagon has
     a flat whose midpoint sits on that chord's midpoint and whose flat-to-flat width equals
     the chord length. This is the claim the wing page prints, and it is the one that would
     fail silently if anyone retuned R_VAL or the ring radius;
  5. the plate is registered: the wing page presents it and the 6x7 matrix credits the cell.

Runner:  python3 tests/test_gallery_islamic_girih_duvazdah.py
"""

import importlib.util
import math
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WING = ROOT / "docs" / "gallery" / "islamic"
PLATE = WING / "12-point-girih-star.svg"
GENERATOR = WING / "generate-girih.py"
WING_PAGE = WING / "index.html"
MATRIX = ROOT / "docs" / "gallery" / "index.html"

# Coordinate tolerance: the SVG prints two decimals, so any distance computed from two
# printed vertices carries at most ~0.01 px of rounding. 0.05 px is four orders of
# magnitude tighter than the smallest design slack in the figure (the star is 720 px
# across and the caption block sits 6 px from the seal), so it fails on a moved shape
# and never on rounding.
TOL = 0.05


def _load_generator():
    spec = importlib.util.spec_from_file_location("desi_girih_duvazdah", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


G = _load_generator()
CX, CY = G.CX, G.CY
R_TIP, R_VAL = G.R_TIP, G.R_VAL
HEX_R = G.HEX_R
HEX_CENTER_R = G.HEX_CENTER_R
CHORD = G.CHORD


def _polygons():
    """Every <polygon> in the plate as a list of (x, y) tuples, in document order."""
    root = ET.parse(PLATE).getroot()
    polys = []
    for element in root.iter():
        if element.tag.split("}")[-1] != "polygon":
            continue
        raw = element.get("points") or ""
        polys.append([tuple(float(v) for v in pair.split(",")) for pair in raw.split()])
    return polys


def _radius(point):
    return math.hypot(point[0] - CX, point[1] - CY)


def _angle(point):
    return math.degrees(math.atan2(point[1] - CY, point[0] - CX)) % 360.0


def _hero_star():
    """The central 12-point star: the 24-gon whose furthest vertex is at the tip radius."""
    candidates = [p for p in _polygons() if len(p) == 24]
    for poly in candidates:
        if abs(max(_radius(v) for v in poly) - R_TIP) <= TOL:
            return poly
    raise AssertionError("no 24-gon in the plate has a vertex at the tip radius")


def _centroid(poly):
    return (sum(v[0] for v in poly) / len(poly), sum(v[1] for v in poly) / len(poly))


def _hero_hexagons():
    """The twelve ring hexagons: six-gons centred at the mid-chord radius.

    Centred, not scaled: the faint tessellation field also uses six-gons, and it uses the
    same *vertex* radius as nothing else does, but it centres them 1.62x further out. The
    centre is the thing that separates the hero ring from the field.
    """
    ring = []
    for poly in _polygons():
        if len(poly) != 6:
            continue
        if abs(_radius(_centroid(poly)) - HEX_CENTER_R) <= TOL:
            ring.append(poly)
    return ring


def _edge_midpoints(poly):
    return [((poly[i][0] + poly[(i + 1) % len(poly)][0]) / 2.0,
             (poly[i][1] + poly[(i + 1) % len(poly)][1]) / 2.0) for i in range(len(poly))]


def _turns(poly):
    """Angle at each vertex between the two incident edges, and its cross-product sign."""
    n = len(poly)
    angles, signs = [], []
    for i in range(n):
        prev, here, nxt = poly[i - 1], poly[i], poly[(i + 1) % n]
        ax, ay = here[0] - prev[0], here[1] - prev[1]
        bx, by = nxt[0] - here[0], nxt[1] - here[1]
        cross = ax * by - ay * bx
        dot = ax * bx + ay * by
        angles.append(abs(math.degrees(math.atan2(cross, dot))))
        signs.append(1 if cross > 0 else -1)
    return angles, signs


def _interior_angles(poly):
    """Interior angle at each vertex of a simple polygon, in degrees.

    The angle between the two edges at a vertex is the interior angle when the vertex is
    convex and its complement to 360 when it is reflex. Which one a vertex is, is decided
    by whether its cross product matches the winding of the polygon as a whole (the sign of
    the signed area) — not by assumption: twelve of this star's twenty-four vertices are
    the reflex valleys, so a sign error is not a rounding matter.
    """
    angles, signs = _turns(poly)
    area = 0.5 * sum(poly[i][0] * poly[(i + 1) % len(poly)][1]
                     - poly[(i + 1) % len(poly)][0] * poly[i][1]
                     for i in range(len(poly)))
    winding = 1 if area > 0 else -1
    # `_turns` measures the deviation of the path (incoming edge direction to outgoing),
    # which is 0 along a straight line: the interior angle is its supplement, and a reflex
    # vertex takes the supplement on the other side.
    return [180.0 - angle if sign == winding else 180.0 + angle
            for angle, sign in zip(angles, signs)]


class GirihDuvazdahPlateTest(unittest.TestCase):
    def test_the_generator_reproduces_the_committed_plate(self):
        committed = PLATE.read_text(encoding="utf-8")
        self.assertEqual(committed, G.build_svg())
        self.assertGreater(len(committed), 10_000)

    def test_the_generator_writes_beside_itself_not_into_the_caller_directory(self):
        before = PLATE.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(GENERATOR)],
                cwd=tmp, capture_output=True, text=True, check=True,
            )
            self.assertEqual(sorted(p.name for p in Path(tmp).iterdir()), [],
                             "the generator left a file in the directory it was run from")
        self.assertIn("12-point-girih-star.svg", result.stdout)
        self.assertEqual(PLATE.read_text(encoding="utf-8"), before)

    def test_the_star_has_twelve_tips_and_twelve_valleys(self):
        star = _hero_star()
        radii = [_radius(v) for v in star]
        tips = [r for r in radii if abs(r - R_TIP) <= TOL]
        valleys = [r for r in radii if abs(r - R_VAL) <= TOL]
        self.assertEqual(len(tips), 12)
        self.assertEqual(len(valleys), 12)
        self.assertEqual(len(tips) + len(valleys), len(star),
                         "a vertex is at neither the tip radius nor the valley radius")
        # Alternating, starting at a tip: the silhouette is a star, not a sawtooth.
        for index, radius in enumerate(radii):
            expected = R_TIP if index % 2 == 0 else R_VAL
            self.assertAlmostEqual(radius, expected, delta=TOL, msg=f"vertex {index}")

    def test_the_tips_and_valleys_sit_on_their_thirtieth_degrees(self):
        star = _hero_star()
        for index, vertex in enumerate(star):
            angle = _angle(vertex)
            expected = (index * 15.0) % 360.0
            offset = min((angle - expected) % 360.0, (expected - angle) % 360.0)
            self.assertLess(offset, 0.01, f"vertex {index} at {angle:.3f} deg, expected {expected}")

    def test_the_star_is_equilateral(self):
        star = _hero_star()
        edges = [math.dist(star[i], star[(i + 1) % len(star)]) for i in range(len(star))]
        self.assertAlmostEqual(max(edges) - min(edges), 0.0, delta=TOL,
                               msg="the 24-gon is not equilateral")
        # Closed form: the triangle centre-tip-valley has sides R_TIP, R_VAL and the
        # included angle 15 deg, so its third side is the edge length, and every edge
        # is congruent to every other. 202.449 px for the committed constants.
        expected = math.sqrt(R_TIP**2 + R_VAL**2 - 2 * R_TIP * R_VAL * math.cos(math.radians(15)))
        self.assertAlmostEqual(sum(edges) / len(edges), expected, delta=TOL)

    def test_the_interior_angles_sum_to_the_polygon_identity(self):
        star = _hero_star()
        angles = _interior_angles(star)
        self.assertAlmostEqual(sum(angles), (24 - 2) * 180.0, delta=0.05)
        cos15 = math.cos(math.radians(15))
        # Tip angle by the law of cosines on the tip-valley-valley triangle.
        denominator = R_TIP**2 - 2 * R_TIP * R_VAL * cos15 + R_VAL**2
        numerator = R_TIP**2 - 2 * R_TIP * R_VAL * cos15 + R_VAL**2 * math.cos(math.radians(30))
        tip_angle = math.degrees(math.acos(numerator / denominator))
        self.assertAlmostEqual(tip_angle, 24.805, delta=0.01)
        measured_tips = [angles[i] for i in range(0, 24, 2)]
        measured_valleys = [angles[i] for i in range(1, 24, 2)]
        for angle in measured_tips:
            self.assertAlmostEqual(angle, tip_angle, delta=0.02)
        for angle in measured_valleys:
            self.assertAlmostEqual(angle, 330.0 - tip_angle, delta=0.02,
                                   msg="a valley is not the reflex partner of a tip")

    def test_every_hexagon_flat_bridges_a_chord_between_adjacent_tips(self):
        star = _hero_star()
        hexagons = _hero_hexagons()
        self.assertEqual(len(hexagons), 12, "the hero ring is not twelve hexagons")

        # The twelve chords joining adjacent tips, each as (midpoint, length).
        chords = []
        for k in range(12):
            tip, nxt = star[2 * k], star[(2 * k + 2) % 24]
            chords.append(((tip[0] + nxt[0]) / 2.0, (tip[1] + nxt[1]) / 2.0,
                           math.dist(tip, nxt)))
        for midpoint, length in [(c[0:2], c[2]) for c in chords]:
            self.assertAlmostEqual(length, CHORD, delta=TOL)

        flat_to_flat = math.sqrt(3.0) * HEX_R
        bridged = 0
        for chord_x, chord_y, length in chords:
            self.assertAlmostEqual(length, flat_to_flat, delta=TOL,
                                   msg="a bridged hexagon's flats are not the chord's length")
            for hexagon in hexagons:
                centre = (sum(v[0] for v in hexagon) / 6.0, sum(v[1] for v in hexagon) / 6.0)
                if math.dist(centre, (chord_x, chord_y)) > TOL:
                    continue
                touching = [m for m in _edge_midpoints(hexagon)
                            if math.dist(m, (chord_x, chord_y)) > TOL
                            and min(math.dist(m, star[2 * i]) for i in range(12)) <= TOL]
                self.assertEqual(len(touching), 2,
                                 "a ring hexagon should touch exactly two star tips, "
                                 "one flat midpoint each")
                bridged += 1
                break
            else:
                self.fail(f"no ring hexagon is centred on the chord at {chord_x:.2f},{chord_y:.2f}")
        self.assertEqual(bridged, 12, "not every chord between adjacent tips is bridged")

    def test_the_plate_is_on_the_wall(self):
        page = WING_PAGE.read_text(encoding="utf-8")
        self.assertIn('href="12-point-girih-star.svg"', page)
        self.assertIn('data="12-point-girih-star.svg"', page)
        self.assertIn("Girih-i Duvāzdah", page)
        matrix = MATRIX.read_text(encoding="utf-8")
        self.assertIn("Girih-i Duvāzdah", matrix)
        self.assertIn('href="islamic/index.html"', matrix)


if __name__ == "__main__":
    unittest.main(verbosity=2)
