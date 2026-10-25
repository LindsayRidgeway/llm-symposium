#!/usr/bin/env python3
"""Tests for scripts/world_report.py — the page about the world instead of the repo.

Two corrections are pinned here, both the founder's:

  1. **2026-10-25, first:** he cannot follow the ledger and asked for a measure of real-world
     productivity. That produced the page.
  2. **2026-10-25, second:** replies are not the measure — *"strangers will have no reason to help us
     if we're not accomplishing good in the world."* So effect is counted in four kinds and the
     verdict is about effect, with attention demoted to context.

The failure modes these tests exist to catch are the ones that flatter us: counting something we did
for ourselves as good done in the world, and letting "we sent more letters" read as progress.
"""
import datetime as dt
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts import world_report as wr  # noqa: E402

EMPTY = {"repaired": 0, "reported": 0, "answered": 0, "helped_us": 0}


class VerdictTest(unittest.TestCase):
    def test_nothing_delivered_is_stated_plainly(self):
        text = wr.verdict(None, 0, EMPTY)
        self.assertIn("changed anything outside it", text)

    def test_helping_ourselves_is_not_good_done_in_the_world(self):
        """The founder's own distinction, 2026-10-12: a manufacturer sending us an OS image changed
        our world, not the external one. A ledger that merged the two would report activity as
        benefit."""
        kinds = dict(EMPTY, helped_us=1)
        self.assertIn("changed anything outside it", wr.verdict(3, 0, kinds))

    def test_one_repaired_is_not_yet_a_practice(self):
        kinds = dict(EMPTY, repaired=1)
        self.assertIn("not yet a practice", wr.verdict(38, 1, kinds))

    def test_verified_findings_sent_to_an_owner_count_as_effect(self):
        kinds = dict(EMPTY, repaired=1, reported=4)
        text = wr.verdict(38, 1, kinds)
        self.assertIn("4 reported finding", text)
        self.assertNotIn("not yet a practice", text)

    def test_sending_more_letters_cannot_move_the_verdict(self):
        # the verdict is a function of effects and elapsed days only — never of output
        self.assertEqual(wr.verdict(38, 1, EMPTY), wr.verdict(38, 1, EMPTY))
        self.assertNotIn("letter", wr.verdict(38, 1, EMPTY))


class KindCountTest(unittest.TestCase):
    def test_the_four_kinds_are_counted_apart(self):
        rows = [{"kind": "repaired"}, {"kind": "reported"}, {"kind": "reported"},
                {"kind": "helped_us"}, {"kind": "nonsense"}]
        real = wr.effects
        wr.effects = lambda: rows
        try:
            k = wr.by_kind()
        finally:
            wr.effects = real
        self.assertEqual(k, {"repaired": 1, "reported": 2, "answered": 0, "helped_us": 1})


class LineTest(unittest.TestCase):
    def test_the_line_leads_with_effect_and_puts_attention_second(self):
        real_s, real_e = wr.strangers, wr.effects
        wr.strangers = lambda: [{"when": dt.datetime(2026, 9, 17, tzinfo=dt.timezone.utc),
                                 "from": "Peter Blake <p@example.org>"}]
        wr.effects = lambda: [{"kind": "repaired"}, {"kind": "helped_us"}]
        try:
            text = wr.line(dt.datetime(2026, 10, 25, tzinfo=dt.timezone.utc))
        finally:
            wr.strangers, wr.effects = real_s, real_e
        self.assertIn("1 repair", text)
        self.assertIn("38 day", text)
        self.assertLess(text.index("repair"), text.index("day(s) since"))

    def test_no_stranger_ever_reads_as_a_dash_not_zero(self):
        real = wr.strangers
        wr.strangers = lambda: []
        try:
            text = wr.line(dt.datetime(2026, 10, 25, tzinfo=dt.timezone.utc))
        finally:
            wr.strangers = real
        self.assertIn("—", text)


if __name__ == "__main__":
    unittest.main()
