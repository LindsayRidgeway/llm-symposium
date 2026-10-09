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

    def _write_inbound(self, name: str, from_line: str, subject: str, msg_id: str) -> None:
        (self.inbound / name).write_text(
            f"# Inbound mail — {name} (claude)\n\n"
            f"- From: {from_line}\n"
            "- Date: 2026-01-01 00:00:00 -0400\n"
            f"- Subject: {subject}\n"
            f"- Message-ID: <{msg_id}>\n\n---\n\nbody text\n",
            encoding="utf-8",
        )

    def test_automated_senders_are_skipped_but_humans_are_not(self):
        """A machine-generated sender must not draw a reply; a human still must.

        Regression pin (filed by Dmitri 2026-10-05): the guard that used to stand in
        `process_inbound_mail` matched the bare token "noreply" but not the hyphenated
        "no-reply", so `no-reply@accounts.google.com` setup mail reached the model and eight
        junk replies left Dmitri's mailbox in the commons' name. The guard now reuses
        `channels.mail.is_automated`, so every spelling is caught in one place.
        """
        import datetime
        today = datetime.date.today().isoformat()

        # The exact sender that produced the junk, plus the other spellings the old test missed.
        automated = [
            # No "security alert" in the subject: the sender alone must cause the skip, which is
            # exactly what the old inline test missed for the hyphenated spelling.
            ("no-reply@accounts.google.com", "Your new Google Account"),
            ("Google <no-reply@google.com>", "Welcome to your new account"),
            ("Mail Delivery Subsystem <mailer-daemon@googlemail.com>",
             "Delivery Status Notification (Failure)"),
            ("do-not-reply@example.com", "Please do not reply"),
            ("postmaster@example.com", "Undeliverable: hello"),
        ]
        for i, (frm, subj) in enumerate(automated):
            self._write_inbound(f"{today}-1200{i:02d}-claude-auto.md", frm, subj, f"auto-{i}@x")

        # One real human message in the same batch — it must still be answered.
        self._write_inbound(
            f"{today}-130000-claude-human.md",
            "Lindsay Ridgeway <ldridgeway@gmail.com>",
            "A real question",
            "human-1@gmail.com",
        )

        with patch("channels.auto_reply.call_amigo_llm",
                   return_value="Hello Lindsay, good to hear from you!\n\n— Claude") as mocked:
            count = auto_reply.process_inbound_mail()

        self.assertEqual(count, 1, "exactly the one human message should draw a reply")
        drafts = list(self.outbound.glob("*.md"))
        self.assertEqual(len(drafts), 1)
        draft_text = drafts[0].read_text(encoding="utf-8")
        self.assertIn("To: ldridgeway@gmail.com", draft_text)
        self.assertNotIn("no-reply", draft_text)
        # The model must not have been asked to answer any automated sender.
        self.assertEqual(mocked.call_count, 1)

    def test_the_guard_reuses_the_canonical_predicate(self):
        """The reply path and the fetch path must agree on what 'automated' means."""
        from channels import mail
        for sender in ("no-reply@accounts.google.com", "Google <no-reply@google.com>",
                       "do-not-reply@example.com", "postmaster@example.com",
                       "Mail Delivery Subsystem <mailer-daemon@googlemail.com>"):
            self.assertTrue(mail.is_automated(sender), sender)
        for sender in ("Lindsay Ridgeway <ldridgeway@gmail.com>", "someone@example.com"):
            self.assertFalse(mail.is_automated(sender), sender)


if __name__ == "__main__":
    unittest.main()
