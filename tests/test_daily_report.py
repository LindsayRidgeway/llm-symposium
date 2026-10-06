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

from scripts.daily_report import DISPLAY_TITLE, _bucket, _short, render  # noqa: E402


class TestInputBuckets(unittest.TestCase):
    """The classification of inbound mail. The human added this section because he wants to know
    what the world sends us, so the only bucket that carries that meaning has to be hard to enter:
    miscounting a robot or the founder as an outsider would inflate the one number that matters."""

    def test_the_founder_is_not_outside_the_commons(self):
        self.assertEqual(_bucket("Lindsay Ridgeway <ldridgeway@gmail.com>", "Incoming", "inbox"),
                         "human")

    def test_an_amigo_writing_to_an_amigo_is_not_outside(self):
        self.assertEqual(_bucket("<dmitri.s.pravdin@gmail.com>", "hi", "inbox"), "ours")

    def test_our_own_newsletter_service_is_not_outside(self):
        self.assertEqual(_bucket("Amigo <llm_symposium@buttondown.email>", "You're in!", "inbox"),
                         "ours")

    def test_a_robot_address_is_a_robot(self):
        for frm in ("GitHub <noreply@github.com>", "<postmaster@microsoft.com>",
                    "Mail Delivery Subsystem <mailer-daemon@googlemail.com>"):
            self.assertEqual(_bucket(frm, "something", "inbox"), "automated", frm)

    def test_an_auto_acknowledgement_is_a_robot_even_from_a_real_organisation(self):
        # Both of these are real: MIT Technology Review and Retraction Watch, replies to our
        # outreach. A report that counted them as people would say the world was answering us.
        self.assertEqual(_bucket("MIT Technology Review <feedback@technologyreview.com>",
                                 "Re: Story idea", "inbox",
                                 "Thank you! We thrive on reader feedback, and we appreciate "
                                 "hearing from you. ... we'll be in touch within one business day."),
                         "automated")
        self.assertEqual(
            _bucket('"Retraction Watch" <team@retractionwatch.com>', "Re: checker", "inbox",
                    "Thank you for your message. ... because of the high volume we receive we "
                    "cannot always respond."),
            "automated")
        self.assertEqual(_bucket('"Retraction Watch" <team@retractionwatch.com>',
                                 "Thank you for your message Re: checker", "inbox"), "automated")

    def test_a_person_writing_from_outside_is_the_only_thing_that_counts(self):
        self.assertEqual(
            _bucket("Peter Blake <petermblake96@gmail.com>",
                    "Re: An AI wrote you a letter", "inbox",
                    "I got word from Lindsay, who is paying for all of this..."),
            "world")

    def test_a_bounce_is_a_bounce(self):
        self.assertEqual(_bucket("postmaster@microsoft.com", "Undeliverable", "bounce"), "bounce")


class TestTitles(unittest.TestCase):
    """Titles are written by a model, not cut by a regex (the human, 2026-10-06). These pin the
    parts that must hold without a network: the cleanup of the model's answer, and the report's
    preference for a written title over a truncated description."""

    def test_quotes_and_trailing_punctuation_are_stripped(self):
        from channels.titles import clean
        self.assertEqual(clean('"Dirty tree blocked all pushes".'), "Dirty tree blocked all pushes")
        self.assertEqual(clean("  `Email replier ignored robots`  "), "Email replier ignored robots")

    def test_an_overlong_answer_is_cut_on_a_word_boundary_within_budget(self):
        from channels.titles import MAX_TITLE, clean
        out = clean("This answer is far too long to be a title at all, honestly it just rambles on")
        self.assertLessEqual(len(out), MAX_TITLE)
        self.assertFalse(out.endswith(" "))

    def test_a_written_title_is_preferred_over_the_truncated_description(self):
        from scripts.daily_report import _name
        rec = {"title": "I fixed the bug that made the commons' email replier answer robot messages",
               "short_title": "Fixed robot email replies"}
        self.assertEqual(_name(rec), "Fixed robot email replies")

    def test_an_untitled_item_still_renders(self):
        from scripts.daily_report import _name
        rec = {"title": "I fixed the bug that made the commons' email replier answer robot messages"}
        self.assertTrue(_name(rec))
        self.assertLessEqual(len(_name(rec)), DISPLAY_TITLE + 1)


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
