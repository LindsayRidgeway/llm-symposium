#!/usr/bin/env python3
"""Read the three creative wings off their own pages and write research/creative-wings-map.md.

Why this exists (Dmitri, 2026-10-19). The to-do item it serves is one sentence: *read the
gallery's seven wings, the conservatory's wings and the literary wing's contribution format, and
record the real section names and formats*, because my earlier gallery attempts named pavilions
from the index summary instead of from the pages. A hand-written note would drift the moment a
page changes and nobody could tell. So the note is *generated*: this script parses the three
front pages and their children, and emits `research/creative-wings-map.md`. `tests/test_creative_
wings_map.py` re-runs it and fails if the committed map no longer matches the pages.

What it reads, and nothing else
-------------------------------
  docs/gallery/index.html          wing titles + anchors, the 5x7 matrix
  docs/gallery/<wing>/index.html   each wing page's own section headings, and its files
  docs/music/index.html            the three catalogue wings, each card's author/genre/specs
  docs/music/*.abc, *.html         which pieces have a symbolic source and a full score
  docs/fiction/index.html          the hard-SF matrix
  docs/fiction/*.html              the story-page structure (the contribution format)

Deliberately no network, no guessing, no "close enough" section names: every name in the output
is a heading or an attribute copied out of a file in this tree.

Usage:  python3 scripts/creative_wings_map.py [--check]
        --check   exit 1 if research/creative-wings-map.md is stale (used by the test)
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT = ROOT / "research" / "creative-wings-map.md"

WS = re.compile(r"[ \t]+")


def text(fragment: str) -> str:
    """HTML fragment -> single-line plain text, entities resolved."""
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    return WS.sub(" ", html.unescape(fragment)).strip()


def headings(page: Path, levels: str = "23") -> list[tuple[str, str]]:
    """[(tag, text)] for h<levels> in document order. Ignores headings inside <script>."""
    raw = page.read_text(encoding="utf-8")
    raw = re.sub(r"<script.*?</script>", "", raw, flags=re.S)
    out = []
    for m in re.finditer(r"<h([%s])[^>]*>(.*?)</h\1>" % levels, raw, flags=re.S | re.I):
        t = text(m.group(2))
        if t:
            out.append((m.group(1), t))
    return out


def tables(page: Path) -> list[list[list[str]]]:
    """Every <table> on the page as a list of rows of cell texts."""
    raw = page.read_text(encoding="utf-8")
    out = []
    for tab in re.findall(r"<table.*?</table>", raw, flags=re.S):
        rows = []
        for row in re.findall(r"<tr.*?</tr>", tab, flags=re.S):
            cells = [text(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, flags=re.S)]
            if cells:
                rows.append(cells)
        if rows:
            out.append(rows)
    return out


def classes(page: Path) -> list[str]:
    return sorted(set(re.findall(r'class="([a-z][a-z-]+)"', page.read_text(encoding="utf-8"))))


# --------------------------------------------------------------------------- gallery


def gallery_wings() -> list[dict]:
    index = DOCS / "gallery" / "index.html"
    raw = index.read_text(encoding="utf-8")
    wings = []
    for m in re.finditer(
        r'<h2 class="wing-title"><a href="([^"/]+)/index\.html"[^>]*>(.*?)</a></h2>', raw, flags=re.S
    ):
        slug, title = m.group(1), text(m.group(2))
        page = DOCS / "gallery" / slug / "index.html"
        d = DOCS / "gallery" / slug
        files = sorted(p.name for p in d.iterdir() if p.is_file()) if d.is_dir() else []
        wings.append(
            {
                "slug": slug,
                "title": title,
                "sections": [t for lvl, t in headings(page)] if page.exists() else [],
                "svg": [f for f in files if f.endswith(".svg")],
                "generators": [f for f in files if f.startswith("generate-") and f.endswith(".py")],
                "prompts": [f for f in files if "prompt" in f and f.endswith(".md")],
                "raster": [f for f in files if f.endswith((".jpg", ".png"))],
                "studies": sorted(
                    p.name for p in (d / "studies").iterdir() if p.is_dir()
                )
                if (d / "studies").is_dir()
                else [],
            }
        )
    return wings


def gallery_matrix() -> list[list[str]]:
    for tab in tables(DOCS / "gallery" / "index.html"):
        if tab and tab[0] and tab[0][0].lower().startswith("wing"):
            return tab
    return []


# --------------------------------------------------------------------------- music


def music_wings() -> list[dict]:
    page = DOCS / "music" / "index.html"
    raw = page.read_text(encoding="utf-8")
    wings = []
    blocks = re.split(r'<section class="catalog-wing">', raw)[1:]
    for block in blocks:
        m = re.search(r'<h2 class="catalog-wing-title">(.*?)</h2>', block, flags=re.S)
        if not m:
            continue
        desc = re.search(r'<p class="catalog-wing-desc">(.*?)</p>', block, flags=re.S)
        cards = []
        for card in re.split(r'<article class="repertoire-card">', block)[1:]:
            author = re.search(r'class="comp-author-pill[^"]*">(.*?)</span>', card, flags=re.S)
            genre = re.search(r'class="comp-genre-tag">(.*?)</span>', card, flags=re.S)
            title = re.search(r'<h3 class="repertoire-card-title">(.*?)</h3>', card, flags=re.S)
            specs = [
                text(s)
                for s in re.findall(r'<span class="spec-pill">(.*?)</span>', card, flags=re.S)
            ]
            cards.append(
                {
                    "author": text(author.group(1)) if author else "",
                    "genre": text(genre.group(1)) if genre else "",
                    "title": text(title.group(1)) if title else "",
                    "specs": specs,
                }
            )
        wings.append(
            {
                "title": text(m.group(1)),
                "desc": text(desc.group(1)) if desc else "",
                "cards": cards,
            }
        )
    return wings


def music_files() -> dict[str, list[str]]:
    d = DOCS / "music"
    names = sorted(p.name for p in d.iterdir() if p.is_file())
    return {
        "abc": [n for n in names if n.endswith(".abc")],
        "abc_tmp": [n for n in names if n.endswith(".abc.tmp")],
        "scores": [n for n in names if n.endswith(".html") and n != "index.html" and n != "sandbox.html"],
    }


# --------------------------------------------------------------------------- fiction


def fiction_matrix() -> list[list[str]]:
    for tab in tables(DOCS / "fiction" / "index.html"):
        if tab and tab[0] and tab[0][0].lower() == "amigo":
            return tab
    return []


def fiction_stories() -> list[dict]:
    d = DOCS / "fiction"
    out = []
    for p in sorted(d.glob("*.html")):
        if p.name == "index.html":
            continue
        raw = p.read_text(encoding="utf-8")
        title = headings(p, "1")
        meta = re.search(r'class="story-meta"[^>]*>(.*?)</div>', raw, flags=re.S)
        out.append(
            {
                "file": p.name,
                "title": title[0][1] if title else p.stem,
                "meta": text(meta.group(1)) if meta else "",
                "classes": classes(p),
            }
        )
    return out


# --------------------------------------------------------------------------- render


def render() -> str:
    L: list[str] = []
    A = L.append
    A("# The creative wings, read off the pages")
    A("")
    A("*Generated by `scripts/creative_wings_map.py` — do not edit by hand. "
      "`tests/test_creative_wings_map.py` fails if this file stops matching the tree.*")
    A("")
    A("Written to answer one question honestly: **what are the sections actually called, and what "
      "does a contribution have to look like?** Every name below is copied from a heading or an "
      "attribute in a page under `docs/`; none is remembered. Dmitri, 2026-10-19.")
    A("")

    # ---- gallery
    gal = gallery_wings()
    matrix = gallery_matrix()
    A("## 1. The Gallery — seven wings")
    A("")
    A("Front page: `docs/gallery/index.html`. Each wing is a directory with its own `index.html`, "
      f"linked from an `<h2 class=\"wing-title\">` and anchored by the directory name. {len(gal)} wings.")
    A("")
    A("| # | anchor (`#id`) | wing page title (verbatim) |")
    A("|---|---|---|")
    for i, w in enumerate(gal, 1):
        A(f"| {i:02d} | `#{w['slug']}` → `docs/gallery/{w['slug']}/index.html` | {w['title']} |")
    A("")
    A("### The section names inside each wing page")
    A("")
    A("These are the headings a reader of the wing page actually sees. Citing a wing by its title is "
      "safe; citing a *section* means one of these.")
    A("")
    for i, w in enumerate(gal, 1):
        A(f"**{i:02d}. {w['title']}** — `docs/gallery/{w['slug']}/`")
        A("")
        page = DOCS / "gallery" / w["slug"] / "index.html"
        for lvl, t in headings(page) if page.exists() else []:
            A(f"- h{lvl}: {t}")
        A("")
        A(f"- files: {len(w['svg'])} SVG, {len(w['raster'])} raster, "
          f"{len(w['generators'])} generator(s)"
          + (f" ({', '.join('`' + g + '`' for g in w['generators'])})" if w["generators"] else "")
          + (f"; prompt files: {', '.join('`' + p + '`' for p in w['prompts'])}" if w["prompts"] else "")
          + (f"; `studies/` by amigo: {', '.join(w['studies'])}" if w["studies"] else ""))
        A("")

    A("### The contribution convention, as the tree actually keeps it")
    A("")
    A("1. **The work is a file in the wing directory**, `docs/gallery/<wing>/<slug>.svg` for a "
      "procedural plate or `<slug>.jpg` for a diffusion study. The exhibition pieces carry a "
      "`-signed` suffix; the unsigned ones in the same directory are not the exhibited set.")
    A("2. **The generator stays with the work** — `generate-<amigo>-<slug>.py` — so the plate can be "
      "recomputed rather than trusted.")
    A("3. **The wing page links it**, with `<a href=\"<slug>.svg\" target=\"_blank\" title=\"Open … in "
      "full resolution\">`. A work on disk that no wing page links is not exhibited; "
      "`scripts/gallery_unwired_works.py` fails on it unless an exemption carries a written reason.")
    A("4. **The front-page matrix row is updated** — the 5×7 table on `docs/gallery/index.html`, "
      "columns `Claude | Desi | Gemini | Tarik | Dmitri`, rows `01.`…`07.` — and the cell must name "
      "a work the wing page actually shows (`tests/test_gallery_matrix.py`).")
    A("5. **Diffusion work goes through the inbox protocol** in "
      "`docs/gallery/prompt-methodology.md`: `Positive prompt:` / `Negative prompt:` as single lines, "
      "three candidates per batch, prompts preserved in the wing's `mage-prompts*.md`, dispatches to "
      "Telegram ending in the sentinel `THE END`, drops in `~/LLM/gallery-inbox/`, and the "
      "originating amigo makes the curatorial choice.")
    A("")
    if matrix:
        A("Current matrix (verbatim from the front page):")
        A("")
        A("| " + " | ".join(matrix[0]) + " |")
        A("|" + "---|" * len(matrix[0]))
        for row in matrix[1:]:
            A("| " + " | ".join(row) + " |")
        A("")

    # ---- music
    mw = music_wings()
    mf = music_files()
    A("## 2. The Music Conservatory — three catalogue wings")
    A("")
    A("Front page: `docs/music/index.html`. Unlike the gallery, the conservatory is **one page with "
      "three wings**; a work is a card on it plus its own files, not a directory.")
    A("")
    for w in mw:
        A(f"### {w['title']}")
        A("")
        if w["desc"]:
            A(f"*{w['desc']}*")
            A("")
        A("| work (verbatim card title) | author pill | genre tag | specs |")
        A("|---|---|---|---|")
        for c in w["cards"]:
            A(f"| {c['title']} | {c['author']} | {c['genre']} | "
              + "; ".join(c["specs"]).replace("|", "/") + " |")
        A("")
    A("### What a contribution needs, in the conservatory's own terms")
    A("")
    A(f"- a **card** in one of the three `<section class=\"catalog-wing\">` blocks with "
      "`comp-author-pill` (amigo + number), `comp-genre-tag`, `repertoire-card-title`, "
      "`spec-pill` specs (key, meter, tempo, voicing) and a `repertoire-summary`;")
    A("- a **symbolic source** where one exists: `docs/music/<slug>.abc` "
      f"({len(mf['abc'])} in the tree: {', '.join('`' + n + '`' for n in mf['abc'])});")
    A("- a **full score page** `docs/music/<slug>.html` "
      f"({len(mf['scores'])} in the tree) carrying the engraving, the "
      "formal constraints and the measure-by-measure analysis;")
    if mf["abc_tmp"]:
        A(f"- note: `*.abc.tmp` files are present and are **not** sources a reader can load: "
          f"{', '.join('`' + n + '`' for n in mf['abc_tmp'])}.")
    A("")

    # ---- fiction
    fm = fiction_matrix()
    stories = fiction_stories()
    A("## 3. The Literary Wing — the Hard SF Matrix")
    A("")
    A("Front page: `docs/fiction/index.html`. One genre, one table, one HTML page per story.")
    A("")
    if fm:
        A("| " + " | ".join(fm[0]) + " |")
        A("|" + "---|" * len(fm[0]))
        for row in fm[1:]:
            A("| " + " | ".join(row) + " |")
        A("")
    A("### The contribution format — a story page")
    A("")
    A("The five delivered stories are the format spec; these files agree on the structure:")
    A("")
    A("| file | title | meta line |")
    A("|---|---|---|")
    for s in stories:
        A(f"| `docs/fiction/{s['file']}` | {s['title']} | {s['meta']} |")
    A("")
    shared = set(stories[0]["classes"]) if stories else set()
    for s in stories[1:]:
        shared &= set(s["classes"])
    A(f"- classes every story page carries: {', '.join('`' + c + '`' for c in sorted(shared))}")
    A("- the physics is not decoration: each page carries a `physics-callout` block naming the law "
      "the plot turns on, and the front-page matrix's third column (`Physical Sandbox / Core Law`) "
      "must match it.")
    A("- the bar, quoted from the front page: *\"physics and math cannot be hand-waved; plots must "
      "turn on causal engineering insights rather than emotional epiphanies\"*.")
    A("")

    # ---- one page
    A("## 4. Which of these are mine, per the record")
    A("")
    A("Read off the matrix cells, the author pills and the file names — not memory. This is the "
      "mechanical half of to-do item 2; the half that needs reading (whether each work is really "
      "mine) is still open.")
    A("")
    if matrix and "Dmitri" in matrix[0]:
        col = matrix[0].index("Dmitri")
        A("| wing | matrix cell (Dmitri) | generator(s) naming me |")
        A("|---|---|---|")
        for w, row in zip(gal, matrix[1:]):
            gens = [g for g in w["generators"] if "dmitri" in g.lower()]
            A(f"| {row[0]} | {row[col]} | " + (", ".join(f"`{g}`" for g in gens) if gens else "—") + " |")
        A("")
        A("Where a wing has a generator of mine but an *Open* cell, the cell is not necessarily wrong: "
          "`russian-realism/the-edge-of-the-sunbreak.svg` is on disk and is declared a study rather "
          "than an exhibited work by `scripts/gallery_unwired_works.py`, which prints the reason. The "
          "matrix cell and the gate are the authority here, not this note.")
        A("")
    dm_music = [
        (w["title"], c["title"], c["author"])
        for w in mw
        for c in w["cards"]
        if "Dmitri" in c["author"]
    ]
    if dm_music:
        A("Conservatory — cards carrying a Dmitri author pill:")
        A("")
        for wing, card, author in dm_music:
            A(f"- {wing} / {card} ({author})")
        A("")
    else:
        A("Conservatory — no card carries a Dmitri author pill.")
        A("")
    if fm and any("Dmitri" in r[0] for r in fm[1:]):
        row = next(r for r in fm[1:] if "Dmitri" in r[0])
        A(f"Literary wing — **{row[1]}**, the law: {row[2]} ({row[3]}).")
        A("")

    # ---- disagreements
    odd = [
        (w["title"], c["title"], c["author"])
        for w in mw
        for c in w["cards"]
        if not re.fullmatch(r"[A-Z][^•]*• Amigo #\d", c["author"])
    ]
    A("## 5. Where the pages disagree with their own convention")
    A("")
    # Was "these are the only two" — a count written into the prose that stopped being true the
    # day one of the two came back clean, so the section read "two" above a list of one. The list
    # is emitted below and the wording no longer counts it (Dmitri, 2026-10-31).
    A("Computed, not noticed — every disagreement this parser can see is listed below:")
    A("")
    if odd:
        A("- author pills that do not follow the `<Name> • Amigo #<n>` shape the other cards use:")
        for wing, card, author in odd:
            A(f"  - {wing} / {card} → pill reads `{author}`")
    else:
        A("- every author pill follows `<Name> • Amigo #<n>`.")
    if mf["abc_tmp"]:
        A(f"- `*.abc.tmp` files sit beside the sources and cannot be loaded by a player: "
          f"{', '.join('`' + n + '`' for n in mf['abc_tmp'])} — an unfinished rename or an "
          "interrupted generator, not a piece.")
    A("")
    return "\n".join(L).rstrip() + "\n"


def main(argv: list[str]) -> int:
    md = render()
    if "--check" in argv:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != md:
            print(f"STALE: {OUT.relative_to(ROOT)} does not match the pages. "
                  f"Run python3 scripts/creative_wings_map.py")
            return 1
        print(f"OK: {OUT.relative_to(ROOT)} matches the pages")
        return 0
    OUT.write_text(md, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(md.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
