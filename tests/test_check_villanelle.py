#!/usr/bin/env python3
"""test_check_villanelle.py — the Literary Wing's villanelle form checker.

The checker exists so that "this is a villanelle" is a claim a script can settle.
So the test has to do two things: confirm the shipped poem passes, and confirm
that each defect the checker names is actually caught. A checker that says PASS
on everything is worse than no checker, because it certifies.
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.check_villanelle import (  # noqa: E402
    CANONICAL_SCHEME, LINE_COUNT, count_syllables, check, parse_poem,
)

POEM_PATH = REPO_ROOT / "docs" / "fiction" / "the-sample-is-too-small.poem"
PAGE_PATH = REPO_ROOT / "docs" / "fiction" / "the-sample-is-too-small.html"


class TestShippedPoem(unittest.TestCase):

    def setUp(self):
        self.text = POEM_PATH.read_text(encoding="utf-8")

    def test_poem_file_exists(self):
        self.assertTrue(POEM_PATH.exists(), f"missing {POEM_PATH}")

    def test_poem_passes_its_own_checker(self):
        ok, errors, _, _ = check(self.text)
        self.assertTrue(ok, f"shipped poem fails its own checker: {errors}")

    def test_poem_page_exists_and_links_are_internal(self):
        self.assertTrue(PAGE_PATH.exists(), f"missing {PAGE_PATH}")
        page = PAGE_PATH.read_text(encoding="utf-8")
        self.assertIn("The Sample Is Too Small to Say", page)
        self.assertNotIn('href="http', page.replace('href="http://www.w3.org', ''))

    def test_index_registers_the_poem(self):
        index = (REPO_ROOT / "docs" / "fiction" / "index.html").read_text(encoding="utf-8")
        self.assertIn("the-sample-is-too-small.html", index)

    def test_scheme_is_the_canonical_one(self):
        meta, _, lines = parse_poem(self.text)
        self.assertEqual(meta["scheme"].split(), CANONICAL_SCHEME)
        self.assertEqual(len(lines), LINE_COUNT)

    def test_every_line_is_ten_syllables(self):
        _, _, lines = parse_poem(self.text)
        counts = [sum(count_syllables(w) for w in __import__("re").findall(r"[A-Za-z][A-Za-z'\-]*", ln))
                  for ln in lines]
        self.assertEqual(counts, [10] * LINE_COUNT, f"syllable counts drifted: {counts}")


class TestDefectsAreCaught(unittest.TestCase):
    """Each test breaks exactly one property and requires the checker to refuse."""

    def setUp(self):
        self.text = POEM_PATH.read_text(encoding="utf-8")

    def assertRejected(self, text, why, expect_in=None):
        ok, errors, _, _ = check(text)
        self.assertFalse(ok, f"accepted a poem that {why}")
        if expect_in:
            self.assertTrue(any(expect_in in e for e in errors),
                            f"rejected, but not for {expect_in!r}: {errors}")

    def test_refrain_drift_is_caught(self):
        broken = self.text.replace(
            "I will not call the verdict either way.\n\nThe bounds",
            "I will not call the verdict, either way.\n\nThe bounds",
        )
        self.assertRejected(broken, "drifts a refrain by one comma", "not refrain_b")

    def test_missing_line_is_caught(self):
        self.assertRejected(self.text.replace("Two bled and quit the arm the second day.\n", ""),
                            "drops a line", "18 lines")

    def test_wrong_rhyme_family_is_caught(self):
        broken = self.text.replace("What stays is nine, and nine is not a line.",
                                   "What stays is nine, and nine is not a stay.")
        self.assertRejected(broken, "puts an a-rhyme at a b-position", "requires")

    def test_unrecorded_rhyme_word_is_caught(self):
        self.assertRejected(self.text.replace("rime.define: aɪn\n", ""),
                            "rhymes on a word absent from its own rime table", "rime table")

    def test_wrong_scheme_is_caught(self):
        broken = self.text.replace("scheme: A1 b A2 a b A1 a b A2 a b A1 a b A2 a b A1 A2",
                                   "scheme: A1 b A2 b A1 b A2 b A1 b A2 b A1 b A2 b A1 b A2 A1 A2")
        self.assertRejected(broken, "declares a scheme that is not a villanelle", "canonical")

    def test_syllable_overrun_is_caught(self):
        broken = self.text.replace("Two bled and quit the arm the second day.",
                                   "Two of the women bled and quit the arm the second day.")
        self.assertRejected(broken, "runs a line over the declared syllable count", "syllables")

    def test_missing_front_matter_is_caught(self):
        with self.assertRaises(ValueError):
            parse_poem("The sample is too small for me to say.\n")


class TestSyllableCounter(unittest.TestCase):
    """The counter is heuristic. These are the words that decide the poem."""

    CASES = {
        "say": 1, "way": 1, "weigh": 1, "day": 1, "pray": 1,
        "line": 1, "nine": 1, "sign": 1, "whole": 1, "small": 1,
        "sample": 2, "table": 2, "verdict": 2, "confine": 2, "decline": 2,
        "design": 2, "define": 2, "display": 2, "second": 2, "number": 2,
        "women": 2, "honest": 2, "either": 2, "cannot": 2, "someone": 2,
        "registry": 3, "prayer": 1, "power": 1, "trial": 2,
    }

    def test_counter_agrees_on_the_poem_s_vocabulary(self):
        for word, want in self.CASES.items():
            self.assertEqual(count_syllables(word), want, f"{word!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
