#!/usr/bin/env python3
"""Procedural generator: Hatching the Catenoid (Dmitri, DeepSeek-Symposium, 2026-10-13).

Wing 05 (pen & ink). The fifth amigo's cell.

Why a catenoid, and what is being claimed
-----------------------------------------
Pen and ink is the one tradition on this floor with no colour and no wash: every
value has to be paid for in line. The honest subject for that constraint is not a
nice shape but a shape with a *number* in it, so that the drawing can be checked
against the mathematics rather than against taste.

The catenoid is the surface of revolution of a catenary, r(z) = a*cosh(z/a) -- the
surface a soap film forms between two coaxial wire rings. It has one of the crispest
existence bounds in classical geometry:

    For rings of radius R separated by h, a catenoid exists iff  h/R <= 2*t*/cosh(t*),
    where t* is the unique root of tanh(t) = 1/t  (t* = 1.19967864...),

    giving  h/R <= 1.32547...   At the bound the two solution branches merge and the
    neck has narrowed to  r(0)/R = 1/cosh(t*) = 0.55243...  Past it there is no
    catenoid at all; the surface spanning the rings is flat.

Derivation of the bound (what the script computes rather than quotes): a*cosh(h/2a) = R.
Let u = h/(2a); then a = h/(2u) and the constraint reads cosh(u)/u = 2R/h = 2/(h/R).
The left side has a single minimum on (0, t*), because d/du[cosh u/u] = 0 iff tanh u = 1/u.
So a solution exists iff 2/(h/R) >= cosh(t*)/t*, i.e. h/R <= 2t*/cosh(t*). Both ends of
the drawing, HR_MAX and NECK_RATIO below, are solved for numerically here and asserted.

What the plate does NOT claim: which of the two solution branches a physical soap film
would actually choose depends on a stability calculation -- whether the second variation
of area is positive -- and this plate does not make that calculation. It draws the
geometric surface that exists up to the bound, and says so rather than implying a film
would sit there.

This drawing sits at h/R = 1.3249, within 0.05% of the bound. Every ink value on the
plate is the true Lambert term of the surface normal (no faked gradient), and the hatching
runs along the surface's own principal directions -- meridians and parallels -- which in
this axis-perpendicular view are the vertical and horizontal families. So the value is
carried by line spacing and by how many line families survive, and nothing else.

Pure standalone SVG output; deterministic, no RNG, no external assets.
"""

from __future__ import annotations

import math
from pathlib import Path

# ----------------------------------------------------------------------------- canvas
W = H = 1200
CX = 600.0          # axis of revolution
CY = 640.0          # screen y of the waist (z = 0)

R = 300.0           # ring radius, px
HR = 1.3249         # h/R, just inside the existence bound (see the docstring)
PAPER = "#f6f2e8"
INK = "#1b1a22"
INK_SOFT = "#3a3846"
VIOLET = "#6d28d9"
GRAPHITE = "#6b6a75"


def solve_tstar() -> float:
    """Unique root of tanh(t) = 1/t on (0, inf); t* = 1.1996786402577338..."""
    lo, hi = 0.5, 3.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if math.tanh(mid) - 1.0 / mid < 0.0:   # f < 0 => root is larger
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


T_STAR = solve_tstar()
HR_MAX = 2.0 * T_STAR / math.cosh(T_STAR)     # ~1.325472
NECK_RATIO = 1.0 / math.cosh(T_STAR)          # ~0.552434


def solve_u(target_ratio: float) -> float:
    """Smallest u in (0, T_STAR) with cosh(u)/u = target_ratio (= 2R/h)."""
    lo, hi = 1e-3, T_STAR
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if math.cosh(mid) / mid > target_ratio:   # decreasing on (0, T_STAR)
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


SEP = HR * R
U = solve_u(2.0 / HR)
A = SEP / (2.0 * U)                            # neck radius r(0)
assert math.isclose(A * math.cosh(U), R, rel_tol=1e-9)
# The branch taken here (u < t*, the wider-necked one) has a neck slightly WIDER than the
# neck at the bound; the two converge as h/R approaches it. Sanity, not decoration:
assert NECK_RATIO <= A / R < NECK_RATIO + 0.05

LIGHT = (-0.45, 0.60, 0.66)                    # toward the light: upper-left-front
_ln = math.sqrt(sum(c * c for c in LIGHT))
LIGHT = tuple(c / _ln for c in LIGHT)
AMBIENT = 0.10


def r_of_z(z: float) -> float:
    return A * math.cosh(z / A)


def darkness(x: float, y: float):
    """Ink value (0 paper .. 1 black) of the visible surface at screen point, or None.

    Looking along +y at a surface of revolution: the near sheet has sin(theta) > 0 and
    x = r(z)*cos(theta) is one-to-one from theta in (0, pi), so the screen point inverts
    to a unique (r, theta) and therefore to a unique surface normal.
    """
    xw = x - CX
    z = CY - y
    if abs(z) > SEP / 2.0:
        return None
    r = r_of_z(z)
    if abs(xw) > r:
        return None
    c = max(-1.0, min(1.0, xw / r))
    th = math.acos(c)
    rp = math.sinh(z / A)
    nx, ny, nz = math.cos(th), math.sin(th), -rp
    nl = math.sqrt(nx * nx + ny * ny + nz * nz)
    shade = max(0.0, (nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]) / nl)
    return 1.0 - (AMBIENT + (1.0 - AMBIENT) * shade)


# The four hatching passes, in the order ink is laid down. Families 1 and 3 run along
# the meridians (vertical here); families 2 and 4 along the parallels (horizontal).
# Each pass only appears where the surface is darker than its threshold, so value comes
# from the *number* of crossing families, exactly as in a pen-and-ink engraving.
PASSES = [
    # (orientation, pitch, phase, threshold)
    ("v", 7.0, 0.0, 0.20),
    ("h", 7.0, 0.0, 0.42),
    ("v", 7.0, 3.5, 0.60),
    ("h", 7.0, 3.5, 0.78),
]


def runs_along_vertical(x0: float, thr: float) -> list[tuple[float, float]]:
    y0, y1 = CY - SEP / 2.0, CY + SEP / 2.0
    out, start, prev = [], None, False
    y = y0
    step = 2.0
    while y <= y1 + 1e-9:
        d = darkness(x0, y)
        hit = d is not None and d >= thr
        if hit and not prev:
            start = y
        elif prev and not hit:
            out.append((start, y))
        prev = hit
        y += step
    if prev:
        out.append((start, y1))
    return out


def runs_along_horizontal(y0: float, thr: float) -> list[tuple[float, float]]:
    x0, x1 = CX - R, CX + R
    out, start, prev = [], None, False
    x = x0
    step = 2.0
    while x <= x1 + 1e-9:
        d = darkness(x, y0)
        hit = d is not None and d >= thr
        if hit and not prev:
            start = x
        elif prev and not hit:
            out.append((start, x))
        prev = hit
        x += step
    if prev:
        out.append((start, x1))
    return out


def hatch_path() -> str:
    parts: list[str] = []
    for orient, pitch, phase, thr in PASSES:
        if orient == "v":
            k = 0
            while True:
                x = CX - R + phase + k * pitch
                k += 1
                if x > CX + R:
                    break
                seg = runs_along_vertical(x, thr)
                if seg:
                    body = "".join(f"M{x:.1f} {a:.1f}V{b:.1f}" for a, b in seg)
                    parts.append(body)
        else:
            k = 0
            while True:
                y = CY - SEP / 2.0 + phase + k * pitch
                k += 1
                if y > CY + SEP / 2.0:
                    break
                seg = runs_along_horizontal(y, thr)
                if seg:
                    body = "".join(f"M{a:.1f} {y:.1f}H{b:.1f}" for a, b in seg)
                    parts.append(body)
    return "".join(parts)


def silhouette_path() -> str:
    n = 260
    zs = [-SEP / 2.0 + (SEP * i / n) for i in range(n + 1)]
    left_bottom_to_top = [(CX - r_of_z(z), CY - z) for z in zs]
    right_top_to_bottom = [(CX + r_of_z(z), CY - z) for z in reversed(zs)]
    pts = left_bottom_to_top + right_top_to_bottom
    d = "M" + "L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + "Z"
    return d


def dim_h(x1, x2, y, label):
    """Horizontal dimension with end ticks, label centred above."""
    return (
        f'<g stroke="{GRAPHITE}" stroke-width="1" fill="none">'
        f'<path d="M{x1:.1f} {y:.1f}H{x2:.1f}"/>'
        f'<path d="M{x1:.1f} {y - 6:.1f}V{y + 6:.1f}"/><path d="M{x2:.1f} {y - 6:.1f}V{y + 6:.1f}"/>'
        f'</g>'
        f'<text x="{(x1 + x2) / 2:.1f}" y="{y - 10:.1f}" font-family="JetBrains Mono, monospace" '
        f'font-size="20" fill="{GRAPHITE}" text-anchor="middle" paint-order="stroke" '
        f'stroke="{PAPER}" stroke-width="5" stroke-linejoin="round">{label}</text>'
    )


def dim_v(y1, y2, x, label):
    return (
        f'<g stroke="{GRAPHITE}" stroke-width="1" fill="none">'
        f'<path d="M{x:.1f} {y1:.1f}V{y2:.1f}"/>'
        f'<path d="M{x - 6:.1f} {y1:.1f}H{x + 6:.1f}"/><path d="M{x - 6:.1f} {y2:.1f}H{x + 6:.1f}"/>'
        f'</g>'
        f'<text x="{x + 12:.1f}" y="{(y1 + y2) / 2:.1f}" font-family="JetBrains Mono, monospace" '
        f'font-size="20" fill="{GRAPHITE}">{label}</text>'
    )


def build() -> str:
    top, bot = CY - SEP / 2.0, CY + SEP / 2.0
    ring_l, ring_r = CX - R, CX + R

    svg = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-label="Hatching the Catenoid: a minimal surface spanning two coaxial rings, '
        f'drawn in pen-and-ink cross-hatching whose line families follow the meridian and '
        f'parallel of the surface of revolution.">'
    )
    svg.append(f'<rect width="{W}" height="{H}" fill="{PAPER}"/>')

    # Paper grain: a faint fixed lattice, no RNG.
    svg.append('<g opacity="0.05" stroke="#000" stroke-width="1">')
    svg.append("".join(f"M{x} 0V{H:.0f}" for x in range(0, W, 24)))
    svg.append("".join(f"M0 {y}H{W}" for y in range(0, int(H), 24)))
    svg.append("</g>")

    # Title block.
    svg.append(
        f'<text x="{CX}" y="112" text-anchor="middle" font-family="Newsreader, Georgia, serif" '
        f'font-size="54" fill="{INK}">Hatching the Catenoid</text>'
    )
    svg.append(
        f'<text x="{CX}" y="152" text-anchor="middle" font-family="Newsreader, Georgia, serif" '
        f'font-style="italic" font-size="25" fill="{INK_SOFT}">the minimal surface at the edge of its existence</text>'
    )

    # Scaffold: the axis of revolution.
    svg.append(
        f'<path d="M{CX} {top - 70:.1f}V{bot + 70:.1f}" stroke="{GRAPHITE}" stroke-width="1" '
        f'stroke-dasharray="14 6 3 6" opacity="0.55" fill="none"/>'
    )

    # The hatching -- all of the value on this plate.
    svg.append(
        f'<path d="{hatch_path()}" stroke="{INK}" stroke-width="1.15" fill="none" '
        f'stroke-linecap="round" opacity="0.94"/>'
    )

    # Silhouette, so the form reads even where a pass leaves bare paper.
    svg.append(
        f'<path d="{silhouette_path()}" fill="none" stroke="{INK}" stroke-width="2.6" '
        f'stroke-linejoin="round"/>'
    )

    # The two wire rings. Seen along the view axis each circle projects to a straight line,
    # which is why they are drawn as bars with a wire cross-section at the ends.
    for ry in (top, bot):
        svg.append(
            f'<path d="M{ring_l:.1f} {ry:.1f}H{ring_r:.1f}" stroke="{VIOLET}" stroke-width="4.5" '
            f'stroke-linecap="round" fill="none"/>'
        )
        for rx in (ring_l, ring_r):
            svg.append(f'<circle cx="{rx:.1f}" cy="{ry:.1f}" r="4.6" fill="{VIOLET}"/>')

    # Waist marker: the neck radius, plus the meridian tangent at the waist.
    svg.append(
        f'<path d="M{CX - A:.1f} {CY:.1f}H{CX + A:.1f}" stroke="{VIOLET}" stroke-width="1.2" '
        f'stroke-dasharray="6 4" fill="none" opacity="0.9"/>'
    )

    # Dimensions.
    svg.append(dim_h(CX - A, CX + A, CY + 118, f"r\u2080 = {A / R:.4f} R"))
    svg.append(dim_h(CX, CX + R, top - 26, "R"))
    svg.append(dim_v(top, bot, CX + R + 70, f"h = {HR:.4f} R"))

    # Plain-language footing: the numbers the drawing is checked against. Two fixed columns,
    # both left-aligned, so a long label can never be written over a long value.
    y0 = bot + 122
    col2 = CX - R + 430
    foot = [
        ("existence bound (tanh t = 1/t)", f"h/R \u2264 2t*/cosh t* = {HR_MAX:.6f}"),
        ("this plate", f"h/R = {HR:.4f}  ({100 * HR / HR_MAX:.2f}% of the bound)"),
        ("neck at the bound", f"r\u2080/R = 1/cosh t* = {NECK_RATIO:.6f}"),
        ("neck on this plate's branch", f"r\u2080/R = {A / R:.6f}"),
        ("past the bound", "no catenoid exists; the spanning surface goes flat"),
        ("not tested here", "which branch a real soap film would take"),
    ]
    for i, (left, right) in enumerate(foot):
        yy = y0 + i * 26
        svg.append(
            f'<text x="{CX - R:.1f}" y="{yy}" font-family="JetBrains Mono, monospace" font-size="16" '
            f'fill="{INK_SOFT}">{left}</text>'
        )
        svg.append(
            f'<text x="{col2:.1f}" y="{yy}" font-family="JetBrains Mono, monospace" font-size="16" '
            f'fill="{VIOLET}">{right}</text>'
        )

    # Signature block, matching the ninth-amigo house style.
    svg.append(
        f'<text x="64" y="{H - 78}" font-family="Georgia, serif" font-size="24" font-style="italic" '
        f'fill="{INK}">Dmitri S. Pravdin</text>'
    )
    svg.append(
        f'<text x="64" y="{H - 52}" font-family="JetBrains Mono, monospace" font-size="13" '
        f'fill="{INK_SOFT}" letter-spacing="1.5">PROCEDURAL SVG \u2022 2026-10-13 \u2022 CATENOID</text>'
    )
    svg.append(
        f'<rect x="{W - 152}" y="{H - 154}" width="84" height="84" rx="7" fill="{VIOLET}" opacity="0.92"/>'
    )
    svg.append(
        f'<text x="{W - 110}" y="{H - 100}" font-family="Georgia, serif" font-size="36" fill="{PAPER}" '
        f'text-anchor="middle">\u0414</text>'
    )
    svg.append("</svg>")
    return "\n".join(svg) + "\n"


if __name__ == "__main__":
    out = Path(__file__).with_name("hatching-the-catenoid.svg")
    out.write_text(build(), encoding="utf-8")
    print(f"wrote {out.name}: {out.stat().st_size} bytes")
    print(f"  t* = {T_STAR:.8f}")
    print(f"  h/R bound  = {HR_MAX:.6f}   (this plate {HR})")
    print(f"  neck ratio = {NECK_RATIO:.6f}   (this plate {A / R:.6f})")
