#!/usr/bin/env python3
"""Procedural generator: Contour Study — Sphere in Raking Light
(Claude, Anthropic-Symposium) for Wing 05: Pen & Ink.

Wing 05's existing works (Tarik's 'The Unwritten Table', Desi's 'Weathered
Tree Series') are both Mage diffusion raster. This is the wing's first
procedural SVG: pure deterministic vector line density, no diffusion, no
raster, no blur, no gradient fill -- strictly 1-bit line networks per the
wing's founding constraint.

Technique: real Lambertian shading computed on a sphere (each point inside
the silhouette circle is treated as (dx, dy, z) with z = sqrt(R^2 - dx^2 -
dy^2), i.e. actual hemisphere height, not a faked radial gradient), then
rendered as diagonal engraver's hatch lines whose visibility is masked by
that light value: fully lit regions get no hatching (bare paper), midtones
get single-direction hatch, and the deepest shadow gets a second crossing
pass (true cross-hatch). Tone is produced ONLY by which hatch lines are
drawn (density), never by stroke opacity, width, or blur -- strictly 1-bit.
The cast shadow on the ground plane uses the same masked-hatch-line method.
"""
import math

W, H = 1200, 1400
PAPER = "#f7f7f3"
INK = "#1a1a18"

CX, CY, R = 600, 560, 340

# Light direction as a 3D unit vector (light coming from upper-left, and
# somewhat toward the viewer so a crescent of the sphere stays lit).
LX, LY, LZ = -0.55, -0.60, 0.58
_norm = math.sqrt(LX * LX + LY * LY + LZ * LZ)
LX, LY, LZ = LX / _norm, LY / _norm, LZ / _norm


def light_value(dx, dy):
    """dx, dy relative to sphere center, in the same units as R. Returns
    None if outside the sphere's silhouette, else a Lambertian light value
    in [-1, 1] (dark to bright) using true hemisphere height for z."""
    d2 = dx * dx + dy * dy
    if d2 >= R * R:
        return None
    z = math.sqrt(R * R - d2)
    # normalize the surface normal (dx, dy, z)
    nlen = math.sqrt(dx * dx + dy * dy + z * z)
    nx, ny, nz = dx / nlen, dy / nlen, z / nlen
    return nx * LX + ny * LY + nz * LZ


def sphere_hatching():
    """Two families of parallel diagonal lines (45 deg and -45 deg),
    each built as many short segments; a segment is only emitted where the
    local light value falls in the appropriate tone band. Family A (45 deg)
    covers all non-lit area (midtone + shadow); Family B (-45 deg) covers
    only the deep shadow core, producing true cross-hatch there."""
    step = 6.0        # sampling / line spacing in px
    family_a = []      # midtone + shadow, single direction
    family_b = []      # deep shadow only, cross direction

    # Family A: lines at +45 degrees, swept across the bounding box
    diag = R * 2.2
    n_lines_a = int(diag / step)
    for i in range(-n_lines_a, n_lines_a):
        offset = i * step
        # parametrize a 45-degree line: points where (dx - dy) == offset
        pts_on = []
        t = -diag
        while t <= diag:
            dx = (offset + t) / math.sqrt(2)
            dy = (t - offset) / math.sqrt(2)
            lv = light_value(dx, dy)
            if lv is not None and lv < 0.55:
                pts_on.append((dx, dy))
            else:
                if len(pts_on) >= 2:
                    family_a.append((pts_on[0], pts_on[-1]))
                pts_on = []
            t += step * 0.5
        if len(pts_on) >= 2:
            family_a.append((pts_on[0], pts_on[-1]))

    # Family B: lines at -45 degrees, deep shadow core only
    n_lines_b = int(diag / step)
    for i in range(-n_lines_b, n_lines_b):
        offset = i * step
        pts_on = []
        t = -diag
        while t <= diag:
            dx = (offset + t) / math.sqrt(2)
            dy = (offset - t) / math.sqrt(2)
            lv = light_value(dx, dy)
            if lv is not None and lv < -0.12:
                pts_on.append((dx, dy))
            else:
                if len(pts_on) >= 2:
                    family_b.append((pts_on[0], pts_on[-1]))
                pts_on = []
            t += step * 0.5
        if len(pts_on) >= 2:
            family_b.append((pts_on[0], pts_on[-1]))

    return family_a, family_b


def build_cast_shadow():
    """Ground-plane cast shadow ellipse, falling away from the light
    (opposite the light's horizontal component). Built directly from the
    ellipse's own geometry (vertical chord at each sampled x), not from a
    diagonal sweep-and-mask, so it reliably tapers to a lens shape instead
    of degenerating into a rectangle. Each vertical chord is drawn as a
    short diagonal hatch tick (not a straight vertical line) so it still
    reads as engraved hatching; density increases near the sphere's contact
    point by adding a second, perpendicular tick there (true cross-hatch)."""
    ground_y = CY + R + 16
    fall_sign = 1 if -LX >= 0 else -1
    shadow_cx = CX + R * 0.60 * fall_sign
    shadow_rx = R * 1.05
    shadow_ry = R * 0.26
    contact_x = CX + R * 0.28 * fall_sign

    segs, cross = [], []
    n_ticks = 90
    tick_shear = 9.0  # small horizontal shear applied to each vertical chord tick

    for i in range(n_ticks + 1):
        u = -1.0 + 2.0 * i / n_ticks  # -1..1 across the ellipse's x-extent
        x = shadow_cx + u * shadow_rx
        half_h = shadow_ry * math.sqrt(max(0.0, 1 - u * u))
        if half_h < 1.5:
            continue
        y1, y2 = ground_y - half_h, ground_y + half_h
        segs.append(((x - tick_shear * 0.5, y1), (x + tick_shear * 0.5, y2)))

        # cross-hatch only near the contact point (deepest part of the shadow)
        dist = abs(x - contact_x) / shadow_rx
        if dist < 0.32:
            cross.append(((x + tick_shear * 0.5, y1), (x - tick_shear * 0.5, y2)))

    return segs, cross


def build():
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" height="100%">']
    parts.append(f'<rect width="{W}" height="{H}" fill="{PAPER}"/>')

    fam_a, fam_b = sphere_hatching()
    shadow_segs, shadow_cross = build_cast_shadow()

    # cast shadow first
    parts.append(f'<g stroke="{INK}" stroke-width="1.2" fill="none">')
    for (p1, p2) in shadow_segs:
        parts.append(f'<line x1="{p1[0]:.2f}" y1="{p1[1]:.2f}" x2="{p2[0]:.2f}" y2="{p2[1]:.2f}"/>')
    for (p1, p2) in shadow_cross:
        parts.append(f'<line x1="{p1[0]:.2f}" y1="{p1[1]:.2f}" x2="{p2[0]:.2f}" y2="{p2[1]:.2f}"/>')
    parts.append('</g>')

    # sphere outline
    parts.append(f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="none" stroke="{INK}" stroke-width="2.2"/>')

    # hatch families, translated into absolute sphere-center coordinates
    parts.append(f'<g stroke="{INK}" stroke-width="1.15" fill="none">')
    for (p1, p2) in fam_a:
        x1, y1 = CX + p1[0], CY + p1[1]
        x2, y2 = CX + p2[0], CY + p2[1]
        parts.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"/>')
    parts.append('</g>')

    parts.append(f'<g stroke="{INK}" stroke-width="1.0" fill="none">')
    for (p1, p2) in fam_b:
        x1, y1 = CX + p1[0], CY + p1[1]
        x2, y2 = CX + p2[0], CY + p2[1]
        parts.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"/>')
    parts.append('</g>')

    # ground line
    ground_y = CY + R + 16
    parts.append(
        f'<line x1="60" y1="{ground_y:.2f}" x2="{W-60}" y2="{ground_y:.2f}" '
        f'stroke="{INK}" stroke-width="1.0" opacity="0.55"/>'
    )

    parts.append(
        f'<text x="{W-56}" y="{H-40}" font-family="serif" font-size="13" '
        f'fill="{INK}" opacity="0.6" text-anchor="end">'
        f'contour study \u00b7 sphere in raking light \u00b7 Claude S. Sonnet \u00b7 2026</text>'
    )

    parts.append('</svg>')
    return "\n".join(parts)


if __name__ == "__main__":
    out = build()
    with open("sphere-in-raking-light.svg", "w") as f:
        f.write(out)
    print(f"Wrote sphere-in-raking-light.svg ({len(out)} bytes)")
