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

    # --- automated-sender filter (filed by Dmitri 2026-10-05) -----------------
    # A fresh mailbox drew eight model-written replies to Google account
    # notices. The reply generator used an ad-hoc check for "noreply", which is
    # not a substring of "no-reply", so the notices were answered. These tests
    # pin the reply boundary to the channel's canonical filter.

    def _write_inbound(self, slug, from_line, subject, body="This is a message.\n"):
        import datetime
        today = datetime.date.today().isoformat()
        p = self.inbound / f"{today}-120000-claude-{slug}.md"
        p.write_text(
            f"# Inbound mail — {today} (claude)\n\n"
            f"- From: {from_line}\n"
            f"- Date: {today} 12:00:00 -0400\n"
            f"- Subject: {subject}\n"
            f"- Message-ID: <{slug}@test>\n\n"
            "---\n\n"
            f"{body}",
            encoding="utf-8",
        )
        return p

    def test_no_hyphen_reply_sender_is_automated(self):
        # The exact regression: the old inline check searched for "noreply",
        # which is NOT a substring of "no-reply@accounts.google.com".
        self.assertFalse("noreply" in "no-reply@accounts.google.com".lower())
        from channels import mail
        self.assertTrue(mail.is_automated("no-reply@accounts.google.com"))

    def test_automated_senders_are_not_answered(self):
        cases = [
            ("google-noreply", "Google <no-reply@accounts.google.com>", "Security alert"),
            ("plain-noreply", "noreply@example.com", "Welcome"),
            ("do-not-reply", "do-not-reply@example.com", "Welcome"),
            ("donotreply", "donotreply@example.com", "Welcome"),
            ("bounce", "Mail Delivery Subsystem <mailer-daemon@googlemail.com>", "Undeliverable: hi"),
        ]
        for slug, from_line, subject in cases:
            self._write_inbound(slug, from_line, subject)

        calls = []
        with patch("channels.auto_reply.call_amigo_llm",
                   side_effect=lambda *a, **k: calls.append(a) or "should not run"):
            count = auto_reply.process_inbound_mail()

        self.assertEqual(count, 0)
        self.assertEqual(calls, [], "no model call should be made for automated senders")
        self.assertEqual(list(self.outbound.glob("*.md")), [])

    def test_human_sender_is_still_answered(self):
        self._write_inbound("human", "Lindsay Ridgeway <ldridgeway@gmail.com>", "Lunch tomorrow?")
        with patch("channels.auto_reply.call_amigo_llm", return_value="Hi Lindsay!"):
            count = auto_reply.process_inbound_mail()
        self.assertEqual(count, 1)
        self.assertEqual(len(list(self.outbound.glob("*.md"))), 1)


if __name__ == "__main__":
    unittest.main()
