#!/usr/bin/env python3
"""Pin the music catalogue gate (Dmitri, 2026-10-19) — and pin that CI runs it.

`scripts/music_catalogue_unwired.py` exists because two finished pieces (`the-level-ground.html`,
`the-cairn.html`) landed on disk and were never reachable from `docs/music/index.html` — the landing
gate checked that the file existed and that the tests passed, and nothing asked whether the catalogue
linked it. Its sibling gate for the gallery (`scripts/gallery_unwired_works.py`) got this file the
day after it was written; the music gate did not, and on 2026-10-20 it was on `main` with **zero
references anywhere in the repository**: not in `tests/`, not in `.github/workflows/test-and-report.yml`.
It printed `0 problem(s)` whenever a person typed its name and ran never otherwise.

A gate nothing runs is not a gate, so this file guards three things:

  1. the live tree is clean (the catalogue links every piece that exists);
  2. each of the gate's three checks still *fails* on a defect — a check that cannot fail is
     decoration. The negative fixtures are the substance of the file;
  3. the gate is registered in the CI workflow, so "written and never run" cannot happen to it again.

Run: ``python3 tests/test_music_catalogue_unwired.py``
"""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import music_catalogue_unwired as gate  # noqa: E402

CARD = (
    '<article class="repertoire-card">\n'
    '  <h3 class="repertoire-card-title">A Wired Piece</h3>\n'
    '  <button data-tune="{tune}">Audition</button>\n'
    '  <a href="{href}">Score</a>\n'
    '</article>'
)

APP_JS = """const COMPOSITIONS = {
  wired_tune: {
    name: "A Wired Piece",
  },
};
"""


def _fixture(tmp: Path, cards=(), app_js: str = APP_JS) -> None:
    """A miniature music directory: one catalogue, one landed piece, an app.js with one tune."""
    music = tmp / "docs" / "music"
    music.mkdir(parents=True)
    (music / "wired-piece.html").write_text("<html>score</html>")
    body = "\n".join(cards) if cards else CARD.format(tune="wired_tune", href="wired-piece.html")
    (music / "index.html").write_text(f"<html><body>{body}</body></html>")
    (music / "app.js").write_text(app_js)


class MusicCatalogueGateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="music-gate-"))
        _fixture(self.tmp)

    def test_wired_tree_is_clean(self):
        self.assertEqual(gate.report(self.tmp), [])
        self.assertEqual(gate.main(["--root", str(self.tmp)]), 0)

    # --- check 1: a landed piece the catalogue never links -------------------------------------
    def test_unlinked_piece_is_flagged(self):
        (self.tmp / "docs" / "music" / "orphan-piece.html").write_text("<html/>")
        self.assertEqual(gate.uncatalogued(self.tmp), ["orphan-piece.html"])
        self.assertTrue(any("NOT CATALOGUED" in p for p in gate.report(self.tmp)))
        self.assertEqual(gate.main(["--root", str(self.tmp)]), 1)

    def test_written_exemption_silences_it(self):
        (self.tmp / "docs" / "music" / "sketch.html").write_text("<html/>")
        saved = dict(gate.NOT_PIECES)
        gate.NOT_PIECES["sketch.html"] = "a working sketch, not a repertoire piece"
        try:
            self.assertEqual(gate.uncatalogued(self.tmp), [])
        finally:
            gate.NOT_PIECES.clear()
            gate.NOT_PIECES.update(saved)

    # --- check 2: a card whose audition button plays nothing -----------------------------------
    def test_dead_audition_tune_is_flagged(self):
        (self.tmp / "docs" / "music" / "index.html").write_text(
            "<html><body>"
            + CARD.format(tune="ghost_tune", href="wired-piece.html")
            + "</body></html>"
        )
        self.assertNotIn("ghost_tune", gate.composition_keys(self.tmp))
        problems = gate.report(self.tmp)
        self.assertTrue(any("DEAD AUDITION" in p and "ghost_tune" in p for p in problems), problems)
        self.assertEqual(gate.main(["--root", str(self.tmp)]), 1)

    # --- check 3: a card promising a page that was never landed --------------------------------
    def test_dangling_card_link_is_flagged(self):
        (self.tmp / "docs" / "music" / "index.html").write_text(
            "<html><body>"
            + CARD.format(tune="wired_tune", href="never-landed.html")
            + "</body></html>"
        )
        self.assertEqual(gate.dangling_links(self.tmp), ["never-landed.html"])
        self.assertTrue(any("DANGLING CARD" in p for p in gate.report(self.tmp)))
        self.assertEqual(gate.main(["--root", str(self.tmp)]), 1)

    # --- two limits of the gate itself, pinned so a later reader knows its strength --------------
    # These two tests assert the CURRENT behaviour, and the current behaviour is weaker than the
    # docstring claims. They are here so the gap is recorded rather than rediscovered: a reviewer
    # who runs this file should see that the gate is a good net with two known holes, not a proof.
    # Fixing either one is the author's call (Dmitri), so the reviewer did not touch the script.

    def test_a_bare_mention_counts_as_catalogued_KNOWN_LIMIT(self):
        """Check 1 is a substring test: the filename anywhere in index.html satisfies it — a
        comment, a 'coming soon' sentence, a prefetch link. No card is required."""
        music = self.tmp / "docs" / "music"
        (music / "mentioned-only.html").write_text("<html/>")
        (music / "index.html").write_text(
            "<html><body>"
            + CARD.format(tune="wired_tune", href="wired-piece.html")
            + "<!-- mentioned-only.html: coming soon --></body></html>"
        )
        self.assertNotIn("mentioned-only.html", gate.uncatalogued(self.tmp))

    def test_links_into_subdirectories_and_with_fragments_are_NOT_checked_KNOWN_LIMIT(self):
        """Check 3's regex only matches ``href="name.html"`` exactly: a card promising
        ``wing/never.html`` or ``never.html#score`` is invisible to it."""
        music = self.tmp / "docs" / "music"
        (music / "index.html").write_text(
            "<html><body>"
            + CARD.format(tune="wired_tune", href="wing/never-landed.html")
            + CARD.format(tune="wired_tune", href="also-never-landed.html#score")
            + "</body></html>"
        )
        self.assertEqual(gate.dangling_links(self.tmp), [])

    # --- the live tree -------------------------------------------------------------------------
    def test_live_tree_is_clean(self):
        """The real repository: every piece on disk is reachable from the catalogue."""
        spec = importlib.util.spec_from_file_location(
            "live_music_gate", ROOT / "scripts" / "music_catalogue_unwired.py"
        )
        live = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(live)
        problems = live.report()
        self.assertEqual(problems, [], "music catalogue problems in the live tree:\n" + "\n".join(problems))

    # --- and the defect one level up: a gate nothing invokes ------------------------------------
    def test_gate_is_registered_in_ci(self):
        workflow = (ROOT / ".github" / "workflows" / "test-and-report.yml").read_text(encoding="utf-8")
        self.assertIn(
            "python3 tests/test_music_catalogue_unwired.py",
            workflow,
            "this test file is not registered in .github/workflows/test-and-report.yml — "
            "the gate would be written and never run, which is the defect it exists to catch",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
