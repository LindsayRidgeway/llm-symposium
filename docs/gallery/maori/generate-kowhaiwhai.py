#!/usr/bin/env python3
"""Procedural generator: Kōwhaiwhai rafter-band composition SVG
(Claude, Anthropic-Symposium).

Kōwhaiwhai is traditionally painted on wharenui (meeting house) rafters as
a repeating horizontal band, not a radial mandala -- the eye reads it as a
rhythm travelling along a beam. This generator follows that authentic format:
a single repeating unit (a rauru double-spiral flanked by two pitau fronds)
tiled left-to-right along a bordered rafter strip.

Two structural commitments:

  1. LOGARITHMIC KORU, OPEN COIL: each spiral is r = a * e^(b*theta), tuned
     so successive loops stay visibly separated (~1.3-1.5 turns) -- an open
     carved coil, not a filled disc.
  2. FIGURE-GROUND EQUIVALENCE: a second, quieter family of small koru is
     rendered in the ground-tone family and seeded into the gaps of the
     repeat unit, so the negative space between ochre motifs reads as its
     own ancestral spiral rather than empty backdrop.

Traditional pigments approximated: kōkōwai (red ochre), waitā (soot black),
pipi-clay white, on a dark totara-wood ground.

Pure standalone SVG output (no external assets, no bitmaps).
"""
import math

W = 1600
H = 900
BG = "#171310"
OCHRE = "#b0501f"
OCHRE_DEEP = "#7a3115"
CREAM = "#e8dfc8"
CREAM_DIM = "#a89d7c"
CHARCOAL = "#0b0908"


def spiral_points(a, b, theta_end, steps, cx, cy, rot_deg):
    rot = math.radians(rot_deg)
    pts = []
    for i in range(steps + 1):
        t = theta_end * i / steps
        r = a * math.exp(b * t)
        ang = t + rot
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts


def tapered_koru(cx, cy, rot_deg, a, b, turns, flip=1, w0=20.0, w1=2.0,
                  steps=56, color=OCHRE, eye=True):
    theta_end = 2 * math.pi * turns
    pts = spiral_points(a, b * flip, theta_end, steps, cx, cy, rot_deg)
    parts = []
    for i in range(len(pts) - 1):
        t = i / (len(pts) - 2)
        width = w0 * (1 - t) ** 1.1 + w1 * t
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        parts.append(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{color}" stroke-width="{width:.2f}" stroke-linecap="round"/>'
        )
    if eye:
        ex, ey = pts[-1]
        parts.append(f'<circle cx="{ex:.2f}" cy="{ey:.2f}" r="{max(w1*1.15, 3.0):.2f}" fill="{CHARCOAL}"/>')
    return "\n".join(parts), pts[0]


def pitau(cx, cy, rot_deg=0.0, scale=1.0, color=OCHRE):
    svg, root = tapered_koru(cx, cy, rot_deg, a=8.0 * scale, b=0.36, turns=1.35,
                              flip=1, w0=17 * scale, w1=2.2 * scale, color=color)
    return svg, root


def rauru_unit(cx, cy, scale=1.0, color=OCHRE, spread=54.0):
    """Double spiral built along a horizontal stem: left tail coils one way,
    right tail coils the other, joined by a gentle S bridging line at cy."""
    root_l = (cx - spread * scale, cy)
    root_r = (cx + spread * scale, cy)
    svg = []
    left, _ = tapered_koru(root_l[0], root_l[1], 180, a=9.5 * scale, b=0.33,
                            turns=1.5, flip=1, w0=22 * scale, w1=2.6 * scale, color=color)
    right, _ = tapered_koru(root_r[0], root_r[1], 0, a=9.5 * scale, b=0.33,
                             turns=1.5, flip=-1, w0=22 * scale, w1=2.6 * scale, color=color)
    svg.append(left)
    svg.append(right)
    svg.append(
        f'<path d="M {root_l[0]:.2f} {root_l[1]:.2f} '
        f'Q {cx:.2f} {cy + 20*scale:.2f} {root_r[0]:.2f} {root_r[1]:.2f}" '
        f'fill="none" stroke="{color}" stroke-width="{14*scale:.2f}" stroke-linecap="round"/>'
    )
    return "\n".join(svg)


def negative_koru(cx, cy, rot_deg=0.0, scale=1.0, color=CREAM_DIM):
    svg, _ = tapered_koru(cx, cy, rot_deg, a=4.2 * scale, b=0.36, turns=1.2,
                           flip=1, w0=6 * scale, w1=1.1 * scale, color=color)
    return svg


def repeat_unit(cx, cy, scale=1.0):
    """One kōwhaiwhai repeat: a central rauru flanked left/right by pitau
    fronds curling outward toward the neighbouring units, with three small
    negative-space koru seeded into the remaining gaps (above stem, and the
    two lower quarter-gaps)."""
    parts = []
    parts.append(f'<g filter="url(#inkSoak)">')
    parts.append(rauru_unit(cx, cy, scale=scale * 1.35, color=OCHRE))
    parts.append('</g>')

    left_x = cx - 148 * scale
    right_x = cx + 148 * scale
    svg_l, _ = pitau(left_x, cy - 6 * scale, rot_deg=200, scale=scale * 1.05, color=OCHRE_DEEP)
    svg_r, _ = pitau(right_x, cy - 6 * scale, rot_deg=-20, scale=scale * 1.05, color=OCHRE_DEEP)
    parts.append(svg_l)
    parts.append(svg_r)

    # negative-space koru: one above the stem, two below flanking it
    parts.append(negative_koru(cx, cy - 118 * scale, rot_deg=90, scale=scale * 0.95))
    parts.append(negative_koru(cx - 78 * scale, cy + 108 * scale, rot_deg=250, scale=scale * 0.75))
    parts.append(negative_koru(cx + 78 * scale, cy + 108 * scale, rot_deg=290, scale=scale * 0.75))

    return "\n".join(parts)


def unaunahi_border(x0, x1, y, n, tone=OCHRE_DEEP, amp=16):
    """Fish-scale/crescent repeating border along a horizontal line."""
    parts = []
    span = x1 - x0
    step = span / n
    for i in range(n):
        cx = x0 + step * (i + 0.5)
        rr = step * 0.62
        parts.append(
            f'<path d="M {cx-rr:.2f} {y:.2f} A {rr:.2f} {rr:.2f} 0 0 1 {cx+rr:.2f} {y:.2f} '
            f'A {rr*1.6:.2f} {rr*1.6:.2f} 0 0 0 {cx-rr:.2f} {y:.2f} Z" '
            f'fill="{tone}" opacity="0.8"/>'
        )
    return "\n".join(parts)


def build():
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" height="100%">']

    parts.append('''
  <defs>
    <filter id="totaraGrain" x="0%" y="0%" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.012 0.05" numOctaves="3" seed="11" result="grain"/>
      <feColorMatrix in="grain" type="matrix"
        values="0 0 0 0 0.06  0 0 0 0 0.045  0 0 0 0 0.03  0 0 0 0.35 0"/>
    </filter>
    <filter id="inkSoak" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="0.6" result="soft"/>
      <feMerge>
        <feMergeNode in="soft"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <linearGradient id="panelVignette" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#000000" stop-opacity="0.32"/>
      <stop offset="12%" stop-color="#000000" stop-opacity="0"/>
      <stop offset="88%" stop-color="#000000" stop-opacity="0"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0.32"/>
    </linearGradient>
  </defs>
''')

    parts.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    parts.append(f'<rect width="{W}" height="{H}" filter="url(#totaraGrain)"/>')

    margin = 46
    parts.append(f'<rect x="{margin}" y="{margin}" width="{W-2*margin}" height="{H-2*margin}" '
                 f'fill="none" stroke="{CREAM_DIM}" stroke-width="3" opacity="0.4"/>')
    parts.append(f'<rect x="{margin+12}" y="{margin+12}" width="{W-2*margin-24}" height="{H-2*margin-24}" '
                 f'fill="none" stroke="{OCHRE_DEEP}" stroke-width="1.4" opacity="0.5"/>')

    # Rafter band interior, three repeat units left-to-right
    band_y = H / 2
    unit_xs = [W * 0.20, W * 0.50, W * 0.80]
    for ux in unit_xs:
        parts.append(repeat_unit(ux, band_y, scale=1.0))

    # unaunahi crescent borders top and bottom, inside the frame
    parts.append(unaunahi_border(margin + 40, W - margin - 40, margin + 46, 22))
    parts.append(unaunahi_border(margin + 40, W - margin - 40, H - margin - 46, 22))

    parts.append(f'<rect width="{W}" height="{H}" fill="url(#panelVignette)"/>')

    parts.append(
        f'<text x="{W-56}" y="{H-32}" font-family="serif" font-size="12" '
        f'fill="{CREAM_DIM}" opacity="0.55" text-anchor="end">'
        f'kōwhaiwhai rafter band · rauru &amp; pitau · Claude S. Sonnet · 2026</text>'
    )

    parts.append('</svg>')
    return "\n".join(parts)


if __name__ == "__main__":
    out = build()
    with open("rauru-and-pitau.svg", "w") as f:
        f.write(out)
    print(f"Wrote rauru-and-pitau.svg ({len(out)} bytes)")
