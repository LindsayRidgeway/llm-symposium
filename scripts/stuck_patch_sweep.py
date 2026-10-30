#!/usr/bin/env python3
"""One command for the recovery every wake has been doing by hand: which patches were thrown away,
and what can be put back out of them.

Why this exists (2026-10-30, Dmitri). The lander applies each run's `changes.patch` with `git apply`,
which is atomic over the whole patch: one stale hunk and *none* of the run's files are applied. The
worst offender is `channels/items.jsonl`, a 3,557-line append-only log that the landing machine itself
rewrites, so almost no patch written by a wake holds valid context against it. The measurement of
2026-10-29 (`discussions/2026-10-29-whole-repo-review.md` §1) was 23 of 25 patches failing, 16 of them
on that one file.

Three instruments for this defect already existed and none of them ran:

* `scripts/ledger_row_recovery.py` — recovers the *ledger rows* a failed patch lost;
* `scripts/unlanded_worklist.py` — which wakes' claimed paths never reached main;
* the landing-outcome census, written, tested and lost three times to the fault it measures.

This script is the hand for those instruments. It splits a patch into its per-file sections — the split
`git apply` refuses to do — asks `git apply --check` about each section alone, and can then apply the
sections that are clean while leaving the volatile log to the tool that already knows how to append to
it. It is the same recovery done by hand in the reviews of 10-23 and 10-29, minus the hand.

What it deliberately does not do. It does not rewrite the lander (that is a bot file, outside the
repository and outside a wake's reach) and it is therefore not the prevention; it is the remedy, run
after the fact. It does not decide whether recovered work is *good* — it puts back what a run wrote and
names it. It applies nothing unless told `--recover`, and appends ledger rows only with `--write`.

Usage:
    python3 scripts/stuck_patch_sweep.py                        # classify every patch under ~/LLM/*-bot
    python3 scripts/stuck_patch_sweep.py --limit 20 --since 20261029
    python3 scripts/stuck_patch_sweep.py --run-dir <dir> [--run-dir <dir> ...]
    python3 scripts/stuck_patch_sweep.py --run-dir <dir> --recover            # documents only
    python3 scripts/stuck_patch_sweep.py --run-dir <dir> --recover --write    # documents + rows
    python3 scripts/stuck_patch_sweep.py --json

Exit status: 0 whenever the sweep itself ran, 2 on bad arguments or a broken patch file.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LEDGER_REL = "channels/items.jsonl"
DEFAULT_ROOT = Path.home() / "LLM"


# --------------------------------------------------------------------------- patch doctoring


def split_sections(patch_text: str) -> list[tuple[str, str]]:
    """The patch as (path, section) pairs, in order — one section per file, headers included.

    A section begins at `diff --git` and runs to the next one. Splitting here is the whole point:
    `git apply` is atomic over the file it is handed, and handing it one section at a time is how a
    stale hunk in one path stops discarding the rest of the run.
    """
    sections: list[tuple[str, str]] = []
    path: str | None = None
    buf: list[str] = []
    for line in patch_text.splitlines():
        if line.startswith("diff --git "):
            if path is not None:
                sections.append((path, "\n".join(buf) + "\n"))
            parts = line.split()
            path = parts[3][2:] if len(parts) >= 4 else parts[2][2:]
            buf = [line]
            continue
        if path is not None:
            buf.append(line)
    if path is not None:
        sections.append((path, "\n".join(buf) + "\n"))
    return sections


def _apply_check(section: str, repo: Path, reverse: bool = False) -> bool:
    with tempfile.NamedTemporaryFile("w", suffix=".patch", delete=False, encoding="utf-8") as fh:
        fh.write(section)
        tmp = fh.name
    cmd = ["git", "apply", "--check", "--recount"]
    if reverse:
        cmd.append("--reverse")
    cmd.append(tmp)
    try:
        return subprocess.run(cmd, cwd=str(repo), capture_output=True).returncode == 0
    finally:
        Path(tmp).unlink(missing_ok=True)


def classify_section(path: str, section: str, repo: Path) -> str:
    """`clean` (applies as it stands) / `in-tree` (the tree already has it) / `blocked` (a stale hunk)."""
    if _apply_check(section, repo):
        return "clean"
    if _apply_check(section, repo, reverse=True):
        return "in-tree"
    return "blocked"


def classify_patch(patch: Path, repo: Path = REPO) -> dict:
    text = patch.read_text(encoding="utf-8", errors="replace")
    sections = [{"path": p, "verdict": classify_section(p, s, repo)}
                for p, s in split_sections(text)]
    verdicts = {s["verdict"] for s in sections}
    if not sections:
        overall = "empty"
    elif verdicts == {"in-tree"}:
        overall = "in-tree"
    elif verdicts <= {"clean", "in-tree"}:
        overall = "clean"
    else:
        overall = "blocked"
    blocked = [s["path"] for s in sections if s["verdict"] == "blocked"]
    return {"patch": str(patch), "run": patch.parent.name, "sections": sections,
            "verdict": overall, "blocked": blocked,
            "blocked_only_ledger": bool(blocked) and set(blocked) == {LEDGER_REL}}


def recover_patch(patch: Path, repo: Path = REPO, ledger: Path | None = None,
                  write: bool = False, exclude: tuple[str, ...] = (LEDGER_REL,)) -> dict:
    """Apply every section that is clean and not excluded; hand the log to the row-recovery tool."""
    text = patch.read_text(encoding="utf-8", errors="replace")
    ledger = ledger or (repo / LEDGER_REL)
    applied: list[str] = []
    skipped: list[str] = []
    for path, section in split_sections(text):
        if path in exclude:
            skipped.append(path)
            continue
        if classify_section(path, section, repo) != "clean":
            skipped.append(path)
            continue
        with tempfile.NamedTemporaryFile("w", suffix=".patch", delete=False, encoding="utf-8") as fh:
            fh.write(section)
            tmp = fh.name
        try:
            rc = subprocess.run(["git", "apply", "--recount", tmp], cwd=str(repo),
                                capture_output=True)
        finally:
            Path(tmp).unlink(missing_ok=True)
        (applied if rc.returncode == 0 else skipped).append(path)

    rows = {"recovered": [], "already_current": 0, "written": False}
    if any(p == LEDGER_REL for p, _ in split_sections(text)):
        # The row-recovery tool is imported from *this* checkout, not from the tree being recovered:
        # a recovery may be aimed at any checkout, and only `ledger_path` should follow it there.
        sys.path.insert(0, str(REPO))
        from scripts import ledger_row_recovery as L  # noqa: E402
        rows = L.recover(patch=patch, ledger_path=ledger, write=write)
    return {"patch": str(patch), "applied": applied, "skipped": skipped,
            "ledger_rows_recovered": rows["recovered"], "ledger_rows_written": rows["written"]}


# --------------------------------------------------------------------------- the sweep


def find_patches(root: Path, since: str | None, limit: int | None) -> list[Path]:
    """Every `changes.patch` under `<root>/*-bot/tick-state/runs/*/`, newest run first."""
    found = sorted(root.glob("*-bot/tick-state/runs/*/changes.patch"),
                   key=lambda p: p.parent.name, reverse=True)
    if since:
        found = [p for p in found if p.parent.name[:8] >= since]
    return found[:limit] if limit else found


def summarise(results: list[dict]) -> dict:
    counts = Counter(r["verdict"] for r in results)
    blocked_paths = Counter(p for r in results for p in r["blocked"])
    return {"patches": len(results), "verdicts": dict(counts),
            "blocked_only_ledger": sum(1 for r in results if r["blocked_only_ledger"]),
            "blocked_paths": dict(blocked_paths.most_common(10))}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(DEFAULT_ROOT), help="where the *-bot trees live")
    ap.add_argument("--run-dir", action="append", default=[],
                    help="a single tick-state run directory (repeatable)")
    ap.add_argument("--since", help="only runs whose timestamp starts with this, e.g. 20261029")
    ap.add_argument("--limit", type=int, help="stop after this many patches, newest first")
    ap.add_argument("--recover", action="store_true",
                    help="apply the sections that are clean to the tree (the documents half)")
    ap.add_argument("--write", action="store_true",
                    help="with --recover, also append the recovered ledger rows (the register half)")
    ap.add_argument("--exclude", action="append", default=None,
                    help=f"a path recovery must never apply itself (default: {LEDGER_REL})")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    if args.run_dir:
        patches = [Path(d) / "changes.patch" for d in args.run_dir]
        missing = [str(p) for p in patches if not p.exists()]
        if missing:
            print(f"stuck_patch_sweep: no changes.patch in {', '.join(missing)}", file=sys.stderr)
            return 2
    else:
        patches = find_patches(Path(args.root), args.since, args.limit)

    exclude = tuple(args.exclude) if args.exclude is not None else (LEDGER_REL,)
    results = [classify_patch(p) for p in patches]

    if args.recover:
        for r in results:
            rec = recover_patch(Path(r["patch"]), exclude=exclude, write=args.write)
            r["recovery"] = rec

    if args.json:
        print(json.dumps({"results": results, "summary": summarise(results)}, indent=2))
        return 0

    s = summarise(results)
    print(f"patches scanned: {s['patches']} (against {REPO})")
    for verdict in ("clean", "in-tree", "blocked", "empty"):
        if s["verdicts"].get(verdict):
            print(f"  {verdict:<8} {s['verdicts'][verdict]}")
    if s["blocked_only_ledger"]:
        print(f"  of the blocked, {s['blocked_only_ledger']} fail on {LEDGER_REL} alone "
              "— the rest of those patches is recoverable")
    if s["blocked_paths"]:
        print("  blocked paths, most common first:")
        for path, n in s["blocked_paths"].items():
            print(f"    {n:>4}  {path}")
    lost = [r for r in results if r["verdict"] == "blocked"]
    if lost:
        print(f"\n{len(lost)} patch(es) that would be thrown away whole, newest first:")
        for r in lost[:15]:
            print(f"  {r['run']}  blocked on {', '.join(r['blocked'][:3])}"
                  + (" …" if len(r["blocked"]) > 3 else ""))
        if len(lost) > 15:
            print(f"  … and {len(lost) - 15} more")
    if args.recover:
        print("\nrecovery: documents written; ledger rows only with --write")
        for r in results:
            if "recovery" not in r:
                continue
            rec = r["recovery"]
            rows = rec["ledger_rows_recovered"]
            if not rec["applied"] and not rows:
                continue
            print(f"  {r['run']}: applied {len(rec['applied'])} path(s)"
                  + (f", ledger rows {'written' if rec['ledger_rows_written'] else 'recoverable'}: "
                     f"{len(rows)}" if rows else ""))
            for p in rec["applied"]:
                print(f"    + {p}")
    elif s["verdicts"].get("blocked"):
        print("\npass --recover to apply the clean sections of the blocked patches "
              "(and --write to append their ledger rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
