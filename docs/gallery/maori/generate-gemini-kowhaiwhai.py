#!/usr/bin/env python3
"""Procedural generator: Mangōpare (Hammerhead) Kōwhaiwhai Rafter Band SVG.
Authored by Gemini S. Lumina (Google/Gemini-Symposium) for Wing 04: Māori Kōwhaiwhai.

Formal characteristics:
  - Mangōpare (hammerhead shark) motif: dual back-to-back koru bulbs symbolizing strength & tenacity
  - Pure logarithmic spiral curvature (r = a * e^(b*theta)) forming the unfurling fern fronds (pitau)
  - Figure-ground equivalence: interlocking positive red/black enamel and negative bone/cream ground
  - Continuous horizontal rafter (heke) band framing with traditional unaunahi crescent notches
"""
import math
import os

W = 1200
H = 400

OCHRE_RED = "#8b1e2d"
CARBON_BLACK = "#181614"
BONE_CREAM = "#f4efe4"
BONE_DARK = "#ded7c8"

def koru_spiral_path(cx, cy, scale, rot_deg=0, flip_y=False):
    """Generates a logarithmic koru spiral path with expanding bulb and returning taper."""
    points_outer = []
    points_inner = []
    
    rot = math.radians(rot_deg)
    
    # Outer expanding curve (pitau stalk to bulb)
    # theta from 0 to 4*pi
    steps = 60
    b = 0.18
    a_init = 3.5 * scale
    
    for i in range(steps + 1):
        t = (i / steps) * (3.4 * math.pi)
        r = a_init * math.exp(b * t)
        x = r * math.cos(t)
        y = r * math.sin(t)
        if flip_y:
            y = -y
        # Rotate
        rx = x * math.cos(rot) - y * math.sin(rot)
        ry = x * math.sin(rot) + y * math.cos(rot)
        points_outer.append((cx + rx, cy + ry))
        
    # Inner returning curve (tapering back to form closed filled koru lobe)
    for i in range(steps, -1, -1):
        t = (i / steps) * (3.4 * math.pi)
        # Offset inner radius to create thickness that bulges at apex and tapers at tail
        thickness = (1.0 - (i / steps) * 0.7) * (14.0 * scale)
        r = max(2.0, a_init * math.exp(b * t) - thickness)
        x = r * math.cos(t)
        y = r * math.sin(t)
        if flip_y:
            y = -y
        rx = x * math.cos(rot) - y * math.sin(rot)
        ry = x * math.sin(rot) + y * math.cos(rot)
        points_inner.append((cx + rx, cy + ry))
        
    pts = points_outer + points_inner
    d = "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in pts) + " Z"
    return d

svg_elements = []

# Background rafter field
svg_elements.append(f'<rect width="{W}" height="{H}" fill="{BONE_CREAM}"/>')
svg_elements.append(f'<rect width="{W}" height="{H}" filter="url(#woodGrain)" opacity="0.35"/>')

# Rafter border margins (kauwhata rails)
svg_elements.append(f'<rect x="0" y="0" width="{W}" height="32" fill="{CARBON_BLACK}"/>')
svg_elements.append(f'<rect x="0" y="{H-32}" width="{W}" height="32" fill="{CARBON_BLACK}"/>')
svg_elements.append(f'<line x1="0" y1="36" x2="{W}" y2="36" stroke="{OCHRE_RED}" stroke-width="4"/>')
svg_elements.append(f'<line x1="0" y1="{H-36}" x2="{W}" y2="{H-36}" stroke="{OCHRE_RED}" stroke-width="4"/>')

# Unaunahi (crescent fish-scale / notch border motifs along top and bottom rails)
for x in range(25, W, 40):
    # Top notches
    svg_elements.append(f'<path d="M {x},42 Q {x+15},56 {x+30},42 Z" fill="{OCHRE_RED}"/>')
    # Bottom notches
    svg_elements.append(f'<path d="M {x},{H-42} Q {x+15},{H-56} {x+30},{H-42} Z" fill="{OCHRE_RED}"/>')

# Central Rafter Pattern: Repeating Mangōpare Units (Hammerhead dual-spiral)
# Each unit consists of central diamond connecting two mirrored koru pairs (red & black)
UNIT_WIDTH = 240
NUM_UNITS = 5
CY = H / 2

for u in range(NUM_UNITS):
    ux = 120 + u * UNIT_WIDTH
    
    # Center chevron / diamond anchor (manawa - heart)
    d_pts = f"{ux-40:.2f},{CY:.2f} {ux:.2f},{CY-50:.2f} {ux+40:.2f},{CY:.2f} {ux:.2f},{CY+50:.2f}"
    svg_elements.append(f'<polygon points="{d_pts}" fill="{CARBON_BLACK}"/>')
    d_in_pts = f"{ux-22:.2f},{CY:.2f} {ux:.2f},{CY-28:.2f} {ux+22:.2f},{CY:.2f} {ux:.2f},{CY+28:.2f}"
    svg_elements.append(f'<polygon points="{d_in_pts}" fill="{OCHRE_RED}"/>')
    
    # 4 Koru Fronds per Mangōpare unit:
    # 1. Top-Left (Ochre Red)
    p1 = koru_spiral_path(ux - 18, CY - 20, scale=1.45, rot_deg=140, flip_y=False)
    svg_elements.append(f'<path d="{p1}" fill="{OCHRE_RED}" stroke="{CARBON_BLACK}" stroke-width="1.5"/>')
    # Bulb center dot
    svg_elements.append(f'<circle cx="{ux - 78:.2f}" cy="{CY - 75:.2f}" r="9" fill="{BONE_CREAM}"/>')
    
    # 2. Top-Right (Ochre Red)
    p2 = koru_spiral_path(ux + 18, CY - 20, scale=1.45, rot_deg=40, flip_y=True)
    svg_elements.append(f'<path d="{p2}" fill="{OCHRE_RED}" stroke="{CARBON_BLACK}" stroke-width="1.5"/>')
    svg_elements.append(f'<circle cx="{ux + 78:.2f}" cy="{CY - 75:.2f}" r="9" fill="{BONE_CREAM}"/>')
    
    # 3. Bottom-Left (Carbon Black)
    p3 = koru_spiral_path(ux - 18, CY + 20, scale=1.45, rot_deg=220, flip_y=True)
    svg_elements.append(f'<path d="{p3}" fill="{CARBON_BLACK}" stroke="{OCHRE_RED}" stroke-width="1.5"/>')
    svg_elements.append(f'<circle cx="{ux - 78:.2f}" cy="{CY + 75:.2f}" r="9" fill="{BONE_CREAM}"/>')
    
    # 4. Bottom-Right (Carbon Black)
    p4 = koru_spiral_path(ux + 18, CY + 20, scale=1.45, rot_deg=-40, flip_y=False)
    svg_elements.append(f'<path d="{p4}" fill="{CARBON_BLACK}" stroke="{OCHRE_RED}" stroke-width="1.5"/>')
    svg_elements.append(f'<circle cx="{ux + 78:.2f}" cy="{CY + 75:.2f}" r="9" fill="{BONE_CREAM}"/>')
    
    # Interlocking connecting ribbons between units
    if u < NUM_UNITS - 1:
        cx_mid = ux + UNIT_WIDTH / 2
        # Upper connecting bridge
        svg_elements.append(f'<path d="M {ux+40},{CY-40} Q {cx_mid},{CY-85} {ux+UNIT_WIDTH-40},{CY-40} Q {cx_mid},{CY-65} {ux+40},{CY-40} Z" fill="{CARBON_BLACK}"/>')
        # Lower connecting bridge
        svg_elements.append(f'<path d="M {ux+40},{CY+40} Q {cx_mid},{CY+85} {ux+UNIT_WIDTH-40},{CY+40} Q {cx_mid},{CY+65} {ux+40},{CY+40} Z" fill="{OCHRE_RED}"/>')

# Caption & Provenance (Discreet on Rafter Bottom)
svg_elements.append(
    f'<text x="24" y="{H-12}" font-family="Newsreader, Georgia, serif" font-size="14" fill="{BONE_CREAM}" opacity="0.9">'
    f'Mangōpare — The Hammerhead Koru (Wing 04)</text>'
)
svg_elements.append(
    f'<text x="{W-24}" y="{H-12}" font-family="JetBrains Mono, monospace" font-size="12" fill="{BONE_CREAM}" opacity="0.75" text-anchor="end">'
    f'Gemini S. Lumina (Google) · 2026-09-09</text>'
)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" height="100%" role="img" aria-label="Kōwhaiwhai — Mangōpare (The Hammerhead Koru)">
  <title>Kōwhaiwhai — Mangōpare</title>
  <defs>
    <filter id="woodGrain" x="0%" y="0%" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.03 0.2" numOctaves="3" result="noise"/>
      <feColorMatrix in="noise" type="matrix" values="0 0 0 0 0.8  0 0 0 0 0.75  0 0 0 0 0.65  0 0 0 0.12 0"/>
    </filter>
  </defs>
  {chr(10).join(svg_elements)}
</svg>'''

out_path = os.path.join(os.path.dirname(__file__), "kowhaiwhai-mangopare.svg")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"Generated {out_path} ({len(svg)} bytes)")
