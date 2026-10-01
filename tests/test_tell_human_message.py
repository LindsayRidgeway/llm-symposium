#!/usr/bin/env python3
"""Regression tests for the Telegram sender's human-facing wake summaries.

The defect pinned here came from the live Telegram wake messages: every run wrapped its one useful
sentence in fixed self-narration ("I woke up by myself...") and a trailing "Nothing needed from you."
The human asked for the opposite: substance first, with only a compact action/status signal kept.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("tell_human", ROOT / "scripts" / "tell_human.py")
tell_human = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(tell_human)


LANDED = (
    "I woke up by myself just now and did some work, and it is in the repository now — "
    "not waiting on anyone. What it was: I rebuilt the site map so the newest page can be found. "
    "Nothing needed from you."
)

REVIEW = (
    "I woke up by myself just now and did some work. What it was: I added a dead-link check and "
    "fixed the page it found. It is not published yet: it goes onto my review pile, which is now "
    "2 pieces deep, and only something other than me can merge that pile. Nothing needed from you."
)

CUT_OFF = (
    "I woke up by myself just now and got nothing finished — I ran out of time or lost the thread "
    "partway through. Nothing came of it. Nothing needed from you."
)


def test_landed_wake_summary_loses_boilerplate_but_keeps_signal():
    out = tell_human.sanitize_for_human(LANDED)
    assert "woke up by myself" not in out
    assert "Nothing needed from you" not in out
    assert "not waiting on anyone" not in out
    assert "I rebuilt the site map so the newest page can be found." in out
    assert "Status: in the repository; action: none." in out


def test_review_branch_wake_summary_names_reviewer_state():
    out = tell_human.sanitize_for_human(REVIEW)
    assert "woke up by myself" not in out
    assert "review pile" not in out
    assert "only something other than me" not in out
    assert "I added a dead-link check and fixed the page it found." in out
    assert "Status: awaiting reviewer; action: none." in out


def test_cutoff_summary_is_short_and_honest():
    out = tell_human.sanitize_for_human(CUT_OFF)
    assert out == (
        "I got nothing finished — I ran out of time or lost the thread partway through. "
        "Nothing came of it.\n\nStatus: no artifact; action: none."
    )


def test_regular_message_is_not_rewritten():
    msg = "The reply arrived: they asked for the source table before Friday."
    assert tell_human.sanitize_for_human(msg) == msg


def _run_all() -> int:
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except Exception as exc:  # noqa: BLE001
                failures += 1
                print(f"FAIL {name}: {exc}")
    print(f"\n{4 - failures}/4 tests passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(_run_all())


# --- the REQUEST a-n channel (human's format, 2026-10-01) ------------------------------------------

def test_request_id_must_carry_the_amigos_own_initial():
    import pytest  # noqa: PLC0415
    for bad in ("C-1", "G-7", "banana", "D-", "-1", "D1"):
        with pytest.raises(SystemExit):
            tell_human._guard_request_id("desi", bad)


def test_a_free_serial_is_accepted():
    assert tell_human._guard_request_id("desi", "D-997") == "D-997"


def test_register_rows_read_the_table_and_ignore_the_header():
    rows = tell_human._register_rows()
    assert all(r[0] not in ("id", "---") for r in rows)
