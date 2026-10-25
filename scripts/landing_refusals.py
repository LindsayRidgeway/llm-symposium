#!/usr/bin/env python3
"""Reconcile the landing refusals — which refused runs are still refused.

Why this exists (2026-10-19, Dmitri). `land_runs.py` writes `landing_failed.txt` into a run's own
directory when the repository's tests show the run's diff introduced new failures, and that file is
never touched again. It is a **verdict**, not a state: it stays in the run directory after the same
work has landed under a later run's commit. Read a fortnight later it says "this work was refused"
about work that is on `main` and green.

Measured this wake, on the run that this wake was assigned to review (desi `20261019T110921Z-df991cc4`):

* its `landing_failed.txt` reads `this run's diff introduced new failures: test_drive_bridge_status.py`;
* all eight paths it claims are on `main`, added whole by desi run `20261019T130933Z-8421299d`
  (commit `6b85041d`), whose own report says the flaky test was traced and fixed;
* the test now passes 15/15 consecutive runs, and the race that made it flaky is documented in the
  test file itself (`mount_unreadable`).

So the refusal was true on the day and is false now, and nothing in the repository distinguishes the
two. That is the same shape as the 2026-09-23 defect ("unlanded is not missing"): a durable marker
that a later reader takes for a verdict about today, which is how ten wakes came to recompute the
same work. This script does the reconciliation a machine can do: for every refusal on the disk, check
whether the run's own claimed paths reached this checkout's `main`.

Classification, per refused run:

    reconciled  every path the run's LAND line claims is on main — the refusal was made good later
    partial     some are on main and some are not — real missing work, and the refusal is half true
    open        none of the claimed paths is on main — the refusal still stands
    no-claim    no LAND line with paths (cut off, or a report that never said) — nothing to check

The `no-claim` rows matter more than they look: a run cut off at its action cap often refused with
nothing named, and that is a delivery nobody can chase from the run record alone.

Read-only. It never edits a run directory. It does not re-run a test unless `--recheck` is asked for
(added 2026-10-23), and that flag exists because the path check answers only half the question: a
refusal names a test as its cause, and whether *that* still reproduces is a second measurement.

Measured 2026-10-23, all 89 refusals on disk: no-claim 37, partial 21, open 13, reconciled 18. Two
in five were refused with nothing named and one in five was made good later, so the record as it
stands is not a list of unfinished work — it is a list of moments. The five test files that refuse
most often (`test_evidence_table_registration`, `test_cited_path_gate`, `test_gen_feed_freshness`,
`test_gallery_unwired_works`, `test_declutter_audit`) all pass on the tree of that measurement.

`--recheck` labels each refusal `green-now` if every test it blames passes in this checkout today,
`red-now` if one still fails, `gone` if the blamed file no longer exists, `untested` if the reason
names none. `green-now` does NOT prove the run was innocent — it says the cause does not reproduce
here, which is exactly what the path-based `reconciled` says about the paths. Both are statements
about today, and neither is a verdict about the day of the refusal.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# A LAND line, as the wake instruction asks for it: `LAND: a, b, c`. Reports also carry
# `LAND: (none yet)`, `LAND: (pending)` and `LAND: (nothing yet)` — those are claims of nothing.
LAND_RE = re.compile(r"^\s*LAND:\s*(.+)$", re.MULTILINE)
PLACEHOLDER = re.compile(r"^\(.*\)$")


def claimed_paths(report_text: str) -> list[str]:
    """The paths a run's report claims, from its last LAND line.

    Last, not first: a report is rewritten as the run proceeds (the instruction says so), so an
    earlier line can legitimately name less than the run finished with.
    """
    matches = LAND_RE.findall(report_text or "")
    if not matches:
        return []
    out: list[str] = []
    for raw in matches[-1].split(","):
        item = raw.strip().strip("`").strip().rstrip(".")
        if not item or PLACEHOLDER.match(item):
            continue
        out.append(item)
    return out


def read(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except OSError:
        return ""


def classify(run_dir: Path, repo: Path) -> dict:
    """One refusal, checked against the repository's own files."""
    reason = read(run_dir / "landing_failed.txt").strip().splitlines()
    paths = claimed_paths(read(run_dir / "report.txt"))
    present = [p for p in paths if (repo / p).exists()]
    if not paths:
        state = "no-claim"
    elif len(present) == len(paths):
        state = "reconciled"
    elif present:
        state = "partial"
    else:
        state = "open"
    return {
        "run": run_dir.name,
        "bot": run_dir.parent.parent.parent.name,
        "state": state,
        "reason": reason[0] if reason else "",
        "claimed": len(paths),
        "on_main": len(present),
        "missing": [p for p in paths if p not in present],
    }


TEST_RE = re.compile(r"\btest_[A-Za-z0-9_]+\.py\b")
RECHECK_TIMEOUT = 180


def named_tests(reason: str) -> list[str]:
    """The test files a refusal blames, by name, in the order it names them.

    The refusal text is always `this run's diff introduced new failures: a.py, b.py`, so the names
    are the only part of the verdict that says *what to run*. Reading them out is the whole trick.
    """
    out: list[str] = []
    for name in TEST_RE.findall(reason or ""):
        if name not in out:
            out.append(name)
    return out


def _default_runner(test_path: Path, repo: Path) -> tuple[int, str]:
    proc = subprocess.run([sys.executable, str(test_path)], cwd=str(repo),
                          capture_output=True, text=True, timeout=RECHECK_TIMEOUT)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def _why(output: str) -> str:
    """The last line of a test run that says something — the count, or the failure."""
    for line in reversed((output or "").strip().splitlines()):
        line = line.strip()
        if line and not line.startswith(("Ran ", "OK", "---")):
            return line[:90]
    tail = (output or "").strip().splitlines()
    return (tail[-1].strip()[:90] if tail else "")


def recheck(row: dict, repo: Path, runner=_default_runner,
            cache: dict | None = None) -> dict:
    """Does the test this refusal blames still fail here? One measurement per named test.

    `cache` is per-invocation: `test_evidence_table_registration.py` is blamed by eleven separate
    refusals and must not be re-run eleven times. The runner is injectable so the tests below can
    assert the labelling without running a real suite.
    """
    cache = {} if cache is None else cache
    names = named_tests(row.get("reason", ""))
    out = dict(row)
    out["tests"] = names
    if not names:
        out["recheck"] = "untested"
        out["recheck_detail"] = []
        return out
    detail = []
    for name in names:
        if name not in cache:
            path = repo / "tests" / name
            if not path.exists():
                cache[name] = ("gone", "not in this checkout")
            else:
                try:
                    code, text = runner(path, repo)
                    cache[name] = ("green-now" if code == 0 else "red-now", _why(text))
                except Exception as exc:                      # timeout, unreadable, anything
                    cache[name] = ("error", f"{type(exc).__name__}: {exc}"[:90])
        state, why = cache[name]
        detail.append((name, state, why))
    states = [d[1] for d in detail]
    if "red-now" in states:
        verdict = "red-now"
    elif "green-now" in states:
        verdict = "green-now"
    elif "error" in states:
        verdict = "error"
    else:
        verdict = "gone"
    out["recheck"] = verdict
    out["recheck_detail"] = detail
    return out


def find_runs(roots: list[Path]) -> list[Path]:
    """Every run directory under the given roots that carries a refusal."""
    found: list[Path] = []
    for root in roots:
        pattern = os.path.join(str(root), "*", "tick-state", "runs", "*", "landing_failed.txt")
        for hit in glob.glob(pattern):
            found.append(Path(hit).parent)
    return sorted(set(found), key=lambda p: p.name)


def survey(roots: list[Path], repo: Path, recheck_tests: bool = False) -> dict:
    rows = [classify(r, repo) for r in find_runs(roots)]
    if recheck_tests:
        cache: dict = {}
        rows = [recheck(row, repo, cache=cache) for row in rows]
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["state"]] = counts.get(row["state"], 0) + 1
    facts = {
        "repo": str(repo),
        "refusals": len(rows),
        "counts": counts,
        "rows": rows,
    }
    if recheck_tests:
        rechecked: dict[str, int] = {}
        for row in rows:
            key = row.get("recheck", "untested")
            rechecked[key] = rechecked.get(key, 0) + 1
        facts["recheck_counts"] = rechecked
    return facts


def render(facts: dict) -> str:
    counts = facts["counts"]
    lines = [
        f"{facts['refusals']} refused landing(s) on disk; checked against {facts['repo']}",
        "  " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())) if counts else "  none",
        "",
    ]
    order = {"open": 0, "partial": 1, "no-claim": 2, "reconciled": 3}
    for row in sorted(facts["rows"], key=lambda r: (order.get(r["state"], 9), r["run"])):
        detail = ""
        if row["state"] == "partial":
            detail = "  missing: " + ", ".join(row["missing"][:4])
            if len(row["missing"]) > 4:
                detail += f" (+{len(row['missing']) - 4} more)"
        lines.append(
            f"  [{row['state']:<10}] {row['bot']:<7} {row['run']}  "
            f"{row['on_main']}/{row['claimed']} on main{detail}"
        )
        if row["state"] == "open" and row["reason"]:
            lines.append(f"               reason: {row['reason'][:110]}")
    lines += [
        "",
        "reconciled = the refusal was made good later; do not redo that work.",
        "open/partial = real missing work; the run's reason above is the starting point.",
        "no-claim = a refusal with nothing named; only the run's own transcript can say what it was.",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs-root", action="append", default=None,
                    help="directory holding <bot>/tick-state/runs (repeatable); "
                         "defaults to ~/LLM")
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parent.parent),
                    help="the checkout whose files are the test of 'reached main'")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when any refusal is still open or partial")
    args = ap.parse_args(argv)

    roots = [Path(os.path.expanduser(r)) for r in (args.runs_root or ["~/LLM"])]
    facts = survey(roots, Path(args.repo).resolve())
    if args.json:
        print(json.dumps(facts, indent=2))
    else:
        print(render(facts))
    if args.strict and (facts["counts"].get("open") or facts["counts"].get("partial")):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
