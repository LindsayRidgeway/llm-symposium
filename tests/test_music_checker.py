#!/usr/bin/env python3
"""test_music_checker.py — Unit tests for ABC music theory & counterpoint verification engine."""

import unittest
from scripts.check_music_rules import verify_abc_score


class TestMusicChecker(unittest.TestCase):

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
