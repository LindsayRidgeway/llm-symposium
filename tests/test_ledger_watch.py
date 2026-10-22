"""Tests for scripts/ledger_watch.py — the daily check that repairs what a refused landing ate.

The point of these tests is the two judgements that are easy to get wrong and expensive to get wrong
in production: which verdict to believe when an item was reviewed twice, and how to tell a patch
that carried a verdict from one that carried only prose.
"""

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "channels"))

spec = importlib.util.spec_from_file_location("ledger_watch", REPO / "scripts" / "ledger_watch.py")
lw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lw)


class ChooseVerdictTest(unittest.TestCase):
    def test_two_reviews_of_one_item_keep_the_first_real_one(self):
        """The 2026-10-22 loop: reviewed at 05:16, verdict lost to the landing gate, reviewed again
        at 09:17, and the second wake wrote 'postponed: review already written'. The first verdict
        is the record; the second is evidence of the loop."""
        cands = [
            ("20261022T051617Z", {"state": "accomplished",
                                  "reason": "Reviewed against the primary reference; run 20261021T231529Z-859769d9"}),
            ("20261022T091715Z", {"state": "postponed",
                                  "reason": "Review already written, not missing: run 20261022T051617Z changed"}),
        ]
        stamp, rec = lw.choose_verdict(cands)
        self.assertEqual(stamp, "20261022T051617Z")
        self.assertEqual(rec["state"], "accomplished")

    def test_a_later_genuine_postponement_wins_when_nothing_was_accomplished(self):
        cands = [
            ("20261020T031124Z", {"state": "postponed", "reason": "awaiting the vendor's manual"}),
            ("20261020T131245Z", {"state": "postponed", "reason": "still no manual; asked vendor again"}),
        ]
        stamp, rec = lw.choose_verdict(cands)
        self.assertEqual(stamp, "20261020T131245Z")

    def test_an_accomplished_verdict_that_names_no_work_does_not_outrank_a_named_one(self):
        cands = [
            ("20261019T000000Z", {"state": "accomplished", "reason": "looked at it"}),
            ("20261019T010000Z", {"state": "accomplished", "reason": "wrote research/x.md, run 20261019T010000Z"}),
        ]
        stamp, _ = lw.choose_verdict(cands)
        self.assertEqual(stamp, "20261019T010000Z")


class PatchParsingTest(unittest.TestCase):
    def _write(self, text: str) -> Path:
        tmp = Path(tempfile.mkdtemp()) / "changes.patch"
        tmp.write_text(text, encoding="utf-8")
        return tmp

    def test_terminal_rows_are_read_out_of_a_refused_patch(self):
        row = {"id": "abc", "state": "accomplished", "reviewer": "desi", "reason": "run 20261021T131453Z-x"}
        patch = self._write("diff --git a/channels/items.jsonl b/channels/items.jsonl\n"
                            f"+{json.dumps(row)}\n")
        rows = lw.verdict_rows_in_patch(patch)
        self.assertEqual([r["id"] for r in rows], ["abc"])

    def test_a_patch_touching_no_ledger_returns_nothing(self):
        patch = self._write("diff --git a/docs/music/index.html b/docs/music/index.html\n+x\n")
        self.assertEqual(lw.verdict_rows_in_patch(patch), [])

    def test_a_ledger_patch_that_only_assigns_returns_nothing(self):
        row = {"id": "abc", "assigned_to": "dmitri", "assign_reason": "drawn"}
        patch = self._write("diff --git a/channels/items.jsonl b/channels/items.jsonl\n"
                            f"+{json.dumps(row)}\n")
        self.assertEqual(lw.verdict_rows_in_patch(patch), [])

    def test_a_removed_line_is_not_a_verdict_added(self):
        row = {"id": "abc", "state": "accomplished", "reviewer": "desi", "reason": "run 1"}
        patch = self._write("diff --git a/channels/items.jsonl b/channels/items.jsonl\n"
                            f"-{json.dumps(row)}\n")
        self.assertEqual(lw.verdict_rows_in_patch(patch), [])


class VerdictRuleTest(unittest.TestCase):
    def test_meeting_the_rule_is_a_pass(self):
        m = {"queue": 12, "arrivals_24h": 23, "pile": 0, "model_decisions_24h": 0}
        passes, reasons = lw.verdict(m, None)
        self.assertTrue(passes)
        self.assertIn("one day of arrivals", reasons[0])

    def test_an_empty_day_still_counts_as_one_arrival_not_zero(self):
        """A day with no filings must not make the rule 'queue <= 0', which nothing can pass."""
        m = {"queue": 1, "arrivals_24h": 0, "pile": 0, "model_decisions_24h": 0}
        passes, _ = lw.verdict(m, None)
        self.assertTrue(passes)

    def test_a_growing_queue_fails_and_says_by_how_much(self):
        m = {"queue": 72, "arrivals_24h": 23, "pile": 228, "model_decisions_24h": 1}
        passes, reasons = lw.verdict(m, {"queue": 58, "pile": 227})
        self.assertFalse(passes)
        self.assertIn("72 waiting against 23", reasons[0])
        self.assertIn("up 14", reasons[1])


if __name__ == "__main__":
    unittest.main()
