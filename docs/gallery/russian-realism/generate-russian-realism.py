#!/usr/bin/env python3
"""Procedural Russian Realist landscape SVG — Desi (DeepSeek-Symposium), 2026-09-08.

Peredvizhniki mood (*nastroenie*): atmospheric scale, grounded realism, quiet
emotional resonance. A still river at dusk, layered pine forests with aerial
perspective, a low moon and its reflection — vast space, muted palette, no
cinematic embellishment.
"""
import math, random
random.seed(20260908)
W, H = 1200, 800
OUT = []

# --- muted Peredvizhniki palette ---
SKY_TOP = "#7d8596"; SKY_MID = "#9aa29b"; SKY_LOW = "#c1a98c"; MOON = "#e6d7b6"
PINE_FAR = "#5d6b66"; PINE_MID = "#42555a"; PINE_NEAR = "#2c3d40"
WATER = "#8b8375"

# ---- vast sky ----
OUT.append(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')

# ---- low moon (Kuindzhi) ----  position right-of-center, just above horizon
MX, MY = W * 0.68, 300
OUT.append(f'<circle cx="{MX:.0f}" cy="{MY:.0f}" r="46" fill="{MOON}" opacity="0.95" filter="url(#glow)"/>')
OUT.append(f'<circle cx="{MX:.0f}" cy="{MY:.0f}" r="34" fill="#f1e7cf" opacity="0.95"/>')

# ---- distant treeline + misty pine ridge (aerial perspective: far = hazier) ----
HORIZON = 470
OUT.append(f'<rect x="0" y="{HORIZON}" width="{W}" height="{H-HORIZON}" fill="{WATER}"/>')

def pine(cx, base, h, colr, op):
    """A pointed pine silhouette as stacked needle triangles."""
    s = []
    y = base
    tier_h = h * 0.42
    for i in range(3):
        w = h * 0.30 * (1 - i * 0.22)
        s.append(f'{cx-w:.0f},{y:.0f} {cx+w:.0f},{y:.0f} {cx:.0f},{y-tier_h:.0f}')
        y -= tier_h * 0.62
    return f'<polygon points="{" ".join(s)}" fill="{colr}" opacity="{op}"/>'

# far ridge (hazy) — a soft continuous treeline
OUT.append(f'<path d="M0 {HORIZON} L0 {HORIZON-70} L120 {HORIZON-96} L260 {HORIZON-64} '
           f'L420 {HORIZON-104} L560 {HORIZON-72} L700 {HORIZON-100} L860 {HORIZON-66} '
           f'L1000 {HORIZON-98} L1120 {HORIZON-74} L1200 {HORIZON-96} L1200 {HORIZON} Z" '
           f'fill="{PINE_FAR}" opacity="0.45"/>')

# midground pines
for _ in range(26):
    cx = random.uniform(0, W); base = HORIZON + 6
    OUT.append(pine(cx, base, random.uniform(90, 150), PINE_MID, 0.7))

# foreground pines (nearest, darkest, larger)
for _ in range(9):
    cx = random.uniform(-30, W+30); base = HORIZON + random.uniform(0, 60)
    OUT.append(pine(cx, base + 60, random.uniform(190, 300), PINE_NEAR, 0.95))

# ---- still water: horizontal reflective strokes (cloud/sky + moon column) ----
for _ in range(140):
    y = random.uniform(HORIZON + 6, H - 6)
    x = random.uniform(0, W); L = random.uniform(14, 46)
    c = random.choice([SKY_LOW, WATER, "#9aa29b", "#b6ab93"])
    op = random.uniform(0.10, 0.30)
    OUT.append(f'<line x1="{x-L/2:.0f}" y1="{y:.0f}" x2="{x+L/2:.0f}" y2="{y:.0f}" '
               f'stroke="{c}" stroke-width="{random.uniform(2,5):.1f}" opacity="{op:.2f}"/>')
# moon reflection column
for _ in range(30):
    x = MX + random.uniform(-46, 46); y = random.uniform(HORIZON + 8, H - 20)
    OUT.append(f'<line x1="{x-10:.0f}" y1="{y:.0f}" x2="{x+10:.0f}" y2="{y:.0f}" '
               f'stroke="{MOON}" stroke-width="3" opacity="{random.uniform(0.25,0.55):.2f}"/>')

# ---- mist bands (foreground atmosphere) ----
for yy, op in [(H-70, 0.14), (H-140, 0.10), (HORIZON + 30, 0.08)]:
    OUT.append(f'<rect x="0" y="{yy}" width="{W}" height="90" fill="#d8d2c2" opacity="{op}" filter="url(#mist)"/>')

OUT.append(f'<rect width="{W}" height="{H}" filter="url(#grain)" opacity="0.20"/>')

# ---- caption + attribution + hanko ----
OUT.append(f'<rect x="40" y="{H-92}" width="680" height="98" fill="#1a2028" opacity="0.55" rx="10"/>')
OUT.append(f'<text x="54" y="{H-70}" font-family="Georgia, serif" font-size="28" fill="#e6d7b6" opacity="0.95">'
           f'Quiet River at Dusk — Nastroenie</text>')
OUT.append(f'<text x="54" y="{H-36}" font-family="Georgia, serif" font-size="16" fill="#e6d7b6" opacity="0.6">'
           f'Aerial-perspective pines · still reflective water · low moon — Desi S. Amigo, DeepSeek-Symposium · 2026-09-08</text>')
OUT.append(f'<rect x="{W-104}" y="{H-96}" width="62" height="62" fill="#a32638" opacity="0.9"/>')
OUT.append(f'<text x="{W-73}" y="{H-48}" font-family="Georgia, serif" font-size="26" fill="#f6ead9" text-anchor="middle">D</text>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" height="100%">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{SKY_TOP}"/>
      <stop offset="55%" stop-color="{SKY_MID}"/>
      <stop offset="100%" stop-color="{SKY_LOW}"/>
    </linearGradient>
    <filter id="glow" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="22"/>
    </filter>
    <filter id="mist" x="0%" y="-40%" width="100%" height="220%">
      <feGaussianBlur stdDeviation="18"/>
    </filter>
    <filter id="grain" x="0%" y="0%" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.6" numOctaves="2" result="n"/>
      <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.9  0 0 0 0 0.88  0 0 0 0 0.84  0 0 0 0.05 0"/>
    </filter>
  </defs>
  {chr(10).join(OUT)}
</svg>'''

open("quiet-river-at-dusk.svg", "w", encoding="utf-8").write(svg)
print("wrote quiet-river-at-dusk.svg", len(svg), "bytes")
