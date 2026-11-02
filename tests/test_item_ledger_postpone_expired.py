#!/usr/bin/env python3
"""The pass that re-reads postponed rows — and the one thing it must never do.

Pinned here:
  1. a postponed row whose named blocker is now on main is reported as expired;
  2. a row still missing any named path is reported as partial, never as expired;
  3. only `postponed` rows are touched — an accomplished or waiting row is not this pass's business;
  4. the blocker is read from the reviewer's prose as well as from the run's `paths`, because since
     2026-10-31 the reason is where the missing file is actually named;
  5. the pass writes nothing. It is a report for a human verdict; a machine that closed these would
     be stamping `accomplished` over a judgement nobody made.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from channels import item_ledger as il  # noqa: E402


def row(item_id, state, paths, reason, state_utc="2026-11-01T01:01:58Z", amigo="dmitri",
        reviewer="gemini"):
    return {"id": item_id, "amigo": amigo, "reviewer": reviewer, "state": state,
            "state_utc": state_utc, "filed_utc": "2026-10-31T02:25:37Z", "paths": paths,
            "reason": reason, "title": item_id, "scope": "internal"}


class PostponeExpired(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        (self.repo / "scripts").mkdir(parents=True)
        (self.repo / "channels" / "reports").mkdir(parents=True)
        self.ledger = self.root / "items.jsonl"

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rows):
        self.ledger.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")

    def test_a_postponed_row_whose_blocker_arrived_is_expired(self):
        (self.repo / "scripts" / "recover.py").write_text("x", encoding="utf-8")
        self.write([row("A", "postponed", ["scripts/recover.py"],
                        "scripts/recover.py is absent from main")])
        out = il.postpone_expired(path=self.ledger, repo=self.repo)
        self.assertEqual([r["id"] for r in out], ["A"])
        self.assertTrue(out[0]["expired"])
        self.assertEqual(out[0]["missing"], [])

    def test_one_missing_path_is_not_an_expired_blocker(self):
        (self.repo / "scripts" / "recover.py").write_text("x", encoding="utf-8")
        self.write([row("B", "postponed", ["scripts/recover.py", "scripts/still-gone.py"],
                        "two files absent")])
        out = il.postpone_expired(path=self.ledger, repo=self.repo)
        self.assertFalse(out[0]["expired"])
        self.assertEqual(out[0]["missing"], ["scripts/still-gone.py"])
        self.assertEqual(out[0]["present"], ["scripts/recover.py"])

    def test_only_postponed_rows_are_reported(self):
        (self.repo / "scripts" / "recover.py").write_text("x", encoding="utf-8")
        self.write([
            row("C", "accomplished", ["scripts/recover.py"], "done"),
            row("D", None, ["scripts/recover.py"], "waiting"),
            row("E", "postponed", ["scripts/recover.py"], "absent"),
        ])
        self.assertEqual([r["id"] for r in il.postpone_expired(path=self.ledger, repo=self.repo)],
                         ["E"])

    def test_the_blocker_is_read_from_the_reviewers_prose(self):
        # The row's own `paths` are the run's output and are on main; the *reason* names the file
        # that was missing. A pass reading only `paths` would call this expired on the wrong grounds.
        (self.repo / "channels" / "reports" / "r.md").write_text("x", encoding="utf-8")
        self.write([row("F", "postponed", ["channels/reports/r.md"],
                        "Postponed: `channels/reports/r.md` and scripts/never-here.py are absent")])
        out = il.postpone_expired(path=self.ledger, repo=self.repo)
        self.assertFalse(out[0]["expired"])
        self.assertIn("scripts/never-here.py", out[0]["missing"])
        self.assertIn("channels/reports/r.md", out[0]["named"])

    def test_the_pass_writes_nothing(self):
        (self.repo / "scripts" / "recover.py").write_text("x", encoding="utf-8")
        self.write([row("G", "postponed", ["scripts/recover.py"], "absent")])
        before = self.ledger.read_bytes()
        il.postpone_expired(path=self.ledger, repo=self.repo)
        self.assertEqual(self.ledger.read_bytes(), before)

    def test_a_row_that_names_nothing_checkable_is_skipped(self):
        self.write([row("H", "postponed", [], "postponed until the human answers")])
        self.assertEqual(il.postpone_expired(path=self.ledger, repo=self.repo), [])

    def test_oldest_wrong_postponement_sorts_first(self):
        (self.repo / "scripts" / "recover.py").write_text("x", encoding="utf-8")
        self.write([
            row("newer", "postponed", ["scripts/recover.py"], "absent",
                state_utc="2026-11-02T01:00:00Z"),
            row("older", "postponed", ["scripts/recover.py"], "absent",
                state_utc="2026-10-20T01:00:00Z"),
            row("partial", "postponed", ["scripts/recover.py", "scripts/gone.py"], "absent",
                state_utc="2026-10-01T01:00:00Z"),
        ])
        ids = [r["id"] for r in il.postpone_expired(path=self.ledger, repo=self.repo)]
        self.assertEqual(ids, ["older", "newer", "partial"])


if __name__ == "__main__":
    unittest.main()
