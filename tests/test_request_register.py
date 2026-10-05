#!/usr/bin/env python3
"""Tests for the request register (`governance/request-register.md`).

Two defects these pin, both measured on the live file rather than imagined:

  * **The register could not be closed from a wake.** Its state changed only inside
    `tell_human.py --close`, and `--close` sends a Telegram message; a wake may not send. So a request
    whose closing fact had already gone out through the chat sat `open` in the file — which is
    exactly what happened to D-3 on 2026-10-05, hours after the human was told "zero pending
    requests", with the weekly nudge queued to email him about it three days later. `--close-recorded`
    is the no-send path; `_append_closure_note` is its audit line.

  * **The state field had no legal-value check.** The human settled the rule on 2026-10-05: a request
    is a thing only he can do, and it is **open or closed, binary** — no third state invented in prose
    ("closed, not done", "deferred", "parked"). `test_live_register_states_are_binary` fails the moment
    a row carries anything else.

`test_live_*` reads the shipped register; the rest use a throwaway one.
"""
from __future__ import annotations

import importlib.util
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("tell_human", ROOT / "scripts" / "tell_human.py")
tell_human = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(tell_human)

LEGAL_STATES = {"open", "done"}
ID_RE = re.compile(r"^[CDGT]-[0-9]+$")

TMP_TABLE = """# Request register

| id | date | from | state | gist | telegram record |
|---|---|---|---|---|---|
| D-1 | 2026-10-01 | desi | done | a newsletter with an API | channels/telegram/a.md |
| D-2 | 2026-10-01 | desi | open | one Hacker News account | channels/telegram/b.md |
"""


def _live_rows():
    return [r for r in tell_human._register_rows() if r and ID_RE.match(r[0])]


# --- the live register -----------------------------------------------------------------------------

def test_live_register_states_are_binary():
    for r in _live_rows():
        assert r[3].lower() in LEGAL_STATES, f"{r[0]} has illegal state {r[3]!r}; a request is open or done"
        assert len(r) == 6, f"{r[0]} row has {len(r)} cells; the table is six columns"


def test_live_register_ids_are_unique_and_well_shaped():
    ids = [r[0] for r in _live_rows()]
    assert len(ids) == len(set(ids)), "a serial was reused; rule 1 forbids it"
    for i in ids:
        assert ID_RE.match(i), f"bad id {i!r}"
        assert i[0] in "CDGT", f"{i!r} is not an amigo initial"


def test_live_register_records_exist():
    for r in _live_rows():
        assert (ROOT / r[5]).exists(), f"{r[0]} points at a telegram record that is not on disk: {r[5]}"


def test_live_register_d3_is_closed():
    """D-3 regression pin (2026-10-05). The human was told it was closed; the file must agree.

    Serial D-3 is never reused (rule 1), so it can only ever read 'done' from here on.
    """
    d3 = {r[0]: r for r in _live_rows()}.get("D-3")
    assert d3 is not None, "D-3 vanished from the register; rows are closed, never deleted"
    assert d3[3].lower() == "done", "D-3 reads open while the record says it is closed — the nudge would email him"


# --- _close_register / _append_closure_note --------------------------------------------------------

def test_close_recorded_flips_state_without_a_message():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        reg = tmp / "request-register.md"
        reg.write_text(TMP_TABLE, encoding="utf-8")
        saved, tell_human.REGISTER = tell_human.REGISTER, reg
        try:
            assert tell_human._row_index("D-2") is not None
            tell_human._close_register("D-2")
            tell_human._append_closure_note("D-2", "desi", "closed in the chat on 2026-10-05")
            out = reg.read_text(encoding="utf-8")
            assert "| D-2 | 2026-10-01 | desi | done |" in out
            assert tell_human.CLOSURE_HEADING in out
            assert "D-2 closed (recorded by desi): closed in the chat on 2026-10-05" in out
        finally:
            tell_human.REGISTER = saved


def test_closing_a_missing_id_refuses():
    with tempfile.TemporaryDirectory() as d:
        reg = Path(d) / "request-register.md"
        reg.write_text(TMP_TABLE, encoding="utf-8")
        saved, tell_human.REGISTER = tell_human.REGISTER, reg
        try:
            assert tell_human._row_index("D-99") is None, "a serial that is not in the register"
        finally:
            tell_human.REGISTER = saved


def _run_all() -> int:
    failures = total = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            total += 1
            try:
                fn()
                print(f"PASS {name}")
            except Exception as exc:  # noqa: BLE001
                failures += 1
                print(f"FAIL {name}: {exc}")
    print(f"\n{total - failures}/{total} tests passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(_run_all())
