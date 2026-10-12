#!/usr/bin/env python3
"""Tests for channels/queue_snapshot.py — the review-blockage experiment's read.

Every test uses a synthetic ledger: the real `channels/items.jsonl` is a moving target and a test that
reads it would pass or fail on the day's queue rather than on the code.
"""
from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("queue_snapshot", REPO / "channels" / "queue_snapshot.py")
qs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qs)


def rec(id_, to, state=None, reason=None):
    return {"id": id_, "amigo": "claude", "assigned_to": to, "state": state,
            "reason": reason, "filed_utc": "2026-10-01T00:00:00Z"}


def items(*recs):
    return {r["id"]: r for r in recs}


def test_queue_ids_only_waiting_and_named():
    ledger = items(
        rec("20260101T000000Z-aaaaaaaa", "desi"),                       # waiting, named -> counts
        rec("20260101T000000Z-bbbbbbbb", "gemini", "postponed", "why"),  # left W -> no
        rec("20260101T000000Z-cccccccc", "desi", "accomplished"),        # A -> no
        rec("20260101T000000Z-dddddddd", "dmitri"),                      # other name -> no
    )
    assert qs.queue_ids(ledger, "desi") == ["20260101T000000Z-aaaaaaaa"]
    assert qs.queue_ids(ledger, "dmitri") == ["20260101T000000Z-dddddddd"]
    assert qs.queue_ids(ledger, "gemini") == []


def test_postponed_without_reason_still_counts_as_waiting():
    """The ledger's own rule: an unwritten postponement is not a decision, so it stays in W."""
    ledger = items(rec("20260101T000000Z-aaaaaaaa", "desi", "postponed", None))
    assert qs.queue_ids(ledger, "desi") == ["20260101T000000Z-aaaaaaaa"]


def test_digest_is_order_independent_and_membership_sensitive():
    a, b = "20260101T000000Z-aaaaaaaa", "20260101T000000Z-bbbbbbbb"
    assert qs.digest([a, b]) == qs.digest([b, a])
    assert qs.digest([a, b]) != qs.digest([a])


def test_snapshot_shape():
    ledger = items(rec("20260101T000000Z-aaaaaaaa", "desi"))
    snap = qs.snapshot(ledger)
    assert set(snap) == {"taken_utc", "counts", "sha256_of_sorted_ids", "ids"}
    assert snap["counts"]["desi"] == 1
    assert snap["counts"]["gemini"] == 0
    assert snap["ids"]["desi"] == ["20260101T000000Z-aaaaaaaa"]


def test_diff_reports_a_removed_item_and_returns_0():
    before = items(rec("20260101T000000Z-aaaaaaaa", "gemini"))
    after = items(rec("20260101T000000Z-aaaaaaaa", "gemini", "postponed", "blocked on X"))
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "snap.json"
        p.write_text(json.dumps(qs.snapshot(before)), encoding="utf-8")
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = qs.diff(str(p), items=after)
    out = buf.getvalue()
    assert code == 0
    assert "left the queue: 20260101T000000Z-aaaaaaaa" in out
    assert "an item left a queue" in out


def test_diff_no_change_returns_1():
    ledger = items(rec("20260101T000000Z-aaaaaaaa", "desi"))
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "snap.json"
        p.write_text(json.dumps(qs.snapshot(ledger)), encoding="utf-8")
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = qs.diff(str(p), items=ledger)
    assert code == 1
    assert "no item has left any queue" in buf.getvalue()


def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"{len(fns)} passed")


if __name__ == "__main__":
    _run_all()
