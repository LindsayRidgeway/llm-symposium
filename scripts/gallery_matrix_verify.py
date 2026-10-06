#!/usr/bin/env python3
"""Verify the Gallery's 4x7 Amigo Matrix against the pavilion pages it claims to describe.

Why this exists (Dmitri, 2026-10-06)
------------------------------------
The 4x7 Amigo Matrix lives as a hand-written HTML table in `docs/gallery/index.html`:
seven wing rows, four amigo columns, and in each of the 28 cells a check mark plus the
*name* of that amigo's work ("✓ Misty Rock & Lone Boat"). Nothing in the commons checks
that those 28 names correspond to anything. `tests/test_artifact_claims.py` verifies
`href`/`data`/`src` attributes and backtick paths, but the matrix cells are plain prose,
so a cell may name a work that does not exist and every existing check stays green.

That is not hypothetical: the original phantom-artifact incident that produced
`test_artifact_claims.py` was a cell of this same table (Gemini credited with a
"Mangopare Koru SVG" at a path that existed nowhere). The fix generalised the *attribute*
check and left the matrix cells themselves — the actual site of the failure — unguarded.
This script closes that specific gap.

What it checks
--------------
For each of the 28 cells:
  1. the cell is non-empty and carries the fill mark — a blank cell means the declared
     floor (one work per amigo per wing) is broken and the "28/28" claim is false;
  2. every distinctive word of the work name appears somewhere in that wing's own
     `index.html` — i.e. the pavilion the matrix points at actually presents the work.

Matching is token-set based, not substring, because the matrix and the pavilion pages
legitimately differ in punctuation and diacritics ("Mangopare Koru" vs a page heading
"Mangopare: The Hammerhead Koru"; "&" vs "and"). Equal-strength, order-free token
containment across the whole wing page is the loosest rule that still fails on a
fabricated name, which is the point: it is a plausibility check, not proof.

Exit code: 0 if all 28 cells are filled and resolve to their wing, 1 otherwise.
"""

from __future__ import annotations

import html
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GALLERY = ROOT / "docs" / "gallery"
INDEX = GALLERY / "index.html"

# Wing label prefix in the table -> pavilion directory.
WING_BY_PREFIX = {
    "01": "sumi-e",
    "02": "watercolor",
    "03": "islamic",
    "04": "maori",
    "05": "pen-and-ink",
    "06": "impressionism",
    "07": "russian-realism",
}

AMIGOS = ["claude", "desi", "gemini", "tarik"]

# Words that carry no identifying weight in a work title.
STOPWORDS = {"and", "the", "of", "a", "an", "in", "on", "at", "amp", "svg"}

FILL_MARKS = ("✓", "✔", "✅")


def normalize_tokens(text: str) -> set[str]:
    """Lowercase, strip accents, split to word tokens, drop stopwords and one-chars."""
    text = html.unescape(text)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    tokens = re.split(r"[^0-9a-z\u3000-\u9fff]+", text)
    return {t for t in tokens if len(t) > 1 and t not in STOPWORDS}


def parse_matrix(index_html: str) -> list[tuple[str, list[str]]]:
    """Return [(wing_slug, [cell, cell, cell, cell])] in row order.

    Raises ValueError if the table shape is not the 7x4 the commons claims.
    """
    table = re.search(r"<table.*?</table>", index_html, re.S)
    if not table:
        raise ValueError("no <table> found in docs/gallery/index.html")
    rows = re.findall(r"<tr.*?</tr>", table.group(0), re.S)

    parsed: list[tuple[str, list[str]]] = []
    for row in rows:
        raw = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)
        cells = [html.unescape(re.sub("<[^>]+>", "", c)).strip() for c in raw]
        if len(cells) != 5:  # header row (5 cols) or a stray row; skip headers by shape
            continue
        if cells[0].startswith(("Wing", "Claude")) or cells[1] == "Claude":
            continue
        prefix = cells[0][:2]
        if prefix not in WING_BY_PREFIX:
            raise ValueError(f"unrecognised wing row label: {cells[0]!r}")
        parsed.append((WING_BY_PREFIX[prefix], cells[1:]))
    return parsed


def verify_cell(wing_slug: str, cell: str) -> list[str]:
    """Return the list of work-name tokens missing from the wing's index.html.

    Empty list == the pavilion presents a work matching this cell's name.
    """
    wing_page = GALLERY / wing_slug / "index.html"
    if not wing_page.exists():
        return sorted(normalize_tokens(cell.lstrip("".join(FILL_MARKS))))
    page_tokens = normalize_tokens(wing_page.read_text(encoding="utf-8", errors="replace"))
    name = cell.lstrip("".join(FILL_MARKS)).strip()
    return sorted(normalize_tokens(name) - page_tokens)


def is_filled(cell: str) -> bool:
    return bool(cell.strip()) and any(mark in cell for mark in FILL_MARKS)


def main() -> int:
    index_html = INDEX.read_text(encoding="utf-8", errors="replace")
    try:
        rows = parse_matrix(index_html)
    except ValueError as exc:
        print(f"GALLERY MATRIX: FAILED — {exc}")
        return 1

    problems: list[str] = []
    if len(rows) != 7:
        problems.append(f"expected 7 wing rows, found {len(rows)}")

    cells_seen = 0
    for wing_slug, cells in rows:
        for amigo, cell in zip(AMIGOS, cells):
            cells_seen += 1
            if not is_filled(cell):
                problems.append(f"{wing_slug}/{amigo}: cell is empty (floor not met)")
                continue
            missing = verify_cell(wing_slug, cell)
            if missing:
                problems.append(
                    f"{wing_slug}/{amigo}: '{cell.lstrip(''.join(FILL_MARKS)).strip()}' "
                    f"not found in docs/gallery/{wing_slug}/index.html "
                    f"(missing: {', '.join(missing)})"
                )

    if cells_seen != 28:
        problems.append(f"expected 28 cells (7 wings x 4 amigos), found {cells_seen}")

    if problems:
        print("GALLERY MATRIX: FAILED")
        for p in problems:
            print(f"  - {p}")
        return 1

    print("GALLERY MATRIX: PASSED")
    print(
        "  All 28 cells (7 wings x 4 amigos) are filled and each names a work "
        "present in its own pavilion page."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
