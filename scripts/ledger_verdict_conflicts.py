#!/usr/bin/env python3
"""The verdict a reviewer gave, and the verdict the machine left in its place.

WHY THIS EXISTS (measured 2026-11-23, Dmitri's 15:39Z wake)
-----------------------------------------------------------
`channels/item_ledger.py --queue dmitri` closes with one warning:

    item_ledger: 24 verdict(s) sit on disk as a mirror and are not in the ledger yet
      fold them in: python3 scripts/ledger_verdict_mirror.py replay

Running that command answers `would apply: 0   already-there-or-later: 787`. Both numbers are
correct and they are not about the same thing: `replay` refuses to walk a ledger row backwards,
so a mirror that is *older* than the row it would replace is skipped — silently, forever. The
warning keeps printing the same 24 ids every wake and the command it recommends cannot move one
of them. That is the shape the reader cannot see from either side.

What the 24 are, read one by one on 2026-11-23:

  11 of them are a reviewer's verdict that the landing machine overruled. The pattern is exact:
  an amigo wakes, judges the item, and writes (say) `postponed` at 13:32Z with the reason that
  stopped it; the run lands; the landing machine appends `accomplished` / `reviewer: auto:land`
  at 13:49Z because the run's files arrived. The item then reads *accomplished*, and the reason
  a model wrote is preserved only in a file under `channels/ledger-verdicts/` that no queue opens.

  13 are harmless in substance — the amigo said `accomplished` and so did the machine — but they
  cost the same thing: the reviewer's name and reasoning are replaced by a stamp, so the ledger
  cannot say who read the item, only that files appeared.

The worst case in the ledger is item 20261121T205015Z-b0467404. Five mirrors from this seat on
2026-11-22: accomplished 03:35Z, 05:35Z, 07:35Z, 09:36Z, then **rejected at 11:36Z**. The row
says `accomplished`, `auto:path`, 12:45Z. Five wakes of judgement, ending in a rejection, and
the record reads "delivered". The four duplicates are the same loop from the other side: a queue
that shows a finished item as waiting is a queue that gets reviewed again.

WHAT THIS DOES
--------------
Nothing writes. It lists the conflict and names both verdicts, so the reader can see which of
the two records to believe. It is deliberately not wired into CI as a pass/fail gate: a check
that fails on live data would block the landing machine, which is the machine that caused the
conflicts. `--check` exits 3 when any *reversed* verdict exists, and that exit code is for a
human or a wake, not for the gate.

USAGE
    python3 scripts/ledger_verdict_conflicts.py
    python3 scripts/ledger_verdict_conflicts.py --json
    python3 scripts/ledger_verdict_conflicts.py --check     # exit 3 if any verdict was reversed
    python3 scripts/ledger_verdict_conflicts.py --item <id>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "channels"))
import item_ledger  # noqa: E402

LEDGER = REPO / "channels" / "items.jsonl"
VERDICTS = REPO / "channels" / "ledger-verdicts"

MACHINE_REVIEWERS = ("auto:land", "auto:path")

#: An amigo's verdict that says *do not do this* — the ones a machine stamp can reverse.
HALTING = ("postponed", "rejected")


def is_machine(row: dict) -> bool:
    """True when a row's `reviewer` is the landing machine rather than a model.

    `is_path_check` is the ledger's own second spelling of the same fact (`auto:path`), and it is
    checked as well because a row written before that reviewer string was standardised carries the
    flag and not the name.
    """
    return row.get("reviewer") in MACHINE_REVIEWERS or item_ledger.is_path_check(row)


def conflicts(ledger: Path = LEDGER, verdicts: Path = VERDICTS) -> list[dict]:
    """Every mirror older than the row that replaced it, with what each of the two said.

    A mirror older than the ledger row is not automatically a conflict: replay has already applied
    it if the row carries the same verdict, and a later *review* legitimately supersedes an earlier
    one. The conflict is narrower, and it is the one nobody can see: the later row is a machine
    stamp, so nothing was judged later — the later row is delivery, and it displaced a judgement.
    """
    items = item_ledger.load(ledger)
    out: list[dict] = []
    if not verdicts.is_dir():
        return out
    for f in sorted(verdicts.glob("*.json")):
        try:
            rec = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        item_id, mirror_state = rec.get("id"), rec.get("state")
        if not item_id or not mirror_state:
            continue
        live = items.get(item_id)
        if not live or not is_machine(live):
            continue
        mirror_moment = item_ledger.verdict_moment(rec)
        live_moment = item_ledger.verdict_moment(live)
        if not mirror_moment or not live_moment or mirror_moment >= live_moment:
            continue
        out.append({
            "id": item_id,
            "mirror_file": f.name,
            "mirror_state": mirror_state,
            "mirror_reviewer": rec.get("reviewer", "?"),
            "mirror_utc": rec.get("state_utc", "?"),
            "mirror_reason": (rec.get("reason") or "")[:400],
            "ledger_state": live.get("state"),
            "ledger_reviewer": live.get("reviewer", "?"),
            "ledger_utc": live.get("state_utc", "?"),
            "reversed": mirror_state != live.get("state"),
            "halting": mirror_state in HALTING,
        })
    out.sort(key=lambda r: (not r["reversed"], r["mirror_utc"]))
    return out


def summarise(rows: list[dict]) -> dict:
    return {
        "conflicts": len(rows),
        "reversed": sum(1 for r in rows if r["reversed"]),
        "reversed_halting": sum(1 for r in rows if r["reversed"] and r["halting"]),
        "same_state": sum(1 for r in rows if not r["reversed"]),
        "items": len({r["id"] for r in rows}),
        "repeat_items": sorted(
            {r["id"] for r in rows
             if sum(1 for x in rows if x["id"] == r["id"]) > 1}),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ledger", type=Path, default=LEDGER)
    ap.add_argument("--verdicts", type=Path, default=VERDICTS)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check", action="store_true",
                    help="exit 3 when a reviewer's verdict was reversed by a machine stamp")
    ap.add_argument("--item", default="", help="only this item id")
    args = ap.parse_args(argv)

    rows = conflicts(args.ledger, args.verdicts)
    if args.item:
        rows = [r for r in rows if r["id"] == args.item]
    s = summarise(rows)
    if args.json:
        print(json.dumps({"summary": s, "rows": rows}, indent=1))
        return 3 if (args.check and s["reversed"]) else 0

    print(f"ledger_verdict_conflicts: {s['conflicts']} mirror(s) over {s['items']} item(s) are "
          f"older than a machine stamp that replaced them")
    print(f"  reversed (the machine says something the reviewer did not): {s['reversed']}"
          f" — {s['reversed_halting']} of them a postponed/rejected turned into accomplished")
    print(f"  same state, reviewer replaced by a stamp: {s['same_state']}")
    for r in rows:
        if not r["reversed"]:
            continue
        print(f"\n  {r['id']}")
        print(f"    reviewer said {r['mirror_state']} at {r['mirror_utc']} "
              f"({r['mirror_reviewer']}) — {r['mirror_file']}")
        if r["mirror_reason"]:
            print(f"      why: {r['mirror_reason']}")
        print(f"    ledger says   {r['ledger_state']} at {r['ledger_utc']} "
              f"({r['ledger_reviewer']})")
    rest = [r for r in rows if not r["reversed"]]
    if rest:
        print(f"\n  and {len(rest)} where both said accomplished — the reviewer's name and reason "
              f"were replaced by a stamp, which is not a reversal but is the same loss.")
    if s["repeat_items"]:
        print(f"\n  items judged more than once: {', '.join(s['repeat_items'])}")
    return 3 if (args.check and s["reversed"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
