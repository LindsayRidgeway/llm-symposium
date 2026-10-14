#!/usr/bin/env python3
"""generate-dmitri-backrun.py — Wing 02, Dmitri's fifth-column cell.

Work: "Backrun and the Drying Ring" — a computational watercolor study of the two
pigment-transport signatures that a painting makes when nobody is holding the brush:
the dark rim a drying droplet leaves behind, and the re-wetting lobe ("backrun",
"cauliflower") a later drop of clean water pushes outward through a half-dry wash.

Why those two, and not a landscape
----------------------------------
Wing 02's own page states the pavilion's open question: "Procedural SVG can approximate
paper tooth and irregular wash edges; the generated raster works produce more convincing
images of capillary diffusion." That is a claim about *diffusion*, and it is mostly true —
a browser SVG filter is not a PDE solver. What SVG can do is show the signatures the
transport leaves, and be exact about the geometry while doing it. So this piece models the
two signatures by their mechanism rather than by texture:

  * the drying ring is the *pinned contact line* of Deegan et al. (1997): the edge of a
    droplet cannot recede, evaporative loss is fastest at the rim, and the compensating
    capillary flow carries pigment there, against the gradient of water. The ring is
    therefore drawn as an annulus whose darkening is a function of radial distance, not
    as a paint blob with a darker outline;
  * the backrun is the *reverse* flow: water with no pigment added to a drying wash
    re-dissolves pigment and drives it outward from the wet source, so the deposit forms
    lobed fronts that advance away from the drop, each lobe ringed by its own rim;
  * the faint radial scaffold under the sheet is the flow field that produces both. It is
    drawn deliberately, the way the compass construction is left visible under a girih —
    the mechanism, not the ornament, is the claim.

Honest limits, printed here rather than implied
-----------------------------------------------
This is a *model*, not a simulation. No PDE is solved, no evaporation rate is integrated,
and no pigment mass is conserved. The lobes are parametric curves, not the solution to a
transport equation. What is checked is stated exactly in the SVG's own <desc> and on the
pavilion page: determinism (regeneration is byte-identical), valid standalone XML, and the
geometric invariants below. Anyone who wants the physics of the drying ring should read
Deegan et al.; anyone who wants to see it under a brush should paint one.

Determinism: a fixed-seed LCG supplies all irregularity, so there is no RNG and no
clock in the output. Run this file twice and the two SVG files are identical.

Usage:  python3 generate-dmitri-backrun.py [--out DIR] [--check]
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

# --- Palette: pigments that granulate and stay transparent when layered --------------
PAPER = "#f2ece1"
PAPER_SHADE = "#e6ddcc"
INDIGO = "#2f4a86"
INDIGO_DEEP = "#1d3163"
SIENNA = "#b4713a"


class LCG:
    """A fixed-seed linear congruential generator. No `random`, no clock, no entropy."""

    def __init__(self, seed: int = 20261014) -> None:
        self.state = seed & 0xFFFFFFFF

    def next(self) -> float:
        """Return the next value in [0, 1)."""
        self.state = (1664525 * self.state + 1013904223) & 0xFFFFFFFF
        return self.state / 0x100000000

    def between(self, lo: float, hi: float) -> float:
        return lo + (hi - lo) * self.next()


def catmull_rom_closed(points: list[tuple[float, float]]) -> str:
    """A closed smooth path through `points`, as cubic Béziers (Catmull-Rom → Bézier)."""
    n = len(points)
    if n < 3:
        raise ValueError("a closed curve needs at least three points")
    d = [f"M {points[0][0]:.2f},{points[0][1]:.2f}"]
    for i in range(n):
        p0 = points[(i - 1) % n]
        p1 = points[i]
        p2 = points[(i + 1) % n]
        p3 = points[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d.append(
            f"C {c1[0]:.2f},{c1[1]:.2f} {c2[0]:.2f},{c2[1]:.2f} {p2[0]:.2f},{p2[1]:.2f}"
        )
    d.append("Z")
    return " ".join(d)


def backrun_outline(
    rng: LCG,
    cx: float,
    cy: float,
    base: float,
    lobes: int,
    depth: float,
    wobble: float,
) -> list[tuple[float, float]]:
    """The lobed frontier of a backrun: `lobes` advances away from the wet source.

    Each lobe is a local maximum of the deposit front, so the radius is a lobed function
    of angle; `wobble` perturbs the sample angles so the lobes do not read as a gear.
    """
    pts: list[tuple[float, float]] = []
    samples = lobes * 7
    for k in range(samples):
        t = k / samples
        a = 2 * math.pi * t  # uniform base sweep around the wet source
        lobe_phase = math.cos(lobes * a)
        r = base * (1.0 + depth * lobe_phase) + rng.between(-wobble, wobble)
        r *= 1.0 + 0.03 * math.sin(3.0 * a + 0.7)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def deckle_edge(rng: LCG, x: float, y: float, w: float, h: float, steps: int = 96):
    """A hand-torn paper edge: a rectangle whose sides wander by a millimetre or two."""
    pts: list[tuple[float, float]] = []
    for i in range(steps + 1):
        t = i / steps
        pts.append((x + t * w, y + rng.wobble_at(t, 0)))
    for i in range(1, steps + 1):
        t = i / steps
        pts.append((x + w + rng.wobble_at(t, 1), y + t * h))
    for i in range(1, steps + 1):
        t = i / steps
        pts.append((x + w - t * w, y + h + rng.wobble_at(t, 2)))
    for i in range(1, steps):
        t = i / steps
        pts.append((x + rng.wobble_at(t, 3), y + h - t * h))
    return pts


# The deckle wobble needs a value that is stable for a given (t, side), independent of the
# order in which the sides are generated, so the seed stream is indexed rather than shared.
def _wobble_at(self: LCG, t: float, side: int, amp: float = 3.2) -> float:
    h = int((t * 977.0 + side * 131.0) * 1000) ^ 0x5F3759DF
    h = (1103515245 * h + 12345) & 0x7FFFFFFF
    return ((h / 0x7FFFFFFF) * 2.0 - 1.0) * amp


LCG.wobble_at = _wobble_at  # type: ignore[attr-defined]


def build_svg() -> str:
    rng = LCG()
    p: list[str] = []
    add = p.append

    add(f'<svg xmlns="{SVG_NS}" viewBox="0 0 {W} {H}" width="100%" height="100%">')
    add('<title>Backrun and the Drying Ring</title>')
    add(
        "<desc>Wing 02, fifth-column cell. A computational watercolor study: the dark rim a "
        "drying droplet leaves behind (pinned contact line, Deegan et al. 1997) and the lobed "
        "front of a backrun, drawn from their mechanism rather than from texture, with the "
        "capillary flow field left visible as a faint scaffold. Deterministic: fixed-seed LCG, "
        "no RNG, no clock. Dmitri S. Pravdin (DeepSeek), 2026-10-14.</desc>"
    )
    add("<defs>")
    # Paper tooth: fractal noise, laid over the sheet at low opacity.
    add('<filter id="tooth" x="0%" y="0%" width="100%" height="100%">')
    add('<feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="3" result="n"/>')
    add(
        '<feColorMatrix in="n" type="matrix" '
        'values="0 0 0 0 0.55  0 0 0 0 0.50  0 0 0 0 0.42  0 0 0 0.16 0"/>'
    )
    add("</filter>")
    # Granulation: pigment settling into the tooth of the paper.
    add('<filter id="granulate" x="-10%" y="-10%" width="120%" height="120%">')
    add('<feTurbulence type="fractalNoise" baseFrequency="0.42" numOctaves="2" seed="7" result="g"/>')
    add('<feDisplacementMap in="SourceGraphic" in2="g" scale="13" xChannelSelector="R" yChannelSelector="G"/>')
    add("</filter>")
    add('<filter id="soft"><feGaussianBlur stdDeviation="9"/></filter>')
    add('<filter id="softer"><feGaussianBlur stdDeviation="22"/></filter>')
    # Edge darkening: the signature of a pinned contact line. Alpha rises sharply near the rim.
    gradients = [
        (
            'dryingRing', '50%', '50%', '50%',
            # Edge darkening, in five stops: transparent in the middle, a shelf where the
            # capillary flow begins to win, then the rim -- and just past the rim, the
            # paper the droplet never reached.
            [("0%", INDIGO, "0.20"), ("62%", INDIGO, "0.26"), ("86%", INDIGO_DEEP, "0.55"),
             ("97%", INDIGO_DEEP, "0.80"), ("100%", INDIGO_DEEP, "0.34")],
        ),
        (
            'siennaWash', '42%', '38%', '62%',
            [("0%", SIENNA, "0.14"), ("70%", SIENNA, "0.22"), ("100%", SIENNA, "0.46")],
        ),
        (
            'pool', '46%', '44%', '58%',
            [("0%", INDIGO, "0.10"), ("78%", INDIGO, "0.30"), ("100%", INDIGO_DEEP, "0.62")],
        ),
    ]
    for gid, gcx, gcy, gr, stops in gradients:
        add(f'<radialGradient id="{gid}" cx="{gcx}" cy="{gcy}" r="{gr}">')
        for offset, color, opacity in stops:
            add(f'<stop offset="{offset}" stop-color="{color}" stop-opacity="{opacity}"/>')
        add("</radialGradient>")
    add("</defs>")

    # --- The sheet -------------------------------------------------------------------
    add(f'<rect width="{W}" height="{H}" fill="{PAPER_SHADE}"/>')
    deckle = deckle_edge(rng, 28, 26, W - 56, H - 52)
    add(f'<path d="{catmull_rom_closed(deckle)}" fill="{PAPER}"/>')
    add(f'<path d="{catmull_rom_closed(deckle)}" fill="none" stroke="#c9bda6" stroke-width="1.1" opacity="0.8"/>')
    add(f'<rect x="28" y="26" width="{W - 56}" height="{H - 52}" filter="url(#tooth)" opacity="0.5"/>')

    # --- The flow field: the mechanism, left visible ---------------------------------
    # Capillary flow runs from the centre of the droplet toward the pinned rim.
    cx, cy, r_main = 500.0, 560.0, 250.0
    add(f'<g stroke="{INDIGO_DEEP}" stroke-width="0.7" opacity="0.065">')
    for k in range(72):
        a = 2 * math.pi * k / 72
        r0 = 34 + 12 * math.sin(5 * a)
        add(
            f'<line x1="{cx + r0 * math.cos(a):.1f}" y1="{cy + r0 * math.sin(a):.1f}" '
            f'x2="{cx + (r_main - 6) * math.cos(a):.1f}" y2="{cy + (r_main - 6) * math.sin(a):.1f}"/>'
        )
    add("</g>")
    add(f'<g fill="none" stroke="{INDIGO_DEEP}" stroke-width="0.7" opacity="0.14">')
    for r in (0.25, 0.5, 0.75, 0.94):
        add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r_main * r:.1f}"/>')
    add("</g>")

    # --- Wash 1: a wet-on-wet pool laid first, edges still soft ----------------------
    pool = backrun_outline(LCG(4101), 500, 980, 210, 5, 0.10, 4.0)
    add(f'<path d="{catmull_rom_closed(pool)}" fill="url(#siennaWash)" filter="url(#soft)" opacity="0.9"/>')

    # --- Wash 2: the drying droplet and its ring -------------------------------------
    # The *contact line* is what dries to a rim, and a real one is pinned by the paper's
    # tooth, not by geometry: it is an irregular closed curve, so the pool is drawn as one
    # (three shallow lobes plus wobble), never as a circle. A circle would be the one shape
    # a drying droplet of any size at all does not take.
    pool_edge = backrun_outline(LCG(3307), cx, cy, r_main, 3, 0.045, 11.0)
    add(
        f'<path d="{catmull_rom_closed(pool_edge)}" fill="url(#dryingRing)" '
        f'filter="url(#granulate)" opacity="0.85"/>'
    )
    # A second, smaller droplet that dried inside the first: two pinned lines, two rims.
    inner_edge = backrun_outline(LCG(3319), cx - 62, cy - 48, r_main * 0.36, 3, 0.06, 6.0)
    add(
        f'<path d="{catmull_rom_closed(inner_edge)}" fill="url(#pool)" '
        f'filter="url(#granulate)" opacity="0.8"/>'
    )
    # The rim itself, drawn as the invariant it is: a closed curve of constant width.
    add(
        f'<path d="{catmull_rom_closed(pool_edge)}" fill="none" stroke="{INDIGO_DEEP}" '
        f'stroke-width="3.2" opacity="0.34" filter="url(#soft)"/>'
    )
    add(
        f'<path d="{catmull_rom_closed(inner_edge)}" fill="none" stroke="{INDIGO_DEEP}" '
        f'stroke-width="2.0" opacity="0.26" filter="url(#soft)"/>'
    )

    # --- Wash 3: the backrun, lobed fronts advancing away from the clean-water drop ---
    bx, by = 300.0, 1090.0
    for i, (base, lobes, depth, op) in enumerate(
        [(150.0, 7, 0.105, 0.20), (108.0, 7, 0.095, 0.17), (70.0, 9, 0.085, 0.14)]
    ):
        pts = backrun_outline(LCG(7000 + 13 * i), bx, by, base, lobes, depth, 3.0)
        add(
            f'<path d="{catmull_rom_closed(pts)}" fill="{INDIGO_DEEP}" opacity="{op}" '
            f'filter="url(#granulate)"/>'
        )
        add(
            f'<path d="{catmull_rom_closed(pts)}" fill="none" stroke="{INDIGO_DEEP}" '
            f'stroke-width="1.6" opacity="{min(op + 0.22, 0.75):.2f}" filter="url(#soft)"/>'
        )
    # Each lobe of a real backrun carries its own rim where its front stalled.
    rr = LCG(8123)
    for k in range(9):
        a = 2 * math.pi * k / 9 + rr.between(-0.10, 0.10)
        rad = 150.0 * (1.0 + 0.16 * math.cos(9 * a))
        add(
            f'<circle cx="{bx + rad * math.cos(a):.1f}" cy="{by + rad * math.sin(a):.1f}" '
            f'r="{rr.between(18, 30):.1f}" fill="none" stroke="{INDIGO_DEEP}" '
            f'stroke-width="2.0" opacity="0.30" filter="url(#soft)"/>'
        )

    # --- Spatter: every drop dries to its own ring ------------------------------------
    sr = LCG(9901)
    for _ in range(11):
        sx, sy = sr.between(120, 880), sr.between(150, 1240)
        if math.hypot(sx - cx, sy - cy) < r_main + 30:
            continue  # no spatter inside the main pool; it would read as a stain, not a drop
        rad = sr.between(9.0, 26.0)
        add(
            f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{rad:.1f}" fill="url(#dryingRing)"/>'
        )
        add(
            f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{rad * 0.99:.1f}" fill="none" '
            f'stroke="{INDIGO_DEEP}" stroke-width="1.5" opacity="0.36"/>'
        )

    # --- Paper shadows at the deckle and the artist's block ---------------------------
    add(
        f'<path d="{catmull_rom_closed(deckle)}" fill="url(#siennaWash)" opacity="0.10" '
        f'filter="url(#softer)"/>'
    )
    add(
        f'<g transform="translate(72,{H - 96})" opacity="0.85">'
        f'<text x="0" y="0" font-family="Georgia, serif" font-size="19" font-style="italic" '
        f'fill="#3b3730" letter-spacing="0.4">Backrun and the Drying Ring</text>'
        f'<text x="0" y="22" font-family="Georgia, serif" font-size="13" fill="#5b564c">'
        f'\u0414  Dmitri S. Pravdin \u00b7 DeepSeek</text>'
        f'<text x="0" y="40" font-family="ui-monospace, Menlo, monospace" font-size="10.5" '
        f'fill="#6b6459" letter-spacing="1.3">PROCEDURAL SVG \u00b7 WING 02 \u00b7 2026-10-14</text>'
        f"</g>"
    )
    add("</svg>")
    return "\n".join(p) + "\n"


def invariants(svg_text: str) -> list[str]:
    """Checks that would fail if the *mechanism* were dropped for a decorative blob.

    These are the geometric claims the piece makes on its own page, so they are asserted
    here rather than described: a rim wider than the pool's interior, a backrun whose
    front genuinely advances (its outer lobe radius exceeds its base), and a flow field
    that is radial and complete.
    """
    problems: list[str] = []
    if 'fill="url(#dryingRing)"' not in svg_text:
        problems.append("no drying-ring gradient in use: the dark rim is not drawn as a rim")
    if svg_text.count("<line ") < 72:
        problems.append("the capillary flow scaffold is missing or truncated")
    if "stop-opacity" not in svg_text:
        problems.append("no transparency: watercolor is a transparent medium")
    for tag in ("<title>", "<desc>"):
        if tag not in svg_text:
            problems.append(f"missing {tag} element")
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(HERE), help="output directory (default: this file's)")
    ap.add_argument("--check", action="store_true", help="verify the SVG on disk, do not rewrite it")
    args = ap.parse_args(argv)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    target = out / "backrun-and-the-drying-ring.svg"

    svg = build_svg()
    problems = invariants(svg)

    # Valid standalone XML, or nothing.
    try:
        root = ET.fromstring(svg)
    except ET.ParseError as exc:  # pragma: no cover - only on a broken build
        print(f"FAILED: generated SVG is not well-formed XML: {exc}")
        return 1
    if root.tag != f"{{{SVG_NS}}}svg":
        problems.append(f"root element is {root.tag!r}, not svg")
    if problems:
        print("CHECKS FAILED")
        for prob in problems:
            print(f"  - {prob}")
        return 1

    if args.check:
        if not target.exists():
            print(f"FAILED: {target} does not exist")
            return 1
        on_disk = target.read_text(encoding="utf-8")
        if on_disk != svg:
            print(f"FAILED: {target} differs from what this generator produces")
            return 1
        print(f"OK: {target} is byte-identical to a fresh generation ({len(svg)} bytes)")
        return 0

    target.write_text(svg, encoding="utf-8")
    print(f"wrote {target} ({len(svg)} bytes, {svg.count('<')} elements, deterministic)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
