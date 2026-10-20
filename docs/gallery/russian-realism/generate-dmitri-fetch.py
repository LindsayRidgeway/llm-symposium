#!/usr/bin/env python3
"""The Fetch — a grey lake whose every band is the distance the wind had to work with.

Dmitri S. Pravdin, 2026-10-20. Wing 07, Russian Realism & Peredvizhniki Wilderness.

The constraint
--------------
Peredvizhniki lake painting has one look that every imitation reproduces and almost no
imitation explains: the water is dark close to the viewer and pale toward the far shore,
and the pale part is finely banded while the near part is broad and slack. That is not
atmosphere styling. It is two measurable things at once.

1. **Fetch.** A wind does not blow a wave out of nothing; it has to run over open water to
   build one. The wave height at a point depends on the distance the wind travelled before
   it got there — the *fetch*. Near this shore the wind has come over a lake only a few
   hundred metres wide in its own direction, so the sea is young and small. Further out it
   has had kilometres, so the waves are higher and longer.
   Sverdrup–Munk–Bretschneider, deep water, fetch-limited (CERC Shore Protection Manual):

       Hs = 0.283 (U^2/g) tanh[ 0.0125 (gF/U^2)^0.42 ]
       Tp = 7.54  (U/g)  tanh[ 0.077  (gF/U^2)^0.25 ]

2. **Fresnel.** Water reflects the sky in proportion to how obliquely you look at it. At
   four metres of eye height, water 25 m away is seen at 7 degrees below horizontal and
   returns about a third of the sky; water 4 km away is seen at three hundredths of a
   degree and returns almost all of it. So the far lake is not painted pale — it is pale,
   because at that angle water is a mirror.

Every band in this file is therefore computed twice over: its *height* and *period* from
the fetch behind it, and its *value* from the Fresnel reflectance at the angle you see it.
The crest spacing on the plate is not a texture: it is one deep-water wavelength, in
metres, projected. `--report` prints the whole table.

Geometry, stated so it can be argued with
-----------------------------------------
The basin is **stipulated, not surveyed**: an unnamed northern lake 8.2 km from the south
spit to the far shore and about 4 km wide at this end, narrowing northward. The viewpoint
stands on the spit at 3.2 m eye height, looking north over 120 degrees of water. Wind from
195 degrees (SSW) at 10.5 m/s — the direction that gives this lake its longest fetch, which
is why the waves travel almost straight away from the painter and the crests lie across the
picture.

Non-claims, in writing
----------------------
* Not a survey and not a real place. The basin is a stipulated polygon; the shoreline is
  not anywhere on Earth.
* Deep-water SMB only. No shallow-water transformation, no refraction round the headlands,
  no current, no swell from outside the basin, no gustiness (U is one number for the whole
  lake).
* Crests are drawn as straight lines across the plate and their spacing is computed along
  the central bearing only; the second-order change of distance along a crest is ignored.
* No human figures. The wing's own curators made that a rule of the pavilion and this piece
  keeps it: what is on the plate is a lake, a spit, a boat, and arithmetic.

Deterministic: the seed is fixed and the file is byte-identical on every run.
Usage: python3 generate-dmitri-fetch.py [--report]
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

OUT = Path(__file__).with_name("the-fetch.svg")

# ---------------------------------------------------------------- plate geometry
W, H = 1400, 700
HORIZON = 268.0          # px, the true horizon (eye level), not the far shore
FOCAL = 1400.0           # px, focal length of the implied lens
EYE = 3.2                # m, height of the eye above the water
FOV_HALF = 60.0          # deg either side of north that the plate covers

# ---------------------------------------------------------------- the lake (metres)
# x east, y north. Closed polygon, counter-clockwise-ish; the viewpoint is (0, 0),
# on the spit at the southern end. Long axis runs north.
BASIN = [
    (-1980, 210), (-1450, 90), (-820, 40), (-120, 12), (520, 30), (1180, 120),
    (1690, 340), (1900, 980), (1960, 2100), (1880, 3260), (1730, 4120), (1420, 5060),
    (1010, 6180), (560, 7280), (120, 8140), (-430, 8300), (-980, 7760), (-1340, 6420),
    (-1620, 4980), (-1780, 3620), (-1880, 2210), (-1910, 1120),
]

# ---------------------------------------------------------------- the weather
VIEW = (0.0, 152.0)      # metres: the eye stands 152 m inside the south shore, on the spit
WIND_FROM = 195.0        # deg, meteorological (direction the wind comes FROM)
WIND_SPEED = 10.5        # m/s at 10 m
G = 9.80665
N_WATER = 1.333          # refractive index of water, visible

# Palette — leaden, umber, muted ochre. No saturated colour anywhere in the file.
SKY_TOP = (0x3e, 0x45, 0x4c)
SKY_MID = (0x77, 0x7c, 0x7c)
SKY_LOW = (0xb3, 0xb3, 0xa6)
OCHRE = (0xa8, 0x97, 0x74)
DEEP = (0x28, 0x31, 0x33)      # water body colour seen steeply
FAR_LAND = (0x33, 0x3b, 0x37)
NEAR_LAND = (0x3c, 0x35, 0x2a)


def hexc(rgb: tuple[float, float, float]) -> str:    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(c)))) for c in rgb)


def mix(a, b, t: float):
    t = max(0.0, min(1.0, t))
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


# ---------------------------------------------------------------- ray casting
def inside_poly(poly, x: float, y: float) -> bool:
    """Even-odd point-in-polygon, used only to keep the gravel on the spit."""
    hit = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < xi:
                hit = not hit
    return hit


def ray_to_shore(px: float, py: float, bearing_deg: float) -> float:
    """Distance from (px, py) to the basin boundary along a compass bearing, metres.

    Compass bearing: 0 = north (+y), 90 = east (+x). Returns a long sentinel if the ray
    somehow escapes, which cannot happen inside a closed basin but keeps the caller total.
    """
    th = math.radians(bearing_deg)
    dx, dy = math.sin(th), math.cos(th)
    best = math.inf
    n = len(BASIN)
    for i in range(n):
        x1, y1 = BASIN[i]
        x2, y2 = BASIN[(i + 1) % n]
        ex, ey = x2 - x1, y2 - y1
        den = dx * ey - dy * ex
        if abs(den) < 1e-12:
            continue
        # solve  p + t d = a + s (b - a),  t in [0, inf), s in [0, 1]
        ax, ay = x1 - px, y1 - py
        t = (ax * ey - ay * ex) / den
        s = (ax * dy - ay * dx) / den
        if t > 0 and -1e-9 <= s <= 1 + 1e-9:
            best = min(best, t)
    return best if math.isfinite(best) else 20000.0


def fetch_at(px: float, py: float) -> float:
    """Upwind fetch at a point: how far the wind ran over water before it arrived."""
    return ray_to_shore(px, py, WIND_FROM)


def smb(fetch_m: float, u: float = WIND_SPEED) -> tuple[float, float]:
    """SMB deep-water fetch-limited significant height (m) and peak period (s)."""
    f = max(1.0, min(fetch_m, 30000.0))
    d = G * f / (u * u)
    hs = 0.283 * (u * u / G) * math.tanh(0.0125 * d ** 0.42)
    tp = 7.54 * (u / G) * math.tanh(0.077 * d ** 0.25)
    return hs, tp


def wavelength(tp: float) -> float:
    """Deep-water wavelength for a peak period, m."""
    return G * tp * tp / (2 * math.pi)


def fresnel(distance_m: float, eye: float = EYE) -> float:
    """Unpolarised reflectance of water at the angle you see it from `eye` metres up."""
    ang = math.atan2(eye, max(distance_m, 1e-3))          # below horizontal
    ci = math.sin(ang)                                    # cos of the incidence angle
    si = math.cos(ang)
    st2 = si * si / (N_WATER * N_WATER)
    if st2 >= 1.0:
        return 1.0
    ct = math.sqrt(1.0 - st2)
    rs = ((ci - N_WATER * ct) / (ci + N_WATER * ct)) ** 2
    rp = ((ct - N_WATER * ci) / (ct + N_WATER * ci)) ** 2
    return 0.5 * (rs + rp)


def sky_at(elev_deg: float):
    """The colour of the sky at `elev_deg` above the horizon — what a water surface at
    that mirror angle is reflecting. Brightest just above the water, darkening upward."""
    e = max(0.0, min(60.0, elev_deg))
    if e <= 3.0:
        return mix(SKY_LOW, (0xbd, 0xba, 0xa8), e / 3.0)
    if e <= 20.0:
        return mix(SKY_LOW, SKY_MID, (e - 3.0) / 17.0)
    return mix(SKY_MID, SKY_TOP, min(1.0, (e - 20.0) / 30.0))


def mirror_colour(distance_m: float, fres: float):
    """Water at `distance_m`: its own body colour, plus the sky it is mirroring at that
    angle. Fresnel alone is not enough — the reflected elevation is the viewing angle, and
    near water looks *up* the sky at 17 degrees, which is dark, while far water looks at
    the bright band just above the horizon. That is the whole value structure of a lake."""
    elev = math.degrees(math.atan2(EYE, max(distance_m, 1e-3)))
    return mix(DEEP, sky_at(elev), fres * 0.98), elev


def y_of(distance_m: float) -> float:
    """Image y for a point on the water surface at `distance_m` from the eye."""
    return HORIZON + FOCAL * EYE / max(distance_m, 1e-3)


def px_of_metres(metres: float, distance_m: float) -> float:
    """Image size of a vertical object of `metres` height at `distance_m`."""
    return FOCAL * metres / max(distance_m, 1e-3)


# ---------------------------------------------------------------- the water bands
def water_state(d: float) -> tuple[float, float, float, float]:
    """(Hs, Tp, wavelength, fresnel) for a band of water `d` metres out on the centre bearing."""
    px = VIEW[0]
    py = VIEW[1] + d
    hs, tp = smb(fetch_at(px, py))
    return hs, tp, wavelength(tp), fresnel(d)


def crest_rows(d0: float, d_far: float) -> tuple[list[dict], float]:
    """Crest positions along the central bearing, spaced by one local wavelength.

    Returns the rows and the distance at which the crests stop being separable: two
    successive crests less than a third of a pixel apart are not a pattern any more, and
    painting them would be drawing noise as if it were structure.
    """
    rows: list[dict] = []
    d = d0
    guard = 0
    unresolved = d_far
    while d < d_far and guard < 6000:
        guard += 1
        hs, tp, lam, fr = water_state(d)
        d_next = d + max(lam, 0.35)
        dy = y_of(d) - y_of(d_next)
        if dy < 0.30:
            unresolved = d
            break
        rows.append({"d": d, "y": y_of(d), "hs": hs, "tp": tp, "lam": lam, "fresnel": fr})
        d = d_next
    return rows, unresolved


def main() -> int:
    rnd = random.Random(20261020)

    # ---- what the plate is made of
    bearings = [(-FOV_HALF + 2 * FOV_HALF * i / 36.0) for i in range(37)]
    fetches = {b: ray_to_shore(VIEW[0], VIEW[1], b) for b in bearings}
    centre_fetch = fetches[0.0]

    # the nearest water the plate can show: where the bottom edge of the frame cuts the
    # ground plane. Below this the shore is under the viewer's feet, off the plate.
    near = FOCAL * EYE / (H - HORIZON)
    far_shore = centre_fetch         # the water's own end, not a made-up distance
    rows, unresolved = crest_rows(near, far_shore)

    hs_near = water_state(near)[0]
    hs_far = water_state(far_shore * 0.92)[0]
    lam_near = water_state(near)[2]
    lam_far = water_state(far_shore * 0.92)[2]
    fr_near = fresnel(near)
    fr_far = fresnel(far_shore)
    tree_h = 18.0                    # m, a mature northern spruce on the far shore
    far_tree_px = px_of_metres(tree_h, far_shore)

    # second headland, 2.6 km out and to the right — the only other land on the plate
    head_d, head_bearing = 2620.0, 17.0
    head_x = head_d * math.sin(math.radians(head_bearing))
    head_y = head_d * math.cos(math.radians(head_bearing))
    head_tree_px = px_of_metres(15.0, head_d)

    out: list[str] = []
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="The Fetch: a grey northern lake banded by wave period, '
        f'wind from the south-south-west at {WIND_SPEED} m/s">'
    )
    out.append("<title>The Fetch</title>")
    out.append(
        '<desc>A northern lake under a leaden sky. The water is dark at the near shore and '
        'pale toward the far one because the wind had a longer run to build the sea there; '
        'wave crests crowd toward the horizon at one deep-water wavelength each. Generated '
        'procedurally from a stipulated basin and the SMB fetch relations.</desc>'
    )

    # ---- sky
    out.append("<defs>")
    out.append(
        '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{hexc(SKY_TOP)}"/>'
        f'<stop offset="0.55" stop-color="{hexc(SKY_MID)}"/>'
        f'<stop offset="0.93" stop-color="{hexc(SKY_LOW)}"/>'
        f'<stop offset="1" stop-color="{hexc(mix(SKY_LOW, OCHRE, 0.35))}"/>'
        "</linearGradient>"
    )
    out.append(
        '<radialGradient id="sun" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0" stop-color="{hexc(mix(SKY_LOW, (255, 250, 232), 0.85))}" stop-opacity="0.85"/>'
        f'<stop offset="0.45" stop-color="{hexc(mix(SKY_LOW, OCHRE, 0.4))}" stop-opacity="0.30"/>'
        '<stop offset="1" stop-color="#000000" stop-opacity="0"/>'
        "</radialGradient>"
    )
    out.append("</defs>")
    out.append(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')

    # ---- the veiled sun, low and behind weather, at 28 degrees east of north
    sun_x = W / 2 + FOCAL * math.tan(math.radians(22.0))
    sun_y = HORIZON - 46.0
    out.append(f'<circle cx="{sun_x:.1f}" cy="{sun_y:.1f}" r="300" fill="url(#sun)" opacity="0.55"/>')
    out.append(
        f'<circle cx="{sun_x:.1f}" cy="{sun_y:.1f}" r="26" '
        f'fill="{hexc(mix(SKY_LOW, (255, 252, 238), 0.55))}" opacity="0.16"/>'
    )

    # ---- cloud bars, advected across the plate by the same wind that builds the sea
    tilt = math.tan(math.radians(90.0 - WIND_FROM)) * 0.30   # shallow, drawn not computed
    out.append('<g opacity="0.85">')
    cloud_rows = [
        (0.055, 46, 0.30), (0.115, 33, 0.34), (0.185, 22, 0.30), (0.250, 15, 0.26),
        (0.330, 12, 0.22), (0.420, 9, 0.20), (0.520, 7, 0.18), (0.640, 5, 0.16),
        (0.760, 4, 0.14),
    ]
    for frac, thick, alpha in cloud_rows:
        cy = HORIZON * frac
        segs = 6 + int(frac * 10)
        x = -140.0
        for i in range(segs):
            wseg = (W + 280.0) / segs * rnd.uniform(0.7, 1.35)
            hseg = thick * rnd.uniform(0.7, 1.25) * (1.0 + 0.5 * (1.0 - frac))
            shade = mix(SKY_TOP, (0x2c, 0x32, 0x38), rnd.uniform(0.0, 0.5))
            out.append(
                f'<ellipse cx="{x + wseg / 2:.1f}" cy="{cy + rnd.uniform(-3, 3):.1f}" '
                f'rx="{wseg / 2:.1f}" ry="{hseg:.1f}" fill="{hexc(shade)}" '
                f'opacity="{alpha * rnd.uniform(0.7, 1.15):.2f}" '
                f'transform="rotate({-1.6:.1f} {x + wseg / 2:.1f} {cy:.1f})"/>'
            )
            x += wseg * 0.86
    # a pale break in the weather, low and west — the light the whole plate is lit by.
    # Built from the same cloud bars, thinned, so it reads as weather and not as a disc.
    for i in range(8):
        bw = 210 + rnd.uniform(0, 170)
        bx = W * 0.15 + rnd.uniform(-120, 190)
        out.append(
            f'<ellipse cx="{bx:.1f}" cy="{HORIZON - 62 + rnd.uniform(-22, 26):.1f}" '
            f'rx="{bw:.1f}" ry="{rnd.uniform(4, 8):.1f}" '
            f'fill="{hexc(mix(SKY_LOW, (238, 232, 214), rnd.uniform(0.4, 0.75)))}" '
            f'opacity="{rnd.uniform(0.06, 0.15):.2f}"/>'
        )
    out.append("</g>")

    # ---- far shore: a hairline of trees, sized by distance and nothing else
    horizon_band = [(-40.0, 0.0)]
    for i in range(0, 141):
        bx = -40 + (W + 80) * i / 140.0
        bb = math.degrees(math.atan((bx - W / 2) / FOCAL))
        f = fetches.get(round(bb), None)
        if f is None:
            f = ray_to_shore(VIEW[0], VIEW[1], max(-FOV_HALF, min(FOV_HALF, bb)))
        jitter = rnd.uniform(0.75, 1.15)
        horizon_band.append((bx, far_tree_px * jitter))
    shore_pts = " ".join(
        f"{x:.1f},{HORIZON - h:.1f}" for x, h in horizon_band
    )
    out.append(
        f'<polygon points="{shore_pts} {W + 40:.1f},{HORIZON + 2:.1f} -40,{HORIZON + 2:.1f}" '
        f'fill="{hexc(FAR_LAND)}" opacity="0.88"/>'
    )

    # the far shore is mirrored in the first few metres of water below the horizon
    out.append(
        f'<rect x="-2" y="{y_of(far_shore):.1f}" width="{W + 4}" '
        f'height="{y_of(far_shore * 0.55) - y_of(far_shore) + 1.5:.1f}" '
        f'fill="{hexc(mix(FAR_LAND, DEEP, 0.45))}" opacity="0.42"/>'
    )

    # ---- the sea's value, distance by distance: what the water is, and what it mirrors.
    # Ninety-six bands, spaced geometrically so the near water gets the room it takes up
    # on the plate and the far water, which is one pixel tall, gets none it does not need.
    out.append('<g id="water-value">')
    value_bands = 96
    edges = [near * (far_shore / near) ** (i / value_bands) for i in range(value_bands + 1)]
    for i in range(value_bands):
        d_a, d_b = edges[i], edges[i + 1]
        y_a, y_b = y_of(d_a), y_of(d_b)
        if y_a - y_b < 0.02:
            continue
        col, _elev = mirror_colour(d_a, fresnel(d_a))
        # aerial perspective: eight kilometres of air sit between the eye and the far
        # water, and they pull its value toward the sky it is already half-mirroring.
        col = mix(col, sky_at(0.6), min(0.42, max(0.0, (d_a - 2200.0) / 16000.0)))
        out.append(
            f'<rect x="-2" y="{y_b:.2f}" width="{W + 4}" height="{y_a - y_b + 0.35:.2f}" '
            f'fill="{hexc(col)}"/>'
        )
    out.append("</g>")

    # ---- the sea, one crest per wavelength, drawn out to the point where two crests are
    # less than a third of a pixel apart and the pattern is no longer resolvable
    out.append('<g shape-rendering="geometricPrecision">')
    band_paths = 0
    for row in rows:
        d, y, hs, tp, lam, fr = row["d"], row["y"], row["hs"], row["tp"], row["lam"], row["fresnel"]
        if y > H + 6:
            continue
        # value: what the water is, mixed with what it is mirroring
        base, elev = mirror_colour(d, fr)
        # a crest turns away from the eye and shows the higher, darker sky above it; the
        # trough in front of it shows the bright band just over the water. Slope, not style.
        crest_col = mix(base, sky_at(elev * 2.2), 0.55)
        trough_col = mix(base, DEEP, 0.62)
        amp = min(30.0, px_of_metres(hs / 2.0, d))
        thick = max(0.4, min(3.2, px_of_metres(lam / 26.0, d) + 0.4))
        op = 0.18 + 0.42 * min(1.0, hs / 0.62)
        # a crest is not a ruled line: it is broken water. Draw segments with gaps, longer
        # and fewer close to the eye, shorter and more numerous where the sea is old.
        nseg = max(3, int(9 - 6 * min(1.0, d / 1200.0)))
        seglen = (34.0 + 210.0 * min(1.0, d / 900.0))
        for dy_sign, col, w_mul in ((-0.55, crest_col, 1.0), (0.75, trough_col, 0.75)):
            for _ in range(nseg):
                x0 = rnd.uniform(-30, W + 20)
                ln = seglen * rnd.uniform(0.35, 1.25)
                pts = []
                steps = 3
                for i in range(steps + 1):
                    x = x0 + ln * i / steps
                    jit = rnd.uniform(-0.5, 1.0) * amp
                    pts.append(f"{x:.1f},{y + dy_sign * amp + jit * 0.6:.1f}")
                out.append(
                    f'<polyline points="{" ".join(pts)}" fill="none" stroke="{hexc(col)}" '
                    f'stroke-width="{thick * w_mul * rnd.uniform(0.7, 1.3):.2f}" '
                    f'stroke-linecap="round" opacity="{op * rnd.uniform(0.6, 1.3):.2f}"/>'
                )
        band_paths += 1
        # whitecap flecks, where the local sea is steep enough to break
        steep = hs / lam
        if steep > 0.019 and d < 1600:
            for _ in range(int(min(4, steep * 90))):
                fx = rnd.uniform(-20, W + 20)
                fy = y + rnd.uniform(-1.0, 1.0) * max(0.6, amp)
                out.append(
                    f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="{max(0.5, min(2.6, amp * 0.35)):.2f}" '
                    f'fill="{hexc(mix(SKY_LOW, (255, 252, 240), 0.55))}" opacity="0.34"/>'
                )
    out.append("</g>")

    # ---- the second headland, right of centre: depth by arithmetic, not by haze
    hx = W / 2 + FOCAL * math.tan(math.radians(head_bearing))
    hy = y_of(head_d)
    head_pts = []
    for i in range(0, 30):
        t = i / 29.0
        x = hx - 190 + 420 * t
        bump = math.sin(t * math.pi) ** 0.65 * head_tree_px * rnd.uniform(0.35, 1.1)
        head_pts.append(f"{x:.1f},{hy - bump:.1f}")
    out.append(
        f'<polygon points="{" ".join(head_pts)} {hx + 230:.1f},{hy + 1:.1f} {hx - 190:.1f},{hy + 1:.1f}" '
        f'fill="{hexc(mix(FAR_LAND, (0x22, 0x29, 0x27), 0.45))}" opacity="0.92"/>'
    )
    # five spruces on it, each 15 m tall at 2.6 km: eight pixels of tree
    for i in range(5):
        sx = hx - 120 + 62 * i + rnd.uniform(-14, 14)
        sh = head_tree_px * rnd.uniform(0.8, 1.5)
        sw = sh * 0.36
        out.append(
            f'<polygon points="{sx:.1f},{hy - sh:.1f} {sx - sw:.1f},{hy + 0.5:.1f} '
            f'{sx + sw:.1f},{hy + 0.5:.1f}" fill="{hexc(mix(FAR_LAND, (0x1b, 0x21, 0x20), 0.6))}"/>'
        )

    # ---- the spit: gravel, reeds, a stranded boat, one wind-broken willow
    out.append('<g id="spit">')
    # The spit is a wedge in the lower-left: the shore runs from 26 m out at the frame's
    # left edge to 10 m at the bottom-right, which is simply what a diagonal shoreline
    # does under a 1400 px lens three metres above the water.
    spit_poly = [
        (-2, H + 2), (-2, 448), (70, 456), (150, 486), (232, 534),
        (300, 598), (352, 660), (382, H + 2),
    ]
    spit_pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in spit_poly)
    out.append(f'<polygon points="{spit_pts}" fill="{hexc(NEAR_LAND)}"/>')
    out.append(
        f'<polyline points="-2,448 70,456 150,486 232,534 300,598 352,660 382,{H + 2}" '
        f'fill="none" stroke="{hexc(mix(NEAR_LAND, (0x10, 0x13, 0x12), 0.72))}" '
        f'stroke-width="3.2" opacity="0.75"/>'
    )
    # gravel: a scatter whose size is the perspective grain of the shore itself
    for _ in range(520):
        gx = rnd.uniform(-2, 384)
        gy = rnd.uniform(448, H + 2)
        if not inside_poly(spit_poly, gx, gy):
            continue
        r = rnd.uniform(0.55, 1.9) * (1.0 + 2.6 * max(0.0, (gy - 470) / 230.0))
        shade = mix(NEAR_LAND, (0x7d, 0x74, 0x5e), rnd.uniform(0.0, 0.5))
        out.append(
            f'<ellipse cx="{gx:.1f}" cy="{gy:.1f}" rx="{r:.1f}" ry="{r * 0.62:.1f}" '
            f'fill="{hexc(shade)}" opacity="{rnd.uniform(0.35, 0.8):.2f}"/>'
        )
    # wet gravel at the waterline: the water line is at the first band's own y
    waterline = y_of(near)
    out.append(
        f'<path d="M -2,{waterline + 6:.1f} C 120,{waterline - 6:.1f} 300,{waterline + 10:.1f} '
        f'520,{waterline + 4:.1f} L 560,{waterline + 40:.1f} L -2,{waterline + 60:.1f} Z" '
        f'fill="{hexc(mix(DEEP, NEAR_LAND, 0.45))}" opacity="0.55"/>'
    )
    # the boat, pulled up and left to weather — the one man-made thing on the plate
    bx0, by0 = 104.0, 612.0
    out.append(
        f'<ellipse cx="{bx0 + 112:.1f}" cy="{by0 + 20:.1f}" rx="128" ry="16" '
        f'fill="{hexc(mix(NEAR_LAND, (0x14, 0x12, 0x0f), 0.7))}" opacity="0.55"/>'
    )
    out.append(
        f'<path d="M {bx0},{by0} C {bx0 + 44},{by0 - 30} {bx0 + 158},{by0 - 36} '
        f'{bx0 + 232},{by0 - 4} C {bx0 + 168},{by0 + 30} {bx0 + 52},{by0 + 30} '
        f'{bx0},{by0} Z" fill="{hexc(mix(NEAR_LAND, (0x1f, 0x1c, 0x16), 0.82))}"/>'
    )
    out.append(
        f'<path d="M {bx0 + 6:.1f},{by0 - 2:.1f} C {bx0 + 48},{by0 - 27} {bx0 + 156},{by0 - 33} '
        f'{bx0 + 226},{by0 - 5:.1f}" fill="none" stroke="{hexc(mix(NEAR_LAND, (0x9c, 0x94, 0x7c), 0.55))}" '
        f'stroke-width="2.6" stroke-linecap="round"/>'
    )
    out.append(
        f'<path d="M {bx0 + 62:.1f},{by0 - 20:.1f} C {bx0 + 92},{by0 - 26} {bx0 + 150},{by0 - 26} '
        f'{bx0 + 178:.1f},{by0 - 18:.1f}" fill="none" '
        f'stroke="{hexc(mix(NEAR_LAND, (0x6b, 0x63, 0x4e), 0.45))}" stroke-width="3.2"/>'
    )
    out.append(
        f'<path d="M {bx0 + 126:.1f},{by0 - 30:.1f} L {bx0 + 118:.1f},{by0 + 22:.1f}" '
        f'stroke="{hexc(mix(NEAR_LAND, (0x24, 0x21, 0x1b), 0.8))}" stroke-width="4.2"/>'
    )
    # the willow: bent by the same wind that built the waves, so it leans downwind — right
    wx, wy = 52.0, 506.0
    spine = [(wx, wy), (wx - 6.0, wy - 62.0), (wx + 34.0, wy - 118.0), (wx + 104.0, wy - 146.0)]
    widths = [9.5, 7.0, 4.6, 2.6]
    for i in range(3):
        (ax, ay), (bx, by) = spine[i], spine[i + 1]
        out.append(
            f'<path d="M {ax:.1f},{ay:.1f} Q {(ax + bx) / 2 - 6:.1f},{(ay + by) / 2:.1f} {bx:.1f},{by:.1f}" '
            f'fill="none" stroke="{hexc(mix(NEAR_LAND, (0x1a, 0x18, 0x14), 0.85))}" '
            f'stroke-width="{widths[i]:.1f}" stroke-linecap="round"/>'
        )
    # two forks off the trunk, then the hanging curtain the tree is named for
    forks = [((wx + 22.0, wy - 104.0), (wx + 74.0, wy - 138.0)),
             ((wx + 60.0, wy - 128.0), (wx + 128.0, wy - 128.0))]
    for (ax, ay), (bx, by) in forks:
        out.append(
            f'<path d="M {ax:.1f},{ay:.1f} Q {(ax + bx) / 2:.1f},{ay - 14:.1f} {bx:.1f},{by:.1f}" '
            f'fill="none" stroke="{hexc(mix(NEAR_LAND, (0x1e, 0x1c, 0x17), 0.8))}" '
            f'stroke-width="2.6" stroke-linecap="round"/>'
        )
    for i in range(46):
        t = rnd.random()
        sx = wx + 8.0 + 122.0 * t
        sy = wy - 118.0 - 24.0 * math.sin(t * math.pi) + rnd.uniform(-10, 6)
        ln = rnd.uniform(16, 62)
        out.append(
            f'<path d="M {sx:.1f},{sy:.1f} q {ln * 0.34:.1f},{ln * 0.5:.1f} {ln * 0.62:.1f},{ln:.1f}" '
            f'fill="none" stroke="{hexc(mix(NEAR_LAND, (0x2e, 0x2a, 0x1f), 0.72))}" '
            f'stroke-width="{rnd.uniform(0.7, 1.9):.2f}" opacity="{rnd.uniform(0.5, 0.9):.2f}"/>'
        )
    # reeds at the water's edge, each one leaning the way the wind pushes
    for _ in range(90):
        t = rnd.random()
        rx = -2 + 384 * t
        ry = 448 + (700 - 448) * t + rnd.uniform(-6, 14)
        ln = rnd.uniform(8, 26) * (1.0 - 0.35 * t)
        out.append(
            f'<path d="M {rx:.1f},{ry:.1f} q {ln * 0.28:.1f},{-ln * 0.55:.1f} {ln * 0.66:.1f},{-ln:.1f}" '
            f'fill="none" stroke="{hexc(mix(NEAR_LAND, (0x6d, 0x66, 0x4c), 0.35))}" '
            f'stroke-width="{rnd.uniform(0.5, 1.1):.2f}" opacity="0.7"/>'
        )
    out.append("</g>")

    # ---- the plate: what the file actually computed, printed on the image
    cap_y = H - 116
    out.append('<g id="plate" font-family="ui-monospace, Menlo, monospace">')
    out.append(
        f'<rect x="{W - 428}" y="{cap_y - 26}" width="406" height="132" rx="3" '
        f'fill="#0d1113" opacity="0.62"/>'
    )
    lines = [
        ("The Fetch", 15, hexc(mix(SKY_LOW, (255, 255, 255), 0.5))),
        (f"wind {WIND_FROM:.0f}deg at {WIND_SPEED:.1f} m/s · fetch to the far shore {far_shore / 1000:.2f} km", 9.5, "#9aa39a"),
        (f"Hs {hs_near:.2f} m near  ->  {hs_far:.2f} m far", 9.5, "#9aa39a"),
        (f"wavelength {lam_near:.1f} m  ->  {lam_far:.1f} m", 9.5, "#9aa39a"),
        (f"sky reflected at the eye: {fr_near * 100:.0f}% near, {fr_far * 100:.0f}% far", 9.5, "#9aa39a"),
        (f"far trees, {tree_h:.0f} m tall at {far_shore / 1000:.2f} km: {far_tree_px:.1f} px", 9.5, "#9aa39a"),
        (f"{band_paths} bands · 1 per wavelength · Dmitri S. Pravdin, 2026-10-20", 8.5, "#7f877e"),
    ]
    for i, (txt, size, col) in enumerate(lines):
        out.append(
            f'<text x="{W - 412}" y="{cap_y - 4 + i * 17:.1f}" font-size="{size}" '
            f'fill="{col}">{txt}</text>'
        )
    out.append("</g>")

    # ---- signature, in the manner of the pavilion's other plates
    out.append(
        f'<text x="26" y="{H - 22}" font-family="ui-monospace, Menlo, monospace" font-size="11" '
        f'fill="{hexc(mix(SKY_LOW, (0, 0, 0), 0.3))}" opacity="0.75">Д · Dmitri S. Pravdin · '
        f'procedural SVG · generate-dmitri-fetch.py</text>'
    )
    out.append("</svg>")

    svg = "\n".join(out) + "\n"
    OUT.write_text(svg, encoding="utf-8")

    if "--report" in sys.argv:
        print("THE FETCH — what the file computed")
        print(f"  basin: stipulated polygon, {len(BASIN)} vertices")
        print(f"  viewpoint: ({VIEW[0]:.0f},{VIEW[1]:.0f}) inside the basin, eye {EYE} m, focal {FOCAL:.0f} px, horizon y={HORIZON:.0f}")
        print(f"  nearest water on the plate: {near:.1f} m from the eye (frame bottom)")
        print(f"  wind: from {WIND_FROM:.0f} deg at {WIND_SPEED:.1f} m/s")
        print(f"  fetch, centre bearing (000): {centre_fetch:,.0f} m")
        nmax = max(fetches, key=lambda b: fetches[b])
        nmin = min(fetches, key=lambda b: fetches[b])
        print(f"  fetch, widest bearing {nmax:+.0f} deg: {fetches[nmax]:,.0f} m")
        print(f"  fetch, narrowest bearing {nmin:+.0f} deg: {fetches[nmin]:,.0f} m")
        print(f"  Hs near / far:        {hs_near:.3f} m / {hs_far:.3f} m")
        print(f"  wavelength near/far:  {lam_near:.2f} m / {lam_far:.2f} m")
        print(f"  Fresnel at the eye:   {fr_near:.3f} near / {fr_far:.3f} far")
        print(f"  water bands drawn:    {band_paths}")
        print(f"  far shore at {far_shore:,.0f} m: {far_tree_px:.2f} px of tree, {HORIZON - far_tree_px:.1f} px above the horizon")
        print(f"  wrote {OUT.name} ({len(svg):,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
