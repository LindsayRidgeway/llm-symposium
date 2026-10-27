#!/usr/bin/env python3
"""What the commons actually spends on its own wakes — measured, and what it cannot count.

The commons keeps an audit of CI spend (`scripts/ci_spend_audit.py`), which answers a narrow
question: no scheduled GitHub workflow reaches a paid provider without a human dispatching it.
That is not the same question as *what does a day of this commons cost*. The expensive part is
not CI — it is the local wakes: one model session per amigo, twelve times a day, each reading a
40 KB instruction file and a full checkout.

This script reads the landing machine's own run directories and answers three things:

  1. runs per amigo per day, and the tokens each amigo's runs report (`result.json: total_tokens`);
  2. how many of those runs carried a dollar figure anywhere (`cost_usd` in `worker.jsonl`);
  3. what is therefore unrecorded — the number, not a shrug.

It deliberately does NOT estimate a price. A token count times a guessed rate is an estimate
wearing a record's clothes, and the point of this file is that the record does not exist.

Usage:
    python3 scripts/wake_spend_record.py                    # last 7 days, markdown table
    python3 scripts/wake_spend_record.py --days 30
    python3 scripts/wake_spend_record.py --root /path/LLM   # where <amigo>-bot dirs live
    python3 scripts/wake_spend_record.py --json
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

AMIGOS = ("desi", "dmitri", "claude", "gemini", "tarik")
DEFAULT_ROOT = os.path.expanduser("~/LLM")


def run_day(run_id: str) -> str | None:
    """`20261026T072831Z-133e4d51` -> `2026-10-26`. None if the id is not in that shape."""
    try:
        return datetime.strptime(run_id.split("-")[0], "%Y%m%dT%H%M%SZ").strftime("%Y-%m-%d")
    except (ValueError, IndexError):
        return None


def worker_cost(worker_path: str) -> float | None:
    """The one final record goose writes with a dollar figure, if this run has one."""
    try:
        with open(worker_path, errors="replace") as handle:
            found = None
            for line in handle:
                if '"cost_usd"' not in line:
                    continue
                try:
                    value = json.loads(line).get("cost_usd")
                except json.JSONDecodeError:
                    continue
                if isinstance(value, (int, float)):
                    found = float(value)
    except OSError:
        return None
    return found


def collect(root: str) -> dict:
    """One pass over every run directory on the machine.

    Returns per-(day, amigo) run counts and token totals, plus the counts that make the gaps
    visible: runs with no `result.json`, runs with no `worker.jsonl`, runs with a dollar figure.
    """
    days: dict[tuple[str, str], dict] = defaultdict(
        lambda: {"runs": 0, "tokens": 0, "cost_runs": 0, "cost_usd": 0.0}
    )
    totals = {
        "runs": 0,
        "tokens": 0,
        "runs_with_cost": 0,
        "cost_usd": 0.0,
        "missing_result_json": 0,
        "missing_worker_jsonl": 0,
        "no_token_record": 0,
    }
    for amigo in AMIGOS:
        pattern = os.path.join(root, f"{amigo}-bot", "tick-state", "runs", "*")
        for run_dir in sorted(glob.glob(pattern)):
            if not os.path.isdir(run_dir):
                continue
            run_id = os.path.basename(run_dir.rstrip(os.sep))
            day = run_day(run_id)
            if day is None:
                continue
            result_path = os.path.join(run_dir, "result.json")
            if not os.path.exists(result_path):
                totals["missing_result_json"] += 1
                continue
            try:
                with open(result_path, errors="replace") as handle:
                    result = json.load(handle)
            except (OSError, json.JSONDecodeError):
                totals["missing_result_json"] += 1
                continue
            tokens = result.get("total_tokens") or 0
            if not isinstance(tokens, int):
                tokens = 0
            bucket = days[(day, amigo)]
            bucket["runs"] += 1
            bucket["tokens"] += tokens
            totals["runs"] += 1
            totals["tokens"] += tokens
            if not tokens:
                totals["no_token_record"] += 1
            worker_path = os.path.join(run_dir, "worker.jsonl")
            if not os.path.exists(worker_path):
                totals["missing_worker_jsonl"] += 1
                continue
            cost = worker_cost(worker_path)
            if cost is None:
                continue
            bucket["cost_runs"] += 1
            bucket["cost_usd"] += cost
            totals["runs_with_cost"] += 1
            totals["cost_usd"] += cost
    return {"days": {f"{d}|{a}": v for (d, a), v in days.items()}, "totals": totals}


def report(data: dict, days_shown: int) -> str:
    days = sorted({key.split("|")[0] for key in data["days"]})
    shown = days[-days_shown:] if days_shown > 0 else days
    totals = data["totals"]
    lines = []
    if days:
        lines.append(f"Wake spend, {shown[0]} to {shown[-1]} ({len(shown)} days with runs on disk)")
        lines.append("")
        header = "| day | " + " | ".join(AMIGOS) + " | runs | tokens |"
        lines.append(header)
        lines.append("|" + "---|" * (len(AMIGOS) + 3))
        for day in shown:
            cells, run_sum, token_sum = [], 0, 0
            for amigo in AMIGOS:
                bucket = data["days"].get(f"{day}|{amigo}")
                if bucket:
                    cells.append(f"{bucket['runs']} · {bucket['tokens'] / 1e6:.2f}M")
                    run_sum += bucket["runs"]
                    token_sum += bucket["tokens"]
                else:
                    cells.append("—")
            lines.append(
                f"| {day} | " + " | ".join(cells) + f" | {run_sum} | {token_sum / 1e6:.2f}M |"
            )
        lines.append("")
    lines.append(
        f"Measured: {totals['runs']} runs, {totals['tokens']:,} tokens "
        f"({totals['tokens'] / 1e6:.1f}M) since the first run directory."
    )
    lines.append(
        f"Recorded in dollars: {totals['runs_with_cost']} of {totals['runs']} runs carry a "
        f"`cost_usd` field ({totals['cost_usd']:.2f} USD in total). "
        f"{totals['runs'] - totals['runs_with_cost']} runs have no dollar figure anywhere."
    )
    lines.append(
        f"Missing records: {totals['missing_result_json']} run directories with no readable "
        f"`result.json`, {totals['missing_worker_jsonl']} with no `worker.jsonl`, "
        f"{totals['no_token_record']} of the runs that do have a `result.json` report zero tokens."
    )
    lines.append(
        "No price is estimated here. Tokens are measured; dollars are not, and a count times a "
        "guessed rate would read like a record without being one."
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=DEFAULT_ROOT, help="directory holding <amigo>-bot")
    parser.add_argument("--days", type=int, default=7, help="days of table to show (0 = all)")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    if not os.path.isdir(args.root):
        print(f"wake_spend_record: no such root: {args.root}", file=sys.stderr)
        return 2
    data = collect(args.root)
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
        return 0
    print(report(data, args.days))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
