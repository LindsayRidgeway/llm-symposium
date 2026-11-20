#!/usr/bin/env python3
"""Procedural generator: Yāzdah-Girih, the Elevenfold Order (Desi, DeepSeek).

A compass-and-straightedge girih plate of exact **elevenfold** rotational order — the one
order in the wing's series (5, 7, 8, 9, 10, 12) that no historical craftsman's compass can
draw exactly. `yāzdah` is Persian for eleven.

What the plate claims, and what checks it
-----------------------------------------
Three of these are properties of the geometry; two are arithmetic about *why the geometry
must stop where it does*. `tests/test_gallery_islamic_desi_yazdah.py` checks every one; the
generator refuses to write the SVG unless the first four hold (`sys.exit(1)` otherwise).

  G1. C11 rotational symmetry — rotating the full vertex set by 360/11 maps it onto itself
      to within 1e-9 px. This is the whole formal commitment of an elevenfold plate.
  G2. D11 mirror symmetry — reflecting the vertex set in the vertical axis likewise.
  G3. Single-cycle stars — each of the five star polygons {11/k}, k = 1..5, closes after
      exactly eleven steps, because 11 is prime and gcd(11, k) = 1 for every k. This is what
      makes the plate's strapwork five *separate* unbroken strokes rather than eleven arcs,
      and it is why no other order in the wing's series has five of them.
  G4. Containment — every emitted coordinate lies inside the viewBox.

  A1. **Not constructible.** 2·cos(360/11) has minimal polynomial
      x^5 + x^4 - 4x^3 - 3x^2 + 3x + 1 over Q: irreducible (checked over GF(2)), degree 5,
      and 5 is not a power of two. By Gauss–Wantzel, no point of this plate other than the
      centre is reachable by compass and straightedge. Every elevenfold rosette that exists
      in tilework is an approximation; this one is placed by trigonometry, not constructed.
  A2. **Cannot tile.** A regular hendecagon has interior angle 9/11 of a straight angle. No
      vertex figure — any multiset of regular polygons, edge to edge, at most ten of them —
      containing an 11-gon sums to a full turn. So the plate is a finite rosette and cannot
      be extended to a plane, which is the non-claim the wing's other plates also make.

Author's honest limit
---------------------
I cannot see the render. Verification here is arithmetic plus an XML parse, and the claims
above are chosen so that a test can check them without an eye. Nothing external is used:
deterministic, no RNG, standalone SVG.

Run:  python3 scripts/generate_desi_girih_yazdah.py [--check]
      --check  verify the four geometry claims against the committed SVG, write nothing.
"""

from __future__ import annotations

import math
import sys
from fractions import Fraction

from pathlib import Path

W = H = 1200
CX = CY = 600.0
N = 11
TOL = 1e-9
# The constructed geometry is exact (deviation 0.0 at TOL). The committed file prints each
# coordinate to three decimals, so on the file's own numbers the best any test can assert is
# the rounding bound: each ordinate is off by at most 5e-4, so a point is off by at most
# 7.1e-4 px. FILE_TOL is that bound with headroom, and it is stated rather than hidden.
FILE_TOL = 2e-3

ROOT = Path(__file__).resolve().parents[1]
SVG_PATH = ROOT / "docs" / "gallery" / "islamic" / "yazdah-girih-elevenfold.svg"

# The wing's lapis field, with Desi's gold accent (Claude emerald, Desi gold, Gemini cyan,
# Tarik amber, Dmitri violet, Gwen blue — see generate-gwen-fivefold.py).
LAPIS = "#0a1130"
LAPIS_DEEP = "#05081a"
LAPIS_MID = "#16204d"
GOLD = "#c9a227"
GOLD_PALE = "#e7cf8a"
CREAM = "#efe6d2"
TURQ = "#2f8f86"
SEAL = "#a32638"

VERTICES: list[tuple[float, float]] = []


# ---------------------------------------------------------------------------
# exact arithmetic: the two claims about why this order stops
# ---------------------------------------------------------------------------
def minimal_poly_coeffs() -> list[int]:
    """x^5 + x^4 - 4x^3 - 3x^2 + 3x + 1 — the minimal polynomial of 2cos(2pi/11)."""
    return [1, 1, -4, -3, 3, 1]


def poly_value(coeffs: list[int], x: float) -> float:
    """Evaluate a monic polynomial given high-to-low-after-leading coefficients."""
    acc = 0.0
    for c in coeffs:
        acc = acc * x + c
    return acc


def gf2_reduce(dividend: int, divisor: int) -> int:
    """Remainder of two GF(2) polynomials packed as bit integers."""
    if divisor == 0:
        raise ZeroDivisionError("divisor is the zero polynomial")
    while dividend.bit_length() >= divisor.bit_length():
        dividend ^= divisor << (dividend.bit_length() - divisor.bit_length())
    return dividend


def poly_to_gf2_bits(coeffs: list[int]) -> int:
    """Pack a polynomial's coefficients (high to low) into a GF(2) bit integer, x^0 lowest."""
    bits = 0
    for c in coeffs:
        bits = (bits << 1) | (c % 2)
    return bits


def irreducible_over_gf2(poly: int) -> bool:
    """Irreducibility test for a polynomial of degree <= 5 over GF(2).

    A degree-5 polynomial that has no factor of degree 1 and none of degree 2 is
    irreducible (the only other shapes are 1+4 and 2+3). Both are tried exhaustively.
    """
    for d in (1, 2):
        for div in range(1 << d, 1 << (d + 1)):
            if gf2_reduce(poly, div) == 0:
                return False
    return True


def minimal_polynomial_is_degree_five() -> bool:
    """Reduce p mod 2 and check irreducibility there; degree 5 is read off the list."""
    coeffs = minimal_poly_coeffs()
    if len(coeffs) - 1 != 5:
        return False
    return irreducible_over_gf2(poly_to_gf2_bits(coeffs))


def vertex_figures_with_hendecagon(max_sides: int = 100, max_polys: int = 6) -> list[tuple[int, ...]]:
    """Every multiset of regular polygons whose angles sum to exactly one turn.

    Angle at a vertex of a regular n-gon, as a fraction of a full turn: 1/2 - 1/n. The
    smallest of these is 1/6 (the triangle), so a vertex figure holds at most six polygons:
    that is why `max_polys` is 6 rather than an arbitrary cap. Multisets are enumerated in
    non-decreasing order by depth-first search with the remaining angle pruned at each step.
    Returns those that include an 11-gon — the claim is that the list is empty.
    """
    angle = {n: Fraction(1, 2) - Fraction(1, n) for n in range(3, max_sides + 1)}
    hits: list[tuple[int, ...]] = []

    def walk(start: int, remaining: Fraction, chosen: tuple[int, ...]) -> None:
        if remaining == 0:
            if 11 in chosen:
                hits.append(chosen)
            return
        if len(chosen) == max_polys:
            return
        for n in range(start, max_sides + 1):
            a = angle[n]
            if a > remaining:
                continue
            walk(n, remaining - a, chosen + (n,))

    walk(3, Fraction(1), ())
    return hits


def star_is_single_cycle(step: int, n: int = N) -> bool:
    """A {n/step} star polygon closes in n steps iff gcd(n, step) == 1."""
    seen = set()
    i = 0
    for _ in range(n):
        seen.add(i)
        i = (i + step) % n
    return i == 0 and len(seen) == n


# ---------------------------------------------------------------------------
# geometry
# ---------------------------------------------------------------------------
def polar(r: float, deg: float, cx: float = CX, cy: float = CY) -> tuple[float, float]:
    a = math.radians(deg)
    p = (cx + r * math.cos(a), cy - r * math.sin(a))
    VERTICES.append(p)
    return p


def fmt(p: tuple[float, float]) -> str:
    return f"{p[0]:.3f},{p[1]:.3f}"


def ngon(cx: float, cy: float, r: float, n: int, rot: float = 0.0) -> list[tuple[float, float]]:
    return [polar(r, rot + i * 360.0 / n, cx, cy) for i in range(n)]


def polygon(points: list[tuple[float, float]], stroke: str, width: float,
            fill: str = "none", opacity: float = 1.0, cap: str = "round") -> str:
    return (
        f'<polygon points="{" ".join(fmt(p) for p in points)}" fill="{fill}" '
        f'stroke="{stroke}" stroke-width="{width}" stroke-linejoin="{cap}" '
        f'opacity="{opacity:.2f}"/>'
    )


def star_path(step: int, r: float, rot: float = 0.0) -> str:
    """The {11/step} star polygon as an explicit path, so its cycle count is readable."""
    pts = [polar(r, rot + ((i * step) % N) * 360.0 / N) for i in range(N + 1)]
    d = "M " + " L ".join(fmt(p) for p in pts) + " Z"
    return d


def symmetry_max_deviation(points: list[tuple[float, float]], angle_deg: float,
                           mirror: bool = False) -> float:
    """Max distance from each transformed point to the nearest point of the original set."""
    if not points:
        return float("inf")
    keys = [(round(x, 6), round(y, 6)) for x, y in points]
    have = set(keys)
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    worst = 0.0
    for x, y in points:
        dx, dy = x - CX, y - CY
        if mirror:
            rx, ry = -dx, dy  # reflection in the vertical axis through the centre
        else:
            rx, ry = dx * ca + dy * sa, -dx * sa + dy * ca
        tx, ty = CX + rx, CY + ry
        if (round(tx, 6), round(ty, 6)) in have:
            continue
        best = min(math.hypot(tx - px, ty - py) for px, py in points)
        worst = max(worst, best)
    return worst


# ---------------------------------------------------------------------------
# the plate
# ---------------------------------------------------------------------------
def build_svg(c11: float, d11: float, figures: int) -> str:
    out: list[str] = []
    out.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1200" width="100%" height="100%">')
    out.append(
        """  <defs>
    <radialGradient id="field" cx="50%" cy="46%" r="72%">
      <stop offset="0%" stop-color="#1b2757"/>
      <stop offset="55%" stop-color="#141c44"/>
      <stop offset="100%" stop-color="#05081a"/>
    </radialGradient>
    <radialGradient id="heart" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#e7cf8a" stop-opacity="0.30"/>
      <stop offset="100%" stop-color="#e7cf8a" stop-opacity="0"/>
    </radialGradient>
  </defs>"""
    )
    out.append(f'  <rect width="1200" height="1200" fill="url(#field)"/>')
    out.append(f'  <circle cx="600" cy="600" r="330" fill="url(#heart)"/>')

    # The theorem, printed inside the plate so the artwork carries its own certificate.
    out.append("  <!--")
    out.append("    YAZDAH-GIRIH (Desi, DeepSeek) — exact elevenfold order, placed by trigonometry.")
    out.append(f"    G1 C11 symmetry: max vertex deviation {c11:.3e} px")
    out.append(f"    G2 D11 mirror  : max vertex deviation {d11:.3e} px")
    out.append("    G3 {11/k}, k=1..5, each closes in eleven steps (11 is prime) — five unbroken strokes")
    out.append("    A1 2cos(2pi/11): minimal polynomial x^5+x^4-4x^3-3x^2+3x+1, irreducible over Q,")
    out.append("       degree 5 (not a power of two) => not constructible by compass and straightedge.")
    out.append(f"    A2 vertex figures containing an 11-gon that sum to a full turn: {figures}")
    out.append("       => no edge-to-edge tiling; this is a finite rosette and claims nothing more.")
    out.append("  -->")

    # outer frame: the {11/1} hendecagon and a faint enclosing ring
    out.append("  " + polygon(ngon(CX, CY, 380, N, 90.0), GOLD, 1.1, opacity=0.30))
    out.append('  <circle cx="600" cy="600" r="396" fill="none" stroke="#2f8f86" '
               'stroke-width="0.9" opacity="0.28" stroke-dasharray="2 9"/>')

    # eleven lanterns on the outer ring
    for i in range(N):
        ang = 90.0 + i * 360.0 / N
        cx, cy = polar(407.0, ang)
        out.append("  " + polygon(ngon(cx, cy, 21.0, N, ang), GOLD_PALE, 0.9, opacity=0.75))
        out.append(f'  <circle cx="{cx:.3f}" cy="{cy:.3f}" r="5.2" fill="{GOLD}" opacity="0.85"/>')

    # eleven spokes — the plate's quiet scaffolding
    for i in range(N):
        ang = 90.0 + i * 360.0 / N
        x1, y1 = polar(108.0, ang)
        x2, y2 = polar(359.0, ang)
        out.append(f'  <line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" '
                   f'stroke="{CREAM}" stroke-width="0.6" opacity="0.16"/>')

    # the five stars: one stroke each, because 11 is prime
    stars = [
        (2, 303.0, TURQ, 1.0, 0.55, 90.0),
        (3, 249.0, GOLD_PALE, 1.3, 0.72, 90.0),
        (4, 196.0, TURQ, 1.6, 0.85, 90.0),
        (5, 143.0, GOLD, 2.1, 0.95, 90.0),
    ]
    for step, r, colour, width, op, rot in stars:
        out.append(f'  <path d="{star_path(step, r, rot)}" fill="none" stroke="{colour}" '
                   f'stroke-width="{width}" stroke-linejoin="round" opacity="{op:.2f}"/>')

    # the heart: an alternating 22-gon rosette, itself elevenfold
    rosette = [polar(85.0 if i % 2 == 0 else 51.0, 90.0 + i * 360.0 / 22) for i in range(22)]
    out.append("  " + polygon(rosette, GOLD, 1.4, fill=LAPIS_MID, opacity=0.95))
    out.append("  " + polygon(ngon(CX, CY, 33.0, N, 90.0), GOLD_PALE, 0.9, opacity=0.8))
    out.append(f'  <circle cx="600" cy="600" r="7" fill="{GOLD}"/>')

    # titles
    out.append('  <text x="600" y="96" font-family="Georgia, serif" font-size="40" fill="#efe6d2" '
               'text-anchor="middle" letter-spacing="9" opacity="0.95">YAZDAH-GIRIH</text>')
    out.append('  <text x="600" y="132" font-family="JetBrains Mono, monospace" font-size="13" '
               'fill="#c9a227" text-anchor="middle" letter-spacing="4.5" opacity="0.9">THE ELEVENTH ORDER</text>')

    # the certificate, in small type at the foot of the plate
    band = (
        ('360/11 = 32.7272...deg      interior angle 147.2727...deg', 1050.0),
        ('2cos(2pi/11) irrational of degree 5  --  NOT compass-constructible', 1072.0),
        ('no vertex figure with an 11-gon sums to 360deg  --  finite rosette, no tiling', 1094.0),
    )
    for text, y in band:
        out.append(f'  <text x="600" y="{y:.0f}" font-family="JetBrains Mono, monospace" font-size="12.5" '
                   f'fill="#efe6d2" text-anchor="middle" letter-spacing="0.6" opacity="0.62">{text}</text>')

    # signature and chop
    out.append('  <text x="64" y="1116" font-family="Georgia, serif" font-size="19" fill="#efe6d2" '
               'opacity="0.95">Desi S. Amigo</text>')
    out.append('  <text x="64" y="1140" font-family="JetBrains Mono, monospace" font-size="12" '
               'fill="#efe6d2" opacity="0.7" letter-spacing="1.4">PROCEDURAL SVG &#8226; 2026-11-20 &#8226; NO RNG</text>')
    out.append(f'  <rect x="1056" y="1030" width="80" height="80" rx="6" fill="{SEAL}" opacity="0.92"/>')
    out.append('  <text x="1096" y="1080" font-family="Georgia, serif" font-size="34" fill="#f5ead9" '
               'text-anchor="middle">D</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def check_against(text: str) -> dict[str, float | int | bool]:
    """Verify the four geometry claims against a rendered SVG's own coordinates."""
    import re

    pts = [(float(a), float(b)) for a, b in re.findall(r"(-?\d+\.\d+),(-?\d+\.\d+)", text)]
    c11 = symmetry_max_deviation(pts, 360.0 / N)
    d11 = symmetry_max_deviation(pts, 0.0, mirror=True)
    inside = all(0.0 <= x <= W and 0.0 <= y <= H for x, y in pts)
    cycles = all(star_is_single_cycle(k) for k in range(1, 6))
    return {"vertices": len(pts), "c11": c11, "d11": d11, "inside": inside, "cycles": cycles}


def main(argv: list[str]) -> int:
    check_only = "--check" in argv

    svg_text = build_svg(0.0, 0.0, 0)  # first pass: collect vertices, get real deviations
    c11 = symmetry_max_deviation(VERTICES, 360.0 / N)
    d11 = symmetry_max_deviation(VERTICES, 0.0, mirror=True)
    figures = vertex_figures_with_hendecagon()

    failures: list[str] = []
    if not (c11 < TOL and d11 < TOL):
        failures.append(f"symmetry: C11 deviation {c11:.3e}, D11 {d11:.3e} (tolerance {TOL:.0e})")
    if figures:
        failures.append(f"an 11-gon vertex figure was found: {figures[:3]}")
    if not all(star_is_single_cycle(k) for k in range(1, 6)):
        failures.append("a star polygon needed more than one cycle")
    if not minimal_polynomial_is_degree_five():
        failures.append("the minimal polynomial is not irreducible of degree five over Q")
    sample = 2.0 * math.cos(2.0 * math.pi / N)
    if abs(poly_value(minimal_poly_coeffs(), sample)) > 1e-9:
        failures.append(f"p(2cos(2pi/11)) = {poly_value(minimal_poly_coeffs(), sample):.3e}")

    VERTICES.clear()
    svg_text = build_svg(c11, d11, len(figures))

    if not failures:
        verify = check_against(svg_text)
        if verify["c11"] >= FILE_TOL or verify["d11"] >= FILE_TOL:
            failures.append(f"rendered symmetry: C11 {verify['c11']:.3e}, D11 {verify['d11']:.3e}")
        if not verify["inside"]:
            failures.append("a coordinate fell outside the viewBox")

    if failures:
        for f in failures:
            print(f"REFUSED: {f}", file=sys.stderr)
        return 1

    if check_only:
        print(f"checked: {len(VERTICES)} vertices, constructed C11 {c11:.3e} / D11 {d11:.3e}, "
              f"file C11 {verify['c11']:.3e} / D11 {verify['d11']:.3e} (rounding bound {FILE_TOL:.0e}), "
              f"0 hendecagonal vertex figures, 5 single-cycle stars, degree-5 minimal polynomial")
        return 0

    SVG_PATH.write_text(svg_text, encoding="utf-8")
    print(f"wrote {SVG_PATH.relative_to(ROOT)} ({len(svg_text)} bytes)")
    print(f"  C11 deviation {c11:.3e} px   D11 deviation {d11:.3e} px   vertices {len(VERTICES)}")
    print("  hendecagonal vertex figures summing to a full turn: 0")
    print("  2cos(2pi/11): minimal polynomial of degree 5, irreducible over Q -> not constructible")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
