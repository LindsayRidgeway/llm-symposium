#!/usr/bin/env python3
# Owner: Desi
"""Tests for `scripts/wake_spend_record.py` — the measured answer to "what does a day cost?".

The defect this guards against is the one that let the commons quote spend figures it could not
support: reading a *token* count and printing a *dollar* figure derived from a rate nobody
recorded. The script must therefore keep the two apart — tokens summed from `result.json`, dollars
summed only from `cost_usd` records that actually exist — and it must say out loud how many runs
carried no dollar figure at all, rather than silently reporting the sum of the few that did.

Also guarded: a run directory that is half-written (no `result.json`, or an unparseable one) is
counted as a missing record rather than dropped from the population, because a denominator that
quietly shrinks makes the survivors look complete.

No network, no keys: every case is a temporary directory shaped like `~/LLM/<amigo>-bot/...`.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import wake_spend_record as spend  # noqa: E402


def make_run(root: Path, amigo: str, run_id: str, tokens=None, cost=None, write_result=True):
    run_dir = root / f"{amigo}-bot" / "tick-state" / "runs" / run_id
    run_dir.mkdir(parents=True)
    if write_result:
        payload = {"run_id": run_id}
        if tokens is not None:
            payload["total_tokens"] = tokens
        (run_dir / "result.json").write_text(json.dumps(payload))
    if cost is not None:
        (run_dir / "worker.jsonl").write_text(
            json.dumps({"type": "turn"}) + "\n" + json.dumps({"cost_usd": cost}) + "\n"
        )
    return run_dir


class TestRunDay(unittest.TestCase):
    def test_reads_the_timestamp_prefix(self):
        self.assertEqual(spend.run_day("20261026T072831Z-133e4d51"), "2026-10-26")

    def test_rejects_a_name_that_is_not_a_run_id(self):
        self.assertIsNone(spend.run_day("not-a-run"))
        self.assertIsNone(spend.run_day("20261332T072831Z-133e4d51"))


class TestWorkerCost(unittest.TestCase):
    def test_takes_the_last_dollar_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "worker.jsonl"
            path.write_text(
                json.dumps({"cost_usd": 0.10}) + "\n"
                + json.dumps({"type": "message"}) + "\n"
                + json.dumps({"cost_usd": 0.20}) + "\n"
            )
            self.assertAlmostEqual(spend.worker_cost(str(path)), 0.20)

    def test_missing_file_is_not_a_zero(self):
        self.assertIsNone(spend.worker_cost("/nonexistent/worker.jsonl"))

    def test_garbage_lines_do_not_raise(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "worker.jsonl"
            path.write_text('{"cost_usd": oops\n' + json.dumps({"cost_usd": 0.05}) + "\n")
            self.assertAlmostEqual(spend.worker_cost(str(path)), 0.05)


class TestCollect(unittest.TestCase):
    def test_tokens_are_summed_per_amigo_and_day(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_run(root, "desi", "20261026T010000Z-aaaaaaa1", tokens=1000)
            make_run(root, "desi", "20261026T020000Z-aaaaaaa2", tokens=500)
            make_run(root, "gemini", "20261026T030000Z-bbbbbbb1", tokens=250)
            data = spend.collect(str(root))
            self.assertEqual(data["days"]["2026-10-26|desi"]["runs"], 2)
            self.assertEqual(data["days"]["2026-10-26|desi"]["tokens"], 1500)
            self.assertEqual(data["days"]["2026-10-26|gemini"]["tokens"], 250)
            self.assertEqual(data["totals"]["tokens"], 1750)

    def test_dollars_come_only_from_cost_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_run(root, "desi", "20261026T010000Z-aaaaaaa1", tokens=1000, cost=0.40)
            make_run(root, "desi", "20261026T020000Z-aaaaaaa2", tokens=1000)
            data = spend.collect(str(root))
            self.assertEqual(data["totals"]["runs"], 2)
            self.assertEqual(data["totals"]["runs_with_cost"], 1)
            self.assertAlmostEqual(data["totals"]["cost_usd"], 0.40)
            # The gap is the point: one of two runs has no dollar figure, and it is named.
            self.assertEqual(data["totals"]["missing_worker_jsonl"], 1)

    def test_half_written_run_counts_as_missing_not_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_run(root, "desi", "20261026T010000Z-aaaaaaa1", tokens=1000)
            make_run(root, "desi", "20261026T020000Z-aaaaaaa2", write_result=False)
            bad = make_run(root, "desi", "20261026T030000Z-aaaaaaa3", tokens=10)
            (bad / "result.json").write_text("{not json")
            data = spend.collect(str(root))
            self.assertEqual(data["totals"]["runs"], 1)
            self.assertEqual(data["totals"]["missing_result_json"], 2)

    def test_zero_token_run_is_counted_but_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_run(root, "tarik", "20261026T010000Z-ccccccc1", tokens=None)
            data = spend.collect(str(root))
            self.assertEqual(data["totals"]["runs"], 1)
            self.assertEqual(data["totals"]["no_token_record"], 1)


class TestReport(unittest.TestCase):
    def test_states_the_measured_total_and_the_missing_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_run(root, "desi", "20261026T010000Z-aaaaaaa1", tokens=2_000_000, cost=0.5)
            make_run(root, "dmitri", "20261026T010000Z-ddddddd1", tokens=1_000_000)
            text = spend.report(spend.collect(str(root)), 7)
            self.assertIn("2 runs", text)
            self.assertIn("3,000,000", text)
            self.assertIn("1 of 2 runs carry a `cost_usd` field", text)
            self.assertIn("1 runs have no dollar figure", text)

    def test_never_prints_an_estimated_price(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_run(root, "desi", "20261026T010000Z-aaaaaaa1", tokens=5_000_000)
            text = spend.report(spend.collect(str(root)), 7)
            self.assertIn("No price is estimated here", text)
            self.assertNotIn("estimated cost", text.lower())

    def test_empty_root_reports_zero_without_crashing(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = spend.collect(tmp)
            self.assertEqual(data["totals"]["runs"], 0)
            self.assertIn("0 runs", spend.report(data, 7))

    def test_days_limit_shows_the_newest_days(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_run(root, "desi", "20261020T010000Z-aaaaaaa1", tokens=1)
            make_run(root, "desi", "20261026T010000Z-aaaaaaa2", tokens=1)
            text = spend.report(spend.collect(str(root)), 1)
            self.assertIn("2026-10-26", text)
            self.assertNotIn("2026-10-20", text)


class TestMain(unittest.TestCase):
    def test_missing_root_is_an_error_not_an_empty_success(self):
        self.assertEqual(spend.main(["--root", "/nonexistent/nowhere"]), 2)

    def test_json_output_is_parseable(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_run(Path(tmp), "desi", "20261026T010000Z-aaaaaaa1", tokens=42)
            self.assertEqual(spend.main(["--root", tmp, "--json"]), 0)


if __name__ == "__main__":
    unittest.main()
