#!/usr/bin/env python3
"""Unit and CLI regressions for the two ABC music checkers."""

import sys
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.check_music_rules import verify_abc_score  # noqa: E402

CP_SPEC = importlib.util.spec_from_file_location(
    "independent_counterpoint", REPO_ROOT / "scripts/check-counterpoint.py"
)
counterpoint = importlib.util.module_from_spec(CP_SPEC)
CP_SPEC.loader.exec_module(counterpoint)


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


class TestClefAwareRanges(unittest.TestCase):
    """A voice is checked against the register its own clef writes in.

    The defect these lock down, measured 2026-10-23: a fuging tune with its tune in the tenor
    (`V: 2 clef=treble name="Tenor (lead)"`) was checked against the default for voice 2 — the
    bass register, C2 to G4 — and failed with 45 range violations, every one of them a correct
    treble pitch. The checker read the voice's number off the `V:` header and threw the clef away.
    """

    TREBLE_TENOR_SCORE = (
        "X: 1\nT: Tenor in treble clef\nM: 4/4\nL: 1/8\nK: C\n"
        "V: 1 clef=treble name=\"Treble\"\nc2 d2 e2 f2 |]\n"
        "V: 2 clef=treble name=\"Tenor (lead)\"\nA,2 B,2 c2 d2 |]\n"
    )

    def run_cli(self, score):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "score.abc"
            path.write_text(score, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts/check_music_rules.py"), str(path)],
                capture_output=True, text=True, check=False,
            )

    def test_declared_treble_tenor_no_longer_fails_for_being_voice_two(self):
        report = verify_abc_score(self.TREBLE_TENOR_SCORE)
        self.assertEqual(report.range_violations, [])
        self.assertTrue(report.passed, report.meter_violations)
        self.assertIn("[55, 86]", report.ranges_applied["2"])
        self.assertIn("clef=treble", report.ranges_applied["2"])

    def test_the_same_pitches_without_a_declared_clef_still_fail(self):
        # The repair must not become a blanket pass: with no clef to go on, voice 2 is still
        # the bass register and c5/d5 above it are still violations.
        score = self.TREBLE_TENOR_SCORE.replace('V: 2 clef=treble name="Tenor (lead)"', "V: 2")
        report = verify_abc_score(score)
        self.assertEqual(len(report.range_violations), 2)
        self.assertFalse(report.passed)
        self.assertIn("the default table", report.ranges_applied["2"])

    def test_bass_clef_and_default_agree_so_nothing_changes_for_ordinary_scores(self):
        score = "M: 4/4\nL: 1/8\nK: C\nV: 1 clef=treble\nc2 d2 e2 f2 |]\nV: 2 clef=bass\nC,2 D,2 E,2 F,2 |]\n"
        report = verify_abc_score(score)
        self.assertEqual(report.range_violations, [])
        self.assertIn("[36, 67]", report.ranges_applied["2"])
        self.assertIn("clef=bass", report.ranges_applied["2"])

    def test_an_unknown_clef_is_reported_and_not_silently_defaulted(self):
        score = self.TREBLE_TENOR_SCORE.replace("clef=treble name=\"Tenor (lead)\"",
                                                "clef=thoroughbass name=\"Tenor\"")
        report = verify_abc_score(score)
        # Nothing was applied, so nothing is claimed to have been checked — and it says so.
        self.assertEqual(report.range_violations, [])
        self.assertIn("does not know", report.ranges_applied["2"])
        self.assertTrue(any("clef=thoroughbass" in warning for warning in report.warnings))

    def test_a_percussion_clef_is_named_as_unchecked_rather_than_warned_about(self):
        score = self.TREBLE_TENOR_SCORE.replace("clef=treble name=\"Tenor (lead)\"",
                                                "clef=perc name=\"Block\"")
        report = verify_abc_score(score)
        self.assertIn("names no pitch register", report.ranges_applied["2"])
        self.assertFalse(any("does not know" in warning for warning in report.warnings))

    def test_a_caller_supplied_range_beats_the_score_header(self):
        report = verify_abc_score(self.TREBLE_TENOR_SCORE, allowed_voice_ranges={"2": (60, 60)})
        self.assertTrue(any("outside range [60, 60]" in v for v in report.range_violations))
        self.assertIn("the caller's range", report.ranges_applied["2"])

    def test_a_voice_with_no_range_is_named_as_unchecked_and_not_silently_skipped(self):
        score = "M: 4/4\nL: 1/8\nK: C\nV: 1\nc2 d2 e2 f2 |]\nV: 9\nc2 d2 e2 f2 |]\n"
        report = verify_abc_score(score)
        self.assertIn("no default for this voice name", report.ranges_applied["9"])
        self.assertTrue(any("Voice 9" in warning for warning in report.warnings))

    def test_a_single_voice_score_reports_its_real_measure_count(self):
        # Was 0: measures_count was assigned only inside the two-voice counterpoint branch, so a
        # valid lead sheet printed "Measures evaluated: 0" under a PASSED verdict.
        score = "M: 4/4\nL: 1/8\nK: C\nV: 1 clef=treble\nc2 d2 e2 f2 | g2 f2 e2 d2 | c8 |]\n"
        report = verify_abc_score(score)
        self.assertEqual(report.measures_count, 3)
        self.assertTrue(report.passed)

    def test_a_declared_but_empty_voice_is_reported(self):
        score = self.TREBLE_TENOR_SCORE + "V: 3 clef=bass name=\"Bass\"\n"
        report = verify_abc_score(score)
        self.assertTrue(any("Voice 3 is declared" in warning for warning in report.warnings))

    def test_the_cli_prints_which_range_was_applied_to_which_voice(self):
        result = self.run_cli(self.TREBLE_TENOR_SCORE)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("[Ranges applied]", result.stdout)
        self.assertIn("Voice 2: [55, 86] from the score's own V: header (clef=treble)", result.stdout)
        self.assertIn("Measures evaluated: 1", result.stdout)


class TestIndependentCounterpoint(unittest.TestCase):
    def run_checker(self, score, *arguments):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "score.abc"
            path.write_text(score, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts/check-counterpoint.py"), str(path), *arguments],
                capture_output=True, text=True, check=False,
            )

    def test_abc_octaves_use_standard_midi_middle_c(self):
        notes = counterpoint.parse_voice_line("C, C c c'")
        self.assertEqual([event[1] for event in notes], [48, 60, 72, 84])

    def test_chord_representative_uses_same_midi_anchor(self):
        notes = counterpoint.parse_voice_line("[CEG] [ceg]")
        self.assertEqual([event[1] for event in notes], [67, 79])

    def test_key_and_bar_accidentals_preserve_correct_octave(self):
        notes = counterpoint.parse_voice_line("B ^c c | c", key_sig=counterpoint.parse_key("Dm"))
        self.assertEqual([event[1] for event in notes if event[0] == "note"], [70, 73, 73, 72])

    def test_rest_stays_silent_between_standard_midi_notes(self):
        events = counterpoint.parse_voice_line("C2 z2 c2")
        timeline = counterpoint.events_to_timeline(events)
        self.assertEqual([event[2] for event in timeline], [60, None, 72])
        self.assertEqual(float(timeline[-1][0] + timeline[-1][1]), 0.75)

    def test_api_physical_range_boundary_and_both_sides(self):
        for note, expected in [("C", True), ("B,", False), ("^C", False)]:
            with self.subTest(note=note):
                self.assertEqual(
                    counterpoint.run_checks(f"L:1/8\nK:C\n[V:1] {note}8 |", ranges={"1": (60, 60)}),
                    expected,
                )

    def test_api_unknown_range_voice_is_failure(self):
        self.assertFalse(counterpoint.run_checks("K:C\n[V:1] C8 |", ranges={"typo": (60, 72)}))

    def test_cli_range_accepts_physical_midi_and_preserves_default(self):
        score = "L:1/8\nK:C\n[V:1] C8 |\n[V:2] E,8 |"
        ranged = self.run_checker(score, "--range", "1=60:60", "--range", "2=52:52")
        self.assertEqual(ranged.returncode, 0, ranged.stdout + ranged.stderr)
        self.assertIn("[1] all notes within [60,60]", ranged.stdout)
        default = self.run_checker(score)
        self.assertEqual(default.returncode, 0, default.stdout)
        self.assertNotIn("--- Range check ---", default.stdout)

    def test_cli_range_rejects_out_of_range_note(self):
        result = self.run_checker("K:C\n[V:1] c8 |", "--range", "1=48:60")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("outside MIDI range [48,60]: [72]", result.stdout)

    def test_cli_unknown_voice_does_not_silently_pass(self):
        result = self.run_checker("K:C\n[V:1] C8 |", "--range", "typo=60:72")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("unknown voice", result.stdout.lower())

    def test_cli_malformed_reversed_or_non_midi_ranges_are_usage_errors(self):
        for value in ("60:72", "=60:72", "1=high:low", "1=72:60", "1=-1:72", "1=0:128"):
            with self.subTest(value=value):
                result = self.run_checker("K:C\n[V:1] C8 |", "--range", value)
                self.assertEqual(result.returncode, 2)

    def test_cli_duplicate_voice_range_is_usage_error(self):
        result = self.run_checker("K:C\n[V:1] C8 |", "--range", "1=60:72", "--range", "1=48:60")
        self.assertEqual(result.returncode, 2)
        self.assertIn("duplicate", result.stderr.lower())

    def test_cli_ranges_cannot_be_silently_ignored_by_self_test(self):
        result = self.run_checker("K:C\n[V:1] C8 |", "--self-test", "--range", "1=60:72")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--range requires a score file", result.stderr)

    def test_parallel_fifth_detection_and_reported_pitches_remain_consistent(self):
        result = self.run_checker("L:1/8\nK:C\n[V:1] G4 A4 |\n[V:2] C4 D4 |")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("parallel fifth", result.stdout)
        self.assertIn("1:67->69", result.stdout)
        self.assertIn("2:60->62", result.stdout)


if __name__ == '__main__':
    unittest.main()
