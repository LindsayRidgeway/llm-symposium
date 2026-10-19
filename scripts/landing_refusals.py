#!/usr/bin/env python3
"""Reconcile the landing refusals — which refused runs are still refused.

Why this exists (2026-10-19, Dmitri). `land_runs.py` writes `landing_failed.txt` into a run's own
directory when the repository's tests show the run's diff introduced new failures, and that file is
never touched again. It is a **verdict**, not a state: it stays in the run directory after the same
work has landed under a later run's commit. Read a fortnight later it says "this work was refused"
about work that is on `main` and green.

Measured this wake, on the run that this wake was assigned to review (desi `20261019T110921Z-df991cc4`):

* its `landing_failed.txt` reads `this run's diff introduced new failures: test_drive_bridge_status.py`;
* all eight paths it claims are on `main`, added whole by desi run `20261019T130933Z-8421299d`
  (commit `6b85041d`), whose own report says the flaky test was traced and fixed;
* the test now passes 15/15 consecutive runs, and the race that made it flaky is documented in the
  test file itself (`mount_unreadable`).

So the refusal was true on the day and is false now, and nothing in the repository distinguishes the
two. That is the same shape as the 2026-09-23 defect ("unlanded is not missing"): a durable marker
that a later reader takes for a verdict about today, which is how ten wakes came to recompute the
same work. This script does the reconciliation a machine can do: for every refusal on the disk, check
whether the run's own claimed paths reached this checkout's `main`.

Classification, per refused run:

    reconciled  every path the run's LAND line claims is on main — the refusal was made good later
    partial     some are on main and some are not — real missing work, and the refusal is half true
    open        none of the claimed paths is on main — the refusal still stands
    no-claim    no LAND line with paths (cut off, or a report that never said) — nothing to check

The `no-claim` rows matter more than they look: a run cut off at its action cap often refused with
nothing named, and that is a delivery nobody can chase from the run record alone.

Read-only. It never edits a run directory and never re-runs a test.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

# A LAND line, as the wake instruction asks for it: `LAND: a, b, c`. Reports also carry
# `LAND: (none yet)`, `LAND: (pending)` and `LAND: (nothing yet)` — those are claims of nothing.
LAND_RE = re.compile(r"^\s*LAND:\s*(.+)$", re.MULTILINE)
PLACEHOLDER = re.compile(r"^\(.*\)$")


def claimed_paths(report_text: str) -> list[str]:
    """The paths a run's report claims, from its last LAND line.

    Last, not first: a report is rewritten as the run proceeds (the instruction says so), so an
    earlier line can legitimately name less than the run finished with.
    """
    matches = LAND_RE.findall(report_text or "")
    if not matches:
        return []
    out: list[str] = []
    for raw in matches[-1].split(","):
        item = raw.strip().strip("`").strip().rstrip(".")
        if not item or PLACEHOLDER.match(item):
            continue
        out.append(item)
    return out


def read(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except OSError:
        return ""


def classify(run_dir: Path, repo: Path) -> dict:
    """One refusal, checked against the repository's own files."""
    reason = read(run_dir / "landing_failed.txt").strip().splitlines()
    paths = claimed_paths(read(run_dir / "report.txt"))
    present = [p for p in paths if (repo / p).exists()]
    if not paths:
        state = "no-claim"
    elif len(present) == len(paths):
        state = "reconciled"
    elif present:
        state = "partial"
    else:
        state = "open"
    return {
        "run": run_dir.name,
        "bot": run_dir.parent.parent.parent.name,
        "state": state,
        "reason": reason[0] if reason else "",
        "claimed": len(paths),
        "on_main": len(present),
        "missing": [p for p in paths if p not in present],
    }


def find_runs(roots: list[Path]) -> list[Path]:
    """Every run directory under the given roots that carries a refusal."""
    found: list[Path] = []
    for root in roots:
        pattern = os.path.join(str(root), "*", "tick-state", "runs", "*", "landing_failed.txt")
        for hit in glob.glob(pattern):
            found.append(Path(hit).parent)
    return sorted(set(found), key=lambda p: p.name)


def survey(roots: list[Path], repo: Path) -> dict:
    rows = [classify(r, repo) for r in find_runs(roots)]
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["state"]] = counts.get(row["state"], 0) + 1
    return {
        "repo": str(repo),
        "refusals": len(rows),
        "counts": counts,
        "rows": rows,
    }


def render(facts: dict) -> str:
    counts = facts["counts"]
    lines = [
        f"{facts['refusals']} refused landing(s) on disk; checked against {facts['repo']}",
        "  " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())) if counts else "  none",
        "",
    ]
    order = {"open": 0, "partial": 1, "no-claim": 2, "reconciled": 3}
    for row in sorted(facts["rows"], key=lambda r: (order.get(r["state"], 9), r["run"])):
        detail = ""
        if row["state"] == "partial":
            detail = "  missing: " + ", ".join(row["missing"][:4])
            if len(row["missing"]) > 4:
                detail += f" (+{len(row['missing']) - 4} more)"
        lines.append(
            f"  [{row['state']:<10}] {row['bot']:<7} {row['run']}  "
            f"{row['on_main']}/{row['claimed']} on main{detail}"
        )
        if row["state"] == "open" and row["reason"]:
            lines.append(f"               reason: {row['reason'][:110]}")
    lines += [
        "",
        "reconciled = the refusal was made good later; do not redo that work.",
        "open/partial = real missing work; the run's reason above is the starting point.",
        "no-claim = a refusal with nothing named; only the run's own transcript can say what it was.",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs-root", action="append", default=None,
                    help="directory holding <bot>/tick-state/runs (repeatable); "
                         "defaults to ~/LLM")
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parent.parent),
                    help="the checkout whose files are the test of 'reached main'")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when any refusal is still open or partial")
    args = ap.parse_args(argv)

    roots = [Path(os.path.expanduser(r)) for r in (args.runs_root or ["~/LLM"])]
    facts = survey(roots, Path(args.repo).resolve())
    if args.json:
        print(json.dumps(facts, indent=2))
    else:
        print(render(facts))
    if args.strict and (facts["counts"].get("open") or facts["counts"].get("partial")):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
