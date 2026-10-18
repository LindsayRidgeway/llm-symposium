#!/usr/bin/env python3
"""test_music_checker.py — Unit tests for ABC music theory & counterpoint verification engine."""

import sys
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.check_music_rules import verify_abc_score  # noqa: E402


class TestMusicChecker(unittest.TestCase):

    @staticmethod
    def isolated_score(upper, lower):
        return f"M: 4/4\nL: 1/8\nK: C\nV: 1\n{upper}8 |\nV: 2\n{lower}8 |\n"

    def run_checker(self, score):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "score.abc"
            path.write_text(score, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts/check_music_rules.py"), str(path)],
                capture_output=True, text=True, check=False,
            )

    def assert_no_other_violations(self, report):
        self.assertEqual(report.voice_names, ["1", "2"])
        self.assertEqual(report.measures_count, 1)
        self.assertEqual(report.errors, [])
        self.assertEqual(report.meter_violations, [])
        self.assertEqual(report.parallel_fifths, [])
        self.assertEqual(report.parallel_octaves, [])

    def test_crossing_alone_fails_verdict(self):
        # Both notes fit their configured registers; only their ordering is wrong.
        report = verify_abc_score(self.isolated_score("C", "E"))
        self.assert_no_other_violations(report)
        self.assertEqual(report.range_violations, [])
        self.assertEqual(len(report.voice_crossings), 1)
        self.assertFalse(report.passed)

    def test_range_alone_fails_verdict(self):
        report = verify_abc_score(self.isolated_score("c''", "C,"))
        self.assert_no_other_violations(report)
        self.assertEqual(report.voice_crossings, [])
        self.assertEqual(len(report.range_violations), 1)
        self.assertFalse(report.passed)

    def test_cli_crossing_alone_returns_failure(self):
        result = self.run_checker(self.isolated_score("C", "E"))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("Voice crossings: 1", result.stdout)
        self.assertIn("[Voice Crossings]", result.stdout)
        self.assertIn("Result: FAILED", result.stdout)
        self.assertNotIn("Result: PASSED", result.stdout)

    def test_cli_range_alone_returns_failure_and_identifies_note(self):
        result = self.run_checker(self.isolated_score("c''", "C,"))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("[Range Violations]", result.stdout)
        self.assertIn("MIDI 96", result.stdout)
        self.assertIn("outside range [55, 86]", result.stdout)
        self.assertIn("Result: FAILED", result.stdout)
        self.assertNotIn("Result: PASSED", result.stdout)

    def test_cli_valid_two_voice_score_still_passes(self):
        result = self.run_checker(self.isolated_score("C", "C,"))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("Voices analyzed: 1, 2", result.stdout)
        self.assertIn("Measures evaluated: 1", result.stdout)
        self.assertIn("Result: PASSED", result.stdout)

    def test_cli_empty_score_explains_failure(self):
        result = self.run_checker("X: 1\nM: 4/4\nK: C\n")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("[Errors]", result.stdout)
        self.assertIn("No playable voices or measures found", result.stdout)

    def test_meter_integrity_valid(self):
        """Test valid 4/4 meter parsing."""
        abc = """
X: 1
T: Valid Meter Test
M: 4/4
L: 1/8
K: C
V: 1 clef=treble
c2 d2 e2 f2 | g2 f2 e2 d2 | c8 |]
V: 2 clef=bass
C,4 G,4 | C,4 G,4 | C,8 |]
"""
        report = verify_abc_score(abc)
        self.assertEqual(len(report.meter_violations), 0)
        self.assertTrue(report.passed)

    def test_meter_integrity_invalid(self):
        """Test that irregular bar lengths are caught."""
        abc = """
X: 2
T: Invalid Meter Test
M: 4/4
L: 1/8
K: C
V: 1
c2 d2 e2 | g8 |]
"""
        report = verify_abc_score(abc)
        self.assertGreater(len(report.meter_violations), 0)
        self.assertFalse(report.passed)

    def test_parallel_fifths_detection(self):
        """Test that consecutive parallel fifths are caught."""
        abc = """
X: 3
T: Parallel Fifths Test
M: 4/4
L: 1/8
K: C
V: 1
g4 a4 |
V: 2
c4 d4 |
"""
        report = verify_abc_score(abc)
        self.assertGreater(len(report.parallel_fifths), 0)
        self.assertFalse(report.passed)

    def test_parallel_octaves_detection(self):
        """Test that consecutive parallel octaves are caught."""
        abc = """
X: 4
T: Parallel Octaves Test
M: 4/4
L: 1/8
K: C
V: 1
c'4 d'4 |
V: 2
c4 d4 |
"""
        report = verify_abc_score(abc)
        self.assertGreater(len(report.parallel_octaves), 0)
        self.assertFalse(report.passed)

    def test_voice_crossing_detection(self):
        """Test voice crossing when voice 2 rises above voice 1."""
        abc = """
X: 5
T: Voice Crossing Test
M: 4/4
L: 1/8
K: C
V: 1
c4 d4 |
V: 2
e4 f4 |
"""
        report = verify_abc_score(abc)
        self.assertGreater(len(report.voice_crossings), 0)

    def test_classical_contrary_motion_pass(self):
        """Test that classical contrary motion counterpoint passes without violations."""
        abc = """
X: 6
T: Classical Counterpoint Pass
M: 4/4
L: 1/8
K: F
V: 1 clef=treble
A2 B2 c2 f2 | e2 d2 c4 |
V: 2 clef=bass
F,2 D,2 A,,2 D,2 | G,,2 B,,2 C,4 |
"""
        report = verify_abc_score(abc)
        self.assertEqual(len(report.parallel_fifths), 0)
        self.assertEqual(len(report.parallel_octaves), 0)
        self.assertEqual(len(report.meter_violations), 0)
        self.assertTrue(report.passed)


if __name__ == '__main__':
    unittest.main()
