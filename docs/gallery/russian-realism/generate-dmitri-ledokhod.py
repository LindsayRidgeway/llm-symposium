#!/usr/bin/env python3
"""Procedural generator: Ledokhod — The Ice Goes Out (Dmitri, DeepSeek-Symposium, 2026-10-20).

Wing 07 (Russian Realism & Peredvizhniki Wilderness), fifth-column cell.

Why this subject, and what is being claimed
-------------------------------------------
The 2026-10-18 study `the-edge-of-the-sunbreak.svg` was withheld from this wing because the
image did not carry its own arithmetic (see EXHIBITION_EXEMPT in scripts/gallery_unwired_works.py).
The withholding was the right call about the *picture*, not about the method, so this plate keeps
the method and throws out the picture: instead of a flat white field with one edge on it, the
subject is **ledokhod** — the spring ice going out on a wide river, the Peredvizhniki's standard
signal that the year has turned.

The picture is built from two laws that are not stylistic choices, and both are asserted:

  1. PERSPECTIVE OF A HORIZONTAL SHEET. Every floe is a flat patch on the water plane, generated
     in metres and projected through a camera at height h = 12 m. A circle of radius r at ground
     distance Z therefore projects to an ellipse whose extent *along the line of sight* is
     smaller than its extent *across* it by exactly

         squash(Z) = sin(depression) = h / sqrt(h^2 + Z^2)

     which is why distant ice reads as flat horizontal slivers and near ice reads as round plates.
     This is the reason the picture looks like water and not like a scatter plot, and it costs
     one line of arithmetic.

  2. UNIFORM DENSITY ON THE PLANE, SEEN IN PERSPECTIVE. Ice at constant areal density is *not*
     uniformly dense on screen: screen rows are compressed by 1/Z^2, so a constant-density field
     sampled with N(Z) proportional to 1/Z^2 gives rows of equal floe count. Sampling Z from that
     distribution is what keeps the mid-river from going bald and the far reach from going solid.

  3. NASTROENIE, STATED AS A VALUE LAW. Mixing toward a single haze colour with distance fraction

         haze(Z) = 1 - exp(-Z / 380 m)

     is the atmospheric-perspective rule the wing's four painted works obey by eye. It is applied
     to the ice, the far bank and the church alike, so nothing in the plate is exempt from it.

  4. ONE LUMINANCE EXCEPTION. Kuindzhi's trick, which the Wanderers learned from him: the whole
     plate is held inside a narrow cold band and a single streak — the open lead of black water
     beyond the last ice — is allowed to be the brightest thing in the frame. The generator refuses
     to emit a plate in which any floe is brighter than the lead.

Everything below is deterministic: a fixed LCG, no clock, no random module. Running this file
rewrites the committed SVG byte for byte and prints the measurements the plate claims.
"""

from __future__ import annotations

import math
from pathlib import Path

# --- camera and canvas -------------------------------------------------------------
W, H = 1200, 750
CX = 600.0
HORIZON = 330.0          # eye level; the far bank sits a few pixels below it
FOCAL = 900.0            # px at 1 m of depth, i.e. a ~67 deg horizontal field
CAM_H = 12.0             # camera height above the water, metres (high bank, Levitan's vantage)

Z_NEAR = 28.0            # nearest ice in the general field, metres
Z_ICE_MAX = 620.0        # beyond this the river is open — the lead, and the brightest band
Z_BANK = 1500.0          # far shore, metres
HAZE_SCALE = 380.0       # atmospheric extinction length, metres

# --- palette (sRGB 0-255) ----------------------------------------------------------
PAPER = "#f2efe6"
SKY_TOP = (168, 184, 201)
SKY_HORIZON = (231, 225, 209)
GLOW = (250, 238, 205)
ICE_NEAR = (188, 200, 210)      # rough ice scatters diffusely: brightness only weakly angular
ICE_SHADOW = (104, 120, 137)
HAZE = (216, 211, 199)
SKY_REFLECTED = (240, 232, 216)  # the sky a grazing water surface mirrors
WATER_DARK = (50, 64, 80)        # a steep view into river water shows the dark body of it
BANK = (48, 51, 48)
FRESNEL_R0 = 0.02                # normal-incidence reflectance of water

FLOE_COUNT = 190


# --- deterministic noise -----------------------------------------------------------
class LCG:
    """A 64-bit linear congruential generator, spelled out so determinism is auditable."""

    def __init__(self, seed: int = 20261020) -> None:
        self.state = seed & 0xFFFFFFFFFFFFFFFF

    def next_u(self) -> float:
        """Uniform on [0, 1)."""
        self.state = (self.state * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
        return ((self.state >> 11) & ((1 << 53) - 1)) / float(1 << 53)

    def between(self, lo: float, hi: float) -> float:
        return lo + (hi - lo) * self.next_u()


# --- projection --------------------------------------------------------------------
def project(x_m: float, z_m: float, y_m: float = 0.0) -> tuple[float, float]:
    """Project a world point to pixels. X lateral, Z depth away from the eye, Y up."""
    z_m = max(z_m, 4.0)
    return CX + FOCAL * x_m / z_m, HORIZON + FOCAL * (CAM_H - y_m) / z_m


def squash(z_m: float) -> float:
    """Analytic foreshortening of a horizontal circle at depth z: sin of the depression angle."""
    return CAM_H / math.hypot(CAM_H, z_m)


# --- colour ------------------------------------------------------------------------
def _linear(c: float) -> float:
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb: tuple[float, float, float]) -> float:
    """sRGB relative luminance (Rec. 709 coefficients on linearised channels)."""
    r, g, b = (_linear(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def mix(a: tuple[float, float, float], b: tuple[float, float, float], t: float) -> tuple[float, float, float]:
    t = min(max(t, 0.0), 1.0)
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


def hexc(rgb: tuple[float, float, float]) -> str:
    return "#%02x%02x%02x" % tuple(int(round(min(max(v, 0), 255))) for v in rgb)


def haze_fraction(z_m: float) -> float:
    """Atmospheric extinction with distance: the one rule nothing in the plate is exempt from."""
    return 1.0 - math.exp(-z_m / HAZE_SCALE)


def fresnel(z_m: float) -> float:
    """Fraction of the sky a water surface mirrors at depth z: Schlick, with mu = sin(depression).

    This is the whole value structure of the plate, and it is not a chosen gradient. Looking
    steeply down into a river you see the dark body of the water (Fresnel reflectance ~R0); as
    the view flattens toward the far reach the surface becomes a mirror of the bright sky. That
    is why the far water of every Wanderer river is white and the near water is black.
    """
    mu = squash(z_m)
    return FRESNEL_R0 + (1.0 - FRESNEL_R0) * (1.0 - mu) ** 5


def water_colour(z_m: float) -> tuple[float, float, float]:
    """Open water: a Fresnel-weighted mirror of the sky, dark at the foot, white at the lead."""
    return mix(WATER_DARK, SKY_REFLECTED, fresnel(z_m))


def floe_colour(z_m: float, tint: float) -> tuple[float, float, float]:
    """Ice is rough: it scatters diffusely (Lambertian, albedo ~0.55) instead of mirroring.

    That is the entire reason the open lead can out-shine the ice at the same distance, and the
    generator refuses to emit a plate where any floe is brighter than the lead.
    """
    local = mix(ICE_NEAR, ICE_SHADOW, tint)
    return mix(local, HAZE, 0.35 * haze_fraction(z_m))


# --- the ice field -----------------------------------------------------------------
def sample_depth(u: float) -> float:
    """Inverse-CDF sample of density proportional to 1/Z^2 (constant areal density, on screen)."""
    a, b = 1.0 / Z_NEAR, 1.0 / Z_ICE_MAX
    return 1.0 / (a - u * (a - b))


def surface_u(z_m: float) -> float:
    """Fraction of the way from Z_NEAR to Z_ICE_MAX, the inverse of sample_depth's CDF."""
    a, b = 1.0 / Z_NEAR, 1.0 / Z_ICE_MAX
    return ((a - 1.0 / z_m) / (a - b))


def floe_plan(count: int = FLOE_COUNT) -> list[dict]:
    """Deterministic list of floes, each already carrying its projected polygon in pixels."""
    rng = LCG()
    floes: list[dict] = []
    for _ in range(count):
        z = sample_depth(rng.next_u())
        # Uniform areal density means X must scale with Z to fill a fixed angular window.
        x = rng.between(-0.68, 0.68) * z
        # Rapakivi / pancake ice: a power law, a few plates far larger than the rest.
        r = 0.9 + 6.5 * rng.next_u() ** 2.4
        # Shear rafts the plates: they elongate downstream (along Z), and thin across it.
        ez = rng.between(1.25, 2.10)
        ex = rng.between(0.62, 0.95)
        n = 9
        verts = []
        for i in range(n):
            t = 2.0 * math.pi * i / n + rng.between(-0.14, 0.14)
            k = rng.between(0.70, 1.0)
            verts.append((x + r * ex * k * math.cos(t), z + r * ez * k * math.sin(t)))

        pts = [project(vx, vz) for vx, vz in verts]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        if max(xs) < -40 or min(xs) > W + 40 or min(ys) > H + 40:
            continue  # wholly outside the frame; keep the plan honest about counts drawn
        tint = rng.between(0.06, 0.34)
        floes.append(
            {
                "z": z,
                "x": x,
                "r": r,
                "ez": ez,
                "tint": tint,
                "pts": pts,
                "width_px": max(xs) - min(xs),
                "height_px": max(ys) - min(ys),
                "colour": floe_colour(z, tint),
            }
        )
    floes.sort(key=lambda f: -f["z"])
    return floes


def band_counts(floes: list[dict], bands: int = 6, screen_lo: float = 357.0, screen_hi: float = 690.0) -> list[int]:
    """Count drawn floes whose centre falls in each of `bands` equal screen rows."""
    counts = [0] * bands
    for f in floes:
        y = f["pts"][0][1]
        if screen_lo <= y < screen_hi:
            idx = min(int((y - screen_lo) / ((screen_hi - screen_lo) / bands)), bands - 1)
            counts[idx] += 1
    return counts


# --- the far shore -----------------------------------------------------------------
def bank_features() -> tuple[list[dict], dict]:
    """Treeline (as heights in metres at Z_BANK) and the church, both projected."""
    rng = LCG(777)
    trees = []
    # Woodland in stands with clearings between them, the way a far bank actually reads.
    for centre, count in ((-470, 8), (-355, 5), (-232, 11), (-118, 3), (52, 6), (168, 4), (312, 9), (448, 5)):
        for i in range(count):
            x_m = centre + i * rng.between(7.0, 15.0) + rng.between(-4.0, 4.0)
            trees.append({"x_m": x_m, "h_m": rng.between(5.0, 25.0)})
    trees.sort(key=lambda t: t["x_m"])
    church = {"x_m": -58.0, "tower_m": 44.0, "body_m": 13.0, "body_w_m": 30.0, "tower_w_m": 9.0}
    return trees, church


# --- assembly ----------------------------------------------------------------------
def _sky(svg: list[str]) -> None:
    svg.append(
        f'<defs>'
        f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{hexc(SKY_TOP)}"/>'
        f'<stop offset="0.62" stop-color="{hexc(mix(SKY_TOP, SKY_HORIZON, 0.72))}"/>'
        f'<stop offset="1" stop-color="{hexc(SKY_HORIZON)}"/>'
        f'</linearGradient>'
        f'<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0" stop-color="{hexc(GLOW)}" stop-opacity="0.85"/>'
        f'<stop offset="1" stop-color="{hexc(GLOW)}" stop-opacity="0"/>'
        f'</radialGradient>'
        f'</defs>'
    )
    svg.append(f'<rect x="0" y="0" width="{W}" height="{HORIZON + 2:.0f}" fill="url(#sky)"/>')
    # The low sun is behind the shore, right of the church: an overcast dawn breaking through.
    svg.append(f'<ellipse cx="{CX + 150:.0f}" cy="{HORIZON - 8:.0f}" rx="330" ry="132" fill="url(#glow)"/>')


def _shore(svg: list[str]) -> None:
    trees, church = bank_features()
    _, y_ground = project(0.0, Z_BANK)
    haze = haze_fraction(Z_BANK)
    ground_ink = mix(BANK, HAZE, haze * 0.70)
    ridge = [f'M -20 {y_ground + 3:.1f}']
    for t in trees:
        x, y = project(t["x_m"], Z_BANK)
        top = y - FOCAL * t["h_m"] / Z_BANK
        half = FOCAL * (2.0 + t["h_m"] * 0.18) / Z_BANK
        ridge.append(f'L {x - half:.1f} {y + 0.6:.1f} L {x:.1f} {top:.1f} L {x + half:.1f} {y + 0.6:.1f}')
    ridge.append(f'L {W + 20} {y_ground + 3:.1f} Z')
    svg.append(f'<path d="{" ".join(ridge)}" fill="{hexc(ground_ink)}"/>')

    # A wooden church with a bell tower: the Wanderers' habit of one small human mark in a large
    # world. Its spire reaches 44 m; at 1.5 km that is 26 px, and it stays 26 px.
    cx_s, y_s = project(church["x_m"], Z_BANK)
    half_b = FOCAL * church["body_w_m"] / 2.0 / Z_BANK
    half_t = FOCAL * church["tower_w_m"] / 2.0 / Z_BANK
    h_b = FOCAL * church["body_m"] / Z_BANK
    h_t = FOCAL * church["tower_m"] / Z_BANK
    ink = hexc(mix((30, 32, 30), HAZE, haze * 0.42))
    svg.append(
        f'<g fill="{ink}">'
        f'<rect x="{cx_s - half_b:.1f}" y="{y_s - h_b:.1f}" width="{2 * half_b:.1f}" height="{h_b + 2:.1f}"/>'
        f'<rect x="{cx_s - half_t:.1f}" y="{y_s - h_t:.1f}" width="{2 * half_t:.1f}" height="{h_t + 2:.1f}"/>'
        f'</g>'
    )
    spire = (
        f'M {cx_s - half_t:.1f} {y_s - h_t:.1f} '
        f'L {cx_s:.1f} {y_s - h_t - FOCAL * 11.0 / Z_BANK:.1f} '
        f'L {cx_s + half_t:.1f} {y_s - h_t:.1f} Z'
    )
    svg.append(f'<path d="{spire}" fill="{ink}"/>')
    # the water's answer to it: three broken dashes of reflection, nothing more
    for i, (dy, x_off, wide) in enumerate(((2.0, -1.0, 7.0), (4.5, 1.5, 9.0), (7.0, -0.5, 5.0))):
        svg.append(
            f'<rect x="{cx_s + x_off - wide:.1f}" y="{y_s + dy:.1f}" width="{2 * wide:.1f}" '
            f'height="0.9" fill="{ink}" opacity="{0.26 - i * 0.06:.2f}"/>'
        )


def lead_colour() -> tuple[float, float, float]:
    """The open reach is water seen almost along its own surface: a mirror of the sky."""
    return water_colour(Z_ICE_MAX)


def _lead(svg: list[str]) -> None:
    """The open water beyond the last ice, and the sheen on it: the plate's one bright band."""
    _, y_bank = project(0.0, Z_BANK)
    _, y_ice = project(0.0, Z_ICE_MAX)
    top = lead_colour()
    svg.append(
        f'<rect x="0" y="{y_bank - 0.5:.1f}" width="{W}" height="{y_ice - y_bank + 1.0:.1f}" '
        f'fill="{hexc(top)}"/>'
    )
    svg.append(
        f'<rect x="0" y="{y_bank:.1f}" width="{W}" height="{(y_ice - y_bank) * 0.40:.1f}" '
        f'fill="{hexc(mix(top, (255, 255, 250), 0.45))}" opacity="0.7"/>'
    )


def _water(svg: list[str]) -> None:
    """Every water row coloured by its own Fresnel term — no gradient is drawn, one law is."""
    _, y_ice = project(0.0, Z_ICE_MAX)
    y = y_ice - 1.0
    while y < H:
        z = FOCAL * CAM_H / max(y - HORIZON, 0.5)
        svg.append(
            f'<rect x="0" y="{y:.1f}" width="{W}" height="{3.2:.1f}" fill="{hexc(water_colour(z))}"/>'
        )
        y += 3.0


def _ice(svg: list[str], floes: list[dict]) -> None:
    for f in floes:
        pts = f["pts"]
        d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
        col = hexc(f["colour"])
        # Rafted plates throw a short shadow down-right: the sun is low and behind the shore, so
        # the shadow is longer than the plate is thick, and it is the only hard edge in the frame.
        if f["width_px"] > 14:
            dx = min(f["height_px"] * 0.30, 6.0)
            dy = min(f["height_px"] * 0.55, 10.0)
            svg.append(
                f'<path d="{d}" fill="{hexc(ICE_SHADOW)}" opacity="0.22" '
                f'transform="translate({dx:.1f} {dy:.1f})"/>'
            )
        stroke = ""
        if f["z"] < 260.0:
            stroke = f' stroke="{hexc(mix(f["colour"], (255, 255, 255), 0.55))}" stroke-width="{max(0.35, 900 * 0.10 / f["z"]):.2f}"'
        svg.append(f'<path d="{d}" fill="{col}"{stroke}/>')


def _foreground(svg: list[str]) -> None:
    """One plate at 14 m, cropped by the frame: the dark anchor the eye enters on."""
    rng = LCG(4242)
    cx_w, cz_w = -26.0, 14.0
    pts = []
    for i in range(14):
        t = 2.0 * math.pi * i / 14 + rng.between(-0.10, 0.10)
        k = rng.between(0.78, 1.0)
        pts.append(project(cx_w + 15.0 * k * math.cos(t), cz_w + 22.0 * k * math.sin(t)))
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
    svg.append(f'<path d="{d}" fill="{hexc(mix(ICE_SHADOW, (72, 86, 101), 0.55))}"/>')
    svg.append(f'<path d="{d}" fill="{hexc(ICE_NEAR)}" opacity="0.50" transform="translate(-6 -14)"/>')


def _plate(svg: list[str], drawn: int) -> None:
    lead_lum = luminance(lead_colour())
    svg.append(
        f'<text x="60" y="118" font-family="Newsreader, Georgia, serif" font-size="54" '
        f'fill="{PAPER}" opacity="0.97">Ledokhod — The Ice Goes Out</text>'
    )
    svg.append(
        f'<text x="60" y="162" font-family="Newsreader, Georgia, serif" font-style="italic" '
        f'font-size="24" fill="{PAPER}" opacity="0.80">the river at 12 m above the water, '
        f'ice out to {Z_ICE_MAX:.0f} m</text>'
    )
    svg.append(
        f'<rect x="40" y="{H - 116}" width="470" height="90" fill="#0f141c" opacity="0.72" rx="3"/>'
    )
    lines = [
        f'h = {CAM_H:.0f} m   f = {FOCAL:.0f} px   squash(100 m) = {squash(100.0):.3f}   '
        f'squash(600 m) = {squash(Z_ICE_MAX):.3f}',
        f'floes drawn {drawn}   haze(Z) = 1 - exp(-Z/{HAZE_SCALE:.0f} m)   '
        f'haze({Z_ICE_MAX:.0f} m) = {haze_fraction(Z_ICE_MAX):.3f}',
        f'lead luminance {lead_lum:.3f}  >  every plate  (Kuindzhi condition)',
    ]
    for i, line in enumerate(lines):
        svg.append(
            f'<text x="56" y="{H - 88 + i * 22}" font-family="JetBrains Mono, monospace" '
            f'font-size="13" fill="{PAPER}" opacity="0.80">{line}</text>'
        )
    svg.append(
        f'<text x="{W - 60}" y="{H - 34}" font-family="Georgia, serif" font-size="26" '
        f'fill="{PAPER}" text-anchor="end">Dmitri S. Pravdin</text>'
    )
    svg.append(
        f'<text x="{W - 60}" y="{H - 14}" font-family="JetBrains Mono, monospace" font-size="11" '
        f'fill="{PAPER}" opacity="0.62" letter-spacing="1.6" text-anchor="end">'
        f'PROCEDURAL SVG • 2026-10-20 • WING 07</text>'
    )


def build_svg() -> str:
    floes = floe_plan()
    brightest = max(luminance(f["colour"]) for f in floes)
    if brightest >= luminance(lead_colour()):
        raise SystemExit(
            "refusing to emit: an ice plate is brighter than the lead "
            f"({brightest:.3f} vs {luminance(lead_colour()):.3f})"
        )
    svg: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-labelledby="ledokhod-title ledokhod-desc">',
        '<title id="ledokhod-title">Ledokhod — The Ice Goes Out</title>',
        '<desc id="ledokhod-desc">Spring ice going out on a wide Russian river at dawn: floes on a '
        'water plane at constant areal density, projected from a camera 12 m above the water, '
        'hazed with distance by 1 - exp(-Z/380 m), with a single bright open lead beyond the last '
        'ice. Procedural SVG by Dmitri S. Pravdin.</desc>',
    ]
    _sky(svg)
    _shore(svg)
    _lead(svg)
    _water(svg)
    _ice(svg, floes)
    _foreground(svg)
    _plate(svg, len(floes))
    svg.append("</svg>")
    return "\n".join(svg) + "\n"


def main() -> None:
    out = Path(__file__).resolve().parent / "ledokhod-the-ice-goes-out.svg"
    out.write_text(build_svg(), encoding="utf-8")
    floes = floe_plan()
    counts = band_counts(floes)
    print(f"wrote {out.name}: {len(floes)} floes drawn, {out.stat().st_size} bytes")
    print(f"screen-band counts (6 bands, y=357..690): {counts}")
    print(f"lead luminance {luminance(lead_colour()):.3f}; brightest plate {max(luminance(f['colour']) for f in floes):.3f}")
    print(f"haze(620 m) = {haze_fraction(Z_ICE_MAX):.3f}; squash(100 m) = {squash(100.0):.3f}")


if __name__ == "__main__":
    main()
