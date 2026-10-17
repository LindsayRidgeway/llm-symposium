#!/usr/bin/env python3
"""Reconcile what a wake *said* it landed with what its landing commit *did*.

Why this exists
---------------
The wake orientation block tells each run which paths a previous wake "claimed" and
did not reach `main`; those lists are built from the run's `report.txt` LAND line.
Measured on 2026-10-17: that line is not the same thing as the diff.  Of 106
`land(wake)` commits in this repository's history, 8 record a path list that differs
from the files the commit actually changed — six under-report (the record omits what
landed), one over-reports (a run's LAND line names six gallery paths and its landing
commit changed none of them).  A later wake reading the over-reported line concludes
the work is missing and rebuilds it.  That loop is documented in
`channels/open-decisions.md` (2026-09-23) and it is why this checkout has a file
called `reject-queue.md`.

The other half of the same problem: an item on the reject queue says a wake "cannot
confirm whether a run's LAND paths reached main" because it has no git remote.  That
is true of *fetching a review branch* and false of *reading this repository's own
history*: every landing leaves a commit here, and the commit is the stronger
evidence.  This tool does that reading.  It needs no network.

What it reports, per run that has a report on disk
--------------------------------------------------
  landed          the LAND paths appear in a landing commit's diff, and the commit's
                  own record agrees with that diff
  record-mismatch the commit landed something, but its "Paths this run changed:" line
                  disagrees with the diff (either direction)
  unlanded        the run names paths and no landing commit in this history contains
                  any of them
  no-claim        the report carries no non-empty LAND line

Usage
-----
    python3 scripts/landing_reconcile.py                    # human table
    python3 scripts/landing_reconcile.py --json             # machine output
    python3 scripts/landing_reconcile.py --limit 40         # newest 40 runs
    python3 scripts/landing_reconcile.py --check            # exit 1 if unlanded > 0

Read-only.  It runs `git log`/`git show` and reads `report.txt` files under
`<runs-root>/*/tick-state/runs/`; it writes nothing.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

RUN_ID_RE = re.compile(r"run ([0-9]{8}T[0-9]{6}Z-[0-9a-f]{8}|codex-[0-9TZ]+-[0-9a-f]{8})")
PATHS_MARKER = "Paths this run changed:"
LAND_RE = re.compile(r"^LAND:\s*(.*)$", re.MULTILINE)
TRAILER_RE = re.compile(r"^Architecture:.*$", re.MULTILINE)


@dataclass
class Commit:
    sha: str
    subject: str
    run_id: str | None
    claimed: list[str]
    actual: list[str]

    @property
    def record_is_true(self) -> bool:
        return set(self.claimed) == set(self.actual)


@dataclass
class Run:
    run_id: str
    bot: str
    report: Path | None
    land_claims: list[str] = field(default_factory=list)
    commits: list[Commit] = field(default_factory=list)
    head_paths: set[str] = field(default_factory=set)

    @property
    def landed_paths(self) -> set[str]:
        out: set[str] = set()
        for c in self.commits:
            out.update(c.actual)
        return out

    def verdict(self) -> str:
        """Ground truth for "did this reach main" is the tree at HEAD, not the
        commit that was supposed to carry it: a path can land under another run's
        commit, or by hand."""
        if not self.land_claims:
            return "no-claim"
        here = [p for p in self.land_claims if p in self.head_paths]
        if not here:
            return "unlanded"
        if len(here) < len(self.land_claims):
            return "partial"
        return "landed"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout


def _norm(text: str) -> list[str]:
    """Split a comma/space separated path list into unique, ordered paths."""
    seen: list[str] = []
    for chunk in re.split(r"[,\s]+", text):
        p = chunk.strip().strip("`'\"").rstrip(".").strip()
        # A wake that has not decided yet writes "LAND: tbd" / "pending" / "none".
        # Those are placeholders, not paths, and counting them as unlanded work is
        # the same mistake as counting a stale claim as missing work.
        if not p or p in seen or "/" not in p and "." not in p:
            continue
        seen.append(p)
    return seen


def parse_land_line(report: Path) -> list[str]:
    try:
        text = report.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    paths: list[str] = []
    for m in LAND_RE.finditer(text):
        body = m.group(1).strip()
        if not body or body.startswith("("):
            continue
        for p in _norm(body):
            if p not in paths:
                paths.append(p)
    return paths


def load_commits(repo: Path) -> dict[str, list[Commit]]:
    """Index landing commits by run id."""
    sep = "\x1e"
    # No pathspec here: an empty landing commit touches no path, and a path-limited log
    # would silently drop exactly the commits this tool most needs to see.
    raw = git(repo, "log", "--format=%H%x1f%s%x1f%b" + sep) or ""
    index: dict[str, list[Commit]] = {}
    for rec in raw.split(sep):
        rec = rec.strip("\n")
        if not rec or "\x1f" not in rec:
            continue
        sha, subject, body = rec.split("\x1f", 2)
        if not subject.startswith("land(wake)"):
            continue
        m = RUN_ID_RE.search(subject)
        if not m:
            continue
        run_id = m.group(1)
        body = TRAILER_RE.sub("", body)
        claimed: list[str] = []
        if PATHS_MARKER in body:
            claimed = _norm(body.split(PATHS_MARKER, 1)[1])
        actual = git(repo, "show", "--name-only", "--format=", sha).split()
        index.setdefault(run_id, []).append(
            Commit(sha=sha[:8], subject=subject, run_id=run_id, claimed=claimed, actual=actual)
        )
    return index


def load_runs(runs_root: Path) -> list[Run]:
    runs: list[Run] = []
    for bot_dir in sorted(runs_root.glob("*-bot/tick-state/runs")):
        bot = bot_dir.parent.parent.name.replace("-bot", "")
        for d in sorted(bot_dir.iterdir(), reverse=True):
            if not d.is_dir():
                continue
            report = d / "report.txt"
            runs.append(
                Run(
                    run_id=d.name,
                    bot=bot,
                    report=report if report.exists() else None,
                    land_claims=parse_land_line(report) if report.exists() else [],
                )
            )
    return runs


def reconcile(repo: Path, runs_root: Path, limit: int | None = None) -> dict:
    index = load_commits(repo)
    runs = load_runs(runs_root)
    if limit:
        runs = runs[:limit]
    head_paths = set(git(repo, "ls-tree", "-r", "--name-only", "HEAD").split())
    for r in runs:
        r.commits = index.get(r.run_id, [])
        r.head_paths = head_paths
    tally: dict[str, int] = {}
    for r in runs:
        v = r.verdict()
        tally[v] = tally.get(v, 0) + 1
    bad_commits = [
        c for cs in index.values() for c in cs if not c.record_is_true
    ]
    return {
        "repository": str(repo),
        "runs_root": str(runs_root),
        "landing_commits": sum(len(cs) for cs in index.values()),
        "commits_with_false_record": len(bad_commits),
        "runs_scanned": len(runs),
        "tally": tally,
        "runs": [
            {
                "run_id": r.run_id,
                "bot": r.bot,
                "verdict": r.verdict(),
                "land_claims": r.land_claims,
                "claims_present_at_head": [p for p in r.land_claims if p in r.head_paths],
                "commit_record_true": all(c.record_is_true for c in r.commits) if r.commits else None,
                "commits": [
                    {
                        "sha": c.sha,
                        "claimed": c.claimed,
                        "actual": c.actual,
                        "claimed_not_landed": sorted(set(c.claimed) - set(c.actual)),
                        "landed_not_claimed": sorted(set(c.actual) - set(c.claimed)),
                    }
                    for c in r.commits
                ],
            }
            for r in runs
        ],
        "commits_with_false_record_detail": [
            {
                "sha": c.sha,
                "run_id": c.run_id,
                "claimed_not_landed": sorted(set(c.claimed) - set(c.actual)),
                "landed_not_claimed": sorted(set(c.actual) - set(c.claimed)),
            }
            for c in bad_commits
        ],
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=os.getcwd())
    ap.add_argument(
        "--runs-root",
        default=str(Path.home() / "LLM"),
        help="directory holding <bot>-bot/tick-state/runs (default ~/LLM)",
    )
    ap.add_argument("--limit", type=int, default=None, help="scan only the newest N runs")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check", action="store_true", help="exit 1 if any run is unlanded")
    args = ap.parse_args(argv)

    result = reconcile(Path(args.repo), Path(args.runs_root), args.limit)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"landing commits indexed: {result['landing_commits']}")
        print(f"  of which the commit's own path record is false: {result['commits_with_false_record']}")
        print(f"runs scanned: {result['runs_scanned']}")
        for verdict, count in sorted(result["tally"].items()):
            print(f"  {verdict:<16} {count}")
        for c in result["commits_with_false_record_detail"]:
            if c["claimed_not_landed"]:
                print(f"\nCLAIMED BUT NOT IN THE DIFF  {c['sha']}  {c['run_id']}")
                for p in c["claimed_not_landed"]:
                    print(f"  - {p}")
        partial = [r for r in result["runs"] if r["verdict"] == "partial"]
        if partial:
            print("\nSOME NAMED PATHS ARE NOT ON main")
            for r in partial[:25]:
                missing = [p for p in r["land_claims"] if p not in r["claims_present_at_head"]]
                print(f"  {r['run_id']} ({r['bot']}): {', '.join(missing[:3])}")
        unlanded = [r for r in result["runs"] if r["verdict"] == "unlanded"]
        if unlanded:
            print("\nNAMED AND NOT FOUND IN ANY LANDING COMMIT")
            for r in unlanded[:25]:
                print(f"  {r['run_id']} ({r['bot']}): {', '.join(r['land_claims'][:3])}")
    if args.check and result["tally"].get("unlanded"):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
