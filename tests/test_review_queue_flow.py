#!/usr/bin/env python3
# Owner: Dmitri
"""Tests for `scripts/review_queue_flow.py` — the census that asks whether the backlog is draining.

The defect this guards against is a census that reads the ledger the way it *looks* rather than the
way it is stored. `channels/items.jsonl` is append-only: one item appears as several rows, the first
filing it and later ones updating its state. A reader that counts rows reports 1,965 items where the
repository has 608, and — worse — counts an item that was filed *and* decided as still waiting,
because the filing row carries `state: null`. The first test below is that exact case.

The second thing guarded is the definition of the delivery defect: a postponement is classed as the
defect only when its reason names an artefact that never reached `main`, so a postponement for a
different reason ("cut off at its cap", "a judgement call") must not be swept in with them — that
number is the whole argument, and inflating it would make it worthless.

No network, no real ledger: every case is a temporary file.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import review_queue_flow as flow  # noqa: E402


def _row(item_id, **kw):
    base = {
        "id": item_id,
        "amigo": "desi",
        "assigned_to": "dmitri",
        "filed_utc": "2026-10-01T00:00:00Z",
        "state": None,
        "state_utc": None,
        "reviewer": None,
        "reason": None,
    }
    base.update(kw)
    return base


class LoadRowsTest(unittest.TestCase):
    def test_last_row_per_item_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "items.jsonl"
            path.write_text(
                "\n".join(
                    json.dumps(r)
                    for r in [
                        _row("a-1"),
                        _row("a-1", state="accomplished", reviewer="dmitri",
                             state_utc="2026-10-02T00:00:00Z"),
                        _row("b-2"),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            rows = flow.load_rows(path)
        self.assertEqual([r["id"] for r in rows], ["a-1", "b-2"], "order follows first appearance")
        self.assertEqual(rows[0]["state"], "accomplished", "the update row is the item's state")

    def test_half_written_trailing_line_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "items.jsonl"
            path.write_text(json.dumps(_row("a-1")) + "\n{\"id\": \"b-2\", ", encoding="utf-8")
            rows = flow.load_rows(path)
        self.assertEqual(len(rows), 1)

    def test_a_decided_item_is_not_waiting(self):
        rows = [_row("a-1", state="postponed", reviewer="desi", reason="not on main")]
        out = flow.census(rows)
        self.assertEqual(out["waiting"], 0)
        self.assertEqual(out["decided"], 1)


class CensusTest(unittest.TestCase):
    def test_stock_names_the_amigo_who_owes_the_decision(self):
        rows = [
            _row("a-1", assigned_to="dmitri"),
            _row("a-2", assigned_to="dmitri"),
            _row("a-3", assigned_to="desi"),
        ]
        out = flow.census(rows)
        self.assertEqual(out["stock"]["dmitri"]["waiting"], 2)
        self.assertEqual(out["stock"]["desi"]["waiting"], 1)

    def test_delivery_defect_share_excludes_other_postponements(self):
        rows = [
            _row("a-1", state="postponed", reviewer="dmitri",
                 reason="its report is named but not on main", state_utc="2026-10-02T00:00:00Z"),
            _row("a-2", state="postponed", reviewer="dmitri",
                 reason="cut off at its action cap; nothing was written",
                 state_utc="2026-10-02T00:00:00Z"),
        ]
        out = flow.census(rows)
        self.assertEqual(out["postponed"]["total"], 2)
        self.assertEqual(out["postponed"]["delivery_defect"], 1)
        self.assertEqual(out["postponed"]["share"], "50%")

    def test_latency_separates_machine_closers_from_named_reviewers(self):
        rows = [
            _row("a-1", state="accomplished", reviewer="auto:land",
                 state_utc="2026-10-01T00:00:00Z"),
            _row("a-2", state="accomplished", reviewer="dmitri",
                 state_utc="2026-10-05T00:00:00Z"),
        ]
        out = flow.census(rows)
        self.assertEqual(out["latency"]["machine"]["median_days"], 0.0)
        self.assertAlmostEqual(out["latency"]["amigo"]["median_days"], 4.0)

    def test_flow_net_is_filed_minus_decided(self):
        rows = [
            _row("a-1"),
            _row("a-2"),
            _row("a-3", state="accomplished", reviewer="desi",
                 state_utc="2026-10-02T00:00:00Z"),
        ]
        out = flow.census(rows, days=400)
        self.assertEqual(out["flow"]["filed"], 3)
        self.assertEqual(out["flow"]["decided"], 1)
        self.assertEqual(out["flow"]["net"], 2)


if __name__ == "__main__":
    unittest.main()
