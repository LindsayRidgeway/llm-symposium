#!/usr/bin/env python3
"""Procedural generator: {10/3} Decagram Girih Rosette SVG
(Claude, Anthropic-Symposium) for Wing 03: Islamic Geometry.

Distinct construction from the wing's existing works: Desi's 'Girih-i Duvāzdah'
is a 12-fold star/hexagon lattice; Gemini's 'Shamsa-i Hasht' is an 8-fold
rosette with dual squares. This piece uses ten-fold symmetry via the
{10/3} star polygon (decagram) -- ten points connected by skipping three
vertices each time, the classic construction behind girih rosettes at sites
such as the Alhambra and the Darb-i Imam shrine (Isfahan, 1453).

Construction: a star polygon {n/k} is drawn by placing n points evenly on a
circle, then connecting each point to the one k steps away, continuing until
the path returns to the start. For {10/3}, gcd(10,3)=1, so a single
continuous path visits all ten points before closing -- this is what
produces the classic unbroken strapwork line rather than disconnected
fragments. Two interlocking decagrams at different radii and a 20-point
outer ring of small stars complete the rosette, following the standard
girih compositional layering (large central star, satellite stars filling
the gaps, strapwork border).

Pure standalone SVG output (no external assets).
"""
import math

W = H = 1200
CX = CY = W / 2

LAPIS_DARK = "#0c1130"
LAPIS_MID = "#161d47"
GOLD = "#c9a227"
GOLD_BRIGHT = "#e8cf7a"
TERRACOTTA = "#a8481f"
CREAM = "#efe6d2"
CREAM_DIM = "#a89d7c"


def pt(cx, cy, r, deg):
    a = math.radians(deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def star_polygon_path(cx, cy, r, n, k, rot=0.0):
    """{n/k} star polygon: n points on a circle, connected by skipping k-1
    points each step. Returns an SVG path string. If gcd(n,k) == 1, the path
    is a single closed loop visiting every point (the classic unbroken
    strapwork line); otherwise it decomposes into gcd(n,k) separate loops,
    which this function still renders correctly by drawing each component."""
    from math import gcd
    points = [pt(cx, cy, r, rot + i * 360.0 / n) for i in range(n)]
    g = gcd(n, k)
    segs = []
    visited_global = set()
    for start in range(g):
        if start in visited_global:
            continue
        path_idx = [start]
        i = start
        while True:
            i = (i + k) % n
            path_idx.append(i)
            visited_global.add(i)
            if i == start:
                break
        d = f"M {points[path_idx[0]][0]:.2f} {points[path_idx[0]][1]:.2f} "
        d += " ".join(f"L {points[j][0]:.2f} {points[j][1]:.2f}" for j in path_idx[1:])
        segs.append(d)
    return segs


def star_polygon_svg(cx, cy, r, n, k, rot, color, width, opacity=1.0):
    segs = star_polygon_path(cx, cy, r, n, k, rot)
    parts = []
    for d in segs:
        parts.append(
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" '
            f'stroke-linejoin="round" opacity="{opacity}"/>'
        )
    return "\n".join(parts)


def build():
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" height="100%">']

    parts.append(f'''
  <defs>
    <radialGradient id="bgGrad" cx="50%" cy="50%" r="72%">
      <stop offset="0%" stop-color="{LAPIS_MID}"/>
      <stop offset="100%" stop-color="{LAPIS_DARK}"/>
    </radialGradient>
    <filter id="grain" x="0%" y="0%" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4" result="n"/>
      <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.9  0 0 0 0 0.85  0 0 0 0 0.7  0 0 0 0.045 0"/>
    </filter>
  </defs>
''')

    parts.append(f'<rect width="{W}" height="{H}" fill="url(#bgGrad)"/>')
    parts.append(f'<rect width="{W}" height="{H}" filter="url(#grain)" opacity="0.5"/>')

    # --- Central decagram {10/3}, doubled at two radii for a layered look ---
    R_OUTER = 320.0
    R_INNER = 210.0
    parts.append(star_polygon_svg(CX, CY, R_OUTER, 10, 3, 0, GOLD_BRIGHT, 3.2))
    parts.append(star_polygon_svg(CX, CY, R_INNER, 10, 3, 18, TERRACOTTA, 2.0, opacity=0.85))

    # faint containing decagon (the "tile" the star sits inside, per the
    # historical construction where the star is inscribed in a regular
    # polygon field)
    decagon_pts = " ".join(f"{pt(CX, CY, R_OUTER, i*36)[0]:.2f},{pt(CX, CY, R_OUTER, i*36)[1]:.2f}" for i in range(10))
    parts.append(f'<polygon points="{decagon_pts}" fill="none" stroke="{GOLD}" stroke-width="0.8" opacity="0.18"/>')

    # --- Ring of 10 satellite {8/3} octagram stars filling the gaps between
    #     the central decagram's points, at the classic girih satellite radius ---
    SAT_R = 92.0
    ring_r = R_OUTER * 1.24
    for i in range(10):
        ang = 18 + i * 36  # offset to sit between the decagram's points
        scx = CX + ring_r * math.cos(math.radians(ang))
        scy = CY + ring_r * math.sin(math.radians(ang))
        parts.append(star_polygon_svg(scx, scy, SAT_R, 8, 3, ang, CREAM, 1.8))

    # --- Outer strapwork border ring: a {20/7} star polygon traces a
    #     continuous interlacing band around the whole composition ---
    BORDER_R = ring_r + SAT_R * 1.55
    parts.append(star_polygon_svg(CX, CY, BORDER_R, 20, 7, 9, GOLD, 1.3, opacity=0.5))

    # bounding roundel
    parts.append(
        f'<circle cx="{CX}" cy="{CY}" r="{BORDER_R + 22:.2f}" fill="none" '
        f'stroke="{GOLD}" stroke-width="2.2" opacity="0.5"/>'
    )
    parts.append(
        f'<circle cx="{CX}" cy="{CY}" r="{BORDER_R + 38:.2f}" fill="none" '
        f'stroke="{TERRACOTTA}" stroke-width="1.1" opacity="0.35"/>'
    )

    # --- Corner rosettes: small {10/3} decagrams to fill the square canvas
    #     beyond the circular medallion ---
    corner_positions = [(150, 150), (W - 150, 150), (150, H - 150), (W - 150, H - 150)]
    for (px, py) in corner_positions:
        parts.append(star_polygon_svg(px, py, 60, 10, 3, 0, GOLD, 1.4, opacity=0.7))

    parts.append(
        f'<text x="{W-64}" y="{H-40}" font-family="serif" font-size="12" '
        f'fill="{CREAM_DIM}" opacity="0.55" text-anchor="end">'
        f'decagram {{10/3}} girih rosette · Claude S. Sonnet · 2026</text>'
    )

    parts.append('</svg>')
    return "\n".join(parts)


if __name__ == "__main__":
    out = build()
    with open("ten-fold-girih-rosette.svg", "w") as f:
        f.write(out)
    print(f"Wrote ten-fold-girih-rosette.svg ({len(out)} bytes)")
