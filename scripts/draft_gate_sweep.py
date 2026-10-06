#!/usr/bin/env python3
# Owner: Dmitri
"""The review gate's closer — the tool the gate has never had.

Since 2026-09-16 every wake lands its changed files on a `drafts/tick-*` branch "for review".
Nothing closes those branches. Measured 2026-10-05: 101 `drafts/tick-*` branches, 2 merged, 99
open, one per four-hourly wake. Two costs follow, both observed:

  * Wakes spend their budget recovering work that already exists on a branch, because a path that
    never reached `main` looks identical to a path that was never written. The vulvodynia screen
    was written, recovered and re-landed four times; ten of twenty wakes recomputed a path that was
    sitting on a review branch.
  * The pile cannot be mass-merged: 68 `land(wake)` commits are already on `main`, so many branches
    hold work that *did* land, by a different path or a later edit. A merge would double it.

So the gate does not need a merger. It needs a **classifier and a closer**, and that must be a
script rather than a judgement, for the same reason the reject-queue count is
(`scripts/reject_queue_sweep.py`): a language model asked "is this branch already landed?" will
sometimes say yes, and a wrong yes silently discards a branch that held real work.

For each `drafts/tick-*` branch this tool answers one question per changed file: **is this exact
blob already on `main`?**

  EMPTY      the branch changed nothing but its own bookkeeping (to-do lists). Nothing to keep.
  LANDED     every substantive file it changed is byte-identical to `main` already. Safe to close.
  UNSETTLED  at least one substantive file is absent from, or different on, `main`. Keep it, and
             the tool prints the files, so the next wake lands the work and closes the branch.

`--check` (default) prints the table and changes nothing. `--close-landed` deletes the EMPTY and
LANDED branches from the remote with `git push <remote> --delete`. The tool refuses to close a
branch it is not certain about: only EMPTY and LANDED are ever deleted.

This must run in a checkout wired to the remote (the landing machine); a wake checkout has no
remote and cannot fetch a branch, which is *why* the gate has sat open — see the reject-queue entry
"Drain the draft pile / verify landed drafts".

Usage:
  python3 scripts/draft_gate_sweep.py                 # classify, change nothing
  python3 scripts/draft_gate_sweep.py --json          # machine-readable
  python3 scripts/draft_gate_sweep.py --close-landed  # retire EMPTY + LANDED branches
  python3 scripts/draft_gate_sweep.py --repo DIR --no-fetch --main main   # offline / tests
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Branch shape written by the wake harness: drafts/tick-<UTC stamp>-<short sha>. The trailing `*`
# matters: `git for-each-ref refs/heads/drafts/tick-` with no wildcard matches that exact name and
# returns nothing, which reads as "no branches" — a silent-empty that would have hidden the pile.
DRAFT_REF_GLOB = "refs/remotes/origin/drafts/tick-*"
LOCAL_REF_GLOB = "refs/heads/drafts/tick-*"
DATE_RE = re.compile(r"tick-(?P<day>\d{8})T")

# A path whose presence on a draft branch is the wake's own bookkeeping, not work. The instruction
# to every wake is to diff *non-todo content* against main; a branch that touched only its to-do
# list has landed nothing worth keeping.
DEFAULT_NOISE = ("to-do-lists/",)

CLOSABLE = ("EMPTY", "LANDED")


def _git(repo, *args):
    return subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)


def branch_date(name: str) -> str | None:
    """The calendar day encoded in a draft branch name, or None if it does not carry one."""
    m = DATE_RE.search(name)
    if not m:
        return None
    d = m.group("day")
    return f"{d[:4]}-{d[4:6]}-{d[6:]}"


def is_noise(path: str, noise=DEFAULT_NOISE) -> bool:
    """True if `path` is bookkeeping rather than work, under the given prefixes."""
    for n in noise:
        n = n.rstrip("/")
        if path == n or path.startswith(n + "/"):
            return True
    return False


def blob_id(repo, rev: str, path: str) -> str | None:
    """The git blob hash of `path` at `rev`, or None if the path is absent there."""
    p = _git(repo, "rev-parse", "--verify", "--quiet", f"{rev}:{path}")
    if p.returncode != 0:
        return None
    return p.stdout.strip() or None


def changed_paths(repo, main: str, branch: str) -> list[str]:
    """Files the branch changed relative to where it left `main` (the branch's own work)."""
    p = _git(repo, "diff", "--name-only", "--diff-filter=ACDMRT", f"{main}...{branch}")
    if p.returncode != 0:
        # No common ancestor (or an unexpected range error): fall back to a plain two-dot diff.
        p = _git(repo, "diff", "--name-only", "--diff-filter=ACDMRT", main, branch)
    return [ln for ln in p.stdout.splitlines() if ln.strip()]


def classify_branch(repo, main: str, branch: str, noise=DEFAULT_NOISE) -> dict:
    """EMPTY / LANDED / UNSETTLED for one branch, with the file lists behind the verdict."""
    changed = changed_paths(repo, main, branch)
    noise_paths = [p for p in changed if is_noise(p, noise)]
    substantive = [p for p in changed if not is_noise(p, noise)]

    landed, unlanded = [], []
    for path in substantive:
        # The one question that matters: is the branch's copy of this file already on main?
        if blob_id(repo, branch, path) == blob_id(repo, main, path):
            landed.append(path)
        else:
            unlanded.append(path)

    if not substantive:
        status = "EMPTY"
    elif not unlanded:
        status = "LANDED"
    else:
        status = "UNSETTLED"

    return {
        "branch": branch,
        "short": short_ref(branch),
        "date": branch_date(branch),
        "status": status,
        "changed": changed,
        "landed": landed,
        "unlanded": unlanded,
        "noise": noise_paths,
    }


def short_ref(ref: str) -> str:
    for pre in ("refs/remotes/origin/", "refs/remotes/", "refs/heads/"):
        if ref.startswith(pre):
            return ref[len(pre):]
    return ref


def list_draft_branches(repo, ref_glob: str = None) -> list[str]:
    """All draft branches in the checkout, newest last. Tries the remote glob, then local."""
    globs = [ref_glob] if ref_glob else [DRAFT_REF_GLOB, LOCAL_REF_GLOB]
    refs = []
    for g in globs:
        if not g.endswith(("*", "/")):
            g += "*"  # a bare prefix is an exact-name match to for-each-ref, i.e. an empty list
        p = _git(repo, "for-each-ref", "--format=%(refname)", g)
        refs = [r.strip() for r in p.stdout.splitlines() if r.strip()]
        if refs:
            break
    return sorted(refs)


def closable(records) -> list[dict]:
    """Only EMPTY and LANDED branches are ever retired; everything else is left for a wake."""
    return [r for r in records if r["status"] in CLOSABLE]


def close_branches(repo, remote: str, records, dry_run: bool = False) -> list[str]:
    """Delete the given branches from `remote`. Returns the branch names removed."""
    removed = []
    for r in records:
        target = r["short"]
        if dry_run:
            removed.append(r["branch"])
            continue
        p = _git(repo, "push", remote, "--delete", target)
        if p.returncode == 0:
            removed.append(r["branch"])
        else:
            sys.stderr.write(f"could not delete {target}: {p.stderr.strip()}\n")
    return removed


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Classify and close the drafts/tick-* review gate.")
    ap.add_argument("--repo", default=".", help="checkout to inspect (default: cwd)")
    ap.add_argument("--main", default=None, help="main ref (default: origin/main if present, else main)")
    ap.add_argument("--remote", default="origin", help="remote to fetch from and delete on")
    ap.add_argument("--ref-glob", default=None, help="override the branch ref glob")
    ap.add_argument("--noise", action="append", default=None,
                    help="extra noise prefix (repeatable); replaces the default set")
    ap.add_argument("--no-fetch", action="store_true", help="do not run `git fetch` first")
    ap.add_argument("--close-landed", action="store_true",
                    help="delete EMPTY and LANDED branches from the remote")
    ap.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = ap.parse_args(argv)

    repo = Path(args.repo).resolve()
    noise = tuple(args.noise) if args.noise else DEFAULT_NOISE

    main = args.main
    if main is None:
        main = "origin/main" if _git(repo, "rev-parse", "--verify", "--quiet", "origin/main").returncode == 0 else "main"

    if not args.no_fetch:
        fetch = _git(repo, "fetch", "--prune", args.remote)
        if fetch.returncode != 0:
            sys.stderr.write(f"warning: git fetch {args.remote} failed; using local refs\n")

    refs = list_draft_branches(repo, args.ref_glob)
    records = [classify_branch(repo, main, r, noise) for r in refs]
    counts = {s: 0 for s in ("EMPTY", "LANDED", "UNSETTLED")}
    for r in records:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    if args.json:
        print(json.dumps({"main": main, "counts": counts, "branches": records}, indent=2))
    else:
        print(f"review gate: {len(records)} draft branch(es) against {main}")
        print(f"  EMPTY {counts['EMPTY']}   LANDED {counts['LANDED']}   UNSETTLED {counts['UNSETTLED']}")
        for r in records:
            day = r["date"] or "?"
            print(f"  [{r['status']:9}] {day}  {r['short']}")
            for path in r["unlanded"]:
                print(f"        unlanded: {path}")
        settles = [r for r in records if r["status"] == "UNSETTLED"]
        if settles:
            print(f"\n{len(settles)} branch(es) hold work not yet on {main}; land those files, then "
                  f"re-run with --close-landed.")

    if args.close_landed:
        to_close = closable(records)
        removed = close_branches(repo, args.remote, to_close)
        verb = "would retire" if args.no_fetch and args.ref_glob else "retired"
        print(f"\n{verb} {len(removed)} branch(es): " + ", ".join(short_ref(r) for r in removed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
