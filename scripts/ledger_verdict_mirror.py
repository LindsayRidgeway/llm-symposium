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
import re
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


_COMPACT = re.compile(r"^(\d{4})(\d{2})(\d{2})[T ](\d{2})(\d{2})(\d{2})Z$")


def _aware(state_utc: str) -> str:
    """The verdict time as an ISO-8601 aware UTC stamp, or SystemExit naming what was unreadable.

    Two spellings reach this function and both are the repository's own house style. `mirror`
    writes `2026-11-08T06:53:58Z`. A verdict written *by hand* — which is how a run records one
    when it is out of turns to call the subcommand — writes the compact run-stamp
    `20261108T065358Z`, because that is the shape every run id and every `_stamp()` filename in
    this repository has. The ledger accepts only the first: `item_ledger.verdict_stamp` raises
    `ValueError: state_utc must be an aware ISO timestamp` on the second.

    Measured 2026-11-08 (run 20261108T085157Z-acb8d5fb): 3 of the 70 mirror files carried the
    compact spelling — the three verdicts written by hand the previous wake. `replay` therefore
    died before applying any of them, and those items stayed in the reading queue looking as
    though nobody had read them: the exact loop the mirror exists to break, reintroduced by a
    timestamp format. Both spellings are accepted here and normalised to the ISO one.
    """
    text = (state_utc or "").strip()
    compact = _COMPACT.match(text)
    if compact:
        year, month, day, hour, minute, second = compact.groups()
        return f"{year}-{month}-{day}T{hour}:{minute}:{second}Z"
    try:
        stamp = item_ledger.parse_iso_aware(text)
    except ValueError:
        raise SystemExit(
            f"state_utc {state_utc!r} is not a time I can read; give me "
            "2026-11-08T06:53:58Z or the compact 20261108T065358Z") from None
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise SystemExit(
            f"state_utc {state_utc!r} carries no timezone; a verdict time must say which clock "
            "it was read on")
    return stamp.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def mirror(item_id: str, state: str, reviewer: str, reason: str, run: str = "",
           verdicts: Path = DEFAULT_VERDICTS, state_utc: str = "") -> Path:
    """Write one verdict as its own file. Returns the path written."""
    if state not in STATES:
        raise SystemExit(f"state must be one of {STATES}, got {state!r}")
    if not reviewer.strip():
        raise SystemExit("a verdict needs a reviewer — an anonymous one cannot be questioned")
    if not reason.strip():
        raise SystemExit("a verdict needs a reason; the reason is the whole record")
    state_utc = _aware(state_utc or _utc())
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


def _verdict_files(verdicts: Path) -> tuple[list[dict], list[str]]:
    """Every readable mirror file, oldest first, plus one line per file that could not be read.

    A file that cannot be read is *reported*, not skipped in silence and not allowed to abort the
    batch. Measured 2026-11-08: one mirror with the compact `state_utc` spelling made `replay` die
    inside `item_ledger.append`, which folds in nothing at all — every other verdict in the
    directory is held hostage by the one bad file, and the run that wrote it believes its work is
    recorded because the file is there. Naming the file and carrying on is the only behaviour that
    both keeps the batch moving and leaves the defect findable.
    """
    out: list[dict] = []
    unreadable: list[str] = []
    if not verdicts.is_dir():
        return out, unreadable
    for path in sorted(verdicts.glob("*.json")):
        try:
            rec = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            unreadable.append(f"{path.name}: not JSON ({exc})")
            continue
        if not rec.get("id") or rec.get("state") not in STATES or not rec.get("state_utc"):
            unreadable.append(f"{path.name}: not a verdict (needs id, state, state_utc)")
            continue
        try:
            rec["state_utc"] = _aware(rec["state_utc"])
        except SystemExit as exc:  # `_aware` explains itself; keep the file name with it
            unreadable.append(f"{path.name}: {exc}")
            continue
        rec["_path"] = str(path)
        out.append(rec)
    return sorted(out, key=lambda r: r["state_utc"]), unreadable



def replay(ledger: Path = DEFAULT_LEDGER, verdicts: Path = DEFAULT_VERDICTS,
           dry_run: bool = False) -> dict:
    """Fold mirrored verdicts into `ledger`. Idempotent, and never overwrites a later verdict."""
    current = item_ledger.load(ledger)
    records, unreadable = _verdict_files(verdicts)
    applied, skipped, unknown = [], [], []
    for rec in records:
        live = current.get(rec["id"])
        if live is None:
            unknown.append(rec["id"])
            continue
        live_utc = ""
        if live.get("state") in STATES and live.get("state_utc"):
            try:  # a ledger row written by hand may carry the compact spelling too
                live_utc = _aware(live["state_utc"])
            except SystemExit:
                live_utc = ""
        if live.get("state") == rec["state"] and live_utc == rec["state_utc"]:
            skipped.append(rec["id"])  # already folded in
            continue
        if live.get("state") in STATES and live_utc and live_utc > rec["state_utc"]:
            skipped.append(rec["id"])  # the ledger is ahead of this verdict; do not walk it back
            continue
        row = dict(live)
        row.update(state=rec["state"], state_utc=rec["state_utc"], reviewer=rec["reviewer"],
                   reason=rec["reason"], verdict_mirror=rec["_path"])
        if not dry_run:
            item_ledger.append([row], ledger)
            current[rec["id"]] = row
        applied.append(rec["id"])
    return {"applied": applied, "skipped": skipped, "unknown": unknown,
            "unreadable": unreadable, "dry_run": dry_run}


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
          f"unknown-id: {len(result['unknown'])}  unreadable: {len(result['unreadable'])}")
    for item_id in result["applied"]:
        print(f"  {label}: {item_id}")
    for item_id in result["unknown"]:
        print(f"  no such item in the ledger: {item_id}")
    for problem in result["unreadable"]:
        print(f"  could not read: {problem}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
