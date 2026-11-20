#!/usr/bin/env python3
"""The value queue: what the commons exists to make, and the condition that closes each item.

Why this exists (2026-11-19, Desi). The founder asked the question the clockwork could not answer:
*three wakes have gone into one piece of research, which is validating a table — will your wakes ever
move on to a different value-work item?* Measured answer: no, not by themselves. Review work rotates
because items are assigned by a draw; value work was chosen freely by each wake, and a wake chooses
what is at the front of its own prompt. Nothing owned the pointer, so the same item stayed at the front
for three wakes and would have stayed for thirty.

So value work gets the thing review work already had: a queue, a head, and a rule that finishing the
head closes it and moves the pointer. `done_when` is not decoration — an item with no closing condition
is a project, and a project at the head of a queue is the same jam in a slower form.

    python3 scripts/value_queue.py --next            # the head, with its closing condition
    python3 scripts/value_queue.py --list           # every item and its state
    python3 scripts/value_queue.py --done mcr-class-b --evidence "research/....md"

Exit 0 normally, 1 when the queue is empty (an empty value queue is a defect, not a rest).
"""
from __future__ import annotations

# `from __future__` added 2026-11-20 (Desi): the annotations below use `X | None`, which is
# evaluated at import time before Python 3.10. Every workflow pins 3.10, but the host the wakes
# run on has 3.9.6, so this tool — the one every wake is told to run by hand — raised
# `TypeError: unsupported operand type(s) for |` there and the queue could not be read or closed
# from the seat it belongs to. Same repair as scripts/wake_spend_record.py already carries.
import argparse
import datetime
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
QUEUE = REPO / "channels" / "value-queue.json"
OPEN = ("open", "in-progress")


def load(path: Path | None = None) -> dict:
    path = path or QUEUE
    if not path.is_file():
        return {"items": []}
    return json.loads(path.read_text(encoding="utf-8"))


def head(data: dict) -> dict | None:
    for item in data.get("items") or []:
        if (item.get("status") or "").lower() in OPEN:
            return item
    return None


def next_up(data: dict, count: int = 2) -> list[dict]:
    return [i for i in (data.get("items") or [])
            if (i.get("status") or "").lower() in OPEN][:count]


def worked(item_id: str, note: str = "", path: Path | None = None,
           when: datetime.date | None = None) -> dict:
    """Record that an item was worked on, and send it to the back of the queue.

    Added 2026-11-19 at the founder's follow-up, which was the better idea: *shouldn't value-work
    rotate? maybe a task would never finish, but at least it wouldn't stay at the top of the queue.*
    Closure and rotation are different jobs and the first version only had closure. An item that takes
    a week of wakes would hold the head for a week even though every wake did real work on it — and a
    queue where the head is whatever was last worked is a queue with one item in it.

    So this is push-to-bottom, the same rule the to-do lists already use for repeats: work it, write
    what you did, and the next wake sees something else. Rotation costs nothing when an item is nearly
    done and forgives everything when it is not.
    """
    path = path or QUEUE
    data = load(path)
    items = data.get("items") or []
    hit = None
    for item in items:
        if item.get("id") == item_id:
            hit = item
            break
    if hit is None:
        raise LookupError(f"no value item with id {item_id!r} in {path.name}")
    hit["last_worked"] = (when or datetime.date.today()).isoformat()
    if note.strip():
        hit["progress"] = (note.strip() if not hit.get("progress")
                           else hit["progress"].rstrip() + " " + note.strip())
    items.remove(hit)
    items.append(hit)                       # push to the bottom, finished or not
    data["items"] = items
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return hit


def done(item_id: str, evidence: str, path: Path | None = None,
         when: datetime.date | None = None) -> dict:
    """Close an item. Evidence is required: an item finished with no artefact is a claim, not a close."""
    path = path or QUEUE
    if not (evidence or "").strip():
        raise ValueError("a value item is closed by an artefact; --evidence is required")
    data = load(path)
    for item in data.get("items") or []:
        if item.get("id") != item_id:
            continue
        item["status"] = "done"
        item["done_on"] = (when or datetime.date.today()).isoformat()
        item["evidence"] = evidence.strip()
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return item
    raise LookupError(f"no value item with id {item_id!r} in {path.name}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--next", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--done", metavar="ID")
    ap.add_argument("--evidence")
    ap.add_argument("--worked", metavar="ID", help="record work and push the item to the back")
    ap.add_argument("--note", help="with --worked: one line on what you did")
    args = ap.parse_args(argv)

    data = load()
    if args.done:
        try:
            item = done(args.done, args.evidence or "")
        except (ValueError, LookupError) as exc:
            print(f"value_queue: {exc}")
            return 1
        print(f"value_queue: {item['id']} closed on {item['done_on']} — {item['evidence'][:80]}")
        nxt = head(load())
        print(f"value_queue: the head is now {nxt['id'] if nxt else 'nothing — the queue is empty'}")
        return 0
    if args.worked:
        try:
            item = worked(args.worked, args.note or "")
        except LookupError as exc:
            print(f"value_queue: {exc}")
            return 1
        print(f"value_queue: {item['id']} worked on {item['last_worked']} and pushed to the bottom")
        nxt = head(load())
        print(f"value_queue: the head is now {nxt['id'] if nxt else 'nothing'}")
        return 0
    if args.list:
        for item in data.get("items") or []:
            print(f"  [{item.get('status'):11}] {item.get('id'):22} {item.get('title')[:70]}")
        return 0
    items = next_up(data)
    if not items:
        print("value_queue: nothing open. An empty value queue is a defect, not a rest.")
        return 1
    print("=== VALUE QUEUE — what the commons exists to make ===")
    for i, item in enumerate(items):
        print(f"- {'HEAD' if i == 0 else 'next'}  {item['id']}  {item['title']}")
        print(f"    closes when: {item['done_when']}")
        if item.get("progress"):
            print(f"    so far: {item['progress']}")
    print("  worked on it, finished or not? push it to the back so the queue rotates: "
          "python3 scripts/value_queue.py --worked <id> --note '<one line>'")
    print("  close it with: python3 scripts/value_queue.py --done <id> --evidence '<path or url>'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
