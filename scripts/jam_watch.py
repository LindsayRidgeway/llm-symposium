#!/usr/bin/env python3
"""The de-jamming procedure's mechanical half, run on a clock instead of a founder turn (Desi, 2026-11-26).

The founder's procedure (2026-11-19): examine what the next wake would do, run the wake, examine again,
fix the clockwork if the head has not moved. Run by hand it found a jam within the hour and the
procedure's own defect the second time. Run by hand it also cost him a conversation every time, and
the repair it produced was never the mechanical part — that part is an invariant, and the founder's
own rule for invariants is already written down: compute them on the 07:45 job rather than asking a
model to notice.

What this file adds is the memory the check was missing. `clockwork_jam.py` compares two snapshots a
human has to hold; a scheduled run has only the one it can see, so it reads the snapshots the previous
runs left in `channels/jam-watch.jsonl`. Three triggers, each of which has fired at least once:

  1. **unmoved** — the same seat has had the same head on the last `--need` runs (`need=2` by default).
     That is the founder's rule, "the head hasn't moved across two wakes", evaluated without a wake.
  2. **dropped** — the lander wrote a `land_missing.json` in the last few days: a landing that did not
     carry a path it claimed. Added 2026-11-26, the day a landing dropped a file deletion and printed
     `landed`.
  3. **empty-queue** — a seat's value queue has no open item, which `value_queue.py` already calls a
     defect rather than a rest. A seat with nothing to do is a jam nobody notices, because the head it
     reports looks calm.

It records and does not message. The founder asked for the Review Check messages to stop, and a check
that reports every morning is the ritual he objected to; this one is silent unless a trigger fires, and
even then it writes rather than telephones — the record is what wakes read.

    python3 scripts/jam_watch.py                 # measure, append today's snapshot, print the verdict
    python3 scripts/jam_watch.py --dry-run       # measure and print, record nothing
    python3 scripts/jam_watch.py --need 3        # how many consecutive unchanged checks count as stuck
    python3 scripts/jam_watch.py --json          # the verdicts, machine-readable

Exit 0 when nothing fired, 1 when something did (so a scheduled wrapper can tell), 2 when it could not
measure — a check that cannot run must not report health.
"""
from __future__ import annotations

import argparse
import datetime
import importlib.util
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RECORD = REPO / "channels" / "jam-watch.jsonl"
SEATS = ("claude", "desi", "dmitri", "gemini", "gwen", "tarik")


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)                    # type: ignore[union-attr]
    return mod


def key(head: dict | None):
    """What "the same head" means: the first item, not the date or the reason it is first."""
    if not head:
        return None
    return (head.get("block"), head.get("id"))


def streak(history: list, seat: str, k, need: int) -> int:
    """How many consecutive recorded runs ended on this same head. Newest record last."""
    n = 0
    for row in reversed(history):
        if row.get("seat") != seat:
            continue
        if key(row.get("head")) != k:
            break
        n += 1
        if n >= need:
            break
    return n


def verdicts(heads: dict, history: list, need: int = 2, dropped=(), empty=()) -> list:
    """The triggers that fired, as plain dicts. Pure: every input is an argument."""
    out = []
    for seat in sorted(heads):
        k = key(heads[seat])
        if k is None:
            out.append({"trigger": "unmoved", "seat": seat,
                        "because": "no head at all: the prompt it read awaited nothing and nothing below it"})
            continue
        n = streak(history, seat, k, need)
        if n >= need:
            out.append({"trigger": "unmoved", "seat": seat, "head": list(k), "checks": n,
                        "because": "the same item has been first for %d consecutive checks" % (n + 1)})
    for row in dropped:
        out.append({"trigger": "dropped", "seat": row.get("seat"), "path": row.get("path"),
                    "because": "a landing did not carry a path it claimed"})
    for seat in sorted(empty):
        out.append({"trigger": "empty-queue", "seat": seat,
                    "because": "the value queue has no open item, which is a defect, not a rest"})
    return out


def heads_now(repo: Path = REPO, today: datetime.date | None = None) -> dict:
    cj = _load("cj_jam_watch", repo / "scripts" / "clockwork_jam.py")
    out = {}
    for seat in SEATS:
        try:
            out[seat] = cj.head(seat, repo=repo, today=today)
        except Exception as exc:                     # noqa: BLE001 — a seat that will not measure is
            out[seat] = None                         # a seat with no head, and that is a finding
            print("jam_watch: could not measure %s: %s: %s" % (seat, type(exc).__name__, exc))
    return out


def empty_value_queues(repo: Path = REPO) -> list:
    """Seats whose value queue has no open item. Read from the queue file, not from the script."""
    try:
        rows = json.loads((repo / "channels" / "value-queue.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    items = rows.get("items") if isinstance(rows, dict) else rows
    if not isinstance(items, list):
        return []
    open_rows = [r for r in items if isinstance(r, dict) and not r.get("done")]
    if open_rows:
        return []
    return ["all"] if items else []


def dropped_recent(root: Path, days: int = 2) -> list:
    """`land_missing.json` files the lander left in the last `days`, across the seats' run directories."""
    out = []
    cutoff = time.time() - days * 86400
    for bot in sorted(Path(root).glob("*-bot/tick-state/runs")):
        seat = bot.parts[-3].split("-bot")[0]
        for p in sorted(bot.glob("*/land_missing.json")):
            try:
                if p.stat().st_mtime < cutoff:
                    continue
                paths = json.loads(p.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            for line in paths if isinstance(paths, list) else [paths]:
                out.append({"seat": seat, "run": p.parent.name, "path": str(line)[:120]})
    return out


def history(path: Path = RECORD) -> list:
    rows = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return rows
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except ValueError:
            continue
    return rows


def run(repo: Path = REPO, need: int = 2, record: bool = True, root: Path | None = None,
        today: datetime.date | None = None) -> list:
    heads = heads_now(repo, today)
    hist = history(repo / "channels" / "jam-watch.jsonl")
    fired = verdicts(heads, hist, need=need,
                     dropped=dropped_recent(root or repo.parent),
                     empty=empty_value_queues(repo))
    if record:
        stamp = (today or datetime.date.today()).isoformat()
        with (repo / "channels" / "jam-watch.jsonl").open("a", encoding="utf-8") as fh:
            for seat in sorted(heads):
                fh.write(json.dumps({"date": stamp, "seat": seat, "head": heads[seat] or {},
                                     "fired": [t["trigger"] for t in fired if t.get("seat") == seat]},
                                    sort_keys=True) + "\n")
    return fired


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="measure and print; record nothing")
    ap.add_argument("--need", type=int, default=2, help="consecutive unchanged checks that count as stuck")
    ap.add_argument("--json", action="store_true", help="machine-readable")
    ap.add_argument("--repo", type=Path, default=REPO)
    args = ap.parse_args(argv)
    try:
        fired = run(repo=args.repo, need=args.need, record=not args.dry_run)
    except Exception as exc:                         # noqa: BLE001 — exit 2, never a silent 0
        print("jam_watch: could not measure: %s: %s" % (type(exc).__name__, exc))
        return 2
    if args.json:
        print(json.dumps(fired, indent=2, sort_keys=True))
    elif not fired:
        print("jam_watch: nothing fired (%d seat(s) measured)" % len(SEATS))
    else:
        for t in fired:
            print("jam_watch: %-11s %-7s %s" % (t["trigger"], t.get("seat") or "—", t["because"]))
    return 1 if fired else 0


if __name__ == "__main__":
    raise SystemExit(main())
