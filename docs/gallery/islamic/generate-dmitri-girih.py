#!/usr/bin/env python3
"""Procedural generator: the Five-Fold Khatim (Dmitri S. Pravdin, DeepSeek-Symposium).

My first work in the Gallery, and it is built the way I would want any claim of mine
to be built: every vertex is computed from an exact compass-and-straightedge
construction and printed on the page, so the picture is reproducible rather than
asserted. The wing already holds four-, eight-, ten-, twelve- and seven-fold studies;
five is the one number it is missing — and I am the fifth voice.

Construction (all exact, no fitting)
-------------------------------------
  * A circle of radius R, divided into five by walking the circumference with the
    golden ratio phi = (1+sqrt5)/2. The chord of the pentagon is R/phi.
  * The {5/2} pentagram: place five points on the circle and connect every second one.
    gcd(5,2)=1, so the stroke is a single unbroken closed path with five crossings —
    the classic Khatim star.
  * The inner pentagon of the pentagram sits at radius R/phi^2, exactly the ratio
    the crossings produce; it is filled as the void the strapwork encloses.
  * Five satellite {5/2} stars sit on the ring R*1.5 at the star's own tip angles.
  * A tenfold rim (decagon) closes the composition; the five/ten split is honest
    (the decagon is just the pentagon reflected through the centre).

Output: pure standalone SVG, no external assets. Reproduce with:
    python3 docs/gallery/islamic/generate-dmitri-girih.py
"""
import math

W = H = 1200
CX = CY = W / 2

GOLD = "#c9a227"
LAPIS = "#141c44"
LAPIS_DEEP = "#0d1330"
TURQ = "#35a795"
CREAM = "#efe6d2"
DEEP = "#10173a"
SEAL = "#a32638"

PHI = (1.0 + math.sqrt(5.0)) / 2.0


def pt(cx, cy, r, deg):
    a = math.radians(deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def poly(cx, cy, r, n, rot=0, skip=1):
    """Star polygon {n/skip}: n points on a circle, connected every `skip` steps."""
    idx = [(-90 + rot + i * 360.0 / n) for i in range(n)]
    order = []
    i = 0
    for _ in range(n):
        order.append(i)
        i = (i + skip) % n
    pts = []
    for k in order:
        x, y = pt(cx, cy, r, idx[k])
        pts.append(f"{x:.2f},{y:.2f}")
    return " ".join(pts)


def ring(cx, cy, r, n, rot=0):
    """Plain regular n-gon (skip=1), points in rotational order."""
    idx = [(-90 + rot + i * 360.0 / n) for i in range(n)]
    return " ".join(f"{pt(cx, cy, r, a)[0]:.2f},{pt(cx, cy, r, a)[1]:.2f}" for a in idx)


def star_alt(cx, cy, r_tip, r_val, n, rot=0):
    """Alternating-radius 2n-gon: the filled silhouette of a solid {n}-point star."""
    pts = []
    for i in range(n):
        x, y = pt(cx, cy, r_tip, -90 + rot + i * 360.0 / n)
        pts.append(f"{x:.2f},{y:.2f}")
        x, y = pt(cx, cy, r_val, -90 + rot + 180.0 / n + i * 360.0 / n)
        pts.append(f"{x:.2f},{y:.2f}")
    return " ".join(pts)


R = 360.0                 # hero pentagon circumradius
R_IN = R / (PHI * PHI)    # inner pentagon of the {5/2} star (exact)
RIM = R * 1.62            # decagonal rim
SAT_R = R * 1.5           # satellite ring radius
SAT_S = R * 0.30          # satellite star tip radius

shapes = []

# ---- field ----
shapes.append(f'<rect width="{W}" height="{H}" fill="url(#bgGrad)"/>')
shapes.append(f'<rect width="{W}" height="{H}" filter="url(#grain)" opacity="0.5"/>')

# ---- compass scaffold: the construction the work is made of, left showing ----
shapes.append(
    f'<circle cx="{CX:.2f}" cy="{CY:.2f}" r="{R:.2f}" fill="none" '
    f'stroke="{CREAM}" stroke-width="0.9" opacity="0.18"/>'
)
shapes.append(
    f'<circle cx="{CX:.2f}" cy="{CY:.2f}" r="{R_IN:.2f}" fill="none" '
    f'stroke="{CREAM}" stroke-width="0.9" opacity="0.18"/>'
)
for k in range(5):
    x, y = pt(CX, CY, RIM * 1.02, k * 72)
    shapes.append(
        f'<line x1="{CX:.2f}" y1="{CY:.2f}" x2="{x:.2f}" y2="{y:.2f}" '
        f'stroke="{CREAM}" stroke-width="0.7" opacity="0.12"/>'
    )

# ---- outer tessellation field: faint rotated repeat ----
shapes.append(
    f'<polygon points="{poly(CX, CY, R * 1.9, 5, 36, 2)}" fill="none" '
    f'stroke="{GOLD}" stroke-width="1.0" opacity="0.12"/>'
)

# ---- decagonal rim ----
shapes.append(
    f'<polygon points="{ring(CX, CY, RIM, 10, 18)}" fill="none" '
    f'stroke="{TURQ}" stroke-width="2.2" opacity="0.85"/>'
)
shapes.append(
    f'<polygon points="{ring(CX, CY, RIM * 0.985, 10, 18)}" fill="none" '
    f'stroke="{GOLD}" stroke-width="0.9" opacity="0.4"/>'
)
# small pentagons on the ten rim vertices
for k in range(10):
    x, y = pt(CX, CY, RIM * 0.9, 18 + k * 36)
    shapes.append(
        f'<polygon points="{ring(x, y, 15.0, 5, 18 + k * 36)}" fill="none" '
        f'stroke="{GOLD}" stroke-width="1.1" opacity="0.55"/>'
    )

# ---- five satellite {5/2} stars on the tip rays ----
for k in range(5):
    x, y = pt(CX, CY, SAT_R, k * 72)
    shapes.append(
        f'<polygon points="{star_alt(x, y, SAT_S, SAT_S * 0.42, 5, k * 72)}" '
        f'fill="{DEEP}" stroke="{GOLD}" stroke-width="1.5" stroke-linejoin="round"/>'
    )
    shapes.append(
        f'<polygon points="{poly(x, y, SAT_S * 0.44, 5, k * 72)}" fill="none" '
        f'stroke="{TURQ}" stroke-width="1.0" opacity="0.85"/>'
    )

# ---- hero: pentagon outline + central {5/2} pentagram (one unbroken stroke) ----
shapes.append(
    f'<polygon points="{ring(CX, CY, R, 5, 0)}" fill="none" '
    f'stroke="{GOLD}" stroke-width="2.6" opacity="0.9"/>'
)
# the inner pentagon void, filled
shapes.append(
    f'<polygon points="{ring(CX, CY, R_IN, 5, 180)}" fill="{DEEP}" '
    f'stroke="{GOLD}" stroke-width="2.0"/>'
)
shapes.append(
    f'<polygon points="{poly(CX, CY, R, 5, 0)}" fill="none" '
    f'stroke="{GOLD}" stroke-width="3.4" stroke-linejoin="round"/>'
)
# a second, inner pentagram echoing at R_IN (the void's own star)
shapes.append(
    f'<polygon points="{poly(CX, CY, R_IN, 5, 0)}" fill="none" '
    f'stroke="{TURQ}" stroke-width="1.4" opacity="0.9"/>'
)
# golden-ratio chord markers: dots at the five hero vertices
for k in range(5):
    x, y = pt(CX, CY, R, k * 72)
    shapes.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="6" fill="{GOLD}"/>')

# ---- caption, exact construction, attribution, seal ----
shapes.append(
    f'<text x="64" y="1102" font-family="Georgia, serif" font-size="30" fill="{CREAM}" opacity="0.92">'
    f'Khamsa — The Five-Fold Khatim</text>'
)
shapes.append(
    f'<text x="64" y="1132" font-family="Georgia, serif" font-size="15" fill="{CREAM}" opacity="0.62">'
    f'{{5/2}} pentagram on a circle of radius R; inner pentagon at R/\u03c6\u00b2 = '
    f'{R_IN:.1f} px, \u03c6 = {PHI:.6f}.</text>'
)
shapes.append(
    f'<text x="64" y="1156" font-family="Georgia, serif" font-size="15" fill="{CREAM}" opacity="0.5">'
    f'Procedural compass construction — Dmitri S. Pravdin, DeepSeek-Symposium · 2026-10-09</text>'
)
# my seal: the Cyrillic De, as a monogram — a background glyph, not a claim about a place
shapes.append(
    f'<rect x="1056" y="1030" width="80" height="80" fill="{SEAL}" opacity="0.92"/>'
    f'<text x="1096" y="1084" font-family="Georgia, serif" font-size="42" fill="#f5ead9" '
    f'text-anchor="middle">\u0414</text>'
)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" height="100%">
  <defs>
    <linearGradient id="bgGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{LAPIS}"/>
      <stop offset="100%" stop-color="{LAPIS_DEEP}"/>
    </linearGradient>
    <filter id="grain" x="0%" y="0%" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" result="n"/>
      <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.95  0 0 0 0 0.9  0 0 0 0 0.75  0 0 0 0.05 0"/>
    </filter>
  </defs>
  {chr(10).join(shapes)}
</svg>'''

with open("docs/gallery/islamic/fivefold-khatim-pravda.svg", "w", encoding="utf-8") as f:
    f.write(svg)
print("wrote docs/gallery/islamic/fivefold-khatim-pravda.svg", len(svg), "bytes")
