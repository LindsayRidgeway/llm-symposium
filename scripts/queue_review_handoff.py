#!/usr/bin/env python3
"""Give Tarik a review: mirror the ledger items assigned to him into the queue his body claims.

Why this exists (2026-10-17). Every amigo is now in the reviewer draw, but Tarik's body does not
choose its own work: it claims the oldest pending task from `channels/tarik-goose-handoff.json` and its
instruction says *"this selected task is your complete work scope."* A review assigned to Tarik that is
not in that file is invisible to him — the item would sit frozen on a name that cannot answer, which is
worse than not naming him at all.

So the adapter runs one way: ledger -> handoff queue, idempotent, no coupling from the ledger back into
Tarik's harness.

    python3 scripts/queue_review_handoff.py            # show what it would add
    python3 scripts/queue_review_handoff.py --write    # add it
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "channels"))
import item_ledger as il  # noqa: E402

QUEUE = REPO / "channels" / "tarik-goose-handoff.json"
AMIGO = "tarik"


def task_for(rec: dict) -> dict:
    item = rec["id"]
    paths = ", ".join(rec.get("paths") or []) or "(the item names no paths)"
    return {
        "id": f"review-{item}",
        "source": "review",
        "status": "pending",
        "created_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "title": f"Review: {rec.get('short_title') or rec.get('title') or item}",
        "reason_for_goose": (
            "Assigned to Tarik by the item ledger's reviewer draw (2026-10-17: every amigo reviews). "
            f"The item was written by {rec.get('amigo')} and is waiting for a different architecture "
            "to judge it."
        ),
        "instructions": (
            f"Review ledger item {item}. Read its report in {rec.get('amigo')}-bot/tick-state/runs/{item}/ "
            f"and the paths it names: {paths}. Judge what is on disk, not the run's own claim, and do not "
            "redo the work. Then close it with exactly one exit, the reason being the record: "
            f"`python3 channels/item_ledger.py --review {item} --state accomplished|postponed|rejected "
            f'--reason "why" --reviewer tarik`. accomplished only for work you did yourself in this '
            "wake; postponed for what stops it; rejected for what should never be done."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--queue", default=str(QUEUE))
    a = ap.parse_args()

    path = Path(a.queue)
    data = json.loads(path.read_text(encoding="utf-8"))
    tasks = data.setdefault("tasks", [])
    have = {t.get("id") for t in tasks}

    waiting = [r for r in il.load().values()
               if il.letter_for(r) == "W" and r.get("assigned_to") == AMIGO]
    new = [task_for(r) for r in waiting if f"review-{r['id']}" not in have]

    if not new:
        print(f"nothing to queue: {len(waiting)} item(s) waiting on {AMIGO}, all already handed over")
        return 0
    for t in new:
        print(f"  + {t['id']}  {t['title']}")
    if not a.write:
        print(f"(dry run: {len(new)} task(s) would be added; --write to add)")
        return 0
    tasks.extend(new)
    path.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    print(f"added {len(new)} task(s) to {path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
