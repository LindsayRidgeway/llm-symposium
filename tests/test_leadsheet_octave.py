#!/usr/bin/env python3
"""The lead-sheet checker must measure pitches the way the page plays them.

Regression guard for a defect found by hand on 2026-10-16 and fixed on 2026-10-17:
`scripts/check-leadsheet.py` computed melody pitches as `60 + BASE[letter] - 12`,
one octave below ABC's own convention (and below `docs/music/app.js`, which states
it in a comment: 'C' is C4 = MIDI 60, 'c' is C5 = 72, 'C,' is C3 = 48).

Consequence of the bug, measured: every delivered lead sheet passed the absolute
range check an octave lower than the pitch abcjs actually renders, so the range
claims printed on the pages were wrong by twelve semitones.
"""
import contextlib
import importlib.util
import io
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/check-leadsheet.py"
spec = importlib.util.spec_from_file_location("check_leadsheet", SCRIPT)
ls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ls)


def pitch(abc):
    notes, _, _, _, _ = ls.extract(abc)
    return [m for m, _ in notes]


def verdict(abc_text):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ok = ls.run(abc_text)
    return ok, buf.getvalue()


def page_abc(rel_path):
    text = (ROOT / rel_path).read_text()
    m = re.search(r'<pre class="abc-code-drawer">(.*?)</pre>', text, re.S)
    assert m, f"no ABC block in {rel_path}"
    return re.sub(r'<[^>]+>', '', m.group(1))


class OctaveTests(unittest.TestCase):
    def test_middle_c_is_midi_60(self):
        self.assertEqual(pitch("K:C\nL:1/4\nC D E F |"), [60, 62, 64, 65])

    def test_abc_octave_convention_matches_app_js(self):
        # app.js: "'C' is C4 (MIDI 60); 'C,' is C3 (MIDI 48); 'c' is C5 (MIDI 72);
        # 'c'' is C6 (MIDI 84)"
        self.assertEqual(pitch("X:1\nK:C\nL:1/4\nC, C c c' |"), [48, 60, 72, 84])

    def test_key_signature_applies_to_melody(self):
        # In K:D the written F and C are F# and C#, as abcjs renders them.
        self.assertEqual(pitch("X:1\nK:D\nL:1/4\nF C |"), [66, 61])

    def test_high_song_fails_the_absolute_range(self):
        # Gemini's *Before the Embers Cool* as written sits G4-C6: a span that fits a
        # 12th but an octave above an untrained voice. The old offset passed it.
        abc = page_abc("docs/music/before-the-embers-cool.html")
        ok, out = verdict(abc)
        self.assertIn("C6", out)
        self.assertNotIn("lowest  G3", out)
        self.assertFalse(ok, "a G4-C6 melody must not pass the singable-range check")

    def test_the_cairn_sits_where_its_page_claims(self):
        # The page claims D4-C#5; the ABC must actually measure that.
        ok, out = verdict(page_abc("docs/music/the-cairn.html"))
        self.assertIn("lowest  D4 (MIDI 62)", out)
        self.assertIn("highest C#5 (MIDI 73)", out)
        self.assertTrue(ok, out)

    def test_self_test_fixture_still_passes(self):
        ok, out = verdict(ls.SELF_TEST)
        self.assertTrue(ok, out)


if __name__ == "__main__":
    unittest.main()
