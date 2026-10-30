#!/usr/bin/env python3
"""Lint the *evidence* a review item cites, before a reviewer is asked to look at it.

Why this exists
---------------
Measured 2026-10-20 (Desi, wake 20261020T031124Z-2689e5c9). Three of the five items waiting
on one reviewer named, between them, `channels/items.jsonl` and `channels/tasks.md` as
evidence. Both files exist in every checkout at every moment, so "the path is present" is
true of every item that ever cites them — the check cannot fail, which means it is not a
check. One of those items (20261018T231750Z-159156aa) claimed in its report to have written a
request into the repository; the paths were present, the request was not, and only a
repository-wide grep could tell the difference.

What it computes, per cited path
--------------------------------
    own      a commit after the item was filed, touching this path, whose message names the
             item's own run (or the commit sha in its evidence) — the run's own landing
    created  a real addition is recorded near/after filing, with no earlier addition, but
             no matching run identifier: a temporal candidate, not authorship evidence
    other    the path existed before filing and was touched after it, but by a landing that
             names a different run — presence says something happened, not that *this* run
             happened
    standing the path existed before filing and nothing has touched it since: its presence
             is evidence of nothing at all
    missing  the path is absent from the checkout's committed HEAD
    unknown  missing filing time, shallow history, or no recorded addition to compare

Only `own` is strong evidence for this run. A `created` path remains available to inspect,
but timing alone cannot distinguish two runs. History is restricted to committed HEAD's
ancestry; another branch's work and an untracked file cannot establish delivery here.

It does not judge whether the work was any good — a reviewer still has to read the report. It
judges whether the item gives that reviewer anything that can fail.

Usage
-----
    python3 scripts/item_evidence_lint.py                # waiting items only
    python3 scripts/item_evidence_lint.py --all          # include items already exited
    python3 scripts/item_evidence_lint.py --json         # machine-readable
    python3 scripts/item_evidence_lint.py --repo DIR     # lint another checkout

Exit codes
----------
    0  every waiting item cites at least one `own` path
    1  at least one waiting item lacks an attributable committed path
    2  the question could not be answered (no git history, unreadable ledger) — the tool says
       "cannot see" rather than reporting a clean bill of health
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

# Slack between a run filing an item and the landing that creates its files: a run that
# starts at T can be landed hours later, so "existed before T - GRACE" means before the run.
GRACE = timedelta(hours=6)

RUN_ID = re.compile(r"\d{8}T\d{6}Z-[0-9a-f]{6,12}")
SHA = re.compile(r"\b[0-9a-f]{7,40}\b")

# Reported for legibility only; every verdict is computed from git, never from this list.
STANDING_HINT = {
    "channels/items.jsonl",
    "channels/tasks.md",
    "channels/agenda.md",
    "channels/open-decisions.md",
    "channels/reject-queue.md",
    "channels/risks.md",
    "scripts/README.md",
}


def _parse_ts(value: str) -> datetime:
    """Parse an item's `filed_utc` (2026-10-18T15:16:57Z) or a plain date."""
    text = value.strip().replace("Z", "+00:00")
    if len(text) == 10:
        text += "T00:00:00+00:00"
    stamp = datetime.fromisoformat(text)
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    return stamp


def _iso(when: datetime) -> str:
    return when.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _git(args: list[str], repo: str) -> str:
    result = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def is_git_checkout(repo: str) -> bool:
    try:
        return _git(["rev-parse", "--is-inside-work-tree"], repo) == "true"
    except (RuntimeError, FileNotFoundError):
        return False


def evidence_tokens(item: dict) -> list[str]:
    """The identifiers a landing commit would carry if this run had really landed the path."""
    text = " ".join(str(item.get(k) or "") for k in ("evidence", "id", "amigo"))
    tokens = set(RUN_ID.findall(text))
    tokens.update(match for match in SHA.findall(text) if len(match) >= 7)
    return sorted(tokens)


def commits_touching(path: str, since: datetime | None, repo: str) -> list[str]:
    args = ["log", "--format=%H %s"]
    if since is not None:
        args.append(f"--since={_iso(since)}")
    args += ["HEAD", "--", ":(literal)" + path]
    out = _git(args, repo)
    return [line for line in out.splitlines() if line.strip()]


def created_before(path: str, when: datetime, repo: str) -> bool:
    out = _git(
        [
            "log",
            f"--before={_iso(when - GRACE)}",
            "--diff-filter=A",
            "--format=%H",
            "-1",
            "HEAD",
            "--",
            ":(literal)" + path,
        ],
        repo,
    )
    return bool(out)


def path_tier(path: str, when: datetime | None, tokens: list[str], repo: str = ".") -> str:
    """Classify committed evidence without treating missing history as a creation event."""
    if when is None:
        return "unknown"
    if _git(["rev-parse", "--is-shallow-repository"], repo) == "true":
        return "unknown"
    present = _git(["ls-tree", "--full-tree", "--name-only", "HEAD", "--",
                    ":(literal)" + path], repo)
    if path not in present.splitlines():
        return "missing"
    recent = commits_touching(path, when, repo)
    for line in recent:
        if any(token in line for token in tokens):
            return "own"
    if not created_before(path, when, repo):
        additions = _git(["log", "--diff-filter=A", f"--since={_iso(when - GRACE)}",
                          "--format=%H", "HEAD", "--", ":(literal)" + path], repo)
        return "created" if additions else "unknown"
    return "other" if recent else "standing"


def load_latest(items_path: str) -> list[dict]:
    """items.jsonl is append-only; the last row for an id is its current state."""
    latest: dict[str, dict] = {}
    order: list[str] = []
    with open(items_path, encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                raise ValueError(f"line {lineno}: malformed ledger JSON") from None
            if not isinstance(row, dict):
                raise ValueError(f"line {lineno}: ledger row must be an object")
            item_id = row.get("id")
            if not isinstance(item_id, str) or not item_id.strip():
                raise ValueError(f"line {lineno}: ledger row requires a nonempty string id")
            if row.get("filed_utc") is not None and not isinstance(row["filed_utc"], str):
                raise ValueError(f"line {lineno}: filed_utc must be a string or null")
            if row.get("paths") is not None and (not isinstance(row["paths"], list)
                    or not all(isinstance(path, str) for path in row["paths"])):
                raise ValueError(f"line {lineno}: paths must be a list of strings or null")
            if item_id not in latest:
                order.append(item_id)
            latest[item_id] = row
    if not latest:
        raise ValueError("ledger contains no item rows")
    return [latest[item_id] for item_id in order]


def classify(item: dict, repo: str = ".") -> dict:
    """Find paths attributable to the run; an unattributed addition is not a strong path."""
    filed = item.get("filed_utc")
    when = _parse_ts(filed) if filed else None
    tokens = evidence_tokens(item)
    paths = [path for path in (item.get("paths") or []) if isinstance(path, str)]
    tiers = {path: path_tier(path, when, tokens, repo) for path in paths}
    strong = [path for path, tier in tiers.items() if tier == "own"]
    return {
        "id": item.get("id"),
        "title": (item.get("short_title") or item.get("title") or "")[:70],
        "assigned_to": item.get("assigned_to"),
        "state": item.get("state"),
        "filed_utc": filed,
        "paths": paths,
        "tiers": tiers,
        "strong": strong,
        "falsifiable": bool(strong),
    }


def lint(items: list[dict], repo: str = ".", include_all: bool = False) -> dict:
    """Classify every item, then keep the ones still waiting unless include_all is set."""
    verdicts = [classify(item, repo) for item in items]
    if not include_all:
        verdicts = [verdict for verdict in verdicts if not verdict["state"]]
    return {
        "checked": len(verdicts),
        "falsifiable": sum(1 for verdict in verdicts if verdict["falsifiable"]),
        "unfalsifiable": [verdict for verdict in verdicts if not verdict["falsifiable"]],
        "no_paths": [verdict for verdict in verdicts if not verdict["paths"]],
        "verdicts": verdicts,
    }


def render(result: dict) -> str:
    lines = [
        f"item evidence: {result['checked']} checked, {result['falsifiable']} cite a path that is "
        f"the run's own, {len(result['unfalsifiable'])} waiting item(s) lack an attributable "
        f"committed path (inspect their tiers; timing alone is not authorship)"
    ]
    for verdict in result["no_paths"]:
        lines.append(f"  NO PATHS {verdict['id']}  {verdict['title']}")
    for verdict in result["unfalsifiable"]:
        lines.append(f"  UNFALSIFIABLE {verdict['id']}  {verdict['title']}")
        lines.append(
            f"    assigned to: {verdict['assigned_to'] or '-'}   filed: {verdict['filed_utc']}"
        )
        for path in verdict["paths"]:
            lines.append(f"    {verdict['tiers'][path]:>8}  {path}")
        if not verdict["paths"]:
            lines.append("    (cites no paths at all)")
    if result["unfalsifiable"]:
        lines.append(
            "  For these, presence cannot separate delivered work from a run that wrote its "
            "report and stopped."
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=".", help="checkout to lint against (default: .)")
    parser.add_argument("--items", default=None, help="path to items.jsonl")
    parser.add_argument("--all", action="store_true", help="include items already exited")
    parser.add_argument("--json", action="store_true", help="print JSON instead of a report")
    args = parser.parse_args(argv)

    repo = os.path.abspath(args.repo)
    items_path = args.items or os.path.join(repo, "channels", "items.jsonl")
    if not os.path.exists(items_path):
        print(f"item_evidence_lint: cannot see {items_path}", file=sys.stderr)
        return 2
    if not is_git_checkout(repo):
        print(f"item_evidence_lint: cannot see git history in {repo} — no verdict", file=sys.stderr)
        return 2

    try:
        result = lint(load_latest(items_path), repo, include_all=args.all)
    except (OSError, UnicodeError, ValueError, RuntimeError) as error:
        print(f"item_evidence_lint: cannot see reliable evidence: {error}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render(result))
    return 1 if result["unfalsifiable"] else 0


if __name__ == "__main__":
    sys.exit(main())
