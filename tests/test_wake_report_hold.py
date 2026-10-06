#!/usr/bin/env python3
"""The hold on bare work reports — the human's request of 2026-10-06.

He asked to stop receiving a report of what each wake did, and to get one counted report a day
instead. The wakes still compose those reports; this pins the rule that decides which of them is
still allowed to reach him, and it is the rule that matters: a message that puts him on the hook
must never be held, and a message that does not must never be sent.
"""
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts.tell_human import is_bare_wake_summary  # noqa: E402


class TestHold(unittest.TestCase):
    def test_a_work_summary_with_nothing_asked_is_held(self):
        for status in ("in the repository", "awaiting reviewer", "no artifact",
                       "parked, unpublished"):
            text = f"I fixed the lander's refusal loop.\n\nStatus: {status}; action: none."
            self.assertTrue(is_bare_wake_summary(text), status)

    def test_a_request_is_never_held(self):
        text = ("REQUEST D-5\n\nPlease create the Gmail account.\n\n"
                "Status: awaiting reviewer; action: none.")
        self.assertFalse(is_bare_wake_summary(text))

    def test_a_message_with_no_status_line_is_never_held(self):
        text = "An outreach reply arrived from the Long Now Foundation — do you want me to answer it?"
        self.assertFalse(is_bare_wake_summary(text))

    def test_a_status_line_mid_message_is_not_a_summary(self):
        # The status must be the tail: a genuine message may quote one and still ask for something.
        text = "Status: awaiting reviewer; action: none.\n\nSeparately, may I spend $40 on parts?"
        self.assertFalse(is_bare_wake_summary(text))

    def test_action_required_is_not_held(self):
        text = "The rover's camera stopped responding.\n\nStatus: blocked; action: needed."
        self.assertFalse(is_bare_wake_summary(text))


if __name__ == "__main__":
    unittest.main(verbosity=2)
