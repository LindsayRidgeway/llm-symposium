#!/usr/bin/env python3
"""Tests for the credential saver.

The promise worth pinning is the one that cost two days with the seed: a value that is not usable must
be *refused*, not saved. And a pasted line ending must not become part of the secret — a password with
a trailing newline logs in nowhere while looking perfectly ordinary on disk.
"""
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts.save_password import clean  # noqa: E402


class TestClean(unittest.TestCase):
    def test_a_trailing_line_ending_is_not_part_of_the_secret(self):
        for raw in ("hunter2\n", "hunter2\r\n", "hunter2\r"):
            self.assertEqual(clean(raw), "hunter2", repr(raw))

    def test_a_trailing_space_is_left_alone(self):
        # Spaces can be part of a real password, and guessing wrong in that direction saves a file
        # that looks fine and fails to log in.
        self.assertEqual(clean("hunter 2 "), "hunter 2 ")

    def test_interior_whitespace_is_left_alone(self):
        self.assertEqual(clean("two words"), "two words")

    def test_nothing_is_refused(self):
        for raw in ("", "\n", "\r\n"):
            with self.assertRaises(ValueError, msg=repr(raw)):
                clean(raw)


if __name__ == "__main__":
    unittest.main(verbosity=2)
