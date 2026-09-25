#!/usr/bin/env python3
"""dedupe_tasks.py — report or collapse repeated entries in channels/tasks.md.

The ledger is written by `file_tasks` in the Telegram bot, which appends on every turn that
mentions a topic and never checks whether the line is already there. Result: one request
(Telegram image intake) filed nine times, another four times. This script is the checker and
the cleaner for that; `channels/task_ledger.py` holds the identity rule and
`tests/test_task_ledger.py` pins it.

Two bands, and only the upper one is applied:

  * **same item** — equal normal forms, a Jaccard score at or above `--threshold`, or a
    shorter filing wholly contained in a longer one. `--apply` collapses these: longest text
    kept, first position kept, and **checked only if every copy was checked**, so a merge can
    never make unfinished work look finished.
  * **near miss** (score at or above `--floor`) — *reported, never merged*. Two entries can
    read alike and be two real tasks; a similarity number is not entitled to decide that. The
    live example is the rover pair in the ledger, which scores 0.31.

Usage:
  python3 scripts/dedupe_tasks.py                 # report (exit 1 if any same-item pair)
  python3 scripts/dedupe_tasks.py --apply         # collapse the same-item pairs
  python3 scripts/dedupe_tasks.py --floor 0 --json   # every scored pair, machine-readable
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from channels import task_ledger as tl  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Report or collapse duplicate ledger entries.")
    ap.add_argument("path", nargs="?", default=str(REPO / tl.LEDGER_REL))
    ap.add_argument("--threshold", type=float, default=tl.NEAR_DUPLICATE,
                    help="score at or above which two entries are the same item (default %(default)s)")
    ap.add_argument("--floor", type=float, default=tl.NEAR_MISS_FLOOR,
                    help="lowest score to report at all (default %(default)s)")
    ap.add_argument("--apply", action="store_true",
                    help="collapse duplicates in place (near misses are never applied)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    if args.apply:
        n = tl.apply_file(args.path, threshold=args.threshold)
        print(f"merged {n} duplicate entr{'y' if n == 1 else 'ies'} in {args.path}")
        return 0

    report = tl.check_file(args.path, threshold=args.threshold, floor=args.floor)
    if args.json:
        print(json.dumps(report, indent=2))
        return 1 if report.get("same") else 0
    if report.get("error"):
        print(f"{report['path']}: {report['error']}")
        return 2
    print(f"{report['path']}: {report['items']} entr(y|ies) over {report['lines']} lines")
    for label, rows in (("the same item", report["same"]),
                        ("near miss (not merged)", report["near"])):
        if not rows:
            continue
        print(f"\n{len(rows)} {label}:")
        for r in rows:
            print(f"  jaccard {r['score']:.2f}  containment {r['containment']:.2f}"
                  f"  line {r['kept_line']} vs {r['dup_line']}")
            print(f"        keep: {r['kept']}")
            print(f"        dup : {r['dup']}")
    if not report["same"] and not report["near"]:
        print("no repeated entries")
    return 1 if report["same"] else 0


if __name__ == "__main__":
    sys.exit(main())
