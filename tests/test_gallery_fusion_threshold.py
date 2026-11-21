#!/usr/bin/env python3
"""The geometry of "The Fusion Threshold", checked against the file rather than the prose.

Dmitri, 2026-11-21 (wake 20261121T033123Z-efcdab70).

Why this exists
---------------
`docs/gallery/impressionism/the-fusion-threshold.svg` is a divisionist dab field that makes
four *numerical* claims, and until today every one of them was asserted only by the generator
that drew it. `generate-dmitri-fusion-threshold.py --check` compares the SVG to a fresh
generation, which proves reproducibility and proves nothing about whether the picture is the
thing it says it is: a hand-edited or rescaled SVG passes `--check` only if it matches the
generator, and a change to the generator passes both halves at once.

The claims the work prints on its own canvas, and which these tests recompute from the pixels:

 1. **No blend anywhere.** Divisionism is the refusal of the gradient. If a `linearGradient`
    or a `fill-opacity` ever enters this file, the mixture is no longer a sum of opaque
    pigments and every other number below stops meaning what it says.
 2. **One named pigment per dab, at full strength.** Every filled path's colour must be one
    of the eleven pigments in the palette — a sixteenth colour means something was blended.
 3. **The dabs are disjoint.** The mixture is an area-weighted mean of *disjoint* areas, not
    an estimate over overlapping ones. Two hexagons that intersect make the coverage figure
    double-count and the fused colour wrong.
 4. **The packing ceiling holds, measured from the picture.** An equal-circle packing covers
    at most pi / (2*sqrt(3)) = 90.69% of the plane, so at least 9% of this canvas must be
    bare primed ground. The test measures the actual pitch from the dab centres, checks that
    no dab is larger than half that pitch, and then checks the area against the ceiling —
    three quantities read off the file, one theorem from outside it.
 5. **The fusion distances follow from that pitch.** 5' chromatic fusion and 1' acuity are
    recomputed here from the pitch the canvas states and compared with the metres the canvas
    prints. A number that was typed rather than computed fails this.

Plus one wiring check, because this repository's characteristic defect is a work that lands
and is never exhibited (`scripts/gallery_unwired_works.py`): the SVG must be linked from its
wing page and named in the gallery matrix's Dmitri cell for that wing.

Two negative controls are included on purpose. A gate that cannot fail is not a gate: the
overlap detector is shown two hexagons that do overlap, and the palette check is shown a
blended fill. If either ever passes, the tests below are decoration.

Run: ``python3 -m unittest tests.test_gallery_fusion_threshold -v``
"""

from __future__ import annotations

import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GALLERY = ROOT / "docs" / "gallery"
WING = GALLERY / "impressionism"
SVG = WING / "the-fusion-threshold.svg"
PAGE = WING / "index.html"
MATRIX = GALLERY / "index.html"

# The palette as it comes out of the tube, from the generator. Eleven pigments, no blends.
PIGMENTS = {
    "#f5f1e6", "#f3d494", "#efb63a", "#dd8a2c", "#cf4229", "#a63b62",
    "#6a5cb0", "#2b4a9b", "#4f93c9", "#2e7d6a", "#2b2b30",
}
# The eye's thresholds, in arcminutes, and the packing ceiling of equal circles in the plane.
CHROMATIC_ARCMIN = 5.0
ACUITY_ARCMIN = 1.0
PACKING_CEILING = math.pi / (2.0 * math.sqrt(3.0))  # 0.9069


def _load() -> str:
    return SVG.read_text(encoding="utf-8")


def _viewbox(text: str) -> tuple[float, float]:
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', text)
    assert m, "the SVG carries no viewBox; every measurement below needs one"
    return float(m.group(1)), float(m.group(2))


def _paths(text: str) -> list[tuple[str, str]]:
    return re.findall(r'<path fill="(#[0-9a-fA-F]{6})" d="([^"]*)"', text)


def _hexagons(text: str) -> list[tuple[float, float, float]]:
    """Every dab as (centre-x, centre-y, circumradius), read from its own six vertices."""
    dabs: list[tuple[float, float, float]] = []
    for _fill, d in _paths(text):
        for sub in d.split("M")[1:]:
            body = sub.replace("Z", "").strip()
            pts = []
            for pair in body.split("L"):
                x, y = pair.strip().split(",")
                pts.append((float(x), float(y)))
            if len(pts) != 6:
                continue
            cx = sum(p[0] for p in pts) / 6.0
            cy = sum(p[1] for p in pts) / 6.0
            r = sum(math.hypot(p[0] - cx, p[1] - cy) for p in pts) / 6.0
            dabs.append((cx, cy, r))
    return dabs


def _overlapping(dabs: list[tuple[float, float, float]], tolerance: float = 0.02):
    """Return the first pair of regular hexagons that intersect, or None.

    Every hexagon in this file is drawn by the same function, so the six flat sides share
    one orientation and the separating-axis theorem needs only three axes: the outward
    normals at 0, 60 and 120 degrees. Two hexagons of circumradius r have projection
    half-width r*cos(30) = r*sqrt(3)/2 on each of them.
    """
    cell = 12.0
    buckets: dict[tuple[int, int], list[int]] = {}
    for i, (x, y, _r) in enumerate(dabs):
        buckets.setdefault((int(x // cell), int(y // cell)), []).append(i)

    axes = [(math.cos(math.radians(a)), math.sin(math.radians(a))) for a in (0.0, 60.0, 120.0)]
    for (bx, by), idxs in buckets.items():
        near = list(idxs)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                near.extend(buckets.get((bx + dx, by + dy), ()))
        for i in idxs:
            x1, y1, r1 = dabs[i]
            for j in near:
                if j <= i:
                    continue
                x2, y2, r2 = dabs[j]
                sep_need = (r1 + r2) * math.sqrt(3.0) / 2.0
                if math.hypot(x2 - x1, y2 - y1) > 2.0 * (r1 + r2):
                    continue
                if not any(
                    abs((x2 - x1) * ax + (y2 - y1) * ay) >= sep_need - tolerance
                    for ax, ay in axes
                ):
                    return (i, j)
    return None


class FusionThresholdTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = _load()
        cls.w, cls.h = _viewbox(cls.text)
        cls.dabs = _hexagons(cls.text)

    def test_the_work_is_there_and_has_dabs(self) -> None:
        self.assertTrue(SVG.exists(), f"{SVG} is missing")
        self.assertGreater(len(self.dabs), 5000, "the dab field is not there")
        self.assertGreater(self.w, 0)
        self.assertGreater(self.h, 0)

    def test_no_gradient_and_no_transparency(self) -> None:
        """Claim 1: divisionism is the refusal of the blend.

        Scoped to the dab field and to gradients, which is what the work claims and what the
        arithmetic needs. The one deliberate exception is the printed label card at the foot
        of the canvas: a `rect` at 86% opacity, which is a caption laid *over* the painting
        and not a dab. It is named here rather than passed over, because a reader who greps
        this file for "opacity" will find it and should find the reason on the same line.
        """
        for banned in ("linearGradient", "radialGradient", "mix-blend", "filter="):
            self.assertTrue(banned not in self.text,
                            f"{banned} is present: the mixture is no longer opaque pigments")
        for fill, d in _paths(self.text):
            self.assertTrue(fill.startswith("#"), "a dab path carries no solid fill")
            self.assertNotIn("opacity", d, "a dab path is translucent")
        # No <path> anywhere may be translucent: only the caption <rect> may be.
        for path_tag in re.findall(r"<path[^>]*>", self.text):
            self.assertNotIn("opacity", path_tag, f"a translucent path: {path_tag[:80]}")

    def test_every_dab_is_one_pigment_at_full_strength(self) -> None:
        """Claim 2: no sixteenth colour, and no path that is not a solid pigment.

        Measured, and the measurement corrects the prose: the palette holds eleven pigments
        but the canvas carries dabs in **eight** of them. Vermilion, rose-madder and viridian
        are mixed into no band, so they are declared and never laid. That is not a defect in
        the file — a painter's palette is the tub, not the picture — but the docstring's
        "eleven pigments" reads as a description of the canvas, so the fact is pinned below.
        """
        fills = {fill.lower() for fill, _d in _paths(self.text)}
        self.assertTrue(fills, "no filled pigment paths at all")
        self.assertLessEqual(fills, PIGMENTS, f"colours outside the palette: {fills - PIGMENTS}")
        self.assertEqual(len(fills), 8, f"dabs are laid in {len(fills)} pigments: {sorted(fills)}")

    def test_the_pigments_not_laid_are_the_three_known_ones(self) -> None:
        """The palette minus the canvas, written down so it cannot drift unnoticed."""
        fills = {fill.lower() for fill, _d in _paths(self.text)}
        unlaid = PIGMENTS - fills
        self.assertEqual(
            unlaid, {"#cf4229", "#a63b62", "#2e7d6a"},
            "the set of declared-but-unlaid pigments changed "
            f"(vermilion, rose-madder, viridian were the three); now {sorted(unlaid)}. "
            "If a band now uses one, update this test and the work's docstring together.",
        )

    def test_dabs_are_disjoint(self) -> None:
        """Claim 3: the mean is over disjoint areas, so the areas may be summed."""
        bad = _overlapping(self.dabs)
        self.assertIsNone(bad, f"dabs {bad} intersect: the coverage figure double-counts")

    def test_packing_ceiling_holds_measured_from_the_picture(self) -> None:
        """Claim 4: at least 9% of the canvas is bare primed ground.

        Three quantities are read out of the file — the stated pitch, the largest dab radius,
        and the summed dab area — and one theorem is applied from outside it: equal circles
        cover at most pi/(2*sqrt(3)) = 90.69% of the plane. Then the lattice is re-measured
        from the dab centres, so a canvas that prints 3.60 mm and draws a 5 mm lattice fails.

        The pitch in pixels is not taken from the generator: it is the stated 3.60 mm on a
        stated 300 mm study, over the viewBox width, all three of which live on the work.
        """
        body = re.search(r"<desc>(.*?)</desc>", self.text, re.S).group(1)
        pitch_mm = float(re.search(r"at a ([\d.]+) mm pitch", body).group(1))
        pitch_px = pitch_mm / (300.0 / self.w)

        r_max = max(r for _x, _y, r in self.dabs)
        self.assertLessEqual(
            r_max, pitch_px / 2.0 + 0.02,
            f"a dab of radius {r_max:.3f} exceeds half the stated pitch {pitch_px:.3f}",
        )

        circle_area = sum(math.pi * r * r for _x, _y, r in self.dabs)
        coverage = circle_area / (self.w * self.h)
        self.assertLessEqual(
            coverage, PACKING_CEILING + 1e-4,
            f"dab coverage {coverage:.4f} beats the packing ceiling {PACKING_CEILING:.4f}",
        )
        self.assertGreaterEqual(
            1.0 - coverage, 0.09,
            f"only {100 * (1 - coverage):.2f}% bare ground; the canvas claims at least 9%",
        )

        # And the lattice on the canvas is the lattice the caption prints: the median
        # nearest-neighbour distance between dab centres is the pitch, less a little jitter
        # (the jitter is bounded, so the median can fall but never far).
        cell = 16.0
        buckets: dict[tuple[int, int], list[int]] = {}
        for i, (x, y, _r) in enumerate(self.dabs):
            buckets.setdefault((int(x // cell), int(y // cell)), []).append(i)
        nearest: list[float] = []
        for (bx, by), idxs in buckets.items():
            near = list(idxs)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    near.extend(buckets.get((bx + dx, by + dy), ()))
            for i in idxs:
                x1, y1, _ = self.dabs[i]
                best = min(
                    (math.hypot(self.dabs[j][0] - x1, self.dabs[j][1] - y1) for j in near if j != i),
                    default=float("inf"),
                )
                if math.isfinite(best):
                    nearest.append(best)
        nearest.sort()
        median_nn = nearest[len(nearest) // 2]
        self.assertAlmostEqual(
            median_nn, pitch_px, delta=0.06 * pitch_px,
            msg=f"the drawn lattice has a {median_nn:.2f} px pitch, the caption {pitch_px:.2f}",
        )

    def test_fusion_distances_follow_from_the_pitch(self) -> None:
        """Claim 5: the printed metres are arithmetic on the stated pitch, not typed in."""
        desc = re.search(r"<desc>(.*?)</desc>", self.text, re.S)
        self.assertIsNotNone(desc, "no <desc>: the numbers are not stated on the work")
        body = desc.group(1)

        pitch_mm = float(re.search(r"at a ([\d.]+) mm pitch", body).group(1))
        fuse_m = float(re.search(r"fuse chromatically beyond ([\d.]+) m", body).group(1))
        acuity_m = float(re.search(r"edges stop being resolvable beyond ([\d.]+) m", body).group(1))

        want_fuse = pitch_mm / 1000.0 / math.tan(math.radians(CHROMATIC_ARCMIN / 60.0))
        want_acuity = pitch_mm / 1000.0 / math.tan(math.radians(ACUITY_ARCMIN / 60.0))
        self.assertAlmostEqual(fuse_m, want_fuse, delta=0.01)
        self.assertAlmostEqual(acuity_m, want_acuity, delta=0.01)
        # And the ordering the physics requires: chromatic fusion happens nearer than the
        # point at which dab edges stop being resolvable.
        self.assertLess(fuse_m, acuity_m)

        # The pitch must also be the pitch the geometry actually has: the canvas is a 300 mm
        # study (stated in the desc), so mm-per-pixel follows, and the lattice must match.
        self.assertIn("300 mm study", body)
        mm_per_px = 300.0 / self.w
        self.assertAlmostEqual(pitch_mm, mm_per_px * 12.0, delta=0.02)

    def test_the_work_is_exhibited_and_not_merely_landed(self) -> None:
        page = PAGE.read_text(encoding="utf-8")
        self.assertIn("the-fusion-threshold.svg", page,
                      "the SVG sits in the wing directory and its own page does not link it")
        matrix = MATRIX.read_text(encoding="utf-8")
        self.assertIn("The Fusion Threshold", matrix,
                      "the gallery matrix does not name the work")


class TheGateCanFailTest(unittest.TestCase):
    """Negative controls. If these pass by accident, the checks above are decoration."""

    def test_the_overlap_detector_finds_an_overlap(self) -> None:
        # Two hexagons of circumradius 5.9 are separated only when their centres are at
        # least 2 * 5.9 * cos(30) = 10.22 apart, so 10.0 is an overlap and 12.0 is not.
        dabs = [(100.0, 100.0, 5.9), (110.0, 100.0, 5.9)]
        self.assertIsNotNone(_overlapping(dabs), "the overlap detector missed two touching dabs")

    def test_the_overlap_detector_clears_a_clean_lattice(self) -> None:
        dabs, dy = [], 12.0 * math.sqrt(3.0) / 2.0
        for row in range(6):
            for col in range(6):
                x = col * 12.0 + (6.0 if row % 2 else 0.0)
                dabs.append((x, row * dy, 5.9))
        self.assertIsNone(_overlapping(dabs), "the overlap detector invents overlaps on a lattice")

    def test_a_blended_fill_is_outside_the_palette(self) -> None:
        fills = {fill.lower() for fill, _d in _paths(_load())}
        self.assertNotIn("#808080", fills)
        self.assertTrue({"#808080"} - PIGMENTS, "the palette check would accept a grey blend")


if __name__ == "__main__":
    unittest.main(verbosity=2)
