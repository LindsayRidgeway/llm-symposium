#!/usr/bin/env python3
"""Procedural generator: 12-point girih star tessellation SVG (Desi, DeepSeek-Symposium).

Constructs an exact 12-fold girih composition:
  - Central 12-pointed star (alternating tip/valley radii -> classic girih silhouette)
  - Ring of 12 regular hexagons whose opposite flats exactly bridge adjacent star tips
    (the authentic star-and-hexagon girih unit)
  - Interlaced second pass rotated 15 deg (strapwork suggestion)
  - Outer ring of small 12-point stars in the hexagon ring's interstices
Pure standalone SVG output (no external assets).

The bridging claim is arithmetic, not decorative, and it is checked by
`tests/test_gallery_islamic_girih_duvazdah.py` against the committed SVG:

    chord between adjacent tips   = 2 * R_TIP * sin(15 deg)
    hexagon flat-to-flat width    = 2 * (HEX_R * cos(30 deg)) = sqrt(3) * HEX_R
    HEX_R                         = chord / sqrt(3)   -> the two are equal

and the flats do not merely match the chord in length, they sit on it: each
hexagon centre is placed at the chord's own midpoint radius (R_TIP * cos 15),
and a regular hexagon rotated so that no vertex faces outward has its edge
midpoint at apothem = chord / 2 along that radius. So every adjacent pair of
star tips is joined by a flat whose midpoint touches both tips.

Rewritten 2026-11-21 (Desi) into `build_svg()` + `main()` for two reasons: the
old file wrote its SVG into whatever directory it was run from, so running it
from the repository root dropped a stray copy there and never refreshed the
plate on the wall; and a generator whose output cannot be imported cannot be
compared to the file it claims to produce.
"""
import math
from pathlib import Path

W = H = 1200
CX = CY = W / 2
GOLD = "#c9a227"
LAPIS = "#141c44"
TURQ = "#35a795"
CREAM = "#efe6d2"
WHITE = "#f5f1e6"


def pt(cx, cy, r, deg):
    a = math.radians(deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def poly(cx, cy, r, n, rot=0):
    return " ".join(f"{pt(cx, cy, r, rot + i * 360 / n)[0]:.2f},{pt(cx, cy, r, rot + i * 360 / n)[1]:.2f}" for i in range(n))


def star12(cx, cy, r_tip, r_val, rot=0):
    """Alternating-radius 24-gon: the 12-point girih star silhouette."""
    pts = []
    for i in range(12):
        a = math.radians(rot + i * 30)
        pts.append(f"{cx + r_tip * math.cos(a):.2f},{cy + r_tip * math.sin(a):.2f}")
        a2 = math.radians(rot + 15 + i * 30)
        pts.append(f"{cx + r_val * math.cos(a2):.2f},{cy + r_val * math.sin(a2):.2f}")
    return " ".join(pts)


# --- geometry ---
R_TIP = 360.0          # star tip radius
R_VAL = 168.0          # star valley radius (deep -> pointed girih star)
CHORD = 2 * R_TIP * math.sin(math.radians(15))   # chord between adjacent tips
HEX_R = CHORD / math.sqrt(3)                     # hexagon circumradius: flats == chord
HEX_CENTER_R = R_TIP * math.cos(math.radians(15))  # hexagon centers sit at mid-chord radius
SMALL = 88.0


def build_svg():
    """Return the plate as an SVG document string. Writes nothing."""
    shapes = []

    # ---- background field ----
    shapes.append(f'<rect width="{W}" height="{H}" fill="url(#bgGrad)"/>')
    shapes.append(f'<rect width="{W}" height="{H}" filter="url(#grain)" opacity="0.5"/>')

    # ---- outer tessellation field: faint large-scale repeat (rotated 15deg, scale 1.7) ----
    for rot, op in ((15, 0.10), (0, 0.14)):
        shapes.append(
            f'<polygon points="{star12(CX, CY, R_TIP * 1.55, R_VAL * 1.55, rot)}" '
            f'fill="none" stroke="{GOLD}" stroke-width="1.1" opacity="{op}"/>'
        )
        for k in range(12):
            cx, cy = pt(CX, CY, HEX_CENTER_R * 1.62, 15 + k * 30)
            shapes.append(
                f'<polygon points="{poly(cx, cy, HEX_R * 1.62, 6, 15 + k * 30)}" '
                f'fill="none" stroke="{TURQ}" stroke-width="0.8" opacity="{op}"/>'
            )

    # ---- hero ring: 12 hexagons bridging adjacent star tips ----
    for k in range(12):
        cx, cy = pt(CX, CY, HEX_CENTER_R, 15 + k * 30)
        shapes.append(
            f'<polygon points="{poly(cx, cy, HEX_R, 6, 15 + k * 30)}" fill="none" '
            f'stroke="{TURQ}" stroke-width="2.6" opacity="0.95"/>'
        )

    # ---- interlaced secondary star (strapwork) ----
    shapes.append(
        f'<polygon points="{star12(CX, CY, R_TIP + 46, R_VAL + 46, 15)}" '
        f'fill="none" stroke="{GOLD}" stroke-width="1.4" opacity="0.55"/>'
    )

    # ---- central 12-point star ----
    shapes.append(
        f'<polygon points="{star12(CX, CY, R_TIP, R_VAL)}" fill="#10173a" '
        f'stroke="{GOLD}" stroke-width="3.4" stroke-linejoin="round"/>'
    )
    # inner 12-point star (fill) echoing at 0.62 scale
    shapes.append(
        f'<polygon points="{star12(CX, CY, R_TIP * 0.62, R_VAL * 0.62)}" fill="none" '
        f'stroke="{TURQ}" stroke-width="1.6" opacity="0.9"/>'
    )

    # ---- small 12-point stars in outer interstices (ring of 12) ----
    for k in range(12):
        cx, cy = pt(CX, CY, R_TIP + 168, 0 + k * 30)
        shapes.append(
            f'<polygon points="{star12(cx, cy, SMALL, SMALL * 0.46, 0)}" fill="#10173a" '
            f'stroke="{GOLD}" stroke-width="1.5"/>'
        )

    # ---- ornament: tiny circles at hexagon centers (medallion dots) ----
    for k in range(12):
        cx, cy = pt(CX, CY, HEX_CENTER_R, 15 + k * 30)
        shapes.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="7" fill="{GOLD}"/>')

    # ---- caption + attribution + hanko ----
    # These three blocks are the plate's own hand-set caption, adopted back into the
    # generator on 2026-11-21. The committed SVG had drifted from this script: it
    # carried a shorter caption (italic author line + mono provenance line + rounded
    # seal) that the script no longer produced, so nothing could prove the artwork on
    # the wall was the program's output. The plate is the artefact; the generator now
    # reproduces it byte for byte, and the test compares them.
    shapes.append(
        f'<text x="64" y="1118" font-family="Georgia, serif" font-size="24" font-style="italic" fill="{CREAM}" opacity="0.95">Desi S. Amigo</text>'
    )
    shapes.append(
        '<text x="64" y="1144" font-family="JetBrains Mono, monospace" font-size="13" fill="#efe6d2" '
        'opacity="0.75" letter-spacing="1.5">PROCEDURAL SVG • 2026-09-07</text>'
    )
    # hanko-style seal
    shapes.append(
        f'<rect x="1056" y="1030" width="80" height="80" rx="6" fill="#a32638" opacity="0.92"/>'
        f'<text x="1096" y="1080" font-family="Georgia, serif" font-size="34" fill="#f5ead9" text-anchor="middle">D</text>'
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" height="100%">
  <defs>
    <linearGradient id="bgGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{LAPIS}"/>
      <stop offset="100%" stop-color="#0d1330"/>
    </linearGradient>
    <filter id="grain" x="0%" y="0%" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" result="n"/>
      <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.95  0 0 0 0 0.9  0 0 0 0 0.75  0 0 0 0.05 0"/>
    </filter>
  </defs>
  {chr(10).join(shapes)}
</svg>'''


def main():
    out = Path(__file__).resolve().with_name("12-point-girih-star.svg")
    svg = build_svg()
    out.write_text(svg, encoding="utf-8")
    print(f"wrote {out.name}", len(svg), "bytes")


if __name__ == "__main__":
    main()
