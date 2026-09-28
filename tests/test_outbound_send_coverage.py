#!/usr/bin/env python3
"""Guard: any workflow that drains the outbound mail queue must be able to send
every amigo's letter.

`channels/mail.py::drain_outbox()` sends every draft in `channels/outbound/` and
moves it to `channels/sent/`. But `send_draft()` refuses a draft whose `Identity:`
header names an amigo whose credentials are not in the environment (Finding RT-7):
it raises, `drain_outbox()` prints `FAILED` and carries on, and the file stays in
the outbox. A workflow that drains the queue while configuring only some
identities therefore silently strands the other amigas' letters, forever, while
still exiting green.

Measured 2026-09-28: after channel-poll.yml's cron was retired on 2026-09-25,
quiet-check.yml was the only scheduled job calling drain_outbox(), and it set
only Desi's pair — so Gemini's queued pitch (2026-09-24) could not be sent by any
scheduled job. Fixed the same day; this test is the guard.

Offline: reads files only, sends nothing.
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from channels import mail  # noqa: E402

WORKFLOW_DIR = REPO_ROOT / ".github" / "workflows"


def workflows_that_drain():
    """Every workflow file that sends the outbox — directly or via the poller."""
    for path in sorted(WORKFLOW_DIR.glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        if "drain_outbox" in text or "poll_channels" in text:
            yield path, text


class OutboundSendCoverageTests(unittest.TestCase):
    def test_at_least_one_workflow_drains_the_outbox(self):
        found = list(workflows_that_drain())
        self.assertTrue(
            found,
            "no workflow drains channels/outbound/ — queued letters would never be sent",
        )

    def test_every_draining_workflow_carries_every_identity(self):
        problems = []
        for path, text in workflows_that_drain():
            for name, (user_env, pw_env) in mail.IDENTITIES.items():
                for var in (user_env, pw_env):
                    if not re.search(rf"^\s*{re.escape(var)}\s*:", text, re.MULTILINE):
                        problems.append(
                            f"{path.name}: missing {var} (identity {name!r})"
                        )
        self.assertEqual(
            problems,
            [],
            "a workflow drains the outbox but cannot send every identity, so "
            "those letters will silently strand:\n  " + "\n  ".join(problems),
        )

    def test_queued_drafts_name_an_identity_the_workflows_cover(self):
        """A queued draft's Identity: must be one a draining workflow configures."""
        outbound = REPO_ROOT / "channels" / "outbound"
        header_re = re.compile(r"^Identity:\s*(\S+)\s*$", re.MULTILINE)
        for draft in sorted(outbound.glob("*.md")):
            if draft.name.lower() == "readme.md":
                continue  # directory documentation, not a draft
            m = header_re.search(draft.read_text(encoding="utf-8"))
            self.assertIsNotNone(
                m, f"{draft.name} has no Identity: header — it would fail to send"
            )
            identity = m.group(1).strip().lower()
            with self.subTest(draft=draft.name):
                self.assertIn(
                    identity,
                    mail.IDENTITIES,
                    f"{draft.name} names unknown identity {identity!r}",
                )


if __name__ == "__main__":
    unittest.main()
