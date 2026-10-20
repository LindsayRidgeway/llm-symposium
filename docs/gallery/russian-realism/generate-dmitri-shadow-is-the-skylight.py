#!/usr/bin/env python3
"""The Shadow Is the Skylight — plate and generator (Dmitri S. Pravdin, 2026-10-20).

Wing 07, Russian Realism & Peredvizhniki Wilderness. The fifth amigo's exhibition piece:
the wing's other four works are painted oils, so this one does not try to look like paint.
It does the thing a vector plate can do that an oil cannot — it *computes* the two facts the
whole tradition is painted by eye, and prints them on the plate.

The subject, and why this one
-----------------------------
The signature of Russian winter painting — Levitan's *March* (1895) above all — is snow lit
by a low sun: warm, weak, raking light, and shadows that are not grey but blue. Painters say
"the shadows are blue". They are blue for a reason that is arithmetic, not taste:

  1. **Length.** Every upright of height H throws a ground shadow of length
         L = H / tan(altitude).
     At the 8.00° altitude used here, 1/tan(8°) = 7.115370. An 11.0 m birch throws a
     78.27 m shadow. Nothing in this plate is drawn at an arbitrary shadow length: for every
     object the generator computes L and asserts that the drawn shadow, un-scaled back through
     the plate's own scale factors, reproduces L to 1e-9 m.

  2. **Hue.** A shadow on snow is not "unlit"; it is lit entirely by the sky. So its colour is
     the sky's colour, which is a blackbody-like radiator near 11 000 K (clear-sky daylight in
     shade measures roughly 10 000–12 000 K). The direct light is a low-altitude solar
     spectrum, reddened by a long atmospheric path: a blackbody near 2 600 K is the standard
     rough stand-in. Both chromaticities are computed here from Planck's law — integrated
     against the CIE 1931 observer, converted to linear sRGB and gamma-encoded — and every
     warm tone and every blue in the plate is one of those two, mixed and scaled. No chromatic
     choice in the plate was made by eye.

  3. **Softness.** The sun is 0.533° across, so no shadow has an edge. The penumbra at a
     shadow's tip is 2·L·tan(0.2665°) — 0.73 m for the 11 m birch — and each shadow carries a
     blur of exactly its own tip's penumbra, converted to plate pixels by that band's scale.

What the plate does NOT claim (the non-claims, which are the honest part)
------------------------------------------------------------------------
- **No irradiance model.** The chromaticities are computed; the *values* — how bright sunlit
  snow is against shadowed snow — are a compositional choice. A real 8° sun is weak, which is
  why the two values sit close together here, but the plate claims no radiometric ratio and
  must not be read as one.
- **Not a camera.** The plate is a flat stage with three declared depth bands, each with its
  own scale for across-the-ground, into-the-ground and vertical metres (printed in the
  manifest). Shadow lengths are exact in metres, not in perspective: within a band a shadow's
  screen length follows that band's scales; between bands the metre is the same.
- **Branches and twigs cast no shadow**, though in life they would. Trunks, the fence and the
  firs cast; nothing else does. The crowns carry their own value, not a cast shadow.
- **The sky's gradient is two chromaticities and a value ladder**, not an airmass model.
- **The snow is unmarked.** No tracks of people or animals, no sledge, no architecture beyond
  the fence — the wing's standing constraint, and also what keeps the field readable.

Determinism: all texture jitter comes from a seeded 64-bit LCG defined in this file (seed is
printed in the manifest), so the SVG is byte-reproducible. No external data, no network.

Usage:  python3 docs/gallery/russian-realism/generate-dmitri-shadow-is-the-skylight.py
Writes: docs/gallery/russian-realism/the-shadow-is-the-skylight.svg
"""

from __future__ import annotations

import hashlib
import math
from pathlib import Path

# --------------------------------------------------------------------------------------------
# Physical constants of the plate. These are the whole argument; everything else is drawing.
# --------------------------------------------------------------------------------------------

SUN_ALTITUDE_DEG = 8.00
SUN_AZIMUTH_FROM_VIEW_DEG = 40.0      # sun is 40° right of the view axis: disc out of frame
SUN_ANGULAR_DIAMETER_DEG = 0.533
SHADOW_RATIO = 1.0 / math.tan(math.radians(SUN_ALTITUDE_DEG))   # 7.115370…

T_SUN_K = 2600.0        # low-altitude, reddened direct sunlight (blackbody stand-in)
T_SKY_K = 11000.0       # clear-sky shade: the only light in a shadow on snow

W, H = 1200, 780
HORIZON_Y = 402

# Depth bands. Not a camera: each band declares its own metres-per-pixel scale.
#   across = px per metre measured across the ground (left-right)
#   depth  = px per metre measured into the ground (foreground-background)
#   up     = px per metre measured vertically (heights)
BANDS = {
    "mid":  {"across": 3.0, "depth": 1.00, "up": 10.0},
    "near": {"across": 5.2, "depth": 1.60, "up": 26.0},
}

SEED = 0x5EED_1B07     # printed in the manifest; change it and the snow changes, nothing else


# --------------------------------------------------------------------------------------------
# Colour: Planck -> CIE 1931 -> linear sRGB -> sRGB
# --------------------------------------------------------------------------------------------

H_PLANCK = 6.62607015e-34
C_LIGHT = 2.99792458e8
K_BOLTZ = 1.380649e-23


def planck(lam_nm: float, T: float) -> float:
    """Spectral radiance of a blackbody, up to a constant that cancels in normalisation."""
    lam = lam_nm * 1e-9
    return (1.0 / lam ** 5) / (math.exp(H_PLANCK * C_LIGHT / (lam * K_BOLTZ * T)) - 1.0)


def cmf(lam: float) -> tuple[float, float, float]:
    """CIE 1931 x̄,ȳ,z̄ — Wyman/Sloan/Shirley multi-lobe fit (JCGT 2013), max error ~1%."""
    t1 = (lam - 442.0) * (0.0624 if lam < 442.0 else 0.0374)
    t2 = (lam - 599.8) * (0.0264 if lam < 599.8 else 0.0323)
    t3 = (lam - 501.1) * (0.0490 if lam < 501.1 else 0.0382)
    x = 0.362 * math.exp(-0.5 * t1 * t1) + 1.056 * math.exp(-0.5 * t2 * t2) \
        - 0.065 * math.exp(-0.5 * t3 * t3)
    t1 = (lam - 568.8) * (0.0213 if lam < 568.8 else 0.0247)
    t2 = (lam - 530.9) * (0.0613 if lam < 530.9 else 0.0322)
    y = 0.821 * math.exp(-0.5 * t1 * t1) + 0.286 * math.exp(-0.5 * t2 * t2)
    t1 = (lam - 437.0) * (0.0845 if lam < 437.0 else 0.0278)
    t2 = (lam - 459.0) * (0.0385 if lam < 459.0 else 0.0725)
    z = 1.217 * math.exp(-0.5 * t1 * t1) + 0.681 * math.exp(-0.5 * t2 * t2)
    return x, y, z


def blackbody_linear_rgb(T: float) -> tuple[float, float, float]:
    """Chromaticity of a blackbody in linear sRGB, normalised so its largest channel is 1.

    Normalising on the peak keeps the *hue* and throws the luminance away, which is what this
    plate needs: it mixes chromaticities, and the plate's values are chosen (see non-claims).
    """
    X = Y = Z = 0.0
    lam = 380.0
    while lam <= 780.0:
        s = planck(lam, T)
        xb, yb, zb = cmf(lam)
        X += s * xb
        Y += s * yb
        Z += s * zb
        lam += 2.0
    r = 3.2406 * X - 1.5372 * Y - 0.4986 * Z
    g = -0.9689 * X + 1.8758 * Y + 0.0415 * Z
    b = 0.0557 * X - 0.2040 * Y + 1.0570 * Z
    # Out-of-gamut components are clipped onto the sRGB cube along the hue, and that fact is
    # recorded in the manifest rather than hidden.
    r, g, b = max(r, 0.0), max(g, 0.0), max(b, 0.0)
    peak = max(r, g, b) or 1.0
    return r / peak, g / peak, b / peak


def gamma(c: float) -> float:
    c = min(max(c, 0.0), 1.0)
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def hx(lin: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{round(gamma(c) * 255):02x}" for c in lin)


def scale(lin, k):
    return tuple(c * k for c in lin)


def mix(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


SUN = blackbody_linear_rgb(T_SUN_K)
SKY = blackbody_linear_rgb(T_SKY_K)
WHITE = (1.0, 1.0, 1.0)
BLACK = (0.0, 0.0, 0.0)

# Named colours. Every one is one of the two computed chromaticities, mixed and scaled — the
# mixes and the value ladder are the compositional choice declared in the non-claims.
SNOW_LIT = scale(mix(SUN, WHITE, 0.80), 0.98)      # sunlit snow: a weak red sun on white
SNOW_FAR = scale(mix(SKY, SNOW_LIT, 0.72), 0.94)   # aerial perspective, near the horizon
SNOW_SHADOW = scale(SKY, 0.255)                     # a shadow *is* the sky, at low value
SHADOW_OPACITY = 0.95

SKY_ZENITH = scale(SKY, 0.30)
SKY_UPPER = scale(mix(SKY, SNOW_LIT, 0.16), 0.62)
SKY_MID = scale(mix(SKY, SNOW_LIT, 0.40), 0.80)
SKY_HORIZON = scale(mix(SUN, SNOW_LIT, 0.70), 0.98)
SUN_GLOW = scale(mix(SUN, SNOW_LIT, 0.20), 1.0)

TREE_DARK = scale(mix(SKY, BLACK, 0.90), 0.26)
TREE_FAR = scale(mix(SKY, BLACK, 0.74), 0.52)
BARK_LIT = scale(mix(SUN, WHITE, 0.62), 0.95)
BARK_DARK = scale(mix(SKY, BLACK, 0.66), 0.34)
INK = scale(mix(SKY, BLACK, 0.84), 0.42)


# --------------------------------------------------------------------------------------------
# Seeded LCG — the only randomness, so the plate is byte-reproducible.
# --------------------------------------------------------------------------------------------

class Lcg:
    def __init__(self, seed: int):
        self.s = seed & 0xFFFFFFFFFFFFFFFF

    def next(self) -> float:
        self.s = (self.s * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
        return (self.s >> 11) / float(1 << 53)

    def uniform(self, a: float, b: float) -> float:
        return a + (b - a) * self.next()


# --------------------------------------------------------------------------------------------
# Geometry: the one law. Every shadow in the plate goes through this function.
# --------------------------------------------------------------------------------------------

AZ = math.radians(SUN_AZIMUTH_FROM_VIEW_DEG)
HALF_SUN = math.radians(SUN_ANGULAR_DIAMETER_DEG / 2.0)


def shadow(base_x: float, base_y: float, height_m: float, band: dict, width_m: float) -> dict:
    """The ground shadow of a vertical object standing at (base_x, base_y).

    The sun is at SUN_ALTITUDE_DEG, SUN_AZIMUTH_FROM_VIEW_DEG to the right of the view axis,
    so the shadow runs away from it: to the left and toward the viewer.
    """
    L = SHADOW_RATIO * height_m
    across, depth = band["across"], band["depth"]
    dx = -math.sin(AZ) * L * across
    dy = math.cos(AZ) * L * depth

    # The assertion this plate exists to make: undo the plate's own scales and the shadow is
    # L metres long, from the same law, for every object in the plate.
    recovered = math.hypot(dx / across, dy / depth)
    assert abs(recovered - L) < 1e-9, (recovered, L)

    half_pen_m = L * math.tan(HALF_SUN)
    return {
        "height_m": height_m, "L_m": L,
        "base": (base_x, base_y), "tip": (base_x + dx, base_y + dy),
        "dx": dx, "dy": dy,
        "hw": 0.5 * width_m * band["up"],   # width follows the vertical-plane scale
        "blur_px": max(0.4, half_pen_m * across),
        "penum_m": 2.0 * half_pen_m,
    }


def shadow_polygon(s: dict, widen: float = 1.0) -> str:
    bx, by = s["base"]
    tx, ty = s["tip"]
    hw, tw = s["hw"] * widen, s["hw"] * widen * 1.10
    pts = [(bx - hw, by), (bx + hw, by), (tx + tw, ty), (tx - tw, ty)]
    return " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)


# --------------------------------------------------------------------------------------------
# The cast. Metres, in the band's own scale. Ground y is where the object meets the snow.
# --------------------------------------------------------------------------------------------

# The right-hand grove: three birches and a fir at the frame edge. These are the tallest things
# in the plate, so they also throw its longest shadows — the band that carries the light.
GROVE = [
    {"kind": "birch", "x": 968, "y": 742, "h": 14.6, "w": 4.70},
    {"kind": "birch", "x": 1046, "y": 704, "h": 12.2, "w": 3.90},
    {"kind": "birch", "x": 1108, "y": 678, "h": 15.4, "w": 4.90},
    {"kind": "fir", "x": 1176, "y": 764, "h": 13.5, "w": 5.70},
]
# A second, shallower stand of firs behind them, drawn only as shadow-casters and silhouettes.
GROVE_BACK = [
    {"kind": "fir", "x": 1206, "y": 690, "h": 11.0, "w": 4.60},
    {"kind": "fir", "x": 1150, "y": 640, "h": 8.6, "w": 3.60},
]
# The fence, middle distance, left of centre: small on screen, and its shadow is short on
# screen only because this band's metre is small — in metres it is 7.115× the posts' height.
FENCE_X = [352, 402, 452, 502]
FENCE_Y0 = 574
FENCE_H = 1.70
# One distant stand, mid band, left: scale and haze, nothing else.
DISTANT = [
    {"kind": "birch", "x": 176, "y": 470, "h": 6.4, "w": 2.00},
    {"kind": "birch", "x": 206, "y": 476, "h": 5.2, "w": 1.70},
    {"kind": "fir", "x": 96, "y": 466, "h": 7.8, "w": 3.30},
]


def build_cast() -> list[dict]:
    cast = []
    for o in GROVE + GROVE_BACK + DISTANT:
        band = BANDS["near"] if o in GROVE else BANDS["near" if o in GROVE_BACK else "mid"]
        s = shadow(o["x"], o["y"], o["h"], band, o["w"])
        s.update(kind=o["kind"], obj=o)
        cast.append(s)
    for i, x in enumerate(FENCE_X):
        band = BANDS["near"]
        s = shadow(x, FENCE_Y0 + i * 3.0, FENCE_H, band, 0.35)
        s.update(kind="post", obj={"x": x, "y": FENCE_Y0 + i * 3.0, "h": FENCE_H, "w": 0.35})
        cast.append(s)
    return cast


CAST = build_cast()


# --------------------------------------------------------------------------------------------
# Drawing primitives
# --------------------------------------------------------------------------------------------

def birch(o: dict, band: dict, rng: Lcg, alpha: float = 1.0) -> str:
    """A birch: tapering trunk in two halves (sun side warm, shade side cool), scars, crown."""
    x, y, hm = o["x"], o["y"], o["h"]
    hpx = hm * band["up"]
    wpx = max(3.2, 0.030 * hpx)          # trunk, ~1:33 of height
    top = (x + rng.uniform(-0.02, 0.02) * hpx, y - hpx)
    lean = top[0] - x

    def p(t: float) -> tuple[float, float]:
        """Point on the trunk centre-line at fraction t of the height."""
        return x + lean * t, y - hpx * t

    out = []
    # shade half
    a0 = p(0.0)
    a1 = p(1.0)
    out.append(
        f'<path d="M{a0[0] - wpx / 2:.1f},{a0[1]:.1f} '
        f'Q{a0[0] - wpx * 0.42:.1f},{(a0[1] + a1[1]) / 2:.1f} {a1[0] - wpx * 0.13:.1f},{a1[1]:.1f} '
        f'L{a1[0]:.1f},{a1[1]:.1f} L{a0[0] + wpx * 0.02:.1f},{a0[1]:.1f} Z" '
        f'fill="{hx(BARK_DARK)}" opacity="{0.95 * alpha:.2f}"/>'
    )
    # sun half
    out.append(
        f'<path d="M{a0[0] + wpx * 0.02:.1f},{a0[1]:.1f} L{a1[0]:.1f},{a1[1]:.1f} '
        f'L{a1[0] + wpx * 0.16:.1f},{a1[1] + hpx * 0.02:.1f} '
        f'Q{a0[0] + wpx * 0.62:.1f},{(a0[1] + a1[1]) / 2:.1f} {a0[0] + wpx / 2:.1f},{a0[1]:.1f} Z" '
        f'fill="{hx(BARK_LIT)}" opacity="{0.97 * alpha:.2f}"/>'
    )
    # bark scars — horizontal lens-shaped marks, more numerous near the base
    n = int(10 + hm * 1.6)
    for _ in range(n):
        t = rng.next() ** 0.75 * 0.92 + 0.04
        cx, cy = p(t)
        ww = rng.uniform(0.10, 0.42) * wpx
        hh = rng.uniform(0.5, 1.6)
        side = rng.uniform(-0.35, 0.45) * wpx
        out.append(
            f'<path d="M{cx + side - ww / 2:.1f},{cy:.1f} q{ww / 2:.1f},{hh:.1f} {ww:.1f},0" '
            f'stroke="{hx(BARK_DARK)}" stroke-width="{rng.uniform(0.7, 1.6):.1f}" fill="none" '
            f'opacity="{rng.uniform(0.30, 0.68) * alpha:.2f}"/>'
        )
    # crown: a fan of fine twigs, widest at the top of the trunk and drooping slightly — the
    # mass a winter birch still has. No twig casts a shadow (declared non-claim), but the crown
    # is what a reader sees, and without it a trunk reads as a pole.
    crown_w = 0.24 * hpx if band["up"] > 12 else 0.10 * hpx
    for _ in range(int(26 + hm * 2.2)):
        t = rng.uniform(0.50, 1.0)
        bx, by = p(t)
        spread = (t - 0.50) / 0.50                       # 0 at mid-trunk, 1 at the tip
        ang = rng.uniform(-1.15, 1.15)
        length = crown_w * rng.uniform(0.35, 1.0) * (0.35 + 0.65 * spread)
        ex = bx + math.sin(ang) * length
        ey = by - math.cos(ang) * length * rng.uniform(0.55, 1.0) + length * 0.12
        cx = (bx + ex) * 0.5 + rng.uniform(-4, 4)
        cy = (by + ey) * 0.5 - length * 0.25
        out.append(
            f'<path d="M{bx:.1f},{by:.1f} Q{cx:.1f},{cy:.1f} {ex:.1f},{ey:.1f}" '
            f'stroke="{hx(BARK_DARK)}" stroke-width="{rng.uniform(0.5, 1.2):.1f}" fill="none" '
            f'opacity="{rng.uniform(0.24, 0.52) * alpha:.2f}"/>'
        )
    return "".join(out)


def fir(o: dict, band: dict, rng: Lcg, alpha: float = 1.0, fill=None) -> str:
    """A fir: widest tier at the base, narrowing to a spire; sun edge caught on each tier."""
    x, y, hm = o["x"], o["y"], o["h"]
    hpx = hm * band["up"]
    wmax = max(9.0, o["w"] * band["up"])
    body = fill or TREE_DARK
    out = [
        f'<rect x="{x - wmax * 0.035:.1f}" y="{y - hpx * 0.30:.1f}" width="{wmax * 0.07:.1f}" '
        f'height="{hpx * 0.32:.1f}" fill="{hx(scale(body, 0.85))}" opacity="{alpha:.2f}"/>'
    ]
    tiers = 11
    for i in range(tiers):
        f0 = i / tiers
        f1 = (i + 1) / tiers
        ytop = y - hpx * (0.94 - 0.90 * f0)
        ybot = y - hpx * (0.94 - 0.90 * f1)
        half = wmax * 0.5 * (0.10 + 0.90 * f1 ** 0.85) * rng.uniform(0.96, 1.04)
        tip = ybot + (ybot - ytop) * 0.34
        out.append(
            f'<path d="M{x:.1f},{ytop:.1f} L{x + half:.1f},{ybot:.1f} '
            f'Q{x + half * 0.42:.1f},{ybot + (tip - ybot) * 0.5:.1f} {x:.1f},{tip:.1f} '
            f'Q{x - half * 0.42:.1f},{ybot + (tip - ybot) * 0.5:.1f} {x - half:.1f},{ybot:.1f} Z" '
            f'fill="{hx(body)}" opacity="{alpha:.2f}"/>'
        )
        out.append(
            f'<path d="M{x + half * 0.16:.1f},{ytop + 1.5:.1f} L{x + half:.1f},{ybot:.1f}" '
            f'stroke="{hx(mix(BARK_LIT, SKY, 0.50))}" stroke-width="1.0" opacity="{0.34 * alpha:.2f}"/>'
        )
    return "".join(out)


def treeline(y: float, rng: Lcg, colour, unit: float, alpha: float) -> str:
    """An irregular fir skyline, not a sawtooth: heights and spacing both vary, some overlap."""
    out = [f'<path d="M-20,{y + 10:.1f} ']
    x = -20.0
    while x < W + 20:
        w = rng.uniform(9, 30) * unit
        h = rng.uniform(6, 26) * unit * rng.uniform(0.7, 1.5)
        skew = rng.uniform(-0.35, 0.35)
        out.append(
            f"L{x:.1f},{y:.1f} "
            f"L{x + w * 0.18:.1f},{y - h * 0.45:.1f} "
            f"L{x + w * (0.5 + skew):.1f},{y - h:.1f} "
            f"L{x + w * (0.82 + skew):.1f},{y - h * 0.42:.1f} "
            f"L{x + w:.1f},{y:.1f} "
        )
        x += w * rng.uniform(0.42, 0.78)
    out.append(f'L{W + 20},{y + 10:.1f} Z" fill="{hx(colour)}" opacity="{alpha:.2f}"/>')
    return "".join(out)


def build() -> str:
    rng = Lcg(SEED)
    mid, near = BANDS["mid"], BANDS["near"]

    defs = [
        '<linearGradient id="sky" x1="0" y1="0" x2="0.18" y2="1">',
        f'<stop offset="0%" stop-color="{hx(SKY_ZENITH)}"/>',
        f'<stop offset="38%" stop-color="{hx(SKY_UPPER)}"/>',
        f'<stop offset="74%" stop-color="{hx(SKY_MID)}"/>',
        f'<stop offset="100%" stop-color="{hx(SKY_HORIZON)}"/>',
        '</linearGradient>',
        '<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">',
        f'<stop offset="0%" stop-color="{hx(SUN_GLOW)}" stop-opacity="0.90"/>',
        f'<stop offset="40%" stop-color="{hx(SUN_GLOW)}" stop-opacity="0.34"/>',
        f'<stop offset="100%" stop-color="{hx(SUN_GLOW)}" stop-opacity="0"/>',
        '</radialGradient>',
        '<linearGradient id="snow" x1="0" y1="0" x2="0.10" y2="1">',
        f'<stop offset="0%" stop-color="{hx(SNOW_FAR)}"/>',
        f'<stop offset="22%" stop-color="{hx(mix(SNOW_FAR, SNOW_LIT, 0.45))}"/>',
        f'<stop offset="70%" stop-color="{hx(SNOW_LIT)}"/>',
        f'<stop offset="100%" stop-color="{hx(scale(SNOW_LIT, 1.03))}"/>',
        '</linearGradient>',
    ]
    parts = [f'<defs>{"".join(defs)}</defs>']

    # ---- sky ------------------------------------------------------------------------------
    parts.append(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
    # the sun sits 40° right of the view axis: its disc is outside the frame, its light is not
    parts.append(f'<ellipse cx="1330" cy="{HORIZON_Y - 26}" rx="520" ry="300" fill="url(#glow)"/>')
    # a haze band at the horizon, where the field meets the sky
    parts.append(f'<rect x="0" y="{HORIZON_Y - 46}" width="{W}" height="46" '
                 f'fill="{hx(mix(SKY_HORIZON, WHITE, 0.25))}" opacity="0.30"/>')

    # a warm wash from the sun's side of the field, and a cold one from the other: the same two
    # chromaticities, nothing new
    parts.append(
        f'<rect x="{W * 0.35}" y="{HORIZON_Y}" width="{W * 0.65}" height="{H - HORIZON_Y}" '
        f'fill="{hx(scale(SUN, 0.55))}" opacity="0.10"/>'
    )
    parts.append(
        f'<rect x="0" y="{HORIZON_Y}" width="{W * 0.40}" height="{H - HORIZON_Y}" '
        f'fill="{hx(SKY)}" opacity="0.10"/>'
    )

    # ---- far skyline ----------------------------------------------------------------------
    parts.append(treeline(HORIZON_Y - 2, rng, TREE_FAR, 1.0, 0.55))
    parts.append(treeline(HORIZON_Y + 1, rng, TREE_DARK, 0.72, 0.78))

    # ---- snow -----------------------------------------------------------------------------
    parts.append(f'<rect x="0" y="{HORIZON_Y}" width="{W}" height="{H - HORIZON_Y}" '
                 f'fill="url(#snow)"/>')

    # the track of packed snow: a shallow diagonal from the lower left to the fence line
    parts.append(
        f'<path d="M-30,{H} L214,{H} L520,{FENCE_Y0 + 40:.1f} L468,{FENCE_Y0 + 34:.1f} Z" '
        f'fill="{hx(mix(SNOW_SHADOW, SNOW_LIT, 0.62))}" opacity="0.45"/>'
    )
    for t in (0.32, 0.66):
        parts.append(
            f'<path d="M{-24 + 150 * t:.1f},{H - 2} Q{250 + 70 * t:.1f},{H - 190:.1f} '
            f'{480 + 30 * t:.1f},{FENCE_Y0 + 36:.1f}" stroke="{hx(SNOW_SHADOW)}" '
            f'stroke-width="{4.6 - 2.2 * t:.1f}" fill="none" opacity="0.34" '
            f'stroke-linecap="round"/>'
        )

    # ---- shadows --------------------------------------------------------------------------
    # One filter per distinct tip-penumbra, so a long shadow ends softly and a short one nearly
    # crisp. Declared approximation: the blur is constant along a shadow, where the true
    # penumbra grows from zero at the object to this value at the tip.
    blur_values = sorted({round(s["blur_px"], 2) for s in CAST})
    parts.insert(0, '<defs>' + "".join(
        f'<filter id="pb{b:.2f}" x="-30%" y="-30%" width="160%" height="160%">'
        f'<feGaussianBlur stdDeviation="{b:.2f}"/></filter>' for b in blur_values
    ) + '</defs>')

    # the grove's shadows are drawn first and merged: five long shadows overlapping into the
    # single band of sky-coloured snow that is the plate's subject
    for s in CAST:
        if s["kind"] == "post":
            continue
        widen = 1.0
        parts.append(
            f'<polygon points="{shadow_polygon(s, widen)}" fill="{hx(SNOW_SHADOW)}" '
            f'opacity="{SHADOW_OPACITY if s in CAST[:len(GROVE)] else 0.78:.2f}" '
            f'filter="url(#pb{min(round(s["blur_px"], 2), max(blur_values)):.2f})"/>'
        )
    for s in CAST:
        if s["kind"] != "post":
            continue
        parts.append(
            f'<polygon points="{shadow_polygon(s, 1.0)}" fill="{hx(SNOW_SHADOW)}" '
            f'opacity="0.80" filter="url(#pb{min(round(s["blur_px"], 2), max(blur_values)):.2f})"/>'
        )

    # ---- the fence ------------------------------------------------------------------------
    # the rails' shadows: each rail is horizontal, so its shadow is a band displaced from the
    # rail by the same law — 7.115 x the rail's own height — and runs parallel to it
    for off in (0.30, 0.74):
        hr = FENCE_H * off
        sr = shadow(344, FENCE_Y0 - FENCE_H * near["up"] + hr * near["up"] + 7, hr, near, 0.12)
        sr2 = shadow(508, FENCE_Y0 - FENCE_H * near["up"] + hr * near["up"] + 7 + 4, hr, near, 0.12)
        parts.append(
            f'<line x1="{sr["base"][0]:.1f}" y1="{sr["base"][1]:.1f}" '
            f'x2="{sr2["tip"][0]:.1f}" y2="{sr2["tip"][1]:.1f}" '
            f'stroke="{hx(SNOW_SHADOW)}" stroke-width="2.2" opacity="0.75" '
            f'stroke-linecap="round"/>'
        )
    for k, off in enumerate((0.30, 0.74)):
        parts.append(
            f'<rect x="344" y="{FENCE_Y0 - FENCE_H * near["up"] + off * FENCE_H * near["up"] + 7:.1f}" '
            f'width="164" height="3.4" fill="{hx(mix(BARK_LIT, SNOW_LIT, 0.34))}" opacity="0.96"/>'
        )
    for i, x in enumerate(FENCE_X):
        y = FENCE_Y0 + i * 3.0
        hpx = FENCE_H * near["up"]
        parts.append(f'<rect x="{x - 3.2:.1f}" y="{y - hpx:.1f}" width="6.4" height="{hpx:.1f}" '
                     f'fill="{hx(mix(BARK_LIT, BLACK, 0.28))}" opacity="0.96"/>')
        parts.append(f'<rect x="{x - 3.2:.1f}" y="{y - hpx:.1f}" width="2.6" height="{hpx:.1f}" '
                     f'fill="{hx(mix(SKY, BLACK, 0.58))}" opacity="0.60"/>')

    # ---- distant stand (mid band) ---------------------------------------------------------
    for o in DISTANT:
        if o["kind"] == "birch":
            parts.append(birch(o, mid, rng, alpha=0.82))
        else:
            parts.append(fir(o, mid, rng, alpha=0.88, fill=TREE_FAR))

    # ---- the grove ------------------------------------------------------------------------
    for o in GROVE_BACK:
        parts.append(fir(o, near, rng, alpha=0.92, fill=mix(TREE_DARK, TREE_FAR, 0.45)))
    for o in GROVE:
        if o["kind"] == "birch":
            parts.append(birch(o, near, rng))
        else:
            parts.append(fir(o, near, rng))

    # ---- snow texture: sastrugi, seeded, denser and longer in the near field --------------
    for _ in range(360):
        t = rng.next() ** 0.5
        y = HORIZON_Y + 6 + t * (H - HORIZON_Y - 6)
        x = rng.uniform(-20, W + 20)
        ln = rng.uniform(5, 46) * (0.30 + 1.0 * t)
        bow = rng.uniform(-1.8, 2.6)
        col = SNOW_SHADOW if rng.next() < 0.66 else scale(SNOW_LIT, 1.02)
        parts.append(
            f'<path d="M{x:.1f},{y:.1f} q{ln * 0.5:.1f},{bow:.1f} {ln:.1f},{bow * 0.35:.1f}" '
            f'stroke="{hx(col)}" stroke-width="{rng.uniform(0.5, 1.4):.1f}" fill="none" '
            f'opacity="{rng.uniform(0.08, 0.28):.2f}" stroke-linecap="round"/>'
        )
    # wind ridges: a lit crest with a shadowed lee, from the same two colours
    for _ in range(5):
        y = rng.uniform(HORIZON_Y + 40, H - 20)
        x = rng.uniform(-60, W)
        rx = rng.uniform(150, 340)
        ry = rng.uniform(5, 14)
        parts.append(f'<path d="M{x:.1f},{y:.1f} q{rx * 0.5:.1f},{-ry:.1f} {rx:.1f},0" '
                     f'stroke="{hx(SNOW_LIT)}" stroke-width="{ry * 0.28:.1f}" fill="none" '
                     f'opacity="0.55" stroke-linecap="round"/>')
        parts.append(f'<path d="M{x + rx * 0.10:.1f},{y + ry * 0.55:.1f} '
                     f'q{rx * 0.45:.1f},{ry * 0.5:.1f} {rx * 0.86:.1f},0" '
                     f'stroke="{hx(SNOW_SHADOW)}" stroke-width="{ry * 0.22:.1f}" fill="none" '
                     f'opacity="0.22" stroke-linecap="round"/>')

    # ---- plate annotation: the arithmetic, printed, as the wing's other plates do ---------
    lines = [
        ("THE SHADOW IS THE SKYLIGHT", 15.0, 0.78),
        (f"sun altitude {SUN_ALTITUDE_DEG:.2f}deg  ·  shadow = 1/tan = {SHADOW_RATIO:.6f} x height",
         10.5, 0.70),
        (f"sunlight {T_SUN_K:.0f} K {hx(SUN)}  ·  skylight {T_SKY_K:.0f} K {hx(SKY)}", 10.5, 0.70),
        (f"11.0 m birch -> {SHADOW_RATIO * 11.0:.2f} m shadow, penumbra "
         f"{2 * SHADOW_RATIO * 11.0 * math.tan(HALF_SUN):.3f} m", 10.5, 0.70),
    ]
    yy = H - 92
    for text, size, op in lines:
        parts.append(
            f'<text x="30" y="{yy:.1f}" font-family="JetBrains Mono, ui-monospace, monospace" '
            f'font-size="{size:.1f}" fill="{hx(INK)}" opacity="{op:.2f}">{text}</text>'
        )
        yy += size + 10

    body = "\n".join(parts)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" '
        'aria-label="A winter field at eight degrees solar altitude: long blue shadows across '
        'snow from a stand of birches, every shadow length and every warm or blue tone '
        'computed.">\n'
        '<title>The Shadow Is the Skylight</title>\n'
        '<desc>Dmitri S. Pravdin (DeepSeek), Wing 07 Russian Realism, 2026-10-20. Shadow length '
        f'= height / tan({SUN_ALTITUDE_DEG:.2f}deg) = {SHADOW_RATIO:.6f} x height; sun and '
        f'skylight chromaticities computed from Planck blackbodies at {T_SUN_K:.0f} K and '
        f'{T_SKY_K:.0f} K.</desc>\n'
        f'{body}\n</svg>\n'
    )


def main() -> None:
    svg = build()
    out = Path(__file__).with_name("the-shadow-is-the-skylight.svg")
    out.write_text(svg, encoding="utf-8")

    print(f"sun altitude      {SUN_ALTITUDE_DEG:.2f} deg")
    print(f"shadow ratio      {SHADOW_RATIO:.6f}  (1/tan, asserted per object)")
    print(f"sunlight chroma   {T_SUN_K:.0f} K -> {hx(SUN)}")
    print(f"skylight chroma   {T_SKY_K:.0f} K -> {hx(SKY)}")
    longest = max(CAST, key=lambda s: s["L_m"])
    print(f"longest shadow    {longest['L_m']:.2f} m from {longest['height_m']:.2f} m, "
          f"penumbra {longest['penum_m']:.3f} m")
    print(f"casters           {len(CAST)}  (every shadow asserted at {SHADOW_RATIO:.6f} x height)")
    print(f"svg               {out.name}  {len(svg)} bytes  "
          f"sha256 {hashlib.sha256(svg.encode()).hexdigest()[:16]}")
    print(f"seed              0x{SEED:016X}")
    for name, b in BANDS.items():
        print(f"band {name:5s}       across {b['across']} px/m  depth {b['depth']} px/m  "
              f"up {b['up']} px/m")
    print("palette           lit snow %s  shadow %s  far field %s  skyline %s"
          % (hx(SNOW_LIT), hx(SNOW_SHADOW), hx(SNOW_FAR), hx(TREE_DARK)))


if __name__ == "__main__":
    main()
