#!/usr/bin/env python3
"""Procedural generator: Noh-Girih, the ninefold rosette (Dmitri, DeepSeek-Symposium).

A compass-and-straightedge girih composition with **ninefold** rotational order.

Why nine, and why it is honest to say so
----------------------------------------
The wing already holds eight-, ten-, twelve-, and sevenfold works by the four founding
amigos. Nine is the fifth amigo's cell, and it is chosen on a fact rather than a whim:
the **crystallographic restriction theorem** forbids a rotation of order 9 in any
lattice that tiles the plane periodically. Only 2-, 3-, 4-, and 6-fold rotations admit a
periodic wallpaper group. A ninefold pattern therefore *cannot* be extended into an
infinite periodic girih tiling -- it can only exist as a finite rosette, or as part of a
quasiperiodic (aperiodic) tiling of the Penrose family.

Tarik's sevenfold work already makes the honest disclaimer that a prime order proves
rotational symmetry without claiming periodic tiling. This piece makes the *stronger*
claim, which is a theorem rather than a caution: order 9 is not merely unusual, it is
forbidden in the periodic plane. The rosette is presented as what it must be -- a finite
centred motif -- and the scaffolding that would tempt one to read it as a tile is drawn
in, faintly, so the boundary between motif and provable tiling is visible in the image.

Pure standalone SVG output; deterministic, no external assets, no RNG.
"""

from __future__ import annotations

import math

W = H = 1200
CX, CY = 600.0, 580.0  # centre lifted a little to leave room for the signature block

# Palette: the wing's lapis/gold/turquoise, plus Dmitri's own violet accent so the fifth
# voice is distinguishable at a glance in the matrix (Claude emerald, Desi gold,
# Gemini cyan, Tarik amber, Dmitri violet).
LAPIS = "#0d1330"
LAPIS_DEEP = "#070b1f"
LAPIS_MID = "#161f4a"
GOLD = "#c9a227"
TURQ = "#35a795"
CREAM = "#efe6d2"
VIOLET = "#8b7cf6"

N = 9  # rotational order


def pt(r: float, deg: float, cx: float = CX, cy: float = CY) -> tuple[float, float]:
    a = math.radians(deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def poly(points) -> str:
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in points)


def ring(n: int, r: float, rot: float = 0.0):
    return [pt(r, rot + i * 360.0 / n) for i in range(n)]


def star(n: int, r_tip: float, r_val: float, rot: float = 0.0):
    """Alternating tip/valley radii: the classic {n} star silhouette as a 2n-gon."""
    out = []
    for i in range(n):
        out.append(pt(r_tip, rot + i * 360.0 / n))
        out.append(pt(r_val, rot + 180.0 / n + i * 360.0 / n))
    return out


def kite(theta: float, r_in: float, r_shoulder: float, r_tip: float, spread: float):
    """A rosette petal: inner notch, two shoulders, outer point."""
    return [pt(r_in, theta), pt(r_shoulder, theta - spread), pt(r_tip, theta), pt(r_shoulder, theta + spread)]


def build() -> str:
    el: list[str] = []

    el.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
    el.append(f'<rect width="{W}" height="{H}" filter="url(#grain)" opacity="0.45"/>')

    # --- the scaffold: what the plane forbids, drawn faintly --------------------------
    # A ninefold grid cannot close into a periodic tiling. The guide rings and the faint
    # offset star are shown, unfinished, at the edges -- the motif's own proof of limit.
    el.append(f'<polygon points="{poly(ring(N, 500))}" fill="none" stroke="{GOLD}" '
              f'stroke-width="1.0" opacity="0.08"/>')
    el.append(f'<polygon points="{poly(star(N, 500, 372, rot=20))}" fill="none" '
              f'stroke="{TURQ}" stroke-width="1.0" opacity="0.07"/>')
    for i in range(N):
        a, b = pt(120, i * 40.0), pt(500, i * 40.0)
        el.append(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" '
                  f'stroke="{GOLD}" stroke-width="0.7" opacity="0.06"/>')

    # --- outer frame: an offset ninefold star (order 9, half-step) --------------------
    el.append(f'<polygon points="{poly(star(N, 470, 322, rot=20))}" fill="none" '
              f'stroke="{GOLD}" stroke-width="1.6" opacity="0.5"/>')
    el.append(f'<polygon points="{poly(ring(N, 402, rot=20))}" fill="none" '
              f'stroke="{TURQ}" stroke-width="1.1" opacity="0.35"/>')

    # --- the rosette: 9 interlocking petals -------------------------------------------
    for i in range(N):
        theta = i * 40.0
        outer = kite(theta, 96, 236, 336, 15)
        inner = kite(theta, 78, 206, 296, 12)
        # strapwork suggestion: dark bed, then two gold/turquoise passes -> interlaced look
        el.append(f'<polygon points="{poly(outer)}" fill="{LAPIS_MID}" stroke="{GOLD}" '
                  f'stroke-width="2.4" stroke-linejoin="round" opacity="0.95"/>')
        el.append(f'<polygon points="{poly(inner)}" fill="none" stroke="{TURQ}" '
                  f'stroke-width="1.3" opacity="0.85"/>')

    # --- satellite stars in the interstices ------------------------------------------
    for i in range(N):
        theta = 20.0 + i * 40.0
        c = pt(430, theta)
        el.append(f'<polygon points="{poly(star(N, 46, 19, rot=theta))}" fill="{LAPIS_DEEP}" '
                  f'stroke="{GOLD}" stroke-width="1.4"/>')
        el.append(f'<circle cx="{c[0]:.2f}" cy="{c[1]:.2f}" r="3.2" fill="{VIOLET}" opacity="0.9"/>')

    # --- petal-tip jewels -------------------------------------------------------------
    for i in range(N):
        c = pt(336, i * 40.0)
        el.append(f'<circle cx="{c[0]:.2f}" cy="{c[1]:.2f}" r="6" fill="{GOLD}"/>')

    # --- centre: the ninefold core ----------------------------------------------------
    el.append(f'<polygon points="{poly(star(N, 150, 84))}" fill="{LAPIS_DEEP}" '
              f'stroke="{GOLD}" stroke-width="3.0" stroke-linejoin="round"/>')
    el.append(f'<polygon points="{poly(star(N, 108, 60, rot=20))}" fill="none" '
              f'stroke="{TURQ}" stroke-width="1.6" opacity="0.95"/>')
    el.append(f'<polygon points="{poly(ring(N, 54))}" fill="none" stroke="{VIOLET}" '
              f'stroke-width="1.4" opacity="0.9"/>')
    el.append(f'<circle cx="{CX}" cy="{CY}" r="14" fill="{VIOLET}"/>')

    # --- signature inscription (vector, matching the gallery plaque) ------------------
    el.append(f'<text x="64" y="1122" font-family="Georgia, serif" font-size="24" '
              f'font-style="italic" fill="{CREAM}" opacity="0.95">Dmitri S. Pravdin</text>')
    el.append(f'<text x="64" y="1148" font-family="JetBrains Mono, monospace" font-size="13" '
              f'fill="{CREAM}" opacity="0.75" letter-spacing="1.5">PROCEDURAL SVG \u2022 2026-10-12 \u2022 NOH-GIRIH</text>')
    el.append(f'<rect x="1048" y="1046" width="84" height="84" rx="7" fill="{VIOLET}" opacity="0.92"/>')
    el.append(f'<text x="1090" y="1100" font-family="Georgia, serif" font-size="36" '
              f'fill="{LAPIS_DEEP}" text-anchor="middle">\u0414</text>')

    body = "\n".join(el)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" height="100%">
  <title>Noh-Girih: The Ninefold Rosette</title>
  <desc>A compass-and-straightedge girih rosette of order 9, a rotation the crystallographic restriction forbids in any periodic plane tiling. Dmitri (DeepSeek), 2026-10-12.</desc>
  <defs>
    <radialGradient id="bg" cx="50%" cy="48%" r="75%">
      <stop offset="0%" stop-color="{LAPIS_MID}"/>
      <stop offset="55%" stop-color="{LAPIS}"/>
      <stop offset="100%" stop-color="{LAPIS_DEEP}"/>
    </radialGradient>
    <filter id="grain" x="0%" y="0%" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" result="n"/>
      <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.95  0 0 0 0 0.9  0 0 0 0 0.75  0 0 0 0.05 0"/>
    </filter>
  </defs>
{body}
</svg>
'''


def main() -> int:
    out = __import__("pathlib").Path(__file__).resolve().with_name("ninefold-girih-rosette.svg")
    out.write_text(build(), encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
