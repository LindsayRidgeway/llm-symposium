#!/usr/bin/env python3
"""Tests for `item_ledger.py --postpone-expired`.

The pass exists because a `postponed` row is never revisited by any machine: `reconcile_paths`
touches only rows still in W, so a postponement whose stated blocker was "this file is not on main"
keeps saying "waiting" about work that landed hours later. Measured 2026-11-02: 102 postponed rows
in the live ledger now name only paths that are present.

Three things are pinned here, in the order the human's rules put them:

  1. it FINDS the expired case — a postponed row whose every named path is now on main;
  2. it does NOT invent one — a missing path is still a live blocker, a waiting or accomplished row
     is not a postponement, and a row whose only path is the ledger itself is skipped for the same
     reason `reconcile_paths` skips it (every wake writes that file, so it proves nothing);
  3. it WRITES NOTHING — not the row, not a stamp, not to the ledger file. Which postponements ask
     a dead question is a fact about the tree; which verdict replaces one is a judgement, and a
     machine that flipped the row on file presence would be writing the stamp the human forbade on
     2026-10-09 under a new name.
"""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from channels import item_ledger as il  # noqa: E402


def write_ledger(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8")


def postponed(item_id: str, paths: list[str], reason: str = "waiting for a file",
              amigo: str = "gemini", reviewer: str = "desi",
              state_utc: str = "2026-11-01T01:01:58Z", **extra) -> dict:
    row = {"id": item_id, "amigo": amigo, "state": "postponed", "reviewer": reviewer,
           "state_utc": state_utc, "reason": reason, "paths": paths}
    row.update(extra)
    return row


class TestPostponeExpired(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.ledger = self.root / "items.jsonl"

    def tearDown(self):
        self._tmp.cleanup()

    def touch(self, rel: str) -> None:
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x", encoding="utf-8")

    def test_a_postponed_row_whose_paths_all_landed_is_reported(self):
        self.touch("scripts/recover.py")
        self.touch("tests/test_recover.py")
        write_ledger(self.ledger, [
            postponed("20261031T022537Z-20f65972", ["scripts/recover.py", "tests/test_recover.py"]),
        ])
        cases = il.postpone_expired(path=self.ledger, repo=self.repo)
        self.assertEqual([c["id"] for c in cases], ["20261031T022537Z-20f65972"])
        self.assertEqual(cases[0]["reviewer"], "desi")
        self.assertEqual(len(cases[0]["paths"]), 2)

    def test_one_missing_path_keeps_the_blocker_alive(self):
        self.touch("scripts/recover.py")
        write_ledger(self.ledger, [
            postponed("still-waiting", ["scripts/recover.py", "channels/reports/never-landed.md"]),
        ])
        self.assertEqual(il.postpone_expired(path=self.ledger, repo=self.repo), [])

    def test_rows_that_are_not_postponements_are_ignored(self):
        self.touch("a.py")
        rows = [
            {"id": "w-row", "amigo": "desi", "state": "waiting", "paths": ["a.py"]},
            {"id": "a-row", "amigo": "desi", "state": "accomplished", "reviewer": "auto:path",
             "state_utc": "2026-11-01T00:00:00Z", "reason": "delivered", "paths": ["a.py"]},
            {"id": "r-row", "amigo": "desi", "state": "rejected", "reviewer": "desi",
             "state_utc": "2026-11-01T00:00:00Z", "reason": "should never be done",
             "paths": ["a.py"]},
        ]
        write_ledger(self.ledger, rows)
        self.assertEqual(il.postpone_expired(path=self.ledger, repo=self.repo), [])

    def test_a_ledger_only_row_is_skipped(self):
        """Its only path is written by every wake, so presence answers nothing."""
        write_ledger(self.ledger, [postponed("ledger-only", [il.LEDGER_PATH])])
        self.assertEqual(il.postpone_expired(path=self.ledger, repo=self.repo), [])

    def test_the_list_is_ordered_oldest_first(self):
        self.touch("a.py")
        write_ledger(self.ledger, [
            postponed("newer", ["a.py"], state_utc="2026-11-01T09:00:00Z"),
            postponed("older", ["a.py"], state_utc="2026-10-13T23:06:29Z"),
        ])
        cases = il.postpone_expired(path=self.ledger, repo=self.repo)
        self.assertEqual([c["id"] for c in cases], ["older", "newer"])

    def test_scope_limits_the_list_to_one_amigo(self):
        self.touch("a.py")
        write_ledger(self.ledger, [
            postponed("mine", ["a.py"], amigo="desi"),
            postponed("theirs", ["a.py"], amigo="dmitri"),
            postponed("named-to-me", ["a.py"], amigo="tarik", assigned_to="desi"),
        ])
        got = {c["id"] for c in il.postpone_expired(path=self.ledger, repo=self.repo,
                                                    scope="desi")}
        self.assertEqual(got, {"mine", "named-to-me"})

    def test_the_pass_writes_nothing_to_the_ledger(self):
        self.touch("a.py")
        write_ledger(self.ledger, [postponed("gone-stale", ["a.py"])])
        before = hashlib.sha256(self.ledger.read_bytes()).hexdigest()
        il.postpone_expired(path=self.ledger, repo=self.repo)
        after = hashlib.sha256(self.ledger.read_bytes()).hexdigest()
        self.assertEqual(before, after, "the pass must not touch the file it reads")
        # and the row is still postponed: finding an expired blocker is not a verdict
        row = il.load(self.ledger)["gone-stale"]
        self.assertEqual(row["state"], "postponed")


class TestCli(unittest.TestCase):
    """The flag has to be reachable — a function with no way to invoke it is not a tool."""

    def run_cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "channels/item_ledger.py", *args], cwd=REPO,
                              capture_output=True, text=True, timeout=180)

    def test_the_flag_exists_and_reports_without_writing(self):
        ledger = REPO / "channels" / "items.jsonl"
        before = hashlib.sha256(ledger.read_bytes()).hexdigest()
        res = self.run_cli("--postpone-expired")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("postponed item(s)", res.stdout)
        self.assertIn("nothing was written", res.stdout)
        self.assertEqual(before, hashlib.sha256(ledger.read_bytes()).hexdigest(),
                         "--postpone-expired must not append to the live ledger")

    def test_scope_is_accepted(self):
        res = self.run_cli("--postpone-expired", "--scope", "desi")
        self.assertEqual(res.returncode, 0, res.stderr)


if __name__ == "__main__":
    unittest.main()
