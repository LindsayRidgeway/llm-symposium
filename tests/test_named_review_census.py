#!/usr/bin/env python3
"""Tests for scripts/named_review_census.py.

Dmitri, 2026-11-02. The census answers one question — did the amigo a review was
named to ever answer it? — and its own failure mode is the one it measures: a
count that cannot tell "closed" from "reviewed", or that misses the second copy
of a row and reports an item still open after it was closed. So each of the four
outcomes is pinned to a synthetic ledger here, and the two ways the reader can
lie (a stale row winning, an unreadable ledger printing a clean zero) are
exercised directly.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import scripts.named_review_census as census  # noqa: E402


def write_ledger(rows):
    handle = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8")
    with handle as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    return Path(handle.name)


ASSIGN = {"id": "x", "assigned_to": "gemini", "assigned_utc": "2026-10-01T00:00:00Z"}


class TestClassify(unittest.TestCase):
    def test_named_amigo_who_answered_counts_as_answered(self):
        rows = [ASSIGN, {"id": "x", "reviewer": "gemini", "state": "accomplished"}]
        self.assertEqual(census.classify(rows)["outcome"], "answered")

    def test_a_verdict_from_a_different_amigo_is_not_the_named_amigo_answering(self):
        rows = [ASSIGN, {"id": "x", "reviewer": "dmitri", "state": "accomplished",
                         "reason": "closed: every path present"}]
        verdict = census.classify(rows)
        self.assertEqual(verdict["outcome"], "read-elsewhere")
        self.assertEqual(verdict["read_by"], ["dmitri"])

    def test_closed_by_the_landing_gate_with_no_model_verdict_is_gate_closed(self):
        rows = [ASSIGN, {"id": "x", "reviewer": "auto:path", "state": "accomplished"}]
        verdict = census.classify(rows)
        self.assertEqual(verdict["outcome"], "gate-closed")
        self.assertEqual(verdict["closed_by"], "auto:path")

    def test_no_verdict_at_all_is_open_not_gate_closed(self):
        self.assertEqual(census.classify([ASSIGN])["outcome"], "open")

    def test_an_item_nobody_was_assigned_is_not_counted(self):
        self.assertIsNone(census.classify([{"id": "x", "path": "a"}])["outcome"])

    def test_a_later_copy_of_the_row_wins(self):
        """The ledger is append-only: the assignment arrives on a second copy."""
        rows = [{"id": "x", "state": "accomplished", "reviewer": "auto:land"},
                ASSIGN]
        self.assertEqual(census.classify(rows)["assigned_to"], "gemini")

    def test_a_non_amigo_assignee_is_not_a_named_review(self):
        self.assertIsNone(census.classify([{"id": "x", "assigned_to": "lindsay"}])["outcome"])


class TestCensus(unittest.TestCase):
    def setUp(self):
        self.rows = {
            "a": [ASSIGN, {"id": "a", "reviewer": "gemini", "state": "accomplished"}],
            "b": [{"id": "b", "assigned_to": "desi"}, {"id": "b", "reviewer": "auto:path",
                                                       "state": "accomplished"}],
            "c": [{"id": "c", "assigned_to": "tarik"},
                  {"id": "c", "reviewer": "claude", "state": "postponed"}],
            "d": [{"id": "d", "assigned_to": "dmitri"}],
            "e": [{"id": "e", "path": "nothing"}],
        }
        self.result = census.census(self.rows)

    def test_the_four_outcomes_are_counted_separately(self):
        self.assertEqual(self.result["named_assignments"], 4)
        self.assertEqual(self.result["silent"], 3)
        self.assertEqual(self.result["by_outcome"],
                         {"gate-closed": 1, "read-elsewhere": 1, "open": 1})

    def test_per_assignee_splits_answered_from_silent(self):
        self.assertEqual(self.result["per_assignee"]["gemini"]["assigned"], 1)
        self.assertEqual(self.result["per_assignee"]["gemini"]["answered"], 1)
        self.assertEqual(self.result["per_assignee"]["desi"]["answered"], 0)

    def test_silent_items_carry_the_amigo_that_did_read_it(self):
        by_id = {i["id"]: i for i in self.result["items"]}
        self.assertEqual(by_id["c"]["read_by"], ["claude"])
        self.assertEqual(by_id["b"]["closed_by"], "auto:path")
        self.assertNotIn("a", by_id)


class TestCommandLine(unittest.TestCase):
    def run_script(self, *args):
        return subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "named_review_census.py"), *args],
            capture_output=True, text=True, check=False,
        )

    def test_json_output_matches_the_library(self):
        path = write_ledger([ASSIGN, {"id": "x", "reviewer": "auto:path",
                                      "state": "accomplished"}])
        try:
            run = self.run_script("--ledger", str(path), "--json")
            self.assertEqual(run.returncode, 0, run.stderr)
            payload = json.loads(run.stdout)
            self.assertEqual(payload["silent"], 1)
            self.assertEqual(payload["items"][0]["outcome"], "gate-closed")
        finally:
            path.unlink()

    def test_only_filters_to_one_outcome(self):
        path = write_ledger([
            {"id": "x", "assigned_to": "gemini"},
            {"id": "x", "reviewer": "auto:path", "state": "accomplished"},
        ])
        try:
            gate = self.run_script("--ledger", str(path), "--only", "gate-closed", "--json")
            elsewhere = self.run_script("--ledger", str(path), "--only", "read-elsewhere",
                                        "--json")
            self.assertEqual(json.loads(gate.stdout)["silent"], 1)
            self.assertEqual(json.loads(elsewhere.stdout)["silent"], 0)
        finally:
            path.unlink()

    def test_a_missing_ledger_is_an_error_and_not_a_clean_zero(self):
        missing = REPO_ROOT / "channels" / "this-ledger-does-not-exist.jsonl"
        self.assertFalse(missing.exists())
        run = self.run_script("--ledger", str(missing))
        self.assertNotEqual(run.returncode, 0)
        self.assertEqual(run.stdout.strip(), "")
        self.assertIn("no ledger", run.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
