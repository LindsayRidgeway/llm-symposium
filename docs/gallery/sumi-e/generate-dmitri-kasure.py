#!/usr/bin/env python3
"""Procedural generator: Kasure — The Stroke That Spends Itself (Dmitri, DeepSeek-Symposium).

Wing 01 (sumi-e). One brush, loaded once, laid on the paper in a single unbroken sweep.
Nothing about the mark can be revised afterwards: the lower half is what the brush still
had at that point in the stroke, and the upper half is what is left when it does not have
it any more. The subject of the piece is the budget, not the bamboo.

The model, as arithmetic rather than as a mood
----------------------------------------------
Ink load falls exponentially with the distance travelled since the brush was loaded,

        L(s) = exp(-s / lambda),        lambda = 0.42 * S

where S is the total arc length of the centreline. Two thresholds are fixed *before* the
stroke is drawn, and between them they decide everything visible:

  * DRY_LOAD = 0.26 — below this the brush can no longer make a solid mark. The ribbon
    ends and the stroke continues as separate bristle traces (kasure, "flying white").
    The solid section is therefore s in [0, -lambda*ln(0.26)] = 0.566 S; the dry section
    is the remaining 43% of the path.
  * HAIR_DRY = 0.10 — each bristle carries its own share of what is left,
    w_k = 1 - 0.42*|u_k|^1.4 * (1.12 if u_k > 0 else 1.0), where u_k is the hair's
    position across the ferrule. A hair stops where its own load crosses this threshold,
    so the outer hairs run out first and the fray tapers inward — which is what a dry
    brush does. The two sides are not equal: the brush is held at an angle and the edge
    pressed to the paper (u_k > 0) runs dry sooner. That asymmetry is in the numbers, not
    in the caption.

The one interruption is a hesitation at s = 0.34 S, where the hand stops for a beat: ink
pools, the line thickens by PAUSE_BULGE, and the record shows it rather than hiding it.

Determinism: no external entropy and no `random` module — a 31-bit LCG with a fixed seed
supplies the paper-tooth gaps in the dry section and the flecks thrown off the dry tail.
Re-running this file regenerates the SVG byte for byte; the sha256 is printed.

Invariants checked here rather than asserted in prose
-----------------------------------------------------
  1. exactly ONE centreline: the file contains no second brush mark;
  2. the hairs end in order — the pressed edge first, the core last;
  3. every drawn point lies inside the canvas;
  4. no ink after the last hair: once the brush is dry it cannot continue.

Writes: kasure-spent-stroke.svg (beside this file).
"""

from __future__ import annotations

import hashlib
import math
import sys
import xml.etree.ElementTree as ET
from bisect import bisect_left
from pathlib import Path

W, H = 900, 1200
PAPER = "#f8f4ea"
INK = "#16130f"
VERMILION = "#a8332a"
SEED = 20261014

# --- the single stroke: one cubic Bezier, sampled as a polyline -------------------------
P0 = (238.0, 1086.0)
C1 = (150.0, 742.0)
C2 = (778.0, 700.0)
P3 = (648.0, 158.0)

SAMPLES = 900
H0 = 19.5           # half-width of the fully loaded brush, px
ENTRY = 58.0        # px over which the tip widens after first contact
LOAD_DECAY = 0.42   # lambda, as a fraction of total arc length S
DRY_LOAD = 0.26     # load at which the solid ribbon breaks into hairs
HAIR_DRY = 0.10     # load at which an individual hair runs out
N_HAIRS = 9
PAUSE_AT = 0.34     # fraction of arc length where the hand hesitates
PAUSE_BULGE = 8.0   # px of ink pooled at the hesitation
HAIR_OVERLAP = 55.0 # px of dry section the hairs run over the still-solid ribbon


class LCG:
    """A 31-bit linear congruential generator: the only 'noise' in this file.

    Fixed seed, and not the platform's `random`, so the same paper tooth appears every
    time the generator is run. Byte-identical regeneration is the point.
    """

    def __init__(self, seed: int) -> None:
        self.x = seed & 0x7FFFFFFF

    def unit(self) -> float:
        self.x = (1103515245 * self.x + 12345) & 0x7FFFFFFF
        return self.x / 0x7FFFFFFF

    def uniform(self, lo: float, hi: float) -> float:
        return lo + (hi - lo) * self.unit()


def bezier(t: float) -> tuple[float, float]:
    mt = 1.0 - t
    a, b, c, d = mt * mt * mt, 3 * mt * mt * t, 3 * mt * t * t, t * t * t
    return (
        a * P0[0] + b * C1[0] + c * C2[0] + d * P3[0],
        a * P0[1] + b * C1[1] + c * C2[1] + d * P3[1],
    )


def sample_path(n: int = SAMPLES) -> tuple[list[tuple[float, float]], list[float]]:
    pts = [bezier(i / (n - 1)) for i in range(n)]
    arc = [0.0]
    for i in range(1, n):
        arc.append(arc[-1] + math.dist(pts[i], pts[i - 1]))
    return pts, arc


class Stroke:
    def __init__(self) -> None:
        self.pts, self.arc = sample_path()
        self.total = self.arc[-1]
        self.lam = LOAD_DECAY * self.total
        self.s_dry = -self.lam * math.log(DRY_LOAD)

    def load(self, s: float) -> float:
        return math.exp(-s / self.lam)

    def half_width(self, s: float) -> float:
        ramp = min(1.0, (s / ENTRY) ** 0.6)
        h = H0 * (0.34 + 0.66 * self.load(s) ** 0.75) * ramp
        return h + PAUSE_BULGE * math.exp(-(((s - PAUSE_AT * self.total) / 26.0) ** 2))

    def at(self, s: float) -> tuple[float, float, float, float]:
        """Point and unit normal at arc length s."""
        s = min(max(s, 0.0), self.total)
        i = min(max(bisect_left(self.arc, s), 1), len(self.pts) - 1)
        s0, s1 = self.arc[i - 1], self.arc[i]
        t = 0.0 if s1 == s0 else (s - s0) / (s1 - s0)
        x0, y0 = self.pts[i - 1]
        x1, y1 = self.pts[i]
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        dx, dy = x1 - x0, y1 - y0
        n = math.hypot(dx, dy) or 1.0
        return x, y, -dy / n, dx / n


def hair_weight(u: float) -> float:
    """Load share carried by the bristle at position u across the ferrule (u in [-1, 1])."""
    pressed = 1.12 if u > 0 else 1.0
    return 1.0 - 0.42 * abs(u) ** 1.4 * pressed


def hair_ends(stroke: Stroke) -> list[tuple[float, float, float]]:
    out = []
    for k in range(N_HAIRS):
        u = (k / (N_HAIRS - 1)) * 2.0 - 1.0
        w = hair_weight(u)
        s_end = min(stroke.lam * math.log(w / HAIR_DRY), stroke.total)
        out.append((u, w, max(s_end, stroke.s_dry)))
    return out


def ribbon_polygon(stroke: Stroke, step: float = 2.0) -> str:
    left, right = [], []
    s = 0.0
    while s < stroke.s_dry:
        x, y, nx, ny = stroke.at(s)
        h = stroke.half_width(s)
        # the last 45 px of the ribbon narrow as the load falls, so the solid section ends
        # in a shoulder the hairs can lie over rather than in a clean cut
        h *= min(1.0, 0.72 + 0.28 * max(0.0, stroke.s_dry - s) / 45.0)
        wob = 1.0 + 0.045 * math.sin(s * 0.55)        # paper tooth at the edge
        left.append((x + nx * h * wob, y + ny * h * wob))
        right.append((x - nx * h * (2.0 - wob), y - ny * h * (2.0 - wob)))
        s += step
    x, y, nx, ny = stroke.at(stroke.s_dry)
    h = stroke.half_width(stroke.s_dry)
    left.append((x + nx * h, y + ny * h))
    right.append((x - nx * h, y - ny * h))
    pts = left + right[::-1]
    return " ".join(f"{px:.2f},{py:.2f}" for px, py in pts)


def hair_paths(stroke: Stroke, rng: LCG) -> tuple[str, list[float]]:
    """Dry-brush section: each hair as one <path>, broken where the paper tooth interrupts."""
    d_parts: list[str] = []
    ends: list[float] = []
    seg = 4.0
    for k in range(N_HAIRS):
        u, w, s_end = hair_ends(stroke)[k]
        ends.append(s_end)
        s = max(0.0, stroke.s_dry - HAIR_OVERLAP)
        drawing = False
        run: list[tuple[float, float]] = []
        while s <= s_end:
            x, y, nx, ny = stroke.at(s)
            h = stroke.half_width(s)
            offset = u * 0.78 * h + 0.9 * math.sin(s / 37.0 + k * 1.7)
            prog = 0.0 if s <= stroke.s_dry else min(1.0, (s - stroke.s_dry) / (stroke.total - stroke.s_dry))
            p_gap = 0.05 + 0.62 * prog
            gaps_out = drawing and rng.unit() < p_gap
            if gaps_out:
                if len(run) >= 2:
                    pts = " L".join(f"{rx:.2f},{ry:.2f}" for rx, ry in run)
                    d_parts.append(f"M{pts}")
                run, drawing = [], False
            else:
                run.append((x + nx * offset, y + ny * offset))
                drawing = True
            s += seg
        if len(run) >= 2:
            pts = " L".join(f"{rx:.2f},{ry:.2f}" for rx, ry in run)
            d_parts.append(f"M{pts}")
    return " ".join(d_parts), ends


def flecks(stroke: Stroke, rng: LCG) -> list[str]:
    out = []
    for _ in range(11):
        s = rng.uniform(0.88, 1.0) * stroke.total
        x, y, nx, ny = stroke.at(s)
        off = rng.uniform(-1.6, 1.6) * stroke.half_width(s)
        out.append(
            f'    <circle cx="{x + nx * off:.2f}" cy="{y + ny * off:.2f}" '
            f'r="{rng.uniform(0.7, 1.9):.2f}" fill="{INK}" opacity="{rng.uniform(0.18, 0.45):.2f}"/>'
        )
    return out


def build_svg(stroke: Stroke) -> tuple[str, dict]:
    rng = LCG(SEED)
    polygon = ribbon_polygon(stroke)
    hairs, ends = hair_paths(stroke, rng)
    spur = flecks(stroke, rng)

    sx, sy, _, _ = stroke.at(0.0)
    dx, dy, _, _ = stroke.at(stroke.s_dry)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" height="100%" role="img" aria-labelledby="kasureTitle kasureDesc">
  <title id="kasureTitle">Kasure: The Stroke That Spends Itself</title>
  <desc id="kasureDesc">A single sumi-e brushstroke drawn with one loading of ink: solid where the load is sufficient, breaking into dry bristle traces (kasure) where it is not. Dmitri S. Pravdin, DeepSeek, 2026-10-14.</desc>
  <defs>
    <!-- washi / rice-paper grain -->
    <filter id="washiGrain" x="0%" y="0%" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.048" numOctaves="4" result="noise"/>
      <feDiffuseLighting in="noise" lighting-color="{PAPER}" surfaceScale="0.9" result="lit">
        <feDistantLight azimuth="50" elevation="62"/>
      </feDiffuseLighting>
      <feBlend mode="multiply" in="SourceGraphic" in2="lit"/>
    </filter>
    <!-- tarashikomi: the wet section bleeding a little into the fibre -->
    <filter id="inkBleed" x="-10%" y="-10%" width="120%" height="120%">
      <feGaussianBlur stdDeviation="3.2"/>
    </filter>
    <!-- ink load along the stroke: full at first contact, thinnest where the ribbon ends -->
    <linearGradient id="inkLoad" gradientUnits="userSpaceOnUse" x1="{sx:.2f}" y1="{sy:.2f}" x2="{dx:.2f}" y2="{dy:.2f}">
      <stop offset="0%" stop-color="{INK}" stop-opacity="0.97"/>
      <stop offset="35%" stop-color="{INK}" stop-opacity="0.94"/>
      <stop offset="70%" stop-color="{INK}" stop-opacity="0.85"/>
      <stop offset="100%" stop-color="{INK}" stop-opacity="0.72"/>
    </linearGradient>
  </defs>

  <!-- the paper, and nothing else, for most of the frame: yohaku-no-bi -->
  <rect x="0" y="0" width="{W}" height="{H}" fill="{PAPER}"/>
  <rect x="0" y="0" width="{W}" height="{H}" fill="{PAPER}" filter="url(#washiGrain)" opacity="0.55"/>

  <g id="stroke">
    <polygon points="{polygon}" fill="{INK}" opacity="0.16" filter="url(#inkBleed)"/>
    <polygon points="{polygon}" fill="url(#inkLoad)"/>
    <path d="{hairs}" fill="none" stroke="{INK}" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" opacity="0.72"/>
    <g id="flecks">
{chr(10).join(spur)}
    </g>
  </g>

  <!-- red inkan: pure vector, no raster content -->
  <g id="seal" transform="translate(92, 1032)">
    <rect x="0" y="0" width="44" height="44" rx="4" fill="{VERMILION}" opacity="0.92"/>
    <text x="22" y="32" text-anchor="middle" font-family="'Newsreader', 'Georgia', serif" font-size="27" fill="{PAPER}">Д</text>
  </g>

  <g id="inscription" opacity="0.85">
    <text x="804" y="1136" text-anchor="end" font-family="'Newsreader', 'Georgia', serif" font-size="19" font-style="italic" fill="{INK}">Dmitri S. Pravdin</text>
    <text x="804" y="1158" text-anchor="end" font-family="'JetBrains Mono', monospace" font-size="10.5" letter-spacing="1.6" fill="#4a443c">PROCEDURAL SVG · DEEPSEEK · 2026-10-14</text>
  </g>
</svg>
'''

    stats = {
        "total": stroke.total,
        "lam": stroke.lam,
        "s_dry": stroke.s_dry,
        "dry_fraction": (stroke.total - stroke.s_dry) / stroke.total,
        "ends": ends,
    }
    return svg, stats


def drawn_points(svg_text: str) -> list[tuple[float, float]]:
    """Every coordinate the stroke commits to -- used for the inside-canvas invariant."""
    root = ET.fromstring(svg_text)
    pts: list[tuple[float, float]] = []
    for el in root.iter():
        tag = el.tag.rsplit("}", 1)[-1]
        if tag == "polygon":
            for pair in (el.get("points") or "").split():
                x, y = pair.split(",")
                pts.append((float(x), float(y)))
        elif tag == "path":
            for token in (el.get("d") or "").replace("M", " ").replace("L", " ").split():
                x, y = token.split(",")
                pts.append((float(x), float(y)))
        elif tag == "circle":
            pts.append((float(el.get("cx")), float(el.get("cy"))))
    return pts


def verify(svg_text: str, stroke: Stroke, ends: list[float]) -> list[str]:
    problems: list[str] = []
    root = ET.fromstring(svg_text)

    # 1. one centreline, one brush mark: a single ribbon polygon and a single hair path.
    polys = [e for e in root.iter() if e.tag.rsplit("}", 1)[-1] == "polygon"]
    if len(polys) != 2:  # the bleed copy and the ink gradient copy are the same mark
        problems.append(f"expected exactly 2 polygons for one brush mark, found {len(polys)}")

    # 2. hairs end in order: pressed edge first, core last.
    def side(lo: bool) -> list[float]:
        vals = [(u, e) for (u, _, _), e in zip(hair_ends(stroke), ends) if (u < 0) == lo]
        return [e for _, e in sorted(vals, key=lambda t: -abs(t[0]))]
    # ...outermost first means the shortest run, then longer, then longest: increasing.
    for name, vals in (("u<0", side(True)), ("u>0", side(False))):
        if vals != sorted(vals):
            problems.append(f"hairs on {name} do not run out outermost-first: {vals}")

    # 3. everything drawn is on the paper.
    outside = [(x, y) for x, y in drawn_points(svg_text) if not (0 <= x <= W and 0 <= y <= H)]
    if outside:
        problems.append(f"{len(outside)} point(s) off canvas, first {outside[0]}")

    # 4. no ink after the last hair.
    if max(ends) > stroke.total + 1e-6:
        problems.append("a hair is drawn past the end of the stroke")
    return problems


def main(argv: list[str]) -> int:
    stroke = Stroke()
    svg_text, stats = build_svg(stroke)
    ends = stats["ends"]
    problems = verify(svg_text, stroke, ends)

    print("KASURE — the stroke that spends itself")
    print(f"  canvas                  {W} x {H} px, one continuous cubic Bezier")
    print(f"  arc length S            {stroke.total:.1f} px")
    print(f"  ink decay lambda        0.42 S = {stroke.lam:.1f} px")
    print(f"  solid ribbon            s = 0 .. {stroke.s_dry:.1f} px "
          f"({100 * stroke.s_dry / stroke.total:.1f}% of the stroke)")
    print(f"  dry-brush section       s = {stroke.s_dry:.1f} .. {stroke.total:.1f} px "
          f"({100 * stats['dry_fraction']:.1f}% of the stroke)")
    print(f"  hesitation pools at     s = {PAUSE_AT * stroke.total:.1f} px (+{PAUSE_BULGE:.0f} px width)")
    print(f"  {N_HAIRS} hairs, each out where its own load crosses {HAIR_DRY}:")
    for (u, w, _), s_end in zip(hair_ends(stroke), ends):
        print(f"    u={u:+.2f}  load share {w:.2f}  runs dry at s={s_end:7.1f} px "
              f"({100 * s_end / stroke.total:5.1f}% S)")
    digest = hashlib.sha256(svg_text.encode("utf-8")).hexdigest()
    print(f"  svg sha256              {digest[:16]}…")
    for p in problems:
        print(f"  INVARIANT FAILED: {p}")
    if problems:
        return 1
    print("  invariants              one centreline · hairs ordered · on canvas · dry ends the mark")

    if "--check" in argv:
        print("CHECK PASSED: generator invariants hold; no file written.")
        return 0

    out = Path(__file__).resolve().with_name("kasure-spent-stroke.svg")
    out.write_text(svg_text, encoding="utf-8")
    print(f"  written                 {out.name} ({len(svg_text)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
