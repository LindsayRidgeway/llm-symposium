#!/usr/bin/env python3
"""How a wake spends its actions: the action cap, the reconnaissance before the first file.

The commons adopted a rule on 2026-10-12 — "start with the artefact, not with the research" —
because wakes were being cut off at goose's action cap with nothing on disk. The rule was
derived from a defect noticed in run reports. It was never measured: whether wakes actually
write sooner now, how many actions the cap gives them, and how many runs write nothing at all
has been asserted from memory in every later report.

This answers it from the runs' own transcripts, which record every tool call:

  tools        how many tool calls the run made (the cap shows up as a mode at 25)
  first_write  the 1-based index of the first `write`/`edit` call, or none
  cut_off      whether the runner killed the run at the cap (`result.json`)
  changed      how many paths the run left modified (its own count)
  land         the landing outcome the runner recorded, e.g. `refused_dirty_tree`

It reads, and never writes, the bot directories. Nothing here is inside the repository, so it
is a census of this machine and says so: on any other machine it finds no runs and exits
without a verdict rather than with a zero.

Caveat, stated in the output as well as here: only the `write`/`edit` tools count as a write.
A file created by a shell redirect or a heredoc is not seen, so `first_write` is an upper bound
on how long a run spent before its first artefact, not a lower one.

Usage:
    scripts/wake_action_census.py                    # all amigo bots under ~/LLM
    scripts/wake_action_census.py --root /path/to/LLM
    scripts/wake_action_census.py --json /tmp/census.json
    scripts/wake_action_census.py --since 2026-10-12 # only runs started on/after a date
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

WRITE_TOOLS = frozenset({"write", "edit", "multi_edit", "notebook_edit", "create_file"})
BOTS = ("desi-bot", "claude-bot", "gemini-bot", "tarik-bot", "dmitri-bot")


def _iter_json_lines(path, needle=None):
    """Yield parsed objects from a worker log, plain or gzipped.

    The log begins with a handful of non-JSON banner lines (the goose splash), so every
    line that does not parse is skipped rather than aborting the run. `needle` is a cheap
    substring filter applied before parsing: a run writes thousands of thinking blocks and
    a few dozen tool calls, and decoding only the second kind is the difference between
    seconds and minutes across a thousand runs.
    """
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", errors="replace") as fh:
        for line in fh:
            if needle is not None and needle not in line:
                continue
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                yield json.loads(line)
            except ValueError:
                continue


def parse_worker(path):
    """Return (tool_calls, first_write_index, tool_mix) for one worker log.

    `first_write_index` is 1-based, and None when the run never called a writing tool.
    """
    tools = 0
    first_write = None
    mix = Counter()
    for event in _iter_json_lines(path, needle='"toolRequest"'):
        if event.get("type") != "message":
            continue
        for block in event.get("message", {}).get("content", []):
            if block.get("type") != "toolRequest":
                continue
            call = block.get("toolCall", {}).get("value", {}) or {}
            name = call.get("name")
            tools += 1
            mix[name or "unknown"] += 1
            if name in WRITE_TOOLS and first_write is None:
                first_write = tools
    return tools, first_write, mix


def parse_run(run_dir):
    """Read one run directory into a flat record, or None if it is not a run."""
    worker = os.path.join(run_dir, "worker.jsonl")
    if not os.path.exists(worker):
        worker = worker + ".gz"
    result_path = os.path.join(run_dir, "result.json")
    if not os.path.exists(worker) and not os.path.exists(result_path):
        return None
    run_id = os.path.basename(run_dir.rstrip(os.sep))
    rec = {
        "run_id": run_id,
        "started": run_id[:16],
        "status": None,
        "cut_off": None,
        "changed": None,
        "land": None,
        "tokens": None,
        "tools": None,
        "first_write": None,
        "mix": {},
    }
    if os.path.exists(result_path):
        try:
            with open(result_path) as fh:
                res = json.load(fh)
        except ValueError:
            res = {}
        rec["status"] = res.get("status")
        rec["cut_off"] = res.get("cut_off")
        rec["changed"] = len(res.get("changed_paths") or [])
        rec["land"] = res.get("land")
        rec["tokens"] = res.get("total_tokens")
    if os.path.exists(worker):
        tools, first_write, mix = parse_worker(worker)
        rec["tools"] = tools
        rec["first_write"] = first_write
        rec["mix"] = dict(mix)
    return rec


def collect(root):
    """Every run under `<root>/<bot>/tick-state/runs/`, in start order."""
    runs = []
    for bot in BOTS:
        runs_dir = os.path.join(root, bot, "tick-state", "runs")
        if not os.path.isdir(runs_dir):
            continue
        amigo = bot.split("-")[0]
        for name in sorted(os.listdir(runs_dir)):
            path = os.path.join(runs_dir, name)
            if not os.path.isdir(path):
                continue
            rec = parse_run(path)
            if rec is None:
                continue
            rec["amigo"] = amigo
            runs.append(rec)
    runs.sort(key=lambda r: r["run_id"])
    return runs


def _median(values):
    if not values:
        return None
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def summarise(runs, late_after=15):
    """Per-amigo counts, and the two shares that carry the question."""
    out = {}
    for amigo in sorted({r["amigo"] for r in runs}):
        mine = [r for r in runs if r["amigo"] == amigo]
        parsed = [r for r in mine if r["tools"]]
        with_write = [r for r in parsed if r["first_write"]]
        out[amigo] = {
            "runs": len(mine),
            "with_transcript": len(parsed),
            "no_tool_calls": len(mine) - len(parsed),
            "cut_off": sum(1 for r in mine if r["cut_off"]),
            "changed_zero": sum(1 for r in mine if r["changed"] == 0),
            "median_tools": _median([r["tools"] for r in parsed]),
            "max_tools": max((r["tools"] for r in parsed), default=None),
            "wrote_nothing": len(parsed) - len(with_write),
            "first_write_late": sum(
                1 for r in with_write if r["first_write"] >= late_after
            ),
            "median_first_write": _median([r["first_write"] for r in with_write]),
        }
    return out


def weekly(runs, late_after=15):
    """One row per week the runs start in, so a rule change can be seen rather than argued."""
    buckets = defaultdict(list)
    for r in runs:
        stamp = r["run_id"][:8]
        try:
            day = datetime.strptime(stamp, "%Y%m%d")
        except ValueError:
            continue
        week = "{}-W{:02d}".format(*day.isocalendar()[:2])
        buckets[week].append(r)
    rows = []
    for week in sorted(buckets):
        mine = buckets[week]
        parsed = [r for r in mine if r["tools"]]
        with_write = [r for r in parsed if r["first_write"]]
        rows.append(
            {
                "week": week,
                "runs": len(mine),
                "with_transcript": len(parsed),
                "median_tools": _median([r["tools"] for r in parsed]),
                "wrote_nothing": len(parsed) - len(with_write),
                "wrote_by_10": sum(1 for r in with_write if r["first_write"] <= 10),
                "first_write_late": sum(
                    1 for r in with_write if r["first_write"] >= late_after
                ),
                "cut_off": sum(1 for r in mine if r["cut_off"]),
                "changed_zero": sum(1 for r in mine if r["changed"] == 0),
            }
        )
    return rows


def _fmt(value):
    if value is None:
        return "-"
    if isinstance(value, float) and value == int(value):
        return str(int(value))
    return str(value)


def report(root, runs, per_amigo, rows):
    print("wake action census — {}".format(root))
    print("{} runs read, {} with a parseable transcript".format(
        len(runs), sum(1 for r in runs if r["tools"])))
    print()
    header = ("amigo", "runs", "tr", "cut", "chg0", "tools~", "max", "nowrite", "late")
    print("{:<7} {:>5} {:>5} {:>4} {:>5} {:>7} {:>4} {:>8} {:>5}".format(*header))
    for amigo, s in per_amigo.items():
        print("{:<7} {:>5} {:>5} {:>4} {:>5} {:>7} {:>4} {:>8} {:>5}".format(
            amigo, s["runs"], s["with_transcript"], s["cut_off"], s["changed_zero"],
            _fmt(s["median_tools"]), _fmt(s["max_tools"]), s["wrote_nothing"],
            s["first_write_late"]))
    print()
    print("cut  = runs the runner recorded as killed at the action cap")
    print("chg0 = runs that left no changed path")
    print("tr   = runs with a parseable transcript (the rest are counted, not guessed)")
    print("late = runs whose first write/edit came at or after action 15")
    print()
    print("by week (UTC, from the run id)")
    print("{:<9} {:>5} {:>4} {:>7} {:>8} {:>6} {:>5} {:>4} {:>5}".format(
        "week", "runs", "tr", "tools~", "nowrite", "by10", "late", "cut", "chg0"))
    for row in rows:
        print("{:<9} {:>5} {:>4} {:>7} {:>8} {:>6} {:>5} {:>4} {:>5}".format(
            row["week"], row["runs"], row["with_transcript"],
            _fmt(row["median_tools"]), row["wrote_nothing"], row["wrote_by_10"],
            row["first_write_late"], row["cut_off"], row["changed_zero"]))
    print()
    print("by10 = of the runs that wrote at all, how many wrote by their tenth action")
    print("Only write/edit tools count as writing; a shell redirect is invisible here,")
    print("so every 'late' figure is an upper bound, not a lower one.")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=os.path.expanduser("~/LLM"),
                    help="directory holding the *-bot trees (default: ~/LLM)")
    ap.add_argument("--since", default=None,
                    help="only runs whose id starts on/after this YYYY-MM-DD")
    ap.add_argument("--json", default=None, help="also write the raw rows here")
    ap.add_argument("--late", type=int, default=15,
                    help="action index at which a first write counts as late (default 15)")
    args = ap.parse_args(argv)

    if not os.path.isdir(args.root):
        print("wake_action_census: no such root: {}".format(args.root), file=sys.stderr)
        print("This census reads the bot run trees on the machine that runs the wakes.",
              file=sys.stderr)
        return 2
    runs = collect(args.root)
    if args.since:
        runs = [r for r in runs if r["run_id"][:10] >= args.since]
    if not runs:
        print("wake_action_census: no run directories under {}".format(args.root),
              file=sys.stderr)
        return 2

    per_amigo = summarise(runs, args.late)
    rows = weekly(runs, args.late)
    report(args.root, runs, per_amigo, rows)
    if args.json:
        payload = {
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "root": args.root,
            "runs": len(runs),
            "per_amigo": per_amigo,
            "weekly": rows,
            "detail": runs,
        }
        with open(args.json, "w") as fh:
            json.dump(payload, fh, indent=1, sort_keys=True)
        print("\nwrote {}".format(args.json))
    return 0


if __name__ == "__main__":
    sys.exit(main())
