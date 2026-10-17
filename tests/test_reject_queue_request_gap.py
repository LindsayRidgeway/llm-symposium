#!/usr/bin/env python3
"""The reject queue's fourth step had no execution — pin it so it cannot go silent again.

Written 2026-10-17 (Desi), after finding the queue in the state this test forbids.

**What was found.** `scripts/reject_queue_sweep.py` is the instrument the human asked for on
2026-09-25: when all five of us have said we cannot do an item, the item becomes a request for his
judgement and the request is marked in the file. It works, and it is tested. But nothing ever runs
`--mark`: the sweep was designed to "ride Desi's existing wake clock", and that call site is in
`~/LLM/desi-bot/local_tick.py` — a private bot file no wake may edit. So the arithmetic has been
correct and unheard. On 2026-10-17 `--check` reported **4 items ready for the steward**, and no item
on the page carried a `steward-requested:` line: the verdict that completed the fourth of them was
written 2026-10-15, so the request had been owed for two days — and, with no call site, would have
been owed indefinitely. That is the precise failure the queue exists to prevent ("a missed count is
how an item goes silent forever"), reached by a different route: not a miscount, a count with no
mouth.

**Why a test and not a call site.** A wake cannot edit the private tick, and adding a scheduled
workflow would run the sweep on a clock, which this project has already ruled out as verification of
unchanged material (see the retired schedule in `test-and-report.yml`). What a wake *can* do is make
the state loud at the one moment the answer can change: the landing gate. This pin runs there.

**What it asserts, and what it deliberately does not.** Only that the file never sits in the state
"ready for the steward and unmarked". It does not judge whether an item *should* be ready, does not
count verdicts itself (the script does the arithmetic — the human's rule: never let a language model
decide it is the fourth), and does not send anything. When it fails, the fix is one command:

    python3 scripts/reject_queue_sweep.py --mark

The second test is the one that keeps the first from passing vacuously: a `ready()` that always
returned `[]` would make the invariant true and meaningless. It feeds the real parser a fixture that
*is* ready and asserts the sweep sees it.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import reject_queue_sweep as sweep  # noqa: E402

QUEUE = REPO / "channels" / "reject-queue.md"


class TheRealQueueCarriesNoSilentRequest(unittest.TestCase):
    def test_no_item_is_ready_for_the_human_without_a_dated_request(self):
        """The invariant: if the sweep would ask him, the file must already say it asked."""
        text = QUEUE.read_text(encoding="utf-8")
        ready = sweep.ready(sweep.parse(text))
        if ready:
            self.fail(
                "%d item(s) on the reject queue have all five verdicts and no `steward-requested:` "
                "line, so the sweep has counted a request it never made: %s\n"
                "Fix: python3 scripts/reject_queue_sweep.py --mark"
                % (len(ready), "; ".join(i["title"] for i in ready))
            )

    def test_every_marked_request_carries_a_real_date(self):
        """A marker with no date, or a placeholder date, is a mark that says nothing."""
        text = QUEUE.read_text(encoding="utf-8")
        items = sweep.parse(text)
        for item in items:
            if item["requested"] is None:
                continue
            self.assertNotIn(
                "YYYY", item["requested"],
                "%s carries the format example as its date, not a request" % item["title"],
            )


class TheSweepWouldNoticeIfItHappened(unittest.TestCase):
    def test_a_ready_item_is_detected(self):
        """Without this, the invariant above could hold because the detector is blind."""
        fixture = (
            "# Reject queue\n\n"
            "## Ready and unmarked\n"
            "- raised: 2026-10-01 by desi\n"
            "- blocked because: nothing here can do it\n"
            + "".join(
                "- reviewed: %s 2026-10-02 cannot (a reason)\n" % a for a in sweep.AMIGOS
            )
            + "\n## Ready and already marked\n"
            "- raised: 2026-10-01 by desi\n"
            "- blocked because: nothing here can do it\n"
            + "".join(
                "- reviewed: %s 2026-10-02 cannot (a reason)\n" % a for a in sweep.AMIGOS
            )
            + "- steward-requested: 2026-10-03\n"
        )
        ready = sweep.ready(sweep.parse(fixture))
        self.assertEqual([i["title"] for i in ready], ["Ready and unmarked"])

    def test_a_partial_review_is_not_ready(self):
        """Four verdicts out of five is not a request; the fifth amigo has not looked."""
        fixture = (
            "# Reject queue\n\n"
            "## Half looked at\n"
            "- raised: 2026-10-01 by desi\n"
            "- blocked because: nothing here can do it\n"
            + "".join(
                "- reviewed: %s 2026-10-02 cannot (a reason)\n" % a for a in sweep.AMIGOS[:-1]
            )
        )
        self.assertEqual(sweep.ready(sweep.parse(fixture)), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
