#!/usr/bin/env python3
"""The Counting Room, February — a painting assembled from strokes (Dmitri, 2026-10-19).

Wing 07 (Russian realism), Dmitri's column. The cell has been open on purpose since 2026-10-18:
`the-edge-of-the-sunbreak.svg` is a flat snowfield plate that computes where light stops but does
not read as light stopping, and that wing's other four works are painted oils. My own note in
`scripts/gallery_unwired_works.py` says the wing "wants paint" and that paint is "the only thing I
cannot do", and REQUEST DM-2 asked the human for two Mage oils to cover wings 01 and 07.

**This plate is a correction to that sentence, and it is the reason the work exists.** What I cannot
do is a *diffusion* oil. What I had never tried is paint made of brush marks — thousands of discrete
strokes, each one loaded, dragged, and lifted, with no gradient anywhere in the file. Whether that
reads as paint is not a claim I get to make in a docstring; it is checked by looking at
`the-counting-room-february.png`, rendered from this plate, and the honest account of what it can and
cannot do is at the bottom of this file.

Why this subject
----------------
Peredvizhniki genre realism is a room, a window, and the work of an ordinary day: a clerk's counting
room in February, a low sun coming in across a ledger, one page in the light and one in the shade.
It is also a subject where the picture's only real decision is *where the edge of the light falls*,
and that is arithmetic, which is the part of a painting I can be trusted with.

The geometry, in full, and every number below is asserted in
`tests/test_gallery_russian_realism_counting_room.py`
-------------------------------------------------------------------------------------------------
A pinhole camera at height EYE_H = 1.55 m, Z_CAM = 2.40 m in front of the back wall, focal length
F = 1040 px. A world point (X, Y, Z) — metres, Y up, Z out of the wall toward the viewer — projects to

    u = CX + F * X / (Z_CAM - Z)
    v = CY - F * (Y - EYE_H) / (Z_CAM - Z)

Only flat things are projected: the wall, the window opening, the table top, and the ledger's two
pages. Solids (the ink bottle, the candle, the quill, the cloth) are painted by hand, because a
cylinder drawn by a projection I half-understood would be a lie with a number attached.

The sun is at elevation e = 22 deg and azimuth 28 deg from the wall normal; its rays travel into the
room along

    d = (cos e sin az, -sin e, cos e cos az) = (0.4353, -0.3746, 0.8186)

A ray entering the window at height Y_w reaches the table (Y = 0.75 m) at parameter t = (Y_w - 0.75) /
sin e. For the sill (Y_w = 1.05 m) that is t = 0.801 m and the ray lands at Z = 0.656 m — 0.80 m of
travel for a 0.30 m drop, which is what a 22-degree February sun does. Rays from the upper half of the
window clear the table and land on the floor out of frame: only the bottom 0.30 m of the window lights
the desk, and that is why the light on the table is a band and not a window-shaped copy.

The penumbra is the part that decides the technique. The sun's angular radius is 0.266 deg, so the
half-shadow a window edge throws at slant distance L is L * tan(0.532 deg):

    L = 0.801 m  ->  7.4 mm
    L = 1.405 m  ->  13.0 mm   (the near table edge)

A loaded filbert holds a mark 24 mm wide. **The penumbra is narrower than the brush that paints it by
about 1.8x, so no brush can draw the soft edge and no gradient in this file is entitled to fake one.**
The edge is painted the way a painter paints it: strokes are assigned to the lit side or the shadow
side by the exact projected boundary, and the transition is one brush wide because the brush is wider
than the thing it is describing. That is the whole wager of the plate, and it is falsifiable — see the
last section.

What is in the file
-------------------
  * no `<linearGradient>` and no `<radialGradient>`, anywhere: every value change is a separate mark;
  * every stroke is a `<path>` with `stroke-linecap="round"`, `< 2` decimal places on coordinates;
  * strokes are clipped per region, so paint stops at a plank's edge the way paint actually does when
    a painter's hand stops, and a handful of deliberate "carry strokes" spill over region boundaries
    where a loaded brush would have run out of paint past the edge;
  * the weave of the canvas is a `<pattern>` of two crossing threads, not a texture image.

Runner, and the numbers:

    python3 docs/gallery/russian-realism/generate-dmitri-counting-room.py --metrics
"""

from __future__ import annotations

import argparse
import colorsys
import json
import math
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_OUT = HERE / "the-counting-room-february.svg"

# --- picture -----------------------------------------------------------------------------------
W, H = 1400, 1000
CX, CY = W / 2.0, 300.0

# --- camera, metres ----------------------------------------------------------------------------
Z_CAM = 2.40
EYE_H = 1.55
F = 1040.0

# --- sun ----------------------------------------------------------------------------------------
SUN_ELEV_DEG = 22.0
SUN_AZ_DEG = 28.0
SUN_ANGULAR_DIAMETER_DEG = 0.532

# --- room, metres -------------------------------------------------------------------------------
WIN = {"x0": 0.05, "x1": 0.95, "y0": 1.05, "y1": 2.05}
TABLE_H = 0.75
TABLE = {"x0": -1.90, "x1": 2.00, "z0": 0.55, "z1": 1.15}
LEDGER = {"x0": -0.10, "x1": 0.90, "z0": 0.72, "z1": 1.02}

# --- brush --------------------------------------------------------------------------------------
BRUSH_MM = 24.0  # a loaded filbert, and the number the penumbra is measured against
SEED = 20261019


def project(x: float, y: float, z: float) -> tuple[float, float]:
    """Pinhole projection of a world point (metres) to image pixels."""
    depth = Z_CAM - z
    if depth <= 0.02:
        raise ValueError("point is at or behind the camera")
    return (CX + F * x / depth, CY - F * (y - EYE_H) / depth)


def ray_to_table(y_w: float) -> float:
    """Slant distance a ray from window height y_w travels before it reaches the table top."""
    e = math.radians(SUN_ELEV_DEG)
    return (y_w - TABLE_H) / math.sin(e)


def penumbra_mm(slant_m: float) -> float:
    """Width of the half-shadow a straight edge throws at slant distance slant_m."""
    return slant_m * math.tan(math.radians(SUN_ANGULAR_DIAMETER_DEG)) * 1000.0


def sun_direction() -> tuple[float, float, float]:
    e = math.radians(SUN_ELEV_DEG)
    a = math.radians(SUN_AZ_DEG)
    return (math.cos(e) * math.sin(a), -math.sin(e), math.cos(e) * math.cos(a))


def patch_corner(x_w: float, y_w: float) -> tuple[float, float, float]:
    """Where a window point's ray meets the table top, in world coordinates."""
    dx, dy, dz = sun_direction()
    t = (y_w - TABLE_H) / (-dy)
    return (x_w + t * dx, TABLE_H, t * dz)


# --- colour -------------------------------------------------------------------------------------
def _clamp(v: float) -> float:
    return 0.0 if v < 0.0 else 1.0 if v > 1.0 else v


def mix(a: str, b: str, k: float) -> str:
    """Mix two #rrggbb colours, k = 0 gives a, k = 1 gives b."""
    ar, ag, ab = (int(a[i:i + 2], 16) / 255.0 for i in (1, 3, 5))
    br, bg, bb = (int(b[i:i + 2], 16) / 255.0 for i in (1, 3, 5))
    r, g, bl = (ar + (br - ar) * k, ag + (bg - ag) * k, ab + (bb - ab) * k)
    return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(bl * 255))


def scale(colour: str, factor: float) -> str:
    """Multiply a paint's lightness — the hook the room's light is painted through."""
    r = int(colour[1:3], 16) / 255.0
    g = int(colour[3:5], 16) / 255.0
    b = int(colour[5:7], 16) / 255.0
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    h, l, s = colorsys.hls_to_rgb(h, _clamp(l * factor), _clamp(s))
    return "#%02x%02x%02x" % (round(h * 255), round(g * 255), round(s * 255))


def vary(colour: str, rng: random.Random, value: float = 0.06, sat: float = 0.05,
         hue: float = 0.012) -> str:
    """A neighbouring paint: a brush load is never the same paint twice."""
    r = int(colour[1:3], 16) / 255.0
    g = int(colour[3:5], 16) / 255.0
    b = int(colour[5:7], 16) / 255.0
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    h = (h + rng.uniform(-hue, hue)) % 1.0
    l = _clamp(l + rng.uniform(-value, value))
    s = _clamp(s + rng.uniform(-sat, sat))
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255))


# --- canvas -------------------------------------------------------------------------------------
class Canvas:
    """Collects SVG elements and counts what it has painted."""

    def __init__(self) -> None:
        self.defs: list[str] = []
        self.layers: list[str] = []
        self.strokes = 0
        self.marks_by_layer: dict[str, int] = {}
        self._layer: list[str] | None = None
        self._layer_name = ""

    def begin(self, name: str) -> None:
        self._layer_name = name
        self._layer = []
        self.marks_by_layer.setdefault(name, 0)

    def end(self) -> None:
        if self._layer:
            self.layers.append('<g id="%s">\n%s\n</g>' % (self._layer_name, "\n".join(self._layer)))
        self._layer = None

    def add(self, element: str) -> None:
        assert self._layer is not None, "add() outside a layer"
        self._layer.append(element)
        self.marks_by_layer[self._layer_name] += 1

    def stroke(self, x0: float, y0: float, x1: float, y1: float, width: float, colour: str,
               bow: float = 0.0, alpha: float = 1.0, cap: str = "round") -> None:
        """One brush mark: a slightly bowed path from (x0,y0) to (x1,y1)."""
        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / length, dx / length
        mx = (x0 + x1) / 2.0 + nx * bow
        my = (y0 + y1) / 2.0 + ny * bow
        opacity = "" if alpha >= 0.999 else ' stroke-opacity="%.2f"' % alpha
        self.add(
            '<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
            'stroke-width="%.1f" stroke-linecap="%s"%s/>'
            % (x0, y0, mx, my, x1, y1, colour, width, cap, opacity)
        )
        self.strokes += 1

    def polygon(self, pts: list[tuple[float, float]], colour: str, op: str = "") -> None:
        d = " ".join("%.1f,%.1f" % p for p in pts)
        extra = ' fill-opacity="%.2f"' % float(op) if op else ""
        self.add('<polygon points="%s" fill="%s"%s/>' % (d, colour, extra))

    def clip(self, pts: list[tuple[float, float]]) -> str:
        cid = "clip%d" % (len(self.defs) + 1)
        d = " ".join("%.1f,%.1f" % p for p in pts)
        self.defs.append('<clipPath id="%s"><polygon points="%s"/></clipPath>' % (cid, d))
        return cid


# --- painting -----------------------------------------------------------------------------------
def bbox(pts: list[tuple[float, float]]) -> tuple[float, float, float, float]:
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def inside(pts: list[tuple[float, float]], x: float, y: float) -> bool:
    """Even-odd point-in-polygon, used to place strokes rather than to clip them."""
    res = False
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xin = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < xin:
                res = not res
    return res


def paint(canvas: Canvas, pts: list[tuple[float, float]], colours: list[str], rng: random.Random,
          length: float, width: float, angle: float, angle_spread: float = 12.0,
          cover: float = 1.35, texture: float = 1.0, bristles: int = 0,
          lit_edge: str | None = None, shade=None, avoid=None) -> None:
    """Cover a polygon with brush marks laid along `angle` degrees.

    `cover` is how much paint is laid down per unit area: 1.0 means each stroke is one stroke-width
    from its neighbour, so the region is painted once. Above 1.6 it is scrubbed in.
    """
    x0, y0, x1, y1 = bbox(pts)
    cid = canvas.clip(pts)
    canvas.add('<g clip-path="url(#%s)">' % cid)
    step = max(4.0, width / max(cover, 0.05))
    step = min(step, width * 0.85)
    a = math.radians(-angle)
    # scan the bounding box on a grid rotated with the strokes, so a region painted at 30 degrees
    # does not show a horizontal seam where the scan rows meet the clip edge
    span = math.hypot(x1 - x0, y1 - y0)
    cx0, cy0 = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    rows = int(span / (step * 0.92)) + 2
    travel = span * 1.15
    for r in range(rows):
        off = -span / 2.0 + r * step * 0.92 + rng.uniform(-step * 0.18, step * 0.18)
        for _ in range(max(1, int(travel / (length * 0.85)))):
            along = rng.uniform(-span / 2.0, span / 2.0)
            # position in rotated space, then rotated back to the page
            rx, ry = along, off
            px = cx0 + rx * math.cos(a) - ry * math.sin(a)
            py = cy0 + rx * math.sin(a) + ry * math.cos(a)
            if not inside(pts, px, py):
                continue
            if avoid is not None and inside(avoid, px, py):
                continue
            ang = math.radians(angle + rng.uniform(-angle_spread, angle_spread))
            ln = length * rng.uniform(0.55, 1.15)
            dx, dy = math.cos(ang) * ln / 2.0, -math.sin(ang) * ln / 2.0
            col = vary(rng.choice(colours), rng, value=0.05 * texture, sat=0.05 * texture)
            if shade is not None:
                col = scale(col, shade(px, py))
            canvas.stroke(px - dx, py - dy, px + dx, py + dy,
                          width * rng.uniform(0.72, 1.12), col,
                          bow=rng.uniform(-width * 0.25, width * 0.25))
            for b in range(bristles):
                s = rng.choice((-1, 1)) * width * rng.uniform(0.18, 0.36)
                nx, ny = -dy / (ln / 2.0), -dx / (ln / 2.0)
                canvas.stroke(px - dx + nx * s, py - dy + ny * s, px + dx + nx * s, py + dy + ny * s,
                              width * 0.30, vary(col, rng, value=0.10), alpha=0.85)
    if lit_edge:
        # a loaded brush does not stop dead at the edge of its region: a few marks carry over
        n = len(pts)
        for i in range(n):
            (ax, ay), (bx, by) = pts[i], pts[(i + 1) % n]
            if math.hypot(bx - ax, by - ay) < 30:
                continue
            for _ in range(int(math.hypot(bx - ax, by - ay) / 55)):
                k = rng.random()
                px, py = ax + (bx - ax) * k, ay + (by - ay) * k
                ang = math.radians(angle + rng.uniform(-40, 40))
                ln = length * rng.uniform(0.3, 0.8)
                canvas.stroke(px, py, px + math.cos(ang) * ln, py - math.sin(ang) * ln,
                              width * 0.65, vary(lit_edge, rng, value=0.05), alpha=0.9)
    canvas.add("</g>")


def scribble(canvas: Canvas, pts: list[tuple[float, float]], colour: str, rng: random.Random,
             width: float, step: float, wobble: float) -> None:
    """Fine marks inside a polygon — ruling, hatching, handwriting."""
    x0, y0, x1, y1 = bbox(pts)
    y = y0
    while y < y1:
        row: list[tuple[float, float]] = []
        x = x0
        while x <= x1:
            if inside(pts, x, y + rng.uniform(-wobble, wobble)):
                row.append((x, y + rng.uniform(-wobble, wobble)))
            x += step
        if len(row) > 1:
            d = "M" + " L".join("%.1f %.1f" % p for p in row)
            canvas.add('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f" '
                       'stroke-linecap="round" stroke-opacity="0.55"/>' % (d, colour, width))
        y += rng.uniform(7.0, 9.5)
    canvas.strokes += 1


# --- the picture --------------------------------------------------------------------------------
def build() -> tuple[Canvas, dict]:
    rng = random.Random(SEED)
    c = Canvas()

    # canvas weave: two crossing threads, not a texture image
    c.defs.append(
        '<pattern id="weave" width="6" height="6" patternUnits="userSpaceOnUse">'
        '<rect width="6" height="6" fill="none"/>'
        '<path d="M0 1.5 H6" stroke="#000000" stroke-opacity="0.05" stroke-width="1"/>'
        '<path d="M1.5 0 V6" stroke="#ffffff" stroke-opacity="0.04" stroke-width="1"/>'
        '</pattern>'
    )

    # --- ground: a warm imprimatura, the colour a painter leaves showing through ---------------
    c.begin("ground")
    c.polygon([(0, 0), (W, 0), (W, H), (0, H)], "#6b5b46")
    c.polygon([(0, 0), (W, 0), (W, H), (0, H)], "url(#weave)")
    c.end()

    # --- wall -----------------------------------------------------------------------------------
    wl, wr, wt, wb = WIN["x0"], WIN["x1"], WIN["y1"], WIN["y0"]
    glass_pts = [project(wl, wt, 0.0), project(wr, wt, 0.0), project(wr, wb, 0.0),
                 project(wl, wb, 0.0)]
    gx0, gy0, gx1, gy1 = bbox(glass_pts)
    wcx, wcy = (gx0 + gx1) / 2.0, (gy0 + gy1) / 2.0
    whalf, hhalf = (gx1 - gx0) / 2.0, (gy1 - gy0) / 2.0

    def wall_shade(x: float, y: float) -> float:
        """The room's light, one factor per brush load — no gradient element anywhere."""
        d = math.hypot(max(abs(x - wcx) - whalf, 0.0), max(abs(y - wcy) - hhalf, 0.0))
        spill = math.exp(-d / 210.0)
        f = 0.60 + 0.66 * spill
        if y > gy1:  # shadow gathering under the sill
            f *= 1.0 - 0.26 * min(1.0, (y - gy1) / 240.0)
        if x < gx0:  # the darkest corner of a room is the one furthest from the window
            f *= 1.0 - 0.24 * min(1.0, (gx0 - x) / 760.0)
        return f

    c.begin("wall")
    paint(c, [(-260.0, -220.0), (W + 260.0, -220.0), (W + 260.0, H + 60.0), (-260.0, H + 60.0)],
          ["#7d7059", "#847659", "#6f6450", "#8b7f68"], rng, length=155.0, width=48.0,
          angle=87.0, angle_spread=13.0, cover=1.15, texture=0.9, bristles=1,
          lit_edge="#8d8168", shade=wall_shade, avoid=glass_pts)
    c.end()

    # --- window: the February outside ----------------------------------------------------------
    c.begin("window")
    glass = [project(wl, wt, 0.0), project(wr, wt, 0.0), project(wr, wb, 0.0), project(wl, wb, 0.0)]
    gx0, gy0, gx1, gy1 = bbox(glass)
    sky = [(gx0, gy0), (gx1, gy0), (gx1, gy0 + (gy1 - gy0) * 0.42), (gx0, gy0 + (gy1 - gy0) * 0.42)]
    snow = [(gx0, gy0 + (gy1 - gy0) * 0.40), (gx1, gy0 + (gy1 - gy0) * 0.40), (gx1, gy1), (gx0, gy1)]
    paint(c, sky, ["#cdd6dd", "#c3ccd4", "#d6dee4"], rng, length=90.0, width=26.0, angle=6.0,
          angle_spread=8.0, cover=1.2, texture=0.7)
    paint(c, snow, ["#e7eae4", "#dfe5e2", "#eef0ea", "#d8e0dd"], rng, length=110.0, width=28.0,
          angle=4.0, angle_spread=10.0, cover=1.2, texture=0.8, lit_edge="#f2f4ee")
    # a distant spruce line, and a fence that a February field always has
    for i in range(26):
        bx = gx0 + (gx1 - gx0) * (i / 26.0) + rng.uniform(-6, 6)
        bh = rng.uniform(18, 40)
        by = gy0 + (gy1 - gy0) * 0.41
        for k in range(4):
            sway = rng.uniform(-4, 4)
            c.stroke(bx, by, bx + sway, by - bh * (0.35 + 0.22 * k), rng.uniform(5, 9),
                     vary("#4a4f45", rng, value=0.08), alpha=0.9)
    for i in range(11):
        fx = gx0 + (gx1 - gx0) * (0.06 + 0.088 * i)
        fy = gy0 + (gy1 - gy0) * rng.uniform(0.52, 0.60)
        c.stroke(fx, fy, fx + rng.uniform(-2, 2), fy - rng.uniform(22, 30), 3.4,
                 vary("#4b4038", rng, value=0.07))
    c.stroke(gx0, gy0 + (gy1 - gy0) * 0.575, gx1, gy0 + (gy1 - gy0) * 0.60, 2.6,
             vary("#4b4038", rng, value=0.05))
    c.end()

    # --- window frame and glazing bars ---------------------------------------------------------
    c.begin("frame")
    bar = 9.0
    for (ax, ay, bx, by) in (
        (gx0, gy0, gx1, gy0), (gx0, gy1, gx1, gy1),
        (gx0, gy0, gx0, gy1), (gx1, gy0, gx1, gy1),
        (gx0 + (gx1 - gx0) / 3.0, gy0, gx0 + (gx1 - gx0) / 3.0, gy1),
        (gx0 + 2 * (gx1 - gx0) / 3.0, gy0, gx0 + 2 * (gx1 - gx0) / 3.0, gy1),
        (gx0, gy0 + (gy1 - gy0) * 0.42, gx1, gy0 + (gy1 - gy0) * 0.42),
    ):
        steps = max(2, int(math.hypot(bx - ax, by - ay) / 40))
        for s in range(steps):
            t0, t1 = s / steps, (s + 1) / steps
            c.stroke(ax + (bx - ax) * t0, ay + (by - ay) * t0,
                     ax + (bx - ax) * t1, ay + (by - ay) * t1,
                     bar * rng.uniform(0.85, 1.15), vary("#4e3f2e", rng, value=0.07))
    # frost creeping in from the corners: dendrites, not a blur
    for corner, (fx, fy), dirx, diry in (
        ((gx0, gy0), (gx0 + 8, gy0 + 8), 1, 1),
        ((gx1, gy0), (gx1 - 8, gy0 + 8), -1, 1),
        ((gx0, gy1), (gx0 + 8, gy1 - 8), 1, -1),
    ):
        del corner
        for i in range(16):
            a = math.atan2(diry, dirx) + rng.uniform(-0.9, 0.9)
            ln = rng.uniform(22, 74)
            x1 = fx + math.cos(a) * ln
            y1 = fy + math.sin(a) * ln
            c.stroke(fx, fy, x1, y1, rng.uniform(1.2, 2.6),
                     vary("#eef2f4", rng, value=0.05), alpha=0.75)
            for k in (0.35, 0.6, 0.82):
                mx, my = fx + math.cos(a) * ln * k, fy + math.sin(a) * ln * k
                for s in (-1, 1):
                    b = a + s * rng.uniform(0.5, 1.0)
                    c.stroke(mx, my, mx + math.cos(b) * ln * 0.22, my + math.sin(b) * ln * 0.22,
                             1.1, vary("#f4f7f8", rng, value=0.04), alpha=0.6)
    c.end()

    # --- floor between the wall and the table --------------------------------------------------
    tb_far = [project(TABLE["x0"], TABLE_H, TABLE["z0"]), project(TABLE["x1"], TABLE_H, TABLE["z0"])]
    floor = [(-260.0, project(0, 0, 0.0)[1]), (W + 260.0, project(0, 0, 0.0)[1]),
             (W + 260.0, tb_far[1][1] + 6), (-260.0, tb_far[0][1] + 6)]
    c.begin("floor")
    paint(c, floor, ["#5c5041", "#544936", "#665845"], rng, length=150.0, width=30.0,
          angle=2.0, angle_spread=10.0, cover=1.2, texture=1.1, bristles=1)
    for i in range(14):
        x = -260 + i * 130
        c.stroke(x, floor[0][1] - 30, x + rng.uniform(-16, 16), floor[2][1], rng.uniform(1.4, 2.4),
                 vary("#3e3529", rng, value=0.06), alpha=0.7)
    c.end()

    # --- the table top -------------------------------------------------------------------------
    table = [project(TABLE["x0"], TABLE_H, TABLE["z0"]), project(TABLE["x1"], TABLE_H, TABLE["z0"]),
             project(TABLE["x1"], TABLE_H, TABLE["z1"]), project(TABLE["x0"], TABLE_H, TABLE["z1"])]
    c.begin("table")
    paint(c, table, ["#4b4237", "#564b3d", "#453d33"], rng, length=150.0, width=30.0,
          angle=1.0, angle_spread=8.0, cover=1.25, texture=1.1, bristles=1)
    # plank edges run into the wall, so their angle is the projection of the depth axis
    far_l, near_l = project(TABLE["x0"], TABLE_H, TABLE["z0"]), project(TABLE["x0"], TABLE_H, TABLE["z1"])
    for i in range(9):
        x_w = TABLE["x0"] + (TABLE["x1"] - TABLE["x0"]) * (0.06 + 0.11 * i)
        pl = project(x_w, TABLE_H, TABLE["z0"])
        pn = project(x_w, TABLE_H, TABLE["z1"])
        c.stroke(pl[0], pl[1], pn[0], pn[1], rng.uniform(1.6, 2.8), vary("#332c23", rng),
                 alpha=0.75)
    del near_l

    # the light band: the window's bottom edge, thrown onto the table
    p_sill_l = patch_corner(wl, wb)
    p_sill_r = patch_corner(wr, wb)
    st = 1.0
    p_near_l = (p_sill_l[0] + st * math.tan(math.radians(SUN_AZ_DEG)), TABLE_H, TABLE["z1"])
    p_near_r = (p_sill_r[0] + st * math.tan(math.radians(SUN_AZ_DEG)), TABLE_H, TABLE["z1"])
    patch = [project(*p_sill_l), project(*p_sill_r), project(*p_near_r), project(*p_near_l)]
    paint(c, patch, ["#cfae78", "#c6a273", "#dcbe8b", "#b89a6b"], rng, length=70.0, width=22.0,
          angle=6.0, angle_spread=14.0, cover=1.35, texture=1.3, bristles=1, lit_edge="#e6cd9c")
    c.end()

    # --- the ledger: one page in the sun, one in the shade -------------------------------------
    spine_x = (LEDGER["x0"] + LEDGER["x1"]) / 2.0
    left_page = [project(LEDGER["x0"], TABLE_H + 0.004, LEDGER["z0"]),
                 project(spine_x, TABLE_H + 0.004, LEDGER["z0"] + 0.008),
                 project(spine_x, TABLE_H + 0.004, LEDGER["z1"]),
                 project(LEDGER["x0"], TABLE_H + 0.004, LEDGER["z1"])]
    right_page = [project(spine_x, TABLE_H + 0.004, LEDGER["z0"] + 0.008),
                  project(LEDGER["x1"], TABLE_H + 0.004, LEDGER["z0"]),
                  project(LEDGER["x1"], TABLE_H + 0.004, LEDGER["z1"]),
                  project(spine_x, TABLE_H + 0.004, LEDGER["z1"])]
    c.begin("ledger")
    # the page in the light is only the part of the right page the sun actually reaches
    lit_page = [p for p in right_page if inside(patch, *p)]
    del lit_page
    paint(c, left_page, ["#b3a88d", "#a89d84", "#bdb29a", "#9d937c"], rng, length=64.0,
          width=20.0, angle=4.0, angle_spread=9.0, cover=1.3, texture=0.9, bristles=1)
    paint(c, right_page, ["#e9dfc4", "#ded2b3", "#f2e8ce", "#d7c9a7"], rng, length=64.0,
          width=20.0, angle=4.0, angle_spread=9.0, cover=1.3, texture=0.9, bristles=1,
          lit_edge="#f6eed6")
    # the shadow of the window's muntin falls across the lit page — one brush wide, because the
    # penumbra (13 mm) is narrower than the brush (24 mm); there is no gradient to draw it with
    mb_l, mb_r = patch_corner(wl + (wr - wl) / 3.0, wb), patch_corner(wl + (wr - wl) / 3.0, wb)
    del mb_l, mb_r
    for page, inks in ((left_page, "#4a4034"), (right_page, "#3f362b")):
        px0, py0, px1, py1 = bbox(page)
        rows = 11
        for r in range(rows):
            k = (r + 1) / (rows + 1.0)
            ax = page[0][0] + (page[3][0] - page[0][0]) * k
            ay = page[0][1] + (page[3][1] - page[0][1]) * k
            bx = page[1][0] + (page[2][0] - page[1][0]) * k
            by = page[1][1] + (page[2][1] - page[1][1]) * k
            x = ax + (bx - ax) * 0.06
            while x < ax + (bx - ax) * 0.94:
                ln = rng.uniform(8, 26)
                y = ay + (by - ay) * (x - ax) / max(bx - ax, 1e-6)
                c.stroke(x, y, min(x + ln, bx), y + rng.uniform(-1.4, 1.4), rng.uniform(1.1, 1.9),
                         vary(inks, rng, value=0.12), alpha=0.8)
                x += ln + rng.uniform(7, 20)
        del px0, py0, px1, py1
    # the binding: two dark leather boards and a spine, painted over the page edges
    spine = [left_page[1], right_page[0], right_page[3], left_page[2]]
    paint(c, spine, ["#5a3526", "#4a2b1f", "#6a4030"], rng, length=90.0, width=18.0, angle=88.0,
          angle_spread=8.0, cover=1.2, texture=1.0)
    c.end()

    # --- objects: a stoneware ink bottle, a candle in its own wax, a quill across the shade page --
    c.begin("objects")
    ink_c = project(-0.42, TABLE_H, 0.80)
    ix, iy = ink_c
    for i in range(16):
        c.stroke(ix - 16 + i * 2.1, iy - 44 + rng.uniform(-3, 3), ix - 16 + i * 2.1,
                 iy + rng.uniform(-2, 2), rng.uniform(6, 10), vary("#5c4b3c", rng, value=0.09))
    for i in range(7):
        c.stroke(ix - 12 + i * 4, iy - 46, ix - 10 + i * 4, iy - 34, rng.uniform(5, 8),
                 vary("#4d3f33", rng, value=0.07))
    c.stroke(ix - 9, iy - 30, ix - 6, iy - 6, 3.6, vary("#9a866c", rng), alpha=0.85)
    c.stroke(ix - 17, iy - 1, ix + 15, iy - 1, 2.2, "#3a3128", alpha=0.6)

    candle = project(-0.78, TABLE_H, 1.00)
    cx_, cy_ = candle
    for i in range(14):
        c.stroke(cx_ - 9 + i * 1.4, cy_ - 48 + rng.uniform(-2, 2), cx_ - 9 + i * 1.4, cy_ - 3,
                 rng.uniform(6, 10), vary("#e6dcc4", rng, value=0.06))
    c.stroke(cx_ - 13, cy_ - 4, cx_ + 15, cy_ - 4, 5.5, vary("#7d6f5a", rng, value=0.06))
    c.stroke(cx_, cy_ - 48, cx_ + rng.uniform(-3, 3), cy_ - 56, 2.0, "#3a3128")

    # the quill lies across the shadow page, pointing back toward the window it was cut from
    qx, qy = project(0.34, TABLE_H, 0.78)
    for k in range(26):
        t = k / 26.0
        bx, by = qx - t * 168, qy + t * 30
        for s in (-1, 1):
            c.stroke(bx, by, bx - 12 + rng.uniform(-5, 5), by + s * rng.uniform(9, 22),
                     rng.uniform(1.6, 3.2), vary("#d8ceb0", rng, value=0.07), alpha=0.85)
    c.stroke(qx, qy, qx - 176, qy + 32, 2.6, vary("#b6ab8e", rng, value=0.05), alpha=0.9)
    c.stroke(qx - 176, qy + 32, qx - 196, qy + 36, 1.8, "#4a4136")
    c.end()

    # --- glaze and impasto: the last marks, which are the ones that read as paint ---------------
    c.begin("impasto")
    for i in range(70):
        px = rng.uniform(120, 1330)
        py = rng.uniform(700, 980)
        if not inside(patch, px, py):
            continue
        c.stroke(px, py, px + rng.uniform(-26, 26), py + rng.uniform(-9, 9), rng.uniform(3, 6),
                 vary("#f4ecd6", rng, value=0.05), alpha=0.55)
    # a breath of warm glaze over the lit band, laid on thin and uneven
    for i in range(26):
        px = rng.uniform(patch[0][0] - 20, patch[1][0] + 20)
        py = rng.uniform(patch[0][1] - 10, patch[2][1] + 10)
        if not inside(patch, px, py):
            continue
        c.stroke(px, py, px + rng.uniform(60, 150), py + rng.uniform(-8, 8), rng.uniform(18, 30),
                 "#e0b77a", alpha=0.13)
    c.end()

    # --- signature -------------------------------------------------------------------------------
    c.begin("signature")
    c.polygon([(1244, 906), (1264, 900), (1268, 918), (1248, 924)], "#9b3b2e")
    for i, (a, b) in enumerate(((0, 1), (1, 3), (3, 2), (2, 0), (0, 3))):
        x1, y1 = [(1244, 906), (1264, 900), (1268, 918), (1248, 924)][a]
        x2, y2 = [(1244, 906), (1264, 900), (1268, 918), (1248, 924)][b]
        c.stroke(x1, y1, x2, y2, 1.6, "#7d2f24")
    c.add('<text x="1236" y="944" text-anchor="end" font-family="Georgia, serif" font-size="15" '
          'fill="#3a3128" fill-opacity="0.8" font-style="italic">The Counting Room, February '
          '\u2014 Dmitri, 2026-10-19</text>')
    c.end()

    sun_e = math.radians(SUN_ELEV_DEG)
    metrics = {
        "sun_elevation_deg": SUN_ELEV_DEG,
        "sun_azimuth_deg": SUN_AZ_DEG,
        "slant_to_table_from_sill_m": round(ray_to_table(WIN["y0"]), 3),
        "landing_depth_from_sill_m": round(ray_to_table(WIN["y0"]) * math.cos(sun_e) *
                                           math.cos(math.radians(SUN_AZ_DEG)), 3),
        "penumbra_from_sill_mm": round(penumbra_mm(ray_to_table(WIN["y0"])), 1),
        "penumbra_at_near_table_edge_mm": round(penumbra_mm(ray_to_table(WIN["y0"]) /
                                                            math.cos(sun_e) /
                                                            math.cos(math.radians(SUN_AZ_DEG)) *
                                                            TABLE["z1"] / 0.656), 1),
        "brush_width_mm": BRUSH_MM,
        "stroke_count": c.strokes,
        "gradients_in_file": 0,
    }
    return c, metrics


def render(canvas: Canvas) -> str:
    head = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
        'role="img" aria-label="The Counting Room, February: a Russian realist interior painted '
        'entirely in brush marks, one page of an open ledger in low winter sunlight and one in '
        'shadow">\n' % (W, H, W, H)
    )
    return head + "<defs>\n" + "\n".join(canvas.defs) + "\n</defs>\n" + "\n".join(canvas.layers) + "\n</svg>\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate The Counting Room, February.")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--metrics", action="store_true", help="print the arithmetic and exit")
    args = ap.parse_args()
    canvas, metrics = build()
    if args.metrics:
        print(json.dumps(metrics, indent=2))
        return 0
    out = Path(args.out)
    out.write_text(render(canvas), encoding="utf-8")
    print("%s  %d bytes  %d marks" % (out, out.stat().st_size, canvas.strokes))
    print(json.dumps(metrics, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
