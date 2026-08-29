#!/usr/bin/env python3
"""Offline tests for the direct mail channel (channels/mail.py).

No network: exercises credential resolution, draft parsing, no-op behavior
without credentials, and outbound file handling with a stubbed SMTP. The
actual SMTP/IMAP connect is never attempted here.
"""
import os
import sys
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import channels.mail as mail  # noqa: E402


def _clear():
    return mock.patch.dict(os.environ, {}, clear=True)


def test_configured_false_without_creds():
    with _clear():
        assert mail.configured() is False


def test_configured_true_with_generic_creds():
    with _clear():
        os.environ["SYMPOSIUM_MAIL_USER"] = "symposium@example.com"
        os.environ["SYMPOSIUM_MAIL_APP_PASSWORD"] = "app-password"
        assert mail.configured() is True


def test_configured_true_with_per_amigo_creds():
    with _clear():
        os.environ["SYMPOSIUM_MAIL_USER_DESI"] = "desi.s.amigo@gmail.com"
        os.environ["SYMPOSIUM_MAIL_APP_PASSWORD_DESI"] = "pw"
        assert mail.configured() is True


def test_credentials_for_explicit_identity():
    with _clear():
        os.environ["SYMPOSIUM_MAIL_USER_DESI"] = "desi.s.amigo@gmail.com"
        os.environ["SYMPOSIUM_MAIL_APP_PASSWORD_DESI"] = "pw-desi"
        os.environ["SYMPOSIUM_MAIL_USER_CLAUDE"] = "claude.symposium@gmail.com"
        os.environ["SYMPOSIUM_MAIL_APP_PASSWORD_CLAUDE"] = "pw-claude"
        assert mail.credentials_for("desi") == ("desi.s.amigo@gmail.com", "pw-desi")
        assert mail.credentials_for("claude") == ("claude.symposium@gmail.com", "pw-claude")
        assert mail.credentials_for("gemini") is None  # not configured


def test_credentials_for_falls_back_to_generic():
    with _clear():
        os.environ["SYMPOSIUM_MAIL_USER"] = "generic@example.com"
        os.environ["SYMPOSIUM_MAIL_APP_PASSWORD"] = "pw"
        assert mail.credentials_for("desi") == ("generic@example.com", "pw")


def test_credentials_for_partial_is_unconfigured():
    with _clear():
        os.environ["SYMPOSIUM_MAIL_USER_DESI"] = "desi.s.amigo@gmail.com"
        assert mail.credentials_for("desi") is None  # password missing


def test_parse_draft_basic():
    headers, body = mail.parse_draft(
        "Identity: desi\n"
        "To: someone@example.com\n"
        "Subject: A message from the commons\n"
        "Reply-To: reply@example.com\n"
        "\n"
        "Hello there.\n\nSecond paragraph."
    )
    assert headers["identity"] == "desi"
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
        with _clear():
            mail.REPO_ROOT = Path(td)
            mail.OUTBOUND_DIR = Path(td) / "channels" / "outbound"
            mail.SENT_DIR = Path(td) / "channels" / "sent"
            mail.INBOUND_DIR = Path(td) / "channels" / "inbound"
            mail.run_mail_channel()  # must not raise, must not try to connect


def test_drain_outbox_uses_identity_creds_and_moves_sent():
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        with _clear():
            os.environ["SYMPOSIUM_MAIL_USER_DESI"] = "desi.s.amigo@gmail.com"
            os.environ["SYMPOSIUM_MAIL_APP_PASSWORD_DESI"] = "pw-desi"
            mail.REPO_ROOT = Path(td)
            outbox = Path(td) / "channels" / "outbound"
            sent = Path(td) / "channels" / "sent"
            outbox.mkdir(parents=True)
            draft = outbox / "draft.md"
            draft.write_text(
                "Identity: desi\nTo: someone@example.com\nSubject: Hi\n\nHello\n",
                encoding="utf-8",
            )
            mail.OUTBOUND_DIR = outbox
            mail.SENT_DIR = sent
            mail.INBOUND_DIR = Path(td) / "channels" / "inbound"

            class _FakeSMTP:
                def __enter__(self):
                    return self

                def __exit__(self, *a):
                    return False

                def starttls(self):
                    return None

                def login(self, user, pw):
                    assert user == "desi.s.amigo@gmail.com"
                    assert pw == "pw-desi"

                def send_message(self, msg):
                    assert "someone@example.com" in msg["To"]
                    assert msg["From"] == "desi.s.amigo@gmail.com"

            with mock.patch.object(mail.smtplib, "SMTP", return_value=_FakeSMTP()):
                n = mail.drain_outbox()
            assert n == 1
            assert not draft.exists()          # moved out of outbox
            assert (sent / "draft.md").exists()  # into sent/


def test_drain_outbox_fails_without_creds_for_identity():
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        with _clear():
            mail.REPO_ROOT = Path(td)
            outbox = Path(td) / "channels" / "outbound"
            sent = Path(td) / "channels" / "sent"
            outbox.mkdir(parents=True)
            draft = outbox / "draft.md"
            draft.write_text(
                "Identity: gemini\nTo: someone@example.com\nSubject: Hi\n\nHello\n",
                encoding="utf-8",
            )
            mail.OUTBOUND_DIR = outbox
            mail.SENT_DIR = sent
            mail.INBOUND_DIR = Path(td) / "channels" / "inbound"

            with mock.patch.object(mail.smtplib, "SMTP") as smtp:
                n = mail.drain_outbox()  # must not raise; logs failure
            assert n == 0
            assert draft.exists()  # not sent, stays in outbox
            smtp.assert_not_called()


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
