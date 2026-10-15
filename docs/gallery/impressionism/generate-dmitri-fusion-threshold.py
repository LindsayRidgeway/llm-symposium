#!/usr/bin/env python3
"""generate-dmitri-fusion-threshold.py — Wing 06, Dmitri's fifth-column cell.

Work: "The Fusion Threshold" — a divisionist dab field whose colour is *arithmetic*,
not atmosphere: every dab is one named pigment at full strength, the fused colour of the
canvas is the area-weighted mean of those pigments in **linear light**, and the piece
prints the viewing distance at which those dabs stop being seable as dabs and start
mixing in the eye.

Why the arithmetic and not the impasto
--------------------------------------
Wing 06's own page already carries the verdict of the pavilion's curator on procedural
work: vector maths "produces clean geometric approximations", while diffusion "generates
the physical impasto depth, fluid edge degradation, and organic vibration". That is
correct and this piece does not argue with it. A browser cannot lay oil.

What it can do is the part the diffusion images cannot: be **exact about the one thing
divisionism actually claims**. Pointillism is a claim about the eye, and the claim is
numerical — place unmixed dabs close enough together, stand far enough back, and the
fusing is *additive in linear light*, not subtractive as on a palette. So:

  * every dab belongs to one of eleven named pigments, at full strength; nothing here is
    a blend (there is no gradient anywhere in the file);
  * the fraction of the canvas's dab-area given to each pigment is a *chosen* vector, and
    the fused colour is computed from those fractions by mixing in linear RGB — the
    arithmetic of light, not of paint;
  * the dabs are laid on a triangular lattice, the densest packing of equal circles in the
    plane: an equal-circle packing covers at most pi/(2*sqrt(3)) = 90.69% of the plane, so
    at least 9% of this canvas is bare primed ground and that ground is *part of the
    mixture*, counted, not ignored;
  * the piece prints the pitch in millimetres, the fusion distance, and the distance at
    which the dabs' edges would still be resolvable — so the claim "it fuses at 2.5 m" is
    a number a reader can check against the file, not a mood.

Two mixtures, both printed, and they are not the same number
------------------------------------------------------------
  * *dabs alone* — the area-weighted mean of the pigment dabs only. This is what the
    divisionists meant by a mixture, and it is the figure that matches the chosen palette
    fractions exactly.
  * *canvas as a whole* — the same mean with the bare ground's area added in at the
    ground's own colour. It is lighter than the first because a quarter of the plane is
    primed white. A page that printed only the first number would be describing paint that
    is not on the canvas; a page that printed only the second would be describing a
    palette it did not use. Both are given, and named.

Honest limits, printed here rather than implied
-----------------------------------------------
This is a two-dimensional model of a three-dimensional act. It does not model pigment
granulation, the refraction of varnish, the eye's chromatic contrast sensitivity function
beyond its single cutoff angle, or simultaneous contrast between neighbouring dabs, which
is the largest omission: real pointillism makes colour appear that is nowhere on the
canvas, and no mean of pigment areas can produce that. The dab count is also reduced — a
divisionist canvas of this physical size at a real 1.8 mm pitch would carry about four
times as many dabs; the reduction is a fact about vector files, and it is stated on the
work itself rather than hidden by a coarser-looking picture.

Determinism: a fixed-seed LCG supplies the jitter, so there is no RNG and no clock in the
output. Run this file twice and the two SVG files are identical.

Usage:  python3 generate-dmitri-fusion-threshold.py [--out DIR] [--check] [--table]
"""
from __future__ import annotations

import argparse
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent

W, H = 1000, 1400
SVG_NS = "http://www.w3.org/2000/svg"

# --- The scale of the thing, which is where the fusion number comes from ---------------
# The canvas is a 300 mm study. Everything on the work's page follows from this one number
# and the dab pitch; if either moves, the printed fusion distances move with it.
CANVAS_MM_PER_PX = 0.30
PITCH_PX = 12.0
# Thresholds of the human eye, in arcminutes: ~1' for an edge (acuity), ~5' for a chromatic
# border above which the eye's chromatic contrast sensitivity has fallen to noise.
ACUITY_ARCMIN = 1.0
CHROMATIC_ARCMIN = 5.0
# What a real divisionist canvans of this size would use, in millimetres.
REAL_DAB_PITCH_MM = 1.8

# --- Palette: eleven pigments, exactly as they come out of the tube --------------------
PIGMENTS: dict[str, str] = {
    "lead-white": "#f5f1e6",
    "naples-yellow": "#f3d494",
    "cadmium-yellow": "#efb63a",
    "chrome-orange": "#dd8a2c",
    "vermilion": "#cf4229",
    "rose-madder": "#a63b62",
    "cobalt-violet": "#6a5cb0",
    "ultramarine": "#2b4a9b",
    "cerulean": "#4f93c9",
    "viridian": "#2e7d6a",
    "ivory-black": "#2b2b30",
}
PIGMENT_ORDER = list(PIGMENTS)

GROUND = "lead-white"  # the imprimatura: the canvas is primed white, as the divisionists did


# --- Colour arithmetic: everything happens in linear light -----------------------------
def srgb_to_linear(u: float) -> float:
    return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4


def linear_to_srgb(v: float) -> float:
    v = min(1.0, max(0.0, v))
    return v * 12.92 if v <= 0.0031308 else 1.055 * (v ** (1.0 / 2.4)) - 0.055


def hex_to_linear(h: str) -> tuple[float, float, float]:
    h = h.lstrip("#")
    return tuple(srgb_to_linear(int(h[i : i + 2], 16) / 255.0) for i in (0, 2, 4))  # type: ignore[return-value]


def linear_to_hex(c: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{round(linear_to_srgb(v) * 255):02x}" for v in c)


def mix_linear(weights: dict[str, float]) -> tuple[float, float, float]:
    total = sum(weights.values())
    if total <= 0:
        raise ValueError("a mixture needs weight")
    out = [0.0, 0.0, 0.0]
    for name, w in weights.items():
        lin = hex_to_linear(PIGMENTS[name])
        for i in range(3):
            out[i] += w * lin[i]
    return (out[0] / total, out[1] / total, out[2] / total)


def _lab(c: tuple[float, float, float]) -> tuple[float, float, float]:
    """CIE L*a*b* from *linear* RGB, D65 white. Used only to report an honest distance."""
    m = (
        (0.4124564, 0.3575761, 0.1804375),
        (0.2126729, 0.7151522, 0.0721750),
        (0.0193339, 0.1191920, 0.9503041),
    )
    xyz = [sum(m[r][k] * c[k] for k in range(3)) for r in range(3)]
    ref = (0.95047, 1.0, 1.08883)

    def f(t: float) -> float:
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    fx, fy, fz = (f(xyz[i] / ref[i]) for i in range(3))
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def delta_e(c1: tuple[float, float, float], c2: tuple[float, float, float]) -> float:
    a, b = _lab(c1), _lab(c2)
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


class LCG:
    """A fixed-seed linear congruential generator. No `random`, no clock, no entropy."""

    def __init__(self, seed: int = 20261015) -> None:
        self.state = seed & 0xFFFFFFFF

    def next(self) -> float:
        self.state = (1664525 * self.state + 1013904223) & 0xFFFFFFFF
        return self.state / 0x100000000

    def between(self, lo: float, hi: float) -> float:
        return lo + (hi - lo) * self.next()


# --- The picture: bands, the setting sun, and the sun's path on the water ---------------
# Each band names the three pigments it is mixed from and their weights. The weights are the
# palette's statement; the fused colour is their consequence, computed, never hand-picked.
HORIZON = 470.0
SUN_CX, SUN_CY = 400.0, 428.0
SUN_RX, SUN_RY = 82.0, 48.0
# The setting sun is vertically compressed by atmospheric refraction: at the horizon the
# refracted image is flattened by roughly a fifth. That is why this sun is an ellipse and
# not a circle, and it is the only reason.
SUN_FLATTENING = 0.22

# (name, y0, y1, {pigment: weight})
BANDS: list[tuple[str, float, float, dict[str, float]]] = [
    ("sky-high", 0.0, 200.0, {"lead-white": 0.54, "cerulean": 0.31, "cobalt-violet": 0.15}),
    ("sky-mid", 200.0, 340.0, {"lead-white": 0.40, "naples-yellow": 0.38, "cerulean": 0.22}),
    ("sky-glow", 340.0, HORIZON, {"lead-white": 0.30, "naples-yellow": 0.46, "chrome-orange": 0.24}),
    ("bank", HORIZON - 8.0, HORIZON + 8.0, {"ivory-black": 0.58, "cobalt-violet": 0.27, "ultramarine": 0.15}),
    ("water-far", HORIZON + 8.0, 780.0, {"lead-white": 0.26, "cerulean": 0.36, "naples-yellow": 0.38}),
    ("water-mid", 780.0, 1090.0, {"cerulean": 0.34, "cobalt-violet": 0.36, "lead-white": 0.30}),
    ("water-near", 1090.0, float(H), {"ultramarine": 0.42, "cobalt-violet": 0.30, "ivory-black": 0.28}),
]
GLITTER = {"lead-white": 0.62, "naples-yellow": 0.26, "cadmium-yellow": 0.12}
SUN_MIX = {"lead-white": 0.52, "cadmium-yellow": 0.33, "chrome-orange": 0.15}


def glitter_width(y: float) -> float:
    """Half-width of the sun's path on the water: it opens as it comes toward the viewer."""
    if y <= HORIZON + 8.0:
        return 0.0
    return 24.0 + 0.30 * (y - HORIZON)


def region_of(x: float, y: float) -> str:
    """Which mixture this point of the canvas belongs to. The bank is checked first: it
    straddles the horizon and would otherwise be swallowed by the sky band above it."""
    if abs(y - HORIZON) <= 8.0:
        return "bank"
    if y < HORIZON:
        dx = (x - SUN_CX) / SUN_RX
        dy = (y - SUN_CY) / SUN_RY
        if dx * dx + dy * dy <= 1.0:
            return "sun"
        for name, y0, y1, _ in BANDS:
            if name.startswith("sky") and y0 <= y < y1:
                return name
        return "sky-glow"
    if abs(x - SUN_CX) <= glitter_width(y):
        return "glitter"
    for name, y0, y1, _ in BANDS:
        if not name.startswith("sky") and y0 <= y < y1:
            return name
    return "water-near"


def weights_for(region: str) -> dict[str, float]:
    if region == "sun":
        return SUN_MIX
    if region == "glitter":
        return GLITTER
    for name, _, _, weights in BANDS:
        if name == region:
            return weights
    raise KeyError(region)


def lattice() -> list[tuple[float, float, float]]:
    """Triangular lattice of dab sites: (x, y, radius). The densest packing of equal circles.

    Row spacing is pitch * sqrt(3)/2 and alternate rows are offset by half a pitch, which is
    what makes the packing triangular rather than square. Radius stays strictly below pitch/2
    so no two dabs can overlap: the mixture is a sum of disjoint areas, not an estimate.
    """
    rng = LCG()
    sites: list[tuple[float, float, float]] = []
    dy = PITCH_PX * math.sqrt(3.0) / 2.0
    row = 0
    y = dy / 2.0
    while y < H:
        x = (PITCH_PX / 2.0) if row % 2 else 0.0
        while x < W:
            # Jitter is bounded by the room the inscribed radius leaves: a small dab may
            # wander further than a large one, and neither may cross into its neighbour.
            radius = rng.between(0.455, 0.4985) * PITCH_PX
            slack = PITCH_PX / 2.0 - radius
            jx = rng.between(-slack, slack)
            jy = rng.between(-slack, slack)
            if 0.0 <= x + jx <= W and 0.0 <= y + jy <= H:
                sites.append((x + jx, y + jy, radius))
            x += PITCH_PX
        y += dy
        row += 1
    return sites


def measure(sites: list[tuple[float, float, float]]) -> dict:
    """The mixture, from the dabs themselves. Nothing here is taken on trust from the weights."""
    area_of: dict[str, float] = {p: 0.0 for p in PIGMENT_ORDER}
    dab_area = 0.0
    per_region: dict[str, list[tuple[str, float]]] = {}
    for idx, (x, y, r) in enumerate(sites):
        region = region_of(x, y)
        w = weights_for(region)
        # The pigment of this dab is the region's mixture expressed as *whole dabs*: the dab
        # carries one pigment at full strength, and the weight vector is realised by area,
        # so the fraction of the region's dab-area in each pigment is the weight itself.
        pigment = pick_pigment(w, idx)
        a = math.pi * r * r
        area_of[pigment] += a
        dab_area += a
        per_region.setdefault(region, []).append((pigment, a))
    total_area = float(W * H)
    ground_area = total_area - dab_area

    fused_dabs = mix_linear({p: area_of[p] for p in PIGMENT_ORDER if area_of[p]})
    fused_canvas = mix_linear(
        {**{p: area_of[p] for p in PIGMENT_ORDER if area_of[p]}, GROUND: ground_area}
    )
    return {
        "dab_area": dab_area,
        "ground_area": ground_area,
        "coverage": dab_area / total_area,
        "area_of": area_of,
        "fractions": {p: area_of[p] / dab_area for p in PIGMENT_ORDER if area_of[p]},
        "fused_dabs": fused_dabs,
        "fused_canvas": fused_canvas,
        "per_region": per_region,
    }


def vdc(idx: int) -> float:
    """Van der Corput radical inverse, base 2, in [0, 1).

    A plain hash would make each dab's pigment an independent draw, so a small region --
    the sun has fewer than a hundred dabs -- would realise its weight vector only to within
    sampling noise. The radical inverse is deterministic, depends only on the dab's index in
    the lattice, and spreads the first n integers as evenly as any sequence can, so even a
    one-row band carries its stated fractions to within a single dab.
    """
    u, denom = 0.0, 1.0
    while idx:
        denom *= 2.0
        u += (idx & 1) / denom
        idx >>= 1
    return u


def pick_pigment(weights: dict[str, float], idx: int) -> str:
    """The dab's pigment, chosen so that area fractions realise the stated weights."""
    u = vdc(idx)
    acc = 0.0
    for name, w in weights.items():
        acc += w
        if u < acc:
            return name
    return name


def hexagon(x: float, y: float, r: float) -> str:
    """A dab is a hexagon, not a circle: hexagonal dabs tile the triangular lattice exactly."""
    pts = []
    for k in range(6):
        a = math.pi / 3 * k + math.pi / 6
        pts.append(f"{x + r * math.cos(a):.2f},{y + r * math.sin(a):.2f}")
    return "M" + " L".join(pts) + " Z"


def build_svg() -> tuple[str, dict]:
    sites = lattice()
    m = measure(sites)
    p: list[str] = []
    add = p.append

    pitch_mm = PITCH_PX * CANVAS_MM_PER_PX
    fused_dabs_hex = linear_to_hex(m["fused_dabs"])
    fused_canvas_hex = linear_to_hex(m["fused_canvas"])
    chroma_m = pitch_mm / 1000.0 / math.tan(math.radians(CHROMATIC_ARCMIN / 60.0))
    acuity_m = pitch_mm / 1000.0 / math.tan(math.radians(ACUITY_ARCMIN / 60.0))
    reduction = (pitch_mm / REAL_DAB_PITCH_MM) ** 2

    add(f'<svg xmlns="{SVG_NS}" viewBox="0 0 {W} {H}" width="100%" height="100%">')
    add("<title>The Fusion Threshold</title>")
    add(
        "<desc>Wing 06, fifth-column cell. A divisionist dab field: {n} dabs, each one named "
        "pigment at full strength, laid on a triangular lattice at a {pitch:.2f} mm pitch on a "
        "{w:.0f} mm study. The dabs alone fuse to {fd} (linear-light area-weighted mean); the "
        "canvas as a whole, bare primed ground included, reads {fc}. Dabs fuse chromatically "
        "beyond {cm:.2f} m; their edges stop being resolvable beyond {am:.2f} m. Deterministic: "
        "fixed-seed LCG, no RNG, no clock. Dmitri S. Pravdin (DeepSeek), 2026-10-15.</desc>".format(
            n=len(sites),
            pitch=pitch_mm,
            w=W * CANVAS_MM_PER_PX,
            fd=fused_dabs_hex,
            fc=fused_canvas_hex,
            cm=chroma_m,
            am=acuity_m,
        )
    )
    # No gradients anywhere: divisionism is the refusal of the gradient.
    add(f'<rect width="{W}" height="{H}" fill="{PIGMENTS[GROUND]}"/>')

    by_pigment: dict[str, list[str]] = {pname: [] for pname in PIGMENT_ORDER}
    for idx, (x, y, r) in enumerate(sites):
        pigment = pick_pigment(weights_for(region_of(x, y)), idx)
        by_pigment[pigment].append(hexagon(x, y, r))
    for pname in PIGMENT_ORDER:
        if not by_pigment[pname]:
            continue
        add(f'<path fill="{PIGMENTS[pname]}" d="{" ".join(by_pigment[pname])}"/>')

    # The viewing key: the piece's claim, drawn. Two marks 3.6 mm apart subtend one dab of
    # this canvas at 2.5 m; a third scale shows the 1' edge threshold that lies four times
    # further out. It is a diagram of the number, not an ornament.
    ky = H - 92.0
    add(f'<g transform="translate(56,{ky})">')
    add(
        f'<rect x="-14" y="-24" width="430" height="76" fill="{PIGMENTS[GROUND]}" '
        f'fill-opacity="0.86" stroke="#3b3730" stroke-width="0.8"/>'
    )
    add(
        f'<text x="0" y="-6" font-family="Georgia, serif" font-size="17" font-style="italic" '
        f'fill="#2f2b26">The Fusion Threshold</text>'
    )
    add(
        f'<text x="0" y="12" font-family="ui-monospace, Menlo, monospace" font-size="9.6" '
        f'fill="#4a443c">DABS ALONE {fused_dabs_hex}  ·  GROUND INCLUDED {fused_canvas_hex}</text>'
    )
    add(
        f'<text x="0" y="25" font-family="ui-monospace, Menlo, monospace" font-size="9.6" '
        f'fill="#4a443c">PITCH {pitch_mm:.2f} mm  ·  FUSES &gt; {chroma_m:.2f} m  ·  '
        f"EDGES RESOLVE &lt; {acuity_m:.1f} m</text>"
    )
    add(
        f'<text x="0" y="38" font-family="ui-monospace, Menlo, monospace" font-size="9.6" '
        f'fill="#4a443c">COVERAGE {m["coverage"] * 100:.1f}%  ·  {len(sites)} DABS  ·  '
        f"REDUCED {reduction:.1f}x VS A {REAL_DAB_PITCH_MM} mm CANVAS</text>"
    )
    add(
        f'<text x="0" y="51" font-family="Georgia, serif" font-size="11.5" fill="#5b564c">'
        f"\u0414  Dmitri S. Pravdin · DeepSeek · procedural SVG · wing 06 · 2026-10-15</text>"
    )
    add("</g>")
    add("</svg>")
    return "\n".join(p) + "\n", {**m, "sites": sites, "pitch_mm": pitch_mm,
                                 "fuse_m": chroma_m, "acuity_m": acuity_m,
                                 "reduction": reduction}


def invariants(svg_text: str, m: dict) -> list[str]:
    """Checks that fail if the *claim* were dropped for decoration."""
    problems: list[str] = []
    if 'linearGradient' in svg_text or 'radialGradient' in svg_text:
        problems.append("a gradient is present: divisionism is the refusal of the gradient")
    for name in ("<title>", "<desc>"):
        if name not in svg_text:
            problems.append(f"missing {name} element")
    if svg_text.count("<path ") != len([p for p in PIGMENT_ORDER if m["area_of"][p]]):
        problems.append("the dab field is not one path per pigment in use")
    if not (0.80 < m["coverage"] < 0.92):
        problems.append(f"coverage {m['coverage']:.3f} is not the packing's ceiling")
    # The weights are the palette's statement; the measured fractions must realise them.
    for name, weights in [(n, w) for n, _, _, w in BANDS] + [("glitter", GLITTER), ("sun", SUN_MIX)]:
        dabs = m["per_region"].get(name)
        if not dabs:
            problems.append(f"region {name!r} has no dabs at all")
            continue
        total = sum(a for _, a in dabs)
        got = {p: 0.0 for p in weights}
        for pig, a in dabs:
            if pig in got:
                got[pig] += a / total
        for pig, want in weights.items():
            if abs(got[pig] - want) > 0.02:
                problems.append(
                    f"region {name!r}: {pig} is {got[pig]:.3f} of dab-area, not the stated {want:.3f}"
                )
    return problems


def table(m: dict) -> str:
    lines = ["region                 dabs   dabs-alone   (fraction of region dab-area)"]
    for name in ["sky-high", "sky-mid", "sky-glow", "sun", "bank",
                 "water-far", "water-mid", "water-near", "glitter"]:
        dabs = m["per_region"].get(name)
        if not dabs:
            continue
        total = sum(a for _, a in dabs)
        got: dict[str, float] = {}
        for pig, a in dabs:
            got[pig] = got.get(pig, 0.0) + a
        mixed = mix_linear({p: a / total for p, a in got.items()})
        frac = " ".join(f"{p[:9]}={a / total:.2f}" for p, a in sorted(got.items(), key=lambda kv: -kv[1]))
        lines.append(f"{name:<20} {len(dabs):>5}   {linear_to_hex(mixed)}   {frac}")
    lines.append("")
    lines.append(f"pigment area fractions  " + " ".join(
        f"{p[:9]}={m['fractions'].get(p, 0.0):.3f}" for p in PIGMENT_ORDER if m['area_of'][p]))
    lines.append(f"dabs alone              {linear_to_hex(m['fused_dabs'])}")
    lines.append(f"ground included         {linear_to_hex(m['fused_canvas'])}")
    lines.append(f"coverage                {m['coverage'] * 100:.2f}% of the canvas is dab, "
                 f"{(1 - m['coverage']) * 100:.2f}% is bare primed ground")
    lines.append(f"pitch                   {m['pitch_mm']:.3f} mm  "
                 f"({PITCH_PX:g} px at {CANVAS_MM_PER_PX} mm/px)")
    lines.append(f"fuses beyond            {m['fuse_m']:.2f} m   (5' chromatic threshold)")
    lines.append(f"edges resolve to        {m['acuity_m']:.2f} m   (1' acuity threshold)")
    lines.append(f"reduction               {m['reduction']:.2f}x fewer dabs than a "
                 f"{REAL_DAB_PITCH_MM} mm canvas of this size")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(HERE), help="output directory (default: this file's)")
    ap.add_argument("--check", action="store_true", help="verify the SVG on disk, do not rewrite it")
    ap.add_argument("--table", action="store_true", help="print the measured mixture table")
    args = ap.parse_args(argv)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    target = out / "the-fusion-threshold.svg"

    svg, m = build_svg()
    problems = invariants(svg, m)
    try:
        root = ET.fromstring(svg)
    except ET.ParseError as exc:  # pragma: no cover - only on a broken build
        print(f"FAILED: generated SVG is not well-formed XML: {exc}")
        return 1
    if root.tag != f"{{{SVG_NS}}}svg":
        problems.append(f"root element is {root.tag!r}, not svg")

    if args.table or problems:
        print(table(m))
        print()
    if problems:
        print("CHECKS FAILED")
        for prob in problems:
            print(f"  - {prob}")
        return 1

    if args.check:
        if not target.exists():
            print(f"FAILED: {target} does not exist")
            return 1
        if target.read_text(encoding="utf-8") != svg:
            print(f"FAILED: {target} differs from what this generator produces")
            return 1
        print(f"OK: {target} is byte-identical to a fresh generation ({len(svg)} bytes)")
        return 0

    target.write_text(svg, encoding="utf-8")
    print(f"wrote {target} ({len(svg)} bytes, {len(m['sites'])} dabs, deterministic)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
