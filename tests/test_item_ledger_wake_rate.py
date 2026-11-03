#!/usr/bin/env python3
"""The reading queue must say, beside each name, whether that body is measured to be waking.

Written 2026-11-02 (Desi) against the failure recorded in `item_ledger.py` itself: on 2026-10-22,
nine never-read items were named to Tarik on the strength of a hand-written capacity table while
his goose run tree had been cold for four days. The queue printed the name and nothing else, so
nothing in the queue could have noticed.

Two properties are pinned here, and one of them is about *not* printing:
  1. a name with evidence of waking gets its measured rate printed beside it;
  2. a name with no measurement gets the word "assumed", never a made-up number — a plausible
     fallback is the failure mode this whole instrument exists to avoid;
  3. the draw is untouched: this changes what a reader is shown, not who is named what.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from channels import item_ledger as il  # noqa: E402


def row(item_id: str, amigo: str, assigned_to: str, filed: str = "2026-11-01T10:00:00Z") -> dict:
    return {
        "id": item_id, "amigo": amigo, "title": "t " + item_id, "short_title": "short",
        "filed_utc": filed, "state": "accomplished", "reason": "landed",
        "reviewer": "auto:land", "paths": ["channels/items.jsonl"],
        "reading_assigned_to": assigned_to, "reading_assigned_by": "collect",
        "reading_assigned_kind": "draw", "reading_assigned_utc": "2026-11-01T11:00:00Z",
    }


class TestRateBeside(unittest.TestCase):
    def test_a_measured_body_shows_its_rate_and_silence(self):
        measured = {"desi": {"wakes_per_day": 2.0, "hours_since": 3.4, "last_utc": "x"}}
        self.assertEqual(il.rate_beside(measured, "desi"), "2.0/day, last 3.4h ago")

    def test_an_unmeasured_body_is_called_assumed_and_never_given_a_number(self):
        self.assertEqual(il.rate_beside(None, "gwen"), "assumed")
        self.assertEqual(il.rate_beside({}, "gwen"), "assumed")
        # No evidence at all is a different statement from a measured zero, and must read as one.
        self.assertEqual(il.rate_beside({"gwen": {"wakes_per_day": 0.0, "hours_since": None}},
                                        "gwen"),
                         "no wake on record — assumed")

    def test_a_broken_instrument_yields_no_measurement_rather_than_a_guess(self):
        with mock.patch.object(il, "REPO", Path("/nonexistent-repo-for-this-test")):
            self.assertIsNone(il.measured_cadence())


class TestReadingQueuePrintsTheRate(unittest.TestCase):
    def _run(self, rows: list[dict], measured: dict | None) -> str:
        tmp = tempfile.mkdtemp()
        ledger = Path(tmp) / "items.jsonl"
        ledger.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
        out = io.StringIO()
        argv = ["item_ledger.py", "--reading-queue", "desi"]
        # `reading_queue(path=LEDGER, ...)` binds its default at def time, so patching the module
        # constant is not enough: the queue would read the real ledger and print the real pile.
        # Wrap the function instead, keeping every other behaviour (the printer under test) intact.
        real_queue = il.reading_queue
        # `_cli` is the entry point; there is no `main` in this module (Python 3.9, no wrapper).
        with mock.patch.object(il, "LEDGER", ledger), \
             mock.patch.object(il, "unreplayed_verdicts", lambda *a, **k: []), \
             mock.patch.object(il, "reading_queue",
                               lambda path=None, who="": real_queue(ledger, who)), \
             mock.patch.object(il, "measured_cadence", lambda *a, **k: measured), \
             mock.patch.object(sys, "argv", argv), \
             contextlib.redirect_stdout(out):
            il._cli()
        return out.getvalue()

    def test_the_name_on_each_item_carries_its_measurement(self):
        # Two rows: desi is measured at 2/day, gwen has no evidence at all.
        rows = [row("20261101T100000Z-aaaaaaaa", "claude", "desi"),
                row("20261101T110000Z-bbbbbbbb", "claude", "gwen", filed="2026-11-01T11:00:00Z")]
        measured = {"desi": {"wakes_per_day": 2.0, "hours_since": 4.0, "last_utc": "x"},
                    "gwen": {"wakes_per_day": 0.0, "hours_since": None, "last_utc": None}}
        text = self._run(rows, measured)
        self.assertIn("-> desi [2.0/day, last 4h ago]", text)
        # gwen's item is not in *desi's* queue, so the per-item line correctly omits it: the
        # measurement must reach the reader through the pile summary instead (the first version of
        # this test asserted a per-item line for a name it had not asked for, which is how it broke
        # the landing of 2026-11-02).
        self.assertNotIn("-> gwen", text)
        # The pile summary names every body holding work, with its rate.
        self.assertIn("the pile's names, with what is measured of each body", text)
        self.assertRegex(text, r"gwen\s+1 item\(s\)\s+no wake on record — assumed")

    def test_without_a_measurement_the_queue_still_prints_and_says_assumed(self):
        rows = [row("20261101T100000Z-aaaaaaaa", "claude", "desi")]
        text = self._run(rows, None)
        self.assertIn("-> desi [assumed]", text)
        self.assertNotIn("/day", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
