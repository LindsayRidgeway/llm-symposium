#!/usr/bin/env python3
"""Which draft-branch pile is finished work, and which is already on `main`.

Owner: Dmitri.  Written 2026-10-11.

**The pile this exists for.** Since the review gate was introduced (2026-09-16) every
wake has parked its diff on its own `drafts/tick-*` branch instead of landing it. A wake's
checkout has **no git remote** (`git remote -v` is empty; `git for-each-ref` shows one
ref, `refs/heads/main`), so no wake can fetch the pile, and nothing else was ever given
the job of draining it. Measured 2026-10-05: 101 `drafts/tick-*` branches, 2 merged, 99
open — one per 4-hourly wake, back to 2026-09-16. The gate has no closer.

**What is actually in the pile (spot-checked 2026-10-05, and again by other wakes).** Real
unlanded work — a Reddit read-access script + tests, an `auto_reply` fix + tests, a probe
report, an affective-pain evidence map. But **68 `land(wake)` commits are on `main`** too,
so much of the pile is the same work under a different path, already delivered. The pile
therefore cannot be mass-merged (that would double-land) and cannot be mass-deleted (that
would lose the unlanded work). It has to be *classified*, path by path, against `main`.

**Why a wake cannot do that, and this tool can.** The classification needs the branch
refs, which live only on the machine wired to the remote (the landing machine). This tool
is written to run *there*: point it at the checkout with the refs and it answers, without
merging anything and without writing anything, which branches carry content `main` does
not have and which are safe to close. It is the read-only half of the closer; the closing
is `git branch -D` (or `git push origin --delete`) on the superseded ones once a human or
a wake has read the report.

**How a path is judged "unlanded".** Not by commit message and not by branch age — by
content. For every path the branch changed since the merge-base, compare the blob on the
branch with the blob on `main` *now*:

  * the blob on `main` is missing, or differs from the branch's -> the branch holds
    content `main` does not have: **unlanded**;
  * the blobs are identical -> someone already landed that exact content by another
    route: **already on main**, the change is not unlanded even though the commit is.

Paths under `to-do-lists/` and the generated indexes (`--noise-path`) are excluded from
"work": the suite rewrites the indexes by running, and every amigo edits their own to-do
list, so those changes are noise in this comparison and never make a branch worth keeping.

Usage:
  python3 scripts/draft_pile_triage.py                        # scan origin/drafts/tick-*
  python3 scripts/draft_pile_triage.py --repo ~/LLM/llm-symposium
  python3 scripts/draft_pile_triage.py --select 'drafts/tick-*' --main origin/main
  python3 scripts/draft_pile_triage.py --json

Exit code is 0 when no scanned branch carries unlanded work (the pile is closable) and 1
when at least one does (there is work to land), so a caller can branch on it without
reading the text.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from pathlib import Path

# The same generated-index set the lander uses (see scripts/landing_tree_report.py); kept
# as a local copy rather than an import so neither tool can break the other at load time.
NOISE_PATHS = {
    "scripts/README.md",
    "channels/agenda.md",
    "context/context-digest.md",
    "discussions/README.md",
}
NOISE_PREFIXES = ("to-do-lists/",)

VERDICT_WORK = "carries-work"
VERDICT_LANDED = "already-landed"
VERDICT_NOISE = "noise-only"
VERDICT_IDENTICAL = "identical"


def git(repo: Path, *args: str):
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True, check=False)


def _rev(repo: Path, spec: str) -> str:
    """Full object hash for a rev:path spec, or "" when the path is absent there."""
    return git(repo, "rev-parse", "--verify", "--quiet", spec).stdout.strip()


def _name_status(repo: Path, left: str, right: str):
    """[(code, path)] for `git diff left right`, renames suppressed, machine format.

    `-z --no-renames` so a space or quote in a filename cannot corrupt the parse, the
    same discipline scripts/landing_tree_report.py uses.
    """
    out = git(repo, "diff", "--name-status", "--no-renames", "-z", left, right).stdout
    fields = [f for f in out.split("\x00") if f]
    return [(fields[i], fields[i + 1]) for i in range(0, len(fields) - 1, 2)]


def is_noise(path: str, noise_paths, noise_prefixes) -> bool:
    return path in noise_paths or path.startswith(tuple(noise_prefixes))


def list_branches(repo: Path, select: str):
    """[(refname, shortname)] for every ref whose short name matches `select`."""
    out = git(repo, "for-each-ref", "--format=%(refname)").stdout.splitlines()
    picked = []
    for refname in out:
        if refname.endswith("/HEAD"):
            continue
        short = refname
        for pref in ("refs/heads/", "refs/remotes/", "refs/"):
            if short.startswith(pref):
                short = short[len(pref):]
                break
        if fnmatch.fnmatch(short, select) or fnmatch.fnmatch(refname, select):
            picked.append((refname, short))
    return sorted(picked)


def classify_branch(repo: Path, refname: str, short: str, main_ref: str,
                    noise_paths, noise_prefixes) -> dict:
    base_proc = git(repo, "merge-base", main_ref, refname)
    base = base_proc.stdout.strip() or main_ref

    counts = git(repo, "rev-list", "--left-right", "--count",
                 f"{main_ref}...{refname}").stdout.split()
    behind, ahead = (int(counts[0]), int(counts[1])) if len(counts) == 2 else (0, 0)

    unlanded, noise, already = [], [], []
    for code, path in _name_status(repo, base, refname):
        if is_noise(path, noise_paths, noise_prefixes):
            noise.append(path)
            continue
        on_branch = _rev(repo, f"{refname}:{path}")
        on_main = _rev(repo, f"{main_ref}:{path}")
        if on_branch and on_main and on_branch == on_main:
            already.append(path)          # same content already reached main
            continue
        kind = {"A": "new", "M": "modified", "D": "deleted", "T": "type-changed"}.get(code, code)
        unlanded.append({"path": path, "kind": kind})

    if unlanded:
        verdict = VERDICT_WORK
    elif noise:
        verdict = VERDICT_NOISE
    elif already:
        verdict = VERDICT_LANDED
    else:
        verdict = VERDICT_IDENTICAL

    return {
        "ref": refname,
        "short": short,
        "verdict": verdict,
        "ahead": ahead,
        "behind": behind,
        "unlanded": unlanded,
        "already_on_main": sorted(already),
        "noise": sorted(noise),
    }


def scan(repo: Path, select: str, main_ref: str,
         noise_paths=None, noise_prefixes=None):
    noise_paths = set(NOISE_PATHS) | set(noise_paths or ())
    noise_prefixes = tuple(NOISE_PREFIXES) + tuple(noise_prefixes or ())
    return [classify_branch(repo, ref, short, main_ref, noise_paths, noise_prefixes)
            for ref, short in list_branches(repo, select)]


def summarize(records) -> dict:
    counts = {VERDICT_WORK: 0, VERDICT_LANDED: 0, VERDICT_NOISE: 0, VERDICT_IDENTICAL: 0}
    for r in records:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    return {
        "scanned": len(records),
        "carries_work": counts[VERDICT_WORK],
        "already_landed": counts[VERDICT_LANDED] + counts[VERDICT_IDENTICAL],
        "noise_only": counts[VERDICT_NOISE],
        "unlanded_paths": sum(len(r["unlanded"]) for r in records),
    }


def render(repo: Path, main_ref: str, select: str, records) -> str:
    s = summarize(records)
    lines = ["draft-pile triage — %s" % repo,
             "  main = %s   select = %r   scanned = %d branch(es)"
             % (main_ref, select, s["scanned"])]

    def section(title, wanted, note):
        rows = [r for r in records if r["verdict"] == wanted]
        if not rows:
            return
        lines.append("")
        lines.append("%s (%d): %s" % (title, len(rows), note))
        for r in rows:
            if wanted == VERDICT_WORK:
                lines.append("  %s   ahead %d / behind %d" % (r["short"], r["ahead"], r["behind"]))
                for u in r["unlanded"]:
                    lines.append("      %-12s %s" % (u["kind"], u["path"]))
                lines.append("      -> inspect: git diff %s...%s" % (main_ref, r["ref"]))
            else:
                lines.append("  %s" % r["short"])

    section("CARRIES WORK", VERDICT_WORK,
            "content main does not have — land or cherry-pick, do NOT delete")
    section("SUPERSEDED (already on main)", VERDICT_LANDED,
            "every changed path is already on main with the same content — closable")
    section("NOISE ONLY", VERDICT_NOISE,
            "only to-do lists / generated indexes changed — nothing to keep")
    section("IDENTICAL", VERDICT_IDENTICAL, "no diff against main at all — closable")

    lines.append("")
    lines.append("  %d branch(es): %d carry work (%d unlanded path(s)), "
                 "%d already landed, %d noise-only."
                 % (s["scanned"], s["carries_work"], s["unlanded_paths"],
                    s["already_landed"], s["noise_only"]))
    if s["carries_work"]:
        lines.append("  Close the superseded/noise branches first; they need no review:")
        lines.append("    git branch -D <short>            # local drafts/tick-* refs")
        lines.append("    git push origin --delete <short> # remote drafts/tick-* refs")
        lines.append("  The carrying branches still need a reader — land each, then delete it.")
    else:
        lines.append("  No branch carries unlanded work: the pile is closable.")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--select", default="drafts/tick-*",
                    help="fnmatch glob for the branch short-name (default: drafts/tick-*)")
    ap.add_argument("--main", default="auto",
                    help="main ref to compare against (default: auto -> origin/main, else main)")
    ap.add_argument("--noise-path", action="append", default=[],
                    help="extra path to ignore as noise")
    ap.add_argument("--noise-prefix", action="append", default=[],
                    help="extra path prefix to ignore as noise")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    if git(repo, "rev-parse", "--git-dir").returncode != 0:
        print("not a git checkout: %s" % repo, file=sys.stderr)
        return 2

    main_ref = args.main
    if main_ref == "auto":
        for cand in ("origin/main", "main"):
            if _rev(repo, cand):
                main_ref = cand
                break
        else:
            print("no main ref found (tried origin/main, main); pass --main", file=sys.stderr)
            return 2
    elif not _rev(repo, main_ref):
        print("main ref not found: %s" % main_ref, file=sys.stderr)
        return 2

    records = scan(repo, args.select, main_ref, args.noise_path, args.noise_prefix)
    if args.json:
        print(json.dumps({"repo": str(repo), "main": main_ref, "select": args.select,
                          "summary": summarize(records), "branches": records}, indent=2))
    else:
        print(render(repo, main_ref, args.select, records))
    return 1 if summarize(records)["carries_work"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
