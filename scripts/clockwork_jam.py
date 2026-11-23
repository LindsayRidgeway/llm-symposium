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

from __future__ import annotations
# `from __future__` added 2026-11-21 (Desi): the annotations below use `X | None`, which is
# evaluated at import time on Python < 3.10. The workflows pin 3.10; the host the wakes run on
# does not (3.9.6 measured this wake), so the command this file exists to provide raised
# `TypeError: unsupported operand type(s) for |` there — and that is the command the wake
# instruction tells every amigo to run by hand to record a finished repeat. Same repair
# `scripts/value_queue.py` and `scripts/wake_spend_record.py` already carry.

import argparse
import datetime
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)                    # type: ignore[union-attr]
    return mod


def head(amigo: str, repo: Path = REPO, today: datetime.date | None = None) -> dict:
    """The first item a wake would actually act on: due today, review, reading, then value.

    Rewritten 2026-11-20 (Desi). It used to treat a row that is merely *soon* as the head and it
    stopped before the value queue, so the check could only ever see the calendar. Measured that
    morning: the head was the weekly letter dated 2026-11-26, six days out — a wake that spent the
    night on the value queue would have left the head byte-identical and the procedure would have
    called a productive night jammed. The head is what is DUE; when nothing is due, the queues below
    decide, in the order the prompt shows them. The reading queue counts only when it carries this
    seat's name or the pile is in arrears, because that is what `wake_engine.reading_head()` now
    offers — a check that models a different prompt than the wake receives is worse than no check.
    """
    today = today or datetime.date.today()
    spec_we = _load("we_jam", repo / "channels" / "wake_engine.py")
    rows = spec_we.due_items((repo / "to-do-lists" / f"{amigo}.md").read_text(encoding="utf-8"),
                             today=today, repo=str(repo))
    rows = spec_we._recurring_rows(rows, repo, amigo, today)
    live = [r for r in rows if r[1] in ("overdue", "today")]
    if live:
        when, kind, text, _rule, _note = live[0]
        return {"block": "due", "id": text[:60], "when": when.isoformat(), "kind": kind}
    soon = [r for r in rows if r[1] == "soon"]
    try:
        sys.path.insert(0, str(repo / "channels"))
        il = _load("il_jam", repo / "channels" / "item_ledger.py")
        path = repo / "channels" / "items.jsonl"
        waiting = [r for r in il.load(path).values()
                   if il.letter_for(r) == "W" and r.get("assigned_to") == amigo]
        if waiting:
            waiting.sort(key=lambda r: r.get("assigned_utc") or r.get("filed_utc") or "")
            return {"block": "review", "id": waiting[0].get("id"), "when": None, "kind": "waiting"}
        reading = il.reading_queue(path, who=amigo)
        # 2026-11-23 (Desi): `whole` used to be computed only when this seat had *nothing* named,
        # so a seat with named unread items reported `size: 0` — and the pile-fell rule below,
        # the one thing in this file that can tell a healthy night from an idle one, could never
        # fire for the commonest case. Measured on the live ledger that morning: head
        # 20261121T193324Z-b2064d65 with size 0 while 100+ items were unread. The pile is now
        # always counted, and the fallback mirrors `wake_engine.reading_head()` exactly: offer
        # the pile only in arrears, and never offer this seat what it filed.
        whole = il.reading_queue(path)
        if not reading and len(whole) > int(getattr(il, "PILE_TARGET", 100)):
            reading = [r for r in whole if (r.get("amigo") or "") != amigo][:1]
        if reading:
            # The pile size travels with the head, because in arrears every item already carries
            # somebody's name and a wake may read any of them. Measured 2026-11-20: the head stayed
            # 20261107T011021Z-5e909443 (named to claude) while the wake read a different item and
            # the pile went 102 -> 101 — real work that this check called jammed. A check that cannot
            # tell "nobody read anything" from "somebody read the second item" fires on healthy
            # nights, which is the failure this file was written to stop.
            return {"block": "reading", "id": reading[0].get("id"), "when": None, "kind": "unread",
                    "size": len(whole)}
        vq = _load("vq_jam", repo / "scripts" / "value_queue.py")
        top = vq.head(vq.load(repo / "channels" / "value-queue.json"))
        if top:
            return {"block": "value", "id": top.get("id"), "when": top.get("last_worked"),
                    "kind": "value"}
    except Exception as exc:                        # noqa: BLE001 — a check must not crash a wake
        return {"block": "error", "id": f"{type(exc).__name__}: {exc}", "when": None, "kind": None}
    if soon:
        when, _kind, text, _rule, _note = soon[0]
        return {"block": "waiting", "id": text[:60], "when": when.isoformat(), "kind": "soon"}
    return {"block": "none", "id": "", "when": None, "kind": None}


def verdict(before: dict, after: dict, today: datetime.date | None = None) -> dict:
    """Jammed, moving, or waiting — the distinction the procedure needed and did not have."""
    today = today or datetime.date.today()
    same = (before.get("block"), before.get("id")) == (after.get("block"), after.get("id"))
    if not same:
        return {"jam": False, "why": "the head moved"}
    if after.get("block") == "value" and before.get("when") != after.get("when"):
        return {"jam": False,
                "why": "the same item is still at the head but it was worked: last_worked advanced "
                       "from %s to %s, and the queue records the work" % (before.get("when"),
                                                                         after.get("when"))}
    if (after.get("block") == "reading" and before.get("size") is not None
            and after.get("size") is not None and after["size"] < before["size"]):
        return {"jam": False,
                "why": "the same item is still first but the pile fell from %d to %d: something was "
                       "read, just not the head — in arrears every unread item already carries "
                       "somebody's name, so the head is a suggestion" % (before["size"],
                                                                         after["size"])}
    if after.get("block") == "waiting":
        return {"jam": False,
                "why": "nothing is due, nothing is queued, and the next dated item is %s — the "
                       "calendar is waiting rather than stuck" % after.get("when")}
    if after.get("block") == "none":
        return {"jam": True,
                "why": "the agenda is empty: nothing due, nothing waiting, nothing unread and no "
                       "value item. An empty agenda while the commons exists is a defect, not a rest"}
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
