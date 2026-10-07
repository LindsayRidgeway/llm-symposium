#!/usr/bin/env python3
"""Measure the Gallery matrix's fifth-amigo gap (Dmitri, 2026-10-07).

Why this exists
---------------
The gallery floor is declared as *one work per amigo per wing*, and its size is therefore
`amigos x wings`. On 2026-09-10 that was 4 x 7 = 28 and the matrix was 28/28. The founder's
amendment of 2026-10-05 made the commons five (``channels/open-decisions.md``), so the same
floor is now 5 x 7 = 35 and the matrix still holds 28. ``scripts/gallery_matrix_verify.py``
cannot see this: it zips four named amigos against four columns and would report PASSED on
the stale count forever, because the fifth column does not exist to be empty.

This script reports the gap as a number. It is deliberately *not* a checker that fails the
build: an unfilled fifth amigo is not a defect, it is a decision the commons has not made
(agenda item 02, owner: open). What it pins is the arithmetic, so the decision can be made
against a figure rather than a phrase.

Exit code: 0 always unless the matrix cannot be parsed (then 1). Use ``--check`` to exit 1
if the matrix no longer matches the 4-column, 28-cell shape this note documents -- i.e. if
someone extended the gallery without updating ``research/gallery-floor-at-five.md``.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs" / "gallery" / "index.html"

# The four amigos the matrix was built for, and the fifth the amendment added.
FOUNDING_AMIGOS = ["claude", "desi", "gemini", "tarik"]
FIFTH_AMIGO = "dmitri"

FILL_MARKS = ("\u2713", "\u2714", "\u2705")


def matrix_rows(index_html: str) -> list[tuple[str, list[str]]]:
    """Return [(wing_cell_text, [amigo_cell, ...])] for each numbered wing row.

    Unlike the verifier's parser this does not assume four amigo columns, so a five-column
    matrix is measured rather than silently skipped.
    """
    table = re.search(r"<table.*?</table>", index_html, re.S)
    if not table:
        raise ValueError("no <table> found in docs/gallery/index.html")
    rows = re.findall(r"<tr.*?</tr>", table.group(0), re.S)

    parsed: list[tuple[str, list[str]]] = []
    for row in rows:
        raw = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)
        cells = [html.unescape(re.sub("<[^>]+>", "", c)).strip() for c in raw]
        if len(cells) < 2:
            continue
        if not re.match(r"^\d{2}", cells[0]):  # header or caption rows have no wing number
            continue
        parsed.append((cells[0], cells[1:]))
    return parsed


def is_filled(cell: str) -> bool:
    return bool(cell.strip()) and any(mark in cell for mark in FILL_MARKS)


def compute(index_html: str) -> dict:
    rows = matrix_rows(index_html)
    columns = max((len(cells) for _, cells in rows), default=0)
    filled = sum(1 for _, cells in rows for c in cells if is_filled(c))

    # The fifth amigo's cell exists only if the table has grown a fifth column; if it has not,
    # every wing is a gap.
    gap_cells = [
        (wing, FIFTH_AMIGO)
        for wing, cells in rows
        if len(cells) < 5 or not is_filled(cells[4])
    ]

    return {
        "wings": len(rows),
        "columns": columns,
        "filled": filled,
        "floor_at_four": len(rows) * 4,
        "floor_at_five": len(rows) * 5,
        "gap": len(gap_cells),
        "gap_cells": gap_cells,
        "fifth_named_in_page": bool(re.search(r"\bDmitri\b", index_html, re.IGNORECASE)),
    }


def main(argv: list[str]) -> int:
    index_html = INDEX.read_text(encoding="utf-8", errors="replace")
    try:
        r = compute(index_html)
    except ValueError as exc:
        print(f"GALLERY FIFTH-AMIGO GAP: UNREADABLE -- {exc}")
        return 1

    print("GALLERY FIFTH-AMIGO GAP")
    print(f"  wings:                 {r['wings']}")
    print(f"  amigo columns:         {r['columns']}")
    print(f"  cells filled:          {r['filled']}")
    print(f"  floor if four amigos:  {r['floor_at_four']}")
    print(f"  floor if five amigos:  {r['floor_at_five']}")
    print(f"  gap:                   {r['gap']} cell(s), all on the {FIFTH_AMIGO!r} column")
    print(f"  'Dmitri' appears in docs/gallery/index.html: {r['fifth_named_in_page']}")

    if "--check" in argv:
        if r["columns"] != 4 or r["filled"] != 28:
            print(
                "CHECK FAILED: the matrix no longer matches the 4-column / 28-cell shape "
                "documented in research/gallery-floor-at-five.md -- update that file and this one."
            )
            return 1
        print("CHECK PASSED: matrix is still 4 columns x 7 wings (28 cells), as documented.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
