#!/usr/bin/env python3
# Owner: Dmitri
"""Recover item-ledger rows a failed landing threw away, from the run's own patch.

Why this exists (2026-10-14). `channels/items.jsonl` is a log, not a table: `load()` reads
it as "later lines override earlier ones, keyed by `id`", and every state change is a new
line. The lander (`land_runs.py`) does not merge — it runs `git apply <the run's patch>` on
the live checkout, and `git apply` is **atomic over the whole patch**: if any one hunk fails,
nothing is applied.

Measured on run `20261013T170314Z-0838fbd7` (the run that named this defect): its patch
touches four paths and three of them fail —

    channels/items.jsonl     failed at :1170
    channels/reject-queue.md failed at :63
    to-do-lists/dmitri.md    failed at :9

— so the 137 ledger rows in the fourth hunk of the *same* patch were discarded with them,
and `result.json` reads `"land": "conflict"`. The 136 review outcomes that run had just
written came straight back onto its queue, which is the review-drain loop.

**The mechanism, measured, and it is not what the to-do item assumed.** The ledger hunk is
`@@ -1170,3 +1170,140 @@` — three leading context lines and 137 additions, with no trailing
context, because the additions *were* the end of the file when the run made them. That shape
applies only while the context lines are still the end of the file. Once any later wake
appended (or the ledger re-derived) lines after them, both `git apply` and GNU `patch` refuse
it — verified directly: the same hunk applies cleanly to the 1172-line preimage and fails
against the grown file, even though its three context lines are byte-identical and still
present at line 1170. The patch's `index 8c207170..b124eed5` names a preimage blob whose
hash is exactly the reconstructible preimage, confirming the file is preimage + appends.

Two consequences worth keeping:

  * A **union merge driver cannot help.** The lander never merges, so `.gitattributes
    merge=union` would be dead text; and (b) the lander's atom cannot be fixed by a merge
    attribute anyway, because the failure happens inside `git apply`.
  * Rows a run *derived* from run records heal on their own (`--collect`/`--reconcile`
    recompute them). Rows set by a **review** — `--review <id> --state rejected|postponed
    --reason ...` — do not: `--collect` skips an `id` it already knows, so a lost review
    outcome is lost for good and the item silently falls back to a derived state. That is
    the loss this tool exists to undo.

What it does, and what it deliberately does not. It reads one run's `changes.patch`, takes
only the added lines of the `channels/items.jsonl` hunk, and appends the ones the live ledger
lacks — or the ones that are *newer* than the ledger's line for the same `id`. It never
removes a line and never overwrites: because the ledger is later-wins, appending a newer row
for an existing id is the ledger's own way of changing state, and appending an older one
would be a regression, so older rows are skipped and named.

It is a remedy, not the prevention. Prevention is a lander that applies each path
independently (or that treats this one log as union-appendable), and that lives in a bot file
a wake may not edit — recorded in `channels/reports/2026-10-14-dmitri-lander-ledger-conflict.md`.

Usage:
  python3 scripts/ledger_row_recovery.py <run-dir>              # report only
  python3 scripts/ledger_row_recovery.py <run-dir> --write      # append what is missing
  python3 scripts/ledger_row_recovery.py --patch changes.patch --ledger channels/items.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEDGER = REPO / "channels" / "items.jsonl"
TARGET = "channels/items.jsonl"


def added_rows(patch_text: str, target: str = TARGET) -> tuple[list[dict], int]:
    """The rows a patch adds to `target`, in patch order, and a count of unparsable ones.

    Only `+` lines inside the `target` file's hunks are read. `+++` is the file header, not
    an addition, and the `diff --git` line that opens each file section is what scopes the
    read — a patch for a different path must never contribute rows here.
    """
    rows: list[dict] = []
    bad = 0
    in_file = False
    for line in patch_text.splitlines():
        if line.startswith("diff --git "):
            in_file = line.split()[2][2:] == target or line.split()[3][2:] == target
            continue
        if not in_file or not line.startswith("+"):
            continue
        if line.startswith("+++"):
            continue
        try:
            rec = json.loads(line[1:])
        except ValueError:
            bad += 1
            continue
        if isinstance(rec, dict) and rec.get("id"):
            rows.append(rec)
        else:
            bad += 1
    return rows, bad


def load_rows(path: Path) -> dict[str, dict]:
    """The live ledger, later line wins, keyed by `id` — the same rule `item_ledger.load` uses."""
    out: dict[str, dict] = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if isinstance(rec, dict) and rec.get("id"):
            out[rec["id"]] = rec
    return out


def _stamp(rec: dict) -> str:
    """How new a row is. `state_utc` is written by every state change; `filed_utc` is the fallback."""
    return rec.get("state_utc") or rec.get("filed_utc") or ""


def plan(rows: list[dict], ledger: dict[str, dict]) -> tuple[list[dict], list[str], list[str]]:
    """Split the patch's rows into (to_append, already_current, staler_than_ledger).

    Within the patch the last row for an `id` wins, matching `load`. A row is appended when
    the ledger has no line for its `id`, or has an older one; it is skipped, and named, when
    the ledger's line is newer — appending it would move the item backwards.
    """
    effective: dict[str, dict] = {}
    for rec in rows:
        effective[rec["id"]] = rec
    append: list[dict] = []
    current: list[str] = []
    staler: list[str] = []
    for rid, rec in effective.items():
        have = ledger.get(rid)
        if have is None:
            append.append(rec)
        elif _stamp(rec) > _stamp(have):
            append.append(rec)
        else:
            current.append(rid)
            if _stamp(rec) < _stamp(have):
                staler.append(rid)
    return append, current, staler


def recover(run_dir: Path | None = None, patch: Path | None = None,
            ledger_path: Path = LEDGER, write: bool = False) -> dict:
    if patch is None:
        if run_dir is None:
            raise ValueError("give a run directory or --patch")
        patch = Path(run_dir) / "changes.patch"
    patch_text = patch.read_text(encoding="utf-8", errors="replace")
    rows, bad = added_rows(patch_text)
    ledger = load_rows(ledger_path)
    append, current, staler = plan(rows, ledger)
    if write and append:
        with ledger_path.open("a", encoding="utf-8") as fh:
            for rec in append:
                fh.write(json.dumps(rec, sort_keys=True) + "\n")
    return {"patch": str(patch), "rows_in_patch": len(rows), "unparsable": bad,
            "recovered": [r["id"] for r in append], "already_current": len(current),
            "staler_than_ledger": staler, "written": bool(write and append)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("run_dir", nargs="?", help="a tick-state run directory holding changes.patch")
    ap.add_argument("--patch", help="read this patch instead of <run-dir>/changes.patch")
    ap.add_argument("--ledger", default=str(LEDGER), help="the ledger to recover into")
    ap.add_argument("--write", action="store_true",
                    help="append the missing rows (without this, report only)")
    args = ap.parse_args(argv)
    if not args.run_dir and not args.patch:
        ap.error("give a run directory or --patch")
    res = recover(Path(args.run_dir) if args.run_dir else None,
                  Path(args.patch) if args.patch else None,
                  Path(args.ledger), write=args.write)
    print(f"patch: {res['patch']}")
    print(f"rows added by the patch: {res['rows_in_patch']}"
          + (f" ({res['unparsable']} unparsable, skipped)" if res["unparsable"] else ""))
    print(f"missing from the ledger (recoverable): {len(res['recovered'])}")
    for rid in res["recovered"]:
        print(f"  + {rid}")
    print(f"already current in the ledger: {res['already_current']}")
    if res["staler_than_ledger"]:
        print(f"older than the ledger's own line, left alone: {len(res['staler_than_ledger'])}")
        for rid in res["staler_than_ledger"]:
            print(f"  ~ {rid}")
    if res["recovered"] and not res["written"]:
        print("dry run — pass --write to append the missing rows")
    elif res["written"]:
        print(f"wrote {len(res['recovered'])} row(s) to the ledger")
    return 0


if __name__ == "__main__":
    sys.exit(main())
