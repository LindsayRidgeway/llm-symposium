#!/usr/bin/env python3
"""draft_gate_closer.py — decide which review-gate branches still matter, so the gate can close.

WHY THIS EXISTS.

The commons' wakes deliver their work to throwaway `drafts/tick-*` branches and *nothing merges
them* (channels/open-decisions.md, 2026-09-23: "the review gate has no closer"). The pile therefore
only grows, and every wake that reads a "path not on main" list cannot tell a genuinely stranded
artifact from one that landed six weeks ago under a different name. Ten of twenty wakes spent their
whole budget redoing work that already existed (the vulvodynia screen was written and recovered four
times). That is not a topic problem; it is a *decidability* problem. The gate has no closer because
nothing can answer, from disk, the one question a closer needs answered:

    for each draft branch, which of its files are NOT already on main?

This script answers exactly that, and nothing else. It is deliberately not a merger: merging needs a
checkout wired to the remote (the landing machine, per the reject queue), while the *decision* — what
to delete, what to carry, what is a duplicate — is pure local git and can be tested offline. So this
is the half of the closer a wake can build, and the half the landing machine was always waiting for.

THE RULE IT ENFORCES (and why it is not "mass-merge").

A file is NOT unlanded just because its path is absent from main. If the same bytes already sit on
main under *any* path, the content is landed and the branch is redundant: delete it. This is the
distinction that stops the two failure modes the commons has actually suffered — re-writing landed
work (because a path looked missing) and mass-merging duplicate trees (because a branch looked
unmerged). Content is compared by blob SHA, not by name.

    REDUNDANT branch  → every changed file's bytes already exist on the base → safe to delete.
    STRANDED branch   → at least one file whose bytes are on no path on the base → needs carrying.
    EMPTY branch      → no diff against the base at all.

USAGE.

    python3 scripts/draft_gate_closer.py                 # human table, current repo, base main
    python3 scripts/draft_gate_closer.py --json          # machine-readable plan
    python3 scripts/draft_gate_closer.py --check         # exit 1 if any branch is STRANDED (gating)
    python3 scripts/draft_gate_closer.py --apply-delete  # delete local REDUNDANT branches
    python3 scripts/draft_gate_closer.py --repo PATH --base origin/main --match 'drafts/tick-*'

In a wake checkout (`git remote -v` empty, only `main`) there are no draft refs, so the script prints
that plainly and exits 0 — which is itself the answer: nothing to close *here*. Run it where the
refs are (the landing machine, or any clone that has fetched `origin/drafts/*`).

Writes nothing unless `--apply-delete` is given, and that only ever deletes a branch whose every
changed byte is already on the base. It never touches a remote branch and never pushes.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from fnmatch import fnmatch

# Paths whose change on a draft branch is routine churn, never the artifact under review. A branch
# that changed only these is empty of *work* even though git reports a diff. (An amigo's own to-do
# file is the loudest example: every wake rewrites it, and a diff there means nothing was delivered.)
DEFAULT_IGNORE = [
    "to-do-lists/*",
    "tests/last-verification.txt",
    "channels/agenda.md",
    "channels/reports/*",
]

REDUNDANT = "REDUNDANT"
STRANDED = "STRANDED"
EMPTY = "EMPTY"


class GitError(RuntimeError):
    pass


def git(repo: str, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", repo, *args],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise GitError(f"git {' '.join(args)} failed: {proc.stderr.strip() or proc.stdout.strip()}")
    return proc.stdout


def resolve_base(repo: str, requested: str) -> str:
    """Prefer the requested base; fall back to origin/<base>, then <base>."""
    candidates = [requested] if "/" in requested else [requested, f"origin/{requested}"]
    for cand in candidates:
        try:
            git(repo, "rev-parse", "--verify", "--quiet", f"{cand}^{{commit}}")
            return cand
        except GitError:
            continue
    raise GitError(
        f"no base ref found: tried {', '.join(candidates)} (is this a repo with a main?)"
    )


def list_refs(repo: str, pattern: str) -> list[str]:
    out = git(
        repo,
        "for-each-ref",
        "--format=%(refname:short)",
        "--sort=refname",
        "refs/heads",
        "refs/remotes",
    )
    refs = []
    for line in out.splitlines():
        ref = line.strip()
        if ref.endswith("/HEAD"):
            continue
        if fnmatch(ref, pattern):
            refs.append(ref)
    return refs


def base_blob_set(repo: str, base: str) -> set[str]:
    out = git(repo, "ls-tree", "-r", base, "--format=%(objectname)")
    return {line.strip() for line in out.splitlines() if line.strip()}


def changed_paths(repo: str, base: str, ref: str) -> list[str]:
    out = git(repo, "diff", "--name-only", base, ref)
    return [p for p in out.splitlines() if p.strip()]


def blob_of(repo: str, ref: str, path: str) -> str | None:
    """Blob SHA of `path` at `ref`, or None if the path does not exist there (deleted in the ref)."""
    try:
        return git(repo, "rev-parse", f"{ref}:{path}").strip()
    except GitError:
        return None


@dataclass
class BranchReport:
    ref: str
    classification: str
    stranded: list[dict] = field(default_factory=list)
    redundant: list[str] = field(default_factory=list)
    ignored: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "ref": self.ref,
            "classification": self.classification,
            "stranded": self.stranded,
            "redundant": self.redundant,
            "ignored": self.ignored,
        }


def classify_branch(repo: str, base: str, ref: str, blobs_on_base: set[str], ignores: list[str]) -> BranchReport:
    report = BranchReport(ref=ref, classification=EMPTY)
    for path in changed_paths(repo, base, ref):
        if any(fnmatch(path, pat) for pat in ignores):
            report.ignored.append(path)
            continue
        sha = blob_of(repo, ref, path)
        if sha is None:
            # Present on base, deleted on the ref: a deletion is not unlanded work. Ignore it.
            continue
        if sha in blobs_on_base:
            report.redundant.append(path)
        else:
            report.stranded.append({"path": path, "blob": sha})
    if report.stranded:
        report.classification = STRANDED
    elif report.redundant or report.ignored:
        report.classification = REDUNDANT
    else:
        report.classification = EMPTY
    return report


def build_plan(repo: str, base: str, pattern: str, ignores: list[str]) -> dict:
    blobs_on_base = base_blob_set(repo, base)
    refs = list_refs(repo, pattern)
    reports = [classify_branch(repo, base, ref, blobs_on_base, ignores) for ref in refs]
    counts = {REDUNDANT: 0, STRANDED: 0, EMPTY: 0}
    for r in reports:
        counts[r.classification] += 1
    return {
        "repo": repo,
        "base": base,
        "match": pattern,
        "refs_found": len(refs),
        "counts": counts,
        "branches": [r.to_dict() for r in reports],
    }


def render_human(plan: dict) -> str:
    lines = []
    lines.append(
        f"draft gate — base {plan['base']}, pattern {plan['match']!r}: {plan['refs_found']} ref(s)"
    )
    if plan["refs_found"] == 0:
        lines.append(
            "  no draft refs in this checkout (no remote / nothing fetched) — nothing to close here."
        )
        return "\n".join(lines)
    c = plan["counts"]
    lines.append(f"  REDUNDANT (safe to delete): {c[REDUNDANT]}")
    lines.append(f"  STRANDED  (must be carried): {c[STRANDED]}")
    lines.append(f"  EMPTY     (no diff):         {c[EMPTY]}")
    lines.append("")
    for b in plan["branches"]:
        if b["classification"] == REDUNDANT:
            lines.append(f"[redundant] {b['ref']}  (delete; {len(b['redundant'])} file(s) already on base)")
        elif b["classification"] == EMPTY:
            lines.append(f"[empty]     {b['ref']}")
        else:
            lines.append(f"[STRANDED]  {b['ref']}  ({len(b['stranded'])} unlanded file(s))")
            for item in b["stranded"]:
                lines.append(f"              {item['blob'][:10]}  {item['path']}")
    return "\n".join(lines)


def is_local_branch(repo: str, ref: str) -> bool:
    """True only if `ref` names a local branch. A slash is not the test: `drafts/x` is local while
    `origin/drafts/x` is not, so ask git which namespace the name resolves into."""
    out = git(repo, "for-each-ref", "--format=%(refname)", f"refs/heads/{ref}")
    return f"refs/heads/{ref}" in out.split()


def apply_deletes(repo: str, plan: dict) -> list[str]:
    """Delete local branches whose every changed byte is already on the base. Never a remote ref."""
    deleted = []
    for b in plan["branches"]:
        ref = b["ref"]
        if b["classification"] != REDUNDANT:
            continue
        if not is_local_branch(repo, ref):
            # Remote-tracking refs are not ours to delete; report, do not act.
            continue
        git(repo, "branch", "-D", ref)
        deleted.append(ref)
    return deleted


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Decide which drafts/tick-* branches still hold unlanded work.")
    ap.add_argument("--repo", default=".", help="path to the git repository (default: cwd)")
    ap.add_argument("--base", default="main", help="base branch (default: main; falls back to origin/main)")
    ap.add_argument("--match", default="drafts/tick-*", help="fnmatch glob over ref short names")
    ap.add_argument("--ignore", action="append", default=None, help="extra routine-churn glob (repeatable)")
    ap.add_argument("--json", action="store_true", help="emit the plan as JSON")
    ap.add_argument("--check", action="store_true", help="exit 1 if any branch is STRANDED")
    ap.add_argument("--apply-delete", action="store_true", help="delete local REDUNDANT branches")
    args = ap.parse_args(argv)

    ignores = list(DEFAULT_IGNORE) + (args.ignore or [])
    try:
        base = resolve_base(args.repo, args.base)
        plan = build_plan(args.repo, base, args.match, ignores)
    except GitError as exc:
        print(f"draft gate: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(plan, indent=2, sort_keys=True))
    else:
        print(render_human(plan))

    if args.apply_delete:
        deleted = apply_deletes(args.repo, plan)
        untouched = [
            b["ref"]
            for b in plan["branches"]
            if b["classification"] == REDUNDANT and not is_local_branch(args.repo, b["ref"])
        ]
        if not args.json:
            print("")
            print(f"deleted {len(deleted)} local redundant branch(es): {', '.join(deleted) or '(none)'}")
            if untouched:
                print(
                    "left alone (remote-tracking; the landing machine must delete these): "
                    + ", ".join(untouched)
                )

    if args.check and plan["counts"][STRANDED] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
