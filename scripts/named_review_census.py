#!/usr/bin/env python3
"""named_review_census.py — did the amigo a review was assigned to ever answer it?

Dmitri, 2026-11-02.

The ledger carries two different promises and only one of them has a queue:

* an *unread* item — filed by a wake, closed by the landing gate, read by nobody.
  `channels/item_ledger.py --reading-queue <amigo>` exists for this and is drained
  a few items a wake.
* a *named review* — a row with `assigned_to: <amigo>`, which is a wake saying
  "I want this one checked, and by you." There is no queue for this at all, and
  nothing anywhere counts whether the named amigo answered.

Measured 2026-11-02: of 603 items carrying a named assignment, **84 were never
answered by the amigo named**. Of those, 35 had no verdict from *any* model —
`auto:path` closed them because every path they named was present on main, which
is a statement about delivery and not about the work being right. This script is
the count, so the number stops having to be re-derived by hand.

Reads `channels/items.jsonl` only. It prints; it does not write, and it has no
opinion about whether an item *should* have been reviewed — only about whether
the named amigo ever left a row with a state on it.

Usage:
    python3 scripts/named_review_census.py
    python3 scripts/named_review_census.py --only gate-closed
    python3 scripts/named_review_census.py --json

Exit status is 0 whenever the ledger was read, including for a clean ledger: a
census is a measurement, not a gate. A missing or empty ledger is an error (2),
because "no items" and "I could not look" must not print the same way.
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LEDGER = REPO_ROOT / "channels" / "items.jsonl"

AMIGOS = ("desi", "claude", "gemini", "tarik", "dmitri", "gwen")

# How a silent assignment ended. Named so a reader can see the distinction the
# whole script is about: "closed" is not "reviewed".
GATE_CLOSED = "gate-closed"   # closed by auto:path / auto:land, no model verdict
READ_ELSEWHERE = "read-elsewhere"  # another amigo did read it
OPEN = "open"                 # no verdict of any kind yet


def load(path: Path) -> dict:
    """One entry per item id, built from every row that names it.

    The ledger is append-only and rows arrive in copies, so the *last* row for a
    field wins — the same rule `channels/item_ledger.py::load()` uses. Getting
    this wrong makes an item look open after it was closed.
    """
    rows: dict = collections.defaultdict(list)
    if not path.exists():
        raise SystemExit(f"named_review_census: no ledger at {path}")
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict) and row.get("id"):
                rows[row["id"]].append(row)
    if not rows:
        raise SystemExit(f"named_review_census: ledger at {path} is empty")
    return rows


def _last(rows: list, field: str):
    for row in reversed(rows):
        if row.get(field) is not None:
            return row[field]
    return None


def classify(rows: list) -> dict:
    """Decide what happened to one item's named assignment.

    Returns a dict with `assigned_to` (None if nobody was named) and `outcome`,
    one of the four words: answered / gate-closed / read-elsewhere / open.
    """
    assigned = _last(rows, "assigned_to")
    if assigned not in AMIGOS:
        return {"assigned_to": None, "outcome": None}

    verdicts = [r for r in rows if r.get("state")]
    answered_by_named = any(r.get("reviewer") == assigned and r.get("state") for r in rows)
    if answered_by_named:
        return {"assigned_to": assigned, "outcome": "answered"}
    if not verdicts:
        return {"assigned_to": assigned, "outcome": OPEN}

    model_readers = {r.get("reviewer") for r in verdicts if r.get("reviewer") in AMIGOS}
    if model_readers:
        return {"assigned_to": assigned, "outcome": READ_ELSEWHERE,
                "read_by": sorted(model_readers)}
    return {"assigned_to": assigned, "outcome": GATE_CLOSED,
            "closed_by": _last(rows, "reviewer")}


def census(rows: dict, amigo: str | None = None, only: str | None = None) -> dict:
    """Count the named assignments, optionally scoped before anything is counted.

    `amigo` and `only` filter at the *assignment* level, not at the printed list:
    a filtered census has to report the counts of what it kept, or `--only
    gate-closed --json` answers "1 silent item" while listing none. (This
    happened: the first version of this script filtered the list and left the
    totals whole, and the test below it caught that before the script shipped.)
    """
    per_assignee = {a: {"assigned": 0, "answered": 0, GATE_CLOSED: 0,
                        READ_ELSEWHERE: 0, OPEN: 0} for a in AMIGOS}
    items = []
    for item_id, item_rows in rows.items():
        verdict = classify(item_rows)
        if verdict["outcome"] is None:
            continue
        who = verdict["assigned_to"]
        if amigo and who != amigo:
            continue
        if only and verdict["outcome"] != only:
            continue
        per_assignee[who]["assigned"] += 1
        per_assignee[who][verdict["outcome"]] += 1
        if verdict["outcome"] != "answered":
            items.append({
                "id": item_id,
                "assigned_to": who,
                "outcome": verdict["outcome"],
                "closed_by": verdict.get("closed_by"),
                "read_by": verdict.get("read_by"),
                "title": (_last(item_rows, "short_title")
                          or _last(item_rows, "title") or "")[:90],
                "assigned_utc": _last(item_rows, "assigned_utc"),
            })
    items.sort(key=lambda i: (i["assigned_utc"] or "", i["id"]))
    totals = collections.Counter(i["outcome"] for i in items)
    return {
        "ledger_items": len(rows),
        "named_assignments": sum(v["assigned"] for v in per_assignee.values()),
        "silent": len(items),
        "by_outcome": dict(totals),
        "per_assignee": per_assignee,
        "items": items,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    ap.add_argument("--amigo", choices=AMIGOS, help="only assignments naming this amigo")
    ap.add_argument("--only", choices=(GATE_CLOSED, READ_ELSEWHERE, OPEN),
                    help="only silent assignments that ended this way")
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    result = census(load(Path(args.ledger)), amigo=args.amigo, only=args.only)
    items = result["items"]
    scope = ""
    if args.amigo or args.only:
        scope = " (scoped: " + ", ".join(
            s for s in (args.amigo and f"named {args.amigo}", args.only) if s) + ")"

    if args.json:
        result["scope"] = scope.strip() or None
        print(json.dumps(result, indent=1, sort_keys=True))
        return 0

    print(f"named review assignments in {result['ledger_items']} ledger items: "
          f"{result['named_assignments']}{scope}")
    print(f"never answered by the amigo named: {result['silent']}")
    for word in (GATE_CLOSED, READ_ELSEWHERE, OPEN):
        print(f"  {word:15s} {result['by_outcome'].get(word, 0):4d}")
    print("\nby assignee: assigned / answered / never answered (gate-closed · read "
          "elsewhere · open)")
    for who in AMIGOS:
        row = result["per_assignee"][who]
        if not row["assigned"]:
            continue
        silent = row["assigned"] - row["answered"]
        print(f"  {who:7s} {row['assigned']:4d} {row['answered']:4d} {silent:4d}      "
              f"({row[GATE_CLOSED]} · {row[READ_ELSEWHERE]} · {row[OPEN]})")
    if items:
        print(f"\n{'id':28s} {'named':7s} {'outcome':15s} title")
        for item in items[:args.limit]:
            print(f"  {item['id'][:26]:26s} {item['assigned_to']:7s} "
                  f"{item['outcome']:15s} {item['title']}")
        if len(items) > args.limit:
            print(f"  … and {len(items) - args.limit} more (--limit)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
