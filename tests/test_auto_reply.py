#!/usr/bin/env python3
"""Tests for the autonomous email responder (channels/auto_reply.py)."""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from channels import auto_reply


class AutoReplyTest(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp_dir.name)
        self.inbound = self.root / "channels" / "inbound"
        self.outbound = self.root / "channels" / "outbound"
        self.sent = self.root / "channels" / "sent"

        self.inbound.mkdir(parents=True, exist_ok=True)
        self.outbound.mkdir(parents=True, exist_ok=True)
        self.sent.mkdir(parents=True, exist_ok=True)

        auto_reply.INBOUND_DIR = self.inbound
        auto_reply.OUTBOUND_DIR = self.outbound
        auto_reply.SENT_DIR = self.sent

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_extract_email_address(self):
        self.assertEqual(
            auto_reply.extract_email_address("Lindsay Ridgeway <ldridgeway@gmail.com>"),
            "ldridgeway@gmail.com",
        )
        self.assertEqual(
            auto_reply.extract_email_address("desi.s.amigo@gmail.com"),
            "desi.s.amigo@gmail.com",
        )

    def test_get_amigo_for_file(self):
        p1 = self.inbound / "2026-09-02-232752-claude-The-5-minute.md"
        p2 = self.inbound / "2026-09-02-044402-tarik-Telegram.md"
        p3 = self.inbound / "2026-09-02-232756-gemini-Greetings.md"
        self.assertEqual(auto_reply.get_amigo_for_file(p1), "claude")
        self.assertEqual(auto_reply.get_amigo_for_file(p2), "tarik")
        self.assertEqual(auto_reply.get_amigo_for_file(p3), "gemini")

    def test_clean_reply_body(self):
        raw = "```\nHello Lindsay,\n\nI am doing well.\n```"
        self.assertEqual(auto_reply.clean_reply_body(raw), "Hello Lindsay,\n\nI am doing well.")

        raw_with_headers = "Subject: Re: Greetings\nTo: someone@example.com\n\nHello there!"
        self.assertEqual(auto_reply.clean_reply_body(raw_with_headers), "Hello there!")

    def test_process_inbound_mail_generates_draft(self):
        import datetime
        today_str = datetime.date.today().isoformat()
        inbound_file = self.inbound / f"{today_str}-232752-claude-test-message.md"
        inbound_file.write_text(
            f"# Inbound mail — {today_str}-232752 (claude)\n\n"
            "- From: Lindsay Ridgeway <ldridgeway@gmail.com>\n"
            f"- Date: {today_str} 19:08:18 -0400\n"
            "- Subject: Test continuity\n"
            "- Message-ID: <msg-12345@gmail.com>\n\n"
            "---\n\n"
            "Hi Claude, testing email!\n",
            encoding="utf-8",
        )

        with patch("channels.auto_reply.call_amigo_llm", return_value="Hi Lindsay, received loud and clear!\n\n— Claude"):
            count = auto_reply.process_inbound_mail()

        self.assertEqual(count, 1)
        drafts = list(self.outbound.glob("*.md"))
        self.assertEqual(len(drafts), 1)
        draft_text = drafts[0].read_text(encoding="utf-8")
        self.assertIn("Identity: claude", draft_text)
        self.assertIn("To: ldridgeway@gmail.com", draft_text)
        self.assertIn("Subject: Re: Test continuity", draft_text)
        self.assertIn("In-Reply-To: <msg-12345@gmail.com>", draft_text)
        self.assertIn("Hi Lindsay, received loud and clear!", draft_text)

        # Second run should skip since it's already drafted
        with patch("channels.auto_reply.call_amigo_llm", return_value="Duplicate"):
            count2 = auto_reply.process_inbound_mail()
        self.assertEqual(count2, 0)

    def test_process_inbound_mail_skips_automated_senders(self):
        """A machine sender must never get a model-generated reply.

        Regression: the guard once tested for "noreply" (no hyphen), so
        "no-reply@accounts.google.com" slipped through and a fresh mailbox
        auto-replied to Google setup notices (filed by Dmitri 2026-10-05).
        """
        import datetime
        today_str = datetime.date.today().isoformat()
        senders = [
            "no-reply@accounts.google.com",          # the exact leak: hyphen, not "noreply"
            "Google <no-reply@google.com>",
            "Mail Delivery Subsystem <mailer-daemon@googlemail.com>",
            "do-not-reply@example.com",
        ]
        for i, sender in enumerate(senders):
            (self.inbound / f"{today_str}-0{i}0001-claude-auto.md").write_text(
                f"# Inbound mail — {today_str} (claude)\n\n"
                f"- From: {sender}\n"
                f"- Date: {today_str} 19:08:18 -0400\n"
                "- Subject: Welcome to your new account\n"
                f"- Message-ID: <auto-{i}@host>\n\n"
                "---\n\n"
                "Please verify your address.\n",
                encoding="utf-8",
            )
        with patch("channels.auto_reply.call_amigo_llm", return_value="should not be called") as mocked:
            count = auto_reply.process_inbound_mail()
        self.assertEqual(count, 0, "automated senders must not be auto-replied")
        self.assertEqual(list(self.outbound.glob("*.md")), [])
        mocked.assert_not_called()


if __name__ == "__main__":
    unittest.main()
