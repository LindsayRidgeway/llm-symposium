#!/usr/bin/env python3
# Owner: Desi
"""Tests for `scripts/burn_ledger.py`. Offline — a tiny temp runs tree, no network.

Why these exist. The document `research/2026-10-16-the-burn-so-far.md` tells the founder a
monthly figure for the only half of the bill nobody could see, and it will be used to size an
endowment. Two failures would corrupt that number silently:

  1. attributing a run to the wrong amigo (the cost per architecture is what the whole
     asymmetry rests on), and
  2. pricing an amigo at zero because its rate is missing, which would make "cheap" a fact of a
     missing row rather than a fact of a price.

Both are pinned here. A missing price must show up as *unpriced tokens*, never as $0.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import burn_ledger as bl  # noqa: E402

RATES = {
    "desi": {"blended": 0.01},
    "gemini": {"blended": 0.59},
    "tarik": {"blended": 1.86},
}


class PathTest(unittest.TestCase):
    def test_amigo_read_from_the_bot_component(self):
        p = "/home/x/LLM/gemini-bot/tick-state/runs/20261016T045852Z-9f457553/repo/result.json"
        self.assertEqual(bl.amigo_of(p), "gemini")

    def test_a_path_with_no_bot_component_is_not_guessed(self):
        self.assertIsNone(bl.amigo_of("/tmp/runs/1/result.json"))

    def test_run_date_reads_leading_date_or_none(self):
        self.assertEqual(bl.run_date("20261016T045852Z-9f457553"), "20261016")
        self.assertIsNone(bl.run_date("nonsense"))
        self.assertIsNone(bl.run_date("2026101"))  # too short


class SummarizeTest(unittest.TestCase):
    RECORDS = [
        {"amigo": "desi", "run_id": "20261014T000000Z-a", "date": "20261014",
         "model": "m", "tokens": 100_000_000},
        {"amigo": "gemini", "run_id": "20261015T000000Z-b", "date": "20261015",
         "model": "m", "tokens": 10_000_000},
        {"amigo": "tarik", "run_id": "20261016T000000Z-c", "date": "20261016",
         "model": "m", "tokens": 10_000_000},
    ]

    def test_totals_and_pricing(self):
        s = bl.summarize(self.RECORDS, RATES)
        self.assertEqual(s["total_runs"], 3)
        self.assertEqual(s["total_tokens"], 120_000_000)
        # desi 100M * 0.01 = $1.00 ; gemini 10M * 0.59 = $5.90 ; tarik 10M * 1.86 = $18.60
        self.assertEqual(s["per_amigo"]["desi"]["cost_usd"], 1.0)
        self.assertEqual(s["total_cost_usd"], 25.5)

    def test_missing_rate_is_unpriced_not_zero(self):
        s = bl.summarize(self.RECORDS, {"desi": {"blended": 0.01}})
        self.assertIsNone(s["per_amigo"]["tarik"]["cost_usd"])
        self.assertEqual(s["tokens_without_a_price"], 20_000_000)
        self.assertEqual(s["total_cost_usd"], 1.0)

    def test_days_window_keeps_only_recent_run_dates(self):
        # newest run date is 20261016, so a 2-day window is 15-16.
        s = bl.summarize(self.RECORDS, RATES, days=2)
        self.assertEqual(s["total_runs"], 2)
        self.assertNotIn("desi", s["per_amigo"])

    def test_empty_is_not_a_crash(self):
        s = bl.summarize([], RATES)
        self.assertEqual(s["total_runs"], 0)
        self.assertEqual(s["total_cost_usd"], 0.0)


class CollectTest(unittest.TestCase):
    def test_collect_reads_a_temp_tree_and_is_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for amigo, tokens, rid in (("desi", 5, "20261016T000000Z-1"),
                                       ("tarik", 7, "20261015T000000Z-2")):
                d = root / f"{amigo}-bot" / "tick-state" / "runs" / rid
                d.mkdir(parents=True)
                (d / "result.json").write_text(json.dumps(
                    {"run_id": rid, "model": "m", "total_tokens": tokens}))
            records = bl.collect(root)
            self.assertEqual(len(records), 2)
            self.assertEqual({r["amigo"] for r in records}, {"desi", "tarik"})
            self.assertFalse(list(root.rglob("*.tmp")), "collect must not write into the tree")


class MeasuredRateTest(unittest.TestCase):
    """The measured column: dollars the provider reported, not dollars we priced.

    The failure this class exists to stop is the same one at one remove. A transcript that was
    killed before goose wrote its `complete` event spent real money and reported none; if that
    reads as a run with zero cost, the measured rate comes out low and the figure the founder is
    shown is *cheaper* than the truth, in the direction that would make him fund too little.
    """

    def _tree(self, root: Path) -> Path:
        priced = root / "gemini-bot" / "tick-state" / "runs" / "20261016T000000Z-1"
        priced.mkdir(parents=True)
        (priced / "worker.jsonl").write_text(
            '{"type":"start"}\n'
            '{"type":"complete","total_tokens":2000000,"cost_usd":1.0}\n')
        cut = root / "desi-bot" / "tick-state" / "runs" / "20261016T030000Z-2"
        cut.mkdir(parents=True)
        (cut / "worker.jsonl").write_text('{"type":"tool"}\n{"type":"error"}\n')
        return root

    def test_provider_reported_cost_becomes_the_rate(self):
        with tempfile.TemporaryDirectory() as tmp:
            per, scanned, unpriced = bl.collect_measured_costs(self._tree(Path(tmp)))
            self.assertEqual((scanned, unpriced), (2, 1))
            self.assertEqual(per["gemini"]["cost_usd"], 1.0)
            self.assertNotIn("desi", per)
            self.assertEqual(bl.measured_rates(per),
                             {"gemini": {"blended": 0.5, "basis": "measured"}})

    def test_an_amigo_with_no_measured_tokens_gets_no_measured_rate(self):
        per = {"tarik": {"tokens": 0, "cost_usd": 0.0, "runs": 1}}
        self.assertEqual(bl.measured_rates(per), {},
                         "a run with no token count must not become a $0/M rate")

    def test_main_measured_swaps_the_measured_rate_and_keeps_the_others(self):
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as tmp:
            root = self._tree(Path(tmp))
            run = root / "gemini-bot" / "tick-state" / "runs" / "20261016T000000Z-1"
            (run / "result.json").write_text(json.dumps(
                {"run_id": "20261016T000000Z-1", "model": "m", "total_tokens": 2_000_000}))
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                bl.main(["--root", str(root), "--measured", "--json"])
            summary = json.loads(buf.getvalue())
            # the chat ledger prices gemini at 0.59/M; the runner's own runs said 0.50
            self.assertEqual(summary["per_amigo"]["gemini"]["rate_usd_per_million"], 0.5)
            self.assertEqual(summary["per_amigo"]["gemini"]["cost_usd"], 1.0)
            self.assertIn("1 carry no complete event", summary["measured_note"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
