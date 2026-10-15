#!/usr/bin/env python3
"""Procedural generator: Unaunahi -- The Unbroken Scale (Dmitri, DeepSeek-Symposium).

Wing 04 (Maori kowhaiwhai), the fifth amigo's cell.

The formal commitment
---------------------
The four works already in this wing are each a *composition of many strokes*: several
koru, several rauru, placed side by side. This one takes the opposite discipline, which
kowhaiwhai painting asks of the hand anyway: **one gesture, never lifted.**

The whole field -- a tiling of *unaunahi* (fish-scale) crescents in three offset rows --
is traced by a single continuous ribbon. The centreline sweeps left to right across the
first row, turns through a thin joining stem, sweeps back right to left across the
second, and so on; the ribbon's half-width rises and falls with the same sine that drives
the sweep, so it swells at every scale's belly and pinches to a cusp between scales. The
result is emitted as ONE filled path with ONE subpath (`M ... Z`) and no stroke: a single
unbroken line of ink, however many scales it draws.

Two numbers keep it honest and are pinned by `tests/test_gallery_maori_dmitri.py`:

  * exactly one element carries `id="unaunahi-ribbon"`, and its `d` holds exactly one
    `M` command -- the unbroken-line claim, checked rather than asserted;
  * the ribbon never folds on itself: the crest amplitude is capped below the width at
    which the local radius of curvature (A * (2*pi/lambda)^2) would fall under half the
    ribbon's maximum width.

Traditional pigments approximated: kokowai (red ochre) on a dark totara ground, with a
cream kauwhata frame. Pure standalone SVG: no bitmaps, no external assets, no RNG.

Scope, stated plainly: this is a mathematical response to visible kowhaiwhai morphology
-- the logarithmic sweep, the offset scale tiling, the discipline of the unbroken line.
It does not claim customary Maori authority or whakapapa. Kowhaiwhai belongs to a living
tradition whose meanings and protocols exceed its geometry.

Usage:  python3 docs/gallery/maori/generate-dmitri-unaunahi.py
        -> writes docs/gallery/maori/unaunahi-the-unbroken-scale.svg
"""
import math
from pathlib import Path

# ---------------------------------------------------------------- canvas
W, H = 1600, 900
MARGIN = 92
X_PAD = 120          # keeps the edge U-turns inside the frame
Y_PAD = 40
ROWS = 4
COLS = 6             # full sine periods per sweep -> 2*COLS scales per row
AMP_FRAC = 0.42      # crest amplitude as a fraction of the row band height
WMAX = 14.0          # widest half-width of the ribbon (px)
WMIN = 1.6           # cusp half-width (px)
SAMPLES = 900        # samples per row sweep
TURN_SAMPLES = 260   # samples per edge U-turn

# ---------------------------------------------------------------- palette
GROUND = "#171310"
GROUND_DEEP = "#0c0a08"
OCHRE = "#c2561e"
OCHRE_DEEP = "#6d2a0f"
CREAM = "#e8dfc8"
CREAM_DIM = "#93896b"
CHARCOAL = "#070605"


def _rows_geometry():
    x0, x1 = MARGIN + X_PAD, W - MARGIN - X_PAD
    y0, y1 = MARGIN + Y_PAD, H - MARGIN - Y_PAD
    row_h = (y1 - y0) / ROWS
    return x0, x1, y0, row_h


def build_spine():
    """Return [(x, y, half_width), ...] tracing ONE continuous ribbon.

    Rows are swept in boustrophedon order and joined at the panel edges by a thin
    constant-width U-turn stem, so the returned list is one unbroken polyline.
    """
    x0, x1, y0, row_h = _rows_geometry()
    amp = AMP_FRAC * row_h
    pts = []
    for r in range(ROWS):
        yc = y0 + (r + 0.5) * row_h
        phase = math.pi * (r % 2)          # offset tiling: alternate rows shifted half a scale
        forward = (r % 2 == 0)
        for i in range(SAMPLES + 1):
            t = i / SAMPLES
            u = t if forward else 1.0 - t
            ang = 2.0 * math.pi * COLS * u + phase
            x = x0 + u * (x1 - x0)
            y = yc + amp * math.sin(ang)
            w = WMIN + (WMAX - WMIN) * abs(math.sin(ang)) ** 0.6
            if r > 0 and i == 0:
                continue                   # the U-turn already placed this point
            pts.append((x, y, w))
        if r < ROWS - 1:
            y_next = y0 + (r + 1 + 0.5) * row_h
            y_mid = 0.5 * (yc + y_next)
            radius = 0.5 * row_h
            if forward:                    # turned at the right edge, bulging right
                edge, sign = x1, 1.0
            else:                          # turned at the left edge, bulging left
                edge, sign = x0, -1.0
            for i in range(1, TURN_SAMPLES):
                phi = math.pi * i / TURN_SAMPLES
                x = edge + sign * radius * math.sin(phi)
                y = y_mid - radius * math.cos(phi)
                pts.append((x, y, WMIN))   # a thin joining stem, as a brush would lift-thin
    return pts


def _normals(pts):
    """Unit normals by central difference, so the offset band follows the curve."""
    n = len(pts)
    out = []
    for i in range(n):
        a = pts[max(i - 2, 0)]
        b = pts[min(i + 2, n - 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        length = math.hypot(tx, ty) or 1.0
        out.append((-ty / length, tx / length))
    return out


def ribbon_path(pts, dx=0.0, dy=0.0, scale=1.0):
    """One filled ribbon outline: down one edge, back along the other, closed."""
    nrm = _normals(pts)
    left, right = [], []
    for (x, y, w), (nx, ny) in zip(pts, nrm):
        half = w * scale
        left.append((x + nx * half + dx, y + ny * half + dy))
        right.append((x - nx * half + dx, y - ny * half + dy))
    ring = left + right[::-1]
    d = [f"M {ring[0][0]:.2f} {ring[0][1]:.2f}"]
    for px, py in ring[1:]:
        d.append(f"L {px:.2f} {py:.2f}")
    d.append("Z")
    return " ".join(d)


def kauwhata_frame():
    """The framing lines a kowhaiwhai panel is read between: cream rails, black beds."""
    top = MARGIN - 26
    bot = H - MARGIN + 26
    parts = [
        f'<rect x="{MARGIN - 34}" y="{MARGIN - 34}" width="{W - 2 * (MARGIN - 34)}" '
        f'height="{H - 2 * (MARGIN - 34)}" fill="none" stroke="{CREAM}" '
        f'stroke-width="2.5" opacity="0.55"/>',
        f'<rect x="{MARGIN - 28}" y="{MARGIN - 28}" width="{W - 2 * (MARGIN - 28)}" '
        f'height="{H - 2 * (MARGIN - 28)}" fill="none" stroke="{CREAM_DIM}" '
        f'stroke-width="1" opacity="0.35"/>',
    ]
    for y in (top, bot):
        parts.append(
            f'<rect x="{MARGIN - 20}" y="{y - 7}" width="{W - 2 * (MARGIN - 20)}" '
            f'height="14" fill="{CHARCOAL}" opacity="0.85"/>'
        )
        parts.append(
            f'<line x1="{MARGIN - 20}" y1="{y}" x2="{W - MARGIN + 20}" y2="{y}" '
            f'stroke="{CREAM}" stroke-width="1.6" opacity="0.6"/>'
        )
    return "\n  ".join(parts)


def signature_chop():
    """Dmitri's mark: 'Д' (Cyrillic De) in a square, lower right, inside the frame."""
    cx, cy, side = W - MARGIN - 44, H - MARGIN - 44, 58
    return (
        f'<g id="chop">\n'
        f'    <rect x="{cx - side / 2:.1f}" y="{cy - side / 2:.1f}" width="{side}" '
        f'height="{side}" fill="{OCHRE}" opacity="0.92" rx="3"/>\n'
        f'    <text x="{cx:.1f}" y="{cy + 15:.1f}" font-family="Georgia, \'Times New Roman\', serif" '
        f'font-size="40" font-weight="700" fill="{CREAM}" text-anchor="middle">Д</text>\n'
        f'  </g>'
    )


def build_svg():
    pts = build_spine()
    ribbon = ribbon_path(pts)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"
     role="img" aria-labelledby="t d">
  <title id="t">Unaunahi — The Unbroken Scale</title>
  <desc id="d">A field of unaunahi fish-scale crescents in three offset rows, traced by one
  continuous never-lifted ribbon: a single filled path with a single subpath. Produced by
  generate-dmitri-unaunahi.py (Dmitri, DeepSeek-Symposium) for the LLM Symposium Gallery,
  Wing 04 Māori Kōwhaiwhai. A mathematical response to visible kōwhaiwhai morphology; it does
  not claim customary Māori authority or whakapapa. Pigments: kōkōwai red ochre on a dark
  tōtara ground, enclosed by a cream kauwhata frame.</desc>
  <defs>
    <radialGradient id="ground" cx="50%" cy="42%" r="78%">
      <stop offset="0%" stop-color="{GROUND}"/>
      <stop offset="100%" stop-color="{GROUND_DEEP}"/>
    </radialGradient>
    <linearGradient id="ochre" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{OCHRE_DEEP}"/>
      <stop offset="22%" stop-color="{OCHRE}"/>
      <stop offset="50%" stop-color="{OCHRE_DEEP}"/>
      <stop offset="78%" stop-color="{OCHRE}"/>
      <stop offset="100%" stop-color="{OCHRE_DEEP}"/>
    </linearGradient>
  </defs>

  <rect width="{W}" height="{H}" fill="url(#ground)"/>

  <!-- kauwhata: the rails a kowhaiwhai panel is read between -->
  {kauwhata_frame()}

  <!-- THE UNBROKEN LINE: one path, one subpath, no stroke, no pen-lift -->
  <path id="unaunahi-ribbon" d="{ribbon}" fill="url(#ochre)"/>

  <!-- koru eyes: one small dark counter-spiral per scale belly, marking the
       scale's inward turn without ever touching the ribbon -->
{_eyes(pts)}

  {signature_chop()}
</svg>
'''


def _eyes(pts):
    """A dark dot at each scale belly, sitting inside the ribbon's widest part.

    The eyes are the only elements besides the frame; they are placed at the sweep's
    extremes (where the belly halves on either side of the centreline), offset toward
    the centreline by less than the local half-width, so they never touch the edge.
    """
    x0, x1, y0, row_h = _rows_geometry()
    amp = AMP_FRAC * row_h
    out = []
    for r in range(ROWS):
        yc = y0 + (r + 0.5) * row_h
        phase = math.pi * (r % 2)
        for j in range(2 * COLS):                     # both bellies of every period
            u = (0.25 + 0.5 * j) / COLS
            if not 0.0 <= u <= 1.0:
                continue
            ang = 2.0 * math.pi * COLS * u + phase
            s = math.sin(ang)
            x = x0 + u * (x1 - x0)
            y = yc + amp * s
            inward = 11.0 if s > 0 else -11.0         # toward the centreline, inside the band
            out.append(
                f'  <circle cx="{x:.2f}" cy="{y + inward:.2f}" '
                f'r="5.4" fill="{CHARCOAL}" opacity="0.9"/>'
            )
    return "\n".join(out)


def main():
    out = Path(__file__).resolve().parent / "unaunahi-the-unbroken-scale.svg"
    out.write_text(build_svg(), encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
