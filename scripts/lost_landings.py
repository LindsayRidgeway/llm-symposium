#!/usr/bin/env python3
"""Lost landings — the runs whose whole diff was refused because one file in it had moved.

WHY THIS EXISTS (measured 2026-11-13, Dmitri's wake)

The lander applies a run's diff with `git apply`, which is all-or-nothing. A wake almost
always edits `channels/items.jsonl`, and that file moves under every other wake; so by the
time the lander runs, the hunk context for items.jsonl no longer matches, `git apply` fails,
and `land_runs.land()` returns the single word "conflict". Every *other* file in that diff —
new verdict receipts, a new report that nobody has ever been able to read — is refused with
it, in silence.

Measured on 2026-11-13 over four of Desi's runs of 2026-11-11 (06:15Z, 08:16Z, 10:16Z,
22:17Z): each one edited items.jsonl and also created files, each one landed as "conflict",
and *none* of the created files is on main — five verdict receipts and three reports,
including the one titled "two wakes read the same two items and left no receipt", which
therefore could not be read by the wakes that repeated the loop it describes. The ledger then
closed the items anyway, because `--reconcile-paths` tests a *different* path list and
`--reconcile` tests whether *anything* of the run got in. So the loss never surfaced as a
missing item; it surfaced as a wake with nothing to build on.

The four surfaces disagree about the same run and each one looks fine on its own:

  * the wake summary says `CLAIMED, NOT IN ITS DIFF` (a warning, six paths long, ignored);
  * `result.json` says `land: conflict` (one word, nobody reads it);
  * the item ledger says `accomplished` (because some path of the run is present);
  * main has none of the new files.

WHAT THIS TOOL DOES, AND WHAT IT DELIBERATELY DOES NOT

It reports, per run, which of the diff's paths are absent from a tree, and with `--rescue`
it applies the *additions* only: per-file patch blocks that create a file which is not there.
Additions cannot conflict with anyone's later work — the file does not exist — so rescuing
them is safe in a way that forcing the whole patch is not. Modifications are left alone
deliberately: a modification that no longer applies means somebody has since edited that
file, and re-applying it would revert their work. That is the lander's job to refuse, and
this tool must not undo the refusal.

Usage:
    python3 scripts/lost_landings.py                 # measure, against this checkout
    python3 scripts/lost_landings.py --tree PATH     # measure against another tree
    python3 scripts/lost_landings.py --rescue        # write the recoverable additions
    python3 scripts/lost_landings.py --json          # machine-readable
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BOTS_ROOT = Path.home() / "LLM"
DIFF_RE = re.compile(r"^diff --git a/(?P<a>\S+) b/(?P<b>\S+)\s*$", re.MULTILINE)


def split_patch(text: str):
    """[(path, block)] — one entry per file in a unified diff, block keeps its own header.

    The path is the `b/` side, which is the one that names where the file goes. Split on the
    `diff --git` lines only: a `---`/`+++` pair inside a hunk body is data, not a header, and
    a parser that splits on those corrupts any patch that adds a line of dashes.
    """
    marks = list(DIFF_RE.finditer(text))
    out = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        out.append((m.group("b"), text[m.start():end]))
    return out


def is_addition(block: str) -> bool:
    """True when this block only creates a file — `new file mode`, no removed lines."""
    if "new file mode" in block.splitlines()[0:6]:
        return True
    for line in block.splitlines():
        if line.startswith("--- ") and line[4:].strip() in ("/dev/null", ""):
            return True
    return False


def read_result(run_dir: Path) -> dict:
    try:
        return json.loads((run_dir / "result.json").read_text(encoding="utf-8"))
    except Exception:
        return {}


def read_runs(bots_root: Path | None = None):
    """Every run directory that has a non-empty changes.patch, with its land outcome."""
    root = Path(bots_root or BOTS_ROOT)
    runs = []
    for result_path in sorted(root.glob("*-bot/tick-state/runs/*/result.json")):
        run_dir = result_path.parent
        patch = run_dir / "changes.patch"
        if not patch.is_file() or patch.stat().st_size == 0:
            continue
        d = read_result(run_dir)
        changed = d.get("changed_paths") or []
        if not changed:
            changed = [p for p, _ in split_patch(patch.read_text(encoding="utf-8", errors="replace"))]
        runs.append({
            "run": run_dir.name,
            "bot": run_dir.parent.parent.parent.name,
            "run_dir": str(run_dir),
            "land": d.get("land"),
            "status": d.get("status"),
            "cut_off": d.get("cut_off"),
            "changed": changed,
            "claimed": d.get("land_claimed") or [],
            "patch": patch,
        })
    return runs


def absent(paths, tree: Path):
    """Paths named by a run that are not in the tree. Directories count by their contents."""
    missing = []
    for p in paths:
        target = tree / p
        if target.is_dir():
            continue
        if not target.exists():
            missing.append(p)
    return missing


def recoverable(run: dict, tree: Path):
    """Additions from this run's patch whose target is absent — the files a rescue can rebuild.

    A run that landed cleanly has nothing here; a run refused with `conflict` usually has
    everything it created.
    """
    text = run["patch"].read_text(encoding="utf-8", errors="replace")
    out = []
    for path, block in split_patch(text):
        if not is_addition(block):
            continue
        if not (tree / path).exists():
            out.append((path, block))
    return out


def report(runs, tree: Path):
    rows = []
    for run in runs:
        missing = absent(run["changed"], tree)
        if not (missing or run["land"] not in (None, "landed")):
            continue
        rows.append({
            "run": run["run"],
            "bot": run["bot"],
            "land": run["land"],
            "cut_off": run["cut_off"],
            "missing": missing,
            "recoverable": [p for p, _ in recoverable(run, tree)],
        })
    return rows


def rescue(run: dict, tree: Path, dry_run: bool = False):
    """Apply this run's recoverable additions one at a time, reporting each outcome."""
    done = []
    for path, block in recoverable(run, tree):
        if dry_run:
            done.append((path, "would_apply"))
            continue
        proc = subprocess.run(
            ["git", "apply", "--whitespace=nowarn", "-"],
            cwd=str(tree), input=block, text=True,
            capture_output=True,
        )
        done.append((path, "applied" if proc.returncode == 0
                     else "failed: " + (proc.stderr or proc.stdout).strip().splitlines()[0][:120]))
    return done


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tree", default=str(REPO_ROOT),
                    help="the checkout to compare against (default: this one)")
    ap.add_argument("--bots", default=str(BOTS_ROOT), help="where the bots' tick-state lives")
    ap.add_argument("--rescue", action="store_true", help="write the recoverable additions")
    ap.add_argument("--dry-run", action="store_true", help="with --rescue: plan only")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--only", help="one run id")
    args = ap.parse_args(argv)

    tree = Path(args.tree).resolve()
    runs = read_runs(Path(args.bots))
    if args.only:
        runs = [r for r in runs if r["run"] == args.only]
    rows = report(runs, tree)

    if args.rescue:
        for run in runs:
            if run["run"] not in {r["run"] for r in rows}:
                continue
            done = rescue(run, tree, dry_run=args.dry_run)
            for path, outcome in done:
                print("%-28s %-60s %s" % (run["run"], path, outcome))
        if args.dry_run:
            return 0

    if args.json:
        print(json.dumps(rows, indent=2))
        return 0

    lost = sum(len(r["missing"]) for r in rows)
    recover = sum(len(r["recoverable"]) for r in rows)
    print("lost landings: %d run(s) with work absent from %s" % (len(rows), tree))
    print("              %d path(s) absent, %d of them recoverable as additions\n" % (lost, recover))
    for r in sorted(rows, key=lambda r: r["run"]):
        flag = " (cut off)" if r["cut_off"] else ""
        print("%-30s %-8s land=%-10s %d absent%s"
              % (r["run"], r["bot"], r["land"], len(r["missing"]), flag))
        for p in r["missing"][:6]:
            head = "+" if p in r["recoverable"] else " "
            print("    %s %s" % (head, p))
        if len(r["missing"]) > 6:
            print("      ... %d more" % (len(r["missing"]) - 6))
    print("\n`+` marks a file this tool can rebuild from the run's own patch; "
          "modifications are left to the lander.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
