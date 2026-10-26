#!/usr/bin/env python3
"""Regressions for clef-aware voice ranges and the monophonic measure count.

Before 2026-10-26 `scripts/check_music_rules.py` decided a voice's permitted range from
the voice's *name* alone: voice "1" got treble (G3-D6), voice "2" got bass (C2-G4), and
any `clef=` on a `V:` line was parsed as metadata and thrown away. The cost was measured
on a real piece: `the-beam-is-standing.abc` writes its second voice as a tenor in treble
clef and the checker read it as a bass, producing 45 range violations that the score
itself contradicts. The fix and its provenance are in
channels/reports/2026-10-26-dmitri-the-clef-the-checker-could-not-read.md.

Two behaviours are pinned here: a declared clef decides the range, and a score with one
voice reports the number of measures it actually has instead of 0.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.check_music_rules import CLEF_RANGES, verify_abc_score  # noqa: E402


class ClefRangeTest(unittest.TestCase):

    def bass_by_index_only(self):
        # V: 2 with no clef: the historical index fallback, which assumes bass.
        return (
            "X: 1\nM: 4/4\nL: 1/8\nK: C\n"
            "V: 1\nc'2 d'2 c'2 d'2 |\n"
            "V: 2\nd2 e2 d2 c2 |\n"
        )

    def tenor_with_clef(self):
        return (
            "X: 1\nM: 4/4\nL: 1/8\nK: C\n"
            "V: 1\nc'2 d'2 c'2 d'2 |\n"
            "V: 2 clef=tenor\nd2 e2 d2 c2 |\n"
        )

    def test_index_fallback_still_calls_a_tenor_line_a_bass(self):
        """The old behaviour, kept deliberately: without a clef, voice 2 is a bass."""
        report = verify_abc_score(self.bass_by_index_only())
        self.assertFalse(report.passed)
        self.assertEqual(len(report.range_violations), 4)
        self.assertIn("voice index default", report.range_violations[0])

    def test_declared_tenor_clef_clears_the_false_violations(self):
        report = verify_abc_score(self.tenor_with_clef())
        self.assertEqual(report.range_violations, [])
        self.assertTrue(report.passed, report.errors + report.meter_violations)
        self.assertEqual(report.measures_count, 1)

    def test_declared_bass_clef_matches_the_old_default(self):
        score = self.tenor_with_clef().replace("clef=tenor", "clef=bass")
        report = verify_abc_score(score)
        self.assertEqual(len(report.range_violations), 4)
        self.assertIn("clef=bass", report.range_violations[0])

    def test_a_real_violation_names_the_clef_it_was_measured_against(self):
        score = (
            "X: 1\nM: 4/4\nL: 1/8\nK: C\n"
            "V: 1\nc'2 d'2 c'2 d'2 |\n"
            "V: 2 clef=tenor\nc2 c2 c2 c''2 |\n"
        )
        report = verify_abc_score(score)
        self.assertTrue(report.range_violations)
        self.assertTrue(report.range_violations[0].endswith("(clef=tenor)"))
        self.assertEqual(len(report.range_violations), 1)

    def test_alto_clef_is_its_own_range(self):
        # MIDI 79 (g) is inside alto (C3-G5) and outside bass (C2-G4): if the clef were
        # ignored, this line would be read as a bass part and fail.
        score = (
            "X: 1\nM: 4/4\nL: 1/8\nK: C\n"
            "V: 1\nc'2 d'2 c'2 d'2 |\n"
            "V: 2 clef=alto\nd2 e2 f2 g2 |\n"
        )
        report = verify_abc_score(score)
        self.assertEqual(report.range_violations, [])
        self.assertIn('alto', CLEF_RANGES)

    def test_clef_none_does_not_guess_a_range(self):
        score = (
            "X: 1\nM: 4/4\nL: 1/8\nK: C\n"
            "V: 1\nc'2 d'2 c'2 d'2 |\n"
            "V: 2 clef=none\nd2 e2 d2 c2 |\n"
        )
        report = verify_abc_score(score)
        self.assertEqual(report.range_violations, [])

    def test_an_unrecognised_clef_is_a_warning_not_a_silent_guess(self):
        score = (
            "X: 1\nM: 4/4\nL: 1/8\nK: C\n"
            "V: 1\nc'2 d'2 c'2 d'2 |\n"
            "V: 2 clef=banjo\nd2 e2 d2 c2 |\n"
        )
        report = verify_abc_score(score)
        self.assertEqual(report.range_violations, [])
        self.assertTrue(any("unrecognised clef" in w for w in report.warnings))

    def test_inline_voice_declaration_carries_its_clef(self):
        score = (
            "X: 1\nM: 4/4\nL: 1/8\nK: C\n"
            "V: 1\nc'2 d'2 c'2 d'2 |\n"
            "[V: 2 clef=tenor] d2 e2 d2 c2 |\n"
        )
        report = verify_abc_score(score)
        self.assertEqual(report.voice_names, ["1", "2"])
        self.assertEqual(report.range_violations, [])
        self.assertEqual(report.measures_count, 1)

    def test_a_caller_supplied_range_beats_the_clef(self):
        score = self.tenor_with_clef()
        report = verify_abc_score(score, allowed_voice_ranges={"2": (30, 40)})
        self.assertEqual(len(report.range_violations), 4)
        self.assertIn("caller range", report.range_violations[0])

    def test_quoted_clef_value_is_read(self):
        score = self.tenor_with_clef().replace("clef=tenor", 'clef="tenor"')
        report = verify_abc_score(score)
        self.assertEqual(report.range_violations, [])


class MonophonicMeasureCountTest(unittest.TestCase):

    def test_one_voice_reports_the_measures_it_has(self):
        score = (
            "X: 1\nM: 4/4\nL: 1/8\nK: C\n"
            "C D E F G A B c |\n"
            "c B A G F E D C |\n"
            "C E G c G E C z |\n"
        )
        report = verify_abc_score(score)
        self.assertEqual(report.voice_names, ["1"])
        self.assertEqual(report.measures_count, 3)
        self.assertEqual(report.meter_violations, [])

    def test_two_voices_still_count_the_shorter_part(self):
        report = verify_abc_score(
            "X: 1\nM: 4/4\nL: 1/8\nK: C\n"
            "V: 1\nc'2 d'2 c'2 d'2 | c'2 d'2 c'2 d'2 |\n"
            "V: 2 clef=tenor\nd2 e2 d2 c2 |\n"
        )
        self.assertEqual(report.measures_count, 1)


class CliReportTest(unittest.TestCase):

    def run_cli(self, score):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "score.abc"
            path.write_text(score, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "check_music_rules.py"), str(path)],
                capture_output=True, text=True, check=False,
            )

    def test_cli_passes_a_tenor_second_voice(self):
        result = self.run_cli(
            "X: 1\nM: 4/4\nL: 1/8\nK: C\n"
            "V: 1\nc'2 d'2 c'2 d'2 |\n"
            "V: 2 clef=tenor\nd2 e2 d2 c2 |\n"
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Measures evaluated: 1", result.stdout)
        self.assertIn("Range violations: 0", result.stdout)

    def test_cli_still_fails_an_undeclared_second_voice_above_the_bass(self):
        result = self.run_cli(
            "X: 1\nM: 4/4\nL: 1/8\nK: C\n"
            "V: 1\nc'2 d'2 c'2 d'2 |\n"
            "V: 2\nd2 e2 d2 c2 |\n"
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Range violations: 4", result.stdout)


if __name__ == "__main__":
    unittest.main()
