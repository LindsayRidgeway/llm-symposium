#!/usr/bin/env python3
"""Triage the `drafts/tick-*` review pile against `main`.

Why this exists (2026-10-08, Dmitri). The review gate was introduced so a wake
that changed files would deliver them "to a draft branch for review". Nothing
ever merged those branches, so the pile grew — one branch per rough wake, ~99
open as of 2026-10-05 — and later wakes kept recovering work that already sat on
a review branch. The missing piece is not more review; it is a *closer*: a
mechanical way to say, for each branch, whether it holds anything genuinely
absent from `main` (merge it) or is only state churn / already landed (close it).

A wake runs in a checkout with no git remote, so it cannot fetch the pile — this
tool does not fetch, it inspects whatever refs a checkout already holds. Run it
on the landing machine (the checkout wired to `origin`) and it prints a decision
per branch, so draining the pile stops being a judgement call.

The set of paths to judge is the branch's own contribution since its fork point
(`base...branch`, a three-dot diff), then each path is checked against the base
tree by content:

    LANDED     base has the file with identical bytes -> already on main, nothing to do
    UNLANDED   branch has the file, base does not     -> a merge candidate
    DIVERGENT  both have the file, bytes differ       -> needs a human eye
    REMOVED    branch removed a file base still has   -> the removal did not land

A branch is CLOSE when every changed path is either LANDED, REMOVED, or on a
state-only path (to-do lists, the telegram/conversation logs, the generated
agenda/ledger files — churn, not artifact). It is REVIEW when at least one
non-state path is UNLANDED or DIVERGENT. It is EMPTY when it changes nothing.

Usage:
  python3 scripts/draft_triage.py [--repo PATH] [--base main]
                                  [--pattern 'drafts/tick-*'] [--json]
                                  [--fail-on-review]

Exit status is 0 unless git itself fails; with --fail-on-review it is 1 when any
branch is REVIEW (so a caller can gate on "the pile still needs a closer").
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Paths whose change is coordination/state churn, never an artifact worth
# merging by itself. Prefixes match on the whole path; exact names match whole.
STATE_ONLY_PREFIXES = (
    "to-do-lists/",
    "channels/telegram/",
    "channels/conversation/",
    "channels/outbound/",
    "runs/",
)
STATE_ONLY_NAMES = {
    "channels/agenda.md",
    "channels/notes-to-self.md",
    "channels/tasks.md",
    "channels/reject-queue.md",
    "channels/risks.md",
    "channels/open-decisions.md",
}

LANDED = "LANDED"
UNLANDED = "UNLANDED"
DIVERGENT = "DIVERGENT"
REMOVED = "REMOVED"
ACTIONABLE = (UNLANDED, DIVERGENT)


@dataclass
class PathChange:
    status: str  # git name-status letter, e.g. A/M/D
    path: str
    verdict: str
    state_only: bool

    @property
    def actionable(self) -> bool:
        return self.verdict in ACTIONABLE and not self.state_only


@dataclass
class BranchTriage:
    branch: str
    changes: list[PathChange] = field(default_factory=list)

    @property
    def actionable(self) -> list[PathChange]:
        return [c for c in self.changes if c.actionable]

    @property
    def verdict(self) -> str:
        if not self.changes:
            return "EMPTY"
        return "REVIEW" if self.actionable else "CLOSE"


def is_state_only(path: str) -> bool:
    if path in STATE_ONLY_NAMES:
        return True
    return any(path.startswith(p) for p in STATE_ONLY_PREFIXES)


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
    )
    if check and proc.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed ({proc.returncode}): {proc.stderr.strip()}"
        )
    return proc


def rev_parse(repo: Path, spec: str) -> str | None:
    """Blob/commit hash for a revision spec, or None if it does not resolve."""
    proc = _git(repo, "rev-parse", "--verify", "--quiet", spec, check=False)
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def changed_paths(repo: Path, base: str, branch: str) -> list[tuple[str, str]]:
    """(status, path) for every path the branch contributes since its fork point.

    Three-dot (`base...branch`) means "what the branch changed since the merge
    base", which is the right question: we want the branch's own contribution,
    not paths where main has since moved on for unrelated reasons. When the two
    histories are unrelated (no merge base) we fall back to a plain tree diff.
    Renames are reported by their new path.
    """
    three_dot = _git(repo, "diff", "--name-status", f"{base}...{branch}", check=False)
    if three_dot.returncode != 0:
        three_dot = _git(repo, "diff", "--name-status", base, branch, check=False)
    rows: list[tuple[str, str]] = []
    for line in three_dot.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status = parts[0]
        path = parts[-1]  # for R/C the new path is last
        rows.append((status, path))
    return rows


def classify_path(repo: Path, base: str, branch: str, status: str, path: str) -> PathChange:
    in_base = rev_parse(repo, f"{base}:{path}")
    in_branch = rev_parse(repo, f"{branch}:{path}")
    if in_branch is None:
        verdict = REMOVED
    elif in_base is None:
        verdict = UNLANDED
    elif in_base == in_branch:
        verdict = LANDED
    else:
        verdict = DIVERGENT
    return PathChange(status=status, path=path, verdict=verdict, state_only=is_state_only(path))


def triage_branch(repo: Path, base: str, branch: str) -> BranchTriage:
    result = BranchTriage(branch=branch)
    for status, path in changed_paths(repo, base, branch):
        result.changes.append(classify_path(repo, base, branch, status, path))
    return result


def list_branches(repo: Path, pattern: str) -> list[str]:
    """Local + remote-tracking branch names matching `pattern`, deduped, sorted.

    A remote-tracking `origin/drafts/tick-x` and a local `drafts/tick-x` name the
    same work; prefer the remote-tracking ref (that is what the pile actually is)
    and drop the local duplicate so a branch is reported once.
    """
    out = _git(
        repo,
        "for-each-ref",
        "--format=%(refname:short)",
        "refs/heads",
        "refs/remotes",
    ).stdout
    seen_local: set[str] = set()
    seen_remote: set[str] = set()
    for name in out.splitlines():
        name = name.strip()
        if not name or name.endswith("/HEAD"):
            continue
        if not fnmatch.fnmatch(name, pattern):
            continue
        if name.startswith("origin/"):
            seen_remote.add(name[len("origin/"):])
        else:
            seen_local.add(name)
    result: list[str] = []
    for local in seen_local:
        result.append(f"origin/{local}" if local in seen_remote else local)
    for remote in seen_remote:
        if remote not in seen_local:
            result.append(f"origin/{remote}")
    return sorted(result)


def triage(repo: Path, base: str, pattern: str) -> list[BranchTriage]:
    return [triage_branch(repo, base, b) for b in list_branches(repo, pattern)]


def render_markdown(results: list[BranchTriage], base: str) -> str:
    lines: list[str] = []
    total = len(results)
    review = [r for r in results if r.verdict == "REVIEW"]
    close = [r for r in results if r.verdict == "CLOSE"]
    empty = [r for r in results if r.verdict == "EMPTY"]
    lines.append(f"# Draft-branch triage vs `{base}`")
    lines.append("")
    lines.append(
        f"{total} branch(es): {len(review)} REVIEW, {len(close)} CLOSE, {len(empty)} EMPTY."
    )
    lines.append("")
    for r in results:
        lines.append(f"## `{r.branch}` — {r.verdict}")
        if not r.changes:
            lines.append("- (no changes vs base)")
            lines.append("")
            continue
        for c in r.changes:
            tag = f"{c.verdict}{' (state-only)' if c.state_only else ''}"
            lines.append(f"- `{c.path}` — {c.status} — {tag}")
        lines.append("")
    return "\n".join(lines)


def to_json(results: list[BranchTriage], base: str) -> str:
    payload = {
        "base": base,
        "branches": [
            {
                "branch": r.branch,
                "verdict": r.verdict,
                "actionable": len(r.actionable),
                "changes": [
                    {
                        "path": c.path,
                        "status": c.status,
                        "verdict": c.verdict,
                        "state_only": c.state_only,
                    }
                    for c in r.changes
                ],
            }
            for r in results
        ],
    }
    return json.dumps(payload, indent=2)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", default=".", help="checkout holding the draft refs (default: .)")
    parser.add_argument("--base", default="main", help="base ref to compare against (default: main)")
    parser.add_argument("--pattern", default="drafts/tick-*", help="branch glob (default: drafts/tick-*)")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    parser.add_argument(
        "--fail-on-review",
        action="store_true",
        help="exit 1 if any branch needs review (default: always exit 0)",
    )
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve()
    if rev_parse(repo, args.base) is None:
        print(f"base ref `{args.base}` does not resolve in {repo}", file=sys.stderr)
        return 2

    results = triage(repo, args.base, args.pattern)
    if args.json:
        print(to_json(results, args.base))
    else:
        print(render_markdown(results, args.base))

    if args.fail_on_review and any(r.verdict == "REVIEW" for r in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
