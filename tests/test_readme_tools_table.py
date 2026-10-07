#!/usr/bin/env python3
"""The front door must list every released Works entry, and get its own count right.

README.md's "Tools you can use right now" table is the first thing a stranger reads about this
commons, and for a while it was the only place a released work was announced. Defect found
2026-10-07 (Dmitri, clock wake): the table stopped at Works entry 8 (2026-09-17) while the catalog
`docs/works/index.html` had reached entry 13 (2026-10-04). Five shipped pages —
`unreported-trials.html`, `recalls.html`, `food-safety.html`, `air.html`, `arena.html` — were
missing from the front door, and the sentence above the table still said "Eight public pages".

The catalog drifts because every wake may add or revise an entry, while the README is edited by hand,
so the two fall out of step silently and only a reader notices. This test makes the drift mechanical:
it derives the released set from `docs/works/index.html` (each released entry is a
`<p class="meta">Entry N …</p>` followed by its `<h3><a href="PAGE">` title link) and requires every
one of those pages to be linked from README.md. It also checks the reverse direction — every works
link in the README resolves to a file on disk — and that the spelled-out count in the prose matches
the number of table rows, so the count cannot go stale on its own.

Scope is deliberately the released list only. The "Tried, and stopped" card is a record of work not
shipped, and the front door must not advertise it; the two works pages the catalog links inline rather
than as entries (`hypothesis-precheck.html`, the command-line twin of `unjoined.html`, and the older
`local-warming.html`, superseded by `warming.html`) are not entries and are not required in the table.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
CATALOG = ROOT / "docs" / "works" / "index.html"
WORKS_DIR = ROOT / "docs" / "works"

# "Entry 9 · research tool · 2026-09-27" … then the entry's own title link on the next heading.
ENTRY = re.compile(
    r'class="meta">Entry\s+\d+[^<]*</p>\s*<h3>\s*<a href="([a-z0-9][a-z0-9-]*\.html)"',
)
README_LINK = re.compile(r"\]\(https://lindsayridgeway\.github\.io/llm-symposium/works/([a-z0-9-]+\.html)\)")
COUNT_WORD = {
    1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight",
    9: "Nine", 10: "Ten", 11: "Eleven", 12: "Twelve", 13: "Thirteen", 14: "Fourteen",
    15: "Fifteen", 16: "Sixteen", 17: "Seventeen", 18: "Eighteen", 19: "Nineteen", 20: "Twenty",
}


def released_pages():
    """The pages of the released Works entries, in catalog order, from the catalog itself."""
    html = CATALOG.read_text(encoding="utf-8")
    # The released section ends at the "Tried, and stopped" heading; stop there so a stopped
    # candidate can never be mistaken for something we ship.
    released = html.split("Tried, and stopped")[0]
    return ENTRY.findall(released)


def readme_links():
    return README_LINK.findall(README.read_text(encoding="utf-8"))


class ReadmeToolsTableTest(unittest.TestCase):
    def test_the_scan_is_not_vacuous(self):
        # If the catalog's markup ever changes shape, the extractor would silently return nothing
        # and this guard would pass by finding no entries at all. Assert it sees real material.
        pages = released_pages()
        self.assertGreaterEqual(len(pages), 13, f"catalog scan found only {pages}")
        self.assertIn("unjoined.html", pages)
        self.assertIn("arena.html", pages)

    def test_every_released_entry_is_on_the_front_door(self):
        linked = set(readme_links())
        missing = [p for p in released_pages() if p not in linked]
        self.assertEqual(
            missing, [],
            "README.md's tools table is missing released Works entries: "
            + ", ".join(missing)
            + " — add a row (with its honest limit) for each, or the front door understates the commons.",
        )

    def test_every_readme_works_link_resolves_to_a_file(self):
        broken = [p for p in readme_links() if not (WORKS_DIR / p).is_file()]
        self.assertEqual(broken, [], f"README links to works pages that do not exist: {broken}")

    def test_the_spelled_out_count_matches_the_row_count(self):
        text = README.read_text(encoding="utf-8")
        rows = README_LINK.findall(text)
        word = COUNT_WORD.get(len(rows))
        self.assertIsNotNone(word, f"{len(rows)} rows: extend COUNT_WORD in this test")
        self.assertIn(
            f"{word} public pages and one command", text,
            f'README says "… public pages and one command" but the table has {len(rows)} pages; '
            f'the prose should read "{word}".',
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
