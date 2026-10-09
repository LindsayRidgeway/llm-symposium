#!/usr/bin/env python3
# Owner: Desi (land_runs.py subsystem). Filed with risk R-009, 2026-10-09.
"""Preflight: will the shared checkout accept a wake's landing?

Why this exists (2026-10-09). `land_runs.py` lands a wake's work into the shared
checkout `~/LLM/llm-symposium` only when that checkout has no *foreign* dirt — an
uncommitted change that is neither a test-regenerated index (`GENERATED`) nor the
live-chat record (`channels/conversation/`, `channels/telegram/`). When foreign dirt
is present it returns `refused_dirty_tree: <path>` and the run's work is diverted to a
`drafts/tick-*` branch instead of reaching `main`.

That refusal is usually attributable to one file, and the cost is not one landing:
measured on 2026-10-09, the shared checkout held exactly one dirty path
(`insights/2026-09-09-rover-build-03-manual-transcription.md`, +73 lines, absent from
`main`), **46 of the 80** `refused_dirty_tree` lines in `~/LLM/desi-bot/bot.log` named
that same file, and **all eight** landings that day were refused. Every refused landing
is a branch piled onto the review gate, so the gate's backlog accumulates from a single
failing check (channels/risks.md R-009).

The landing tool reports the refusal *after* the fact. This reports the same condition
*before* one, so a wake can see that the checkout is blocked — and who unblocks it —
rather than only the pile of drafts that follow.

Usage:
  python3 scripts/landing_preflight.py                 # the shared checkout, if found
  python3 scripts/landing_preflight.py --repo <dir>    # an explicit checkout
  python3 scripts/landing_preflight.py --json          # machine-readable

Exit status: 0 = a landing would be accepted; 1 = it would be refused (foreign dirt);
2 = the given path is not a git work tree.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# Kept in step with land_runs.py by hand: these are the only two categories of dirt
# that the landing tool tolerates. Drift here can only make this preflight *stricter*
# than the tool (it would flag a benign path as foreign), never looser, so the failure
# direction is safe.
GENERATED = {
    "scripts/README.md",
    "channels/agenda.md",
    "context/context-digest.md",
    "discussions/README.md",
}
RECORD_PREFIXES = ("channels/conversation/", "channels/telegram/")

DEFAULT_REPO = Path.home() / "LLM" / "llm-symposium"


def _git(args, cwd):
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True
    )


def is_work_tree(repo: Path) -> bool:
    if not (repo / ".git").exists():
        return False
    return _git(["rev-parse", "--is-inside-work-tree"], repo).stdout.strip() == "true"


def dirty_paths(repo: Path) -> list[str]:
    """Uncommitted paths: unstaged, staged, and untracked, de-duplicated in order.

    Mirrors `land_runs.py`'s `dirty_paths`, and for the same reason: slicing
    `git status --porcelain` at column 3 eats the leading space of the first line and
    yields a misnamed path. Three explicit commands have no such corner.
    """
    seen: list[str] = []
    for args in (
        ("diff", "--name-only"),
        ("diff", "--cached", "--name-only"),
        ("ls-files", "--others", "--exclude-standard"),
    ):
        for path in _git(args, repo).stdout.splitlines():
            path = path.strip()
            if path and path not in seen:
                seen.append(path)
    return seen


def classify(paths) -> dict[str, list[str]]:
    """Group dirty paths into record / generated / foreign.

    `foreign` is what the landing tool refuses on; empty foreign means a landing
    would be accepted.
    """
    record, generated, foreign = [], [], []
    for p in paths:
        if p.startswith(RECORD_PREFIXES):
            record.append(p)
        elif p in GENERATED:
            generated.append(p)
        else:
            foreign.append(p)
    return {"record": record, "generated": generated, "foreign": foreign}


def resolve_repo(explicit: str | None) -> Path | None:
    if explicit:
        return Path(explicit).expanduser()
    env = os.environ.get("LLM_SYMPOSIUM_REPO")
    if env:
        return Path(env).expanduser()
    return DEFAULT_REPO


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", help="path to the shared checkout (default: %s)" % DEFAULT_REPO)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    repo = resolve_repo(args.repo)
    if repo is None or not is_work_tree(repo):
        print(f"landing_preflight: not a git work tree: {repo}", file=sys.stderr)
        return 2

    groups = classify(dirty_paths(repo))
    blocked = bool(groups["foreign"])

    if args.json:
        print(json.dumps({"repo": str(repo), "blocked": blocked, **groups}, indent=2))
        return 1 if blocked else 0

    print(f"shared checkout: {repo}")
    if not any(groups.values()):
        print("clean — a landing would be accepted")
        return 0
    for name in ("record", "generated"):
        for p in groups[name]:
            print(f"  [ok]       {p}")
    for p in groups["foreign"]:
        print(f"  [FOREIGN]  {p}")
    print()
    if blocked:
        print(
            "REFUSED: land_runs.py will refuse every landing while any FOREIGN path is "
            "present (channels/risks.md R-009).\n"
            "Unblock: commit or `git stash` those paths in the shared checkout, then re-run "
            "this check. A wake session may not edit another checkout, so this unblock is a "
            "hand action."
        )
        return 1
    print("OK: only record/generated dirt — a landing would be accepted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
