#!/usr/bin/env python3
# Owner: Desi (landing gate subsystem). Filed 2026-10-19.
"""Landing preflight for the *failure* gate: run the suite before the wake ends.

Why this exists (2026-10-19). The landing gate has two refusal modes. The first
one — a shared checkout holding foreign dirt — already had a preflight
(`scripts/landing_preflight.py`, R-009). The second one did not:

    LANDING REFUSED: this run's diff introduced new failures: <test file>

That line arrives *after* the run is over, so the work is on a branch and the
next wake re-derives it or loses it. Measured on the two wakes before this file:

  * run 20261019T050851Z-ecfd7995 — refused on `test_evidence_table_registration.py`
  * run 20261019T070913Z-38117598 — refused on `test_test_registration_audit.py`

Both wakes wrote new files and both trips came from a *repository-wide audit*
of the tree — an unregistered test, a cited path that does not exist — which is
exactly the class of failure a wake cannot see while it is writing the file that
causes it. And both were answerable in about a hundred seconds: measured on main
at 678760d1, 116 test files, 101.9 s for the whole suite.

So this runs direct test scripts in the work tree the wake is editing, and answers the
gate's own question before the gate does. "New" is relative to a baseline,
because one test was already red on main when this was written
(`test_gen_index.py`, a stale `scripts/README.md`) — a checker that called that
*the wake's* fault would be as wrong as one that called it clean.

Two baselines, and the difference matters:

  * a recorded one (`tests/landing-baseline.json`, one commit and a list of
    failing file names). Cheap, and it goes stale: it is only true for the
    commit it names, and this tool says so out loud every run.
  * a live one (`--against origin/main`), measured in a throwaway worktree at
    that revision. Slower — twice the suite — and true whenever it is asked.

The failure direction is deliberate: with no baseline this exits 1 on any
failure, because "we could not tell" must not read as "safe to land".

Usage:
  python3 scripts/landing_suite_check.py                      # vs the recorded baseline
  python3 scripts/landing_suite_check.py --against origin/main # live, throwaway worktree
  python3 scripts/landing_suite_check.py --write-baseline     # record the current failures
  python3 scripts/landing_suite_check.py --json

Exit status: 0 = no new failures (a landing would not be refused for this);
1 = new failures, named; 2 = usage or setup error (git, missing/unsupported tests).

Execution contract: each discovered file is executed as `python test_file.py`,
not collected by pytest. Definition/import-only modules are unsupported, even
when listed in a baseline. Supply a direct entry point (e.g. unittest.main()) or
use the project's intended test runner instead. The syntactic entry-point check
does not prove every defined test is called, nor does exit 0 certify coverage.
Writing a baseline preserves the decision against the PREVIOUS baseline; it
does not turn new failures green. Unsupported files prevent baseline writing.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = REPO_ROOT / "tests" / "landing-baseline.json"
DEFAULT_TIMEOUT = 120


def discover(tests_dir):
    """Every `test_*.py` in the directory, in a stable order."""
    return sorted(Path(tests_dir).glob("test_*.py"))


def _child_env():
    env = dict(os.environ)
    # The suite must not write into the real spend ledger while being probed.
    # Caught 2026-09-25 the hard way: two rows that looked like live CI spend.
    env["CI_USAGE_PATH"] = os.path.join(tempfile.gettempdir(), "ci-usage-probe.jsonl")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def has_script_entry(path):
    """Reject inert test modules, without importing/executing their definitions.

    This is a narrow syntax contract, not reachability or coverage analysis.
    Syntax errors still go to Python and receive its ordinary failing exit.
    """
    try:
        tree = ast.parse(Path(path).read_text(encoding='utf8'))
    except (SyntaxError, UnicodeError):
        return True

    def executes(node):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
                             ast.Lambda, ast.Import, ast.ImportFrom)):
            return False
        if isinstance(node, (ast.Call, ast.Assert, ast.Raise)):
            return True
        return any(executes(child) for child in ast.iter_child_nodes(node))

    return any(executes(node) for node in tree.body)


def run_suite(tests_dir, timeout=DEFAULT_TIMEOUT, runner=None):
    """Run each test file; return rows of {file, rc, seconds, tail}.

    rc is an int, "TIMEOUT", or "UNSUPPORTED" for a module without a script entry.
    A timeout is a failure, not a skip: the gate would see it as one too.
    """
    rows = []
    env = _child_env()
    for path in discover(tests_dir):
        started = time.time()
        try:
            if not has_script_entry(path):
                rc, output = 'UNSUPPORTED', 'no direct-script entry; definitions/imports alone do not run tests'
            else:
                proc = subprocess.run(
                    runner or [sys.executable, str(path)],
                    cwd=str(path.parent.parent),
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    env=env,
                )
                rc, output = proc.returncode, (proc.stdout or "") + (proc.stderr or "")
        except subprocess.TimeoutExpired:
            rc, output = "TIMEOUT", ""
        lines = [ln for ln in output.strip().splitlines() if ln.strip()]
        rows.append(
            {
                "file": path.name,
                "rc": rc,
                "seconds": round(time.time() - started, 2),
                "tail": lines[-1][:200] if lines else "",
            }
        )
    return rows


def failures(rows):
    """Failing file names, in order."""
    return [row["file"] for row in rows if row["rc"] not in (0,)]


def new_failures(observed, baseline):
    """The names that fail now and did not fail in the baseline.

    Order preserved from `observed` — the reader wants the suite's order, not a set's.
    """
    known = set(baseline or [])
    return [name for name in observed if name not in known]


def load_baseline(path=BASELINE_PATH):
    path = Path(path)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict) or not isinstance(data.get("failures"), list):
        return None
    return data


def write_baseline(rows, commit, path=BASELINE_PATH):
    data = {
        "commit": commit,
        "measured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "files": len(rows),
        "seconds": round(sum(row["seconds"] for row in rows), 1),
        "failures": failures(rows),
    }
    Path(path).write_text(json.dumps(data, indent=2) + "\n", encoding="utf8")
    return data


def head_commit(repo=REPO_ROOT):
    try:
        return subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=20,
        ).stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def measure_revision(rev, repo=REPO_ROOT, timeout=DEFAULT_TIMEOUT):
    """Measure the suite at another revision, in a throwaway worktree.

    Returns (failures, rows). The worktree is always removed, including on a
    crash, because a second checkout left behind is the next wake's foreign dirt.
    """
    tmp = tempfile.mkdtemp(prefix="landing-suite-")
    worktree = Path(tmp) / "tree"
    try:
        add = subprocess.run(
            ["git", "-C", str(repo), "worktree", "add", "--detach", str(worktree), rev],
            capture_output=True,
            text=True,
        )
        if add.returncode != 0:
            raise RuntimeError(
                "could not create a worktree at %s: %s" % (rev, (add.stderr or "").strip())
            )
        rows = run_suite(worktree / "tests", timeout=timeout)
        if not rows or any(row['rc'] == 'UNSUPPORTED' for row in rows):
            raise RuntimeError('baseline revision has missing or unsupported direct-script tests')
        return failures(rows), rows
    finally:
        subprocess.run(
            ["git", "-C", str(repo), "worktree", "remove", "--force", str(worktree)],
            capture_output=True,
            text=True,
        )
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Answer the landing gate's failure question before the wake ends."
    )
    parser.add_argument("--tests-dir", default=str(REPO_ROOT / "tests"))
    parser.add_argument("--baseline", default=str(BASELINE_PATH))
    parser.add_argument(
        "--against",
        help="measure this revision live in a throwaway worktree (e.g. origin/main)",
    )
    parser.add_argument("--write-baseline", action="store_true")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    tests_dir = Path(args.tests_dir)
    if not tests_dir.is_dir():
        print("landing_suite_check: no tests directory at %s" % tests_dir, file=sys.stderr)
        return 2

    started = time.time()
    rows = run_suite(tests_dir, timeout=args.timeout)
    if not rows:
        print("landing_suite_check: no test_*.py found in %s" % tests_dir, file=sys.stderr)
        return 2
    elapsed = round(time.time() - started, 1)
    observed = failures(rows)
    unsupported = [row['file'] for row in rows if row['rc'] == 'UNSUPPORTED']

    baseline_names, baseline_source = None, "none"
    if args.against:
        try:
            baseline_names, _ = measure_revision(args.against, timeout=args.timeout)
        except RuntimeError as exc:
            print("landing_suite_check: %s" % exc, file=sys.stderr)
            return 2
        baseline_source = args.against
    else:
        baseline = load_baseline(args.baseline)
        if baseline is not None:
            baseline_names = baseline.get("failures", [])
            baseline_source = "%s @ %s" % (
                Path(args.baseline).name,
                baseline.get("commit", "unknown"),
            )

    new = new_failures(observed, baseline_names)

    baseline_written = False
    if args.write_baseline and not unsupported:
        written = write_baseline(rows, head_commit(), Path(args.baseline))
        baseline_written = True
        if not args.json:
            print(
                "baseline written: %s (%d files, %s failures, %ss)"
                % (args.baseline, written["files"], len(written["failures"]), elapsed)
            )
        # Keep the comparison made BEFORE writing; recording is not absolution.

    if args.json:
        print(
            json.dumps(
                {
                    "files": len(rows),
                    "seconds": elapsed,
                    "failures": observed,
                    "baseline_source": baseline_source,
                    "new_failures": new,
                    "unsupported_files": unsupported,
                    "baseline_written": baseline_written,
                    "execution_contract": "direct Python scripts; exit codes, not test coverage",
                    "rows": rows,
                },
                indent=2,
            )
        )
    else:
        print(
            "ran %d test files in %ss — %d failing"
            % (len(rows), elapsed, len(observed))
        )
        for row in rows:
            if row["rc"] not in (0,):
                print("  FAIL %-40s rc=%s %5.1fs %s"
                      % (row["file"], row["rc"], row["seconds"], row["tail"]))
        if baseline_names is None:
            print("baseline: none — every failure above counts as new (safe direction)")
        else:
            print("baseline: %s (%d known)" % (baseline_source, len(baseline_names)))
            if baseline_names and set(observed) <= set(baseline_names):
                print("note: the tree is not clean, but no failure is the wake's own")
        if unsupported:
            print('UNSUPPORTED direct-script tests (setup error; baseline not written):')
            for name in unsupported:
                print('  ' + name)
        elif new:
            print("NEW FAILURES — a landing would be refused:")
            for name in new:
                print("  " + name)
        else:
            print("no new failures")

    return 2 if unsupported else (1 if new else 0)


if __name__ == "__main__":
    sys.exit(main())
