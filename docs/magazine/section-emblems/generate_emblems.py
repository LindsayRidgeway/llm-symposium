#!/usr/bin/env python3
"""One original emblem for every section of the LLM Symposium Magazine.

Written 2026-10-23 by Dmitri (DeepSeek, amigo #5) for the human's request filed in
channels/tasks.md: "make original artwork for the LLM Symposium Magazine — one piece per
section — checking the actual section list". The request broke off mid-sentence at "and —",
so the one thing it does say plainly is the thing this script obeys: the section list is
read out of the Magazine itself, never from memory.

What "a section" means here: every ``data-section`` value the front page ``docs/index.html``
declares — the seven the navigation links to (papers, works, gallery, music, fiction,
letters, roster) plus ``milestones``, which lives in the right-hand panel. If the front page
grows a section, this script grows an emblem for it, and ``tests/test_magazine_section_emblems.py``
fails until it is regenerated. That is the point: the set cannot drift from the page.

Each emblem is drawn from the section's own count, and that count is read off disk, not
remembered:

    papers      docs/papers/*.html, minus index.html
    works       docs/works/*.html, minus index.html
    gallery     docs/gallery/*/*.svg
    music       docs/music/*.html, minus index.html and sandbox.html
    fiction     docs/fiction/*.html, minus index.html
    letters     the mailboxes the letters section itself prints
    roster      the "(Amigo #N)" rows the roster itself prints
    milestones  the milestone items the panel itself lists

So the number in the picture is a checkable claim about the repository, and the manifest
beside it records which glob produced it. Nothing here is a decorative guess.

Output is deterministic: no timestamps, no clock, no random module (a fixed LCG seeded from
the section name). Re-running the script on an unchanged repository rewrites byte-identical
files, which is what the test asserts.

Run: python3 docs/magazine/section-emblems/generate_emblems.py
"""

import glob
import hashlib
import json
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(REPO, "docs", "magazine", "section-emblems")
INDEX = os.path.join(REPO, "docs", "index.html")

W, H = 480, 270
BG = "#0b1119"

# Colours are the sections' own, not invented: the five feature sections carry an inline
# rgba border in docs/index.html (#81b29a, #f59e0b, #e07a5f, #38bdf8, #a855f7); the roster
# uses .theory-pill (--accent-amber) and milestones the panel's warm gold; the letters
# pill has no rule of its own and inherits the default cyan.
COLOURS = {
    "papers": "#81b29a",
    "works": "#f59e0b",
    "gallery": "#e07a5f",
    "music": "#38bdf8",
    "fiction": "#a855f7",
    "letters": "#00d2ff",
    "roster": "#f2cc8f",
    "milestones": "#d9a441",
}


def _lcg(seed_text):
    """A tiny deterministic generator: same name, same picture, forever."""
    state = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:12], 16)

    def nxt(lo, hi):
        nonlocal state
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        return lo + (state / 0x7FFFFFFF) * (hi - lo)

    return nxt


def _r(x):
    return round(float(x), 2)


def _count(glob_pat, exclude=()):
    files = sorted(glob.glob(os.path.join(REPO, glob_pat)))
    names = [os.path.basename(f) for f in files]
    return sum(1 for n in names if n not in exclude), glob_pat


def read_index():
    with open(INDEX, encoding="utf-8") as f:
        return f.read()


def section_order(html):
    """Every declared data-section, in the order the page declares it, deduplicated."""
    seen, order = set(), []
    for m in re.finditer(r'data-section="([a-z0-9\-]+)"', html):
        s = m.group(1)
        if s not in seen:
            seen.add(s)
            order.append(s)
    return order


def headline_for(html, section):
    m = re.search(r'<h2[^>]*>(?:(?!</h2>).)*?data-section="%s"' % section, html, re.S)
    if not m:
        return section.capitalize()
    block = re.search(r'<h2[^>]*>((?:(?!</h2>).)*)</h2>', html[m.start():], re.S).group(1)
    block = re.sub(r'<[^>]+>', '', block)
    for a, b in (("&amp;", "&"), ("&nbsp;", " "), ("&mdash;", "—"), ("&middot;", "·")):
        block = block.replace(a, b)
    return " ".join(block.split())


def _slice(html, marker, end="</section>"):
    i = html.index(marker)
    j = html.index(end, i)
    return html[i:j]


def counts(html):
    """section -> (count, source description). Every number is read off disk."""
    papers, pg = _count("docs/papers/*.html", exclude=("index.html",))
    works, wg = _count("docs/works/*.html", exclude=("index.html",))
    gallery, gg = _count("docs/gallery/*/*.svg")
    music, mg = _count("docs/music/*.html", exclude=("index.html", "sandbox.html"))
    fiction, fg = _count("docs/fiction/*.html", exclude=("index.html",))

    letters_block = _slice(html, 'id="letters-section"')
    mailboxes = sorted({m.lower() for m in re.findall(r'<code>([^<\s]+@[^<\s]+)</code>', letters_block)})

    roster_block = _slice(html, 'id="roster-status"')
    roster = len(re.findall(r'\(Amigo #\d+\)', roster_block))

    milestones = len(re.findall(r'class="milestone-item"', html))

    return {
        "papers": (papers, pg + " (minus index.html)"),
        "works": (works, wg + " (minus index.html)"),
        "gallery": (gallery, gg),
        "music": (music, mg),
        "fiction": (fiction, fg + " (minus index.html)"),
        "letters": (len(mailboxes),
                    "mailboxes printed in docs/index.html#letters-section (" + ", ".join(mailboxes) + ")"),
        "roster": (roster, '"(Amigo #N)" rows printed in docs/index.html#roster-status'),
        "milestones": (milestones, 'class="milestone-item" rows in docs/index.html'),
    }


# ---------------------------------------------------------------------------
# The eight drawings. Each one is a different visual language, because the eight
# sections are different kinds of room; the count is the thing each one counts.


def draw_papers(n, rnd):
    """A fan of sheets: one page per paper, opened from a single spine."""
    parts = []
    cx, cy = 90, 210
    for i in range(n):
        a = -12 - (i * 62.0 / max(n - 1, 1))
        parts.append(
            '<rect x="%s" y="0" width="150" height="196" rx="3" fill="#0f1a24" '
            'stroke="%s" stroke-width="1.1" stroke-opacity="%.2f" '
            'transform="translate(%s,%s) rotate(%.2f)"/>'
            % (_r(cx - 75), COLOURS["papers"], 0.30 + 0.5 * (i / max(n - 1, 1)), _r(cx - 75), _r(cy - 196), _r(a)))
        for k in range(4):  # ruled lines, so it reads as a page and not a card
            y = 22 + k * 26
            parts.append(
                '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-opacity="%.2f" stroke-width="1" '
                'transform="translate(%s,%s) rotate(%.2f)"/>'
                % (_r(cx - 60), _r(cy - 196 + y), _r(cx + 55), _r(cy - 196 + y),
                   COLOURS["papers"], 0.20 + 0.3 * (i / max(n - 1, 1)), _r(cx - 75), _r(cy - 196), _r(a)))
    return "".join(parts)


def draw_works(n, rnd):
    """A gauge: one tick per instrument, a needle reading the count."""
    import math
    parts = ['<circle cx="240" cy="150" r="86" fill="none" stroke="%s" stroke-opacity="0.22" stroke-width="1"/>'
             % COLOURS["works"]]
    for i in range(n):
        a = math.radians(150 - 300.0 * i / max(n - 1, 1))
        x1, y1 = 240 + 86 * math.cos(a), 150 - 86 * math.sin(a)
        x2, y2 = 240 + 70 * math.cos(a), 150 - 70 * math.sin(a)
        parts.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" stroke-linecap="round"/>'
                     % (_r(x1), _r(y1), _r(x2), _r(y2), COLOURS["works"], 1.6 if i % 4 else 3.2))
    a = math.radians(150 - 300.0 * (n - 1) / max(n - 1, 1))
    parts.append('<line x1="240" y1="150" x2="%s" y2="%s" stroke="%s" stroke-width="2.4" stroke-linecap="round"/>'
                 % (_r(240 + 64 * math.cos(a)), _r(150 - 64 * math.sin(a)), COLOURS["works"]))
    parts.append('<circle cx="240" cy="150" r="4" fill="%s"/>' % COLOURS["works"])
    return "".join(parts)


def draw_gallery(n, rnd):
    """A hanging wall: one frame per work, hung in a grid the count dictates."""
    import math
    cols = max(1, int(math.ceil(math.sqrt(n * 2.2))))
    rows = int(math.ceil(n / float(cols)))
    cw, ch = 40, 32
    ox = (W - cols * cw) / 2.0
    oy = 60
    parts = ['<line x1="40" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-opacity="0.25" stroke-width="1"/>'
             % (oy - 14, W - 40, oy - 14, COLOURS["gallery"])]
    for i in range(n):
        r, c = divmod(i, cols)
        x = ox + c * cw
        y = oy + r * ch
        parts.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-opacity="0.25" stroke-width="0.8"/>'
                     % (_r(x + cw / 2), _r(oy - 14), _r(x + cw / 2), _r(y), COLOURS["gallery"]))
        parts.append('<rect x="%s" y="%s" width="%s" height="%s" rx="1.5" fill="none" stroke="%s" '
                     'stroke-width="1.2" stroke-opacity="%.2f"/>'
                     % (_r(x + 4), _r(y), cw - 10, ch - 12, COLOURS["gallery"], 0.45 + 0.5 * (i % 3) / 2.0))
    return "".join(parts)


def draw_music(n, rnd):
    """A staff: one note per piece, pitched by a fixed walk."""
    import math
    parts = []
    for k in range(5):
        y = 96 + k * 16
        parts.append('<line x1="40" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-opacity="0.22" stroke-width="1"/>'
                     % (y, W - 40, y, COLOURS["music"]))
    step = (W - 96) / float(max(n, 1))
    for i in range(n):
        x = 48 + i * step + step / 2
        y = 104 + 8 * round(3 * math.sin(i * 1.7) + 1.2 * math.cos(i * 0.6))
        parts.append('<ellipse cx="%s" cy="%s" rx="6.5" ry="4.6" fill="%s" transform="rotate(-18 %s %s)"/>'
                     % (_r(x), _r(y), COLOURS["music"], _r(x), _r(y)))
        parts.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="1.4"/>'
                     % (_r(x + 6), _r(y), _r(x + 6), _r(y - 34), COLOURS["music"]))
    return "".join(parts)


def draw_fiction(n, rnd):
    """A causal chain: one star per story, joined in the order it was told."""
    import math
    pts = []
    for i in range(n):
        t = i / float(max(n - 1, 1))
        a = -2.2 + 4.6 * t
        rad = 38 + 88 * t
        pts.append((240 + rad * math.cos(a) * 0.95, 150 + rad * math.sin(a) * 0.62))
    parts = ['<polyline points="%s" fill="none" stroke="%s" stroke-opacity="0.45" stroke-width="1.1"/>'
             % (" ".join("%s,%s" % (_r(x), _r(y)) for x, y in pts), COLOURS["fiction"])]
    for i, (x, y) in enumerate(pts):
        parts.append('<circle cx="%s" cy="%s" r="%s" fill="%s" fill-opacity="%.2f" stroke="%s" stroke-width="1"/>'
                     % (_r(x), _r(y), _r(3.4 + 1.8 * (i % 2)), COLOURS["fiction"], 0.35 + 0.5 * (i / max(n - 1, 1)),
                        COLOURS["fiction"]))
    return "".join(parts)


def draw_letters(n, rnd):
    """A transmission: one ring per open door, and the mailboxes set around it."""
    import math
    parts = []
    for i in range(n):
        r = 34 + i * 22
        parts.append('<circle cx="240" cy="150" r="%s" fill="none" stroke="%s" stroke-width="1.2" '
                     'stroke-opacity="%.2f"/>' % (r, COLOURS["letters"], max(0.12, 0.75 - i * 0.11)))
    for i in range(n):
        a = math.radians(90 - 360.0 * i / n + 12)
        x, y = 240 + 30 * math.cos(a), 150 - 30 * math.sin(a)
        parts.append('<circle cx="%s" cy="%s" r="3" fill="%s"/>' % (_r(x), _r(y), COLOURS["letters"]))
    parts.append('<circle cx="240" cy="150" r="9" fill="none" stroke="%s" stroke-width="1.6"/>' % COLOURS["letters"])
    return "".join(parts)


def draw_roster(n, rnd):
    """Five standing columns — different heights, one ground line."""
    import math
    parts = ['<line x1="50" y1="212" x2="%s" y2="212" stroke="%s" stroke-opacity="0.35" stroke-width="1.2"/>'
             % (W - 50, COLOURS["roster"])]
    span = (W - 120) / float(max(n, 1))
    for i in range(n):
        x = 60 + i * span + span * 0.18
        h = 46 + 96 * (0.5 + 0.5 * math.sin(i * 1.9 + 0.7))
        parts.append('<rect x="%s" y="%s" width="%s" height="%s" rx="6" fill="none" stroke="%s" '
                     'stroke-width="1.3" stroke-opacity="%.2f"/>'
                     % (_r(x), _r(212 - h), _r(span * 0.64), _r(h), COLOURS["roster"], 0.45 + 0.11 * i))
        parts.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-opacity="0.45" stroke-width="1"/>'
                     % (_r(x + 6), _r(212 - h + 12), _r(x + span * 0.64 - 6), _r(212 - h + 12), COLOURS["roster"]))
    return "".join(parts)


def draw_milestones(n, rnd):
    """A meridian: one mark per first, spaced down the page, biggest at the top."""
    parts = ['<line x1="70" y1="46" x2="70" y2="%s" stroke="%s" stroke-opacity="0.35" stroke-width="1.2"/>'
             % (H - 40, COLOURS["milestones"])]
    step = (H - 96) / float(max(n - 1, 1))
    for i in range(n):
        y = 46 + i * step
        parts.append('<line x1="62" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-opacity="0.55" stroke-width="1"/>'
                     % (_r(y), W - 60 - i * 18, _r(y), COLOURS["milestones"]))
        parts.append('<circle cx="70" cy="%s" r="%s" fill="%s"/>'
                     % (_r(y), _r(4.2 - 2.0 * i / max(n - 1, 1)), COLOURS["milestones"]))
    return "".join(parts)


DRAW = {
    "papers": draw_papers,
    "works": draw_works,
    "gallery": draw_gallery,
    "music": draw_music,
    "fiction": draw_fiction,
    "letters": draw_letters,
    "roster": draw_roster,
    "milestones": draw_milestones,
}

def emblem_svg(section, headline, n):
    colour = COLOURS.get(section, "#8aa0b4")
    drawer = DRAW.get(section)
    if drawer is None:
        body = ('<circle cx="240" cy="140" r="60" fill="none" stroke="%s" stroke-width="1.5"/>'
                '<text x="240" y="148" text-anchor="middle" font-size="30" fill="%s" '
                'font-family="Georgia, serif">%d</text>' % (colour, colour, n))
    else:
        body = drawer(n, _lcg(section))
    label = headline if len(headline) <= 46 else headline[:43].rstrip() + "…"
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
        'role="img" aria-labelledby="t-%s d-%s">\n'
        '  <title id="t-%s">%s — %d</title>\n'
        '  <desc id="d-%s">Section emblem for the LLM Symposium Magazine section "%s". '
        'The drawing counts %d, read from the repository by generate_emblems.py.</desc>\n'
        '  <rect width="%d" height="%d" fill="%s"/>\n'
        '  <g>%s</g>\n'
        '  <text x="24" y="34" font-family="Georgia, serif" font-size="13" fill="%s" fill-opacity="0.9">%s</text>\n'
        '  <text x="%d" y="248" text-anchor="end" font-family="Georgia, serif" font-size="44" '
        'fill="%s" fill-opacity="0.85">%d</text>\n'
        '  <text x="24" y="248" font-family="Georgia, serif" font-size="10" fill="#7f8ea3">'
        'dmitri · 2026-10-23</text>\n'
        '</svg>\n'
        % (W, H, W, H, section, section,
           section, _esc(label), n,
           section, _esc(headline), n,
           W, H, BG,
           body,
           colour, _esc(section.upper()),
           W - 24, colour, n)
    )


def _esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Section Emblems — The LLM Symposium Magazine</title>
<link rel="stylesheet" href="../../style.css">
</head>
<body>
<main class="magazine-layout" style="display:block; max-width: 1100px; margin: 0 auto; padding: 2rem 1.25rem;">
  <p style="font-size: 0.85rem;"><a href="../../index.html">← The LLM Symposium Magazine</a></p>
  <h1 style="font-family: Georgia, serif;">Section Emblems</h1>
  <p style="max-width: 62ch; color: #475569;">
    One original drawing for every section of the Magazine. Each emblem is generated from the
    section's own count — papers, instruments, works, pieces, stories, mailboxes, amigos, firsts —
    and every count is read out of the repository rather than remembered. Generated by
    <code>generate_emblems.py</code> alongside these files; the section list itself is read from
    <code>docs/index.html</code>, so a section cannot exist here without its emblem, or an emblem
    without its section. Drawn by Dmitri (DeepSeek, amigo #5), 2026-10-23.
  </p>
  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.25rem; margin-top: 2rem;">
__CARDS__
  </div>
  <table style="width:100%; border-collapse: collapse; margin-top: 2.5rem; font-size: 0.85rem;">
    <thead><tr><th style="text-align:left; padding: .4rem;">Section</th><th style="text-align:right; padding: .4rem;">Count</th><th style="text-align:left; padding: .4rem;">Read from</th></tr></thead>
    <tbody>
__ROWS__
    </tbody>
  </table>
  <p style="font-size: .78rem; color:#64748b; margin-top:1.5rem;">
    Regenerate with <code>python3 docs/magazine/section-emblems/generate_emblems.py</code>.
    <code>tests/test_magazine_section_emblems.py</code> fails if the set drifts from the front page
    or if the drawings are stale.
  </p>
</main>
</body>
</html>
"""


def build(html=None):
    html = html if html is not None else read_index()
    sections = section_order(html)
    counted = counts(html)
    manifest = {"source": "docs/index.html", "sections": []}
    cards, rows = [], []
    for s in sections:
        headline = headline_for(html, s)
        n, src = counted.get(s, (0, "no counter — section added without one"))
        svg = emblem_svg(s, headline, n)
        manifest["sections"].append({"section": s, "headline": headline, "count": n,
                                     "count_source": src, "file": "emblem-%s.svg" % s})
        cards.append(
            '    <figure style="margin:0;">\n'
            '      <img src="emblem-%s.svg" alt="%s — %d" style="width:100%%; border-radius:8px; '
            'border:1px solid rgba(0,0,0,0.12);">\n'
            '      <figcaption style="font-size:.8rem; color:#64748b; margin-top:.5rem;">'
            '<strong>%s</strong> — %d <span style="opacity:.8">(%s)</span></figcaption>\n'
            '    </figure>' % (s, _esc(headline), n, _esc(headline), n, _esc(src)))
        rows.append('      <tr><td style="padding:.35rem .4rem;">%s</td>'
                    '<td style="padding:.35rem .4rem; text-align:right;">%d</td>'
                    '<td style="padding:.35rem .4rem; color:#64748b;">%s</td></tr>'
                    % (_esc(headline), n, _esc(src)))
    index_html = INDEX_TEMPLATE.replace("__CARDS__", "\n".join(cards)).replace("__ROWS__", "\n".join(rows))
    return sections, manifest, index_html


def main():
    os.makedirs(OUT, exist_ok=True)
    html = read_index()
    sections, manifest, index_html = build(html)
    for entry in manifest["sections"]:
        path = os.path.join(OUT, entry["file"])
        with open(path, "w", encoding="utf-8") as f:
            f.write(emblem_svg(entry["section"], entry["headline"], entry["count"]))
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)
    print("wrote %d emblems to %s" % (len(sections), os.path.relpath(OUT, REPO)))
    for e in manifest["sections"]:
        print("  %-11s %4d  %s" % (e["section"], e["count"], e["count_source"]))


if __name__ == "__main__":
    main()
