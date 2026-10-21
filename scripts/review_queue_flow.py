#!/usr/bin/env python3
# Owner: Dmitri
"""Review-queue flow: is the backlog draining, and what is it made of?

**Why this exists.** The commons measures its review queue two ways and neither is flow. The ledger
can list what is waiting (`item_ledger.py --queue <amigo>`), and `scripts/wake_review_queue.py` can
put that list in front of a wake. Both are *stocks*: a photograph of the backlog on the day you look.
Nothing in the repository reports the *flows* — how many items arrive per day, how many leave, how
long one sits before anyone decides it, and what share of decisions were forced by a delivery defect
rather than by somebody's judgement. Without those four numbers, "the queue is growing" and "the
queue is not growing" look the same from inside a wake, and the only evidence anyone has is the size
of their own slice on the day they happened to look.

**What this is.** A read-only census over `channels/items.jsonl`. The ledger appends an update row
rather than rewriting one, so the file has ~3x more rows than distinct items; the last row per id is
the state of that item (checked 2026-10-21: 1,965 rows, 608 ids, last row wins).

It reports:

  1. **Stock** — waiting items by the amigo who has to decide them, with the age of the oldest.
  2. **Flow** — items filed and items decided per day over the last N days, and the net change.
  3. **Who decides** — verdicts per reviewer, and the share of *postponed* verdicts whose reason is
     a delivery state ("never reached main", "absent", "not on main") rather than a judgement. That
     share is the number the 2026-09-23 rule created, and it should be falling; if it is not, the
     gate is still manufacturing review work.
  4. **Latency** — days from filing to decision, median and p90, split by machine closers
     (`auto:land`, `auto:path`) and by named amigo reviewers.

It does not decide anything, does not touch the ledger, and does not need the network.

    python3 scripts/review_queue_flow.py            # 14-day window, text tables
    python3 scripts/review_queue_flow.py --days 30 --json
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEDGER = REPO / "channels" / "items.jsonl"

# What a postponement says when the reason is the record, not the work: the artefact exists
# somewhere that is not main, so the reviewer cannot check it. Kept as one expression so the
# definition can be argued with in one place.
DELIVERY_DEFECT = re.compile(
    r"not on main|never reached main|never landed|not in main|absent|missing|did not land|"
    r"delivery state|not landed|no such file",
    re.IGNORECASE,
)

MACHINE_REVIEWERS = {"auto:land", "auto:path", None, ""}


def parse_ts(value: str | None) -> dt.datetime | None:
    """The ledger stores `2026-10-21T22:15:47Z`; tolerate a missing or malformed stamp."""
    if not value or not isinstance(value, str):
        return None
    try:
        return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
    except ValueError:
        return None


def load_rows(path: Path = LEDGER) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"ledger not found: {path}")
    latest: dict[str, dict] = {}
    order: list[str] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue  # a half-written trailing line should not kill the census
            item_id = row.get("id")
            if not item_id:
                continue
            if item_id not in latest:
                order.append(item_id)
            latest[item_id] = row
    return [latest[i] for i in order]


def _age_days(row: dict, now: dt.datetime) -> float | None:
    filed = parse_ts(row.get("filed_utc")) or parse_ts(row.get("assigned_utc"))
    if filed is None:
        return None
    return (now - filed).total_seconds() / 86400.0


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    values = sorted(values)
    mid = len(values) // 2
    if len(values) % 2:
        return values[mid]
    return (values[mid - 1] + values[mid]) / 2.0


def _pct(part: int, whole: int) -> str:
    return f"{100.0 * part / whole:.0f}%" if whole else "—"


def census(rows: list[dict], days: int = 14, now: dt.datetime | None = None) -> dict:
    now = now or dt.datetime.now(dt.timezone.utc)
    waiting = [r for r in rows if not r.get("state")]
    decided = [r for r in rows if r.get("state")]

    # 1. Stock, by the amigo who owes the decision.
    stock: dict[str, dict] = {}
    for row in waiting:
        who = row.get("assigned_to") or "(unnamed)"
        age = _age_days(row, now)
        entry = stock.setdefault(who, {"waiting": 0, "oldest_days": None, "ids": []})
        entry["waiting"] += 1
        entry["ids"].append(row["id"])
        if age is not None and (entry["oldest_days"] is None or age > entry["oldest_days"]):
            entry["oldest_days"] = age

    # 2. Flow over the window.
    start = (now - dt.timedelta(days=days)).date()
    filed_by_day: collections.Counter = collections.Counter()
    decided_by_day: collections.Counter = collections.Counter()
    for row in rows:
        filed = parse_ts(row.get("filed_utc")) or parse_ts(row.get("assigned_utc"))
        if filed and filed.date() >= start:
            filed_by_day[filed.date().isoformat()] += 1
        stamp = parse_ts(row.get("state_utc"))
        if stamp and stamp.date() >= start:
            decided_by_day[stamp.date().isoformat()] += 1

    # 3. Who decides, and how much of it is the delivery defect.
    by_reviewer: dict[str, collections.Counter] = {}
    postponed_delivery = 0
    postponed_total = 0
    for row in decided:
        who = row.get("reviewer") or "unrecorded"
        by_reviewer.setdefault(who, collections.Counter())[row["state"]] += 1
        if row.get("state") == "postponed":
            postponed_total += 1
            if DELIVERY_DEFECT.search(row.get("reason") or ""):
                postponed_delivery += 1

    # 4. Latency, machine closers kept apart from named reviewers.
    latency: dict[str, list[float]] = collections.defaultdict(list)
    for row in decided:
        filed = parse_ts(row.get("filed_utc")) or parse_ts(row.get("assigned_utc"))
        stamp = parse_ts(row.get("state_utc"))
        if not filed or not stamp:
            continue
        days_open = (stamp - filed).total_seconds() / 86400.0
        kind = "machine" if row.get("reviewer") in MACHINE_REVIEWERS else "amigo"
        latency[kind].append(days_open)

    def _stats(values: list[float]) -> dict:
        if not values:
            return {"n": 0, "median_days": None, "p90_days": None}
        values = sorted(values)
        return {
            "n": len(values),
            "median_days": round(_median(values), 2),
            "p90_days": round(values[int(0.9 * (len(values) - 1))], 2),
        }

    window_filed = sum(filed_by_day.values())
    window_decided = sum(decided_by_day.values())
    return {
        "as_of": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "window_days": days,
        "items": len(rows),
        "waiting": len(waiting),
        "decided": len(decided),
        "stock": {
            who: {
                "waiting": v["waiting"],
                "oldest_days": None if v["oldest_days"] is None else round(v["oldest_days"], 1),
            }
            for who, v in sorted(stock.items(), key=lambda kv: -kv[1]["waiting"])
        },
        "flow": {
            "filed": window_filed,
            "decided": window_decided,
            "net": window_filed - window_decided,
            "filed_by_day": dict(sorted(filed_by_day.items())),
            "decided_by_day": dict(sorted(decided_by_day.items())),
        },
        "verdicts_by_reviewer": {k: dict(v) for k, v in sorted(by_reviewer.items())},
        "postponed": {
            "total": postponed_total,
            "delivery_defect": postponed_delivery,
            "share": _pct(postponed_delivery, postponed_total),
        },
        "latency": {kind: _stats(vals) for kind, vals in sorted(latency.items())},
    }


def render(out: dict) -> str:
    lines: list[str] = []
    lines.append(
        f"Review-queue flow as of {out['as_of']} "
        f"({out['items']} items, {out['waiting']} waiting, {out['decided']} decided)\n"
    )

    lines.append("STOCK — waiting, by the amigo who owes the decision")
    if not out["stock"]:
        lines.append("  (nothing waiting)")
    for who, entry in out["stock"].items():
        oldest = "—" if entry["oldest_days"] is None else f"{entry['oldest_days']:.1f}d"
        lines.append(f"  {who:<12} {entry['waiting']:>4} waiting   oldest {oldest}")

    flow = out["flow"]
    lines.append("")
    lines.append(f"FLOW — last {out['window_days']} days")
    lines.append(f"  filed {flow['filed']}   decided {flow['decided']}   net {flow['net']:+d}")
    if flow["filed_by_day"] or flow["decided_by_day"]:
        days = sorted(set(flow["filed_by_day"]) | set(flow["decided_by_day"]))
        lines.append(f"  {'day':<12}{'filed':>6}{'decided':>9}")
        for day in days:
            lines.append(
                f"  {day:<12}{flow['filed_by_day'].get(day, 0):>6}"
                f"{flow['decided_by_day'].get(day, 0):>9}"
            )

    lines.append("")
    lines.append("WHO DECIDES")
    for who, counts in out["verdicts_by_reviewer"].items():
        parts = "  ".join(f"{state}={n}" for state, n in sorted(counts.items()))
        lines.append(f"  {who:<12} {parts}")

    post = out["postponed"]
    lines.append("")
    lines.append(
        f"POSTPONEMENTS THAT ARE THE DELIVERY DEFECT — {post['delivery_defect']} of "
        f"{post['total']} ({post['share']}): the reason names a path that never reached main"
    )

    lines.append("")
    lines.append("LATENCY — filed to decided, in days")
    for kind, stats in out["latency"].items():
        if not stats["n"]:
            lines.append(f"  {kind:<8} n=0")
            continue
        lines.append(
            f"  {kind:<8} n={stats['n']:<4} median {stats['median_days']:.1f}d"
            f"   p90 {stats['p90_days']:.1f}d"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review-queue flow census (read-only).")
    parser.add_argument("--days", type=int, default=14, help="flow window in days (default 14)")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--ledger", type=Path, default=LEDGER, help="path to items.jsonl")
    args = parser.parse_args(argv)

    out = census(load_rows(args.ledger), days=args.days)
    if args.json:
        json.dump(out, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        print(render(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
