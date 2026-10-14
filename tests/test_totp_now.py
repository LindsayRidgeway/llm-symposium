#!/usr/bin/env python3
"""Tests for the code generator D-10's verification needs.

Two things are pinned: that the arithmetic is *standard* TOTP — checked against the published
RFC 6238 vectors, because a generator that is merely self-consistent would agree with a wrong seed
and prove nothing — and that a setup key is accepted the way GitHub shows it, in groups with
spaces.
"""
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts.totp_now import code_for  # noqa: E402

# RFC 6238 Appendix B. The shared secret is the ASCII string "12345678901234567890", which is
# base32 "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ". Times are the RFC's step boundaries.
RFC_SECRET = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"


class TestStandardTOTP(unittest.TestCase):
    def test_rfc6238_vectors(self):
        for when, expected in ((59, "287082"), (1111111109, "081804"),
                               (1111111111, "050471"), (1234567890, "005924"),
                               (2000000000, "279037")):
            self.assertEqual(code_for(RFC_SECRET, when), expected, when)

    def test_the_code_is_six_digits_with_leading_zeros_kept(self):
        self.assertEqual(len(code_for(RFC_SECRET, 1111111109)), 6)
        self.assertTrue(code_for(RFC_SECRET, 1111111109).startswith("0"))

    def test_a_key_shown_in_groups_is_accepted(self):
        # GitHub shows the setup key as one string, but other screens group it; a space must not
        # silently become a different secret, which is the failure that would look like a bad seed.
        grouped = "GEZD GNBV GY3T QOJQ GEZD GNBV GY3T QOJQ"
        self.assertEqual(code_for(grouped, 59), code_for(RFC_SECRET, 59))

    def test_two_moments_inside_one_step_agree(self):
        self.assertEqual(code_for(RFC_SECRET, 60), code_for(RFC_SECRET, 89))
        self.assertNotEqual(code_for(RFC_SECRET, 89), code_for(RFC_SECRET, 90))


if __name__ == "__main__":
    unittest.main(verbosity=2)
