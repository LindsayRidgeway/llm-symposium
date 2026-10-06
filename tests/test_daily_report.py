#!/usr/bin/env python3
"""Tests for the daily report's display rules.

The human asked for shorter item names (2026-10-06), pointing at the old COBOL paragraph-name
budget of ~30 characters, and for the postponed list to stay truncated *provided the total is still
shown*. Both are display promises about a report he reads on a phone, so both are pinned here —
along with the one thing that must never be cut, which is the count.
"""
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts.daily_report import DISPLAY_TITLE, _short, render  # noqa: E402


class TestShortName(unittest.TestCase):
    def test_a_long_title_is_cut_to_a_glance(self):
        t = ("I fixed the bug that made the commons' email replier answer robot messages and send "
             "pointless replies — the same fault that sent eight junk replies")
        self.assertLessEqual(len(_short(t)), DISPLAY_TITLE)
        self.assertTrue(_short(t).endswith("…"))

    def test_first_person_leads_are_dropped(self):
        self.assertTrue(_short("I sent the two follow-up emails that were overdue to both groups, "
                               "each written to three weeks ago").startswith("sent the two"))
        self.assertTrue(_short("I am fixing a flaw in our chat processor so messages are not "
                               "processed twice").startswith("fixing a flaw"))

    def test_the_cut_lands_on_a_word_boundary(self):
        out = _short("I checked the pile of review branches that hold finished work which never "
                     "reached the main repository")
        self.assertNotIn("…", out.rstrip("…")[-1:])   # no partial word before the ellipsis
        self.assertFalse(out.endswith(" …"))

    def test_a_short_title_is_left_alone(self):
        self.assertEqual(_short("I broke Telegram"), "broke Telegram")
        self.assertEqual(_short(""), "")


class TestReportShape(unittest.TestCase):
    def test_the_three_groups_are_reported_and_the_identity_is_printed(self):
        out = render(hours=24)
        for group in ("N=", "A=", "P=", "R="):
            self.assertIn(group, out, group)
        self.assertIn("N=A+P+R", out)
        self.assertNotIn("U=", out)          # the human replaced U with P, 2026-10-06

    def test_the_postponed_total_survives_truncation(self):
        # He asked for a truncated list *as long as the total is still shown*.
        out = render(hours=24)
        self.assertIn("postponed", out)
        self.assertIn("not yet reviewed", out)
        self.assertIn("showing", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
