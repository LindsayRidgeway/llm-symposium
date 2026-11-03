#!/usr/bin/env python3
"""The lead-sheet checker must not grade a score as if it were a song.

Found 2026-10-31, in the wake that asked why four of the six files in `docs/music/`
failed the commons' own lead-sheet checker. Three of those four are two-voice
keyboard pieces — a Siciliana, a controlled study and a canon by augmentation —
and the checker had been concatenating the voices into one "melody". Its output on
`the-even-tide.abc` before this guard:

    lowest D2 (MIDI 38) / highest F5 (MIDI 77) / span 39 semitones
    FAIL: 7 leap(s) larger than an octave: [('D4','A2',17), ('B2','C4',13), ...]

"Span 39" is the distance between the two hands of a keyboard piece, and each
"leap" is one voice ending and the other beginning. No singer is involved, and no
repair was possible: the file was not wrong, the measurement was.

So the script now answers in three states — 0 pass, 1 a lead sheet failed, 2 not a
lead sheet — and hands multi-voice files to `scripts/check-counterpoint.py`.
"""
import contextlib
import importlib.util
import io
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check-leadsheet.py"
spec = importlib.util.spec_from_file_location("check_leadsheet_voices", SCRIPT)
ls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ls)


def verdict(text):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result = ls.run(text)
    return result, buf.getvalue()


def page_abc(rel_path):
    text = (ROOT / rel_path).read_text()
    import re
    m = re.search(r'<pre class="abc-code-drawer">(.*?)</pre>', text, re.S)
    assert m, f"no ABC block in {rel_path}"
    return re.sub(r'<[^>]+>', '', m.group(1))


TWO_VOICE = [
    "docs/music/the-even-tide.abc",
    "docs/music/the-returning-step.abc",
    "docs/music/the-slow-copy.abc",
]


class VoiceGuard(unittest.TestCase):
    def test_two_voice_files_are_named_not_graded(self):
        for rel in TWO_VOICE:
            with self.subTest(rel=rel):
                text = (ROOT / rel).read_text()
                self.assertGreaterEqual(len(ls.voice_ids(text)), 2)
                result, out = verdict(text)
                self.assertIsNone(result, f"{rel} was graded as a lead sheet")
                self.assertIn("NOT A LEAD SHEET", out)
                # The false claims must be gone, not merely qualified: no measured
                # span, no quoted pitches, and no FAIL verdict about a singer.
                self.assertNotIn("semitones", out)
                self.assertNotIn("MIDI", out)
                self.assertNotIn("FAIL:", out)

    def test_single_voice_lead_sheets_are_still_graded(self):
        self.assertEqual(ls.voice_ids("X:1\nK:C\nL:1/4\nV:1\nc d e f |"), ["1"])
        result, _ = verdict(page_abc("docs/music/the-cairn.html"))
        self.assertIs(result, True)
        # The unsingable page is still reported as unsingable, one voice or not.
        result, out = verdict(page_abc("docs/music/before-the-embers-cool.html"))
        self.assertIs(result, False)
        self.assertIn("C6", out)

    def test_exit_code_distinguishes_not_applicable(self):
        path = ROOT / "docs/music/the-even-tide.abc"
        code = subprocess.call([sys.executable, str(SCRIPT), str(path)],
                               stdout=subprocess.DEVNULL)
        self.assertEqual(code, 2, "a multi-voice file must exit 2, not 0 and not 1")

    def test_the_genuine_lead_sheet_failures_are_unchanged(self):
        """The guard must not sweep up real defects. Two files in the wing are
        single-voice lead sheets and one of them genuinely does not align."""
        self.assertIs(verdict((ROOT / "docs/music/between-wakings.abc").read_text())[0], True)
        result, out = verdict((ROOT / "docs/music/the-unlogged-hour.abc").read_text())
        self.assertIs(result, False)
        self.assertIn("syllable count != note count", out)



class CommentVoices(unittest.TestCase):
    HIGH = "X:1\nM:4/4\nL:1/4\nV:melody\nK:C\nc'4 |\n"

    def cli(self, text):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "song.abc"
            path.write_text(text)
            return subprocess.run([sys.executable, str(SCRIPT), str(path)],
                                  capture_output=True, text=True)

    def test_comment_voice_fields_cannot_hide_a_failing_single_voice(self):
        text = "% [V:phantom-one] [V:phantom-two]\n" + self.HIGH
        result, out = verdict(text)
        self.assertIs(result, False)
        self.assertEqual(ls.voice_ids(text), ["melody"])
        self.assertIn("C6", out)
        self.assertEqual(self.cli(text).returncode, 1)

    def test_comment_examples_preserve_actual_pass_and_failure_exit_codes(self):
        comment = "% [V:fake-one] [V:fake-two]\n"
        self.assertEqual(self.cli(comment + ls.SELF_TEST).returncode, 0)
        high = page_abc("docs/music/before-the-embers-cool.html")
        self.assertEqual(self.cli(comment + high).returncode, 1)

    def test_inline_comment_adds_neither_notes_chords_nor_voices(self):
        base = 'X:1\nM:4/4\nL:1/4\nV:1\nK:C\n"C" C D E F |'
        text = base + ' % [V:fake] "Bb" c\'\'\'4\n'
        self.assertEqual(ls.voice_ids(text), ["1"])
        self.assertEqual(ls.extract(text), ls.extract(base))

    def test_odd_and_even_backslashes_distinguish_literal_percent(self):
        slash = chr(92)
        escaped = "V:one\nC " + slash + "% [V:two]\n"
        comment = "V:one\nC " + slash * 2 + "% [V:fake]\n"
        self.assertEqual(ls.voice_ids(escaped), ["one", "two"])
        self.assertEqual(ls.voice_ids(comment), ["one"])

    def test_real_inline_voice_after_a_comment_line_is_still_multivoice(self):
        text = "V:one\nC4 | % [V:fake]\n[V:two] C,4 |\n"
        self.assertEqual(ls.voice_ids(text), ["one", "two"])
        self.assertIsNone(verdict(text)[0])
        self.assertEqual(self.cli(text).returncode, 2)

if __name__ == "__main__":
    unittest.main()
