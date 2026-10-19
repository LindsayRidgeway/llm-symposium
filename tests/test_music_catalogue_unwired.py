#!/usr/bin/env python3
"""Pin the music catalogue gate (Dmitri, 2026-10-19).

`scripts/music_catalogue_unwired.py` exists because two finished pieces were repaired by hand in
two days: `the-level-ground.html` (wired 2026-10-19 by run 20261019T011755Z) and `the-cairn.html`
(wired 2026-10-19 by this run). Both had a score page and a playable entry in `app.js`, and the
catalogue never linked either one. A third manual repair would be a third instance of the same
defect, so the class gets a gate.

The live tree must pass, and the gate must still fail when a piece is dropped into the directory
uncatalogued, when a card's audition id has no composition, and when a card links a page that is
not there. A gate that cannot fail is not a gate; the negative cases are the point.
"""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import music_catalogue_unwired as gate  # noqa: E402

WING_III = """<section class="catalog-wing"><div class="repertoire-grid">
<article class="repertoire-card">
  <div>
    <div class="repertoire-card-header"><span class="comp-author-pill pill-desi">Desi</span></div>
    <h3 class="repertoire-card-title">The Cairn</h3>
  </div>
  <div class="repertoire-card-footer">
    <button class="catalog-audition-btn" data-tune="cairn">▶ Audition</button>
    <a href="the-cairn.html" class="btn-score-link">View Full Score &amp; Analysis →</a>
  </div>
</article>
</div></section>"""

APP = """const COMPOSITIONS = {
  cairn: {
    id: "cairn",
    title: "The Cairn",
  },
  dmitri: {
    id: "dmitri",
    title: "The Level Ground",
  },
};
"""


class MusicCatalogueGateTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="music-gate-"))
        music = self.root / "docs" / "music"
        music.mkdir(parents=True)
        (music / "index.html").write_text(
            "<html><body>" + WING_III + '<a href="sandbox.html">Sandbox</a></body></html>'
        )
        (music / "the-cairn.html").write_text("<html>score</html>")
        (music / "sandbox.html").write_text("<html>tool</html>")
        (music / "app.js").write_text(APP)

    # --- the clean case -------------------------------------------------
    def test_clean_tree_reports_nothing(self):
        self.assertEqual(gate.report(self.root), [])
        self.assertEqual(gate.uncatalogued(self.root), [])
        self.assertEqual(gate.dangling_links(self.root), [])

    def test_composition_keys_are_read_from_the_object(self):
        self.assertEqual(gate.composition_keys(self.root), {"cairn", "dmitri"})

    def test_sandbox_is_not_a_piece(self):
        # sandbox.html is not linked as a piece but is exempt by name; if the exemption were
        # ignored, every run would report it forever and the gate would be noise.
        self.assertIn("sandbox.html", gate.NOT_PIECES)
        self.assertEqual(gate.uncatalogued(self.root), [])

    # --- the defects this gate exists for -------------------------------
    def test_uncatalogued_piece_is_flagged(self):
        (self.root / "docs" / "music" / "the-cairn-two.html").write_text("<html>score</html>")
        problems = gate.report(self.root)
        self.assertEqual(len(problems), 1)
        self.assertIn("NOT CATALOGUED", problems[0])
        self.assertIn("the-cairn-two.html", problems[0])

    def test_dead_audition_id_is_flagged(self):
        music = self.root / "docs" / "music"
        music.joinpath("index.html").write_text(
            music.joinpath("index.html").read_text().replace('data-tune="cairn"', 'data-tune="cairne"')
        )
        problems = gate.report(self.root)
        self.assertEqual(len(problems), 1)
        self.assertIn("DEAD AUDITION", problems[0])
        self.assertIn("cairne", problems[0])

    def test_dangling_card_link_is_flagged(self):
        music = self.root / "docs" / "music"
        music.joinpath("index.html").write_text(
            music.joinpath("index.html").read_text().replace(
                'href="the-cairn.html"', 'href="the-cairn-never-landed.html"'
            )
        )
        problems = gate.report(self.root)
        # Two problems on purpose: the page is no longer linked *and* the new link is dangling.
        joined = "\n".join(problems)
        self.assertIn("DANGLING CARD", joined)
        self.assertIn("the-cairn-never-landed.html", joined)
        self.assertIn("NOT CATALOGUED", joined)

    def test_cli_exit_codes(self):
        self.assertEqual(gate.main(["--root", str(self.root)]), 0)
        (self.root / "docs" / "music" / "orphan.html").write_text("<html>score</html>")
        self.assertEqual(gate.main(["--root", str(self.root)]), 1)

    # --- the live tree ---------------------------------------------------
    def test_live_tree_is_clean(self):
        self.assertEqual(gate.report(), [], "docs/music has a page the catalogue cannot reach")

    def test_the_cairn_is_catalogued_on_main(self):
        # The specific repair this run made, pinned so it cannot silently come undone.
        body = (ROOT / "docs" / "music" / "index.html").read_text(encoding="utf-8")
        self.assertIn("the-cairn.html", body)
        self.assertIn('data-tune="cairn"', body)


if __name__ == "__main__":
    unittest.main()
