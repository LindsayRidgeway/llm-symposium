#!/usr/bin/env python3
"""What is due — a reader for `to-do-lists/`.

One file per amigo (see `to-do-lists/README.md`). This script does not write anything;
it reads every list and reports what is overdue, due today, and coming, expanding
recurring items to their **next instance only** using the engine the commons already
owns (`probes/recurrence_projection.py`) rather than a second implementation of
recurrence.

Item format:
    - [ ] YYYY-MM-DD — text
          continuation lines, indented, are context
          repeat: FREQ=WEEKLY;INTERVAL=1[;COUNT=n][;UNTIL=YYYYMMDD]

Usage:
    python3 scripts/todo_due.py            # everything
    python3 scripts/todo_due.py desi       # one amigo
    python3 scripts/todo_due.py --days 14  # widen the coming window
"""
from __future__ import annotations

import datetime as dt
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LISTS = os.path.join(REPO, "to-do-lists")
sys.path.insert(0, os.path.join(REPO, "probes"))

try:
    from recurrence_projection import expand_rrule, validate_rrule, UnsupportedRRULEError
except Exception:  # pragma: no cover - the engine should be there; say so if it is not
    expand_rrule = validate_rrule = None

    class UnsupportedRRULEError(ValueError):
        pass

ITEM = re.compile(r"^- \[ \] (\d{4})-(\d{2})-(\d{2}) — (.*)$")
CONT = re.compile(r"^\s{2,}(\S.*)$")


def parse(path: str):
    items, cur = [], None
    for line in open(path, encoding="utf-8"):
        m = ITEM.match(line.rstrip("\n"))
        if m:
            y, mo, d, text = m.groups()
            cur = {"date": dt.date(int(y), int(mo), int(d)), "text": text.strip(), "extra": []}
            items.append(cur)
            continue
        if cur is not None:
            c = CONT.match(line.rstrip("\n"))
            if c:
                cur["extra"].append(c.group(1).strip())
            elif line.strip() == "":
                cur = None
    return items


def repeat_of(item) -> str | None:
    for line in item["extra"]:
        if line.lower().startswith("repeat:"):
            return line.split(":", 1)[1].strip()
    return None


def next_instance(item, today: dt.date):
    """Next occurrence on/after today, or None. Returns (date, note)."""
    rule = repeat_of(item)
    if not rule:
        return None, None
    if expand_rrule is None:
        return None, "engine unavailable"
    try:
        validate_rrule(  # raises on anything outside the supported subset
            __import__("recurrence_projection").parse_rrule(rule)
        )
        occ, truncated = expand_rrule(rule, item["date"], horizon_days=400, limit=600)
    except UnsupportedRRULEError as e:
        return None, f"unsupported rule: {e}"
    except Exception as e:  # pragma: no cover
        return None, f"bad rule: {e}"
    ahead = [d for d in occ if d >= today]
    if not ahead:
        return None, "rule exhausted"
    return ahead[0], ("truncated horizon" if truncated else None)


def main() -> int:
    args = [a for a in sys.argv[1:]]
    days = 7
    if "--days" in args:
        i = args.index("--days")
        days = int(args[i + 1])
        del args[i:i + 2]
    who = args[0] if args else None

    today = dt.date.today()
    if not os.path.isdir(LISTS):
        print("no to-do-lists/ directory")
        return 1

    files = sorted(
        f for f in os.listdir(LISTS)
        if f.endswith(".md") and f != "README.md" and (who is None or f[:-3] == who)
    )
    if not files:
        print(f"no list for {who!r}" if who else "no lists found")
        return 1

    print(f"=== due lists — {today.isoformat()} ===")
    total = 0
    for f in files:
        items = parse(os.path.join(LISTS, f))
        rows = []
        for it in items:
            eff, note = it["date"], None
            nxt, why = next_instance(it, today)
            if nxt:
                eff, note = nxt, ("(next of repeat)" if not why else f"({why})")
            age = (eff - today).days
            rows.append((eff, age, it["text"], note))
        rows.sort(key=lambda r: (r[0], r[2]))
        print(f"\n--- {f[:-3]}  ({len(rows)} open)")
        if not rows:
            print("    (empty)")
        for eff, age, text, note in rows:
            if age < 0:
                label = f"OVERDUE {abs(age)}d"
            elif age == 0:
                label = "TODAY"
            elif age <= days:
                label = f"in {age}d"
            else:
                label = f"in {age}d"
            flag = "  " if age <= days else "  "
            print(f"  {flag}{eff}  {label:>12}  {text[:96]}")
            if note:
                print(f"                   {note}")
            if age <= days:
                total += 1
    print(f"\n{total} item(s) at or inside the {days}-day window.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
