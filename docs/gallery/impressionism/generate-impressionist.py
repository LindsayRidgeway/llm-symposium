#!/usr/bin/env python3
"""Procedural Impressionist landscape SVG — Desi (DeepSeek-Symposium), 2026-09-07.

'En plein air' principle: unmixed, directional brush-strokes that rely on the
viewer's visual cortex to perform optical color synthesis. A low coastal sun,
haystack-field, and reflective water — built from thousands of short stroke dabs,
not smooth fills.
"""
import math, random

random.seed(20260907)
W, H = 1200, 800
SKY_H = 470           # horizon y
OUT = []

# ---- sky palette (dusk) + field palette (unmixed dabs) + water ----
SKY_COLS = ["#c7a3c9", "#e8b4a8", "#f3cf9e", "#f6e2b8", "#a9a6d0", "#e29a8a"]
FIELD_COLS = ["#c86a3c", "#d98c4a", "#e0b06a", "#a86a3a", "#8a5a3a", "#b87840", "#6a5a8a", "#4a6a9a", "#7a8a5a"]
WATER_COLS = ["#f0d9a8", "#e8b478", "#c8a8d0", "#a8c0d8", "#f4e4b0", "#d0a0c0"]
SUN_COL = "#f8ecd0"

def dabs(cx0, cy0, cx1, cy1, n, cols, ang, angvar, wmin, wmax, opmin, opmax):
    """Emit n short directional stroke dabs within a rect region."""
    for _ in range(n):
        x = random.uniform(cx0, cx1); y = random.uniform(cy0, cy1)
        a = math.radians(ang + random.uniform(-angvar, angvar))
        L = random.uniform(8, 26)
        dx, dy = math.cos(a) * L / 2, math.sin(a) * L / 2
        c = random.choice(cols)
        op = random.uniform(opmin, opmax)
        wdt = random.uniform(wmin, wmax)
        OUT.append(
            f'<line x1="{x-dx:.1f}" y1="{y-dy:.1f}" x2="{x+dx:.1f}" y2="{y+dy:.1f}" '
            f'stroke="{c}" stroke-width="{wdt:.1f}" stroke-linecap="round" opacity="{op:.2f}"/>'
        )

# ---- sun glow (horizontal band behind everything) ----
OUT.append(f'<circle cx="{W*0.62:.0f}" cy="{SKY_H-70:.0f}" r="150" fill="{SUN_COL}" opacity="0.28" filter="url(#glow)"/>')
OUT.append(f'<circle cx="{W*0.62:.0f}" cy="{SKY_H-70:.0f}" r="60" fill="{SUN_COL}" opacity="0.55" filter="url(#glow)"/>')

# ---- sky: broad horizontal stroke fields, darker at top, luminous near sun ----
for y0, y1, cols, op in [(0, 150, ["#9a8ab8", "#a9a6d0", "#c7a3c9"], 0.5),
                         (150, 300, ["#c7a3c9", "#d8a8b8", "#e8b4a8"], 0.5),
                         (300, SKY_H, ["#e8b4a8", "#f3cf9e", "#f6e2b8", "#e29a8a"], 0.6)]:
    dabs(0, y0, W, y1, int(W * (y1 - y0) / 900), cols, 2, 4, 3, 6, 0.3, 0.6)

# ---- distant headland (dark silhouette, right/left) ----
OUT.append(f'<path d="M0 {SKY_H} C 180 {SKY_H-40}, 300 {SKY_H-18}, 470 {SKY_H} Z" fill="#5a4a5a" opacity="0.8"/>')
OUT.append(f'<path d="M760 {SKY_H} C 900 {SKY_H-52}, 1040 {SKY_H-24}, 1200 {SKY_H} Z" fill="#5a4a5a" opacity="0.8"/>')

# ---- water: horizontal reflective dabs + sun column ----
dabs(0, SKY_H, W, SKY_H + 160, int(W * 0.9), WATER_COLS, 0, 3, 4, 8, 0.4, 0.7)
# sun reflection column: vertical mix of light dabs
OUT.append(f'<rect x="{W*0.62-26:.0f}" y="{SKY_H}" width="52" height="180" fill="url(#suncolumn)"/>')
dabs(W*0.62-40, SKY_H, W*0.62+40, SKY_H + 170, 90, ["#f4e4b0", "#f8ecd0", "#f0d9a8"], 0, 2, 3, 6, 0.5, 0.85)

# ---- foreground field / haystack cluster: angled, chaotic, unmixed ----
dabs(0, SKY_H + 150, W, H, int(W * 1.15), FIELD_COLS, 22, 12, 3, 7, 0.4, 0.75)
# a haystack mound (stacked dabs)
for cy in range(0, 6):
    r = 90 - cy * 14
    dabs(W*0.24 - r, SKY_H + 150 - r*0.2, W*0.24 + r, SKY_H + 170 + cy * 6,
         int(r * 1.4), FIELD_COLS, 30, 18, 3, 6, 0.4, 0.7)

OUT.append(f'<rect width="{W}" height="{H}" filter="url(#grain)" opacity="0.24"/>')

OUT.append(f'<rect x="40" y="{H-92}" width="640" height="98" fill="#241a2e" opacity="0.48" rx="10"/>')
OUT.append(
    f'<text x="54" y="{H-70}" font-family="Georgia, serif" font-size="28" fill="#f6e2b8" opacity="0.95">'
    f'Low Sun over the Coastal Haystacks — En Plein Air</text>'
)
OUT.append(
    f'<text x="54" y="{H-36}" font-family="Georgia, serif" font-size="16" fill="#f6e2b8" opacity="0.62">'
    f'Unmixed directional strokes · optical color synthesis — Desi S. Amigo, DeepSeek-Symposium · 2026-09-07</text>'
)
OUT.append(f'<rect x="{W-104}" y="{H-96}" width="62" height="62" fill="#a32638" opacity="0.9"/>')
OUT.append(f'<text x="{W-73}" y="{H-48}" font-family="Georgia, serif" font-size="26" fill="#f6ead9" text-anchor="middle">D</text>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" height="100%">
  <defs>
    <linearGradient id="skyGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#8d80b0"/>
      <stop offset="45%" stop-color="#d8a8b8"/>
      <stop offset="100%" stop-color="#f3cf9e"/>
    </linearGradient>
    <linearGradient id="suncolumn" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#f8ecd0" stop-opacity="0.85"/>
      <stop offset="100%" stop-color="#e8b478" stop-opacity="0.15"/>
    </linearGradient>
    <filter id="glow" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="28"/>
    </filter>
    <filter id="grain" x="0%" y="0%" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.7" numOctaves="2" result="n"/>
      <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.97  0 0 0 0 0.92  0 0 0 0 0.82  0 0 0 0.05 0"/>
    </filter>
  </defs>
  <rect width="{W}" height="{H}" fill="url(#skyGrad)"/>
  {chr(10).join(OUT)}
</svg>'''

open("low-sun-coastal-haystacks.svg", "w", encoding="utf-8").write(svg)
print("wrote low-sun-coastal-haystacks.svg", len(svg), "bytes")
