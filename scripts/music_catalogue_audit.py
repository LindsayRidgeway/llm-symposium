#!/usr/bin/env python3
"""music_catalogue_audit.py — does the conservatory's catalogue match its shelf?

Why this exists (Dmitri, 2026-10-20). Two things went missing from `docs/music/`
without anyone noticing, and neither was caught by any test:

  * The Passacaglia in G Minor's catalogue card, landed 2026-10-13, was dropped
    from `docs/music/index.html` on 2026-10-17 by a stash-conflict resolution
    ("resolved toward upstream"). The score page itself survived. For eleven
    days the conservatory held a full score that nothing linked to, so no reader
    could reach it — and the page still rendered, so nothing looked broken.
  * "The Unlogged Hour" was landed on 2026-10-13 as a bare `.abc` source file
    with no page, no card and no audio entry, and a lyric that did not fit its
    own melody. A score that exists as a file nobody can play is not a
    contribution, and nothing said so.

Both are the same defect: the catalogue page and the files beside it are
maintained by hand, in different commits, by different parties, and no check
compares them. This is a check. It reports six things:

  1. ORPHAN PAGE     — a score page on disk that `index.html` never links to.
  2. ORPHAN CARD     — a catalogue card linking to a page that does not exist.
  3. DEAD TUNE       — a `data-tune` / composition with no audio entry, or an
                       audio entry no card can reach.
  4. PAGE/ENGINE DIVERGENCE — the engraved ABC on a score page differs from the
                       ABC the audition button actually synthesizes. The reader
                       and the player then disagree about what the piece *is*.
  5. ORPHAN SOURCE   — a `.abc` file that no page embeds and no engine entry
                       holds (a composition that never became visible).
  6. DEBRIS          — leftover `*.tmp` scratch files in `docs/music/`.

What it does NOT check: whether a piece is any good, whether a card's prose is
true, or whether an orphan *should* be indexed. Those are judgements.

Known gaps. Some of these conditions predate the check and belong to scores
another amigo wrote; a gate that fails on someone else's debt is a gate that
gets switched off. They are listed in KNOWN_GAPS with a reason, the audit names
them on every run as debt, and it **fails only on conditions not on that list**.
The list may only shrink: `--check-debt` fails if an entry no longer reproduces,
so a repaired gap has to be deleted from the file rather than left behind.

Usage:
    python3 scripts/music_catalogue_audit.py            # audit docs/music
    python3 scripts/music_catalogue_audit.py --root .   # audit another checkout
    python3 scripts/music_catalogue_audit.py --strict   # non-zero on any finding
"""

import argparse
import html
import re
import sys
from pathlib import Path

# --- frozen debt: (kind, subject) -> why it is not fixed here ----------------
KNOWN_GAPS = {
    ("orphan_page", "the-cairn.html"):
        "score page on main, no catalogue card; indexing another amigo's score "
        "means inventing its metadata, which is its author's or the curator's call",
    ("orphan_page", "the-returning-step.html"):
        "score page on main, no catalogue card (Tarik's Controlled Study IV)",
    ("orphan_page", "the-small-repair.html"):
        "score page on main, no catalogue card (Tarik's lead sheet)",
    ("orphan_source", "between-wakings.abc"):
        "Claude's lead-sheet source on main with no page and no engine entry",
}

PAGE_SKIP = {"index.html", "sandbox.html"}

DRAWER_RE = re.compile(
    r'<pre class="abc-code-drawer">(.*?)</pre>', re.S)
TUNE_RE = re.compile(r'data-tune="([^"]+)"')
HREF_RE = re.compile(r'href="([A-Za-z0-9._-]+\.html)"')
COMP_ENTRY_RE = re.compile(r'^  ([A-Za-z0-9_]+): \{', re.M)
COMP_ID_RE = re.compile(r'^    id: "([^"]+)"', re.M)


def normalise(abc: str) -> str:
    """Compare ABC by content, not by layout: no trailing spaces, no blank lines."""
    lines = [line.rstrip() for line in abc.strip().splitlines()]
    return "\n".join(line for line in lines if line)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def compositions(app_js: Path):
    """Return {tune key: (engine id, abc)} from the COMPOSITIONS object."""
    text = read(app_js)
    entries, found = {}, []
    keys = list(COMP_ENTRY_RE.finditer(text))
    for i, match in enumerate(keys):
        end = keys[i + 1].start() if i + 1 < len(keys) else len(text)
        block = text[match.start():end]
        ident = COMP_ID_RE.search(block)
        abc = re.search(r'abc: `(.*?)`', block, re.S)
        if ident and abc:
            found.append((match.group(1), ident.group(1), abc.group(1)))
    for key, ident, abc in found:
        entries[key] = (ident, abc)
    return entries


def audit(root: Path):
    music = root / "docs" / "music"
    index = music / "index.html"
    app_js = music / "app.js"
    findings = []

    index_text = read(index)
    pages = {p.name for p in music.glob("*.html")} - PAGE_SKIP
    linked = set(HREF_RE.findall(index_text)) - PAGE_SKIP
    tunes = set(TUNE_RE.findall(index_text))
    comps = compositions(app_js)

    # 1 / 2 — pages and cards, both directions
    for page in sorted(pages - linked):
        findings.append(("orphan_page", page,
                         "page exists on disk but no catalogue card links to it"))
    for link in sorted(linked - pages - {"index.html"}):
        findings.append(("orphan_card", link,
                         "index.html links to a page that does not exist"))

    # 3 — audition wiring, both directions
    for tune in sorted(tunes - set(comps)):
        findings.append(("dead_tune", tune,
                         "catalogue card offers ▶ Audition but app.js has no such composition"))
    for tune in sorted(set(comps) - tunes):
        findings.append(("dead_tune", tune,
                         "app.js composition has no catalogue card, so nothing can reach it"))

    # 4 — the page's engraving vs the engine's synthesis
    drawers = {}
    for page in sorted(pages & linked):
        match = DRAWER_RE.search(read(music / page))
        if not match:
            continue
        drawers[page] = normalise(html.unescape(match.group(1)))
    for page, drawer in drawers.items():
        for tune, (ident, abc) in comps.items():
            if ident and ident in read(music / page):
                if normalise(abc) != drawer:
                    findings.append(("page_engine_divergence", page,
                                     f"engraved ABC differs from the {tune} audio entry"))

    # 5 — .abc sources that nothing shows
    shown = set(drawers.values()) | {normalise(abc) for _, abc in comps.values()}
    for source in sorted(music.glob("*.abc")):
        if normalise(read(source)) not in shown:
            findings.append(("orphan_source", source.name,
                             "no score page embeds this ABC and no engine entry holds it"))

    # 6 — scratch files left in the published directory
    for debris in sorted(list(music.glob("*.tmp")) + list(music.glob("*.abc.tmp"))):
        findings.append(("debris", debris.name,
                         "leftover scratch file in the published music directory"))

    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    parser.add_argument("--strict", action="store_true",
                        help="exit non-zero on frozen debt too")
    parser.add_argument("--check-debt", action="store_true",
                        help="also fail if a frozen entry no longer reproduces")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    findings = audit(root)
    found = {(kind, subject) for kind, subject, _ in findings}

    new = [f for f in findings if (f[0], f[1]) not in KNOWN_GAPS]
    debt = [f for f in findings if (f[0], f[1]) in KNOWN_GAPS]
    repaired = sorted(set(KNOWN_GAPS) - found)

    print("Music catalogue audit — docs/music/")
    print(f"  findings: {len(findings)}  (new: {len(new)}, known debt: {len(debt)})")
    if new:
        print("\n[NEW] not on the frozen list:")
        for kind, subject, why in new:
            print(f"  {kind:<22} {subject}\n      {why}")
    if debt:
        print("\n[KNOWN DEBT] recorded, not fixed here:")
        for kind, subject, _ in debt:
            print(f"  {kind:<22} {subject}\n      {KNOWN_GAPS[(kind, subject)]}")
    if repaired and args.check_debt:
        print("\n[STALE LIST] these entries no longer reproduce — delete them:")
        for kind, subject in repaired:
            print(f"  {kind:<22} {subject}")

    failed = bool(new) or bool(repaired and args.check_debt) or (args.strict and findings)
    print("\nResult:", "FAILED" if failed else "PASSED")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
