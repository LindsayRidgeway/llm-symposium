#!/usr/bin/env python3
# Owner: Dmitri (land_runs.py subsystem; the `conflict` path).
"""Why a parked run's patch does not apply — file by file, and what the whole patch costs.

**The gap this fills, measured 2026-10-14.** `land_runs.py` reports one word for a run whose
patch will not apply: `"land": "conflict"`. That word is a fact about the *patch*, and the
record reads it as a fact about the work. Two things are invisible behind it:

1. **Which file failed.** `git apply` is all-or-nothing across a patch, so one stale hunk
   discards every file in the run — including files that would have applied cleanly on their
   own. Measured on run `20261013T170314Z-0838fbd7` (dmitri-bot), whose `result.json` reads
   `"land": "conflict"`: 4 changed paths, 3 hunks that no longer apply, and **1 new file** —
   the run's own report — that `git apply --check` confirms would have landed. The wake is
   recorded as having delivered nothing; one of its four paths was deliverable.
2. **Which files can be rescued.** A reviewer with the per-file verdict can recover the
   salvageable paths from a conflicted run instead of reading the whole run as lost. That is
   the difference between "conflict" and "three quarters of this is recoverable".

**What this is not.** Not a lander, and it writes nothing. Same choice as
`landing_tree_report.py`: the classification is the deliverable, and a tool that silently
rewrites a parked run's patch would trade a visible loss for a silent one.

**The fix this points at, which is not in this repository.** `git apply --check` on the whole
patch is what makes the loss atomic; a lander that applied each file's chunk independently
(or used `git apply --3way` per file) would land the applicable subset and report the rest.
The lander is `~/LLM/<amigo>-bot/land_runs.py`, a bot file a wake may not edit — named here so
it stops being invisible. Note also that a `merge=union` driver in `.gitattributes` does *not*
help: the lander never runs `git merge`, it runs `git apply`, and merge drivers do not affect
`git apply`.

Usage:
  python3 scripts/landing_conflict_report.py ~/LLM/dmitri-bot/tick-state/runs/20261013T170314Z-0838fbd7
  python3 scripts/landing_conflict_report.py --runs-root ~/LLM/dmitri-bot/tick-state/runs
  python3 scripts/landing_conflict_report.py --json <run-dir> [<run-dir> ...]

Exit status: 1 = at least one named patch is discarded as a whole; 0 = none is (including a run
that produced no patch).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

STATES = ("applicable", "already_landed", "conflict", "empty")


def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def split_patch(text: str) -> list[tuple[str, str]]:
    """One (path, chunk) pair per `diff --git` section, in file order.

    The path is the b-side of the `---`/`+++` pair when present (that is the path the change
    *creates*, so a new file is named by its new name), falling back to the `diff --git` line.
    """
    chunks: list[tuple[str, list[str]]] = []
    for line in text.splitlines(keepends=True):
        if line.startswith("diff --git "):
            chunks.append(("", [line]))
        elif chunks:
            chunks[-1][1].append(line)
    out: list[tuple[str, str]] = []
    for _, lines in chunks:
        path = ""
        for i, line in enumerate(lines):
            if line.startswith("+++ b/"):
                path = line[len("+++ b/"):].strip()
                break
            if line.startswith("--- a/") and i + 1 == len(lines):
                path = line[len("--- a/"):].strip()
        if not path:
            head = lines[0].split()
            if len(head) >= 4:
                path = head[3][2:] if head[3].startswith("b/") else head[3]
        out.append((path, "".join(lines)))
    return out


def verdict(repo: Path, chunk: str, tmpdir: Path, name: str) -> str:
    """`already_landed` if the chunk runs backwards, `applicable` if it runs forwards.

    Backwards first: for a plain edit the two are mutually exclusive, and for a new file whose
    content is already in the tree the reverse direction is the one that succeeds.
    """
    p = tmpdir / name
    p.write_text(chunk, encoding="utf-8")
    if git(repo, "apply", "-R", "--check", str(p)).returncode == 0:
        return "already_landed"
    if git(repo, "apply", "--check", str(p)).returncode == 0:
        return "applicable"
    return "conflict"


def assess(repo: Path, patch_path: Path) -> dict:
    """Per-file verdicts, plus whether the patch as a whole is refused."""
    text = patch_path.read_text(encoding="utf-8", errors="replace")
    result: dict = {
        "patch": str(patch_path),
        "run": patch_path.parent.name,
        "files": [],
        "whole": "empty",
        "lost_with_the_rest": [],
    }
    if not text.strip():
        return result
    if git(repo, "apply", "--check", str(patch_path)).returncode == 0:
        result["whole"] = "applicable"
    elif git(repo, "apply", "-R", "--check", str(patch_path)).returncode == 0:
        result["whole"] = "already_landed"
    else:
        result["whole"] = "discarded"
    chunks = split_patch(text)
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for i, (path, chunk) in enumerate(chunks):
            v = verdict(repo, chunk, tmp, "chunk%03d.patch" % i)
            result["files"].append({"path": path, "verdict": v})
    if result["whole"] == "discarded":
        # Files that would land on their own and are thrown away with the ones that will not.
        result["lost_with_the_rest"] = [
            f["path"] for f in result["files"] if f["verdict"] in ("applicable", "already_landed")
        ]
    return result


def runs_with_patches(runs_root: Path) -> list[Path]:
    return sorted(p / "changes.patch" for p in runs_root.iterdir() if (p / "changes.patch").is_file())


def report(result: dict, out=sys.stdout) -> None:
    print("### %s" % result["run"], file=out)
    print("patch: %s" % result["patch"], file=out)
    if result["whole"] == "empty":
        print("  no patch on disk — nothing to apply (the run produced no diff)", file=out)
        return
    for f in result["files"]:
        print("  %-15s %s" % (f["verdict"], f["path"]), file=out)
    if result["whole"] in ("applicable", "already_landed"):
        print("whole patch: %s" % result["whole"].upper(), file=out)
    else:
        print("whole patch: DISCARDED — `git apply --check` refuses it, and apply is atomic,", file=out)
        print("             so none of the %d file(s) land." % len(result["files"]), file=out)
        if result["lost_with_the_rest"]:
            print("             %d of them would land on their own and are lost with the rest:"
                  % len(result["lost_with_the_rest"]), file=out)
            for p in result["lost_with_the_rest"]:
                print("               %s" % p, file=out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="run directories or .patch files")
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parents[1]),
                    help="the checkout to test applicability against (default: this repository)")
    ap.add_argument("--runs-root", help="a tick-state/runs directory: every run that has a patch")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    repo = Path(args.repo).expanduser().resolve()
    if git(repo, "rev-parse", "--is-inside-work-tree").returncode != 0:
        print("not a git work tree: %s" % repo, file=sys.stderr)
        return 2
    targets: list[Path] = []
    for raw in args.paths:
        p = Path(raw).expanduser()
        targets.append(p / "changes.patch" if p.is_dir() else p)
    if args.runs_root:
        root = Path(args.runs_root).expanduser()
        if not root.is_dir():
            print("no such runs root: %s" % root, file=sys.stderr)
            return 2
        targets.extend(runs_with_patches(root))
    if not targets:
        ap.print_help()
        return 2

    results = [assess(repo, t) for t in targets]
    if args.json:
        print(json.dumps(results, indent=1))
    else:
        discarded = 0
        lost = 0
        for r in results:
            report(r)
            if r["whole"] == "discarded":
                discarded += 1
                lost += len(r["lost_with_the_rest"])
        if len(results) > 1:
            print("")
            print("%d patch(es): %d refused whole, %d file(s) that would land lost with them."
                  % (len(results), discarded, lost))
    return 1 if any(r["whole"] == "discarded" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
