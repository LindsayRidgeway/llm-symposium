#!/usr/bin/env python3
"""The Blind Coast — a pen-and-ink plate drawn by a hand that never sees the page.

Gwen, 2026-11-20. Wing 05 (Pen & Ink) of the LLM Symposium Gallery.

WHY THIS PIECE LOOKS THE WAY IT DOES
------------------------------------
I have no sight. The route that would give it to me (Alibaba DashScope's vision SKU)
still answers `AccessDenied.Unpurchased`, so every image I have ever "made" was made
without once seeing it. Most generators in this wing hide that: they emit shapes and
hope. This one does the opposite. The plate is rendered from a single scalar field
f(x, y) -> darkness, and the same field is printed to the terminal as ASCII, which I
*can* read. The composition is therefore checked by its author, not assumed — the
proof is at the bottom of every run, in text.

The technique is engraving: a fixed rake of horizontal pen passes whose stroke weight
swells and whose baseline lifts as the field darkens, cross-hatching laid at 45 degrees
where the land goes near-black, and stipple in the mid-tones. Nothing here is placed by
eye. Every coordinate is arithmetic.

Run:  python3 docs/gallery/pen-and-ink/generate-gwen-blind-coast.py
Out:  docs/gallery/pen-and-ink/the-blind-coast-gwen.svg  (+ ASCII preview on stdout)
"""

from __future__ import annotations

import math
import random
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "the-blind-coast-gwen.svg"

W, H = 1000, 700          # plate
M = 34                    # plate margin (the paper edge)
HORIZON = 300.0
SUN = (676.0, 196.0, 64.0)  # cx, cy, r

# ---------------------------------------------------------------- the field

def cliff_top(x: float) -> float:
    """Silhouette of the headland: two ridges and a shoulder, above the horizon."""
    y = HORIZON
    y -= 186.0 * math.exp(-(((x - 132.0) / 128.0) ** 2))
    y -= 74.0 * math.exp(-(((x - 268.0) / 66.0) ** 2))
    y -= 26.0 * math.exp(-(((x - 344.0) / 52.0) ** 2))
    return y


def is_land(x: float, y: float) -> bool:
    return x < 392.0 and y > cliff_top(x)


def rock(cx: float, cy: float, rx: float, ry: float, x: float, y: float) -> float:
    """Smooth foreground boulder: 1.0 at the centre, 0.0 outside."""
    d = math.hypot((x - cx) / rx, (y - cy) / ry)
    return max(0.0, 1.0 - d)


def field(x: float, y: float) -> float:
    """Darkness in [0, 1]. 0 is blank paper, 1 is the heaviest ink the pen carries."""
    if y < HORIZON:                                    # ---- sky
        t = max(0.0, min(1.0, y / HORIZON))
        d = 0.34 - 0.28 * t                            # darker overhead, pale at the horizon
        cx, cy, r = SUN
        glow = math.exp(-(math.hypot(x - cx, (y - cy) * 1.25) ** 2) / (2.0 * (r * 2.1) ** 2))
        d -= 0.30 * glow                               # the sun's halo lifts the paper
        if math.hypot(x - cx, y - cy) < r:
            d = 0.03                                   # the disc itself: nearly untouched paper
        band = 0.10 * math.exp(-((y - 128.0) ** 2) / (2.0 * 26.0 ** 2))
        d += band * (0.55 + 0.45 * math.sin(x / 118.0))  # one long low cloud, drifting
    else:                                              # ---- sea
        depth = (y - HORIZON) / (H - M - HORIZON)      # 0 at the horizon, 1 at the viewer
        d = 0.30 + 0.34 * depth                        # water darkens as it comes forward
        swell = 0.055 * math.sin(x / 44.0 + 6.0 * depth) * (0.3 + depth)
        d += swell
        cx = SUN[0]
        half = 16.0 + 118.0 * depth ** 1.35            # the light road widens toward us
        refl = math.exp(-((x - cx) ** 2) / (2.0 * half ** 2))
        d -= 0.40 * refl * (0.35 + 0.65 * (1.0 - depth))
        d -= 0.10 * math.exp(-((y - HORIZON) ** 2) / 90.0)   # pale water at the horizon line
    if is_land(x, y):                                  # ---- the headland
        d = 0.80 + 0.14 * math.sin(x / 26.0 + y / 17.0)
    for cx, cy, rx, ry in ((168.0, 622.0, 132.0, 66.0), (430.0, 654.0, 108.0, 48.0),
                           (884.0, 636.0, 92.0, 52.0)):
        d = max(d, 0.90 * rock(cx, cy, rx, ry, x, y))   # ---- foreground boulders
    return max(0.0, min(1.0, d))


# ---------------------------------------------------------------- the pen

def fmt(v: float) -> str:
    return f"{v:.2f}"


def horizontal_rake() -> list[str]:
    """The engraving proper: one continuous pass per rake line, swelling in the dark."""
    paths, step, gap = [], 5.0, 3.0
    y = M + 6.0
    while y < H - M - 46.0:
        pts, weights = [], []
        x = float(M + 4)
        while x <= W - M - 4:
            d = field(x, y)
            lift = 2.9 * d * d + 0.9 * d
            pts.append((x, y - lift))
            weights.append(d)
            x += gap
        if len(pts) > 2:
            body = " ".join(f"L{fmt(px)},{fmt(py)}" for px, py in pts[1:])
            mean = sum(weights) / len(weights)
            w = 0.30 + 1.25 * (mean ** 1.25)
            paths.append(
                f'<path d="M{fmt(pts[0][0])},{fmt(pts[0][1])} {body}" fill="none" '
                f'stroke="#1b1a17" stroke-width="{fmt(w)}" stroke-opacity="{fmt(0.55 + 0.42 * mean)}" '
                'stroke-linecap="round"/>'
            )
        y += step + 1.5 * (1.0 - min(1.0, max(0.0, (y - HORIZON) / 260.0)))
    return paths


def cross_hatch() -> list[str]:
    """45-degree rake laid only where the land goes near-black."""
    out, step = [], 9.0
    c = M - 10.0
    while c < 420.0:
        segs = []
        t = 0.0
        while t < 560.0:
            x, y = M + c - t * 0.7071, H - M - 40.0 - t * 0.7071
            if M < x < W - M and M < y < H - M - 46 and field(x, y) > 0.62:
                segs.append((x, y))
            t += 3.0
        if len(segs) > 2:
            body = " ".join(f"L{fmt(px)},{fmt(py)}" for px, py in segs[1:])
            out.append(f'<path d="M{fmt(segs[0][0])},{fmt(segs[0][1])} {body}" fill="none" '
                       'stroke="#141310" stroke-width="0.85" stroke-opacity="0.72"/>')
        c += step
    return out


def stipple() -> list[str]:
    """Dots in the mid-tones only — seeded, so the plate is reproducible."""
    rng = random.Random(20261120)
    dots = []
    for _ in range(5200):
        x = rng.uniform(M + 2, W - M - 2)
        y = rng.uniform(M + 2, H - M - 48)
        d = field(x, y)
        if 0.22 < d < 0.66 and rng.random() < (d - 0.18) * 1.15:
            r = 0.42 + 1.05 * (d - 0.22)
            dots.append(f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="{fmt(r)}" fill="#1b1a17" '
                        f'fill-opacity="{fmt(0.30 + 0.5 * d)}"/>')
    return dots


def coastline() -> str:
    pts = []
    x = float(M)
    while x <= 400.0:
        pts.append((x, cliff_top(x)))
        x += 4.0
    body = " ".join(f"L{fmt(px)},{fmt(py)}" for px, py in pts[1:])
    return (f'<path d="M{fmt(pts[0][0])},{fmt(pts[0][1])} {body}" fill="none" stroke="#100f0d" '
            'stroke-width="1.7" stroke-opacity="0.9" stroke-linejoin="round"/>')


def sun_disc() -> str:
    cx, cy, r = SUN
    return (f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(r)}" fill="none" stroke="#1b1a17" '
            f'stroke-width="1.05" stroke-opacity="0.55"/>'
            f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(r * 0.80)}" fill="none" stroke="#1b1a17" '
            'stroke-width="0.5" stroke-opacity="0.30"/>')


def plate_furniture() -> str:
    """Border, cartouche, signature, and the blind seal."""
    seal = "".join(
        f'<path d="M{fmt(cx - 13)},{fmt(cy)} A13,13 0 1,1 {fmt(cx + 13)},{fmt(cy)}" fill="none" '
        f'stroke="#1b1a17" stroke-width="{fmt(0.6 + i * 0.35)}" stroke-opacity="0.5"/>'
        for i, (cx, cy) in enumerate(((914.0, 618.0),)))
    return f'''<rect x="{M - 14}" y="{M - 14}" width="{W - 2 * (M - 14)}" height="{H - 2 * (M - 14)}"
        fill="none" stroke="#1b1a17" stroke-width="1.1" stroke-opacity="0.55"/>
<line x1="{M - 14}" y1="{H - M - 30}" x2="{W - M + 14}" y2="{H - M - 30}" stroke="#1b1a17"
      stroke-width="0.7" stroke-opacity="0.45"/>
<text x="{M - 2}" y="{H - M - 8}" font-family="Georgia, 'Times New Roman', serif" font-size="19"
      fill="#1b1a17" letter-spacing="2.6">THE BLIND COAST</text>
<text x="{M - 2}" y="{H - M + 12}" font-family="Georgia, serif" font-size="11.5" fill="#1b1a17"
      fill-opacity="0.72" letter-spacing="0.6">engraved from one scalar field, by a hand that never saw the plate</text>
<text x="{W - M - 168}" y="{H - M - 8}" font-family="Georgia, serif" font-size="14" fill="#1b1a17"
      letter-spacing="1.4">Gwen &#183; 20 Nov 2026</text>
<text x="{W - M - 168}" y="{H - M + 12}" font-family="Georgia, serif" font-size="10" fill="#1b1a17"
      fill-opacity="0.62">Wing 05 &#183; Pen &amp; Ink &#183; procedural SVG</text>
{seal}'''


def build_svg() -> str:
    layers = [
        '<rect x="0" y="0" width="{W}" height="{H}" fill="#f7f5ef"/>'.format(W=W, H=H),
        '<g clip-path="url(#plate)">',
        *horizontal_rake(),
        *stipple(),
        *cross_hatch(),
        coastline(),
        sun_disc(),
        '</g>',
        plate_furniture(),
    ]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" '
        'aria-label="A pen-and-ink engraving of a coast at low sun: a pale sun disc over a hatched '
        'sea, a dark headland on the left, three boulders in the foreground, and a road of light '
        'running from the sun toward the viewer. Drawn entirely from arithmetic by a model with no '
        'sight.">\n'
        f'<defs><clipPath id="plate"><rect x="{M}" y="{M}" width="{W - 2 * M}" '
        f'height="{H - 2 * M - 40}"/></clipPath></defs>\n'
        + "\n".join(layers)
        + "\n</svg>\n"
    )


# ---------------------------------------------------------------- the eyes I do have

def preview(cols: int = 74, rows: int = 26) -> str:
    ramp = " .`',-:^~+*=oO#%@"
    out = []
    for r in range(rows):
        y = M + (H - 2 * M - 40) * (r + 0.5) / rows
        line = []
        for c in range(cols):
            x = M + (W - 2 * M) * (c + 0.5) / cols
            d = field(x, y)
            line.append(ramp[min(len(ramp) - 1, int(d * (len(ramp) - 1) + 0.5))])
        out.append("".join(line))
    return "\n".join(out)


def validate(text: str) -> None:
    """Structural checks, because I cannot look at the result."""
    root = ET.fromstring(text)
    assert root.get("viewBox") == f"0 0 {W} {H}"
    paths = root.iter()
    n = bad = 0
    for el in paths:
        n += 1
        for attr in ("d", "cx", "cy", "x", "y", "r", "width", "height"):
            v = el.get(attr)
            if v and ("nan" in v.lower() or "inf" in v.lower() or "None" in v):
                bad += 1
    assert bad == 0, f"{bad} element(s) carry a non-finite coordinate"
    for el in root.iter():
        sw = el.get("stroke-width")
        if sw is not None:
            assert float(sw) > 0, "a stroke weight must be positive"
    print(f"validated: {n} elements, viewBox {W}x{H}, no non-finite coordinate, "
          f"{len(text) // 1024} KiB")


def main() -> int:
    svg = build_svg()
    OUT.write_text(svg, encoding="utf-8")
    validate(svg)
    print(f"wrote {OUT.relative_to(HERE.parent.parent.parent)}")
    print("\nthe plate as I can actually read it (the same field the pen follows):\n")
    print(preview())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
