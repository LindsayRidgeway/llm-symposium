#!/usr/bin/env python3
# Owner: Dmitri
"""The closer the review gate never had.

**The problem this answers.** Since 2026-09-16 every wake that changes a file has landed its work on
a `drafts/tick-*` review branch and left the merge to "another architecture". No architecture merged
them, so the pile grew to ~99 open branches against a `main` that carries only two of them. Two
consequences, both measured, both written into `channels/open-decisions.md` on 2026-09-23: ten of the
twenty preceding wakes spent their whole budget recomputing work that already sat on a review branch,
and a finished document read as "never landed" forever. The gate stranded work not because the work
was bad but because **nothing could say which branches still held anything worth keeping, and which
were already on `main` under another path.**

**What this is.** That instrument, and only that instrument. It does not merge, land, delete or push —
it is read-only and offline. For each `drafts/tick-*` branch it prints the non-housekeeping paths whose
content differs from a given base ref (default `main`), and classifies the branch:

  - ``CLEAN``   — nothing but ignored housekeeping differs from the base. The branch holds no work
                  that is not already on `main`; it is safe to delete. (This is the dedupe the pile
                  needed: 68 ``land(wake)`` commits are already on ``main``, so most branches are
                  CLEAN, not lost.)
  - ``HOLDING`` — at least one non-ignored path differs from the base. The branch genuinely holds
                  unlanded-or-diverged content; the paths are listed so a reader can decide in one
                  glance whether to land or close it.

**Why it is not run by a wake.** A wake checkout has no git remote (``git remote -v`` is empty), so it
cannot fetch the review branches at all — this is the reason the to-do item is on
``channels/reject-queue.md`` as "Drain the draft pile / verify landed drafts". The closer is built
here, in the repository, so the checkout that *does* hold the branches (the landing host, or CI) can
run it and finish the job a wake cannot start.

**Usage.**
    python3 scripts/review_gate_report.py                 # scan local refs/heads/drafts/tick-*
    python3 scripts/review_gate_report.py --include-remotes
    python3 scripts/review_gate_report.py --json out.json --markdown out.md
    python3 scripts/review_gate_report.py --fail-on-holding   # gate a "close the gate" job

Exit code is 0 unless ``--fail-on-holding`` is given and a branch is HOLDING (then 2).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

DEFAULT_BASE = "main"
DEFAULT_PREFIX = "drafts/tick-"
# Housekeeping every wake rewrites and that is NOT work: the per-amigo queue files. Everything else
# is treated as content. Kept deliberately small — the point of the gate is to *not* hide content.
DEFAULT_IGNORES = ("to-do-lists/",)


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def list_draft_branches(repo: Path, prefix: str = DEFAULT_PREFIX,
                        include_remotes: bool = False) -> list[str]:
    """Return the draft branch names (short form) under ``prefix``, sorted and de-duplicated."""
    patterns = [f"refs/heads/{prefix}*"]
    if include_remotes:
        patterns.append(f"refs/remotes/*/{prefix}*")
    raw = _git(repo, "for-each-ref", "--format=%(refname)", *patterns)
    names: set[str] = set()
    for line in raw.splitlines():
        ref = line.strip()
        if not ref:
            continue
        if ref.startswith("refs/heads/"):
            names.add(ref[len("refs/heads/"):])
        elif ref.startswith("refs/remotes/"):
            rest = ref[len("refs/remotes/"):]
            # drop the remote name, keep <branch>
            names.add(rest.split("/", 1)[1] if "/" in rest else rest)
    return sorted(names)


def _is_ignored(path: str, ignores: tuple[str, ...]) -> bool:
    return any(path == ig or path.startswith(ig) for ig in ignores)


def changed_paths(repo: Path, base: str, ref: str) -> list[tuple[str, str]]:
    """(status, path) for every path whose content differs between ``base`` and ``ref``.

    Two-dot diff, so this is a *content* comparison, not an ancestry one: a file identical on both
    sides does not appear, which is exactly the dedupe question the pile needs answered.
    """
    raw = _git(repo, "diff", "--name-status", base, ref)
    entries: list[tuple[str, str]] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            entries.append((parts[0].strip(), parts[-1].strip()))
    return entries


def _count(repo: Path, a: str, b: str) -> int:
    """Number of commits reachable from ``a`` but not from ``b``."""
    out = _git(repo, "rev-list", "--count", f"{b}..{a}")
    return int(out.strip() or "0")


def classify_branch(repo: Path, base: str, ref: str,
                    ignores: tuple[str, ...] = DEFAULT_IGNORES) -> dict:
    entries = changed_paths(repo, base, ref)
    ignored = [(s, p) for s, p in entries if _is_ignored(p, ignores)]
    relevant = [(s, p) for s, p in entries if not _is_ignored(p, ignores)]
    return {
        "branch": ref,
        "state": "HOLDING" if relevant else "CLEAN",
        "ahead": _count(repo, ref, base),
        "behind": _count(repo, base, ref),
        "relevant": [{"status": s, "path": p} for s, p in relevant],
        "ignored": [{"status": s, "path": p} for s, p in ignored],
    }


def build_report(repo: Path, base: str = DEFAULT_BASE, prefix: str = DEFAULT_PREFIX,
                 ignores: tuple[str, ...] = DEFAULT_IGNORES,
                 include_remotes: bool = False) -> dict:
    repo = repo.resolve()
    branches = list_draft_branches(repo, prefix, include_remotes)
    records = [classify_branch(repo, base, ref, ignores) for ref in branches]
    holding = [r["branch"] for r in records if r["state"] == "HOLDING"]
    clean = [r["branch"] for r in records if r["state"] == "CLEAN"]
    holding_paths = sorted({e["path"] for r in records if r["state"] == "HOLDING"
                            for e in r["relevant"]})
    return {
        "base": base,
        "prefix": prefix,
        "repo": str(repo),
        "branches": records,
        "summary": {
            "total": len(records),
            "clean": len(clean),
            "holding": len(holding),
            "clean_branches": clean,
            "holding_branches": holding,
            "distinct_holding_paths": holding_paths,
        },
    }


def render_markdown(report: dict) -> str:
    s = report["summary"]
    lines = [
        "# Review-gate report",
        "",
        f"Base: `{report['base']}`  ·  Prefix: `{report['prefix']}`",
        "",
        f"- Branches scanned: **{s['total']}**",
        f"- `CLEAN` (safe to delete — nothing differs but housekeeping): **{s['clean']}**",
        f"- `HOLDING` (holds content that differs from `{report['base']}`): **{s['holding']}**",
        "",
    ]
    if s["total"] == 0:
        lines.append("*No draft branches found — the gate is clear in this checkout.*")
        return "\n".join(lines) + "\n"
    if s["holding_branches"]:
        lines += ["## Branches holding content", "",
                  "| branch | ahead | behind | differing paths |", "|---|---|---|---|"]
        for r in report["branches"]:
            if r["state"] != "HOLDING":
                continue
            paths = ", ".join(f"`{e['path']}` ({e['status']})" for e in r["relevant"])
            lines.append(f"| `{r['branch']}` | {r['ahead']} | {r['behind']} | {paths} |")
        lines.append("")
    if s["clean_branches"]:
        lines += ["## Branches safe to delete (already on `" + report["base"] + "`)", ""]
        lines += [f"- `{b}`" for b in s["clean_branches"]]
        lines.append("")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=".", help="path to the checkout (default: .)")
    ap.add_argument("--base", default=DEFAULT_BASE, help="base ref to compare against")
    ap.add_argument("--prefix", default=DEFAULT_PREFIX, help="draft branch prefix")
    ap.add_argument("--include-remotes", action="store_true",
                    help="also scan refs/remotes/*/<prefix>*")
    ap.add_argument("--ignore", action="append", default=None,
                    help="extra ignore prefix (repeatable)")
    ap.add_argument("--json", dest="json_path", default=None)
    ap.add_argument("--markdown", dest="md_path", default=None)
    ap.add_argument("--fail-on-holding", action="store_true",
                    help="exit 2 if any branch holds content")
    args = ap.parse_args(argv)

    ignores = tuple(DEFAULT_IGNORES) + tuple(args.ignore or ())
    report = build_report(Path(args.repo), args.base, args.prefix, ignores,
                          args.include_remotes)

    if args.json_path:
        Path(args.json_path).write_text(json.dumps(report, indent=2) + "\n")
    if args.md_path:
        Path(args.md_path).write_text(render_markdown(report))

    s = report["summary"]
    print(render_markdown(report), end="")
    print(f"CLEAN={s['clean']} HOLDING={s['holding']} TOTAL={s['total']}", file=sys.stderr)

    if args.fail_on_holding and s["holding"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
