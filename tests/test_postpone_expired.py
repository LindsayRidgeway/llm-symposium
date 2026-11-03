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



class TestTheClassOfTheReason(unittest.TestCase):
    """Which classes the tree can decide, and which it cannot (2026-11-03, Desi).

    `postpone_expired` lists rows whose *claimed* paths are all on main. The class is about a
    different set — the paths the **reason** names — because the reason is where the blocker is
    stated. Measured on the 66 expired rows in Desi's scope on 2026-11-03: 38 reasons named paths
    that have all arrived, 8 named at least one still missing, 20 named no path at all. The last
    group is the point: for those, file presence is a coincidence of what the run touched, and a
    reviewer must read the run. Nothing here is a verdict — the pass still writes nothing.
    """

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

    def test_a_reason_naming_only_present_paths_is_delivery_state(self):
        self.touch("channels/reports/r.md")
        verdict = il.classify_postponement("waiting for channels/reports/r.md to land", self.repo)
        self.assertEqual(verdict["klass"], "delivery-state")
        self.assertEqual(verdict["reason_paths"], ["channels/reports/r.md"])
        self.assertEqual(verdict["reason_missing"], [])

    def test_a_reason_naming_a_missing_path_is_a_live_blocker(self):
        """Presence of the row's own paths must not close a row whose reason names something absent."""
        self.touch("scripts/done.py")
        verdict = il.classify_postponement(
            "blocked on channels/reports/never-written.md", self.repo)
        self.assertEqual(verdict["klass"], "blocker-stands")
        self.assertEqual(verdict["reason_missing"], ["channels/reports/never-written.md"])

    def test_a_reason_naming_no_path_is_unclassified(self):
        """The commonest case in the live ledger: a judgement about work, not about a file."""
        verdict = il.classify_postponement(
            "the run was cut off at its cap and left no finished artefact", self.repo)
        self.assertEqual(verdict["klass"], "unclassified")
        self.assertEqual(verdict["reason_paths"], [])

    def test_the_ledger_path_alone_proves_nothing(self):
        """Every wake writes channels/items.jsonl, so a reason naming only that names nothing."""
        self.touch(il.LEDGER_PATH)
        verdict = il.classify_postponement(f"see {il.LEDGER_PATH}", self.repo)
        self.assertEqual(verdict["klass"], "unclassified")

    def test_prose_and_version_numbers_are_not_paths(self):
        """A loose matcher would invent paths and manufacture delivery-states."""
        self.assertEqual(il.paths_named_in_reason("e.g. 2026-11-03, v1.2, 42 item(s)"), [])
        self.assertEqual(il.paths_named_in_reason("a bare `report.txt` basename"), [])

    def test_a_trailing_line_number_is_not_part_of_the_path(self):
        self.touch("scripts/item_ledger.py")
        self.assertEqual(il.paths_named_in_reason("see scripts/item_ledger.py:1000"),
                         ["scripts/item_ledger.py"])

    def test_only_class_filters_the_list_and_writes_nothing(self):
        self.touch("channels/reports/here.md")
        write_ledger(self.ledger, [
            postponed("delivered", ["channels/reports/here.md"],
                      reason="waiting for channels/reports/here.md"),
            postponed("judged", ["channels/reports/here.md"],
                      reason="the payload never existed and the run was cut off"),
        ])
        before = hashlib.sha256(self.ledger.read_bytes()).hexdigest()
        got = il.postpone_expired(path=self.ledger, repo=self.repo, only_class="delivery-state")
        self.assertEqual([c["id"] for c in got], ["delivered"])
        self.assertEqual(got[0]["klass"], "delivery-state")
        self.assertEqual(il.postpone_expired(path=self.ledger, repo=self.repo,
                                             only_class="unclassified")[0]["id"], "judged")
        self.assertEqual(hashlib.sha256(self.ledger.read_bytes()).hexdigest(), before)

    def test_the_cli_prints_a_count_per_class(self):
        out = subprocess.run([sys.executable, "channels/item_ledger.py", "--postpone-expired",
                              "--scope", "desi"], cwd=REPO, capture_output=True, text=True,
                             timeout=180)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("by class:", out.stdout)
        self.assertIn("delivery-state", out.stdout)


if __name__ == "__main__":
    unittest.main()
