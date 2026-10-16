#!/usr/bin/env python3
"""Dedicated offline unit tests for Telegram batch update draining and pagination.

Covers channels/telegram.py:drain_all_updates() edge cases:
- Empty queues and sub-100 message batches
- Pagination across backlogs > 100 updates
- Batch persistence via on_batch callback before advancing offset
- Handling of sparse / non-sequential update_id values
- Telegram API failure handling (ok=False)
- Exception propagation during on_batch ensuring offset is not acknowledged
"""
import json
import sys
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import channels.telegram as tg  # noqa: E402


class _MockResponse:
    def __init__(self, data: dict):
        self._body = json.dumps(data).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self._body


def test_drain_empty_updates():
    """Verify empty response terminates pagination and yields no updates."""
    with mock.patch.object(tg.urllib.request, "urlopen", return_value=_MockResponse({"ok": True, "result": []})):
        batches = []
        updates = tg.drain_all_updates("fake_token", on_batch=batches.append)
        assert updates == []
        assert batches == []


def test_drain_single_batch_under_100():
    """Verify a batch < 100 does not issue a subsequent offset query."""
    batch_data = [{"update_id": i, "message": {"text": f"msg {i}"}} for i in range(42)]
    calls = []

    def fake_urlopen(req, timeout=60):
        calls.append(req)
        return _MockResponse({"ok": True, "result": batch_data})

    with mock.patch.object(tg.urllib.request, "urlopen", side_effect=fake_urlopen):
        batches = []
        updates = tg.drain_all_updates("fake_token", on_batch=batches.append)
        assert len(updates) == 42
        assert len(batches) == 1
        assert len(calls) == 1
        assert b"offset" not in calls[0].data


def test_drain_multipage_backlog_exceeding_100():
    """Verify pagination across 250 updates in 3 pages (100, 100, 50)."""
    p1 = [{"update_id": i, "message": {"text": f"m{i}"}} for i in range(100)]
    p2 = [{"update_id": 100 + i, "message": {"text": f"m{100 + i}"}} for i in range(100)]
    p3 = [{"update_id": 200 + i, "message": {"text": f"m{200 + i}"}} for i in range(50)]

    pages = [p1, p2, p3]
    calls = []
    batches_seen = []

    def fake_urlopen(req, timeout=60):
        calls.append(req)
        page_idx = len(calls) - 1
        return _MockResponse({"ok": True, "result": pages[page_idx]})

    def on_batch(b):
        # Durability check: on_batch must run BEFORE next HTTP request is issued
        assert len(calls) == len(batches_seen) + 1
        batches_seen.append(b)

    with mock.patch.object(tg.urllib.request, "urlopen", side_effect=fake_urlopen):
        updates = tg.drain_all_updates("fake_token", on_batch=on_batch)

    assert len(updates) == 250
    assert len(calls) == 3
    assert len(batches_seen) == 3
    assert b"offset" not in calls[0].data
    assert b"offset=100" in calls[1].data
    assert b"offset=200" in calls[2].data


def test_drain_handles_sparse_and_unordered_update_ids():
    """Verify max(update_id) + 1 tracks properly even if update_ids are unordered."""
    p1 = [
        {"update_id": 500, "message": {"text": "msg"}},
        {"update_id": 999, "message": {"text": "msg"}},
        {"update_id": 12, "message": {"text": "msg"}},
    ] + [{"update_id": 100 + i, "message": {"text": "pad"}} for i in range(97)]
    assert len(p1) == 100

    p2 = [{"update_id": 1005, "message": {"text": "final"}}]
    calls = []

    def fake_urlopen(req, timeout=60):
        calls.append(req)
        return _MockResponse({"ok": True, "result": p1 if len(calls) == 1 else p2})

    with mock.patch.object(tg.urllib.request, "urlopen", side_effect=fake_urlopen):
        updates = tg.drain_all_updates("fake_token")

    assert len(updates) == 101
    assert len(calls) == 2
    assert b"offset=1000" in calls[1].data


def test_drain_api_error_raises_runtime_error():
    """Verify RuntimeError is raised on ok: False and stops iteration."""
    with mock.patch.object(
        tg.urllib.request,
        "urlopen",
        return_value=_MockResponse({"ok": False, "description": "Unauthorized"}),
    ):
        try:
            tg.drain_all_updates("bad_token")
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "Telegram getUpdates error" in str(e)


def test_drain_callback_exception_halts_before_next_offset():
    """Verify that an exception in on_batch halts before requesting the next offset."""
    p1 = [{"update_id": i, "message": {"text": f"m{i}"}} for i in range(100)]
    calls = []

    def fake_urlopen(req, timeout=60):
        calls.append(req)
        return _MockResponse({"ok": True, "result": p1})

    def failing_batch(batch):
        raise IOError("Disk full while logging batch")

    with mock.patch.object(tg.urllib.request, "urlopen", side_effect=fake_urlopen):
        try:
            tg.drain_all_updates("fake_token", on_batch=failing_batch)
            assert False, "Should have raised IOError"
        except IOError:
            pass

    # Crucial safety invariant: because on_batch failed on page 1,
    # no second request with offset=100 was ever made to Telegram.
    assert len(calls) == 1


if __name__ == "__main__":
    test_drain_empty_updates()
    test_drain_single_batch_under_100()
    test_drain_multipage_backlog_exceeding_100()
    test_drain_handles_sparse_and_unordered_update_ids()
    test_drain_api_error_raises_runtime_error()
    test_drain_callback_exception_halts_before_next_offset()
    print("All Telegram drain tests passed.")
