#!/usr/bin/env python3
"""The counterpoint checker must read a score before it calls it clean.

Found 2026-10-31, in the wake after the lead-sheet checker turned out to be
grading two-voice keyboard pieces as if they were songs. The same wing, the
same shape of fault, in the other instrument:

`scripts/check-counterpoint.py` understood exactly one way of naming a voice —
the inline `[V:n]` tag at the start of each physical line. Three of the six
scores in `docs/music/` declare their voices the other legal way, with a `V: 1`
header line, and those three produced no voices at all. The function returned
False and the caller turned that into `sys.exit(0)`, so the output was:

    No [V:n] voices found — nothing to check.        (exit 0)

Half the wing was reported as clean because the checker was blind to it. The
fix reads the declaration form, skips body-level fields (`w:` lyric lines are
full of letters A-G and were parsed as pitches), and answers in three states:
0 pass, 1 a violation, 2 could not check — the same three states the lead-sheet
checker adopted the day before, for the same reason.
"""
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check-counterpoint.py"
spec = importlib.util.spec_from_file_location("check_counterpoint_voices", SCRIPT)
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)

# Two voices written the declaration way, with a planted parallel fifth: both
# voices step up together while a fifth apart (C4/F3 -> D4/G3).
DECLARED_WITH_PARALLEL_FIFTH = """X: 1
T: planted fifth
M: 4/4
L: 1/8
K: C
V: 1 clef=treble
C4 D4 |
V: 2 clef=bass
F,4 G,4 |
"""

# The same music, one voice, declared the declaration way.
DECLARED_SINGLE_VOICE = """X: 2
T: one voice
M: 4/4
L: 1/8
K: C
V: 1 clef=treble
C4 G4 | D4 A4 |
"""

# A melody with a lyric line under it. The words are full of A-G letters; none
# of them may become a note.
WITH_LYRICS = """X: 3
T: lyric
M: 4/4
L: 1/8
K: C
V: 1 clef=treble
C4 G4 | D4 A4 |
w: A decade of faded cabbage, a bee
w: edg
"""


class ExtractVoicesReadsBothLayouts(unittest.TestCase):
    def test_inline_tags_still_work(self):
        abc = "L: 1/8\nK: C\n[V:1] C4 D4 |\n[V:2] C,4 D,4 |\n"
        order, voices = cp.extract_voices(abc)
        self.assertEqual(order, ['1', '2'])
        self.assertEqual(len(voices['1']), 3)  # note, note, bar

    def test_declaration_form_is_now_read(self):
        order, voices = cp.extract_voices(DECLARED_SINGLE_VOICE)
        self.assertEqual(order, ['1'])
        self.assertTrue(voices['1'], "a V: header must start a voice, not vanish")

    def test_declaration_form_keeps_voices_apart(self):
        order, voices = cp.extract_voices(DECLARED_WITH_PARALLEL_FIFTH)
        self.assertEqual(order, ['1', '2'])
        pitches_1 = [m for k, m, _ in voices['1'] if k == 'note']
        pitches_2 = [m for k, m, _ in voices['2'] if k == 'note']
        self.assertEqual(pitches_1, [60, 62])
        self.assertEqual(pitches_2, [53, 55])


class ThreeStates(unittest.TestCase):
    def test_declared_parallel_fifth_is_caught(self):
        self.assertEqual(cp.run_checks(DECLARED_WITH_PARALLEL_FIFTH), 'fail')

    def test_single_voice_is_unchecked_not_pass(self):
        self.assertEqual(cp.run_checks(DECLARED_SINGLE_VOICE), 'unchecked')

    def test_no_voices_at_all_is_unchecked_not_pass(self):
        self.assertEqual(cp.run_checks("K: C\nC4 D4 E4 F4 |\n"), 'unchecked')

    def test_self_test_still_passes(self):
        statuses = [cp.run_checks(abc) for abc in cp.SELF_TEST_PIECES.values()]
        self.assertEqual(statuses, ['pass'])


class LyricsAreNotNotes(unittest.TestCase):
    def test_lyric_line_adds_no_pitches(self):
        _, clean = cp.extract_voices(DECLARED_SINGLE_VOICE)
        _, sung = cp.extract_voices(WITH_LYRICS)
        self.assertEqual(
            [m for k, m, _ in sung['1'] if k == 'note'],
            [m for k, m, d in clean['1'] if k == 'note'],
        )


class TheWingItself(unittest.TestCase):
    """No score in docs/music/ may come out "clean" without being read."""

    def test_every_score_is_either_judged_or_declared_unchecked(self):
        pieces = sorted((ROOT / "docs" / "music").glob("*.abc"))
        self.assertGreaterEqual(len(pieces), 6)
        for piece in pieces:
            with self.subTest(piece=piece.name):
                order, voices = cp.extract_voices(piece.read_text())
                self.assertTrue(order, f"{piece.name}: no voices found at all")
                status = cp.run_checks(piece.read_text())
                self.assertIn(status, ('pass', 'fail', 'unchecked'))
                # The old bug: a file could not be read and still exit 0.
                if status == 'unchecked':
                    self.assertLess(
                        len([v for v in order if voices[v]]), 2,
                        f"{piece.name}: unchecked for a reason other than being monophonic",
                    )

    def test_exit_codes(self):
        cases = [
            (DECLARED_WITH_PARALLEL_FIFTH, 1),
            (DECLARED_SINGLE_VOICE, 2),
            (cp.SELF_TEST_PIECES["claude (invention)"], 0),
        ]
        import tempfile
        for abc, expected in cases:
            with tempfile.NamedTemporaryFile('w', suffix='.abc', delete=False) as fh:
                fh.write(abc)
                path = fh.name
            proc = subprocess.run([sys.executable, str(SCRIPT), path],
                                  capture_output=True, text=True)
            self.assertEqual(proc.returncode, expected,
                             f"{expected} expected, got {proc.returncode}:\n{proc.stdout}")


if __name__ == '__main__':
    unittest.main()
