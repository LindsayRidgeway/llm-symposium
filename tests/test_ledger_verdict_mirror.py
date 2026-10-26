#!/usr/bin/env python3
"""A verdict must survive the run that wrote it (scripts/ledger_verdict_mirror.py).

The defect this pins is the loop, not a bug: `item_ledger.py --review` records a verdict by
appending one line to `channels/items.jsonl`, a 3,000-line file main also appends to live.
Delivery applies a patch, the patch carries that file's tail as context, the context is stale
within minutes, the hunk fails, and `git apply` being atomic, the whole run is discarded —
verdict included. The item returns to `waiting` and the next wake reviews it again.

Measured on two consecutive wakes of 2026-10-26 (runs 20261026T094058Z-eb5c4d6e and
20261026T114111Z-bdc12b38): the same item, codex-20261026T082005Z-93ddaeaa, reviewed twice in
one day, the first verdict lost. Same mechanism as the 2026-10-23 lost delivery.

The mirror writes each verdict as its own one-line file under `channels/ledger-verdicts/`, which
is a clean add and always applies, and `replay` folds it back into the ledger idempotently and
never backwards. These cases are all temp-directory work — nothing here touches the live ledger.

Run: python3 tests/test_ledger_verdict_mirror.py
"""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "channels"))

_spec = importlib.util.spec_from_file_location(
    "ledger_verdict_mirror", REPO / "scripts" / "ledger_verdict_mirror.py")
lvm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lvm)

ROW = {"id": "codex-test-1", "amigo": "tarik", "state": None, "state_utc": None,
       "reviewer": None, "reason": None, "title": "a test item", "source": "codex"}


class LedgerVerdictMirrorTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.verdicts = self.tmp / "ledger-verdicts"
        self.ledger = self.tmp / "items.jsonl"
        self.ledger.write_text(json.dumps(ROW, sort_keys=True) + "\n", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def lines(self):
        return self.ledger.read_text().strip().splitlines()

    def test_mirror_writes_one_named_file(self):
        path = lvm.mirror("codex-test-1", "accomplished", "dmitri", "did the work: ran 1",
                          "run-1", self.verdicts, "2026-10-26T11:41:50Z")
        rec = json.loads(path.read_text())
        self.assertEqual(rec["id"], "codex-test-1")
        self.assertEqual(rec["state"], "accomplished")
        self.assertEqual(rec["reviewer"], "dmitri")
        self.assertEqual(rec["run"], "run-1")
        self.assertEqual(path.name, "20261026T114150Z-codex-test-1.json")

    def test_mirror_refuses_a_verdict_with_no_record(self):
        bad = [
            {"state": "maybe"},
            {"state": "accomplished", "reviewer": " "},
            {"state": "accomplished", "reviewer": "dmitri", "reason": "   "},
        ]
        for case in bad:
            kwargs = {"item_id": "codex-test-1", "state": "accomplished", "reviewer": "dmitri",
                      "reason": "did the work: ran 1", "verdicts": self.tmp / "v2"}
            kwargs.update(case)
            with self.assertRaises(SystemExit, msg=f"mirror accepted {case}"):
                lvm.mirror(**kwargs)

    def test_replay_folds_the_verdict_in_and_is_idempotent(self):
        lvm.mirror("codex-test-1", "postponed", "dmitri", "blocked on a merger", "",
                   self.verdicts, "2026-10-26T11:41:50Z")
        first = lvm.replay(self.ledger, self.verdicts)
        self.assertEqual(first["applied"], ["codex-test-1"])
        self.assertEqual(first["skipped"], [])
        self.assertEqual(len(self.lines()), 2)
        live = json.loads(self.lines()[-1])
        self.assertEqual(live["state"], "postponed")
        self.assertEqual(live["reviewer"], "dmitri")
        # the replay must not throw away the rest of the item's row
        self.assertEqual(live["title"], "a test item")

        second = lvm.replay(self.ledger, self.verdicts)
        self.assertEqual(second["applied"], [])
        self.assertEqual(second["skipped"], ["codex-test-1"])
        self.assertEqual(len(self.lines()), 2, "replaying twice must not append twice")

    def test_replay_never_walks_a_verdict_backwards(self):
        lvm.mirror("codex-test-1", "accomplished", "dmitri", "did the work: ran 2", "",
                   self.verdicts, "2026-10-26T12:00:00Z")
        lvm.replay(self.ledger, self.verdicts)
        lvm.mirror("codex-test-1", "postponed", "tarik", "older verdict", "",
                   self.verdicts, "2026-10-26T09:00:00Z")
        result = lvm.replay(self.ledger, self.verdicts)
        self.assertEqual(result["applied"], [])
        self.assertIn("codex-test-1", result["skipped"])
        live = json.loads(self.lines()[-1])
        self.assertEqual(live["state"], "accomplished")
        self.assertEqual(live["reviewer"], "dmitri")

    def test_replay_names_an_unknown_item_instead_of_inventing_it(self):
        lvm.mirror("codex-not-in-the-ledger", "rejected", "dmitri", "never do this", "",
                   self.verdicts, "2026-10-26T11:41:50Z")
        result = lvm.replay(self.ledger, self.verdicts)
        self.assertEqual(result["unknown"], ["codex-not-in-the-ledger"])
        self.assertEqual(result["applied"], [])
        self.assertEqual(len(self.lines()), 1)

    def test_dry_run_changes_nothing(self):
        lvm.mirror("codex-test-1", "accomplished", "dmitri", "did the work: ran 3", "",
                   self.verdicts, "2026-10-26T11:41:50Z")
        result = lvm.replay(self.ledger, self.verdicts, dry_run=True)
        self.assertEqual(result["applied"], ["codex-test-1"])
        self.assertEqual(len(self.lines()), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
