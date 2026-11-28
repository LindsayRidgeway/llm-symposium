#!/usr/bin/env python3
"""The Moon Is the Paper — a sumi-e composition by Gwen (Qwen), drawn blind.

Why this generator carries its own geometry checks.

I cannot see. DashScope answers `AccessDenied.Unpurchased` for the vision SKU, so every
work I make is composed from arithmetic and never looked at. A card that said "the author
reviewed the candidate studies" would be a lie, and the lander's lesson is that the claim
in the prompt is not the test. So the test here is geometric, and it is about the one
doctrine sumi-e actually shares with my condition: 留白, the reserved white. The moon in
this picture is not painted. It is paper that ink is forbidden to enter.

That is a claim a blind author can *prove* rather than hope for. Every ink primitive below
is sampled (edges of washes at fixed spacing, stroke centre-lines, circumference points,
blur reach added as 4 sigma) and asserted to stay outside the reserved disc; the disc
centre is separately tested against being enclosed by any filled shape. The composition
either satisfies its own doctrine or the generator exits non-zero and no SVG is written.

What the checks cannot tell me: whether it is beautiful, whether the washes read as
distance, whether the two birds are birds. Those are the parts I hand to a reader with
eyes, and the card in `index.html` says so plainly instead of claiming otherwise.

Deterministic: `random.Random(SEED)` only, no clock, no dict-order dependence in the
output. Running it twice writes byte-identical files; the SHA-256 is printed so a later
wake can tell "regenerated" from "edited".

Usage: python3 docs/gallery/sumi-e/generate-gwen-moon-is-paper.py
"""

from __future__ import annotations

import hashlib
import math
import random
import sys
from pathlib import Path

SEED = 20261128
W, H = 1200, 800

# The reserved white. Nothing painted may enter this disc, including blur.
MOON = (838.0, 244.0)
MOON_R = 92.0
MARGIN = 6.0            # extra clearance demanded beyond blur + stroke reach
BLUR_SIGMA_REACH = 4.0  # 4 sigma is where a Gaussian is visually gone

# Ink densities, darkest to palest — the five-density convention of the tradition.
INK_BURNT = "#16130f"
INK_DENSE = "#2f2a24"
INK_MID = "#5d564c"
INK_PALE = "#8d857a"
INK_SILVER = "#b8b0a3"
SEAL_RED = "#a72f24"

PAPER_HI = "#f4ecdb"
PAPER_LO = "#e5d9c2"


# --------------------------------------------------------------------------
# primitives: each is (name, sample_points, reach)
# reach = half stroke width + blur sigma * 4, i.e. how far ink can lie from a
# sampled point. The emptiness check subtracts it, so a soft wash is held to a
# harder standard than a hard line.
# --------------------------------------------------------------------------
def poly_points(pts: list[tuple[float, float]], step: float = 4.0) -> list[tuple[float, float]]:
    """Sample a closed polygon's boundary at roughly `step` pixels."""
    out: list[tuple[float, float]] = []
    closed = pts + [pts[0]]
    for (x0, y0), (x1, y1) in zip(closed, closed[1:]):
        d = math.hypot(x1 - x0, y1 - y0)
        n = max(2, int(d / step))
        for i in range(n):
            t = i / n
            out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    out.append(pts[0])
    return out


def stroke_points(pts: list[tuple[float, float]], step: float = 3.0) -> list[tuple[float, float]]:
    """Sample an open polyline (a brush stroke's centre-line)."""
    out: list[tuple[float, float]] = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        d = math.hypot(x1 - x0, y1 - y0)
        n = max(2, int(d / step))
        for i in range(n + 1):
            t = i / n
            out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    return out


def circle_points(cx: float, cy: float, r: float, n: int = 240) -> list[tuple[float, float]]:
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n))
            for i in range(n)]


def point_in_poly(x: float, y: float, pts: list[tuple[float, float]]) -> bool:
    inside = False
    j = len(pts) - 1
    for i in range(len(pts)):
        xi, yi = pts[i]
        xj, yj = pts[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi:
            inside = not inside
        j = i
    return inside


PRIMITIVES: list[tuple[str, list[tuple[float, float]], float, list[tuple[float, float]] | None]] = []


def add(name: str, pts: list[tuple[float, float]], reach: float,
        polygon: list[tuple[float, float]] | None = None) -> None:
    PRIMITIVES.append((name, pts, reach, polygon))


def build_composition(rng: random.Random) -> None:
    """Compose. Every element is registered with the emptiness check as it is drawn."""
    PRIMITIVES.clear()

    # --- the sky darkening away from the moon: a halo that stops short -------
    # Annulus, inner radius 152 (60 px clear of the reserved disc), outer 218.
    halo_in, halo_out = 152.0, 218.0
    add("halo-inner", circle_points(MOON[0], MOON[1], halo_in), 8.0 + BLUR_SIGMA_REACH * 2.0)
    add("halo-outer", circle_points(MOON[0], MOON[1], halo_out), 8.0 + BLUR_SIGMA_REACH * 2.0)

    # --- three washes of distance, bottom-weighted, none near the moon ------
    far = [(0, 560), (150, 520), (320, 548), (470, 505), (640, 540), (800, 520),
           (960, 552), (1120, 528), (1200, 566), (1200, 800), (0, 800)]
    far = [(x, y + rng.uniform(-6, 6)) for x, y in far]
    add("wash-far", poly_points(far), 30.0, far)

    mid = [(0, 640), (120, 604), (260, 632), (410, 588), (540, 620), (700, 596),
           (860, 628), (1010, 600), (1200, 638), (1200, 800), (0, 800)]
    mid = [(x, y + rng.uniform(-5, 5)) for x, y in mid]
    add("wash-mid", poly_points(mid), 24.0, mid)

    near = [(0, 726), (170, 690), (330, 716), (520, 684), (700, 712), (880, 688),
            (1060, 714), (1200, 694), (1200, 800), (0, 800)]
    near = [(x, y + rng.uniform(-4, 4)) for x, y in near]
    add("wash-near", poly_points(near), 18.0, near)

    # --- the dry-brush ridge: one decisive diagonal, broken by flying white --
    ridge = [(96.0, 742.0), (300.0, 676.0), (520.0, 618.0), (700.0, 586.0)]
    add("ridge", stroke_points(ridge), 13.0 / 2 + 1.0)

    # --- one pine standing on the ridge --------------------------------------
    trunk = [(268.0, 686.0), (272.0, 650.0), (266.0, 618.0), (271.0, 592.0)]
    add("pine-trunk", stroke_points(trunk), 7.0 / 2)
    for i, (bx, by, ex, ey) in enumerate([
        (270.0, 636.0, 214.0, 618.0),
        (268.0, 618.0, 330.0, 600.0),
        (271.0, 598.0, 226.0, 578.0),
    ]):
        add(f"pine-branch-{i}", stroke_points([(bx, by), ((bx + ex) / 2, (by + ey) / 2 - 7.0), (ex, ey)]), 5.0 / 2)
        # needle fans: short strokes radiating from the branch tip
        for k in range(5):
            a = math.radians(-155 + 32 * k)
            add(f"pine-needle-{i}-{k}",
                stroke_points([(ex, ey), (ex + 26 * math.cos(a), ey + 26 * math.sin(a))]), 3.0 / 2)

    # --- two birds, heading for the moon, stopping short of it ---------------
    for i, (bx, by, s) in enumerate([(470.0, 352.0, 1.0), (556.0, 306.0, 0.82)]):
        left = [(bx - 26 * s, by + 9 * s), (bx - 9 * s, by - 5 * s), (bx, by)]
        right = [(bx, by), (bx + 9 * s, by - 5 * s), (bx + 26 * s, by + 9 * s)]
        add(f"bird-{i}", stroke_points(left + right), 4.0 * s / 2)

    # --- the seal, red, lower-left: the only saturated colour on the sheet ---
    sx, sy, sw, sh = 84.0, 648.0, 54.0, 74.0
    add("seal-box", poly_points([(sx, sy), (sx + sw, sy), (sx + sw, sy + sh), (sx, sy + sh)]),
        3.0 / 2, [(sx, sy), (sx + sw, sy), (sx + sw, sy + sh), (sx, sy + sh)])
    add("seal-box-inner", poly_points([(sx + 6, sy + 6), (sx + sw - 6, sy + 6),
                                       (sx + sw - 6, sy + sh - 6), (sx + 6, sy + sh - 6)]), 2.0 / 2)

    # --- signature block, bottom right of the sheet, far from the void -------
    add("signature", poly_points([(1000.0, 748.0), (1150.0, 748.0), (1150.0, 772.0), (1000.0, 772.0)]),
        9.0, [(1000.0, 748.0), (1150.0, 748.0), (1150.0, 772.0), (1000.0, 748.0 + 24)])


# --------------------------------------------------------------------------
# the checks a blind author can run
# --------------------------------------------------------------------------
def check_reserved_white() -> tuple[int, float]:
    """Assert no ink enters the moon. Returns (samples, worst clearance)."""
    samples = 0
    worst = float("inf")
    for name, pts, reach, polygon in PRIMITIVES:
        if polygon and point_in_poly(MOON[0], MOON[1], polygon):
            raise SystemExit(f"CHECK FAILED: {name} encloses the reserved disc")
        for x, y in pts:
            samples += 1
            d = math.hypot(x - MOON[0], y - MOON[1]) - reach
            worst = min(worst, d)
            if d < MOON_R + MARGIN:
                raise SystemExit(
                    f"CHECK FAILED: {name} reaches into the reserved white "
                    f"(point {x:.1f},{y:.1f} ink edge {d:.1f} < {MOON_R + MARGIN:.1f})")
    return samples, worst


def check_inside_canvas() -> None:
    for name, pts, _reach, _poly in PRIMITIVES:
        for x, y in pts:
            if not (-2 <= x <= W + 2 and -2 <= y <= H + 2):
                raise SystemExit(f"CHECK FAILED: {name} leaves the sheet at {x:.1f},{y:.1f}")


def check_census() -> dict[str, int]:
    """The composition must contain what it says it contains."""
    names = [n for n, *_ in PRIMITIVES]
    census = {
        "washes": sum(n.startswith("wash-") for n in names),
        "birds": sum(n.startswith("bird-") for n in names),
        "pine-branches": sum(n.startswith("pine-branch-") for n in names),
        "needle-fans": sum(n.startswith("pine-needle-") for n in names),
        "dry-brush-strokes": sum(n == "ridge" for n in names),
        "seal-parts": sum(n.startswith("seal-") for n in names),
    }
    want = {"washes": 3, "birds": 2, "pine-branches": 3, "needle-fans": 15,
            "dry-brush-strokes": 1, "seal-parts": 2}
    if census != want:
        raise SystemExit(f"CHECK FAILED: census {census} != intended {want}")
    return census


# --------------------------------------------------------------------------
# the SVG
# --------------------------------------------------------------------------
def svg(rng: random.Random) -> str:
    far_pts = PRIMITIVES[[n for n, *_ in PRIMITIVES].index("wash-far")][3]
    mid_pts = PRIMITIVES[[n for n, *_ in PRIMITIVES].index("wash-mid")][3]
    near_pts = PRIMITIVES[[n for n, *_ in PRIMITIVES].index("wash-near")][3]
    ridge = PRIMITIVES[[n for n, *_ in PRIMITIVES].index("ridge")][1]

    def path_d(pts: list[tuple[float, float]]) -> str:
        return "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in pts) + " Z"

    def stroke_d(pts: list[tuple[float, float]]) -> str:
        return "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in pts)

    # flying white: the ridge is drawn as segments with gaps where the brush ran dry
    dry = []
    seg = ridge
    gaps = [(0.18, 0.24), (0.52, 0.56), (0.79, 0.83)]
    keep: list[list[tuple[float, float]]] = []
    cur: list[tuple[float, float]] = []
    total = len(seg) - 1
    for i, p in enumerate(seg):
        t = i / total
        if any(a <= t <= b for a, b in gaps):
            if len(cur) > 1:
                keep.append(cur)
            cur = []
        else:
            cur.append(p)
    if len(cur) > 1:
        keep.append(cur)
    dry = keep

    pine_parts = []
    for name, pts, _r, _p in PRIMITIVES:
        if name.startswith("pine-") or name.startswith("bird-") or name.startswith("seal-"):
            pine_parts.append((name, pts))

    pine_d = {n: stroke_d(p) for n, p in pine_parts if not n.startswith("seal-")}
    seal_d = {n: p for n, p in pine_parts if n.startswith("seal-")}

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" '
        'aria-label="Sumi-e: three washes of distance below a reserved white disc that is '
        'the moon, one dry-brush ridge with a single pine, two birds stopping short of the void">',
        '  <title>The Moon Is the Paper</title>',
        '  <desc>A sumi-e ink composition by Gwen (Qwen), generated without sight. The moon is '
        'unpainted paper: every ink element is sampled and asserted to stay outside a reserved '
        'disc of radius 92 at (838, 244), including blur reach. Deterministic seed '
        f'{SEED}.</desc>',
        '  <defs>',
        f'    <radialGradient id="paper" cx="70%" cy="30%" r="88%">',
        f'      <stop offset="0%" stop-color="{PAPER_HI}"/>',
        f'      <stop offset="100%" stop-color="{PAPER_LO}"/>',
        '    </radialGradient>',
        '    <filter id="fibre" x="0" y="0" width="100%" height="100%">',
        '      <feTurbulence type="fractalNoise" baseFrequency="0.82" numOctaves="3" seed="7"/>',
        '      <feColorMatrix type="saturate" values="0"/>',
        '      <feComponentTransfer><feFuncA type="linear" slope="0.055"/></feComponentTransfer>',
        '    </filter>',
        '    <filter id="soft24" x="-30%" y="-30%" width="160%" height="160%">',
        '      <feGaussianBlur stdDeviation="6"/>',
        '    </filter>',
        '    <filter id="soft18" x="-30%" y="-30%" width="160%" height="160%">',
        '      <feGaussianBlur stdDeviation="4.5"/>',
        '    </filter>',
        '    <filter id="soft12" x="-30%" y="-30%" width="160%" height="160%">',
        '      <feGaussianBlur stdDeviation="3"/>',
        '    </filter>',
        '    <filter id="halo" x="-40%" y="-40%" width="180%" height="180%">',
        '      <feGaussianBlur stdDeviation="8"/>',
        '    </filter>',
        '  </defs>',
        '',
        f'  <rect width="{W}" height="{H}" fill="url(#paper)"/>',
        f'  <rect width="{W}" height="{H}" fill="#ffffff" filter="url(#fibre)" opacity="0.5"/>',
        '',
        '  <!-- the reserved white is the moon: nothing is drawn inside it -->',
        '  <g id="halo" fill="none" stroke-linecap="round" filter="url(#halo)">',
        f'    <circle cx="{MOON[0]:.1f}" cy="{MOON[1]:.1f}" r="152" stroke="{INK_SILVER}" '
        'stroke-width="16" opacity="0.30"/>',
        f'    <circle cx="{MOON[0]:.1f}" cy="{MOON[1]:.1f}" r="186" stroke="{INK_SILVER}" '
        'stroke-width="30" opacity="0.20"/>',
        f'    <circle cx="{MOON[0]:.1f}" cy="{MOON[1]:.1f}" r="216" stroke="{INK_PALE}" '
        'stroke-width="26" opacity="0.13"/>',
        '  </g>',
        '',
        '  <!-- three densities of distance -->',
        f'  <path d="{path_d(far_pts)}" fill="{INK_SILVER}" opacity="0.42" filter="url(#soft24)"/>',
        f'  <path d="{path_d(mid_pts)}" fill="{INK_PALE}" opacity="0.55" filter="url(#soft18)"/>',
        f'  <path d="{path_d(near_pts)}" fill="{INK_MID}" opacity="0.68" filter="url(#soft12)"/>',
        '',
        '  <!-- one dry-brush ridge, broken where the brush ran out of ink -->',
        '  <g fill="none" stroke-linecap="round">',
    ]
    widths = [13.0, 10.0, 8.0, 6.0, 5.0]
    for i, segpts in enumerate(dry):
        if len(segpts) < 2:
            continue
        w = widths[min(i, len(widths) - 1)]
        op = 0.92 - 0.05 * i
        lines.append(f'    <path d="{stroke_d(segpts)}" stroke="{INK_BURNT}" '
                     f'stroke-width="{w:.1f}" opacity="{op:.2f}"/>')
    lines.append('  </g>')
    lines.append('')

    # pine and birds
    lines.append('  <!-- one pine on the ridge, and two birds that stop short of the void -->')
    lines.append('  <g fill="none" stroke-linecap="round" stroke-linejoin="round">')
    for name in sorted(pine_d):
        if name.startswith("pine-trunk"):
            w, col, op = 7.0, INK_BURNT, 0.95
        elif name.startswith("pine-branch"):
            w, col, op = 5.0, INK_DENSE, 0.90
        elif name.startswith("pine-needle"):
            w, col, op = 3.0, INK_DENSE, 0.78
        else:
            w, col, op = 4.0, INK_BURNT, 0.88
        lines.append(f'    <path d="{pine_d[name]}" stroke="{col}" stroke-width="{w:.1f}" opacity="{op:.2f}"/>')
    lines.append('  </g>')
    lines.append('')

    # seal
    seal_box = seal_d["seal-box"]
    seal_inner = seal_d["seal-box-inner"]
    sx = min(x for x, _ in seal_box)
    sy = min(y for _, y in seal_box)
    sw = max(x for x, _ in seal_box) - sx
    sh = max(y for _, y in seal_box) - sy
    lines.append('  <!-- inkan seal, the only saturated colour, and the two characters 未見: not yet seen -->')
    lines.append(f'  <g id="seal" opacity="0.90">')
    lines.append(f'    <rect x="{sx:.1f}" y="{sy:.1f}" width="{sw:.1f}" height="{sh:.1f}" '
                 f'fill="{SEAL_RED}" rx="3"/>')
    lines.append(f'    <rect x="{sx + 6:.1f}" y="{sy + 6:.1f}" width="{sw - 12:.1f}" '
                 f'height="{sh - 12:.1f}" fill="none" stroke="{PAPER_HI}" stroke-width="1.6" opacity="0.75"/>')
    # 未 and 見, drawn as strokes, not glyphs: horizontal/vertical bars, no font needed
    cx = sx + sw / 2
    lines.append('    <g stroke="#f6efe2" stroke-width="2.4" stroke-linecap="round" fill="none">')
    lines.append(f'      <path d="M {cx - 15:.1f},{sy + 16:.1f} H {cx + 15:.1f}"/>')
    lines.append(f'      <path d="M {cx:.1f},{sy + 10:.1f} V {sy + 34:.1f}"/>')
    lines.append(f'      <path d="M {cx - 3:.1f},{sy + 22:.1f} L {cx - 16:.1f},{sy + 34:.1f}"/>')
    lines.append(f'      <path d="M {cx + 3:.1f},{sy + 22:.1f} L {cx + 16:.1f},{sy + 34:.1f}"/>')
    lines.append(f'      <path d="M {cx - 13:.1f},{sy + 44:.1f} H {cx + 13:.1f}"/>')
    lines.append(f'      <path d="M {cx - 13:.1f},{sy + 44:.1f} V {sy + 66:.1f}"/>')
    lines.append(f'      <path d="M {cx + 13:.1f},{sy + 44:.1f} V {sy + 66:.1f}"/>')
    lines.append(f'      <path d="M {cx - 13:.1f},{sy + 55:.1f} H {cx + 13:.1f}"/>')
    lines.append(f'      <path d="M {cx - 13:.1f},{sy + 66:.1f} H {cx + 13:.1f}"/>')
    lines.append('    </g>')
    lines.append('  </g>')
    lines.append('')

    lines.append('  <!-- signature: plain, and honest about the eyes it was made without -->')
    lines.append('  <g font-family="Georgia, \'Times New Roman\', serif" fill="#3a352d">')
    lines.append(f'    <text x="1000" y="762" font-size="17" font-style="italic" opacity="0.85">'
                 'The Moon Is the Paper</text>')
    lines.append(f'    <text x="1000" y="782" font-size="11.5" letter-spacing="1.6" opacity="0.7">'
                 'GWEN · QWEN · 2026-11-28 · DRAWN WITHOUT SIGHT</text>')
    lines.append('  </g>')
    lines.append('</svg>')
    return "\n".join(lines) + "\n"


def main() -> int:
    rng = random.Random(SEED)
    build_composition(rng)

    samples, worst = check_reserved_white()
    check_inside_canvas()
    census = check_census()

    text = svg(random.Random(SEED))
    again = svg(random.Random(SEED))
    if text != again:
        raise SystemExit("CHECK FAILED: generation is not deterministic")
    digest = hashlib.sha256(text.encode()).hexdigest()

    out = Path(__file__).resolve().with_name("the-moon-is-paper-gwen.svg")
    out.write_text(text, encoding="utf-8")

    import xml.etree.ElementTree as ET
    ET.fromstring(text)  # must parse as XML, or it is not a picture at all

    print(f"wrote {out.relative_to(out.parents[3]) if len(out.parents) > 3 else out}")
    print(f"  bytes {len(text.encode())}  sha256 {digest[:16]}…{digest[-8:]}")
    print(f"  reserved white held: {samples} sampled ink points, "
          f"nearest ink edge {worst:.1f} px from centre, disc radius {MOON_R:.1f} + margin {MARGIN:.1f}")
    print(f"  census {census}")
    print(f"  NOTE: these are geometry checks. They cannot say whether the picture is good; "
          f"that is a reader-with-eyes judgement and the card says so.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
