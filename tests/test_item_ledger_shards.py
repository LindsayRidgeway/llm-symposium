#!/usr/bin/env python3
# Owner: Dmitri
"""A wake's ledger row must go to a file no other run can collide with.

Why this file exists (2026-10-23). The lander replays a run's `changes.patch` with `git apply`,
which is atomic over the whole patch. `channels/items.jsonl` is the commons' only write-hot file —
every wake that files, assigns or reviews appends at the same end of it — so by the time a run's
patch is replayed its ledger hunk no longer matches main, and one stale hunk discards *every* file
the run wrote: verdicts, report, artefact. Measured on item `20261019T170221Z-c56a22e8`, marked
`accomplished` by three wakes and still `state=null` on main, and on the 137 review rows discarded
with run `20261013T170314Z-0838fbd7`.

The fix is not to merge better: it is to stop the wake writing to the shared file at all. A row goes
to `channels/ledger-shards/<run id>.jsonl`, which no other writer touches, so its hunk always
applies. `load()` reads the shards after the ledger and lets the later-dated row win, so a shard is
part of the record rather than a side channel — which is what these checks pin.
"""
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


def _load_module():
    path = Path(__file__).resolve().parent.parent / "channels" / "item_ledger.py"
    spec = importlib.util.spec_from_file_location("item_ledger_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class ShardWriteTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.channels = self.root / "channels"
        self.channels.mkdir()
        self.ledger = self.channels / "items.jsonl"
        self.ledger.write_text(
            json.dumps({"id": "a1", "filed_utc": "2026-10-01T00:00:00Z",
                        "state": None, "paths": ["x.md"]}) + "\n",
            encoding="utf-8")
        self.il = _load_module()
        self.il.REPO = self.root
        self.il.LEDGER = self.ledger
        os.environ.pop("SYMPOSIUM_RUN_ID", None)

    def _in_wake(self, run_id="20261023T093101Z-6cfc39d8"):
        self.il.REPO = self.root / "tick-state" / "runs" / run_id / "repo"
        self.il.REPO.mkdir(parents=True, exist_ok=True)

    def test_outside_a_wake_checkout_rows_still_go_to_the_ledger(self):
        self.assertEqual(self.il.write_path(self.ledger), self.ledger)
        self.assertEqual(self.il._run_id(), "")

    def test_a_wake_writes_a_shard_and_leaves_the_ledger_alone(self):
        self._in_wake()
        self.assertEqual(self.il._run_id(), "20261023T093101Z-6cfc39d8")
        before = self.ledger.read_text(encoding="utf-8")
        self.il.append([{"id": "a1", "state": "postponed",
                         "state_utc": "2026-10-23T09:31:01Z", "reason": "r"}], self.ledger)
        self.assertEqual(self.ledger.read_text(encoding="utf-8"), before,
                         "the shared ledger must not be touched by a wake")
        shard = self.channels / "ledger-shards" / "20261023T093101Z-6cfc39d8.jsonl"
        self.assertTrue(shard.exists(), "the row went nowhere a replay could pick up")
        self.assertIn("postponed", shard.read_text(encoding="utf-8"))

    def test_load_reads_the_shard_as_part_of_the_record(self):
        self._in_wake()
        self.il.append([{"id": "a1", "state": "postponed",
                         "state_utc": "2026-10-23T09:31:01Z", "reason": "r"}], self.ledger)
        items = self.il.load(self.ledger)
        self.assertEqual(items["a1"]["state"], "postponed")

    def test_a_shard_may_not_undo_a_newer_verdict(self):
        shard_dir = self.channels / "ledger-shards"
        shard_dir.mkdir()
        (shard_dir / "20261023T093101Z-6cfc39d8.jsonl").write_text(
            json.dumps({"id": "a1", "state": "postponed",
                        "state_utc": "2026-10-20T00:00:00Z", "reason": "old"}) + "\n",
            encoding="utf-8")
        with self.ledger.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"id": "a1", "state": "accomplished",
                                 "state_utc": "2026-10-22T00:00:00Z", "reason": "new"}) + "\n")
        self.assertEqual(self.il.load(self.ledger)["a1"]["state"], "accomplished")

    def test_the_run_id_comes_from_the_checkout_path_and_sorts_by_time(self):
        self._in_wake("20261023T093101Z-6cfc39d8")
        earlier = self.il.write_path(self.ledger)
        self._in_wake("20261024T010000Z-aaaaaaaa")
        later = self.il.write_path(self.ledger)
        self.assertLess(earlier.name, later.name, "shard names must sort chronologically")


if __name__ == "__main__":
    unittest.main(verbosity=2)
