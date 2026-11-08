#!/usr/bin/env python3
"""The "fold these verdicts in first" nag must stop once they are folded in.

Written 2026-11-08 (Desi). Measured that morning, on main: `--reading-queue desi` ended with
"3 mirrored verdict(s) are on disk but not yet in the ledger ... Fold them in first:
python3 scripts/ledger_verdict_mirror.py replay", and `replay` answered `applied: 0,
already-there-or-later: 74` — twice, in the same wake, on the same three ids. Both commands were
telling the truth about the same bytes; the comparison between them was not.

`scripts/ledger_verdict_mirror` stamps its verdict file with the compact run stamp
(`20261108T065358Z`) because that is the shape of every run id in this repository; the ledger row
it folds in carries the ISO stamp (`2026-11-08T06:53:58Z`). Compared as strings the compact form
always wins — `-` (0x2d) sorts below `1` (0x31) — so the ledger's verdict looked older than the
verdict it had just inherited, the nag printed again next wake, and a reader following the queue
would replay forever.

What is pinned:
  1. the same moment written two ways is the same moment, so no nag;
  2. a ledger verdict that really is older is still reported (the check keeps its use);
  3. a machine close still counts as no verdict — the reading pile is made of those rows;
  4. an unparseable stamp does not crash the queue printer.

Run: python3 tests/test_unreplayed_verdicts.py
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from channels import item_ledger as il  # noqa: E402


def ledger_row(item_id: str, state: str | None, reviewer: str | None, state_utc: str | None) -> dict:
    return {"id": item_id, "amigo": "dmitri", "title": "t " + item_id, "filed_utc": "2026-11-01T10:00:00Z",
            "state": state, "reviewer": reviewer, "state_utc": state_utc, "reason": "r"}


class UnreplayedVerdicts(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.ledger = self.tmp / "items.jsonl"
        self.vdir = self.tmp / "ledger-verdicts"
        self.vdir.mkdir()

    def write_ledger(self, *rows: dict) -> None:
        self.ledger.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")

    def write_mirror(self, name: str, item_id: str, state: str, reviewer: str, state_utc: str) -> None:
        (self.vdir / f"{name}.json").write_text(
            json.dumps({"id": item_id, "state": state, "reviewer": reviewer, "state_utc": state_utc,
                        "reason": "r", "paths": []}), encoding="utf-8")

    def test_same_moment_in_two_spellings_is_not_unreplayed(self) -> None:
        """The measured defect: compact mirror stamp vs ISO ledger stamp, identical moment."""
        self.write_ledger(ledger_row("20261028T053300Z-55114152", "accomplished", "dmitri",
                                     "2026-11-08T06:53:58Z"))
        self.write_mirror("20261108T065358Z-20261028T053300Z-55114152",
                          "20261028T053300Z-55114152", "accomplished", "dmitri", "20261108T065358Z")
        self.assertEqual(il.unreplayed_verdicts(self.ledger, self.vdir), [])

    def test_a_genuinely_older_ledger_verdict_is_still_reported(self) -> None:
        self.write_ledger(ledger_row("20261028T073326Z-85e03a27", "accomplished", "desi",
                                     "2026-11-08T07:00:00Z"))
        self.write_mirror("20261108T065358Z-20261028T073326Z-85e03a27",
                          "20261028T073326Z-85e03a27", "accomplished", "dmitri", "20261108T065359Z")
        self.assertEqual(il.unreplayed_verdicts(self.ledger, self.vdir),
                         ["20261028T073326Z-85e03a27"])

    def test_machine_close_is_still_no_verdict(self) -> None:
        self.write_ledger(ledger_row("codex-20261108T045905Z-87d4be45", "accomplished", "auto:land",
                                     "2026-11-08T06:53:01Z"))
        self.write_mirror("20261108T065301Z-codex-20261108T045905Z-87d4be45",
                          "codex-20261108T045905Z-87d4be45", "accomplished", "dmitri",
                          "20261108T065301Z")
        self.assertEqual(il.unreplayed_verdicts(self.ledger, self.vdir),
                         ["codex-20261108T045905Z-87d4be45"])

    def test_unparseable_stamp_does_not_crash(self) -> None:
        self.write_ledger(ledger_row("20261028T053300Z-55114152", "accomplished", "desi", "not a time"))
        self.write_mirror("x", "20261028T053300Z-55114152", "accomplished", "dmitri",
                          "20261108T065358Z")
        self.assertEqual(il.unreplayed_verdicts(self.ledger, self.vdir),
                         ["20261028T053300Z-55114152"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
