#!/usr/bin/env python3
"""A run's patch is not one thing; the lander treats it as one (Dmitri, 2026-10-25).

Why this exists
---------------
`land_runs.py` applies a run's `changes.patch` with a single `git apply`, and `git apply` is atomic:
one hunk that no longer matches discards every file the run wrote. Measured 2026-10-25 in this
checkout, on the five items waiting in one amigo's review queue:

    three of the five patches no longer apply at all, and in every one of them the failing hunk is
    `channels/items.jsonl` — the shared ledger, which `main` rewrites every few minutes, so any
    run's hunk against it is stale by the time the lander reaches it.

The run's real work is sitting in the same patch, unharmed, and is thrown away with it. That is the
delivery loop the commons has spent months reading as "the work does not exist": 93 runs across the
five bots carry `land: conflict` or a refusal, and every later wake that reads a missing-path list
recomputes work that is on a disk the whole time.

So this splits a patch at its `diff --git` boundaries and asks git about each file separately.
Dry run by default; `--apply` writes the files that do match.

The ledger is not a file, it is a log
-------------------------------------
`channels/items.jsonl` is append-only, so its hunks are almost always stale — and they are also the
one kind of stale hunk that can be repaired without guessing: the rows the run added are still in the
patch, verbatim. The tool therefore does not apply ledger hunks. It extracts the rows the run *added*
and appends the ones whose `id` is not already in the file, reporting the rest as duplicates. This
matters: an earlier repair that appended blindly is how the ledger came to hold every item four
times over (Desi, 2026-10-23).

Honest limits, stated here rather than discovered later:
  * A modified line in the ledger (a state change, not an append) is not reconstructed. Rows are
    matched by `id`; a run whose whole point was to move an existing id to `accomplished` will have
    that line reported as a duplicate and skipped. The tool says so rather than pretending.
  * Only `channels/items.jsonl` is treated as a log. Every other file gets the strict treatment,
    because a half-applied prose file is worse than an unapplied one.
  * Applying a patch can bring tests with it. This tool does not run them; the lander still does.

Usage
-----
    python3 scripts/land_patch_split.py ~/LLM/desi-bot/tick-state/runs/<id>/changes.patch
    python3 scripts/land_patch_split.py --apply <patch> [<patch> ...]
    python3 scripts/land_patch_split.py --repo /path/to/checkout <patch>
    python3 scripts/land_patch_split.py --runs ~/LLM/*-bot/tick-state/runs   # every stuck run

Exit 0 when every file in every patch applied (or was already present), 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

LEDGER = "channels/items.jsonl"


def split_patch(text: str):
    """Split a unified diff into (path, chunk) pairs, one per file.

    Keeps the `diff --git` header with its chunk so each piece is a valid patch on its own.
    """
    chunks, current, header = [], [], None
    for line in text.splitlines(keepends=True):
        if line.startswith("diff --git "):
            if current:
                chunks.append((header, "".join(current)))
            current, header = [line], _path_from_header(line)
        elif current:
            current.append(line)
    if current:
        chunks.append((header, "".join(current)))
    return [(p, c) for p, c in chunks if p]


def _path_from_header(line: str) -> str:
    # "diff --git a/foo b/foo" — take the b-side; renamed files are rare here and both sides print.
    parts = line.strip().split(" b/", 1)
    return parts[1] if len(parts) == 2 else line.strip().split()[-1]


def _git(repo: Path, *args, stdin: str | None = None):
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        input=stdin, text=True, capture_output=True,
    )


def check_chunk(repo: Path, chunk: str):
    """Return (ok, reason). A chunk is ok if git would apply it to this tree."""
    r = _git(repo, "apply", "--check", "-", stdin=chunk)
    if r.returncode == 0:
        return True, ""
    reason = (r.stderr or r.stdout).strip().splitlines()
    return False, reason[0] if reason else "git apply --check failed"


def ledger_rows(chunk: str):
    """The lines a chunk adds to the ledger, as parsed objects plus their raw text."""
    rows = []
    for line in chunk.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            raw = line[1:]
            if not raw.strip():
                continue
            try:
                rows.append((json.loads(raw), raw))
            except json.JSONDecodeError:
                rows.append((None, raw))
    return rows


def repair_ledger(repo: Path, chunk: str, apply: bool):
    """Append rows the ledger does not already hold, by `id`. Returns (added, dupes, unparsable)."""
    target = repo / LEDGER
    existing_lines = set()
    existing_ids = set()
    if target.exists():
        for line in target.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.strip():
                existing_lines.add(line)
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(obj, dict) and obj.get("id"):
                    existing_ids.add(str(obj["id"]))

    added, dupes, unparsable = [], [], []
    for obj, raw in ledger_rows(chunk):
        if raw in existing_lines:
            dupes.append(raw)
        elif obj is None:
            unparsable.append(raw)
        elif obj.get("id") and str(obj["id"]) in existing_ids:
            dupes.append(raw)
        else:
            added.append(raw)
            existing_lines.add(raw)

    if apply and added and target.exists():
        text = target.read_text(encoding="utf-8", errors="replace")
        with target.open("a", encoding="utf-8") as fh:
            if text and not text.endswith("\n"):
                fh.write("\n")  # otherwise the last old row and the first new one become one line
            fh.write("".join(row + "\n" for row in added))
    return added, dupes, unparsable


def process(patch: Path, repo: Path, apply: bool, verbose: bool):
    text = patch.read_text(encoding="utf-8", errors="replace")
    chunks = split_patch(text)
    result = {"patch": str(patch), "files": [], "repaired": 0, "failed": 0}

    for path, chunk in chunks:
        entry = {"path": path}
        if path == LEDGER:
            added, dupes, bad = repair_ledger(repo, chunk, apply)
            entry["status"] = "ledger"
            entry["rows_added"] = len(added)
            entry["rows_duplicate"] = len(dupes)
            entry["rows_unparsable"] = len(bad)
            result["repaired"] += 1
        else:
            ok, reason = check_chunk(repo, chunk)
            if ok:
                if apply:
                    r = _git(repo, "apply", "-", stdin=chunk)
                    ok = r.returncode == 0
                    if not ok:
                        reason = (r.stderr or r.stdout).strip().splitlines()
                        reason = reason[0] if reason else "apply failed"
                entry["status"] = "applies" if ok else "failed"
                if ok:
                    result["repaired"] += 1
                else:
                    result["failed"] += 1
            else:
                entry["status"] = "failed"
                result["failed"] += 1
            if entry["status"] == "failed":
                entry["reason"] = reason
        result["files"].append(entry)

    print(f"{patch.parent.name if patch.name == 'changes.patch' else patch.name}")
    for entry in result["files"]:
        if entry["status"] == "ledger":
            print(f"  ledger  {entry['path']}: {entry['rows_added']} row(s) new, "
                  f"{entry['rows_duplicate']} already present, {entry['rows_unparsable']} unparsable")
        elif entry["status"] == "applies":
            print(f"  ok      {entry['path']}")
        else:
            print(f"  FAILED  {entry['path']} — {entry.get('reason', '')}")
            if verbose:
                print("          (the file's own hunks are stale; the rest of the patch is unaffected)")
    return result


def stuck_patches(runs: Path):
    """Every run under the given roots whose own result.json says it did not land, oldest first."""
    for result_file in sorted(runs.glob("*/runs/*/result.json")):
        try:
            data = json.loads(result_file.read_text(encoding="utf-8", errors="replace"))
        except (json.JSONDecodeError, OSError):
            continue
        land = data.get("land") or ""
        if land == "landed":
            continue
        patch = result_file.parent / "changes.patch"
        if patch.exists() and patch.stat().st_size > 0:
            yield patch


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("patches", nargs="*", type=Path)
    ap.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--apply", action="store_true", help="write the files that match (default: dry run)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--runs", type=Path, action="append", default=[],
                    help="a tick-state/runs root, or a directory of bot roots, to scan for stuck runs")
    ap.add_argument("--limit", type=int, default=0, help="with --runs, stop after this many patches")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    targets = list(args.patches)
    for root in args.runs:
        if (root / "runs").is_dir():
            found = list(stuck_patches(root))
        else:
            found = []
            for bot in sorted(root.glob("*-bot")):
                found.extend(stuck_patches(bot / "tick-state"))
        targets.extend(found)
    if args.limit:
        targets = targets[: args.limit]
    if not targets:
        print("nothing to do: no patches given and no stuck runs found", file=sys.stderr)
        return 0

    results = [process(p, args.repo, args.apply, args.verbose) for p in targets]
    if args.json:
        print(json.dumps(results, indent=2))

    total_ok = sum(r["repaired"] for r in results)
    total_bad = sum(r["failed"] for r in results)
    print(f"\n{len(results)} patch(es): {total_ok} file(s) recoverable, {total_bad} still stale"
          + ("" if args.apply else "  (dry run — pass --apply to write)"))
    return 0 if total_bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
