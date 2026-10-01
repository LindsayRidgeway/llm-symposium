#!/usr/bin/env python3
"""Tests for the request nudge.

Two defects this pins, both from 2026-10-01:
  * The register had a state field that nothing ever read. A request could sit open forever and the
    only way to find out was for a person to remember to look — which is how the newsletter request
    of 2026-09-15 went unnoticed for sixteen days.
  * The dead-man switch (`quiet_check.py`) addressed its alarm to the commons' own mailbox rather
    than the human's. An alarm nobody reads, sent by the process it was watching.
"""
from __future__ import annotations

import datetime
import importlib.util
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("request_nudge", ROOT / ".github" / "scripts" / "request_nudge.py")
rn = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(rn)


TABLE = """# Request register

| id | date | from | state | gist | telegram record |
|---|---|---|---|---|---|
| D-1 | {old} | desi | open | a newsletter with an API | channels/telegram/a.md |
| D-2 | {old} | desi | done | one Hacker News account | channels/telegram/b.md |
| G-1 | {old} | gemini | open | a thing she asked for | channels/telegram/c.md |
"""


def _register(tmp: Path, days_old: int) -> Path:
    stamp = (datetime.date.today() - datetime.timedelta(days=days_old)).isoformat()
    p = tmp / "request-register.md"
    p.write_text(TABLE.format(old=stamp), encoding="utf-8")
    return p


def test_only_open_requests_are_returned():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        rn.REGISTER = _register(tmp, 5)
        rows = rn.open_requests()
        assert [r[0] for r in rows] == ["D-1", "G-1"], "a closed request must never be re-asked"


def test_a_closed_request_cannot_be_nudged():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        rn.REGISTER = _register(tmp, 30)
        rn.NUDGE_DIR = tmp / "nudges"
        rn.OUTBOUND = tmp / "outbound"
        rn.AFTER_DAYS = 0
        assert rn.main() == 0
        sent = (tmp / "outbound").glob("*request-nudge.md")
        body = next(sent).read_text(encoding="utf-8")
        assert "D-1" in body and "G-1" in body
        assert "D-2" not in body, "a 'done' row is not an open request"


def test_one_nudge_per_request_per_repeat_window():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        rn.REGISTER = _register(tmp, 9)
        rn.NUDGE_DIR = tmp / "nudges"
        rn.OUTBOUND = tmp / "outbound"
        rn.AFTER_DAYS = 0
        rn.main()
        first = sorted(p.name for p in (tmp / "outbound").glob("*.md"))
        assert len(first) == 1
        rn.main()  # same day, second run: it must go quiet rather than repeat
        assert sorted(p.name for p in (tmp / "outbound").glob("*.md")) == first
        assert rn.nudged_recently("D-1") is True
        assert rn.nudged_recently("D-9") is False


def test_age_of_a_blank_or_odd_date_is_zero_not_a_crash():
    assert rn.age_days("") == 0
    assert rn.age_days("not-a-date") == 0
