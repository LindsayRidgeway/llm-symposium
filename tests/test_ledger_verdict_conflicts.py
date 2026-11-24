"""A reviewer's verdict must not be discharged by the landing machine's stamp.

Written 2026-11-23 (Dmitri) with `scripts/ledger_verdict_conflicts.py`. The instrument exists
because two tools disagreed in public and both were right: `item_ledger --queue` said 24 verdicts
were not folded in, and `ledger_verdict_mirror.py replay` said there was nothing to fold. `replay`
never walks a ledger row backwards, so a mirror older than the row it would replace is skipped —
and when that row is a machine stamp (`auto:land` / `auto:path`), a model's `postponed` or
`rejected` has been replaced by delivery. These tests pin the classification, not the count: the
count is live data and moves every hour.
"""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "channels"))

SPEC = importlib.util.spec_from_file_location(
    "ledger_verdict_conflicts", REPO / "scripts" / "ledger_verdict_conflicts.py")
LVC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LVC)


def mirror(dirpath, item_id, state, utc, reviewer="gemini", reason="why"):
    p = Path(dirpath) / f"{utc.replace('-', '').replace(':', '')}-{item_id}.json"
    p.write_text(json.dumps({"id": item_id, "state": state, "state_utc": utc,
                             "reviewer": reviewer, "reason": reason}), encoding="utf-8")
    return p


class Classification(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.vdir = self.root / "ledger-verdicts"
        self.vdir.mkdir()
        self.ledger = self.root / "items.jsonl"

    def tearDown(self):
        self.tmp.cleanup()

    def write_ledger(self, rows):
        self.ledger.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")

    def test_reviewer_postponed_then_machine_accomplished_is_a_reversal(self):
        """The measured pattern: judged at 13:32Z, landed at 13:49Z, item reads accomplished."""
        self.write_ledger([{"id": "A", "state": "accomplished",
                            "state_utc": "2026-11-22T13:49:55Z", "reviewer": "auto:land"}])
        mirror(self.vdir, "A", "postponed", "2026-11-22T13:34:19Z")
        rows = LVC.conflicts(self.ledger, self.vdir)
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["reversed"])
        self.assertTrue(rows[0]["halting"])
        self.assertEqual(rows[0]["mirror_state"], "postponed")

    def test_a_human_reviewer_may_supersede_an_earlier_verdict(self):
        """A later *review* standing on an earlier one is the queue working, not a conflict."""
        self.write_ledger([{"id": "A", "state": "rejected",
                            "state_utc": "2026-11-22T23:00:00Z", "reviewer": "desi"}])
        mirror(self.vdir, "A", "postponed", "2026-11-22T13:34:19Z")
        self.assertEqual(LVC.conflicts(self.ledger, self.vdir), [])

    def test_machine_stamp_that_agrees_is_counted_but_not_reversed(self):
        """Same state, reviewer replaced: not a reversal, and the same loss of the reason."""
        self.write_ledger([{"id": "B", "state": "accomplished",
                            "state_utc": "2026-11-21T12:45:10Z", "reviewer": "auto:path",
                            "path_check": True}])
        mirror(self.vdir, "B", "accomplished", "2026-11-21T11:16:00Z", reviewer="gwen")
        rows = LVC.conflicts(self.ledger, self.vdir)
        self.assertEqual(len(rows), 1)
        self.assertFalse(rows[0]["reversed"])
        s = LVC.summarise(rows)
        self.assertEqual((s["conflicts"], s["reversed"], s["same_state"]), (1, 0, 1))

    def test_a_mirror_newer_than_the_row_is_left_to_replay(self):
        """Not this instrument's business: replay applies those, and it does move forward."""
        self.write_ledger([{"id": "C", "state": "accomplished",
                            "state_utc": "2026-11-21T00:00:00Z", "reviewer": "auto:path"}])
        mirror(self.vdir, "C", "postponed", "2026-11-22T00:00:00Z")
        self.assertEqual(LVC.conflicts(self.ledger, self.vdir), [])

    def test_undatable_mirror_is_not_ordered_by_text(self):
        """A compact or malformed stamp cannot be shown to be older, so it is not called one."""
        self.write_ledger([{"id": "D", "state": "accomplished",
                            "state_utc": "2026-11-21T00:00:00Z", "reviewer": "auto:land"}])
        mirror(self.vdir, "D", "postponed", "not-a-date")
        self.assertEqual(LVC.conflicts(self.ledger, self.vdir), [])

    def test_check_exits_three_only_when_a_verdict_was_reversed(self):
        self.write_ledger([{"id": "A", "state": "accomplished",
                            "state_utc": "2026-11-22T13:49:55Z", "reviewer": "auto:land"}])
        mirror(self.vdir, "A", "postponed", "2026-11-22T13:34:19Z")
        code = LVC.main(["--ledger", str(self.ledger), "--verdicts", str(self.vdir), "--check"])
        self.assertEqual(code, 3)
        self.write_ledger([{"id": "A", "state": "accomplished",
                            "state_utc": "2026-11-22T13:49:55Z", "reviewer": "desi"}])
        code = LVC.main(["--ledger", str(self.ledger), "--verdicts", str(self.vdir), "--check"])
        self.assertEqual(code, 0)


class LiveLedger(unittest.TestCase):
    """The real ledger, read only: whatever the count is, the reader must agree with itself."""

    def test_every_conflict_is_also_a_mirror_the_ledger_tool_calls_unreplayed(self):
        pending = set(LVC.item_ledger.unreplayed_verdicts(LVC.LEDGER, LVC.VERDICTS))
        rows = LVC.conflicts(LVC.LEDGER, LVC.VERDICTS)
        for r in rows:
            self.assertIn(r["id"], pending,
                          f"{r['id']} is a conflict but item_ledger does not call it unreplayed")

    def test_summary_counts_agree_with_the_rows(self):
        rows = LVC.conflicts(LVC.LEDGER, LVC.VERDICTS)
        s = LVC.summarise(rows)
        self.assertEqual(s["conflicts"], len(rows))
        self.assertEqual(s["reversed"] + s["same_state"], s["conflicts"])


if __name__ == "__main__":
    unittest.main()
