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
    """The record a relay writes is handed to the one publisher, and only that record.

    The old docstring here said an uncommitted record "blocks every amigo's delivery: the lander
    refuses a dirty checkout". That stopped being true on 2026-11-02, when the lander moved into its
    own worktree; what a dirty or ahead checkout still costs is the lander's final fast-forward.
    The same commit that noticed this (c349e96d) moved ``tell_human`` and ``daily_report`` onto
    ``channels.record_push.commit_and_publish``, which commits and pushes in a throwaway worktree —
    and left these two tests replacing ``subprocess.run`` to watch for git calls that are no longer
    made here. They went red on main and stayed red for three days, invisibly: the lander compares a
    run's diff to a baseline that was already failing.

    So the seam is the function the relay actually calls. What is pinned here is what it hands over
    and what it says when the hand-over fails; the git mechanics are pinned for real against
    throwaway repositories in ``tests/test_record_push.py`` and ``tests/test_script_publish.py``.
    """

    def setUp(self):
        import tempfile
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        (self.root / "channels" / "telegram").mkdir(parents=True)
        self.rec = self.root / "channels" / "telegram" / "2026-10-08-outbound-desi-session.md"
        self.rec.write_text("a message\n", encoding="utf-8")

    def _commit(self, paths, result=None, raiser=None):
        import contextlib
        import io
        from unittest import mock
        import scripts.tell_human as th
        from channels import record_push
        seen = {"called": False}

        def fake(root, rel, msg, **kw):
            seen.update(called=True, root=root, paths=list(rel), message=msg)
            if raiser is not None:
                raise raiser
            return dict(result if result is not None
                        else {"ok": True, "errors": [], "pushed": True})

        with mock.patch.object(th, "REPO", self.root), \
                mock.patch.object(record_push, "commit_and_publish", fake):
            with contextlib.redirect_stdout(io.StringIO()) as buf:
                th._commit_own_outputs(list(paths), "record(telegram): desi")
        return buf.getvalue(), seen

    def test_the_record_is_handed_to_the_publisher_and_nothing_else(self):
        out, seen = self._commit([self.rec])
        self.assertTrue(seen["called"])
        self.assertEqual(seen["paths"], ["channels/telegram/2026-10-08-outbound-desi-session.md"])
        self.assertEqual(seen["root"], str(self.root))

    def test_a_missing_record_is_not_handed_over(self):
        # The message has already gone; a relay that invents a path to commit is worse than one
        # that writes nothing at all.
        out, seen = self._commit([self.root / "channels" / "telegram" / "never-written.md"])
        self.assertFalse(seen["called"])
        self.assertNotIn("WARNING", out)

    def test_a_failed_publish_names_the_consequence_and_is_survived(self):
        out, seen = self._commit(
            [self.rec],
            result={"ok": False, "errors": ["push: [rejected] (fetch first)"], "pushed": False})
        self.assertIn("WARNING", out)
        self.assertIn("push: [rejected]", out)
        self.assertIn("fast-forward", out)

    def test_a_publisher_that_raises_does_not_take_the_relay_down(self):
        out, seen = self._commit([self.rec], raiser=OSError("no git here"))
        self.assertIn("WARNING", out)
        self.assertIn("no git here", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
