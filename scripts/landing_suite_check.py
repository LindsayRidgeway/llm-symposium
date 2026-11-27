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

What a recorded baseline is allowed to excuse, and the third liability (2026-11-27).
A recorded baseline is one run at one tree, and it has two ways to lie quietly:
it can name a failure with no reason (the "red as weather" excuse this file was
filed about), and it can be *older than a test file*. The second one was measured
today: `tests/landing-baseline.json` said `"files": 242` while `tests/` held 243
`test_*.py`, so any failure in the file nobody had measured would have been
excused by a baseline that never ran it. `write_baseline` therefore records
`measured_files` — every file it actually executed — and `baseline_problems()`
turns the two liabilities into named strings, which
`tests/test_landing_baseline_is_current.py` applies to the committed file at every
landing. A baseline without `measured_files` is a problem, not a legacy format to
be tolerated: deleting the key would be a one-line way to disarm the guard.

Usage:
  python3 scripts/landing_suite_check.py                      # vs the recorded baseline
  python3 scripts/landing_suite_check.py --against origin/main # live, throwaway worktree
  python3 scripts/landing_suite_check.py --against main --repo /path/to/checkout
  python3 scripts/landing_suite_check.py --write-baseline     # record the current failures
  python3 scripts/landing_suite_check.py --verify-baseline --against origin/main
                                                              # does main fail where the recorded
                                                              # baseline names no one? (exit 1, named)
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
# 600, not 120 (raised 2026-11-27). The landing gate's own `failing_tests()` calls every
# test file as a subprocess with `timeout=600`, and the suite contains a test whose own
# inner subprocess timeout is 600 (`tests/test_declutter_audit.py:280`, the auditor run over
# the real tree). At 120 this preflight named that file TIMEOUT -- a *different set of
# failures* from the one the gate names, so the gate's refusal line ("N already failing on
# main before this diff") could not be reconciled with the tool every wake is told to run.
# Measured 2026-11-27 at 2c8cda66: preflight 2 failures of 242 files, the gate 4.
DEFAULT_TIMEOUT = 600


def discover(tests_dir):
    """Every `test_*.py` in the directory, in a stable order."""
    return sorted(Path(tests_dir).glob("test_*.py"))


def _child_env():
    env = dict(os.environ)
    # The gate runs each file with the repository root on PYTHONPATH
    # (`land_runs.failing_tests`) and tests that import a `scripts/` module fail with an
    # ImportError only when it is absent. Both halves of the count must read the same tree
    # the same way or the refusal line cannot be compared with this tool's output.
    env["PYTHONPATH"] = os.pathsep.join(
        [str(REPO_ROOT)] + [q for q in [env.get("PYTHONPATH")] if q]
    )
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


def baseline_problems(baseline, test_names, repo=None):
    """Reasons this baseline cannot be trusted, one string per problem.

    `test_names` is every `test_*.py` the tree holds now. An empty list means the
    baseline measured this exact set of files and every name it excuses carries a
    reason. The two liabilities, in the order a reader wants them:

      * a failure excused without a reason — the "red as weather" defect;
      * a file the baseline never measured — a baseline written before the file
        existed excuses nothing about it, and its failure would hide in the count.

    Strings, not booleans, so the landing gate's refusal can name the problem.
    """
    if baseline is None:
        return ["no recorded baseline: every failure counts as new"]

    problems = []
    measured = baseline.get("measured_files")
    if not isinstance(measured, list):
        problems.append(
            "baseline records no measured_files (written before 2026-11-27), so it "
            "cannot say which test files it ran; re-record it: "
            "python3 scripts/landing_suite_check.py --write-baseline"
        )
        measured = None

    excused = [name for name in (baseline.get("failures") or []) if isinstance(name, str)]
    notes = " ".join(str(note) for note in (baseline.get("notes") or []))

    if measured is not None:
        measured_set = {name for name in measured if isinstance(name, str)}
        # 2026-11-27 (Desi, founder's session): when `repo` is given the reference tree is the
        # tests/ tree *at the commit the baseline cites*, not the tree standing here. Comparing
        # against the live tree made every newly landed test a defect in the baseline, so the only
        # honest baseline was the one written seconds earlier — a guard that demands a ten-minute
        # re-measurement per test file is a guard that gets switched off.
        reference = None
        if repo is not None:
            reference = _test_files_at(str(baseline.get("commit") or ""), repo)
        if reference is None:
            reference = set(test_names)
        for name in sorted(reference - measured_set):
            problems.append("test file not measured by this baseline: %s" % name)
        for name in sorted(measured_set - reference):
            problems.append("baseline measured a test file that is gone: %s" % name)
        if baseline.get("files") != len(measured_set):
            problems.append(
                "baseline says %r files but measured_files names %d"
                % (baseline.get("files"), len(measured_set))
            )
        for name in excused:
            if name not in measured_set:
                problems.append("baseline excuses a failure it never measured: %s" % name)

    for name in excused:
        if name not in notes:
            problems.append("baseline excuses a failure with no reason in notes: %s" % name)

    # The citation. Not a staleness check: a false one. The committed baseline of 2026-11-27 named
    # b1d53f43 and listed a test file that landed after it, because `head_commit()` was read *after*
    # the 320-second measurement in a checkout five other seats land into. The writer now reads HEAD
    # first and measures a pinned worktree; this checks the files already written.
    if repo is not None and measured is not None:
        commit = str(baseline.get("commit") or "")
        present = _test_files_at(commit, repo)
        if present is None:
            problems.append(
                "baseline names commit %r, which this repository does not have: the citation "
                "cannot be checked, so the baseline cannot be trusted" % (commit or "unknown"))
        else:
            for name in sorted(measured_set - present):
                problems.append(
                    "baseline names %s but that file did not exist at %s: the measurement "
                    "describes a different tree than the commit it cites" % (name, commit))
            for name in sorted(present - measured_set):
                problems.append(
                    "baseline cites %s, which held %s, but never measured it: that file's failure "
                    "would be excused by a baseline that did not run it" % (commit, name))

    return problems


def _test_files_at(commit, repo):
    """`test_*.py` names present in tests/ at `commit`, or None when the commit is unknown."""
    if not commit:
        return None
    try:
        r = subprocess.run(["git", "-C", str(repo), "ls-tree", "-r", "--name-only", commit, "tests"],
                           capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    # `.py` only: tests/ also holds JavaScript harnesses named test_*.mjs, and a Python file once
    # sat here as `test_ledger_watch.py.new`. A baseline measures what `discover()` runs.
    return {line.split("/", 1)[1] for line in (r.stdout or "").split()
            if line.startswith("tests/test_") and line.endswith(".py")}


def write_baseline(rows, commit, path=BASELINE_PATH):
    data = {
        "commit": commit,
        "measured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "files": len(rows),
        "seconds": round(sum(row["seconds"] for row in rows), 1),
        "failures": failures(rows),
        # Every file this run executed, not just the count. Without it a baseline
        # written before a test file existed silently excuses that file (measured
        # 2026-11-27: "files": 242 in a tree holding 243 test_*.py).
        "measured_files": sorted(row["file"] for row in rows),
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
    parser.add_argument(
        "--verify-baseline",
        action="store_true",
        help="measure --against REV and name every failure there the recorded baseline does "
             "not excuse (exit 1); the local tree is not run in this mode",
    )
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument(
        "--repo",
        default=str(REPO_ROOT),
        help="repository to resolve --against and HEAD in (default: this checkout); "
             "the tests use it to drive the live path against a fixture",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    tests_dir = Path(args.tests_dir)
    if not tests_dir.is_dir():
        print("landing_suite_check: no tests directory at %s" % tests_dir, file=sys.stderr)
        return 2

    if args.verify_baseline and (not args.against or args.write_baseline):
        print(
            "landing_suite_check: --verify-baseline asks about another revision and writes "
            "nothing here: give it --against origin/main and no --write-baseline",
            file=sys.stderr,
        )
        return 2

    started = time.time()
    # 2026-11-27 (Desi, founder's session). `--write-baseline` measured this live tree for 320
    # seconds and then read HEAD, so a landing from any other seat during the run produced a
    # baseline that cited a commit it had not measured — that is how the morning's file came to
    # name b1d53f43 and list a test that landed after it. It now measures a throwaway worktree
    # pinned to one revision, which cannot straddle a landing, and cites that revision.
    own_tests = Path(args.tests_dir).resolve() == (Path(args.repo) / "tests").resolve()
    if args.write_baseline and not args.against and not args.verify_baseline and own_tests:
        rev = subprocess.run(["git", "-C", str(args.repo), "rev-parse", "HEAD"],
                             capture_output=True, text=True).stdout.strip()
        try:
            _, pinned_rows = measure_revision(rev, repo=Path(args.repo), timeout=args.timeout)
        except (RuntimeError, OSError, subprocess.SubprocessError) as exc:
            print("landing_suite_check: could not measure %s: %s" % (rev[:12], exc), file=sys.stderr)
            return 2
        written = write_baseline(pinned_rows, rev[:7], Path(args.baseline))
        elapsed = round(time.time() - started, 1)
        if args.json:
            print(json.dumps({"baseline": written, "seconds": elapsed}, indent=2))
        else:
            print("baseline written: %s (%d files at %s, %d failures, %ss)"
                  % (args.baseline, written["files"], written["commit"],
                     len(written["failures"]), elapsed))
        return 0

    if args.verify_baseline:
        # Verify mode measures the OTHER revision and holds it against the recorded baseline:
        # "does main fail where the baseline names no one?" The local tree is not run, because
        # it is not what the question is about and a full suite costs minutes.
        try:
            observed, rows = measure_revision(
                args.against, repo=Path(args.repo), timeout=args.timeout
            )
        except RuntimeError as exc:
            print("landing_suite_check: %s" % exc, file=sys.stderr)
            return 2
        elapsed = round(time.time() - started, 1)
        unsupported = []
    else:
        # Read HEAD before the run: if it moves, these rows describe no single commit and the
        # caller must not record them as one.
        commit_before = head_commit(repo=Path(args.repo))
        rows = run_suite(tests_dir, timeout=args.timeout)
        if not rows:
            print("landing_suite_check: no test_*.py found in %s" % tests_dir, file=sys.stderr)
            return 2
        elapsed = round(time.time() - started, 1)
        observed = failures(rows)
        unsupported = [row['file'] for row in rows if row['rc'] == 'UNSUPPORTED']

    baseline_names, baseline_source, defects = None, "none", []
    if args.against and not args.verify_baseline:
        try:
            baseline_names, _ = measure_revision(
                args.against, repo=Path(args.repo), timeout=args.timeout
            )
        except RuntimeError as exc:
            print("landing_suite_check: %s" % exc, file=sys.stderr)
            return 2
        baseline_source = args.against
    else:
        baseline = load_baseline(args.baseline)
        if baseline is not None:
            names = baseline.get("failures")
            baseline_names = names if isinstance(names, list) else None
            baseline_source = "%s @ %s" % (
                Path(args.baseline).name,
                baseline.get("commit", "unknown"),
            )
            if args.verify_baseline:
                # A name earns its excuse from what the file records about it: that these exact
                # files were measured, and why each failing one stays red. Anything less excuses
                # nothing here, because the question is about main, not about this checkout.
                defects = baseline_problems(baseline, [row["file"] for row in rows])
                if defects:
                    baseline_names = None
                    baseline_source += " (unusable: %d defect(s))" % len(defects)

    new = new_failures(observed, baseline_names)

    baseline_written = False
    if args.write_baseline and not unsupported:
        moved = head_commit(repo=Path(args.repo)) != commit_before
        if moved:
            print("landing_suite_check: HEAD moved during the measurement (%s -> %s), so these "
                  "results describe no single commit; baseline NOT written. Re-run it."
                  % (commit_before, head_commit(repo=Path(args.repo))), file=sys.stderr)
            return 2
        written = write_baseline(rows, commit_before, Path(args.baseline))
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
                    "verify_baseline": bool(args.verify_baseline),
                    "baseline_defects": defects,
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
        if defects:
            print("baseline is unusable — it excuses nothing until it records what it measured "
                  "and why each name stays red:")
            for problem in defects:
                print("  " + problem)
        if baseline_names is None:
            print("baseline: none — every failure above counts as new (safe direction)")
        else:
            print("baseline: %s (%d known)" % (baseline_source, len(baseline_names)))
            # The gate's own refusal line prints a count and throws the names away
            # (~/LLM/desi-bot/land_runs.py:884,1107 — the bot's file, not editable here). This
            # is the readable half: the names in hand are printed, both the ones excused and the
            # ones the file still claims but the tree no longer carries.
            known = set(baseline_names)
            excused = [name for name in observed if name in known]
            if excused:
                print("  already failing there, excused by name (the line the gate hides):")
                for name in excused:
                    print("  " + name)
            stale = [name for name in baseline_names if name not in set(observed)]
            if stale:
                print("  named in the baseline but passing there (stale — re-record it):")
                for name in stale:
                    print("  " + name)
            if baseline_names and set(observed) <= known:
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
