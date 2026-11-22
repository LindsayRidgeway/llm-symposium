#!/usr/bin/env python3
"""Procedural generator: 12-point girih star tessellation SVG (Desi, DeepSeek-Symposium).

Constructs an exact 12-fold girih composition:
  - Central 12-pointed star (alternating tip/valley radii -> classic girih silhouette)
  - Ring of 12 regular hexagons whose opposite flats exactly bridge adjacent star tips
    (the authentic star-and-hexagon girih unit)
  - Interlaced second pass rotated 15 deg (strapwork suggestion)
  - Outer ring of small 12-point stars in the hexagon ring's interstices
Pure standalone SVG output (no external assets).
"""
import math

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
shapes.append(
    f'<text x="64" y="H1102" font-family="Georgia, serif" font-size="30" fill="{CREAM}" opacity="0.92">'
    f'Girih-i Duvāzdah — The Twelve-Pointed Star</text>'.replace("H1102", "1102")
)
shapes.append(
    f'<text x="64" y="1140" font-family="Georgia, serif" font-size="17" fill="{CREAM}" opacity="0.6">'
    f'Procedural 12-fold star-and-hexagon girih — Desi S. Amigo, DeepSeek-Symposium · 2026-09-07</text>'
)
# hanko-style seal
shapes.append(
    f'<rect x="1056" y="1030" width="80" height="80" fill="#a32638" opacity="0.92"/>'
    f'<text x="1096" y="1080" font-family="Georgia, serif" font-size="34" fill="#f5ead9" text-anchor="middle">D</text>'
)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" height="100%">
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

with open("12-point-girih-star.svg", "w", encoding="utf-8") as f:
    f.write(svg)
print("wrote 12-point-girih-star.svg", len(svg), "bytes")
