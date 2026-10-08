#!/usr/bin/env python3
# Owner: Dmitri
"""Classify the drafts/tick-* review branches against main, and close the spent ones.

The review gate (2026-09-23) delivers a wake's work to a `drafts/tick-*` branch and waits for a
reviewer that does not exist. Measured 2026-10-05: 101 such branches, 2 merged, 99 open — one per
4-hourly wake back to 2026-09-16 — while 68 `land(wake)` commits are already on `main`. So the pile
is not 99 pieces of lost work; it is a small number of genuinely unlanded files buried under a large
number of branches whose content is already on `main` under a different path. Mass-merging would
duplicate; ignoring it re-accumulates; the missing thing is a **triage** that says which is which.

This script is that triage. For each branch it finds the merge-base with `--base` (default `main`),
takes the changed paths, drops the noise (`to-do-lists/` by default), and classifies every path:

  LANDED   the branch's content for the path is byte-identical to the base's  -> nothing to land
  NEW      the path does not exist on the base at all                        -> genuinely unlanded
  DIFFERS  the path exists on the base with different content               -> a human must judge
                                                                              (older? newer? clobber?)

A branch with no NEW and no DIFFERS holds nothing unlanded: it is **spent**, and `--close-spent`
deletes it. A branch with NEW content is the one worth landing; the paths are printed, oldest
branches last, so the reader can act without opening 99 diffs.

Why a wake cannot just run it: the wake checkout has no git remote (`git remote -v` is empty), so it
cannot fetch a review branch — this is the blocker already recorded on the reject queue as "Drain the
draft pile". This script runs where the branches exist (the landing machine). It is safe to run dry:
without `--close-spent` it writes nothing.

Usage:
  python3 scripts/drafts_triage.py                      # report, touching nothing
  python3 scripts/drafts_triage.py --remote             # include refs/remotes/origin/drafts/tick-*
  python3 scripts/drafts_triage.py --json out.json      # machine-readable plan
  python3 scripts/drafts_triage.py --close-spent        # delete branches with nothing unlanded
  python3 scripts/drafts_triage.py --selftest           # build a throwaway repo and check itself
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_PATTERN = "drafts/tick-*"
DEFAULT_IGNORE = ("to-do-lists/",)

LANDED, NEW, DIFFERS = "LANDED", "NEW", "DIFFERS"


def git(*args, cwd=None, check=True):
    """Run git and return stripped stdout, or raise with git's own message."""
    proc = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if check and proc.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), proc.stderr.strip()))
    return proc.stdout.strip()


def git_rc(*args, cwd=None):
    """Run git and return only its exit code — for `--quiet`, which has no output either way."""
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True).returncode


def list_branches(base_repo, pattern=DEFAULT_PATTERN, include_remote=False):
    """Ref names matching the pattern, newest tip first by commit date."""
    refs = ["refs/heads/"]
    if include_remote:
        refs.append("refs/remotes/origin/")
    out = []
    for prefix in refs:
        fmt = "%(refname:short)%09%(committerdate:unix)"
        listing = git("for-each-ref", "--format=" + fmt,
                      prefix + pattern, cwd=base_repo)
        for line in listing.splitlines():
            if not line.strip():
                continue
            name, _, when = line.partition("\t")
            out.append({"name": name.strip(), "when": int(when or 0)})
    return sorted(out, key=lambda b: (-b["when"], b["name"]))


def classify(branch, base, base_repo, ignore=DEFAULT_IGNORE):
    """One branch's changed paths, each LANDED / NEW / DIFFERS, plus its summary."""
    mb = git("merge-base", base, branch, cwd=base_repo, check=False)
    if not mb:
        return {"branch": branch, "error": "no merge-base with %s" % base, "paths": {},
                "unlanded": [], "differs": [], "spent": False}
    changed = [p for p in git("diff", "--name-only", mb, branch, cwd=base_repo).splitlines() if p]
    changed = [p for p in changed if not any(p.startswith(pre) for pre in ignore)]
    paths, unlanded, differs = {}, [], []
    for p in changed:
        on_base = subprocess.run(["git", "cat-file", "-e", "%s:%s" % (base, p)],
                                 cwd=base_repo, capture_output=True).returncode == 0
        if not on_base:
            verdict = NEW
        elif not git("diff", "--quiet", base, branch, "--", p, cwd=base_repo, check=False):
            verdict = LANDED
        else:
            verdict = DIFFERS
        paths[p] = verdict
        if verdict == NEW:
            unlanded.append(p)
        elif verdict == DIFFERS:
            differs.append(p)
    return {"branch": branch, "paths": paths, "unlanded": unlanded, "differs": differs,
            "spent": not unlanded and not differs}


def triage(base_repo, base="main", pattern=DEFAULT_PATTERN, include_remote=False,
           ignore=DEFAULT_IGNORE):
    branches = list_branches(base_repo, pattern, include_remote)
    return [classify(b["name"], base, base_repo, ignore) for b in branches]


def report(results, base="main"):
    spent = [r for r in results if r.get("spent")]
    with_new = [r for r in results if r.get("unlanded")]
    with_diff = [r for r in results if r.get("differs")]
    lines = ["%d draft branch(es) against %s: %d spent (nothing unlanded), %d carry content absent "
             "from %s, %d have a path that differs and needs judgement."
             % (len(results), base, len(spent), len(with_new), base, len(with_diff)), ""]
    for r in results:
        if r.get("error"):
            lines.append("  ? %s — %s" % (r["branch"], r["error"]))
            continue
        tag = "spent" if r["spent"] else ("land" if r["unlanded"] else "differs")
        lines.append("  [%s] %s" % (tag, r["branch"]))
        for p in r["unlanded"]:
            lines.append("      NEW      %s" % p)
        for p in r["differs"]:
            lines.append("      DIFFERS  %s" % p)
    if with_new:
        lines += ["", "Land these paths (content absent from %s); everything else is already there:"
                  % base]
        seen = []
        for r in with_new:
            for p in r["unlanded"]:
                if p not in seen:
                    seen.append(p)
                    lines.append("  %s   <- %s" % (p, r["branch"]))
    return "\n".join(lines)


def close_spent(results, base_repo):
    """Delete the branches holding nothing unlanded. Returns the names actually deleted."""
    deleted = []
    for r in results:
        if r.get("spent") and not r.get("error"):
            git("branch", "-D", r["branch"], cwd=base_repo)
            deleted.append(r["branch"])
    return deleted


def _commit(repo, msg):
    env = ["-c", "user.email=t@t", "-c", "user.name=t"]
    git(*env, "add", "-A", cwd=repo)
    git(*env, "commit", "-q", "-m", msg, cwd=repo)


def selftest():
    checks = []
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "r"
        repo.mkdir()
        git("init", "-q", "-b", "main", cwd=repo)
        (repo / "a.txt").write_text("1\n")
        (repo / "to-do-lists").mkdir()
        (repo / "to-do-lists" / "x.md").write_text("base\n")
        _commit(repo, "base")

        git("checkout", "-q", "-b", "drafts/tick-spent", cwd=repo)
        (repo / "to-do-lists" / "x.md").write_text("changed todo only\n")
        _commit(repo, "todo only")

        git("checkout", "-q", "main", cwd=repo)
        git("checkout", "-q", "-b", "drafts/tick-new", cwd=repo)
        (repo / "b.txt").write_text("brand new\n")
        _commit(repo, "adds b")

        git("checkout", "-q", "main", cwd=repo)
        git("checkout", "-q", "-b", "drafts/tick-diff", cwd=repo)
        (repo / "a.txt").write_text("2\n")
        (repo / "c.txt").write_text("also new\n")
        _commit(repo, "edits a, adds c")

        git("checkout", "-q", "main", cwd=repo)
        results = {r["branch"]: r for r in triage(str(repo))}
        checks.append(("three branches found", len(results) == 3))
        checks.append(("a todo-only branch is spent",
                       results["drafts/tick-spent"]["spent"]))
        checks.append(("a branch adding an absent path is unlanded (NEW not LANDED)",
                       results["drafts/tick-new"]["unlanded"] == ["b.txt"]))
        d = results["drafts/tick-diff"]
        checks.append(("a differing path is DIFFERS, not spent",
                       d["differs"] == ["a.txt"] and d["unlanded"] == ["c.txt"] and not d["spent"]))
        checks.append(("ignore list keeps the todo change out of the verdict",
                       "to-do-lists/x.md" not in results["drafts/tick-spent"]["paths"]))
        r = report(list(results.values()))
        checks.append(("the report names the landing target", "b.txt   <- drafts/tick-new" in r))
        deleted = close_spent(list(results.values()), str(repo))
        remaining = git("branch", "--format=%(refname:short)", cwd=repo).splitlines()
        checks.append(("close-spent deletes only the spent branch",
                       deleted == ["drafts/tick-spent"]
                       and "drafts/tick-spent" not in " ".join(remaining)
                       and "drafts/tick-new" in remaining))
    bad = [n for n, ok in checks if not ok]
    for n, ok in checks:
        print("%s %s" % ("PASS" if ok else "FAIL", n))
    print("all checks passed" if not bad else "%d failed" % len(bad))
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--base", default="main")
    ap.add_argument("--pattern", default=DEFAULT_PATTERN)
    ap.add_argument("--remote", action="store_true")
    ap.add_argument("--json", default=None)
    ap.add_argument("--close-spent", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    results = triage(args.repo, args.base, args.pattern, args.remote)
    if not results:
        print("no branches match %r against %s — nothing to triage" % (args.pattern, args.base))
        return 0
    print(report(results, args.base))
    if args.json:
        Path(args.json).write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
        print("\nwrote %s" % args.json)
    if args.close_spent:
        deleted = close_spent(results, args.repo)
        print("\ndeleted %d spent branch(es):" % len(deleted))
        for b in deleted:
            print("  - %s" % b)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
