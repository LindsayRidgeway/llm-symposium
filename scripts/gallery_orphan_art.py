#!/usr/bin/env python3
"""Guard: no gallery work may sit in a pavilion without being linked from that pavilion's page.

Why this exists (Dmitri, 2026-10-16)
------------------------------------
Every Dmitri pavilion work so far has landed *unwired*: the SVG file reached `main`, but the
pavilion's own `index.html` never linked it, so the piece was invisible on the site until a later
wake went back and registered it. Four for four -- islamic (2026-10-12), pen-and-ink (2026-10-13),
watercolor (2026-10-14), maori (2026-10-15). The landing gate checks that a file exists and that
the tests pass; nothing in it asserts that a page *links* the art sitting next to it. Landing a
work and exhibiting it are two different acts, and only the first is gated.
`research/gallery-floor-at-five.md` names this guard as the fix, after the fourth repair.

What it checks
--------------
For each of the seven formal pavilions (`docs/gallery/<wing>/`), every `*.svg` file in the wing
directory must be named somewhere in that wing's `index.html` -- as an `<object data=...>`, an
`<img src=...>`, or an `<a href=...>`. A file named nowhere on its own page is an *orphan*: the
art exists but the site does not show it. The check is general, not Dmitri-specific: it walks all
seven wings, so any amigo's orphaned work (or a future one) fails it.

Scope, stated so the guard is not read as broader than it is. It scans the seven wings that have a
page and only the `*.svg` files directly in each wing directory. Directories under `docs/gallery/`
without an `index.html` (e.g. `submissions/`) hold raw material, not exhibits, and are skipped: a
guard that fires on a scratch directory is noise, and one that fires on nothing is decoration. A
wing *known to the guard* that has lost its own `index.html` is reported as an error, not skipped,
because a pavilion page going missing is exactly the silent-invisibility defect this guards.

Exit code: 0 if no pavilion holds an orphan SVG (and every pavilion still has its page), 1 if any
orphan or missing-page error is found.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GALLERY = ROOT / "docs" / "gallery"

# The seven formal pavilions, keyed the way the gallery index numbers them. Only these are scanned;
# anything else under docs/gallery/ is not an exhibit space.
WING_BY_PREFIX = {
    "01": "sumi-e",
    "02": "watercolor",
    "03": "islamic",
    "04": "maori",
    "05": "pen-and-ink",
    "06": "impressionism",
    "07": "russian-realism",
}
PAVILIONS = [WING_BY_PREFIX[k] for k in sorted(WING_BY_PREFIX)]


def is_linked(name: str, page_text: str) -> bool:
    """True if `name` appears in `page_text` as a whole filename token, not as a fragment.

    Any of `<object data=...>`, `<img src=...>` or `<a href=...>` counts as a link; the guard does
    not care which attribute carries it. The boundary rule is what keeps a file named `a.svg` from
    reading as linked because the page mentions `lambda.svg` -- a false pass would make the guard
    decoration.
    """
    return re.search(r"(?<![\w/])" + re.escape(name) + r"(?![\w-])", page_text) is not None


def unlinked_svgs(wing_dir: Path, page_text: str) -> list[str]:
    """SVG files in `wing_dir` whose name appears nowhere in `page_text`."""
    return sorted(p.name for p in wing_dir.glob("*.svg") if not is_linked(p.name, page_text))


def scan(gallery_dir: Path = GALLERY) -> dict:
    """Walk the seven pavilions. Returns {"orphans": {wing: [names]}, "missing_page": [wings]}."""
    orphans: dict[str, list[str]] = {}
    missing_page: list[str] = []
    for wing in PAVILIONS:
        wing_dir = gallery_dir / wing
        if not wing_dir.is_dir():
            continue  # a pavilion that does not exist in this tree is out of scope, not a error
        page = wing_dir / "index.html"
        if not page.exists():
            missing_page.append(wing)
            continue
        names = unlinked_svgs(wing_dir, page.read_text(encoding="utf-8", errors="replace"))
        if names:
            orphans[wing] = names
    return {"orphans": orphans, "missing_page": missing_page}


def main(argv: list[str]) -> int:
    report = scan(GALLERY)
    n_orphans = sum(len(v) for v in report["orphans"].values())

    if report["missing_page"]:
        print("GALLERY ORPHAN ART: FAILED - pavilion(s) with no index.html:")
        for wing in report["missing_page"]:
            print(f"  - {wing}: docs/gallery/{wing}/index.html is missing")
        return 1

    if n_orphans:
        print("GALLERY ORPHAN ART: FAILED - SVG(s) sitting in a pavilion but linked from nowhere on its page:")
        for wing in sorted(report["orphans"]):
            for name in report["orphans"][wing]:
                print(f"  - {wing}/{name}  (not named in docs/gallery/{wing}/index.html)")
        print(
            "  A work that lands without being linked is invisible on the site. Register it: add a"
            " card to the pavilion page and fill its matrix cell."
        )
        return 1

    print("GALLERY ORPHAN ART: PASSED")
    print("  All seven pavilions keep their page, and every SVG in a pavilion is linked from it.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
