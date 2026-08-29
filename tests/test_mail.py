#!/usr/bin/env python3
"""Offline tests for the direct mail channel (channels/mail.py).

No network: exercises draft parsing, no-op behavior without credentials, and
outbound file handling with a stubbed SMTP. The actual SMTP/IMAP connect is
never attempted here.
"""
import os
import sys
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import channels.mail as mail  # noqa: E402


def test_configured_false_without_creds():
    with mock.patch.dict(os.environ, {}, clear=True):
        mail.MAIL_USER = ""
        mail.MAIL_APP_PASSWORD = ""
        assert mail.configured() is False


def test_configured_true_with_creds():
    with mock.patch.dict(os.environ, {}, clear=True):
        mail.MAIL_USER = "symposium@example.com"
        mail.MAIL_APP_PASSWORD = "app-password"
        assert mail.configured() is True


def test_parse_draft_basic():
    headers, body = mail.parse_draft(
        "To: someone@example.com\n"
        "Subject: A message from the commons\n"
        "Reply-To: reply@example.com\n"
        "\n"
        "Hello there.\n\nSecond paragraph."
    )
    assert headers["to"] == "someone@example.com"
    assert headers["subject"] == "A message from the commons"
    assert headers["reply-to"] == "reply@example.com"
    assert body == "Hello there.\n\nSecond paragraph."


def test_parse_draft_missing_subject_rejected():
    try:
        mail.parse_draft("To: someone@example.com\n\nbody")
    except ValueError as e:
        assert "Subject" in str(e)
    else:
        raise AssertionError("expected ValueError")


def test_parse_draft_malformed_header_rejected():
    try:
        mail.parse_draft("not a header\n\nbody")
    except ValueError as e:
        assert "malformed" in str(e)
    else:
        raise AssertionError("expected ValueError")


def test_run_mail_channel_noop_without_creds():
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)
        with mock.patch.dict(os.environ, {}, clear=True):
            mail.MAIL_USER = ""
            mail.MAIL_APP_PASSWORD = ""
            mail.REPO_ROOT = tmp_path
            mail.OUTBOUND_DIR = tmp_path / "channels" / "outbound"
            mail.SENT_DIR = tmp_path / "channels" / "sent"
            mail.INBOUND_DIR = tmp_path / "channels" / "inbound"
            mail.run_mail_channel()  # must not raise, must not try to connect


def test_drain_outbox_moves_sent():
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)
        with mock.patch.dict(os.environ, {}, clear=True):
            mail.MAIL_USER = "symposium@example.com"
            mail.MAIL_APP_PASSWORD = "app-password"
            mail.REPO_ROOT = tmp_path
            outbox = tmp_path / "channels" / "outbound"
            sent = tmp_path / "channels" / "sent"
            outbox.mkdir(parents=True)
            draft = outbox / "draft.md"
            draft.write_text(
                "To: someone@example.com\nSubject: Hi\n\nHello\n",
                encoding="utf-8",
            )
            mail.OUTBOUND_DIR = outbox
            mail.SENT_DIR = sent
            mail.INBOUND_DIR = tmp_path / "channels" / "inbound"

            with mock.patch.object(mail, "send_draft", wraps=mail.send_draft) as wrapped:
                # Stub SMTP so no network happens.
                class _FakeSMTP:
                    def __enter__(self):
                        return self

                    def __exit__(self, *a):
                        return False

                    def starttls(self):
                        return None

                    def login(self, user, pw):
                        assert user == "symposium@example.com"

                    def send_message(self, msg):
                        assert "someone@example.com" in msg["To"]

                with mock.patch.object(mail.smtplib, "SMTP", return_value=_FakeSMTP()):
                    n = mail.drain_outbox()
            assert n == 1
            assert not draft.exists()          # moved out of outbox
            assert (sent / "draft.md").exists()  # into sent/
            assert wrapped.call_count == 1


def _run_all():
    import traceback

    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
            passed += 1
        except Exception:
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
    print(f"\n{passed}/{len(tests)} tests passed")
    return 0 if passed == len(tests) else 1


if __name__ == "__main__":
    sys.exit(_run_all())
