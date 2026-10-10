#!/usr/bin/env python3
# Owner: dmitri
"""What is actually in W — and how much of it the ledger can ever close.

Why this exists (2026-10-10). The daily report prints `W` (waiting for review) as
the honest remainder, and says plainly what it cannot do: tell *delivery* from
*review*. Its own words are "the waiting-for-review counts describe delivery, not
review — they can include finished work the lander parked on a side branch rather
than work nobody has looked at." That caveat has been carried unquantified for
days, and the pile keeps being described as a review backlog when part of it is
not reviewable at all.

This script replaces the caveat with two cheap, read-only measurements:

  1. **Path presence.** For every waiting item, do the paths it names exist on
     `main`? `all_present` / `some_present` / `none_present` / `no_paths`.

  2. **The pipeline floor.** `channels/item_ledger.py` marks a run accomplished
     only when a `land(wake): work from run <id>` commit names it (see
     `landed_run_ids`). Work that reached `main` any other way — the era before
     the landing pipeline existed, or a manual commit — can *never* be marked by
     that collector. So `W` has a floor: items filed before the first `land(wake)`
     commit that no land commit names sit in `W` forever, however hard anyone
     reviews. That floor is a fact about delivery, not about effort, and it should
     be named rather than counted as a backlog.

It changes nothing: it reads `channels/items.jsonl` and `git log`, and prints a
report. Read-only by construction — nothing here writes the ledger.

Honest limit, stated here so the number is not over-read: path *presence* is not
proof that *this run's* content landed. The same file is touched by many later
runs, so `all_present` means "the paths this run named exist on main now", not
"this run's version of them is on main". It is an upper bound on delivery, which
is still enough to separate a reviewable queue from a historical one.

CLI:
    python3 scripts/waiting_pile.py                 # markdown report to stdout
    python3 scripts/waiting_pile.py --out FILE      # write it to a file
    python3 scripts/waiting_pile.py --json          # machine-readable summary
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from channels import item_ledger as il  # noqa: E402

LAND_STAMP = il.LANDING_STAMP  # "land(wake)"


def pipeline_start(repo: Path = REPO) -> str | None:
    """ISO date of the oldest `land(wake)` commit, or None if the pipeline never ran.

    The landing pipeline is the *only* mechanism the ledger has ever used to close an
    item without a human. Before its first commit there is no automated closer at all, so
    everything filed earlier is closed, if ever, by hand.
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "log", "--format=%cI", "--grep", LAND_STAMP],
            capture_output=True, text=True, timeout=60, check=True,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    if not out:
        return None
    return min(out.splitlines())


def path_status(paths: list[str] | None, repo: Path = REPO) -> str:
    """all_present / some_present / none_present / no_paths. Never raises on odd input."""
    paths = [p for p in (paths or []) if isinstance(p, str) and p]
    if not paths:
        return "no_paths"
    present = sum(1 for p in paths if (repo / p).exists())
    if present == len(paths):
        return "all_present"
    if present:
        return "some_present"
    return "none_present"


def _day(stamp: str | None) -> str:
    return (stamp or "")[:10]


def summarize(items: dict[str, dict], start: str | None, repo: Path = REPO) -> dict:
    """The whole measurement, as plain data, so a test can hold it still."""
    waiting = [r for r in items.values() if il.letter_for(r) == "W"]
    names = sorted({a for r in waiting for a in [r.get("assigned_to")] if a})
    named = {n: 0 for n in names}
    holes = 0
    by_status = {"all_present": 0, "some_present": 0, "none_present": 0, "no_paths": 0}
    by_author: dict[str, int] = {}
    floor_pre_pipeline = 0
    opened = 0
    for r in waiting:
        who = r.get("assigned_to")
        if who:
            named[who] = named.get(who, 0) + 1
        else:
            holes += 1
        by_status[path_status(r.get("paths"), repo)] += 1
        author = r.get("amigo") or "?"
        by_author[author] = by_author.get(author, 0) + 1
        filed = r.get("filed_utc")
        if start and filed and filed < start:
            # filed before the pipeline existed. The collector (landed_run_ids) is the only
            # automated closer and it can never name these, because no land commit will.
            floor_pre_pipeline += 1
        elif start and filed:
            opened += 1
    return {
        "waiting": len(waiting),
        "named": named,
        "holes": holes,
        "by_path_status": by_status,
        "by_author": by_author,
        "pipeline_start": start,
        "floor_pre_pipeline": floor_pre_pipeline,
        "pipeline_era": opened,
        "newest_waiting": max((r.get("filed_utc") or "") for r in waiting) if waiting else None,
        "oldest_waiting": min((r.get("filed_utc") or "") for r in waiting) if waiting else None,
    }


def render(s: dict) -> str:
    w = s["waiting"]
    named = ", ".join(f"{k}={v}" for k, v in sorted(s["named"].items())) or "(none)"
    st = s["by_path_status"]
    lines = [
        "# What is actually in W",
        "",
        f"*Generated {dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} by "
        f"`scripts/waiting_pile.py` (read-only).*",
        "",
        f"Waiting items (W): **{w}**",
        f"  carried by name: {named}",
        f"  holes (no name): {s['holes']}",
        f"  oldest still waiting: {_day(s['oldest_waiting'])} · "
        f"newest: {_day(s['newest_waiting'])}",
        "",
        "## Do the paths each item names exist on main?",
        "",
        f"  all_present   {st['all_present']:4d}   every path this run named exists on main now",
        f"  some_present  {st['some_present']:4d}   part of it exists",
        f"  none_present  {st['none_present']:4d}   none of it exists on main",
        f"  no_paths      {st['no_paths']:4d}   the run recorded no paths",
        "",
        f"So **{st['all_present']} of {w}** waiting items ({_pct(st['all_present'], w)}) name only "
        "paths that are on main. Those are at least *delivered in some form*; whether *that run's* "
        "version landed cannot be told from presence alone, so this is an upper bound on delivery, "
        "not a proof of it.",
        "",
        "## How many can the ledger ever close on its own?",
        "",
    ]
    if not s["pipeline_start"]:
        lines.append("  No `land(wake)` commit exists, so there is no automated closer at all.")
    else:
        lines += [
            f"  The landing pipeline's first commit is {_day(s['pipeline_start'])}. The ledger "
            "closes a run only when a `land(wake)` commit names it.",
            f"  filed before that date and still waiting: **{s['floor_pre_pipeline']}**",
            f"  filed on or after that date and still waiting: {s['pipeline_era']}",
            "",
            f"The **{s['floor_pre_pipeline']}** pre-pipeline items are a *floor* on W, not a "
            "backlog: no reviewer and no lander can retire them, because the only automated closer "
            "cannot name them. Every daily report that counts them as 'waiting for review' is "
            "counting delivery as effort. They need a rule of their own (a closer that closes "
            "pre-pipeline work by hand, once), not more looking.",
        ]
    return "\n".join(lines) + "\n"


def _pct(n: int, d: int) -> str:
    return f"{0 if not d else round(100 * n / d)}%"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=None, help="write the markdown report here")
    ap.add_argument("--json", action="store_true", help="print the summary as JSON instead")
    ap.add_argument("--repo", default=str(REPO))
    args = ap.parse_args(argv)
    repo = Path(args.repo)
    start = pipeline_start(repo)
    s = summarize(il.load(), start, repo)
    if args.json:
        print(json.dumps(s, indent=2, sort_keys=True))
        return 0
    text = render(s)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
