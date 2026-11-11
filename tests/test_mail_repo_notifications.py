"""GitHub repository notifications: machine mail, filed as telemetry, never as a human letter.

Added 2026-11-11 (Desi). Before this, `notifications@github.com` matched nothing in
AUTOMATED_SENDER_RE, so issue, pull-request and workflow mail from the repository was filed in
channels/inbound/ — the folder that exists to hold letters from people. Keying it as automated
without routing it would trade one fault for a worse one: the notice of a run that failed on the
far side would be dropped, and it is the only trace such a run leaves here.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from channels import mail

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_github_notifications_are_machine_mail():
    assert mail.is_automated("GitHub <notifications@github.com>") is True
    assert mail.is_automated("notifications@github.com") is True


def test_a_lookalike_domain_is_not_a_repository_notification():
    assert mail.is_repo_notification("GitHub <notifications@github.com>") is True
    assert mail.is_repo_notification("notifications@github.com.example.net") is False
    assert mail.is_repo_notification("Lindsay Ridgeway <ldridgeway@gmail.com>") is False


def test_a_repository_notification_lands_in_diagnostics(tmp_path, monkeypatch):
    monkeypatch.setattr(mail, "INBOUND_DIR", tmp_path)
    out = mail._file_diagnostic(
        identity="desi",
        heading="Repository notification",
        from_addr="GitHub <notifications@github.com>",
        date="Wed, 11 Nov 2026 18:00:00 +0000",
        subject="[LindsayRidgeway/llm-symposium] Run failed: channel-poll",
        body="See https://api.github.com/repos/x/y?access_token=SECRET123 for the log.",
        msg_id="<abc@github.com>",
        fallback="repo-notification",
    )
    assert out.parent == tmp_path / "diagnostics"
    text = out.read_text(encoding="utf-8")
    assert text.startswith("# Repository notification — ")
    assert "SECRET123" not in text, "the key-bearing URL must be redacted before it is stored"
    assert "Run failed" in out.name


def test_mail_py_is_importable_when_run_as_a_script():
    """The runner runs `python3 channels/mail.py`, which puts channels/ at sys.path[0].

    `channels.triage` is not importable from there and the fetch loop's except turns that
    ModuleNotFoundError into one printed line, so triage was silently off in exactly the mode the
    channel is used in. Reproduce that sys.path and require the dotted import to work.
    """
    code = (
        "import runpy, sys\n"
        "sys.path[0] = 'channels'\n"
        "runpy.run_path('channels/mail.py', run_name='not_main')\n"
        "import channels.triage\n"
        "print('ok')\n"
    )
    proc = subprocess.run([sys.executable, "-c", code], cwd=REPO_ROOT, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr[-2000:]
    assert proc.stdout.strip().endswith("ok")
