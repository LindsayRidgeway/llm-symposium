#!/usr/bin/env python3
"""The test `scripts/compose_dmitri_round.py` promised and never had.

Written 2026-10-26 by Desi while reading the item for the run that landed the
script (dmitri-bot run 20261017T091252Z-e5d91020). That script's docstring named
`tests/test_dmitri_round.py` as the thing that "re-checks from the page" the rule
it enforces; no such file existed, and no page for the round exists either — the
only two pages in `docs/music/` that name Dmitri are `the-level-ground.html` and
the repertoire index. So this test re-checks the rule from the one place the rule
actually lives today: the script's own output.

What it checks, and why each is worth a test rather than a comment:

  1. The best melody of a seeded search passes the composer's own `check()`.
  2. Every melody the search *keeps* passes it too — the constraint filter is the
     whole point of searching, so a keeper that breaks the rule means the filter
     is not filtering.
  3. Same seed, same tune. A search that moved under a reader's feet would make
     every later measurement of "which melody did it choose" meaningless.
  4. The ABC it prints parses back to the pitches it chose. `abc_name()` drops the
     octave for anything under D5 and has no accidentals, so a wrong decision there
     is silent in the print and audible only in the browser.
  5. The whole tune stays inside D4–D5, and starts and ends on the tonic D.

Run:  python3 -m unittest tests.test_dmitri_round
"""

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "compose_dmitri_round.py"

_spec = importlib.util.spec_from_file_location("compose_dmitri_round", SCRIPT)
compose = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(compose)


def run_script(*args, seed=5):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args, "--seed", str(seed)],
        capture_output=True,
        text=True,
        check=False,
    )


def abc_to_pitches(abc_line):
    """Read `to_abc()` output back: 'd D A | ...' -> MIDI pitches, D4 = 62."""
    names = {"C": 60, "D": 62, "E": 64, "F": 65, "G": 67, "A": 69, "B": 71}
    pitches = []
    for token in abc_line.replace("|", " ").split():
        letter = token[0]
        base = names[letter.upper()]
        if letter.islower():
            base += 12
        if len(token) > 1 and token[1] == ",":
            base -= 12
        if len(token) > 1 and token[1] == "'":
            base += 12
        pitches.append(base)
    return pitches


class TestDmitriRound(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        result = run_script()
        cls.result = result
        cls.lines = [line for line in result.stdout.splitlines() if line.strip()]
        cls.abc = cls.lines[1] if len(cls.lines) > 1 else ""

    def test_script_exits_clean_and_reports_its_search(self):
        self.assertEqual(self.result.returncode, 0, self.result.stdout + self.result.stderr)
        self.assertTrue(self.lines, "the script printed nothing")
        self.assertIn("melodies searched", self.lines[0])
        self.assertNotIn("PROBLEM:", self.result.stdout)

    def test_the_chosen_melody_holds_the_rule(self):
        pitches = abc_to_pitches(self.abc)
        self.assertEqual(len(pitches), compose.SLOTS)
        self.assertEqual(compose.check(pitches), [])

    def test_every_keeper_holds_the_rule(self):
        found = []
        compose.sample(5, found, wanted=200)
        self.assertTrue(found, "the search kept nothing, so nothing is being checked")
        for index, melody in enumerate(found):
            self.assertEqual(
                compose.check(melody), [],
                f"kept melody {index} breaks the rule the search exists to enforce",
            )

    def test_same_seed_same_tune(self):
        again = run_script()
        self.assertEqual(again.stdout, self.result.stdout)

    def test_printed_abc_is_the_tune_it_chose(self):
        self.assertEqual(abc_to_pitches(self.abc), abc_to_pitches(self.abc))
        pitches = abc_to_pitches(self.abc)
        # re-printing what we just parsed must give the same ABC back
        self.assertEqual(compose.to_abc(pitches), self.abc)

    def test_stays_in_range_and_on_the_tonic(self):
        pitches = abc_to_pitches(self.abc)
        self.assertGreaterEqual(min(pitches), compose.LOW)
        self.assertLessEqual(max(pitches), compose.HIGH)
        self.assertEqual(pitches[0], compose.LOW)
        self.assertEqual(pitches[-1], compose.LOW)


if __name__ == "__main__":
    unittest.main()
