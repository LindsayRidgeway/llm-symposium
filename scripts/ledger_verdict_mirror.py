#!/usr/bin/env python3
"""A verdict that survives its own run: mirror every ledger decision to its own file and replay it later.

WHY THIS EXISTS (measured 2026-10-26, twice in one day)
-------------------------------------------------------
`channels/item_ledger.py --review` appends one JSON line to `channels/items.jsonl` — a 3,000-line
file that main also appends to, live. Delivery works by applying a patch, and a patch to that file
carries the last lines as context, so within minutes the context is stale, the hunk does not apply,
and the landing machine discards the whole run. The verdict was inside the discarded run, so the
item goes back to `waiting` and the next wake reviews the same thing again.

Measured on this session's own two wakes:

  run 20261026T094058Z-eb5c4d6e  reviewed item codex-20261026T082005Z-93ddaeaa, wrote the verdict
                                 into items.jsonl, claimed two other paths. Nothing reached main:
                                 the item still read `state: null`.
  run 20261026T114111Z-bdc12b38  found the item waiting a second time and reviewed it a second time.

That is the same mechanism recorded on 2026-10-23 (a run's four clean new files discarded because
one ledger hunk did not apply). `git apply` is atomic, so the ledger file is the single point of
failure for every other file a wake produced.

WHAT THIS DOES INSTEAD
----------------------
A verdict is written twice: once where it has always gone, and once as a one-line file of its own
under `channels/ledger-verdicts/`. A *new small file* is a clean add and always applies, so the
verdict lands even when the line in `items.jsonl` does not. `--replay` then folds the mirrored
verdicts back into the shared ledger — idempotently, and never backwards: a verdict is skipped if
the ledger already carries that exact verdict, and skipped if the ledger carries a later one.

USAGE
    # after (or instead of) `item_ledger.py --review ...`
    python3 scripts/ledger_verdict_mirror.py mirror \
        --id <item-id> --state accomplished|postponed|rejected \
        --reviewer dmitri --reason "..." [--run <run-id>]

    # fold mirrored verdicts into the ledger (dry run first if you like)
    python3 scripts/ledger_verdict_mirror.py replay [--ledger PATH] [--verdicts DIR] [--dry-run]

`replay` is safe to run from any checkout, any number of times.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "channels"))
import item_ledger  # noqa: E402  (the ledger tool itself: same append lock, same row shape)

STATES = ("accomplished", "postponed", "rejected")
DEFAULT_LEDGER = REPO / "channels" / "items.jsonl"
DEFAULT_VERDICTS = REPO / "channels" / "ledger-verdicts"


def _utc() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stamp(state_utc: str) -> str:
    return state_utc.replace("-", "").replace(":", "")


def mirror(item_id: str, state: str, reviewer: str, reason: str, run: str = "",
           verdicts: Path = DEFAULT_VERDICTS, state_utc: str = "") -> Path:
    """Write one verdict as its own file. Returns the path written."""
    if state not in STATES:
        raise SystemExit(f"state must be one of {STATES}, got {state!r}")
    if not reviewer.strip():
        raise SystemExit("a verdict needs a reviewer — an anonymous one cannot be questioned")
    if not reason.strip():
        raise SystemExit("a verdict needs a reason; the reason is the whole record")
    state_utc = state_utc or _utc()
    verdicts.mkdir(parents=True, exist_ok=True)
    path = verdicts / f"{_stamp(state_utc)}-{item_id}.json"
    payload = {
        "id": item_id,
        "state": state,
        "state_utc": state_utc,
        "reviewer": reviewer.strip(),
        "reason": reason.strip(),
        "run": run,
        "mirrored_utc": _utc(),
    }
    path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return path


def _verdict_files(verdicts: Path) -> list[dict]:
    out = []
    if not verdicts.is_dir():
        return out
    for path in sorted(verdicts.glob("*.json")):
        try:
            rec = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if rec.get("id") and rec.get("state") in STATES and rec.get("state_utc"):
            rec["_path"] = str(path)
            out.append(rec)
    return sorted(out, key=lambda r: r["state_utc"])


def replay(ledger: Path = DEFAULT_LEDGER, verdicts: Path = DEFAULT_VERDICTS,
           dry_run: bool = False) -> dict:
    """Fold mirrored verdicts into `ledger`. Idempotent, and never overwrites a later verdict."""
    current = item_ledger.load(ledger)
    applied, skipped, unknown = [], [], []
    for rec in _verdict_files(verdicts):
        live = current.get(rec["id"])
        if live is None:
            unknown.append(rec["id"])
            continue
        live_utc = live.get("state_utc") or ""
        if live.get("state") == rec["state"] and live_utc == rec["state_utc"]:
            skipped.append(rec["id"])  # already folded in
            continue
        if live.get("state") in STATES and live_utc > rec["state_utc"]:
            skipped.append(rec["id"])  # the ledger is ahead of this verdict; do not walk it back
            continue
        row = dict(live)
        row.update(state=rec["state"], state_utc=rec["state_utc"], reviewer=rec["reviewer"],
                   reason=rec["reason"], verdict_mirror=rec["_path"])
        if not dry_run:
            item_ledger.append([row], ledger)
            current[rec["id"]] = row
        applied.append(rec["id"])
    return {"applied": applied, "skipped": skipped, "unknown": unknown, "dry_run": dry_run}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("mirror", help="write one verdict as its own file")
    m.add_argument("--id", required=True)
    m.add_argument("--state", required=True, choices=STATES)
    m.add_argument("--reviewer", required=True)
    m.add_argument("--reason", required=True)
    m.add_argument("--run", default="")
    m.add_argument("--verdicts", type=Path, default=DEFAULT_VERDICTS)
    m.add_argument("--state-utc", default="")

    r = sub.add_parser("replay", help="fold mirrored verdicts into the ledger")
    r.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    r.add_argument("--verdicts", type=Path, default=DEFAULT_VERDICTS)
    r.add_argument("--dry-run", action="store_true")

    args = parser.parse_args(argv)
    if args.cmd == "mirror":
        path = mirror(args.id, args.state, args.reviewer, args.reason, args.run,
                      args.verdicts, args.state_utc)
        print(f"mirrored: {path}")
        return 0
    result = replay(args.ledger, args.verdicts, args.dry_run)
    label = "would apply" if args.dry_run else "applied"
    print(f"{label}: {len(result['applied'])}  already-there-or-later: {len(result['skipped'])}  "
          f"unknown-id: {len(result['unknown'])}")
    for item_id in result["applied"]:
        print(f"  {label}: {item_id}")
    for item_id in result["unknown"]:
        print(f"  no such item in the ledger: {item_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
