#!/usr/bin/env python3
"""test_songbook_source_sync.py — a score on disk and the score the player plays are one score.

Written 2026-11-02 (Dmitri) while reading Tarik's *The Small Repair*
(`codex-20261017T080313Z-a4868124`). The reading found the three copies in agreement and found
that **nothing in the repository would have said so if they had not been**: `docs/music/*.abc`
is the source of truth for four published pieces, the player carries its own copy of every score
as a template literal in `docs/music/app.js`, and each page carries a third. A source file that
drifts from the player is a slow, silent defect — the file says one thing, the page sings
another, and the only people who would notice are the ones who already read both.

So the check is on the music, not on the bytes. Three findings shaped it, all measured here:

1. **Bytes are the wrong unit.** `docs/music/the-even-tide.abc` differs from its player block
   only by the `% ===== mm 1-4 … =====` rehearsal comments, i.e. not at all. A byte comparison
   would be red on a file that is right, and a check that is red for a correct file teaches the
   landing gate to ignore red. Comments and blank lines are therefore stripped before comparing.

2. **`X:` is not a key.** Two different scores in `app.js` both declare `X: 8`, so the file is
   matched to *any* block with the same number and the music decides.

3. **An unreachable score is a different fault, and it is already tracked elsewhere.**
   `scripts/music_catalogue_unwired.py` owns the question "can a reader reach this piece", with
   `KNOWN_DARK` naming the scores that are on disk with no page, card or player key. This test
   asserts that same set, so that a *new* unreachable score fails here too, and fixing a known
   one fails until the list is corrected — a known-answer list that never has to be edited is a
   list nobody is reading.

Separate and not asserted as a fault: `the-even-tide.abc` has a player block and no page. The
piece is reachable through the player, so `music_catalogue_unwired.py` is right not to call it
dark; what it lacks is a page and a catalogue card. It is listed here so that the distinction
between "unreachable" and "half-built" is written down rather than inferred.
"""

import re
import unittest
from pathlib import Path

MUSIC = Path(__file__).resolve().parent.parent / "docs" / "music"

# The scores on disk that no reader can reach: no page, no catalogue card, no player key.
# Kept in step with KNOWN_DARK in scripts/music_catalogue_unwired.py, which owns the reason and
# the owner for each. A name leaving this set is good news and should edit this line.
KNOWN_DARK = {"between-wakings.abc", "the-unlogged-hour.abc"}

# Scores that play but have no page of their own yet: reachable, half-built.
BLOCK_BUT_NO_PAGE = {"the-even-tide.abc"}


def music_lines(text):
    """The notes, without the furniture: ABC comment lines and blank lines dropped."""
    return [ln.rstrip() for ln in text.splitlines()
            if ln.strip() and not ln.lstrip().startswith("%")]


def abc_number(text):
    m = re.search(r"^X:\s*(\d+)", text, re.M)
    return int(m.group(1)) if m else None


def player_blocks():
    app = (MUSIC / "app.js").read_text(encoding="utf-8")
    return re.findall(r"abc: `(.*?)`", app, re.S)


def source_files():
    return sorted(MUSIC.glob("*.abc"))


class SongbookSync(unittest.TestCase):
    def setUp(self):
        self.blocks = player_blocks()
        self.assertGreater(len(self.blocks), 10, "app.js should carry the player's scores")

    def test_no_source_file_is_lost(self):
        """Every .abc on disk is either played or on the known-dark list — nothing in between."""
        missing = []
        for path in source_files():
            number = abc_number(path.read_text(encoding="utf-8"))
            same_number = [b for b in self.blocks if abc_number(b) == number]
            mine = music_lines(path.read_text(encoding="utf-8"))
            if not any(music_lines(b) == mine for b in same_number):
                missing.append(path.name)
        self.assertEqual(sorted(missing), sorted(KNOWN_DARK),
                         "a .abc file with no player block is a score no reader can hear; "
                         "either wire it into docs/music/app.js or name it in KNOWN_DARK here "
                         "and in scripts/music_catalogue_unwired.py")

    def test_the_music_agrees_with_the_file(self):
        """Where a file is played, the player plays exactly what the file says."""
        mismatched = []
        for path in source_files():
            if path.name in KNOWN_DARK:
                continue
            number = abc_number(path.read_text(encoding="utf-8"))
            mine = music_lines(path.read_text(encoding="utf-8"))
            candidates = [b for b in self.blocks if abc_number(b) == number]
            matches = [b for b in candidates if music_lines(b) == mine]
            if len(matches) != 1:
                mismatched.append((path.name, len(matches)))
        self.assertEqual(mismatched, [],
                         "each source file must equal exactly one player block after comments "
                         "are stripped; 0 means the file and the player disagree, 2+ means two "
                         "player blocks claim the same X: and the same music")

    def test_pages_still_match_their_files(self):
        """A piece with a page: the page's own copy must be the file's music too."""
        problems = []
        for path in source_files():
            if path.name in KNOWN_DARK:
                continue
            page = path.with_suffix(".html")
            if not page.exists():
                if path.name not in BLOCK_BUT_NO_PAGE:
                    problems.append(f"{path.name}: no page")
                continue
            if not any(music_lines(b) == music_lines(path.read_text(encoding="utf-8"))
                       for b in self.blocks
                       if abc_number(b) == abc_number(path.read_text(encoding="utf-8"))):
                problems.append(f"{path.name}: no matching player block")
        self.assertEqual(problems, [])

    def test_the_half_built_list_is_honest(self):
        """BLOCK_BUT_NO_PAGE names the scores that play but cannot be read as a page."""
        measured = {p.name for p in source_files()
                    if not p.with_suffix(".html").exists() and p.name not in KNOWN_DARK}
        self.assertEqual(measured, BLOCK_BUT_NO_PAGE,
                         "a score that gained or lost its page should edit BLOCK_BUT_NO_PAGE")


if __name__ == "__main__":
    unittest.main(verbosity=2)
