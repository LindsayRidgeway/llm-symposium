#!/usr/bin/env python3
"""Tests for the setup-key saver.

The promise worth pinning is the one that failed twice: a key that is not a key must be *refused*,
not saved. Garbage that decodes as base32 is bad enough; garbage that does not decode at all would
be saved as an ordinary-looking file producing ordinary-looking wrong codes, which is precisely the
artifact that cost an evening.
"""
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts.save_seed import normalise  # noqa: E402


class TestNormalise(unittest.TestCase):
    def test_a_key_is_kept_as_is(self):
        self.assertEqual(normalise("GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"),
                         "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ")

    def test_grouping_and_case_are_not_part_of_the_secret(self):
        # Screens show setup keys in groups; GitHub shows it plain. Both are the same secret, and a
        # space that survived into the file would silently be a different one.
        for raw in ("GEZD GNBV GY3T QOJQ GEZD GNBV GY3T QOJQ",
                    "gezd-gnbv-gy3t-qojq-gezd-gnbv-gy3t-qojq",
                    "  GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ  "):
            self.assertEqual(normalise(raw), "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ", raw)

    def test_a_non_base32_string_is_refused(self):
        for raw in ("not-a-key-at-all-1l0", "0189", "!!!!"):
            with self.assertRaises(ValueError, msg=raw):
                normalise(raw)

    def test_an_empty_entry_is_refused(self):
        for raw in ("", "   "):
            with self.assertRaises(ValueError, msg=repr(raw)):
                normalise(raw)


if __name__ == "__main__":
    unittest.main(verbosity=2)
