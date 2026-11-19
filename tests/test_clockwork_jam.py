#!/usr/bin/env python3
"""The de-jamming procedure's own defect, pinned (2026-11-19).

The founder's procedure: examine the head, run a wake, examine again, and call an unchanged head a
jam. Run by hand it found a real jam within the hour. Run a second time it called a healthy idle day a
jam too, because a head dated tomorrow is identical before and after a wake and nothing is wrong with
it. A test that fires on a healthy day teaches its reader to ignore it, so the distinction is pinned
here: unchanged-and-due is jammed, unchanged-and-future is waiting, moved is fine.
"""
import datetime
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import clockwork_jam as cj  # noqa: E402

TODAY = datetime.date(2026, 11, 19)


def snap(block, ident="x", when=None):
    return {"block": block, "id": ident, "when": when, "kind": None}


class Verdict(unittest.TestCase):
    def test_a_due_item_that_is_still_the_head_after_a_wake_is_a_jam(self):
        v = cj.verdict(snap("due", "letter", "2026-11-19"), snap("due", "letter", "2026-11-19"), TODAY)
        self.assertTrue(v["jam"])
        self.assertIn("is still the head after the wake", v["why"])

    def test_a_head_dated_tomorrow_is_waiting_not_jammed(self):
        v = cj.verdict(snap("due", "artefact", "2026-11-20"), snap("due", "artefact", "2026-11-20"), TODAY)
        self.assertFalse(v["jam"])
        self.assertIn("future", v["why"])

    def test_a_moving_head_is_never_a_jam(self):
        v = cj.verdict(snap("due", "letter", "2026-11-19"), snap("reading", "20261105-x"), TODAY)
        self.assertFalse(v["jam"])
        self.assertIn("moved", v["why"])

    def test_a_review_head_that_never_moves_is_a_jam(self):
        v = cj.verdict(snap("review", "20261118-a"), snap("review", "20261118-a"), TODAY)
        self.assertTrue(v["jam"])
        self.assertIn("no clock will move it", v["why"])

    def test_the_head_of_this_repository_is_readable(self):
        head = cj.head("desi")
        self.assertIn(head["block"], ("due", "review", "reading", "none"))


if __name__ == "__main__":
    unittest.main()
