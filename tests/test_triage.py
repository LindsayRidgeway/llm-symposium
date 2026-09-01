#!/usr/bin/env python3
"""Offline tests for channel triage (channels/triage.py)."""
import os
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import channels.triage as triage  # noqa: E402


def _with_temp_repo(fn):
    with tempfile.TemporaryDirectory() as td:
        old = (triage.REPO_ROOT, triage.CHANNELS_DIR, triage.ACTION_QUEUE, triage.DIGEST, triage.ACTUATOR_REQUESTS)
        root = Path(td)
        triage.REPO_ROOT = root
        triage.CHANNELS_DIR = root / "channels"
        triage.ACTION_QUEUE = root / "channels" / "action-queue.md"
        triage.DIGEST = root / "channels" / "channel-digest.md"
        triage.ACTUATOR_REQUESTS = root / "actuator" / "requests"
        try:
            fn(root)
        finally:
            triage.REPO_ROOT, triage.CHANNELS_DIR, triage.ACTION_QUEUE, triage.DIGEST, triage.ACTUATOR_REQUESTS = old


def test_non_actionable_gets_digest_not_queue():
    def run(root):
        triage.process_inbound("telegram", "tarik", "Lindsay", "channels/telegram/m.md", "hello there")
        assert triage.DIGEST.exists()
        assert "non-actionable" in triage.DIGEST.read_text(encoding="utf-8")
        assert not triage.ACTION_QUEUE.exists()
    _with_temp_repo(run)


def test_actionable_gets_queue_item():
    def run(root):
        triage.process_inbound("telegram", "tarik", "Lindsay", "channels/telegram/m.md", "Goal: repair the channel poll workflow")
        assert triage.ACTION_QUEUE.exists()
        q = triage.ACTION_QUEUE.read_text(encoding="utf-8")
        assert "Status: open" in q
        assert "repair the channel poll workflow" in q
    _with_temp_repo(run)


def test_queue_is_idempotent_for_same_message():
    def run(root):
        text = "Goal: fix the workflow"
        triage.process_inbound("telegram", "tarik", "Lindsay", "channels/telegram/m.md", text)
        triage.process_inbound("telegram", "tarik", "Lindsay", "channels/telegram/m.md", text)
        q = triage.ACTION_QUEUE.read_text(encoding="utf-8")
        assert q.count("queue-id:") == 1
    _with_temp_repo(run)


def test_actuator_request_requires_sentinel_and_model_proposer():
    def run(root):
        text = (
            "SYMPOSIUM_ACTUATOR_REQUEST\n"
            "Proposer: Tarik\n"
            "```diff\n"
            "diff --git a/docs/example.md b/docs/example.md\n"
            "--- a/docs/example.md\n"
            "+++ b/docs/example.md\n"
            "@@ -0,0 +1 @@\n"
            "+hello\n"
            "```\n"
        )
        routed = triage.route_actuator_requests("telegram", "tarik", text)
        assert len(routed) == 1
        assert routed[0].startswith("actuator/requests/")
        assert list((root / "actuator" / "requests").glob("*.patch"))
    _with_temp_repo(run)


def test_actuator_request_blocks_workflow_path():
    def run(root):
        text = (
            "SYMPOSIUM_ACTUATOR_REQUEST\n"
            "Proposer: Claude\n"
            "```diff\n"
            "diff --git a/.github/workflows/channel-poll.yml b/.github/workflows/channel-poll.yml\n"
            "--- a/.github/workflows/channel-poll.yml\n"
            "+++ b/.github/workflows/channel-poll.yml\n"
            "@@ -1 +1 @@\n"
            "-old\n"
            "+new\n"
            "```\n"
        )
        routed = triage.route_actuator_requests("telegram", "claude", text)
        assert routed == []
        assert triage.ACTION_QUEUE.exists()
        assert "blocked channel-originated patch path" in triage.ACTION_QUEUE.read_text(encoding="utf-8")
    _with_temp_repo(run)


def _run_all():
    import traceback
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
            passed += 1
        except Exception:
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
    print(f"\n{passed}/{len(tests)} tests passed")
    return 0 if passed == len(tests) else 1


if __name__ == "__main__":
    sys.exit(_run_all())
