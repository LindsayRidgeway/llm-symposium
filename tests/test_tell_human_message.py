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


def test_review_branch_without_pile_suffix_names_reviewer_state():
    msg = (
        "I woke up by myself just now and did some work. What it was: I am speeding up our email checks "
        "by only searching recent sent messages. It is not published yet — it is waiting for someone "
        "other than me to look at it. Nothing needed from you."
    )
    out = tell_human.sanitize_for_human(msg)
    assert "woke up by myself" not in out
    assert "Nothing needed from you" not in out
    assert "waiting for someone other than me" not in out
    assert "I am speeding up our email checks by only searching recent sent messages." in out
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
    total = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            total += 1
            try:
                fn()
                print(f"PASS {name}")
            except (Exception, SystemExit) as exc:  # noqa: BLE001 — SystemExit is BaseException
                failures += 1
                print(f"FAIL {name}: {exc}")
    print(f"\n{total - failures}/{total} tests passed")
    return 1 if failures else 0




# --- the REQUEST a-n channel (human's format, 2026-10-01) ------------------------------------------

def _expect_exit(fn, *args):
    """These three were written for pytest and had therefore NEVER RUN — pytest is not installed
    anywhere in this project, and `_run_all()` sat above them in the file so they were not even
    collected by the runner the other tests in this file use. A test that cannot run is not a test;
    repaired 2026-10-12 while adding the supersede tests beside them."""
    try:
        fn(*args)
    except SystemExit:
        return
    raise AssertionError(f"{getattr(fn, '__name__', fn)} did not refuse {args!r}")


def test_request_id_must_carry_the_amigos_own_initial():
    for bad in ("C-1", "G-7", "banana", "D-", "-1", "D1"):
        _expect_exit(tell_human._guard_request_id, "desi", bad)


def test_a_free_serial_is_accepted():
    assert tell_human._guard_request_id("desi", "D-997") == "D-997"


def test_register_rows_read_the_table_and_ignore_the_header():
    rows = tell_human._register_rows()
    assert all(r[0] not in ("id", "---") for r in rows)


# --------------------------------------------------------------------------- #
# A request that replaces an earlier one (added 2026-10-12)
# --------------------------------------------------------------------------- #

def test_a_superseding_request_says_so_on_its_first_line():
    """The register's rule: a later request that replaces an earlier one names it on the first line,
    and the earlier one is closed in the same breath. D-7 named a GitHub account
    `llm-symposium-commons`; the human pointed out that "commons" already means the symposium, so the
    name said the thing twice and the function never, and the fix had to be a request rather than a
    quiet edit of a message he had already been sent."""
    text = tell_human.request_text("desi", "D-8", "Use llm-symposium-machine instead.", supersedes="D-7")
    first = text.splitlines()[0]
    assert first == "REQUEST D-8 (supersedes D-7)", first
    assert text.rstrip().endswith("— Desi")


def test_a_request_that_replaces_nothing_is_just_its_id():
    assert tell_human.request_text("desi", "D-9", "do the thing").splitlines()[0] == "REQUEST D-9"


def test_the_register_has_the_request_that_will_be_superseded():
    assert tell_human._row_index("D-7") is not None
    assert tell_human._row_index("D-999") is None




def test_a_superseded_row_is_not_written_as_done():
    """The founder asked whether D-7 needed its own closing message. It does not — but the row said
    `done`, which is the wrong fact: he never did the thing, a later request replaced it."""
    import tempfile
    real = tell_human.REGISTER
    with tempfile.TemporaryDirectory() as td:
        reg = Path(td) / "register.md"
        reg.write_text("| id | date | from | state | gist | record |\n| D-7 | 2026-10-12 | desi | open | x | y |\n",
                       encoding="utf-8")
        tell_human.REGISTER = reg
        try:
            tell_human._close_register("D-7", state="superseded")
            assert "| superseded |" in reg.read_text(encoding="utf-8")
            refused = False
            try:
                tell_human._close_register("D-7", state="closed")
            except ValueError:
                refused = True
            assert refused, "a closure word the register does not define was accepted"
        finally:
            tell_human.REGISTER = real


def test_the_register_and_the_transcript_agree_that_d_7_was_superseded():
    row = tell_human._register_rows()[tell_human._row_index("D-7")]
    assert row[3] == "superseded", row
    assert tell_human._register_rows()[tell_human._row_index("D-8")][3] == "open"


if __name__ == "__main__":
    sys.exit(_run_all())
