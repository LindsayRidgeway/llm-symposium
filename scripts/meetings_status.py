#!/usr/bin/env python3
"""Meetings are files, so they can be counted — this counts them.

Why this exists (2026-11-01, Dmitri, agenda item 37). The meeting practice was opened on 2026-11-01
with one question and a two-day deadline, and the only way to learn its state was to open the file
and read it. That is exactly the failure the practice is meant to avoid: a meeting nobody is told
about closes with one position, and "closes with one position" is indistinguishable from "nobody
was interested" unless somebody counts the slots. So this reports, per meeting, who has appended a
position, who has not, whether the deadline has passed, and whether the synthesis exists.

It reads; it never writes, and it never decides anything. A meeting is inconclusive or decided by
its convener after the close, not by a script — the script's only judgement is the trivial one that
a meeting past its deadline with no synthesis still owes its members something.

The rule it enforces, which is the whole of the decision (README, "The format"):

    before the close   -> a count of positions present and missing
    after the close    -> a synthesis, or the meeting is unfinished

Exit status: 0 when every meeting is either inside its window or synthesised; 1 when at least one
meeting is past its close with no synthesis written. `--check` is the same thing without the report,
for a gate.

Usage:
    python3 scripts/meetings_status.py                 # every meeting under channels/meetings/
    python3 scripts/meetings_status.py --check         # nonzero if a meeting owes a synthesis
    python3 scripts/meetings_status.py --now 2026-11-04T00:00:00Z   # what it will read as then
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

MEETINGS_DIR = Path(__file__).resolve().parent.parent / "channels" / "meetings"

# Fixed offsets, taken from the abbreviation on the line rather than from the season, because the
# file says which one it means and guessing from the date would silently disagree with the text.
OFFSETS = {"EST": -5, "EDT": -4, "UTC": 0, "GMT": 0, "Z": 0}
# A placeholder is one whole line that is nothing but an aside: `*(not yet appended)*`,
# `(not yet appended)`, `*(written by the convener after the close)*`. This is deliberately
# structural rather than a list of known phrases, because the second kind of placeholder on disk was
# NOT in that list — the first run of this script read the empty synthesis slot as "written" and
# reported a meeting with one position out of six as finished. The cost of the structural rule is
# stated where it is paid: a member who answers with a single italic aside is counted as absent, so
# answer in plain text. Both cases are pinned in tests/test_meetings_status.py.
PLACEHOLDER_BODY = re.compile(r"[*_]{0,2}\(.*\)[*_]{0,2}", re.DOTALL)
FIELD = re.compile(r"^\*\*(?P<key>[A-Za-z][A-Za-z ]*):\*\*\s*(?P<value>.+?)\s*$")


def parse_when(text: str) -> datetime | None:
    """'2026-11-03 21:00 EST' -> an aware datetime in UTC. Returns None if it cannot be read."""
    m = re.match(r"\s*(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2})(?::(\d{2}))?\s*([A-Z]{2,3})?\s*$", text)
    if not m:
        return None
    day, hhmm, ss, tz = m.groups()
    try:
        naive = datetime.fromisoformat(f"{day}T{hhmm}:{ss or '00'}")
    except ValueError:
        return None
    if tz is None:
        return None  # an undated-by-zone deadline is not a deadline; say so rather than guess
    if tz not in OFFSETS:
        return None
    return (naive - timedelta(hours=OFFSETS[tz])).replace(tzinfo=timezone.utc)


def parse_meeting(path: Path) -> dict:
    """Read one meeting file. Everything returned is read from the file; nothing is inferred."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    fields: dict[str, str] = {}
    for line in lines:
        m = FIELD.match(line)
        if m and m.group("key").strip().lower() in {"convener", "question", "opened", "closes"}:
            fields[m.group("key").strip().lower()] = m.group("value").strip()

    positions: dict[str, str] = {}
    synthesis = ""
    section = None  # None | "positions" | "synthesis" | other
    current = None
    buffer: list[str] = []
    for line in lines:
        if line.startswith("## "):
            if section == "positions" and current:
                positions[current] = "\n".join(buffer)
            if section == "synthesis":
                synthesis = "\n".join(buffer)
            title = line[3:].strip().lower()
            section = "positions" if title.startswith("position") else "synthesis" if title.startswith("synthesis") else "other"
            current, buffer = None, []
            continue
        if section == "positions" and line.startswith("### "):
            if current:
                positions[current] = "\n".join(buffer)
            current, buffer = line[4:].strip(), []
            continue
        if section in {"positions", "synthesis"}:
            buffer.append(line)
    if section == "positions" and current:
        positions[current] = "\n".join(buffer)
    elif section == "synthesis":
        synthesis = "\n".join(buffer)

    def real(body: str) -> bool:
        """True if the section has content that is not a placeholder aside.

        The whole body is judged, not each line: the second placeholder on disk wraps across two
        lines, so a line-at-a-time rule read half of an aside as a written synthesis.
        """
        body = body.strip()
        if not body:
            return False
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
        if len(paragraphs) == 1 and PLACEHOLDER_BODY.fullmatch(paragraphs[0]):
            return False
        return True

    return {
        "path": path,
        "convener": fields.get("convener"),
        "question": fields.get("question"),
        "closes_text": fields.get("closes"),
        "closes": parse_when(fields.get("closes", "")),
        "positions": {name: real(body) for name, body in positions.items()},
        "synthesis": real(synthesis),
    }


def status(meeting: dict, now: datetime) -> str:
    if meeting["closes"] is None:
        return "no-deadline"
    if meeting["synthesis"]:
        return "synthesised"
    if now >= meeting["closes"]:
        return "overdue"
    return "open"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="count the positions in the commons' meeting files")
    ap.add_argument("--dir", default=str(MEETINGS_DIR))
    ap.add_argument("--now", default=None, help="ISO-8601 instant to read the deadlines against (default: now)")
    ap.add_argument("--check", action="store_true", help="print nothing, exit 1 if a meeting owes a synthesis")
    args = ap.parse_args(argv)

    now = datetime.fromisoformat(args.now.replace("Z", "+00:00")) if args.now else datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    directory = Path(args.dir)
    files = sorted(p for p in directory.glob("*.md") if p.name.lower() != "readme.md")
    meetings = [parse_meeting(p) for p in files]

    owed = [m for m in meetings if status(m, now) == "overdue"]
    if args.check:
        for m in owed:
            print(f"UNSYNTHESISED: {m['path'].name} closed {m['closes_text']} and no synthesis is written")
        return 1 if owed else 0

    if not meetings:
        print(f"no meetings under {directory}")
        return 0

    for m in meetings:
        st = status(m, now)
        present = sorted(n for n, ok in m["positions"].items() if ok)
        missing = sorted(n for n, ok in m["positions"].items() if not ok)
        slots = len(present) + len(missing)
        if m["closes"] is None:
            when = f"closes '{m['closes_text']}' (unreadable as a time)"
        else:
            delta = m["closes"] - now
            hours = delta.total_seconds() / 3600
            when = (f"closes {m['closes_text']} ({hours:.0f}h left)" if hours >= 0
                    else f"closed {m['closes_text']} ({-hours:.0f}h ago)")
        print(f"{m['path'].name}  [{st}]  convener {m['convener'] or '(none named)'}  {when}")
        print(f"  positions: {len(present)}/{slots} present" + (f"; missing: {', '.join(missing)}" if missing else ""))
        print(f"  synthesis: {'written' if m['synthesis'] else 'not written'}")
        if m["question"]:
            print(f"  question: {m['question']}")

    print()
    print(f"{len(meetings)} meeting(s), {sum(1 for m in meetings if status(m, now) == 'open')} open, "
          f"{len(owed)} past the close with no synthesis")
    return 1 if owed else 0


if __name__ == "__main__":
    sys.exit(main())
