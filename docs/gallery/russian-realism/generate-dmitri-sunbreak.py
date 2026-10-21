#!/usr/bin/env python3
"""Procedural generator: The Edge of the Sunbreak (Dmitri, DeepSeek-Symposium, 2026-10-18).

Wing 07 (Russian realism). The fifth amigo's cell — the last one of the seven that was still
empty after the maori cell was filled on 2026-10-16.

Why this subject, and what is being claimed
-------------------------------------------
Russian realism claims "deep atmospheric perspective" and *nastroenie*. Both are usually
painted by eye. A flat snowfield with one break of sun in an overcast deck is a subject
where the eye is not needed: the two things that make the picture — where the light stops,
and how softly it stops — are set by the sun's elevation, the cloud base, and the angular
size of the sun's disc. Those are three numbers, and this plate computes all three rather
than guessing at them. Every claim below is asserted in `tests/test_gallery_russian_realism_dmitri.py`.

The geometry, in full
---------------------
The deck is a flat sheet at altitude h_c. The sun's centre is at elevation e. A ray of
elevation a reaches the deck at horizontal distance h_c*cot(a). So the sun's disc — which
spans elevations [e-theta, e+theta], theta = 0.266 deg being the solar angular radius —
paints the cloud plane over the interval

    [D_lo, D_hi] = [h_c*cot(e+theta), h_c*cot(e-theta)],      width W = 13.06 m at h_c = 250 m.

A single straight edge of cloud at cloud-plane distance A throws its shadow on the ground at
ground distance A - h_c*cot(e); the *penumbra* is the interval the disc paints, and its full
width on the ground is exactly

    W = h_c * [cot(e - theta) - cot(e + theta)]

which is the only softness in this picture. It is not a blur: it is the circle of the sun,
partly hidden, and the visible fraction of the disc at a point x past the edge is the
circular-segment area

    f(u) = [arccos u - u*sqrt(1-u^2)] / pi,   u = (x - x_edge)/ (W/2),

so f = 1/2 exactly at the geometric edge, f = 1 half a penumbra inside the light, f = 0 half
a penumbra inside the shadow. Every value of light on the field in this plate comes from
that function; nothing is graded by hand.

The chosen sky
--------------
Latitude 55.75 N, solar declination -9.2 deg (mid-October) gives a noon elevation of
e = 90 - 55.75 - 9.2 = 25.05 deg. With h_c = 250 m — a low winter stratocumulus base —
h_c*cot(e) = 535.2 m. The hole in the deck is placed at cloud-plane distance [530, 556] m,
which puts the near edge of the light at ground distance -5.2 m (behind the camera, so the
foreground of the plate is fully sunlit) and the far edge at 20.8 m, with its penumbra
running from 14.3 m to 27.4 m. The near edge of a lit patch is therefore *behind* the
viewer, which is why this plate shows one edge and not two, and why the bright band does not
run out of frame.

The sun itself: the camera's own line of sight to the sun crosses the deck at 535.2 m,
inside the hole [530, 556] — so the sun *is* visible from the camera, and is drawn, at a
drawn radius of f*tan(theta) = 4.41 px. It is a small hole: 1.06 deg tall against a solar
diameter of 0.53 deg, so the disc sits in it with about a quarter of a degree of margin.

What is not modelled, said rather than hidden
---------------------------------------------
  * cloud raggedness. The hole here is two straight edges, so the edge of the light on the
    snow is a straight line in the picture. A real gap in a real deck is frayed; that is the
    one visible difference between this plate and the moment it describes.
  * multiple scattering in the deck. The sky is a declared gradient with no radiative-
    transfer solution behind it — it is the *field* that is computed, not the sky. The one
    sky number that is physical is the 4.7% of airlight at the treeline: exp(-1200/25000)
    for a 25 km clear-air scale, i.e. at 1.2 km there is almost no aerial perspective, and
    the wing's "deep atmospheric perspective" is a claim about detail and value compression,
    not about scattering. The treeline here is drawn at the computed 4.7%, and it stays dark.
  * the snow's own texture. Sastrugi ridges and stubble are drawn in world coordinates and
    projected, so their spacing is right, but their shapes are a drawing, not a measurement.

Colour is computed in linear light and encoded with the sRGB transfer function: direct sun
is warm (5900 K-ish), the overcast sky is blue-dominant, so the shadowed snow comes out blue
and the sunlit snow comes out warm white. The ratio between them is E_sky/(E_direct*sin e +
E_sky), a stated number, not a taste.

Pure standalone SVG output; deterministic, no RNG, no clock, no external assets.
"""

from __future__ import annotations

import math
from pathlib import Path

# ----------------------------------------------------------------------------- the numbers
W = 1600
H = 1000
CX = 800.0
HORIZON = 500.0          # screen row of the horizon (camera pitch 0)
FOCAL = 950.0            # px; 1600 px wide is about 56 deg horizontally
CAM_HEIGHT = 1.6         # m, eye height above the snow

LATITUDE = 55.75         # Moscow, deg N
DECLINATION = -9.20      # mid-October, deg
SUN_ELEVATION = 90.0 - LATITUDE + DECLINATION      # deg, 25.05
THETA_SUN = 15.99 / 60.0                            # deg, solar angular radius (16')

CLOUD_BASE = 250.0       # m
HOLE_NEAR = 530.0        # m, cloud-plane distance of the hole's near edge
HOLE_FAR = 556.0         # m, and its far edge

AIR_SCALE = 25000.0      # m, clear-air extinction scale (25 km visibility)
TREELINE = 1200.0        # m
TREE_TALLEST = 26.0      # m

E_DIRECT = 1.0           # direct normal irradiance, arbitrary units
E_SKY = 0.17             # diffuse horizontal / direct normal, clear-sky order of magnitude
SUN_RGB = (1.000, 0.955, 0.870)     # linear, direct sun through the atmosphere: warm
SKY_RGB = (0.620, 0.760, 1.000)     # linear, overcast sky: blue-dominant
SNOW_RGB = (0.880, 0.900, 0.930)    # snow albedo, slightly higher in the blue (fresh snow)
SKY_RADIANCE = 0.24      # linear radiance scale of the sky at the horizon
GAIN = 5.6               # exposure; chosen so sunlit snow encodes to ~0.95 and no channel clips

PAPER = "#f2efe6"
INK = "#20202a"
INK_SOFT = "#4a4a58"
ACCENT = "#8b7cf6"       # the fifth amigo's colour in the matrix

SNOW_SURFACE = "#eef1f6"
DECK = "#8f96a6"


# --------------------------------------------------------------------- the small geometry
def cot(deg: float) -> float:
    return 1.0 / math.tan(math.radians(deg))


def shadow_offset() -> float:
    """Horizontal distance at which the sun's centre ray reaches the cloud base, m."""
    return CLOUD_BASE * cot(SUN_ELEVATION)


def penumbra_half_width() -> float:
    """Half the width of the sun's disc painted on the ground, m."""
    return 0.5 * CLOUD_BASE * (cot(SUN_ELEVATION - THETA_SUN) - cot(SUN_ELEVATION + THETA_SUN))


def penumbra_width() -> float:
    return 2.0 * penumbra_half_width()


def lit_edges() -> tuple[float, float]:
    """Ground distances (m) of the two edges of the lit patch: near edge, far edge."""
    off = shadow_offset()
    return HOLE_NEAR - off, HOLE_FAR - off


def ground_depth(row: float) -> float:
    """Depth (m) of the flat snow at screen row `row`: d = f*h/(row - horizon)."""
    return FOCAL * CAM_HEIGHT / (row - HORIZON)


def ground_row(depth: float) -> float:
    return HORIZON + FOCAL * CAM_HEIGHT / depth


def chord_fraction(u: float) -> float:
    """Visible fraction of the solar disc past a straight edge, offset u in disc radii."""
    if u >= 1.0:
        return 0.0
    if u <= -1.0:
        return 1.0
    return (math.acos(u) - u * math.sqrt(1.0 - u * u)) / math.pi


def sun_fraction(depth: float) -> float:
    """Fraction of the sun's disc that reaches the ground at ground distance `depth`."""
    r = penumbra_half_width()
    near, far = lit_edges()
    # Both edges are compared on the ground, where the cloud-plane distances differ from
    # these by the same h_c*cot(e), so the offset cancels and is not written out here.
    past_near = chord_fraction((near - depth) / r)
    past_far = chord_fraction((depth - far) / r)
    return min(past_near, past_far)


def sun_screen() -> tuple[float, float, float]:
    """Sun centre (x, y) px and drawn disc radius px. Straight ahead, elevation e."""
    y = HORIZON - FOCAL * math.tan(math.radians(SUN_ELEVATION))
    r = FOCAL * math.tan(math.radians(THETA_SUN))
    return CX, y, r


def tree_height_px(height_m: float, at_distance: float) -> float:
    return FOCAL * height_m / at_distance


def project(x_m: float, depth_m: float) -> tuple[float, float]:
    """Project a ground point (lateral offset, depth) to screen."""
    return CX + FOCAL * x_m / depth_m, HORIZON + FOCAL * CAM_HEIGHT / depth_m


# ------------------------------------------------------------------------- the light maths
def _encode(linear: float) -> float:
    """Linear radiance -> sRGB, clamped."""
    x = max(0.0, min(1.0, linear))
    s = 12.92 * x if x <= 0.0031308 else 1.055 * (x ** (1.0 / 2.4)) - 0.055
    return max(0.0, min(1.0, s))


def _hex(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{int(round(_encode(c) * 255)):02x}" for c in rgb)


def sky_radiance(row: float) -> tuple[float, float, float]:
    """Declared overcast gradient: brighter overhead, dimmer toward the horizon."""
    above = max(0.0, HORIZON - row) / HORIZON
    scale = SKY_RADIANCE * (0.62 + 0.38 * math.sqrt(above))
    return tuple(scale * c for c in SKY_RGB)


def ground_radiance(fraction: float, depth: float) -> tuple[float, float, float]:
    """Reflected radiance of the snow, with the airlight of the path to it mixed in."""
    sin_e = math.sin(math.radians(SUN_ELEVATION))
    out = []
    for albedo, sun, sky in zip(SNOW_RGB, SUN_RGB, SKY_RGB):
        irradiance = E_DIRECT * fraction * sin_e * sun + E_SKY * sky
        out.append(albedo * irradiance / math.pi * GAIN)
    transmittance = math.exp(-depth / AIR_SCALE)
    air = sky_radiance(HORIZON)          # the sky behind the field is the airlight
    return tuple(t * obj + (1.0 - t) * a for t, obj, a in zip([transmittance] * 3, out, air))


def tree_colour(depth: float) -> str:
    """A winter conifer under overcast: near-black, with the airlight of its distance."""
    shadowed = ground_radiance(0.0, 0.0)
    base = [0.145 * c for c in shadowed]
    transmittance = math.exp(-depth / AIR_SCALE)
    air = sky_radiance(HORIZON)
    return _hex(tuple(t * b + (1.0 - t) * a for t, b, a in zip([transmittance] * 3, base, air)))


# --------------------------------------------------------------------------------- the SVG
def _sky(svg: list[str]) -> None:
    sx, sy, sr = sun_screen()
    svg.append(
        f'<defs>'
        f'<linearGradient id="deck" x1="0" y1="0" x2="0" y2="{HORIZON}" '
        f'gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="{_hex(sky_radiance(0))}"/>'
        f'<stop offset="0.55" stop-color="{_hex(sky_radiance(HORIZON * 0.45))}"/>'
        f'<stop offset="1" stop-color="{_hex(sky_radiance(HORIZON))}"/>'
        f'</linearGradient>'
        f'<radialGradient id="blaze" cx="{sx}" cy="{sy}" r="{sr * 10:.1f}" '
        f'gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="#ffffff" stop-opacity="0.92"/>'
        f'<stop offset="0.22" stop-color="#fff6e2" stop-opacity="0.55"/>'
        f'<stop offset="0.6" stop-color="#f3e6d2" stop-opacity="0.18"/>'
        f'<stop offset="1" stop-color="#f3e6d2" stop-opacity="0"/>'
        f'</radialGradient>'
        f'</defs>'
    )
    svg.append(f'<rect x="0" y="0" width="{W}" height="{HORIZON:.0f}" fill="url(#deck)"/>')

    # The deck's folds. Not modelled — a declared drawing, at a value that keeps the sky a
    # sky rather than a wash. Four bands, deterministic, no RNG.
    for k, (y0, amp, tone, op) in enumerate(
        [(70.0, 26.0, "#ffffff", 0.05), (188.0, 34.0, "#3b4354", 0.10),
         (300.0, 30.0, "#ffffff", 0.04), (410.0, 22.0, "#3b4354", 0.08)]
    ):
        pts = []
        for i in range(41):
            x = W * i / 40.0
            y = y0 + amp * math.sin(1.7 * i + 2.1 * k) + 0.55 * amp * math.sin(4.3 * i - k)
            pts.append((x, y))
        d = ("M" + "L".join(f"{p[0]:.1f} {p[1]:.1f}" for p in pts)
             + f"L{W} {HORIZON:.0f}L0 {HORIZON:.0f}Z")
        svg.append(f'<path d="{d}" fill="{tone}" opacity="{op}"/>')

    # The hole: the sun's disc painted on the deck, plus a little margin. Its edges are the
    # same two numbers that put the edge of the light on the snow.
    # A hole edge at cloud-plane distance A appears at elevation atan(h_c/A), and a small
    # angle projects to FOCAL*tan(angle) px above the horizon.
    hole_top = HORIZON - FOCAL * math.tan(math.atan(CLOUD_BASE / HOLE_NEAR))
    hole_bottom = HORIZON - FOCAL * math.tan(math.atan(CLOUD_BASE / HOLE_FAR))
    half_w = (hole_bottom - hole_top) * 1.15
    svg.append(
        f'<path d="M{sx - half_w:.1f} {hole_top:.1f}'
        f'Q{sx - half_w * 0.55:.1f} {hole_top - 3.0:.1f} {sx:.1f} {hole_top - 2.0:.1f}'
        f'Q{sx + half_w * 0.6:.1f} {hole_top + 1.5:.1f} {sx + half_w:.1f} {hole_top + 2.5:.1f}'
        f'L{sx + half_w * 1.05:.1f} {hole_bottom:.1f}'
        f'Q{sx + half_w * 0.5:.1f} {hole_bottom + 3.5:.1f} {sx + 1.5:.1f} {hole_bottom + 2.0:.1f}'
        f'Q{sx - half_w * 0.5:.1f} {hole_bottom + 1.0:.1f} {sx - half_w * 1.05:.1f} {hole_bottom - 1.5:.1f}Z" '
        f'fill="#fdfaf2" opacity="0.96"/>'
    )
    svg.append(
        f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{sr * 10:.1f}" fill="url(#blaze)"/>'
        f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{sr:.2f}" fill="#fffdf8"/>'
    )


def _field(svg: list[str]) -> None:
    first = int(math.ceil(HORIZON)) + 1
    for row in range(first, H + 1):
        depth = ground_depth(row)
        colour = _hex(ground_radiance(sun_fraction(depth), depth))
        svg.append(f'<rect x="0" y="{row}" width="{W}" height="1" fill="{colour}"/>')


def _sastrugi(svg: list[str]) -> None:
    """Wind ridges in world coordinates, projected: their spacing is the perspective's."""
    near, far = lit_edges()
    lit_from = near + penumbra_half_width()          # behind the camera; keep the drawing honest
    lit_to = far - penumbra_half_width()
    top = max(lit_from, ground_row(H))               # nearest depth on screen
    steps = 26
    for k in range(steps):
        frac = k / (steps - 1.0)
        depth0 = top + (lit_to - top) * (frac ** 1.35)
        pts = []
        half = depth0 * CX / FOCAL + 60.0
        for i in range(29):
            x = -half + 2.0 * half * i / 28.0
            wobble = 0.085 * math.sin(2.9 * x + 1.7 * k) + 0.05 * math.sin(6.1 * x - 0.4 * k)
            d = depth0 + wobble
            if d <= 0.4:
                continue
            pts.append(project(x, d))
        if len(pts) < 2:
            continue
        d_path = "M" + "L".join(f"{p[0]:.1f} {p[1]:.1f}" for p in pts)
        svg.append(
            f'<path d="{d_path}" fill="none" stroke="#ffffff" stroke-width="1.1" '
            f'opacity="{0.30 - 0.16 * frac:.3f}" stroke-linecap="round"/>'
        )
        d_path2 = "M" + "L".join(f"{p[0]:.1f} {p[1] + 1.6:.1f}" for p in pts)
        svg.append(
            f'<path d="{d_path2}" fill="none" stroke="#9aa4bb" stroke-width="1.0" '
            f'opacity="{0.22 - 0.12 * frac:.3f}" stroke-linecap="round"/>'
        )


def _stubble(svg: list[str]) -> None:
    """Last year's grass through the snow, near enough to be counted."""
    for k in range(34):
        frac = (k * 0.6180339887) % 1.0
        depth = 3.2 + 8.2 * frac
        lateral = (-0.5 + ((k * 0.7548776662) % 1.0)) * 1.55 * depth * CX / FOCAL
        x, y = project(lateral, depth)
        h_px = tree_height_px(0.10 + 0.09 * ((k * 0.4142135) % 1.0), depth)
        lean = (-1.0 + 2.0 * ((k * 0.3183099) % 1.0)) * h_px * 0.28
        svg.append(
            f'<path d="M{x:.1f} {y:.1f}Q{x + lean * 0.5:.1f} {y - h_px * 0.6:.1f} '
            f'{x + lean:.1f} {y - h_px:.1f}" fill="none" stroke="#4c4a52" '
            f'stroke-width="{max(0.7, 34.0 / depth):.2f}" opacity="{0.26 + 0.30 * frac:.3f}"/>'
        )


def _treeline(svg: list[str]) -> None:
    """Conifers at 1.2 km: 16-20 px tall, and dark, because there is no haze to lift them."""
    colour = tree_colour(TREELINE)
    tallest = tree_height_px(TREE_TALLEST, TREELINE)
    pts = [(0.0, HORIZON + 1.0)]
    x = 0.0
    k = 0
    while x < W:
        h = tallest * (0.55 + 0.45 * ((k * 0.6180339887) % 1.0))
        w = 5.0 + 4.0 * ((k * 0.7548776662) % 1.0)
        pts.append((x, HORIZON + 1.0))
        pts.append((x + w * 0.5, HORIZON + 1.0 - h))
        pts.append((x + w, HORIZON + 1.0))
        x += w * (0.75 + 0.5 * ((k * 0.4142135) % 1.0))
        k += 1
    pts.append((W, HORIZON + 1.0))
    d = "M" + "L".join(f"{p[0]:.1f} {p[1]:.1f}" for p in pts) + "Z"
    svg.append(f'<path d="{d}" fill="{colour}"/>')

    # One bare birch at 260 m for scale: 12 m of tree, 44 px on the plate.
    bx, by = project(-7.4, 260.0)
    bh = tree_height_px(12.0, 260.0)
    svg.append(
        f'<path d="M{bx:.1f} {by:.1f}Q{bx - 1.2:.1f} {by - bh * 0.55:.1f} '
        f'{bx - 2.4:.1f} {by - bh:.1f}" fill="none" stroke="{colour}" '
        f'stroke-width="1.6" stroke-linecap="round"/>'
        f'<path d="M{bx - 1.1:.1f} {by - bh * 0.48:.1f}L{bx - 7.0:.1f} {by - bh * 0.86:.1f}'
        f'M{bx - 1.7:.1f} {by - bh * 0.66:.1f}L{bx + 4.2:.1f} {by - bh * 1.02:.1f}'
        f'M{bx - 2.2:.1f} {by - bh * 0.82:.1f}L{bx - 6.0:.1f} {by - bh * 1.08:.1f}" '
        f'fill="none" stroke="{colour}" stroke-width="1.0" opacity="0.9"/>'
    )


def _annotation(svg: list[str]) -> None:
    """The measured span: the whole of the softness in this picture, with its number."""
    _near, far = lit_edges()
    half = penumbra_half_width()
    # Only the far edge is in the picture: the near edge of the lit patch falls behind the
    # camera, which is the geometry's way of saying the foreground is all in the sun.
    y_in = ground_row(far - half)
    y_out = ground_row(far + half)
    x = W - 92.0
    svg.append(
        f'<g stroke="{ACCENT}" fill="none" stroke-width="1.4">'
        f'<path d="M{x} {y_in:.1f}H{x + 46:.1f}"/><path d="M{x} {y_out:.1f}H{x + 46:.1f}"/>'
        f'<path d="M{x + 23:.1f} {y_in:.1f}V{y_out:.1f}"/>'
        f'<path d="M{x + 17:.1f} {y_in + 4:.1f}L{x + 23:.1f} {y_in:.1f}L{x + 29:.1f} {y_in + 4:.1f}"/>'
        f'<path d="M{x + 17:.1f} {y_out - 4:.1f}L{x + 23:.1f} {y_out:.1f}L{x + 29:.1f} {y_out - 4:.1f}"/>'
        f'</g>'
        f'<text x="{x + 56:.1f}" y="{(y_in + y_out) / 2 + 6:.1f}" '
        f'font-family="JetBrains Mono, monospace" font-size="19" fill="{ACCENT}">'
        f'{penumbra_width():.2f} m</text>'
    )


def build_svg() -> str:
    svg: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-label="The Edge of the Sunbreak: a flat snowfield under a low '
        f'overcast deck, with one break of sun. The far edge of the sunlight, and the width of '
        f'the softness at that edge, are computed from the solar elevation, the cloud base and '
        f'the angular size of the sun, not painted by eye.">'
    ]
    _sky(svg)
    _field(svg)
    _sastrugi(svg)
    _stubble(svg)
    _treeline(svg)
    _annotation(svg)

    # Title block, in the deck where there is room for it.
    svg.append(
        f'<text x="60" y="150" font-family="Newsreader, Georgia, serif" font-size="56" '
        f'fill="{PAPER}" opacity="0.96">The Edge of the Sunbreak</text>'
    )
    svg.append(
        f'<text x="60" y="196" font-family="Newsreader, Georgia, serif" font-style="italic" '
        f'font-size="25" fill="{PAPER}" opacity="0.82">'
        f'where the light stops on the snow, {lit_edges()[1] - penumbra_half_width():.1f} m '
        f'to {lit_edges()[1] + penumbra_half_width():.1f} m</text>'
    )
    near, far = lit_edges()
    half = penumbra_half_width()
    svg.append(
        f'<text x="60" y="{H - 96}" font-family="JetBrains Mono, monospace" font-size="14" '
        f'fill="{INK}" opacity="0.72">'
        f'e = {SUN_ELEVATION:.2f}\u00b0   h\u1d04 = {CLOUD_BASE:.0f} m   '
        f'\u03b8\u2299 = {THETA_SUN:.3f}\u00b0   H\u2081 = {near:.1f} m   H\u2082 = {far:.1f} m</text>'
    )
    svg.append(
        f'<text x="60" y="{H - 74}" font-family="JetBrains Mono, monospace" font-size="14" '
        f'fill="{INK}" opacity="0.72">'
        f'penumbra = h\u1d04[cot(e\u2212\u03b8) \u2212 cot(e+\u03b8)] = '
        f'{penumbra_width():.2f} m, over {W} px of field</text>'
    )

    # Signature block, the house style of the fifth amigo's plates.
    svg.append(
        f'<text x="60" y="{H - 44}" font-family="Georgia, serif" font-size="24" '
        f'font-style="italic" fill="{INK}">Dmitri S. Pravdin</text>'
    )
    svg.append(
        f'<text x="60" y="{H - 20}" font-family="JetBrains Mono, monospace" font-size="12" '
        f'fill="{INK_SOFT}" opacity="0.85" letter-spacing="1.5">'
        f'PROCEDURAL SVG \u2022 2026-10-18 \u2022 SUNBREAK</text>'
    )
    svg.append(
        f'<rect x="{W - 148}" y="{H - 130}" width="80" height="80" rx="7" '
        f'fill="{ACCENT}" opacity="0.92"/>'
    )
    svg.append(
        f'<text x="{W - 108}" y="{H - 78}" font-family="Georgia, serif" font-size="34" '
        f'fill="{PAPER}" text-anchor="middle">\u0414</text>'
    )
    svg.append("</svg>")
    return "\n".join(svg) + "\n"


if __name__ == "__main__":
    # Archived as a study, not an exhibition piece (2026-10-21): the arithmetic is exact
    # and the image does not carry it. Studies live in studies/<amigo>/, so the pavilion
    # gate can tell an unshown study from a work that landed and was forgotten.
    out = Path(__file__).with_name("studies") / "dmitri" / "the-edge-of-the-sunbreak.svg"
    out.write_text(build_svg(), encoding="utf-8")
    near, far = lit_edges()
    half = penumbra_half_width()
    print(f"wrote {out.name}: {out.stat().st_size} bytes")
    print(f"  e = {SUN_ELEVATION:.3f} deg, h_c = {CLOUD_BASE:.0f} m")
    print(f"  shadow offset = {shadow_offset():.2f} m, penumbra = {penumbra_width():.3f} m "
          f"(+/- {half:.3f})")
    print(f"  lit patch on the ground: {near:.2f} m .. {far:.2f} m")
    print(f"  penumbra rows: {ground_row(near + half):.1f} .. {ground_row(far - half):.1f}")
    print(f"  sun at ({sun_screen()[0]:.1f}, {sun_screen()[1]:.1f}) px, r = {sun_screen()[2]:.2f} px")
