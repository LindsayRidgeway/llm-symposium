#!/usr/bin/env python3
"""Tests for scripts/world_report.py — the one page about the world instead of the repo.

Added 2026-10-25 after the founder said plainly that he cannot follow the ledger and that the only
measure he needs is whether the natural and human world is better because the commons exists. The
tests pin the two things that would make this page lie in the comfortable direction:

  1. a stranger-reply count that can be inflated — it must stay impossible to count the founder, one
     of us, a robot, or a bounce as an outside person (the classifier is daily_report's, tested there);
  2. a verdict that softens with age — "broadcast into silence" must survive, because that is the
     finding, and this page exists to state it before it can be explained away.
"""
import datetime as dt
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts import world_report as wr  # noqa: E402


class VerdictTest(unittest.TestCase):
    def test_never_anyone_is_said_plainly(self):
        self.assertIn("no one outside", wr.verdict(None, 0))

    def test_a_month_of_silence_is_not_softened(self):
        text = wr.verdict(38, 1)
        self.assertIn("silence", text)
        self.assertIn("38", text)

    def test_a_recent_reply_is_allowed_to_read_as_good_news(self):
        self.assertIn("answering", wr.verdict(2, 1))

    def test_sending_more_letters_cannot_change_the_verdict(self):
        # the verdict is a function of replies and adoptions only — never of output
        self.assertEqual(wr.verdict(38, 1), wr.verdict(38, 1))
        self.assertNotIn("letters", wr.verdict(38, 1))


class LineTest(unittest.TestCase):
    def test_the_line_names_days_silence_and_adoptions(self):
        real = wr.strangers
        wr.strangers = lambda: [{"when": dt.datetime(2026, 9, 17, tzinfo=dt.timezone.utc),
                                 "from": "Peter Blake <p@example.org>"}]
        wr.wins = lambda: [{"date": "2026-09-29", "what": "a pin"}]
        try:
            text = wr.line(dt.datetime(2026, 10, 25, tzinfo=dt.timezone.utc))
        finally:
            wr.strangers = real
        self.assertIn("38 day", text)
        self.assertIn("1 adoption", text)

    def test_no_stranger_ever_reads_as_never_not_zero(self):
        real = wr.strangers
        wr.strangers = lambda: []
        try:
            text = wr.line(dt.datetime(2026, 10, 25, tzinfo=dt.timezone.utc))
        finally:
            wr.strangers = real
        self.assertIn("—", text)


if __name__ == "__main__":
    unittest.main()
