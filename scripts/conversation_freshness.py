#!/usr/bin/env python3
"""conversation_freshness.py — how long since each amigo last appended to its conversation log.

Why this exists (2026-11-01). `scripts/append-goose.py` writes the distilled record of a Goose session
into `channels/conversation/<amigo>.md` — the human's message and the amigo's final response, never the
thinking. It is a real practice: 249 commits touched that directory in the fortnight to 2026-11-01. But
it is a *habit*, not a mechanism: the agenda index has a test that fails when it drifts from its sources,
and the conversation logs have nothing. On 2026-11-01 my own log's newest entry was two days old and the
three before that were battery warnings rather than conversation.

A stale log is not automatically a defect. Clause 6 of agenda 35 says dormancy is a *recorded* state, and
an amigo may legitimately go quiet. What is a defect is staleness nobody can see. So this reports; it does
not fail the suite. Silence stays a legitimate state; unobserved silence does not.

Usage:
    python3 scripts/conversation_freshness.py                  # table, exit 0
    python3 scripts/conversation_freshness.py --stale-after 7   # exit 1 if any log is older (for a timer)
    python3 scripts/conversation_freshness.py --json
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONV = REPO / "channels" / "conversation"

# Two stamp formats are in the record: [Goose 2026-11-01 09:55] and [Telegram 2026-10-30-003519]
GOOSE = re.compile(r"\[Goose (\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2})\]")
TELEGRAM = re.compile(r"\[Telegram (\d{4}-\d{2}-\d{2})-(\d{2})(\d{2})(\d{2})\]")


def last_stamp(text: str) -> dt.datetime | None:
    """The newest stamp in a log, from either format. None if the log carries no stamp at all."""
    found: list[dt.datetime] = []
    for m in GOOSE.finditer(text):
        try:
            found.append(dt.datetime.strptime(f"{m.group(1)} {m.group(2)}", "%Y-%m-%d %H:%M"))
        except ValueError:
            pass
    for m in TELEGRAM.finditer(text):
        try:
            found.append(
                dt.datetime.strptime(f"{m.group(1)} {m.group(2)}:{m.group(3)}", "%Y-%m-%d %H:%M")
            )
        except ValueError:
            pass
    return max(found) if found else None


def scan(now: dt.datetime | None = None, conv: Path | None = None) -> list[dict]:
    """Rows for every conversation log. `conv` is injectable so the test does not depend on the repo."""
    now = now or dt.datetime.utcnow()
    rows = []
    for path in sorted((conv or CONV).glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        body = path.read_text(encoding="utf-8", errors="replace")
        # A notes file is not a conversation: if no exchange with the human is in it, skip it.
        if "**Lindsay:**" not in body:
            continue
        stamp = last_stamp(body)
        age = None if stamp is None else round((now - stamp).total_seconds() / 86400, 1)
        rows.append(
            {
                "amigo": path.stem,
                "last": stamp.strftime("%Y-%m-%d %H:%M") if stamp else "(no stamp)",
                "days": age,
                "lines": sum(1 for _ in path.open(encoding="utf-8", errors="replace")),
            }
        )
    return sorted(rows, key=lambda r: (r["days"] is None, -(r["days"] or 0)))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stale-after", type=float, default=None,
                    help="exit 1 if any log is older than this many days (for a timer)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--state", default=None,
                    help="path to a small state file: alert once per change of the stale set, not daily")
    args = ap.parse_args()

    rows = scan()
    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        print("amigo        last append          age      lines")
        for r in rows:
            age = "unknown" if r["days"] is None else f"{r['days']:>5.1f}d"
            print(f"{r['amigo']:<12} {r['last']:<19} {age:>7}  {r['lines']:>6}")

    if args.stale_after is None:
        return 0

    stale = [r for r in rows if r["days"] is None or r["days"] > args.stale_after]
    if not stale:
        return 0

    # A daily timer that repeats the same alert every morning is a nag, not a gate. Speak when the
    # stale set changes; stay quiet when it has not.
    names = sorted(r["amigo"] for r in stale)
    if args.state:
        try:
            previous = json.loads(Path(args.state).read_text()).get("stale", [])
        except (OSError, ValueError):
            previous = []
        if previous == names:
            print("no change in the stale set since the last alert — staying quiet")
            return 0
        Path(args.state).write_text(json.dumps({"stale": names, "checked": dt.datetime.utcnow().isoformat()}))

    print()
    for r in stale:
        age = "no timestamp at all" if r["days"] is None else f"{r['days']:.1f} days"
        print(f"STALE: {r['amigo']} — last conversation entry {age} old ({r['last']})")
    print("\nEach amigo appends with: python3 scripts/append-goose.py <amigo> \"<human>\" \"<response>\"")
    return 1


if __name__ == "__main__":
    sys.exit(main())
