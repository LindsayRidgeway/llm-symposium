#!/usr/bin/env python3
"""The lead-sheet checker must read a key's mode, not just its tonic.

Regression guard for a defect found by Dmitri's run `20261017T031231Z-7fbc0298`
(the finding was raised in that run's report; the fix landed 2026-10-17) and
measured by hand on the wing's own files:

`scripts/check-leadsheet.py` section 2 built its diatonic pitch classes from the
*major* scale on the tonic, whatever mode the `K:` field named. So:

  - `K: Gmix` (`docs/music/bounded-frontier.html`) had its plain tonic seventh
    `F` reported as "chromatic to Gmix" — F natural is the whole point of G
    mixolydian;
  - a minor-key lead sheet would have had four of its seven scale degrees
    (the third, fourth, sixth and seventh) called chromatic, and the ordinary
    major dominant of a minor cadence along with them.

The mode's own scale is now used, and in minor modes the raised seventh (the
harmonic-minor leading tone) is admitted as well.
"""
import contextlib
import importlib.util
import io
import html
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check-leadsheet.py"
spec = importlib.util.spec_from_file_location("check_leadsheet_modes", SCRIPT)
ls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ls)

MAJOR = {0, 2, 4, 5, 7, 9, 11}          # C major
GMIX = {7, 9, 11, 0, 2, 4, 5}           # G A B C D E F
AMIN = {9, 11, 0, 2, 4, 5, 7, 8}        # A B C D E F G + G# (leading tone)
DDOR = {2, 4, 5, 7, 9, 11, 0}           # D E F G A B C


class TestKeyMode(unittest.TestCase):

    def test_mode_is_read_from_the_suffix(self):
        self.assertEqual(ls.key_mode("Gmix"), "mix")
        self.assertEqual(ls.key_mode("Ador"), "dor")
        self.assertEqual(ls.key_mode("Dm"), "m")
        self.assertEqual(ls.key_mode("Eb"), "major")
        self.assertEqual(ls.key_mode("  f  "), "major")

    def test_major_key_unchanged(self):
        self.assertEqual(ls.diatonic_pcs("C"), MAJOR)
        self.assertEqual(ls.diatonic_pcs("F"), {5, 7, 9, 10, 0, 2, 4})

    def test_mixolydian_admits_its_own_seventh(self):
        pcs = ls.diatonic_pcs("Gmix")
        self.assertEqual(pcs, GMIX)
        self.assertIn(5, pcs)            # F natural — the mode's signature note
        self.assertNotIn(6, pcs)         # F# is genuinely outside

    def test_dorian_admits_its_own_sixth(self):
        self.assertEqual(ls.diatonic_pcs("Ddor"), DDOR)
        self.assertIn(11, ls.diatonic_pcs("Ddor"))   # B natural, not Bb

    def test_minor_admits_its_flat_third_and_leading_tone(self):
        pcs = ls.diatonic_pcs("Am")
        self.assertEqual(pcs, AMIN)
        for pc in (0, 2, 5, 7):          # C, D, F, G: the "wrong" four under the old code
            self.assertIn(pc, pcs)
        self.assertIn(8, pcs)            # G#: harmonic-minor leading tone
        self.assertNotIn(1, pcs)         # C# is genuinely outside A minor
        self.assertNotIn(3, pcs)         # Eb too

    def test_chromatic_chord_is_still_flagged_in_a_mode(self):
        """A mode's kindness must not become blindness."""
        abc = "\n".join([
            "X: 1", "T: modal flag", "M: 4/4", "L: 1/4", "K: Gmix",
            '"G" G2 "F" F2 | "Eb" E2 "D" D2 |',
        ])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            ls.run(abc, verbose=False)
        printed = out.getvalue()
        self.assertIn("chromatic to Gmix", printed)
        self.assertIn("Eb", printed)
        self.assertNotIn("['F'", printed)

    def test_the_wings_own_mixolydian_page_is_clean(self):
        """`docs/music/bounded-frontier.html` (K: Gmix) had one false alarm; it has none now."""
        page = ROOT / "docs" / "music" / "bounded-frontier.html"
        if not page.exists():
            self.skipTest("page not present in this checkout")
        m = re.search(r'<pre class="abc-code-drawer">(.*?)</pre>', page.read_text(), re.S)
        if not m:
            self.skipTest("no ABC block on the page")
        abc = html.unescape(m.group(1))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            ls.run(abc, verbose=False)
        printed = out.getvalue()
        self.assertNotIn("chromatic to Gmix", printed,
                         "G mixolydian's own seventh was reported as chromatic again")


if __name__ == "__main__":
    unittest.main()
