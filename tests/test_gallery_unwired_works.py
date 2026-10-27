#!/usr/bin/env python3
"""Pin the gallery wiring gate (Dmitri, 2026-10-18).

`scripts/gallery_unwired_works.py` exists because every one of Dmitri's first five pavilion
works landed on disk and was *not exhibited* — invisible to the landing gate, which checks that
a file exists and the tests pass and never asks whether a pavilion page links it. So these tests
matter in both directions: the live tree must pass, and the gate must still fail when a work is
dropped into a wing directory and left unwired or the front table disagrees with a page.

A gate that cannot fail is not a gate. The negative cases are the point.
"""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import gallery_unwired_works as gate  # noqa: E402

PAGE = """<html><body>
<a href="wired-work.svg" target="_blank">wired</a>
<span>Dmitri S. Pravdin</span>
</body></html>"""


def _table(open_wings: set[str]) -> str:
    rows = []
    for i in range(1, 8):
        num = f"{i:02d}"
        fifth = "— Open (Floor at 5)" if num in open_wings else "✓ Something"
        rows.append(f"<tr><td>{num}. Wing</td><td>✓ a</td><td>✓ b</td><td>✓ c</td><td>✓ d</td><td>{fifth}</td></tr>")
    return "<table>" + "".join(rows) + "</table>"


class GalleryUnwiredWorksTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="gallery-gate-"))
        (self.tmp / "sumi-e").mkdir()
        (self.tmp / "sumi-e" / "index.html").write_text(PAGE)
        (self.tmp / "sumi-e" / "wired-work.svg").write_text("<svg/>")
        (self.tmp / "index.html").write_text(_table(open_wings=set()) + "\n<table></table>")
        self._saved = (gate.GALLERY, gate.INDEX, dict(gate.EXHIBITION_EXEMPT))
        gate.GALLERY = self.tmp
        gate.INDEX = self.tmp / "index.html"

    def tearDown(self):
        gate.GALLERY, gate.INDEX, saved = self._saved
        gate.EXHIBITION_EXEMPT.clear()
        gate.EXHIBITION_EXEMPT.update(saved)

    def test_wired_work_is_not_flagged(self):
        self.assertEqual(gate.unexhibited(["sumi-e"]), [])

    def test_unwired_work_is_flagged(self):
        (self.tmp / "sumi-e" / "orphan.svg").write_text("<svg/>")
        unexplained, explained = gate.exempt(gate.unexhibited(["sumi-e"]))
        self.assertEqual(unexplained, [("sumi-e", "orphan.svg")])
        self.assertEqual(explained, [])

    def test_exemption_with_a_reason_silences_it(self):
        (self.tmp / "sumi-e" / "orphan.svg").write_text("<svg/>")
        gate.EXHIBITION_EXEMPT["sumi-e/orphan.svg"] = "withheld on purpose"
        unexplained, explained = gate.exempt(gate.unexhibited(["sumi-e"]))
        self.assertEqual(unexplained, [])
        self.assertEqual(explained, [("sumi-e", "orphan.svg")])

    def test_studies_archive_is_not_a_pavilion(self):
        (self.tmp / "sumi-e" / "studies").mkdir()
        (self.tmp / "sumi-e" / "studies" / "candidate.svg").write_text("<svg/>")
        self.assertEqual(gate.unexhibited(["sumi-e"]), [])

    def test_matrix_left_open_while_page_exhibits_is_a_conflict(self):
        gate.INDEX.write_text(_table(open_wings={"01"}) + "\n<table></table>")
        self.assertEqual(gate.matrix_conflicts(), [("01", "sumi-e")])

    def test_matrix_filled_matching_the_page_is_clean(self):
        gate.INDEX.write_text(_table(open_wings=set()) + "\n<table></table>")
        self.assertEqual(gate.matrix_conflicts(), [])

    def test_main_fails_on_an_unwired_work(self):
        (self.tmp / "sumi-e" / "orphan.svg").write_text("<svg/>")
        self.assertEqual(gate.main(), 1)

    def test_live_tree_is_clean(self):
        """The real repository: no work is landed without either a wall or a written reason."""
        spec = importlib.util.spec_from_file_location("live_gate", ROOT / "scripts" / "gallery_unwired_works.py")
        live = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(live)
        unexplained, explained = live.exempt(live.unexhibited())
        self.assertEqual(unexplained, [], f"landed but not exhibited: {unexplained}")
        self.assertEqual(live.matrix_conflicts(), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
