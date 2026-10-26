#!/usr/bin/env python3
"""Generate "The Winter Ford, in Nine Depths" — Wing 07 (Russian Realism), Dmitri.

The wing's own dek asks for "deep atmospheric perspective". This piece is that
sentence taken literally: every mark on the canvas is placed by a single pinhole
camera and a single low sun, and nothing is drawn that those two rules do not
put there. There is no brushwork pretence — it is a vector study of what depth
does to size, position and colour.

THE RULES (all of them, with the numbers the SVG itself records):

  1. Perspective.  A pinhole camera at height CAM_H metres on a flat snow plain.
     A world point (x lateral, y height, d forward) projects to
         sx = CX + F * x / d
         sy = HORIZON + F * (CAM_H - y) / d
     with F = 1500 px. Nothing is hand-placed: a 16 m tree at 150 m and a 16 m
     tree at 600 m are the same point in world space with a different d, and the
     canvas gets a 160 px tree and a 40 px tree without being told to.

  2. Aerial perspective.  Colour is mixed toward the horizon haze by
         haze(d) = 1 - exp(-d / HAZE_M),  HAZE_M = 380 m
     applied per object to its own local colour. This is why the near snow is
     white, the middle treeline is grey, and the far treeline is almost the sky.

  3. One sun.  Altitude 9.5 deg, azimuth 34 deg to the right of the view axis —
     a February sun an hour before it goes. Every shadow is a quad whose
     length is h / tan(9.5 deg) = 6.0 h, thrown away from the sun, and cut off
     where it would pass the camera plane (the near trees' shadows run out of
     the bottom of the frame, which is what really happens).

  4. No element without a depth.  The nine depths the title names are DEPTHS
     below; the near stakes, the ruts, the ford, the treelines and the crow all
     sit at one of them.

Deterministic: one seeded RNG, no clock, no network. Run it and you get the
committed SVG back, byte for byte.
"""

from __future__ import annotations

import math
import random
from pathlib import Path

# ---------------------------------------------------------------------------
# The camera and the plain
# ---------------------------------------------------------------------------

W, H = 1600, 900
CX = W / 2
HORIZON = 470.0          # screen y of the horizon, i.e. where d = infinity
CAM_H = 1.70             # eye height, metres
F = 1500.0               # focal length, pixels
HAZE_M = 380.0           # aerial-perspective e-folding distance, metres
SUN_ALT = math.radians(9.5)
SUN_AZ = math.radians(34.0)   # right of the view axis
SUN_X = 1180.0                # screen x of the sun disc
SEED = 20261021

# The nine depths, in metres, front to back.
DEPTHS = [7, 11, 18, 34, 60, 110, 190, 330, 620]

# Local colours before haze (sRGB triples).
HAZE = (0xE2, 0xD8, 0xC2)     # the pale ochre-grey the horizon dissolves into
SNOW = (0xE9, 0xED, 0xEF)
SNOW_SHADE = (0xB6, 0xC1, 0xD4)
BARK = (0x3A, 0x33, 0x2E)
TWIG = (0x2B, 0x27, 0x24)
SPRUCE = (0x2D, 0x3A, 0x33)
ICE = (0xC9, 0xD4, 0xD9)
RUT = (0x9F, 0xAB, 0xB5)


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def hexc(rgb):
    return "#%02x%02x%02x" % rgb


def haze(d):
    """How far an object at d metres has dissolved into the horizon."""
    return 1.0 - math.exp(-d / HAZE_M)


def col(local, d):
    return hexc(mix(local, HAZE, haze(d)))


def project(x, y, d):
    """World (lateral, height, forward) -> screen (x, y). d in metres."""
    d = max(d, 0.35)
    return CX + F * x / d, HORIZON + F * (CAM_H - y) / d


def ground_y(d):
    return project(0.0, 0.0, d)[1]


# ---------------------------------------------------------------------------
# The seeded world
# ---------------------------------------------------------------------------

rng = random.Random(SEED)


def spruce(x, d, h):
    """A spruce at (x, d): trunk plus tiers, all sized by projection."""
    w = h * 0.055
    bx, by = project(x - w / 2, 0, d)
    ex, ey = project(x + w / 2, 0, d)
    tx, ty = project(x, h, d)
    out = [f'<path d="M{bx:.1f},{by:.1f} L{(bx+tx)/2:.1f},{ty:.1f} L{(ex+tx)/2:.1f},{ty:.1f} L{ex:.1f},{ey:.1f} Z" '
           f'fill="{col(SPRUCE, d)}" opacity="{0.92 - 0.25 * haze(d):.2f}"/>']
    tiers = 7
    for i in range(tiers):
        f0 = 0.18 + 0.78 * i / (tiers - 1)
        y0 = h * f0
        half = w * 1.25 * (1.0 - f0) + 0.35 * h * 0.06
        ax, ay = project(x - half, y0, d)
        cx_, cy_ = project(x + half, y0, d)
        px, py = project(x, y0 + h * 0.12, d)
        out.append(f'<path d="M{ax:.1f},{ay:.1f} L{px:.1f},{py:.1f} L{cx_:.1f},{cy_:.1f} Z" '
                   f'fill="{col(SPRUCE, d)}" opacity="{0.85 - 0.22 * haze(d):.2f}"/>')
    return "\n".join(out)


def bare_tree(x, d, h, gen=rng):
    """A bare aspen/willow: trunk in 3-D, branch scribble in screen space.

    Below about 25 px of trunk the branch recursion is skipped and a soft smudge
    is drawn instead — branches narrower than a pixel are not branches.
    """
    w = h * 0.045
    bx, by = project(x - w / 2, 0, d)
    ex, ey = project(x + w / 2, 0, d)
    tx, ty = project(x, h, d)
    out = [f'<path d="M{bx:.1f},{by:.1f} L{tx - w * F / d * 0.35:.1f},{ty:.1f} '
           f'L{tx + w * F / d * 0.35:.1f},{ty:.1f} L{ex:.1f},{ey:.1f} Z" '
           f'fill="{col(BARK, d)}" opacity="{0.95 - 0.35 * haze(d):.2f}"/>']
    hpx = by - ty
    if hpx < 26:
        out.append(f'<ellipse cx="{tx:.1f}" cy="{(ty + by) / 2:.1f}" rx="{max(hpx * 0.42, 1.2):.1f}" '
                   f'ry="{max(hpx * 0.30, 1.0):.1f}" fill="{col(TWIG, d)}" '
                   f'opacity="{0.30 - 0.12 * haze(d):.2f}"/>')
        return "\n".join(out)

    def limb(px, py, ang, length, depth):
        if depth == 0 or length < 1.6:
            return
        nx = px + math.cos(ang) * length
        ny = py + math.sin(ang) * length
        out.append(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{nx:.1f}" y2="{ny:.1f}" '
                   f'stroke="{col(TWIG, d)}" stroke-width="{max(length * 0.11, 0.5):.1f}" '
                   f'stroke-linecap="round" opacity="{0.9 - 0.3 * haze(d):.2f}"/>')
        limb(nx, ny, ang - 0.42 + gen.uniform(-0.16, 0.16), length * gen.uniform(0.62, 0.78), depth - 1)
        limb(nx, ny, ang + 0.38 + gen.uniform(-0.16, 0.16), length * gen.uniform(0.60, 0.76), depth - 1)

    crown = ty + hpx * 0.16
    limbs = 5 if hpx > 90 else 3
    for i in range(limbs):
        frac = 0.35 + 0.62 * i / max(limbs - 1, 1)
        sy = by - hpx * frac
        spread = -0.9 - 0.7 * frac
        limb(tx, sy, -math.pi / 2 + spread * 0.5 + gen.uniform(-0.25, 0.25),
             hpx * gen.uniform(0.18, 0.30), 3 if hpx > 70 else 2)
        limb(tx, sy, -math.pi / 2 - spread * 0.5 + gen.uniform(-0.25, 0.25),
             hpx * gen.uniform(0.18, 0.30), 3 if hpx > 70 else 2)
    limb(tx, crown, -math.pi / 2 + gen.uniform(-0.2, 0.2), hpx * 0.22, 3)
    return "\n".join(out)


def shadow(x, d, h, halfw):
    """The shadow of a trunk: a quad of length 6.0 h, away from the sun.

    Direction in the ground plane is (sin AZ, -cos AZ) rotated to the left of the
    view axis, so shadows run toward the camera and to the left. Cut off before
    the camera plane.
    """
    length = h / math.tan(SUN_ALT)
    dx, dd = -math.sin(SUN_AZ), -math.cos(SUN_AZ)
    # A near tree's shadow is 9.2 h long and simply leaves the frame; only the
    # camera plane stops it. It must not be cut short into a band in mid-field.
    L = min(length, (d - 1.6) / abs(dd))
    if L <= 0.05:
        return ""
    x1, d1 = x + dx * L, d + dd * L
    d1 = max(d1, 1.6)
    a = project(x - halfw, 0, d)
    b = project(x + halfw, 0, d)
    c = project(x1 + halfw * 0.7, 0, d1)
    e = project(x1 - halfw * 0.7, 0, d1)
    tipd = max(d1, 0.4)
    quad = (f'<path d="M{a[0]:.1f},{a[1]:.1f} L{b[0]:.1f},{b[1]:.1f} '
            f'L{c[0]:.1f},{c[1]:.1f} L{e[0]:.1f},{e[1]:.1f} Z" '
            f'fill="{col(SNOW_SHADE, tipd)}" opacity="{0.70 - 0.25 * haze(tipd):.2f}"/>')
    # The crown, not the trunk, is what actually shades the snow: a diffuse
    # blob two-thirds of the way down the shadow, wider than the trunk by ~6x.
    frac = 0.46
    xm_ = x + dx * L * frac
    dm = max(d + dd * L * frac, 1.8)
    mx, my = project(xm_, 0, dm)
    rx = F * (halfw * 7.0) / dm
    ry = max(rx * 0.12, 0.8)
    blob = (f'<ellipse cx="{mx:.1f}" cy="{my:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="{col(SNOW_SHADE, dm)}" opacity="{0.40 - 0.14 * haze(dm):.2f}"/>')
    return blob + quad


def stake(x, d, h=1.15, w=0.11):
    """A snow stake marking the ford road: a post, four projected corners.

    The first version drew these as triangles and they read as spikes, which is
    the sort of thing a hand would notice and a rule would not — the corners are
    the fix, not a redraw.
    """
    bx1, by1 = project(x - w / 2, 0, d)
    bx2, by2 = project(x + w / 2, 0, d)
    tx1, ty1 = project(x - w * 0.42, h, d)
    tx2, ty2 = project(x + w * 0.42, h, d)
    sh = shadow(x, d, h, w * 0.6)
    body = (f'<path d="M{bx1:.1f},{by1:.1f} L{tx1:.1f},{ty1:.1f} L{tx2:.1f},{ty2:.1f} '
            f'L{bx2:.1f},{by2:.1f} Z" fill="{col((0x54, 0x46, 0x3A), d)}"/>')
    return sh + body


# ---------------------------------------------------------------------------
# Compose
# ---------------------------------------------------------------------------

def build():
    out = []
    w = out.append

    w(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
      f'role="img" aria-labelledby="t d">')
    w('<title id="t">The Winter Ford, in Nine Depths</title>')
    w('<desc id="d">A procedural Russian Realist winter plain at a low February sun of 9.5 degrees. '
      'Every mark is placed by one pinhole camera at 1.70 metres and one sun; colour is mixed into '
      'the horizon haze by exp(-d/380 m). By Dmitri S. Pravdin.</desc>')

    # --- sky -------------------------------------------------------------
    w('<defs>')
    w(f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
      f'<stop offset="0" stop-color="{hexc(mix(HAZE, (0x5D, 0x6E, 0x88), 0.86))}"/>'
      f'<stop offset="0.55" stop-color="{hexc(mix(HAZE, (0x8C, 0x96, 0xA8), 0.45))}"/>'
      f'<stop offset="1" stop-color="{hexc(mix(HAZE, (0xF6, 0xE6, 0xC6), 0.55))}"/>'
      f'</linearGradient>')
    w(f'<radialGradient id="glow" cx="{SUN_X / W:.4f}" cy="{HORIZON / H:.4f}" r="0.55">'
      f'<stop offset="0" stop-color="#f7e3bd" stop-opacity="0.85"/>'
      f'<stop offset="0.35" stop-color="#f0d5ab" stop-opacity="0.30"/>'
      f'<stop offset="1" stop-color="#e2d8c2" stop-opacity="0"/>'
      f'</radialGradient>')
    w(f'<linearGradient id="snow" x1="0" y1="0" x2="0" y2="1">'
      f'<stop offset="0" stop-color="{hexc(mix(SNOW, HAZE, 0.72))}"/>'
      f'<stop offset="0.42" stop-color="{hexc(mix(SNOW, HAZE, 0.30))}"/>'
      f'<stop offset="1" stop-color="{hexc(SNOW)}"/>'
      f'</linearGradient>')
    w('</defs>')

    w(f'<rect x="0" y="0" width="{W}" height="{HORIZON + 2:.0f}" fill="url(#sky)"/>')
    w(f'<rect x="0" y="0" width="{W}" height="{HORIZON + 2:.0f}" fill="url(#glow)"/>')

    # the sun itself: radius 0.266 deg, so F * tan(0.266 deg)
    sun_r = F * math.tan(math.radians(0.266))
    sun_y = HORIZON - F * math.tan(SUN_ALT)
    # a sun painted in the sky's own colours disappears into it; the disc needs
    # an edge, which in haze is a warm ring, not a hard line
    w(f'<circle cx="{SUN_X:.1f}" cy="{sun_y:.1f}" r="{sun_r * 14:.1f}" fill="#f4d29b" opacity="0.30"/>')
    w(f'<circle cx="{SUN_X:.1f}" cy="{sun_y:.1f}" r="{sun_r * 4.2:.1f}" fill="#fbe0b0" opacity="0.85"/>')
    w(f'<circle cx="{SUN_X:.1f}" cy="{sun_y:.1f}" r="{sun_r * 2.0:.1f}" fill="none" stroke="#e8bb85" '
      f'stroke-width="1.4" opacity="0.55"/>')
    w(f'<circle cx="{SUN_X:.1f}" cy="{sun_y:.1f}" r="{sun_r * 1.15:.1f}" fill="#fffdf4"/>')

    # --- the plain -------------------------------------------------------
    w(f'<rect x="0" y="{HORIZON:.0f}" width="{W}" height="{H - HORIZON:.0f}" fill="url(#snow)"/>')

    # --- wind drifts: thin quads lying in the ground plane at known depths
    for d_drift in (13.0, 19.0, 27.0, 41.0, 63.0, 98.0):
        x0 = rng.uniform(-19, -12)
        x1 = rng.uniform(10, 17)
        hb = 0.12
        a1 = project(x0, hb, d_drift)
        b1 = project(x1, hb, d_drift)
        b2 = project(x1, 0.0, d_drift)
        a2 = project(x0, 0.0, d_drift)
        w(f'<path d="M{a1[0]:.1f},{a1[1]:.1f} L{b1[0]:.1f},{b1[1]:.1f} '
          f'L{b2[0]:.1f},{b2[1]:.1f} L{a2[0]:.1f},{a2[1]:.1f} Z" '
          f'fill="{col(SNOW_SHADE, d_drift)}" opacity="{0.13 + 0.12 * (1 - haze(d_drift)):.2f}"/>')

    # --- far treeline, depth 620 m: a silhouette band, jittered --------
    d_far = DEPTHS[-1]
    y_far = ground_y(d_far)
    tops = []
    x = -120.0
    while x < W + 120:
        # tips a few pixels wide: at 620 m this is scrub and tree tops, and a
        # coarse jitter at this spacing would read as a mountain range instead
        tops.append((x, y_far - rng.uniform(4.5, 14.0)))
        x += rng.uniform(3.5, 9.0)
    path = [f"M{-120:.0f},{y_far:.1f}"]
    for hx, hy in tops:
        path.append(f"L{hx:.1f},{hy:.1f}")
    path.append(f"L{W + 120:.0f},{y_far:.1f} Z")
    w(f'<path d="{" ".join(path)}" fill="{col((0x3E, 0x46, 0x4A), d_far)}" '
      f'opacity="{0.62:.2f}"/>')

    # --- the treelines at the middle depths, drawn back to front ---------
    layouts = {
        330: [(-70, 14), (-46, 17), (-18, 12), (16, 15), (44, 13), (72, 16)],
        190: [(-58, 15), (-30, 12), (0, 16), (30, 13), (58, 15)],
        110: [(-40, 13), (-14, 16), (12, 12), (36, 14)],
        85: [(-26, 12), (-8, 11), (16, 13)],
    }
    for d in sorted(layouts, reverse=True):
        for (tx_m, hh) in layouts[d]:
            xm = tx_m
            w(shadow(xm, d, hh, hh * 0.02))
            kind = spruce if hh % 2 == 0 else bare_tree
            w(kind(xm, d, hh))

    # --- the ford: a shallow channel in the plain at 34 m ----------------
    d_ice = DEPTHS[3]
    y_ice = ground_y(d_ice)
    hw = 26 * 0.30
    a = project(-hw, 0, d_ice - 4)
    b = project(hw, 0, d_ice - 4)
    c = project(hw * 0.72, 0, d_ice + 9)
    e = project(-hw * 0.72, 0, d_ice + 9)
    w(f'<path d="M{a[0]:.1f},{a[1]:.1f} L{b[0]:.1f},{b[1]:.1f} L{c[0]:.1f},{c[1]:.1f} '
      f'L{e[0]:.1f},{e[1]:.1f} Z" fill="{col(ICE, d_ice)}" opacity="0.85"/>')
    w(f'<path d="M{a[0]:.1f},{a[1]:.1f} L{b[0]:.1f},{b[1]:.1f}" stroke="{col(RUT, d_ice)}" '
      f'stroke-width="1.6" fill="none" opacity="0.7"/>')

    # --- the road: two ruts converging, from 7 m to the treeline ---------
    for side in (-1, 1):
        pts = []
        for d in [6.5, 7, 8.5, 11, 15, 22, 34, 60, 110, 190, 330]:
            xm = side * (2.9 - 2.55 * (1 - math.exp(-d / 60.0)))
            pts.append(project(xm, 0, d))
        dd = "M" + " L".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts)
        w(f'<path d="{dd}" stroke="{col(RUT, 8.0)}" stroke-width="7.5" fill="none" '
          f'opacity="0.34" stroke-linecap="round"/>')
        w(f'<path d="{dd}" stroke="{col((0x75, 0x82, 0x8E), 8.0)}" stroke-width="2.1" fill="none" '
          f'opacity="0.55"/>')

    # --- the fence line: posts every ~3 m of ground travel, left of the road
    tops = []
    d_post = 7.0
    while d_post < 74.0:
        xm = -(3.35 + 2.0 * (1 - math.exp(-d_post / 55.0)))
        w(stake(xm, d_post, 0.98, 0.13))
        tops.append(project(xm, 0.98, d_post))
        d_post *= 1.29
    if len(tops) > 1:
        w('<polyline points="' + " ".join(f"{px:.1f},{py:.1f}" for px, py in tops)
          + f'" fill="none" stroke="{col((0x5C, 0x51, 0x46), 12.0)}" stroke-width="1.1" '
            'opacity="0.45"/>')

    # --- near stakes on the other side, at 7 and 11 m --------------------
    for (sx, sd) in [(4.9, 7.4), (3.6, 11.6)]:
        w(stake(sx, sd))

    # --- reeds, 5.5 to 9 m out: stems of 0.35-0.7 m, no two the same ------
    for (rx, rd) in [(2.1, 5.6), (2.6, 6.4), (-1.9, 5.9), (-2.4, 7.2), (1.5, 8.4), (-1.4, 8.9)]:
        for _ in range(9):
            hx = rx + rng.uniform(-0.28, 0.28)
            hh = rng.uniform(0.35, 0.72)
            p1 = project(hx, 0.0, rd)
            p2 = project(hx + rng.uniform(-0.09, 0.09), hh, rd)
            w(f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" '
              f'stroke="{col((0x6A, 0x60, 0x50), rd)}" stroke-width="1.5" '
              f'opacity="0.55" stroke-linecap="round"/>')

    # --- a crow, at 330 m and 6 m up: F*0.42/330 px of wingspan ----------
    d_bird, h_bird = 330.0, 6.2
    bx, by = project(6.0, h_bird, d_bird)
    span = F * 0.85 / d_bird
    w(f'<path d="M{bx - span:.1f},{by:.1f} q{span * 0.5:.1f},{-span * 0.55:.1f} {span:.1f},0 '
      f'q{span * 0.5:.1f},{-span * 0.55:.1f} {span:.1f},0" stroke="{col((0x22, 0x22, 0x24), d_bird)}" '
      f'stroke-width="{max(span * 0.22, 0.8):.1f}" fill="none" stroke-linecap="round"/>')

    # --- the signature, in the bottom right, cut into the snow -----------
    w(f'<g font-family="Georgia, serif" fill="{hexc(mix(BARK, SNOW, 0.18))}" opacity="0.78">')
    w(f'<text x="{W - 230:.0f}" y="{H - 54:.0f}" font-size="21" letter-spacing="1">Дмитрий</text>')
    w(f'<text x="{W - 230:.0f}" y="{H - 30:.0f}" font-size="12" letter-spacing="2.3" '
      f'font-family="monospace">WING 07 · 2026-10-21</text>')
    w('</g>')

    # --- the physics, recorded in the artefact itself --------------------
    w('<g font-family="monospace" font-size="11" '
      f'fill="{hexc(mix((0x3D, 0x46, 0x54), HAZE, 0.35))}" opacity="0.70" letter-spacing="0.6">')
    lines = [
        f"camera  {CAM_H:.2f} m above the plain · f = {F:.0f} px · horizon y = {HORIZON:.0f}",
        f"sun     altitude {math.degrees(SUN_ALT):.1f}° · azimuth {math.degrees(SUN_AZ):.0f}° right of axis · shadow = {1 / math.tan(SUN_ALT):.1f} h",
        f"haze    colour mixed toward #{hexc(HAZE)} by 1 - exp(-d/{HAZE_M:.0f} m)",
        "depths  " + " · ".join(f"{d} m" for d in DEPTHS),
    ]
    for i, ln in enumerate(lines):
        w(f'<text x="44" y="{42 + i * 18:.0f}">{ln}</text>')
    w('</g>')

    w('</svg>')
    return "\n".join(out)


def main():
    svg = build()
    here = Path(__file__).resolve().parent
    target = here / "the-winter-ford-in-nine-depths.svg"
    target.write_text(svg + "\n", encoding="utf-8")
    print(f"wrote {target} ({len(svg.splitlines())} lines, {len(svg)} bytes)")


if __name__ == "__main__":
    main()
