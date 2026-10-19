#!/usr/bin/env python3
"""Catalogued is not the same as landed, and landed is not the same as reachable (Dmitri, 2026-10-19).

Why this exists
---------------
The gallery got a gate for this on 2026-10-18 (`scripts/gallery_unwired_works.py`) after five of
Dmitri's pavilion works landed on disk and were never exhibited. The music conservatory did not,
and the same class of defect was repaired there **by hand twice**:

    2026-10-19  the-level-ground.html   landed, absent from docs/music/index.html   → wired by run
                                                                                     20261019T011755Z
    2026-10-19  the-cairn.html          landed, absent from docs/music/index.html   → wired by this run

Both were finished pieces with a full score page *and* a playable entry in `app.js`: the audition
engine already knew the tune, the catalogue page did not. A reader who came in through
`docs/music/index.html` — which is the only way in from the site — could not reach either one.
The landing gate checked that the file existed and that the tests passed; nothing checked that the
catalogue linked it. That is why this is a script and not a third manual repair.

What it checks
--------------
1. **Reachability.** Every top-level ``*.html`` in ``docs/music/`` is either catalogued (its filename
   appears in ``index.html``) or listed in ``NOT_PIECES`` below with the reason it is not a catalogue
   entry. The default is failure; an exemption is an argument, not a silence.

2. **The audition button points at a tune that exists.** Every ``data-tune="…"`` on a catalogue card
   must be a key of ``COMPOSITIONS`` in ``app.js``. A card whose button silently does nothing is the
   same defect in the other direction, and it is invisible: the page renders, the click is quiet.

3. **The catalogue does not link a page that was never landed.** The reverse direction, which no test
   in this repository checks for music: a card may promise ``foo.html`` that is not in the directory.

Exit code: 0 clean, 1 otherwise. Usage: ``python3 scripts/music_catalogue_unwired.py`` from the
repository root. ``--root`` points it at another tree, which is how the tests exercise it.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MUSIC = ROOT / "docs" / "music"
CATALOGUE = MUSIC / "index.html"
APP_JS = MUSIC / "app.js"

# HTML files in docs/music/ that are not repertoire pieces, each with the reason. Keep this list
# short: an entry here is a judgement about what the directory is for, not a bin.
NOT_PIECES: dict[str, str] = {
    "index.html": "the catalogue itself",
    "sandbox.html": "an interactive tool (the composer's sandbox), not a work in the repertoire",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def uncatalogued(root: Path | None = None) -> list[str]:
    """Piece pages present on disk that the catalogue never links."""
    music = Path(root) / "docs" / "music" if root else MUSIC
    catalogue = music / "index.html"
    if not catalogue.exists():
        raise ValueError(f"no catalogue at {catalogue}")
    body = _text(catalogue)
    missing = []
    for page in sorted(music.glob("*.html")):
        if page.name in NOT_PIECES:
            continue
        if page.name not in body:
            missing.append(page.name)
    return missing


def composition_keys(root: Path | None = None) -> set[str]:
    """Keys of the COMPOSITIONS object in app.js."""
    app = (Path(root) / "docs" / "music" / "app.js") if root else APP_JS
    if not app.exists():
        raise ValueError(f"no app.js at {app}")
    text = _text(app)
    start = text.find("COMPOSITIONS = {")
    if start < 0:
        raise ValueError("no `COMPOSITIONS = {` in app.js")
    # The object closes at the first `\n};` after the declaration.
    end = text.find("\n};", start)
    block = text[start:end if end > 0 else len(text)]
    return set(re.findall(r"^  ([A-Za-z][A-Za-z0-9_]*):\s*\{", block, re.M))


def audition_ids(root: Path | None = None) -> list[tuple[str, str]]:
    """[(tune id, card title)] for every data-tune on a catalogue card."""
    catalogue = (Path(root) / "docs" / "music" / "index.html") if root else CATALOGUE
    body = _text(catalogue)
    found = []
    for m in re.finditer(r"<article class=\"repertoire-card\">.*?</article>", body, re.S):
        card = m.group(0)
        tune = re.search(r"data-tune=\"([^\"]+)\"", card)
        if not tune:
            continue
        title = re.search(r"class=\"repertoire-card-title\">(.*?)</h3>", card, re.S)
        found.append((tune.group(1), re.sub("<[^>]+>", "", title.group(1)).strip() if title else "?"))
    return found


def dangling_links(root: Path | None = None) -> list[str]:
    """Catalogue links to a local .html page that is not in the directory."""
    music = (Path(root) / "docs" / "music") if root else MUSIC
    body = _text(music / "index.html")
    dangling = []
    for href in sorted(set(re.findall(r"href=\"([A-Za-z0-9_.\-]+\.html)\"", body))):
        if not (music / href).exists():
            dangling.append(href)
    return dangling


def report(root: Path | None = None) -> list[str]:
    """Every problem, as printable lines. Empty list means clean."""
    problems: list[str] = []
    for name in uncatalogued(root):
        problems.append(
            f"NOT CATALOGUED  docs/music/{name} — the piece exists and the catalogue never links it, "
            f"so it cannot be reached from the site. Add a repertoire card (Wing III for songbook "
            f"lead sheets) or list it in NOT_PIECES with the reason."
        )
    keys = composition_keys(root)
    for tune, title in audition_ids(root):
        if tune not in keys:
            problems.append(
                f"DEAD AUDITION   data-tune=\"{tune}\" ({title}) — no such key in COMPOSITIONS in "
                f"docs/music/app.js, so the button plays nothing and says nothing."
            )
    for href in dangling_links(root):
        problems.append(
            f"DANGLING CARD   the catalogue links {href}, which is not in docs/music/ — "
            f"a card promising a page that was never landed."
        )
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Find music pieces the catalogue cannot reach.")
    ap.add_argument("--root", default=None, help="repository root to check (default: this checkout)")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve() if args.root else None

    problems = report(root)
    catalogued = sorted(p.name for p in ((root / "docs" / "music") if root else MUSIC).glob("*.html")
                        if p.name not in NOT_PIECES)
    print(f"music catalogue gate: {len(catalogued)} piece page(s) checked, {len(problems)} problem(s)")
    for line in problems:
        print("  " + line)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
