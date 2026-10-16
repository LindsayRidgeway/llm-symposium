#!/usr/bin/env python3
"""tests/test_leadsheet_checker.py — pins the octave the lead-sheet checker measures on.

`scripts/check-leadsheet.py` compares a melody against an ABSOLUTE vocal compass
(MIDI 55..79, G3..G5) — unlike the two counterpoint checkers, which only ever read
intervals between voices and are indifferent to where the pitch axis is anchored.

Until 2026-10-16 its pitch parser anchored ABC one octave low:

    midi = 60 + BASE[letter] - 12 + ...

The `- 12` was harmless in the file it was copied from (`scripts/check-counterpoint.py`),
which reads intervals only. Here it is load-bearing, so every green "singable range"
result the Conservatory published was measured one octave *below* the pitch that
actually sounds — and the same ABC is read at concert pitch by the browser synth
(`docs/music/app.js`, `parseAbcPitch`: "Note 'C' (octave 0) is C4 (MIDI 60) ...
'c' is C5 (MIDI 72), 'c'' is C6 (MIDI 84)") and by the canonical counterpoint checker
(`scripts/check_music_rules.py`: "C = C4 (60), c = C5 (72)").

These tests pin the anchor and both sides of the consequence: a melody genuinely written
inside the untrained compass must pass, and the same shape written an octave above it
must fail *on the range clause*. Every sample below carries a lyric whose syllable count
equals its note count, so a test can never pass because of an alignment failure wearing
a range failure's clothes.

Written 2026-10-16 (Dmitri, run 20261016T090958Z-c1220121).
"""

import contextlib
import importlib.util
import io
import pathlib
import unittest

REPO = pathlib.Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location(
    "check_leadsheet", REPO / "scripts" / "check-leadsheet.py")
_checker = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_checker)


def _report(abc_text):
    """Run the checker's report on `abc_text`; return (passed, printed_output)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        passed = _checker.run(abc_text)
    return passed, buf.getvalue()


def _pitches(abc_text):
    notes, _chords, _lyrics, _key, _meter = _checker.extract(abc_text)
    return [m for m, _d in notes]


class TestOctaveAnchor(unittest.TestCase):
    """The ABC pitch axis must be the standard one the engraver and synth use."""

    ANCHOR_ABC = """X: 1
T: anchor
M: 4/4
L: 1/8
K: C
C8 | c8 | c'8 | C,8 | g8 |]
"""

    def test_pitch_axis_is_standard_abc(self):
        # C = middle C = C4 = 60; c = C5 = 72; c' = C6 = 84; C, = C3 = 48; g = G5 = 79.
        self.assertEqual(_pitches(self.ANCHOR_ABC), [60, 72, 84, 48, 79])

    def test_names_reported_are_the_sounding_octave(self):
        self.assertEqual(_checker.name_of(60), "C4")
        self.assertEqual(_checker.name_of(72), "C5")
        self.assertEqual(_checker.name_of(84), "C6")


class TestAbsoluteCompass(unittest.TestCase):
    """The range check is only meaningful if the axis is the sounding one."""

    # Written G3..G4 ("G," .. "G"): sounds G3..G4, span 12, genuinely inside G3..G5.
    IN_COMPASS = """X: 1
T: in-compass
M: 4/4
L: 1/8
K: C
"C" G,2 A,2 B,2 C2 | "G" D2 E2 F2 G2 | "C" C8 |]
w: this is in the com- pass for a voice
"""

    # The same shape written an octave above: sounds G5..G6 (79..91), outside the compass.
    ABOVE_COMPASS = """X: 1
T: above-compass
M: 4/4
L: 1/8
K: C
"C" g2 a2 b2 c'2 | "G" d'2 e'2 f'2 g'2 | "C" c'8 |]
w: this is a- bove the com- pass to sing
"""

    # C4 up to C5, span 12: fits, so this one must pass and prove the samples are comparable.
    def test_melody_inside_the_compass_passes(self):
        passed, out = _report(self.IN_COMPASS)
        self.assertIn("OK: every lyric line matches its music line note-for-syllable", out)
        self.assertIn("OK: inside absolute range", out)
        self.assertTrue(passed)
        # Before the octave fix this read G2..G3 and was rejected as out of range.
        self.assertEqual(min(_pitches(self.IN_COMPASS)), 55)
        self.assertEqual(max(_pitches(self.IN_COMPASS)), 67)

    def test_melody_an_octave_above_the_compass_fails_on_the_range_clause(self):
        passed, out = _report(self.ABOVE_COMPASS)
        # The lyric is aligned, so the ONLY thing that can fail it is the range.
        self.assertIn("OK: every lyric line matches its music line note-for-syllable", out)
        self.assertIn("FAIL: sits outside absolute range [G3, G5]", out)
        self.assertFalse(passed)
        self.assertEqual(min(_pitches(self.ABOVE_COMPASS)), 79)
        self.assertEqual(max(_pitches(self.ABOVE_COMPASS)), 91)

    def test_the_checker_still_catches_an_unsingable_span(self):
        wide = """X: 1
T: wide
M: 4/4
L: 1/8
K: C
"C" C2 D2 E2 F2 | "C" G,2 A,2 B,2 C2 | "C" C8 |]
w: this will not fit a voice at all here
"""
        passed, out = _report(wide)
        self.assertIn("FAIL: span", out)
        self.assertFalse(passed)


if __name__ == '__main__':
    unittest.main()
