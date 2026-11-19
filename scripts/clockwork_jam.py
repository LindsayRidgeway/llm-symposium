#!/usr/bin/env python3
"""The founder's de-jamming procedure, as a check rather than a habit.

His procedure, 2026-11-19: (1) examine what the next wake would do first; (2) run the wake; (3)
examine again — if the head is the same, the clockwork is jammed, so fix it; (4) loop; (5) stop when a
wake has produced one of the things that matter outside the commons.

Running it by hand found the first jam within the hour (a sent letter that the calendar kept asking
for). Running it by hand also found the procedure's own defect the second time: a head dated *in the
future* is identical before and after a wake and is not a jam at all — nothing is due, the calendar is
merely waiting. So the check distinguishes the two, because a test that fires on a healthy idle day
teaches its reader to ignore it.

    python3 scripts/clockwork_jam.py --before-before...   # see --help

The interface is deliberately two snapshots rather than a stored history: a snapshot is what a wake's
prompt already contains, and comparing two of them is the whole procedure.
"""
import argparse
import datetime
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def head(amigo: str, repo: Path = REPO, today: datetime.date | None = None) -> dict:
    """The first non-empty item in the seat's agenda: due block, then review queue, then reading."""
    spec = importlib.util.spec_from_file_location("we_jam", repo / "channels" / "wake_engine.py")
    we = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(we)                     # type: ignore[union-attr]
    today = today or datetime.date.today()

    rows = we.due_items((repo / "to-do-lists" / f"{amigo}.md").read_text(encoding="utf-8"),
                        today=today, repo=str(repo))
    rows = we._recurring_rows(rows, repo, amigo, today)
    live = [r for r in rows if r[1] in ("overdue", "today", "soon")]
    if live:
        when, kind, text, _rule, _note = live[0]
        return {"block": "due", "id": text[:60], "when": when.isoformat(), "kind": kind}
    try:
        sys.path.insert(0, str(repo / "channels"))
        import item_ledger as il
        path = repo / "channels" / "items.jsonl"
        waiting = [r for r in il.load(path).values()
                   if il.letter_for(r) == "W" and r.get("assigned_to") == amigo]
        if waiting:
            waiting.sort(key=lambda r: r.get("assigned_utc") or r.get("filed_utc") or "")
            return {"block": "review", "id": waiting[0].get("id"), "when": None, "kind": "waiting"}
        reading = il.reading_queue(path, who=amigo)
        if reading:
            return {"block": "reading", "id": reading[0].get("id"), "when": None, "kind": "unread"}
    except Exception as exc:                        # noqa: BLE001 — a check must not crash a wake
        return {"block": "error", "id": f"{type(exc).__name__}: {exc}", "when": None, "kind": None}
    return {"block": "none", "id": "", "when": None, "kind": None}


def verdict(before: dict, after: dict, today: datetime.date | None = None) -> dict:
    """Jammed, moving, or waiting — the distinction the procedure needed and did not have."""
    today = today or datetime.date.today()
    same = (before.get("block"), before.get("id")) == (after.get("block"), after.get("id"))
    if not same:
        return {"jam": False, "why": "the head moved"}
    if after.get("block") != "due":
        return {"jam": True,
                "why": "the same %s item is at the head and no clock will move it" % after["block"]}
    when = datetime.date.fromisoformat(after["when"]) if after.get("when") else None
    if when and when > today:
        return {"jam": False,
                "why": "the head is dated %s, which is in the future: nothing is due, the calendar "
                       "is waiting rather than stuck" % when.isoformat()}
    return {"jam": True,
            "why": "the head is due %s and is still the head after the wake" % after.get("when")}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--amigo", required=True)
    ap.add_argument("--before", help="JSON snapshot from a previous run")
    ap.add_argument("--save", help="write this run's snapshot to a file")
    args = ap.parse_args(argv)
    now = head(args.amigo)
    print(json.dumps(now))
    if args.save:
        Path(args.save).write_text(json.dumps(now) + "\n", encoding="utf-8")
    if args.before:
        before = json.loads(Path(args.before).read_text(encoding="utf-8"))
        v = verdict(before, now)
        print(("JAMMED — " if v["jam"] else "not jammed — ") + v["why"])
        return 1 if v["jam"] else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
