#!/usr/bin/env python3
"""Reconcile the drafts/tick-* review branches against main.

Why this exists (2026-10-10, Dmitri). The review gate has no closer: each
unattended wake pushes a `drafts/tick-*` branch and nothing merges it, so the
pile grows ~6/day and every later wake that wants a path on it has to recover
it by hand. Measured today: **148** such branches on origin, against 1 `main`.

The blocker recorded on `channels/reject-queue.md` -- "a wake runs in a checkout
with no git remote and no remote refs, so it cannot fetch a review branch" -- is
half true and half false. There is no *configured* remote, but the remote is
reachable: `git ls-remote <url>` and `git fetch <url> <ref>` work from a wake
checkout. So the pile CAN be inventoried from here.

This script does the inventory, not the merge. For each branch it compares the
files that branch changed (relative to its merge-base with main) against main's
current tree, and classifies each as:

  LANDED   main already has this file with byte-identical content
  DIFFERS  main has the path but different content (main moved on, or a real edit)
  MISSING  main does not have this path at all

MISSING is the high-signal class: a path that exists on a draft and nowhere on
main is the clearest evidence of genuinely unlanded work. DIFFERS is noisy
because main advances independently, so it is reported but not treated as a
verdict.

Prerequisite (the script does not do network I/O):

    git fetch --no-tags <url> 'refs/heads/drafts/*:refs/remotes/drafts/*'

Usage:
    python3 scripts/draft_branch_inventory.py [--refs-prefix refs/remotes/drafts]
        [--main main] [--json PATH] [--md PATH]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def git(*args: str) -> str:
    out = subprocess.run(
        ["git", *args], capture_output=True, text=True, check=False
    )
    if out.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {out.stderr.strip()}")
    return out.stdout


def blob(ref: str, path: str) -> str | None:
    """Return the blob hash of path at ref, or None if the path is absent."""
    r = subprocess.run(
        ["git", "rev-parse", f"{ref}:{path}"],
        capture_output=True, text=True, check=False,
    )
    if r.returncode != 0:
        return None
    return r.stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--refs-prefix", default="refs/remotes/drafts")
    ap.add_argument("--main", default="main")
    ap.add_argument("--json", default=None)
    ap.add_argument("--md", default=None)
    ap.add_argument(
        "--ignore-prefix",
        action="append",
        default=["to-do-lists/"],
        help="path prefix to treat as bookkeeping, not deliverable (repeatable)",
    )
    args = ap.parse_args()

    main_ref = args.main
    refs = git(
        "for-each-ref", "--format=%(refname)", args.refs_prefix
    ).splitlines()
    refs = sorted(r for r in refs if r.strip())
    if not refs:
        print(f"no refs under {args.refs_prefix}; run the fetch first", file=sys.stderr)
        return 2

    branches: list[dict] = []
    missing_index: dict[str, dict] = {}

    for ref in refs:
        short = ref[len(args.refs_prefix):].lstrip("/")
        # files this branch changed relative to where it forked from main
        base = git("merge-base", main_ref, ref).strip()
        changed = git("diff", "--name-only", base, ref).splitlines()
        changed = [
            p for p in changed
            if p.strip()
            and not any(p.startswith(pre) for pre in args.ignore_prefix)
        ]

        entry = {"branch": short, "sha": git("rev-parse", ref).strip(), "base": base,
                 "files": {"LANDED": [], "DIFFERS": [], "MISSING": []}}

        for path in changed:
            b = blob(ref, path)
            m = blob(main_ref, path)
            if m is None:
                status = "MISSING"
            elif m == b:
                status = "LANDED"
            else:
                status = "DIFFERS"
            entry["files"][status].append(path)
            if status == "MISSING":
                rec = missing_index.setdefault(
                    path, {"path": path, "count": 0, "branches": []}
                )
                rec["count"] += 1
                rec["branches"].append(short)

        entry["verdict"] = (
            "UNLANDED" if entry["files"]["MISSING"]
            else ("LANDED" if not entry["files"]["DIFFERS"] else "DIVERGED")
        )
        branches.append(entry)

    n = len(branches)
    unlanded = sum(1 for b in branches if b["verdict"] == "UNLANDED")
    landed = sum(1 for b in branches if b["verdict"] == "LANDED")
    diverged = sum(1 for b in branches if b["verdict"] == "DIVERGED")
    missing_sorted = sorted(
        missing_index.values(), key=lambda r: (-r["count"], r["path"])
    )

    summary = {
        "generated_by": "scripts/draft_branch_inventory.py",
        "main": git("rev-parse", "--short", main_ref).strip(),
        "branches_total": n,
        "branches_unlanded": unlanded,
        "branches_landed": landed,
        "branches_diverged": diverged,
        "distinct_missing_paths": len(missing_sorted),
        "missing_paths": missing_sorted,
        "branches": branches,
    }

    if args.json:
        Path(args.json).write_text(json.dumps(summary, indent=2) + "\n")

    if args.md:
        lines = []
        lines.append("# Draft-branch inventory")
        lines.append("")
        lines.append(
            f"Generated by `scripts/draft_branch_inventory.py` against `main` @ "
            f"`{summary['main']}`."
        )
        lines.append("")
        lines.append(
            f"- draft branches scanned: **{n}** (`{args.refs_prefix}/*`)"
        )
        lines.append(
            f"- carry at least one path main does not have (`UNLANDED`): **{unlanded}**"
        )
        lines.append(
            f"- every changed file already byte-identical on main (`LANDED`): **{landed}**"
        )
        lines.append(
            f"- changed files all present on main but differing (`DIVERGED`): **{diverged}**"
        )
        lines.append(
            f"- distinct paths absent from main across the pile: **{len(missing_sorted)}**"
        )
        lines.append("")
        lines.append("**How to read this.** `MISSING` is the high-signal class, but it is not")
        lines.append("automatically a defect: it also catches paths `main` is meant never to carry")
        lines.append("(transient `channels/declutter/` and `channels/telegram/` logs, `report.txt`).")
        lines.append("`DIFFERS` is noisy — `main` advances independently — and is reported, not")
        lines.append("judged. This file inventories; it does not adjudicate. Bookkeeping under")
        lines.append("`to-do-lists/` is excluded by default.")
        lines.append("")
        if missing_sorted:
            lines.append("## Paths a draft holds that `main` does not (by frequency)")
            lines.append("")
            lines.append("| branches | path | newest branch holding it |")
            lines.append("|---:|---|---|")
            for rec in missing_sorted:
                lines.append(
                    f"| {rec['count']} | `{rec['path']}` | `{sorted(rec['branches'])[-1]}` |"
                )
        else:
            lines.append(
                "No path on any draft is absent from `main`: the pile holds no "
                "work that main lacks by this measure."
            )
        Path(args.md).write_text("\n".join(lines) + "\n")

    print(json.dumps({k: v for k, v in summary.items() if k != "branches"}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
