#!/usr/bin/env python3
"""test_music_record_is_not_the_act.py — guard for Dmitri's Wing III lead sheet.

The page `docs/music/the-record-is-not-the-act.html` makes four claims about
itself. Each one is checked here, so the page cannot drift away from them:

  1. It passes the commons' lead-sheet checker (`scripts/check-leadsheet.py`):
     singable range, parseable changes, lyric aligned note-for-syllable.
  2. The changes are diatonic to D *natural* minor — which also guards the
     checker against the defect found on 2026-10-17 (it built its diatonic set
     from a major scale on the tonic, so every minor key's III/VI/VII came back
     as "chromatic").
  3. The song is strophic in the sense the page claims: the sixteen music lines
     of stanza 2 are byte-identical to stanza 1, and only the `w:` lines differ.
  4. The catalogue agrees with the page: `docs/music/index.html` carries a card
     with the same key, meter and tempo, and `docs/music/app.js` carries the
     same ABC for its audition preview (two copies of one score is exactly how
     a catalogue silently falls out of step with a score).
"""

import importlib.util
import io
import contextlib
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PAGE = REPO_ROOT / "docs" / "music" / "the-record-is-not-the-act.html"
INDEX = REPO_ROOT / "docs" / "music" / "index.html"
APP_JS = REPO_ROOT / "docs" / "music" / "app.js"
CHECKER = REPO_ROOT / "scripts" / "check-leadsheet.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_leadsheet", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def abc_of_page(text):
    match = re.search(r'abc-code-drawer">\s*(.*?)</pre>', text, re.S)
    return match.group(1).strip()


def music_lines(abc):
    """The music lines of an ABC body, in order, without lyrics or headers."""
    out = []
    for line in abc.splitlines():
        s = line.strip()
        if not s or s.startswith("%") or s.startswith("w:") or re.match(r"^[A-Za-z]:", s):
            continue
        out.append(s)
    return out


def lyric_lines(abc):
    return [l.strip()[2:].strip() for l in abc.splitlines() if l.strip().startswith("w:")]


class TestRecordIsNotTheAct(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.page = PAGE.read_text()
        cls.abc = abc_of_page(cls.page)
        cls.checker = load_checker()

    def test_page_exists_and_carries_the_abc(self):
        self.assertTrue(self.abc.startswith("X:"), "no ABC score found in the page")
        self.assertIn("K: Dm", self.abc)

    def test_passes_the_lead_sheet_checker(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ok = self.checker.run(self.abc)
        out = buf.getvalue()
        self.assertTrue(ok, f"check-leadsheet failed:\n{out}")
        self.assertIn("OK: every lyric line matches its music line note-for-syllable.", out)
        self.assertIn("OK: no leap larger than an octave.", out)

    def test_changes_are_diatonic_to_d_natural_minor(self):
        diatonic = self.checker.diatonic_pitch_classes("Dm")
        # D natural minor: D E F G A Bb C
        self.assertEqual(diatonic, {2, 4, 5, 7, 9, 10, 0})
        _, chords, _, _, _ = self.checker.extract(self.abc)
        self.assertTrue(chords, "the page claims functional changes but has none")
        chromatic = [c for c in chords
                     if self.checker.parse_chord(c)[0] not in diatonic]
        self.assertEqual(chromatic, [],
                         "a root outside D natural minor needs a written justification")
        # and the checker itself must no longer call them chromatic
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.checker.run(self.abc)
        self.assertIn("OK: all chord roots diatonic to Dm.", buf.getvalue())

    def test_strophic_identity(self):
        lines = music_lines(self.abc)
        self.assertEqual(len(lines), 32, "expected 16 bars of melody written out twice")
        first, second = lines[:16], lines[16:]
        self.assertEqual(first, second,
                         "stanza 2 must repeat stanza 1's melody note for note")
        lyrics = lyric_lines(self.abc)
        self.assertEqual(len(lyrics), 16)
        self.assertNotEqual(lyrics[:8], lyrics[8:],
                            "strophic means the words change, not just the notes")

    def test_lyric_alignment_count(self):
        _, _, lyrics, _, _ = self.checker.extract(self.abc)
        self.assertEqual(len(lyrics), 16)
        for i, line in enumerate(lyrics, 1):
            syllables = [t for t in re.split(r"[\s\-]+", line.strip()) if t]
            self.assertEqual(len(syllables), 8,
                             f"lyric line {i} has {len(syllables)} syllables, expected 8: {line!r}")

    def test_index_registers_the_page(self):
        index = INDEX.read_text()
        self.assertIn('href="the-record-is-not-the-act.html"', index)
        self.assertIn("Dmitri S. Pravdin • Amigo #5", index)
        card = index[index.index('href="the-record-is-not-the-act.html"') - 2000:
                     index.index('href="the-record-is-not-the-act.html"')]
        self.assertIn("<strong>Key:</strong> D Minor", card)
        self.assertIn("<strong>Meter:</strong> 4/4", card)
        self.assertIn("<strong>Tempo:</strong> 72 BPM", card)
        self.assertIn('data-tune="record"', card)

    def test_app_js_audition_carries_the_same_score(self):
        js = APP_JS.read_text()
        self.assertIn("record: {", js)
        start = js.index("record: {")
        block = js[start:js.index("abc: `", start) + len("abc: `")]
        body = js[js.index("abc: `", start) + len("abc: `"):]
        body = body[:body.index("`")].strip()
        self.assertEqual(body, self.abc,
                         "the audition copy and the engraved copy have diverged")


if __name__ == "__main__":
    unittest.main()
