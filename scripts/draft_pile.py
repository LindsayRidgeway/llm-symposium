#!/usr/bin/env python3
"""Tick the review-gate draft pile: what is real work, and what is already on main?

The gate writes a `drafts/tick-*` branch whenever a wake did not land its own work on
`main`. Nothing merges or closes those branches, so the pile grows one branch per wake
and every later wake that reads "these paths never reached main" has to guess whether
the content is new. This answers that question mechanically, from git, instead of
re-deriving it by hand.

For every branch matching a pattern it compares the changes the branch introduces
(relative to its merge-base with the base branch) against the base branch, and
classifies each changed path:

  NEW              the branch adds a path the base branch does not have
  EDIT_UNLANDED    the base branch has the file exactly as it was *before* the branch's
                   edit, so the edit never reached the base branch
  ADDED_LANDED     the branch adds a path whose content is already on the base
  LANDED           the branch modifies a path to content the base already has
  MOVED_ON         the base branch has its own, newer version of the file (the branch's
                   edit is neither present nor provably absent) — needs a human eye
  ADD_CONFLICT     the branch adds a path where the base has unrelated content
  DELETED          the branch removes a path (a wake should not delete)

NEW and EDIT_UNLANDED are the strong signals: the base branch demonstrably lacks that
content. A branch with neither is either already landed or ambiguous, and the script
prints the exact `git push origin --delete` command for the landed ones.

The script never writes to the remote and never pushes. It is a *reader*: it tells the
human-run landing machine (the only checkout wired to push) which branches to drop and
which to rescue. That is the closer the gate never had.

Usage:
    scripts/draft_pile.py --fetch                 # fetch refs, then report
    scripts/draft_pile.py --json /tmp/pile.json   # machine-readable
    scripts/draft_pile.py --remote https://github.com/OWNER/REPO
    scripts/draft_pile.py --pattern '*/autonomous/*'
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import subprocess
import sys

# Strong "the base branch lacks this content" states.
UNLANDED_STATES = ("NEW", "EDIT_UNLANDED")
# "safe to drop" = every non-ignored path is one of these.
LANDED_STATES = ("ADDED_LANDED", "LANDED", "DELETED")


def git(*args: str, allow_fail: bool = False) -> str:
    """Run git and return stripped stdout. Exit (or return '') on failure."""
    proc = subprocess.run(
        ["git", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={"GIT_TERMINAL_PROMPT": "0", "PATH": os.environ.get("PATH", "/usr/bin:/bin")},
    )
    if proc.returncode != 0:
        if allow_fail:
            return ""
        raise SystemExit(f"git {' '.join(args)} failed:\n{proc.stderr.strip()}")
    return proc.stdout.strip()


def rev_path(rev: str, path: str) -> str:
    """Object id of `path` at `rev`, or '' if the path is absent there."""
    return git("rev-parse", "--verify", "--quiet", f"{rev}:{path}", allow_fail=True)


def list_branches(pattern: str) -> list[str]:
    out = git("for-each-ref", "--format=%(refname:short)", allow_fail=True)
    names = [ln.strip() for ln in out.splitlines() if ln.strip()]
    return sorted(n for n in names if fnmatch.fnmatch(n, pattern))


def changed_paths(merge_base: str, branch: str) -> list[str]:
    """Paths the branch adds or modifies relative to the merge base.

    `--no-renames` keeps the parser trivial: a rename shows as a delete plus an add,
    and the add is what we care about.
    """
    out = git("diff", "--name-only", "--no-renames", "-z", merge_base, branch, allow_fail=True)
    return [p for p in out.split("\0") if p]


def classify(base: str, mb: str, branch: str, path: str) -> str:
    b = rev_path(branch, path)
    m = rev_path(base, path)
    o = rev_path(mb, path)
    if not b:
        return "DELETED"
    if not o:  # the branch adds the path
        if not m:
            return "NEW"
        return "ADDED_LANDED" if m == b else "ADD_CONFLICT"
    # the branch modifies the path
    if not m:
        return "MOVED_ON"  # base deleted a file the branch edits
    if m == b:
        return "LANDED"
    if m == o:
        return "EDIT_UNLANDED"  # base never took the edit
    return "MOVED_ON"


def build_pile(pattern: str, base: str, ignore: str):
    reports = []
    skipped = []
    for br in list_branches(pattern):
        mb = git("merge-base", base, br, allow_fail=True)
        if not mb:
            skipped.append(br)
            continue
        paths, ignored = {}, {}
        for path in changed_paths(mb, br):
            state = classify(base, mb, br, path)
            (ignored if ignore and fnmatch.fnmatch(path, ignore) else paths)[path] = state
        reports.append({"branch": br, "merge_base": mb, "paths": paths, "ignored": ignored})
    return reports, skipped


def _verdict(paths: dict) -> str:
    if any(s in UNLANDED_STATES for s in paths.values()):
        return "HOLDS_WORK"
    if any(s not in LANDED_STATES for s in paths.values()):
        return "REVIEW"
    return "SAFE_TO_DELETE"


def render_text(reports, skipped) -> str:
    lines = []
    unlanded: dict[str, list[str]] = {}
    for rep in sorted(reports, key=lambda r: r["branch"]):
        verdict = _verdict(rep["paths"])
        lines.append(f"\n## {rep['branch']}  [{verdict}]  (merge-base {rep['merge_base'][:10]})")
        if rep["paths"]:
            for path, state in sorted(rep["paths"].items()):
                lines.append(f"  {state:14} {path}")
                if state in UNLANDED_STATES:
                    unlanded.setdefault(path, []).append(rep["branch"])
        else:
            lines.append("  (no non-ignored changes)")
        if rep["ignored"]:
            lines.append(f"  ({len(rep['ignored'])} ignored path(s), e.g. to-do lists)")
    for br in skipped:
        lines.append(f"\n## {br}  [UNCOMPARABLE]  no merge-base with base branch")

    work = [r for r in reports if _verdict(r["paths"]) == "HOLDS_WORK"]
    review = [r for r in reports if _verdict(r["paths"]) == "REVIEW"]
    safe = [r for r in reports if _verdict(r["paths"]) == "SAFE_TO_DELETE"]

    lines += [
        "\n" + "=" * 72,
        f"branches: {len(reports)} compared, {len(skipped)} uncomparable",
        f"  HOLDS_WORK (base demonstrably lacks the content): {len(work)}",
        f"  REVIEW (only ambiguous/moved-on paths):           {len(review)}",
        f"  SAFE_TO_DELETE (every change already on base):    {len(safe)}",
        f"  distinct unlanded paths:                          {len(unlanded)}",
    ]
    if unlanded:
        lines.append("\nContent the base branch does not have (the real work in the pile):")
        for path in sorted(unlanded):
            lines.append(f"  {path}")
            lines.append(f"      on: {', '.join(sorted(unlanded[path]))}")
    if safe:
        lines.append("\nSafe to delete (every non-ignored change is already on base):")
        for rep in safe:
            lines.append(f"  git push origin --delete {rep['branch'].split('/', 1)[-1]}")
    return "\n".join(lines) + "\n"


def render_markdown(reports, skipped, base: str, pattern: str) -> str:
    """A durable, dated snapshot of the pile — checked against git, not transcribed."""
    import datetime

    today = datetime.date.today().isoformat()
    work = [r for r in reports if _verdict(r["paths"]) == "HOLDS_WORK"]
    review = [r for r in reports if _verdict(r["paths"]) == "REVIEW"]
    safe = [r for r in reports if _verdict(r["paths"]) == "SAFE_TO_DELETE"]
    unlanded: dict[str, list[str]] = {}
    for rep in reports:
        for path, state in rep["paths"].items():
            if state in UNLANDED_STATES:
                unlanded.setdefault(path, []).append(rep["branch"])

    out = [
        "<!-- GENERATED by scripts/draft_pile.py --md — DO NOT EDIT.",
        "     Regenerate: python3 scripts/draft_pile.py --fetch --md channels/draft-pile.md -->",
        "",
        "# The draft pile — what the review gate is holding",
        "",
        f"*Generated {today} from `git` against `{base}` for refs matching `{pattern}`.*",
        "",
        "The gate writes a `drafts/tick-*` branch whenever a wake does not land its own work on",
        "`main`, and nothing closes them. This table says, mechanically, which branches hold",
        "content the base branch demonstrably lacks and which are already landed. `NEW` and",
        "`EDIT_UNLANDED` mean the base branch does not have that content; `MOVED_ON`/`ADD_CONFLICT`",
        "mean the base has its own version and a human should look; the rest are already on the",
        "base. This file is a reader's snapshot: the landing machine acts on it, this script does",
        "not push.",
        "",
        "## Summary",
        "",
        f"- **{len(reports)}** branches compared ({len(skipped)} uncomparable)",
        f"- **{len(work)}** hold work the base lacks",
        f"- **{len(review)}** reference-only / ambiguous",
        f"- **{len(safe)}** safely deletable (every change already on the base)",
        f"- **{len(unlanded)}** distinct unlanded paths",
        "",
        "## Branches",
        "",
        "| branch | verdict | unlanded / ambiguous paths |",
        "|---|---|---|",
    ]
    for rep in sorted(reports, key=lambda r: r["branch"]):
        notable = [
            f"`{p}` ({s})"
            for p, s in sorted(rep["paths"].items())
            if s not in LANDED_STATES
        ]
        cell = "<br>".join(notable) if notable else "—"
        out.append(f"| {rep['branch'].split('/', 1)[-1]} | {_verdict(rep['paths'])} | {cell} |")
    for br in skipped:
        out.append(f"| {br.split('/', 1)[-1]} | UNCOMPARABLE | no merge-base with `{base}` |")

    if unlanded:
        out += ["", "## Content the base branch does not have", "",
                "| path | on branches |", "|---|---|"]
        for path in sorted(unlanded):
            brs = ", ".join(b.split("/", 1)[-1] for b in sorted(unlanded[path]))
            out.append(f"| `{path}` | {brs} |")
    if safe:
        out += ["", "## Safe to delete", "", "```"]
        for rep in safe:
            out.append(f"git push origin --delete {rep['branch'].split('/', 1)[-1]}")
        out.append("```")
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", default="main", help="base branch to compare against")
    ap.add_argument("--pattern", default="*/drafts/tick-*", help="fnmatch over short ref names")
    ap.add_argument("--ignore", default="to-do-lists/*", help="path globs summarised separately")
    ap.add_argument("--remote", default="origin", help="git remote to fetch from")
    ap.add_argument("--fetch", action="store_true", help="fetch the pattern before reporting")
    ap.add_argument("--json", metavar="PATH", help="also write a JSON report here")
    ap.add_argument("--md", metavar="PATH", help="write a dated Markdown snapshot here")
    args = ap.parse_args(argv)

    if args.fetch:
        if "drafts" not in args.pattern:
            raise SystemExit("--fetch currently supports the drafts/* family only")
        url = git("remote", "get-url", args.remote, allow_fail=True) or args.remote
        git("fetch", "--no-tags", args.remote,
            f"+refs/heads/drafts/*:refs/remotes/{args.remote}/drafts/*")
        sys.stderr.write(f"fetched drafts/* from {url}\n")

    reports, skipped = build_pile(args.pattern, args.base, args.ignore)
    sys.stdout.write(render_text(reports, skipped))

    if args.json:
        payload = {
            "base": args.base,
            "pattern": args.pattern,
            "unlanded_states": list(UNLANDED_STATES),
            "branches": [
                {**r, "verdict": _verdict(r["paths"])} for r in sorted(reports, key=lambda r: r["branch"])
            ],
            "uncomparable": skipped,
        }
        with open(args.json, "w") as fh:
            json.dump(payload, fh, indent=2, sort_keys=True)
            fh.write("\n")
        sys.stderr.write(f"wrote {args.json}\n")

    if args.md:
        with open(args.md, "w") as fh:
            fh.write(render_markdown(reports, skipped, args.base, args.pattern))
        sys.stderr.write(f"wrote {args.md}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
