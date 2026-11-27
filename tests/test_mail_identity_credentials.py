#!/usr/bin/env python3
"""Offline regression tests for mail identity and SMTP-envelope isolation."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from channels import mail  # noqa: E402


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

    # ---- the from address is not necessarily the login (REQUEST D-16, 2026-11-27) ----------------
    def _send(self, env: dict, identity: str = "desi"):
        """Send one minimal draft through the fake SMTP; return (login_args, message)."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            draft = root / "draft.md"
            draft.write_text(
                f"Identity: {identity}\nTo: recipient@example.test\nSubject: From test\n\nBody.\n",
                encoding="utf-8",
            )
            with (
                mock.patch.dict(os.environ, env, clear=True),
                mock.patch.object(mail, "SENT_DIR", root / "sent"),
                mock.patch.object(mail.smtplib, "SMTP", FakeSMTP),
            ):
                mail.send_draft(draft)
        smtp = FakeSMTP.instances[-1]
        return smtp.login_args, smtp.message

    def test_a_relay_that_logs_in_as_a_token_still_sends_from_an_address(self):
        # Resend's SMTP username is the literal string `resend`. Before this, From: was the username,
        # so pointing the channel at the relay would have sent every letter from an address that
        # cannot receive a reply — and no test would have said so.
        env = {
            mail.FROM_ENV: "desi@kythe.app",
            mail.GENERIC_USER_ENV: "resend",
            mail.GENERIC_PW_ENV: "re_test_key",
        }
        login, message = self._send(env)
        self.assertEqual(login, ("resend", "re_test_key"))
        self.assertEqual(message["From"], "desi@kythe.app")

    def test_an_amigo_own_address_wins_over_the_shared_one(self):
        env = {
            mail.FROM_ENV: "commons@kythe.app",
            "SYMPOSIUM_MAIL_FROM_CLAUDE": "claude@kythe.app",
            "SYMPOSIUM_MAIL_USER_CLAUDE": "resend",
            "SYMPOSIUM_MAIL_APP_PASSWORD_CLAUDE": "re_test_key",
        }
        login, message = self._send(env, identity="claude")
        self.assertEqual(login, ("resend", "re_test_key"))
        self.assertEqual(message["From"], "claude@kythe.app")

    def test_with_no_address_configured_the_login_is_still_the_from(self):
        # The old behaviour, pinned: a Gmail mailbox whose login is its address keeps sending as
        # itself, so this change cannot silently rename the sender for the channel as it runs today.
        env = {
            "SYMPOSIUM_MAIL_USER_TARIK": "tarik@example.test",
            "SYMPOSIUM_MAIL_APP_PASSWORD_TARIK": "tarik-password",
        }
        login, message = self._send(env, identity="tarik")
        self.assertEqual(login, ("tarik@example.test", "tarik-password"))
        self.assertEqual(message["From"], "tarik@example.test")

    # ---- the relay transport is opt-in, and refuses the one thing it cannot do safely -------------
    def test_the_relay_is_off_unless_the_variable_says_otherwise(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(mail.transport(), "")
            self.assertIsNone(mail.credentials_for("desi"))

    def test_the_relay_supplies_one_pair_for_every_seat(self):
        env = {mail.TRANSPORT_ENV: "resend", mail.RESEND_KEY_ENV: "re_test_key"}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(mail.credentials_for("desi"), ("resend", "re_test_key"))
            self.assertEqual(mail.credentials_for("gwen"), ("resend", "re_test_key"))
            self.assertEqual(mail.credentials_for(None), ("resend", "re_test_key"))

    def test_the_relay_without_a_from_address_refuses_rather_than_sending_from_the_login(self):
        env = {mail.TRANSPORT_ENV: "resend", mail.RESEND_KEY_ENV: "re_test_key"}
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            draft = root / "draft.md"
            draft.write_text(
                "Identity: desi\nTo: recipient@example.test\nSubject: Refusal\n\nBody.\n",
                encoding="utf-8",
            )
            with (
                mock.patch.dict(os.environ, env, clear=True),
                mock.patch.object(mail, "SENT_DIR", root / "sent"),
                mock.patch.object(mail.smtplib, "SMTP", FakeSMTP),
            ):
                with self.assertRaises(RuntimeError) as caught:
                    mail.send_draft(draft)
            self.assertIn("SYMPOSIUM_MAIL_FROM", str(caught.exception))
        # And nothing was transmitted: a refused letter is not a sent letter.
        self.assertEqual(FakeSMTP.instances, [])

    def test_every_amigo_can_be_given_their_own_address(self):
        for name in sorted(mail.IDENTITIES):
            self.assertIn(name, mail.FROM_IDENTITY_ENV)
            self.assertEqual(mail.FROM_IDENTITY_ENV[name], "SYMPOSIUM_MAIL_FROM_" + name.upper())


if __name__ == "__main__":
    unittest.main()
