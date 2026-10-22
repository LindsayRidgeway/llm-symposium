#!/usr/bin/env python3
"""Keep research/creative-wings-map.md honest (Dmitri, 2026-10-19).

The map is generated from the three creative front pages and their children. Its only value is
that it cannot quietly become wrong: a hand-written note about "the seven wings" is exactly what
the to-do item was opened to fix. So this test re-renders the map and compares it to the
committed file, and it checks that the names the map asserts are actually present in the pages
rather than merely present in the map.

Nothing here asserts a *curated* fact. Wing titles, section headings, card titles and matrix
cells are read from `docs/`; if a page changes and the map is not regenerated, this fails.
"""

import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import creative_wings_map as cwm  # noqa: E402

MAP = ROOT / "research" / "creative-wings-map.md"


class CreativeWingsMapTest(unittest.TestCase):
    def setUp(self):
        self.generated = cwm.render()
        self.committed = MAP.read_text(encoding="utf-8")

    def test_the_committed_map_is_current(self):
        self.assertEqual(
            self.committed,
            self.generated,
            "research/creative-wings-map.md is stale: run python3 scripts/creative_wings_map.py",
        )

    def test_check_flag_agrees(self):
        r = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "creative_wings_map.py"), "--check"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_every_gallery_wing_title_is_in_the_map(self):
        wings = cwm.gallery_wings()
        self.assertEqual(len(wings), 7, "the gallery is documented as seven wings")
        for w in wings:
            self.assertIn(w["title"], self.committed)

    def test_every_gallery_section_heading_reaches_the_map(self):
        """A wing page's headings are the names the map exists to stop guessing at."""
        for w in cwm.gallery_wings():
            page = ROOT / "docs" / "gallery" / w["slug"] / "index.html"
            for _lvl, t in cwm.headings(page):
                self.assertIn(t, self.committed, f"{w['slug']}: heading missing from the map")

    def test_every_music_card_reaches_the_map(self):
        wings = cwm.music_wings()
        self.assertEqual(len(wings), 3, "the conservatory is documented as three wings")
        for w in wings:
            self.assertIn(w["title"], self.committed)
            for c in w["cards"]:
                self.assertIn(c["title"], self.committed)

    def test_every_fiction_story_reaches_the_map(self):
        for s in cwm.fiction_stories():
            self.assertIn(s["title"], self.committed)

    def test_the_matrix_in_the_map_matches_the_front_page(self):
        matrix = cwm.gallery_matrix()
        self.assertTrue(matrix, "the gallery front page must carry the 5x7 matrix")
        col = matrix[0].index("Dmitri")
        for row in matrix[1:]:
            self.assertIn(row[col], self.committed)

    def test_the_map_names_a_real_path_for_every_wing(self):
        for w in cwm.gallery_wings():
            self.assertTrue(
                (ROOT / "docs" / "gallery" / w["slug"] / "index.html").is_file(),
                f"{w['slug']} has no wing page",
            )
            self.assertIn(f"docs/gallery/{w['slug']}/index.html", self.committed)

    def test_the_map_does_not_invent_a_section_name(self):
        """Every `h2:`/`h3:` bullet in the map must name a heading that exists in that wing page."""
        current, real = None, {}
        for w in cwm.gallery_wings():
            page = ROOT / "docs" / "gallery" / w["slug"] / "index.html"
            real[w["title"]] = {t for _l, t in cwm.headings(page)}
        for line in self.committed.splitlines():
            m = re.match(r"\*\*\d\d\. (.+?)\*\* — `docs/gallery/([^/]+)/`", line)
            if m:
                current = m.group(1)
                continue
            m = re.match(r"- h[23]: (.+)$", line)
            if m and current:
                self.assertIn(
                    m.group(1), real[current], f"invented heading under {current}: {m.group(1)}"
                )


if __name__ == "__main__":
    unittest.main()
