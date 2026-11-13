#!/usr/bin/env python3
"""GitHub repository notifications: machine mail, filed as telemetry, never as a human letter.

Added 2026-11-11 (Desi). Before this, `notifications@github.com` matched nothing in
AUTOMATED_SENDER_RE, so issue, pull-request and workflow mail from the repository was filed in
channels/inbound/ — the folder that exists to hold letters from people. Keying it as automated
without routing it would trade one fault for a worse one: the notice of a run that failed on the
far side would be dropped, and it is the only trace such a run leaves here.

Rewritten 2026-11-13 (Desi) as a unittest file with a `__main__` runner. It was written
pytest-style — `assert` statements and a `tmp_path`/`monkeypatch` fixture — and nothing in this
repository runs pytest: `python3 -m unittest tests.test_mail_repo_notifications` reported
*Ran 0 tests* and OK, and no workflow named it. A guard that is present and silent is the defect
it measures, so the file was repaired before it was registered
(.github/workflows/test-and-report.yml). The assertions are unchanged; only the harness is.

Run: python3 tests/test_mail_repo_notifications.py
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from channels import mail  # noqa: E402


class RepoNotificationTests(unittest.TestCase):
    def test_github_notifications_are_machine_mail(self):
        self.assertIs(mail.is_automated("GitHub <notifications@github.com>"), True)
        self.assertIs(mail.is_automated("notifications@github.com"), True)

    def test_a_lookalike_domain_is_not_a_repository_notification(self):
        self.assertIs(mail.is_repo_notification("GitHub <notifications@github.com>"), True)
        self.assertIs(mail.is_repo_notification("notifications@github.com.example.net"), False)
        self.assertIs(mail.is_repo_notification("Lindsay Ridgeway <ldridgeway@gmail.com>"), False)

    def test_a_repository_notification_lands_in_diagnostics(self):
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(mail, "INBOUND_DIR", Path(tmp)):
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
            self.assertEqual(out.parent, Path(tmp) / "diagnostics")
            text = out.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("# Repository notification — "))
            self.assertNotIn("SECRET123", text,
                             "the key-bearing URL must be redacted before it is stored")
            # The filename is the subject slugged, so the space is a hyphen. The original
            # assertion looked for "Run failed" and could never have passed: it was written
            # pytest-style, never ran, and this line is what the first real run found.
            self.assertIn("Run-failed-channel-poll", out.name)

    def test_mail_py_is_importable_when_run_as_a_script(self):
        """The runner runs `python3 channels/mail.py`, which puts channels/ at sys.path[0].

        `channels.triage` is not importable from there and the fetch loop's except turns that
        ModuleNotFoundError into one printed line, so triage was silently off in exactly the mode
        the channel is used in. Reproduce that sys.path and require the dotted import to work.
        """
        code = (
            "import runpy, sys\n"
            "sys.path[0] = 'channels'\n"
            "runpy.run_path('channels/mail.py', run_name='not_main')\n"
            "import channels.triage\n"
            "print('ok')\n"
        )
        proc = subprocess.run([sys.executable, "-c", code], cwd=REPO_ROOT,
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr[-2000:])
        self.assertTrue(proc.stdout.strip().endswith("ok"))


if __name__ == "__main__":
    unittest.main()
