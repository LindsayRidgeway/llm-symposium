#!/usr/bin/env python3
"""Take, and later diff, a snapshot of the review queue.

The review-blockage experiment (`channels/reports/2026-10-12-review-blockage-experiment.md`) is read as
one question per body: *did an item leave the queue that carries its name?* A queue is the set of
`items.jsonl` records that sit in W (waiting for review) with `assigned_to == <amigo>`. The before-count
is a snapshot taken once; every later read is a `--diff` against it, so the read is a command and not a
re-derivation — the failure the 2026-09-23 note names ("UNLANDED IS NOT MISSING": a path absent from
main is a delivery state, not work to redo) applies equally to a queue: an id absent from a queue that
was not diffed against its before-count is not a measurable drain.

Why a hash over the **sorted** ids: order is noise, membership is the signal. An id that merely moved
position is not a change; an id that left is visible as a removed id, which is the only thing the
experiment counts.

    python3 channels/queue_snapshot.py --write            # today's snapshot, into channels/reports/
    python3 channels/queue_snapshot.py --diff <path>      # what changed since that file
    python3 channels/queue_snapshot.py --diff             # newest snapshot in channels/reports/

Exit code of `--diff`: 0 if an item has left some queue, 1 if none has — so a wake can branch on it.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REPORTS = REPO / "channels" / "reports"

# The ledger is the one owner of "what is waiting"; import its own predicate rather than copy it, so
# the snapshot cannot drift from `item_ledger --queue` (letters and reassignment rules live there).
_spec = importlib.util.spec_from_file_location("item_ledger", REPO / "channels" / "item_ledger.py")
_il = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_il)

AMIGOS = _il.AMIGOS


def queue_ids(items: dict, amigo: str) -> list[str]:
    """The waiting items that carry this amigo's name, sorted. Sorted because order is noise."""
    return sorted(r["id"] for r in items.values()
                  if _il.letter_for(r) == "W" and r.get("assigned_to") == amigo)


def digest(ids: list[str]) -> str:
    """A short, order-independent fingerprint of a membership set — the same form the 10-12 file used."""
    return hashlib.sha256("\n".join(sorted(ids)).encode()).hexdigest()[:16]


def snapshot(items: dict | None = None) -> dict:
    items = _il.load() if items is None else items
    per = {a: queue_ids(items, a) for a in AMIGOS}
    return {
        "taken_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "counts": {a: len(per[a]) for a in AMIGOS},
        "sha256_of_sorted_ids": {a: digest(per[a]) for a in AMIGOS},
        "ids": per,
    }


def write(path: str | None = None) -> Path:
    data = snapshot()
    out = Path(path) if path else REPORTS / f"{data['taken_utc'][:10]}-queue-snapshot.json"
    out.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(REPO)}: "
          + ", ".join(f"{a}={data['counts'][a]}" for a in AMIGOS))
    return out


def newest() -> Path:
    files = sorted(REPORTS.glob("*-queue-snapshot.json"))
    if not files:
        raise SystemExit("no snapshot in channels/reports/ — take one with --write")
    return files[-1]


def diff(path: str | None = None, items: dict | None = None) -> int:
    src = Path(path) if path else newest()
    snap = json.loads(src.read_text(encoding="utf-8"))
    items = _il.load() if items is None else items
    print(f"snapshot {src.name} taken {snap.get('taken_utc', '?')}")
    any_left = False
    for a in AMIGOS:
        if a not in snap.get("ids", {}):
            print(f"  {a}: not in this snapshot (taken before the queue named {a})")
            continue
        ids = queue_ids(items, a)
        old = snap.get("ids", {}).get(a, [])
        h, oh = digest(ids), snap.get("sha256_of_sorted_ids", {}).get(a)
        added = sorted(set(ids) - set(old))
        removed = sorted(set(old) - set(ids))
        print(f"  {a}: {snap.get('counts', {}).get(a, 0)} -> {len(ids)}  "
              f"{oh} -> {h}  {'unchanged' if h == oh else 'CHANGED'}")
        if removed:
            any_left = True
            print(f"      left the queue: {', '.join(removed)}")
        if added:
            print(f"      added: {', '.join(added)}")
    print("RESULT: " + ("an item left a queue" if any_left else "no item has left any queue"))
    return 0 if any_left else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", nargs="?", const="", default=None, metavar="PATH",
                    help="take a snapshot (optionally to PATH)")
    ap.add_argument("--diff", nargs="?", const="", default=None, metavar="PATH",
                    help="diff the live queue against a snapshot (default: newest)")
    args = ap.parse_args(argv)
    if args.write is None and args.diff is None:
        ap.print_help()
        return 2
    if args.write is not None:
        write(args.write or None)
    if args.diff is not None:
        return diff(args.diff or None)
    return 0


if __name__ == "__main__":
    sys.exit(main())
