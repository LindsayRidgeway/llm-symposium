#!/usr/bin/env python3
"""Tests for scripts/founder_attribution_audit.py — the citation must point at the sentence.

Why this file exists (2026-10-28). The audit is an instrument, and an instrument that names the
wrong place is worse than no instrument: it produces a list that *looks* reviewable. On 2026-10-27
the tool was landed and run — 104 REVIEW candidates in 55 files — and every single one reported
`file:1`, because the sentence splitter accumulated a buffer line by line and reset its "start
line" only when the buffer ran empty, which after the first split almost never happened.

Nobody noticed in the run that landed it, because `--summary` (the mode you run when you want a
number) never prints a line number at all. That is the same shape as the generated index that
nobody could notice (2026-10-27): the mode that reports a count cannot see the defect in the mode
that reports a location.

The fix is asserted here: a candidate carries the line of its own first character.

Run: python3 tests/test_founder_attribution_audit.py
"""

import importlib.util
import os
import subprocess
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO, "scripts", "founder_attribution_audit.py")


def load():
    spec = importlib.util.spec_from_file_location("founder_attribution_audit", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestLineNumbers(unittest.TestCase):
    def setUp(self):
        self.mod = load()

    def test_each_sentence_carries_its_own_line(self):
        """The defect in one assertion: three sentences, three different lines."""
        text = (
            "Line one is short.\n"
            "\n"
            "The founder wrote the rules of engagement.\n"
            "Another line that says nothing.\n"
            "\n"
            "He decided the rules. And then more.\n"
        )
        got = self.mod.sentences(text)
        rules = [(line, s) for line, s in got if "rules of engagement" in s]
        self.assertEqual(len(rules), 1, got)
        self.assertEqual(rules[0][0], 3)

        decided = [(line, s) for line, s in got if s.startswith("He decided")]
        self.assertEqual(decided[0][0], 6)

    def test_a_sentence_starting_mid_line_reports_that_line(self):
        text = "First sentence here. The founder designed the charter.\n"
        got = self.mod.sentences(text)
        charter = [(line, s) for line, s in got if "charter" in s]
        self.assertEqual(charter[0][0], 1)

    def test_line_numbers_are_not_all_the_same_in_a_real_file(self):
        """The regression that cost the day: every candidate at `:1`."""
        module_text = open(SCRIPT, encoding="utf-8").read()
        lines = {line for line, _ in self.mod.sentences(module_text)}
        self.assertGreater(len(lines), 20, f"splitter collapsed to {sorted(lines)[:5]}")

    def test_scan_of_a_file_reports_the_line_of_the_hit(self):
        hits = self.mod.audit(globs=("README.md",), root=self.mod.REPO)
        self.assertTrue(hits, "README.md should hold at least one founder candidate")
        self.assertGreater(len({h["line"] for h in hits}), 1, [
            (h["line"], h["label"]) for h in hits
        ])


class TestClassification(unittest.TestCase):
    """The labels are candidates, not verdicts — but they must not be nonsense."""

    def setUp(self):
        self.mod = load()

    def test_crediting_him_with_a_rule_is_review(self):
        self.assertEqual(self.mod.classify("The founder wrote the rules of engagement."), "REVIEW")

    def test_instantiating_the_repository_is_fact(self):
        self.assertEqual(
            self.mod.classify("The founder instantiated the repository in August."), "FACT"
        )

    def test_a_bare_pronoun_is_not_a_candidate(self):
        self.assertIsNone(self.mod.classify("He wrote the rules of engagement."))


class TestRunsAsAScript(unittest.TestCase):
    def test_selftest_exits_zero(self):
        proc = subprocess.run(
            [sys.executable, SCRIPT, "--selftest"], capture_output=True, text=True
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_file_mode_prints_a_line_number_after_the_path(self):
        proc = subprocess.run(
            [sys.executable, SCRIPT, "--file", "README.md", "--label", "REVIEW"],
            capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        printed = [ln for ln in proc.stdout.splitlines() if "README.md:" in ln]
        self.assertTrue(printed, proc.stdout)
        numbers = {ln.split("README.md:")[1].split()[0] for ln in printed}
        self.assertNotEqual(numbers, {"1"}, f"every hit still says line 1: {numbers}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
