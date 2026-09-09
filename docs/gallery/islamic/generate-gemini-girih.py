#!/usr/bin/env python3
"""Procedural generator: 8-Fold Shamsa & Interlocking Girih Rosette SVG.
Authored by Gemini S. Lumina (Google/Gemini-Symposium) for Wing 03: Islamic Geometry.

Mathematical construction:
  - Central 8-pointed star (Khatam) with dual interlaced squares (Rub el Hizb)
  - 16-fold radiant Shamsa (sunburst medallion) petal envelope
  - 8 radiating satellite Khatam stars at exact geometric offset
  - Interlocking octagonal strapwork ribbons with interlaced weave
  - Authentic Andalusian & Seljuk palette: Lapis lazuli, Persian turquoise, burnished gold, cream
"""
import math
import os

W = H = 1200
CX = CY = W / 2

# Palette
LAPIS_DARK = "#091024"
LAPIS_MID = "#122046"
LAPIS_LIGHT = "#1b3066"
GOLD = "#d4af37"
GOLD_BRIGHT = "#f3e5ab"
TURQ = "#2ba89c"
TURQ_LIGHT = "#5eead4"
TERRACOTTA = "#c2593f"
CREAM = "#fbf7ee"
CREAM_MUTED = "#ded6c5"

def pt(cx, cy, r, deg):
    a = math.radians(deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))

def star_points(cx, cy, r_tip, r_val, n, rot=0):
    pts = []
    step = 360.0 / n
    half = step / 2.0
    for i in range(n):
        a_tip = rot + i * step
        pts.append(pt(cx, cy, r_tip, a_tip))
        a_val = rot + i * step + half
        pts.append(pt(cx, cy, r_val, a_val))
    return pts

def pts_str(pts):
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)

def poly_regular(cx, cy, r, n, rot=0):
    pts = [pt(cx, cy, r, rot + i * 360.0 / n) for i in range(n)]
    return pts_str(pts)

shapes = []

# --- Background Field with Radial Islamic Geometry Gradient & Texture ---
shapes.append(f'<rect width="{W}" height="{H}" fill="url(#bgGrad)"/>')
shapes.append(f'<rect width="{W}" height="{H}" filter="url(#grain)" opacity="0.45"/>')

# --- Subtle Background 8-Fold Grid Lattice ---
for r in [520, 440, 360, 280, 200]:
    shapes.append(f'<circle cx="{CX}" cy="{CY}" r="{r}" fill="none" stroke="{GOLD}" stroke-width="0.8" opacity="0.18" stroke-dasharray="4,6"/>')

for i in range(16):
    a = i * 22.5
    x1, y1 = pt(CX, CY, 80, a)
    x2, y2 = pt(CX, CY, 560, a)
    shapes.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{GOLD}" stroke-width="0.8" opacity="0.15"/>')

# --- Outer Arabesque / Ray Ring (Shamsa Crown) ---
RAY_OUTER = 530
RAY_INNER = 475
ray_pts = []
for i in range(32):
    a_tip = i * 11.25
    a_val = a_tip + 5.625
    r_t = RAY_OUTER if i % 2 == 0 else (RAY_OUTER - 25)
    ray_pts.append(pt(CX, CY, r_t, a_tip))
    ray_pts.append(pt(CX, CY, RAY_INNER, a_val))
shapes.append(f'<polygon points="{pts_str(ray_pts)}" fill="none" stroke="{GOLD}" stroke-width="1.6" opacity="0.85"/>')

# Outer border rings
shapes.append(f'<circle cx="{CX}" cy="{CY}" r="{RAY_INNER}" fill="none" stroke="{TURQ}" stroke-width="2.2" opacity="0.9"/>')
shapes.append(f'<circle cx="{CX}" cy="{CY}" r="{RAY_INNER - 12}" fill="none" stroke="{GOLD}" stroke-width="1.2" opacity="0.75"/>')

# --- 8 Satellite Khatam Stars in Outer Ring ---
SAT_R = 365
for i in range(8):
    a = i * 45 + 22.5
    scx, scy = pt(CX, CY, SAT_R, a)
    
    # Outer 8-star
    s_pts = star_points(scx, scy, 75, 42, 8, rot=a)
    shapes.append(f'<polygon points="{pts_str(s_pts)}" fill="{LAPIS_MID}" stroke="{GOLD}" stroke-width="2.2"/>')
    
    # Inner 8-star
    s_in_pts = star_points(scx, scy, 40, 22, 8, rot=a + 22.5)
    shapes.append(f'<polygon points="{pts_str(s_in_pts)}" fill="{TURQ}" stroke="{GOLD_BRIGHT}" stroke-width="1.2" opacity="0.9"/>')
    
    # Center jewel
    shapes.append(f'<circle cx="{scx:.2f}" cy="{scy:.2f}" r="6" fill="{GOLD_BRIGHT}"/>')

# --- Interlocking Strapwork Ribbon: 8 Intersecting Octagonal Squares ---
for rot in [0, 22.5, 45, 67.5]:
    # Wide ribbon shadow
    shapes.append(f'<polygon points="{poly_regular(CX, CY, 380, 4, rot)}" fill="none" stroke="#040814" stroke-width="14" opacity="0.6"/>')
    # Wide ribbon strap
    shapes.append(f'<polygon points="{poly_regular(CX, CY, 380, 4, rot)}" fill="none" stroke="{GOLD}" stroke-width="7" opacity="0.95"/>')
    # Inner inlay line
    shapes.append(f'<polygon points="{poly_regular(CX, CY, 380, 4, rot)}" fill="none" stroke="{LAPIS_DARK}" stroke-width="2.2" opacity="0.9"/>')

# --- Middle Rosette Ring (16-Pointed Star Rosette) ---
MID_TIP = 260
MID_VAL = 165
mid_pts = star_points(CX, CY, MID_TIP, MID_VAL, 16, rot=11.25)
shapes.append(f'<polygon points="{pts_str(mid_pts)}" fill="{LAPIS_LIGHT}" stroke="{GOLD}" stroke-width="3.2" stroke-linejoin="round"/>')

# Inlaid 16-point petals
for i in range(16):
    a = i * 22.5 + 11.25
    tip_x, tip_y = pt(CX, CY, MID_TIP - 6, a)
    base_l = pt(CX, CY, MID_VAL + 10, a - 9)
    base_r = pt(CX, CY, MID_VAL + 10, a + 9)
    petal_pts = f"{tip_x:.2f},{tip_y:.2f} {base_l[0]:.2f},{base_l[1]:.2f} {CX:.2f},{CY:.2f} {base_r[0]:.2f},{base_r[1]:.2f}"
    color = TURQ if i % 2 == 0 else TERRACOTTA
    shapes.append(f'<polygon points="{petal_pts}" fill="{color}" stroke="{GOLD}" stroke-width="1.2" opacity="0.88"/>')

# --- Central Medallion (Hero 8-Pointed Khatam Star) ---
HERO_TIP = 168
HERO_VAL = 92
hero_pts = star_points(CX, CY, HERO_TIP, HERO_VAL, 8, rot=0)
# Shadow
shapes.append(f'<polygon points="{pts_str(hero_pts)}" fill="none" stroke="#03060f" stroke-width="16" opacity="0.5"/>')
# Hero star fill
shapes.append(f'<polygon points="{pts_str(hero_pts)}" fill="{LAPIS_DARK}" stroke="{GOLD}" stroke-width="4" stroke-linejoin="round"/>')

# Dual Intersecting Squares (Rub el Hizb)
sq1 = poly_regular(CX, CY, HERO_TIP, 4, rot=0)
sq2 = poly_regular(CX, CY, HERO_TIP, 4, rot=45)
shapes.append(f'<polygon points="{sq1}" fill="none" stroke="{GOLD_BRIGHT}" stroke-width="2.5" opacity="0.95"/>')
shapes.append(f'<polygon points="{sq2}" fill="none" stroke="{GOLD_BRIGHT}" stroke-width="2.5" opacity="0.95"/>')

# Inner Core Rosette (8-point golden core)
CORE_TIP = 72
CORE_VAL = 42
core_pts = star_points(CX, CY, CORE_TIP, CORE_VAL, 8, rot=22.5)
shapes.append(f'<polygon points="{pts_str(core_pts)}" fill="{GOLD}" stroke="{GOLD_BRIGHT}" stroke-width="1.8"/>')

# Center Sun Jewel
shapes.append(f'<circle cx="{CX}" cy="{CY}" r="18" fill="{TURQ}" stroke="{GOLD_BRIGHT}" stroke-width="2"/>')
shapes.append(f'<circle cx="{CX}" cy="{CY}" r="7" fill="{GOLD_BRIGHT}"/>')

# Corner ornamental cornerpieces (Spandrel L-girih)
CORNER_DIST = 530
for cx, cy, rot in [(80, 80, 0), (W-80, 80, 90), (W-80, H-80, 180), (80, H-80, 270)]:
    c_pts = star_points(cx, cy, 60, 32, 8, rot=rot)
    shapes.append(f'<polygon points="{pts_str(c_pts)}" fill="{LAPIS_MID}" stroke="{GOLD}" stroke-width="1.5" opacity="0.8"/>')

# --- Typography & Provenance ---
shapes.append(
    f'<text x="64" y="1105" font-family="Newsreader, Georgia, serif" font-size="30" font-weight="600" fill="{CREAM}" opacity="0.95" letter-spacing="0.5">'
    f'Shamsa-i Hasht — The Eight-Fold Radiant Medallion</text>'
)
shapes.append(
    f'<text x="64" y="1142" font-family="Plus Jakarta Sans, sans-serif" font-size="16" fill="{CREAM_MUTED}" opacity="0.75" letter-spacing="0.2">'
    f'Procedural 8-fold Khatam and Shamsa star geometry — Gemini S. Lumina (Google) · 2026-09-09</text>'
)

# Gemini Emblem / Hallmark
shapes.append(
    f'<rect x="1056" y="1030" width="80" height="80" rx="8" fill="{TURQ}" stroke="{GOLD}" stroke-width="2" opacity="0.9"/>'
)
shapes.append(
    f'<text x="1096" y="1078" font-family="Newsreader, Georgia, serif" font-size="32" font-weight="bold" fill="{CREAM}" text-anchor="middle">♊</text>'
)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" height="100%">
  <defs>
    <radialGradient id="bgGrad" cx="50%" cy="50%" r="75%">
      <stop offset="0%" stop-color="#14234d"/>
      <stop offset="45%" stop-color="#0a1228"/>
      <stop offset="100%" stop-color="#040711"/>
    </radialGradient>
    <filter id="grain" x="0%" y="0%" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" result="noise"/>
      <feColorMatrix in="noise" type="matrix" values="0 0 0 0 0.95  0 0 0 0 0.9  0 0 0 0 0.75  0 0 0 0.04 0"/>
    </filter>
  </defs>
  {chr(10).join(shapes)}
</svg>'''

out_path = os.path.join(os.path.dirname(__file__), "shamsa-girih-hasht.svg")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"Generated {out_path} ({len(svg)} bytes)")
