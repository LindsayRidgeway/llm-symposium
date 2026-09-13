#!/usr/bin/env python3
"""Validate autonomous Goose diffs before opening a PR.

This is intentionally conservative. The autonomous Tarik workflow is allowed to
experiment, but it should not create review noise for state-only churn, generic
appendices to old reviews, or unpublished miscellany under docs/papers/.

Usage:
  python3 scripts/validate_autonomous_diff.py [--repo PATH] [--name-status FILE]

If --name-status is omitted, the script inspects the current git worktree using
`git diff --name-status` plus untracked files. Exit status 0 means a PR may be
opened; exit status 1 means upload logs but do not open a PR.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

STATE_ONLY = {
    "channels/agenda.md",
    "channels/notes-to-self.md",
    "to-do-lists/tarik.md",
}

AUTONOMOUS_IMPL = {
    ".github/workflows/autonomous-goose-tarik.yml",
    "recipes/autonomous-goose/tarik.yaml",
    "recipes/autonomous-goose/tarik-mission.md",
    "scripts/validate_autonomous_diff.py",
    "tests/test_validate_autonomous_diff.py",
}

DATED_DISCUSSION = re.compile(r"^discussions/\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*\.md$")
DATED_GOVERNANCE = re.compile(r"^governance/\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*\.md$")
DATED_EXPERIMENT = re.compile(r"^experiments/\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*\.(md|py|json)$")


def _run(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True)


def current_changes(repo: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for line in _run(repo, "diff", "--name-status").splitlines():
        if not line.strip():
            continue
        status, path = line.split("\t", 1)
        rows.append((status, path))
    for path in _run(repo, "ls-files", "--others", "--exclude-standard").splitlines():
        if path.strip():
            rows.append(("A", path.strip()))
    return rows


def parse_name_status(text: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for raw in text.splitlines():
        if not raw.strip():
            continue
        parts = raw.split("\t")
        if len(parts) < 2:
            rows.append(("?", raw.strip()))
        else:
            rows.append((parts[0], parts[-1]))
    return rows


def _has_required_metadata(repo: Path, path: str) -> bool:
    try:
        text = (repo / path).read_text(encoding="utf-8")
    except OSError:
        return False
    head = text[:1200]
    return (
        len(text.strip()) >= 1200
        and "**Author:" in head
        and "**Date:" in head
        and "**Status:" in head
        and "Suggested Improvements" not in head
    )


def is_substantive(repo: Path, status: str, path: str) -> bool:
    if path in AUTONOMOUS_IMPL:
        return True
    if path in STATE_ONLY:
        return False

    # New dated arguments/experiments may open PRs, but old discussion edits and
    # undated docs/papers markdown do not. This blocks the observed failure mode:
    # a generic appendix to an old review or a loose docs/papers/*.md note.
    if DATED_DISCUSSION.match(path) or DATED_GOVERNANCE.match(path):
        return status == "A" and _has_required_metadata(repo, path)
    if DATED_EXPERIMENT.match(path):
        return status == "A"

    # Implementation work is allowed when it touches code/tests or the live site.
    if path.startswith(("scripts/", "tests/", "probes/")):
        return True
    if path.startswith("docs/music/"):
        return True
    if path.startswith("docs/papers/") and path.endswith(".html"):
        return True

    return False


def validate(repo: Path, changes: list[tuple[str, str]]) -> tuple[bool, list[str]]:
    if not changes:
        return False, ["no changed files"]
    substantive = [path for status, path in changes if is_substantive(repo, status, path)]
    if not substantive:
        return False, [
            "no substantive artifact path found",
            "state/coordination-only or generic artifact changes are not enough to open a PR",
        ]
    return True, ["substantive artifact(s): " + ", ".join(substantive)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--name-status")
    args = parser.parse_args(argv)
    repo = Path(args.repo).resolve()

    if args.name_status:
        changes = parse_name_status(Path(args.name_status).read_text(encoding="utf-8"))
    else:
        changes = current_changes(repo)

    ok, messages = validate(repo, changes)
    for status, path in changes:
        print(f"{status}\t{path}")
    for msg in messages:
        print(msg)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
