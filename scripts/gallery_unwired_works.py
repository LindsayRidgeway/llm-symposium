#!/usr/bin/env python3
"""Landed is not exhibited: find gallery works that no pavilion page links (Dmitri, 2026-10-18).

Why this exists
---------------
Every pavilion work Dmitri made before today landed *unwired*, five times out of five:

    2026-10-12  islamic           ninefold-girih-rosette.svg       → wired 2026-10-13
    2026-10-13  pen-and-ink       hatching-the-catenoid.svg        → wired 2026-10-14
    2026-10-14  watercolor        backrun-and-the-drying-ring.svg  → wired 2026-10-14
    2026-10-15  maori             unaunahi-the-unbroken-scale.svg  → wired 2026-10-16
    2026-10-15  impressionism     the-fusion-threshold.svg         → wired 2026-10-18

`research/gallery-floor-at-five.md` names the cause exactly: the landing gate checks that a
file exists and the tests pass, and **nothing in it asserts that a pavilion page links the
SVG sitting next to it.** So each repair was a repair of the instance, not of the class. This
is the gate the note asks for.

What it checks
--------------
1. **Wiring.** For each wing, every top-level ``*.svg`` in the wing directory must appear in
   that wing's ``index.html`` — as a ``href``, ``object data``, ``img src``, or a plain
   mention. An SVG that is present but unreferenced is *landed and not exhibited*, which is
   invisible to every other test in the suite. Files under ``studies/`` are an archive of
   candidates, not exhibition pieces, and are not counted.

   A work may be *deliberately* unexhibited — a study that the author, who is the only
   person entitled to curate their own work (prompt-methodology.md §4), decided against
   showing. That is legitimate, but it must be **written down**, one line of reason per file,
   in ``EXHIBITION_EXEMPT`` below. So the default is failure and exemption is an argument,
   not a silence.

2. **The matrix agrees with the pavilions.** If a wing's page exhibits a work signed by
   Dmitri, the gallery matrix's Dmitri cell for that wing must not still read
   "Open (Floor at 5)". This is the other half of the same defect: a page can be wired while
   the front table still says the cell is empty.

Exit code: 0 clean, 1 if anything is landed-but-unexhibited or the matrix contradicts a page.
Usage: ``python3 scripts/gallery_unwired_works.py`` (from the repository root).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GALLERY = ROOT / "docs" / "gallery"
INDEX = GALLERY / "index.html"

# Wing directories whose pages are exhibition pages. `submissions/` is a holding area and
# `studies/` inside a wing is the candidates archive — neither is a pavilion.
WINGS = [
    "sumi-e",
    "watercolor",
    "islamic",
    "maori",
    "pen-and-ink",
    "impressionism",
    "russian-realism",
]

# Works that are present, finished, and deliberately not on the wall — each with the reason
# a reader would need to know it was a decision and not an oversight. Keep this list short:
# an entry here is a curatorial judgement, not a bin.
EXHIBITION_EXEMPT: dict[str, str] = {
    "russian-realism/the-edge-of-the-sunbreak.svg":
        "A study, not an exhibition piece (Dmitri, 2026-10-18). The penumbra arithmetic is "
        "sound and printed on the plate, but the image does not carry it: the snow reads as a "
        "blank field with scattered marks rather than as light stopping at a distance, and the "
        "wing's other four works are painted oils. Withheld until wing 07 has a painted work; "
        "the request for that work is REQUEST DM-2. Not deleted — the constraint work stands.",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def unexhibited(wings: list[str] | None = None) -> list[tuple[str, str]]:
    """Return [(wing, filename)] for top-level SVGs no pavilion page references."""
    found: list[tuple[str, str]] = []
    for wing in wings or WINGS:
        d = GALLERY / wing
        page = d / "index.html"
        if not page.exists():
            continue
        body = _text(page)
        for svg in sorted(d.glob("*.svg")):
            if svg.name not in body:
                found.append((wing, svg.name))
    return found


def exempt(found: list[tuple[str, str]]) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """Split unreferenced works into (unexplained, explained-by-exemption)."""
    unexplained, explained = [], []
    for wing, name in found:
        (explained if f"{wing}/{name}" in EXHIBITION_EXEMPT else unexplained).append((wing, name))
    return unexplained, explained


DMITRI_SIGNS = ("Dmitri S. Pravdin", "Правдин")


def matrix_conflicts() -> list[tuple[str, str]]:
    """Wings whose page exhibits a Dmitri work while the matrix still calls the cell open."""
    index = _text(INDEX)
    table = re.search(r"<table.*?</table>", index, re.S)
    if not table:
        raise ValueError("no matrix <table> in docs/gallery/index.html")
    open_wing_nums: set[str] = set()
    for row in re.findall(r"<tr.*?</tr>", table.group(0), re.S):
        cells = [re.sub("<[^>]+>", "", c).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
        if len(cells) >= 6 and re.match(r"^\d{2}", cells[0]) and "Open" in cells[5]:
            open_wing_nums.add(cells[0][:2])

    conflicts: list[tuple[str, str]] = []
    for wing in WINGS:
        page = GALLERY / wing / "index.html"
        if not page.exists() or not any(s in _text(page) for s in DMITRI_SIGNS):
            continue
        num = f"{WINGS.index(wing) + 1:02d}"
        if num in open_wing_nums:
            conflicts.append((num, wing))
    return conflicts


def main() -> int:
    unexplained, explained = exempt(unexhibited())
    conflicts = matrix_conflicts()

    print("GALLERY WIRING — landed vs exhibited")
    print(f"  wings scanned:                  {len(WINGS)}")
    print(f"  unreferenced SVGs, unexplained: {len(unexplained)}")
    print(f"  unreferenced SVGs, exempted:    {len(explained)}")
    for wing, name in unexplained:
        print(f"    NOT EXHIBITED  {wing}/{name}")
    for wing, name in explained:
        print(f"    exempt         {wing}/{name} — {EXHIBITION_EXEMPT[f'{wing}/{name}'].splitlines()[0][:90]}")
    print(f"  matrix contradictions:           {len(conflicts)}")
    for num, wing in conflicts:
        print(f"    MATRIX SAYS OPEN  {num} {wing} — but the pavilion page exhibits a Dmitri work")

    if unexplained or conflicts:
        print("\nFAIL — a work is on disk and not on the wall (or the table disagrees with the page).")
        return 1
    print("\nPASS — every finished work is either exhibited or has a written reason it is not.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
