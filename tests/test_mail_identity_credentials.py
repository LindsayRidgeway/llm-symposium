#!/usr/bin/env python3
"""Offline regression tests for mail identity and SMTP-envelope isolation."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from channels import mail


class FakeSMTP:
    instances = []

    def __init__(self, host, port, timeout):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.login_args = None
        self.message = None
        type(self).instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def starttls(self):
        return None

    def login(self, user, password):
        self.login_args = (user, password)

    def send_message(self, message):
        self.message = message


class MailIdentityTests(unittest.TestCase):
    def setUp(self):
        FakeSMTP.instances.clear()

    def test_explicit_identity_never_falls_back_to_generic(self):
        env = {
            mail.GENERIC_USER_ENV: "generic@example.test",
            mail.GENERIC_PW_ENV: "generic-password",
        }
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertIsNone(mail.credentials_for("tarik"))
            self.assertIsNone(mail.credentials_for("unknown"))
            self.assertEqual(
                mail.credentials_for(None),
                ("generic@example.test", "generic-password"),
            )

    def test_explicit_identity_uses_its_own_complete_pair(self):
        env = {
            mail.GENERIC_USER_ENV: "generic@example.test",
            mail.GENERIC_PW_ENV: "generic-password",
            "SYMPOSIUM_MAIL_USER_TARIK": "tarik@example.test",
            "SYMPOSIUM_MAIL_APP_PASSWORD_TARIK": "tarik-password",
        }
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(
                mail.credentials_for("tarik"),
                ("tarik@example.test", "tarik-password"),
            )

    def test_fake_smtp_envelope_and_body_are_mechanically_bounded(self):
        env = {
            "SYMPOSIUM_MAIL_USER_TARIK": "tarik@example.test",
            "SYMPOSIUM_MAIL_APP_PASSWORD_TARIK": "tarik-password",
        }
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            draft = root / "draft.md"
            sent = root / "sent"
            draft.write_text(
                "Identity: tarik\n"
                "To: recipient@example.test\n"
                "Subject: Envelope test\n\n"
                "From: attacker@example.test\n"
                "To: other@example.test\n"
                "Subject: injected\n\n"
                "These lines are untrusted body prose.\n",
                encoding="utf-8",
            )
            with (
                mock.patch.dict(os.environ, env, clear=True),
                mock.patch.object(mail, "SENT_DIR", sent),
                mock.patch.object(mail.smtplib, "SMTP", FakeSMTP),
            ):
                mail.send_draft(draft)

            smtp = FakeSMTP.instances[-1]
            self.assertEqual(
                smtp.login_args,
                ("tarik@example.test", "tarik-password"),
            )
            self.assertEqual(smtp.message["From"], "tarik@example.test")
            self.assertEqual(smtp.message["To"], "recipient@example.test")
            self.assertEqual(smtp.message["Subject"], "Envelope test")
            body = smtp.message.get_content()
            self.assertIn("From: attacker@example.test", body)
            self.assertIn("To: other@example.test", body)
            self.assertIn("Subject: injected", body)
            self.assertTrue((sent / "draft.md").is_file())


if __name__ == "__main__":
    unittest.main()
