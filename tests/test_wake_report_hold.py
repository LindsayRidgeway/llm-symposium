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


class TestTheRecordIsCommitted(unittest.TestCase):
    """An uncommitted record blocks every amigo's delivery: the lander refuses a dirty checkout, so
    a file this relay writes and does not commit turns into a silent stall. That happened for two
    days (2026-10-06 to 08) with the daily report's own output, which is why the same guard is
    pinned here."""

    def setUp(self):
        import tempfile
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.rec = Path(self.tmp.name) / "2026-10-08-outbound-desi-session.md"
        self.rec.write_text("a message\n", encoding="utf-8")
        self.calls = []

    def _commit(self, run, *paths):
        import scripts.tell_human as th
        real = th.subprocess.run
        th.subprocess.run = run
        try:
            import contextlib
            import io
            with contextlib.redirect_stdout(io.StringIO()) as buf:
                th._commit_own_outputs(list(paths), "record(telegram): desi")
            return buf.getvalue()
        finally:
            th.subprocess.run = real

    def test_the_record_is_staged_then_committed(self):
        from types import SimpleNamespace

        def run(argv, **kw):
            self.calls.append(argv)
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        self._commit(run, self.rec)
        self.assertIn(str(self.rec), self.calls[0])
        self.assertEqual(self.calls[1][:4], ["git", "-C", str(REPO), "commit"])

    def test_a_git_failure_names_the_consequence_and_is_survived(self):
        import subprocess as sp

        def run(argv, **kw):
            raise sp.CalledProcessError(1, argv)
        out = self._commit(run, self.rec)
        self.assertIn("landing is blocked", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
