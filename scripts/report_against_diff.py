#!/usr/bin/env python3
"""Does a run's own report say anything about what the run did?

Why this exists (2026-10-27, Desi). Reading six never-read items in one wake, two of them
(`20261026T170624Z-73a75cc5` and `20261027T074357Z-17bb8688`) turned out to have the same shape: their
`report.txt` was a single intent line — "Starting: checking review queue..." / "Started: about to check my
review queue..." — while the run itself had landed real work. The first one added a 67-line review to main;
the second wrote a 3,500-word report. The record of the run said nothing, and the work was fine.

That is not a delivery failure and it is not dishonesty. It is the action cap: the instruction tells a wake
to write its intent as its first line and replace it as it goes, and 228 of 258 runs measured on 2026-10-27
never get back to the file (dmitri's `scripts/wake_reconnaissance_census.py` counts the actions spent before
the first write). Nobody had counted the other half — how often the record is silent while the diff is not.

What this measures, in one sentence each, with no thresholds to tune:

* `patch_bytes`  — the size of the run's `changes.patch`, i.e. whether it wrote anything at all;
* `report`       — one of `missing` (no file), `silent` (the file exists but has at most one non-empty
  line, so it cannot contain an account of anything), `account` (two or more lines and no `LAND:` line) or
  `landed` (two or more lines including a `LAND:` line).

The interesting cell is `silent` with `patch_bytes > 0`: the work exists, the record of it does not. A
reader — the human, a reviewer, a later wake — reading only the report sees nothing, which is why the same
item is often re-derived from scratch.

What this deliberately does not do: it does not judge whether the work was any good, and it does not read
`changes.patch`. It answers one factual question about a run's bookkeeping.

Usage:
    python3 scripts/report_against_diff.py                 # summary over ~/LLM/*-bot
    python3 scripts/report_against_diff.py --root /tmp/x
    python3 scripts/report_against_diff.py --show silent   # list the silent ones, newest first
    python3 scripts/report_against_diff.py --json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

RUNS_GLOB = "*-bot/tick-state/runs"


def nonempty_lines(text: str) -> list[str]:
    """Every line with content, whitespace-stripped. Blank lines are not a record of anything."""
    return [line.strip() for line in text.splitlines() if line.strip()]


def classify_report(report: pathlib.Path) -> str:
    """`missing` | `silent` | `account` | `landed` — see the module docstring."""
    if not report.exists():
        return "missing"
    try:
        lines = nonempty_lines(report.read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return "missing"
    if len(lines) <= 1:
        # The first line is the intent, by instruction. One line cannot also be the account.
        return "silent"
    if any(line.startswith("LAND:") for line in lines):
        return "landed"
    return "account"


def patch_bytes(run: pathlib.Path) -> int:
    patch = run / "changes.patch"
    try:
        return patch.stat().st_size
    except OSError:
        return 0


def census(root: pathlib.Path) -> list[dict]:
    """One row per run directory under every `*-bot/tick-state/runs` below `root`."""
    rows: list[dict] = []
    for base in sorted(root.glob(RUNS_GLOB)):
        if not base.is_dir():
            continue
        bot = base.parent.parent.name
        for run in sorted(base.iterdir()):
            if not run.is_dir():
                continue
            report = classify_report(run / "report.txt")
            first = ""
            if report != "missing":
                lines = nonempty_lines((run / "report.txt").read_text(encoding="utf-8", errors="replace"))
                first = lines[0] if lines else ""
            rows.append({
                "id": run.name,
                "bot": bot,
                "patch_bytes": patch_bytes(run),
                "report": report,
                "first_line": first,
            })
    return rows


def summarise(rows: list[dict]) -> dict:
    total = len(rows)
    worked = [r for r in rows if r["patch_bytes"] > 0]
    by_report = {"missing": 0, "silent": 0, "account": 0, "landed": 0}
    for row in rows:
        by_report[row["report"]] = by_report.get(row["report"], 0) + 1
    silent_with_work = [r for r in worked if r["report"] == "silent"]
    return {
        "runs": total,
        "runs_with_a_patch": len(worked),
        "by_report": by_report,
        "silent_with_work": len(silent_with_work),
        "silent_with_work_share_of_patched": (
            round(100.0 * len(silent_with_work) / len(worked), 1) if worked else 0.0
        ),
        "landed_share_of_patched": (
            round(100.0 * sum(1 for r in worked if r["report"] == "landed") / len(worked), 1)
            if worked else 0.0
        ),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(pathlib.Path.home() / "LLM"),
                    help="directory holding the bots' checkouts (default: ~/LLM)")
    ap.add_argument("--show", choices=["missing", "silent", "account", "landed"],
                    help="list the runs in this class instead of only counting them")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    root = pathlib.Path(args.root).expanduser()
    if not root.is_dir():
        print(f"report_against_diff: no such directory: {root}", file=sys.stderr)
        return 2

    rows = census(root)
    stats = summarise(rows)

    if args.show:
        shown = [r for r in rows if r["report"] == args.show]
        for row in shown:
            print(f"{row['id']}  patch={row['patch_bytes']:>7}  {row['bot']}  {row['first_line'][:90]}")
        print(f"\n{len(shown)} run(s) classified {args.show!r}")
        return 0

    if args.json:
        print(json.dumps({"summary": stats, "rows": rows}, indent=1))
        return 0

    print(f"runs read: {stats['runs']}")
    print(f"  runs that changed the checkout (changes.patch > 0)  {stats['runs_with_a_patch']}")
    for kind in ("landed", "account", "silent", "missing"):
        print(f"  report {kind:<8}  {stats['by_report'].get(kind, 0)}")
    print()
    print(f"silent record, real work   {stats['silent_with_work']} of {stats['runs_with_a_patch']} "
          f"patched runs ({stats['silent_with_work_share_of_patched']}%)")
    print(f"LAND line present          {stats['landed_share_of_patched']}% of patched runs")
    print()
    print("silent = the report has at most one non-empty line, so it cannot say what the run did.")
    print("`--show silent` lists them; `--show missing` lists runs with no report.txt at all.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
