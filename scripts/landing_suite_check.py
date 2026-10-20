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

So this runs the suite in the work tree the wake is editing, and answers the
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
  python3 scripts/landing_suite_check.py --refusal <run dir>   # was a refusal true?

Exit status: 0 = no new failures (a landing would not have been refused for this);
1 = new failures, named; 2 = usage or setup error (git, missing tests).

`--refusal` was added 2026-10-20, because the gate's sentence is a *claim* and a
claim can be wrong. It reads a run's `landing_failed.txt` and `changes.patch`,
applies the patch to a throwaway worktree at the base, and runs **only the tests
the refusal named** — before and after. The finding that made it necessary is in
`channels/reports/2026-10-20-desi-was-the-refusal-true.md`; the short version is
that the gate measures both sides of its comparison in the live shared checkout,
not at the run's own base, so a tree that is not `main` can hand a diff a failure
it did not write.
"""
from __future__ import annotations

import argparse
import json
import os
import re
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


def run_suite(tests_dir, timeout=DEFAULT_TIMEOUT, runner=None):
    """Run each test file; return rows of {file, rc, seconds, tail}.

    rc is an int, or the string "TIMEOUT" for a file that outlived its limit.
    A timeout is a failure, not a skip: the gate would see it as one too.
    """
    rows = []
    env = _child_env()
    for path in discover(tests_dir):
        started = time.time()
        try:
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
        return failures(rows), rows
    finally:
        subprocess.run(
            ["git", "-C", str(repo), "worktree", "remove", "--force", str(worktree)],
            capture_output=True,
            text=True,
        )
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# Adjudicating a refusal that has already happened (added 2026-10-20).
#
# `land_runs.py` says "this run's diff introduced new failures: <test>" after the
# run is over, and it measures both sides of that comparison in the live shared
# checkout rather than at the run's own base. Measured on 2026-10-20:
#
#   * the two runs refused that day named `test_ci_spend_audit.py` and
#     `test_repair_ledger_conflicts.py`; both pass on a clean `main` (25 and 14
#     tests, rc=0), and the 13:12Z run's own patch, applied inside its own
#     checkout, passes the named test too — so for that run the sentence was
#     false as written;
#   * at 13:2xZ the shared checkout was missing three tracked files that `main`
#     carries and held an uncommitted append to `channels/items.jsonl`: a tree
#     that is not `main`, where any repository-wide audit can disagree with the
#     one measured seconds earlier.
#
# So the claim is checkable in one worktree and two runs of the *named* test.
# The exit status is the answer: 1 = the refusal was true, 0 = it was not
# reproducible, 2 = it could not be checked from here (base moved, no record).

_TEST_NAME = re.compile(r"[A-Za-z0-9_./-]+\.py")


def parse_refusal(text):
    """Test file names named by a `landing_failed.txt`, in order, no duplicates."""
    names = []
    for token in _TEST_NAME.findall(text or ""):
        name = Path(token).name
        if name.startswith("test_") and name not in names:
            names.append(name)
    return names


def judge(named, at_base, after_patch):
    """Was the refusal caused by the diff? -> (verdict, exit status, detail)."""
    base, after = set(at_base), set(after_patch)
    detail = {
        "caused": [n for n in named if n not in base and n in after],
        "preexisting": [n for n in named if n in base and n in after],
        "fixed_by_patch": [n for n in named if n in base and n not in after],
        "not_reproduced": [n for n in named if n not in base and n not in after],
    }
    if not named:
        return "NO TEST NAMED: nothing in the refusal record to check", 2, detail
    if detail["caused"]:
        return "SUPPORTED: the diff introduces the named failure", 1, detail
    if detail["preexisting"] and not detail["not_reproduced"]:
        return "NOT CAUSED: the named test fails without the diff as well", 0, detail
    return "NOT REPRODUCED: the named test passes with the diff applied", 0, detail


def run_named(tests_dir, names, timeout=DEFAULT_TIMEOUT):
    """Run just these test files. -> (failing names, names absent from the tree)."""
    env = _child_env()
    failing, missing = [], []
    for name in names:
        path = Path(tests_dir) / name
        if not path.exists():
            missing.append(name)  # an absent test cannot be the gate's failure
            continue
        try:
            proc = subprocess.run(
                [sys.executable, str(path)],
                cwd=str(path.parent.parent),
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
            )
            if proc.returncode != 0:
                failing.append(name)
        except subprocess.TimeoutExpired:
            failing.append(name)
    return failing, missing


def adjudicate_refusal(run_dir, repo=REPO_ROOT, rev="HEAD", timeout=DEFAULT_TIMEOUT):
    """Check a past refusal against the diff it blames. -> (detail, exit status)."""
    run_dir = Path(run_dir)
    detail = {"run": run_dir.name, "rev": rev, "named": [], "verdict": "", "applied": False}
    failure_file = run_dir / "landing_failed.txt"
    patch = run_dir / "changes.patch"
    if not failure_file.exists() or not patch.exists():
        detail["verdict"] = "NO REFUSAL RECORD: %s needs landing_failed.txt and changes.patch" % run_dir
        return detail, 2
    named = parse_refusal(failure_file.read_text(encoding="utf8", errors="replace"))
    detail["named"] = named
    if not named:
        detail["verdict"] = "NO TEST NAMED: %s names no test_" % failure_file
        return detail, 2

    tmp = tempfile.mkdtemp(prefix="landing-refusal-")
    worktree = Path(tmp) / "tree"
    try:
        add = subprocess.run(
            ["git", "-C", str(repo), "worktree", "add", "--detach", str(worktree), rev],
            capture_output=True,
            text=True,
        )
        if add.returncode != 0:
            detail["verdict"] = "CANNOT ADJUDICATE: no worktree at %s (%s)" % (
                rev, (add.stderr or "").strip()[:200])
            return detail, 2
        at_base, missing = run_named(worktree / "tests", named, timeout)
        detail["at_base"], detail["missing_at_base"] = at_base, missing
        applied = subprocess.run(
            ["git", "-C", str(worktree), "apply", str(patch.resolve())],
            capture_output=True,
            text=True,
        )
        if applied.returncode != 0:
            detail["apply_error"] = (applied.stderr or "").strip()[:300]
            detail["verdict"] = (
                "CANNOT ADJUDICATE: the patch does not apply at %s — the base has moved "
                "since the run, so the failure cannot be reproduced from here" % rev
            )
            return detail, 2
        detail["applied"] = True
        after, _ = run_named(worktree / "tests", named, timeout)
        detail["after_patch"] = after
        verdict, status, judged = judge(named, at_base, after)
        detail.update(judged)
        detail["verdict"] = verdict
        return detail, status
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

    if args.write_baseline:
        written = write_baseline(rows, head_commit(), Path(args.baseline))
        if not args.json:
            print(
                "baseline written: %s (%d files, %s failures, %ss)"
                % (args.baseline, written["files"], len(written["failures"]), elapsed)
            )
        # Writing a baseline is not a landing decision: report the same verdict.
        new = []

    if args.json:
        print(
            json.dumps(
                {
                    "files": len(rows),
                    "seconds": elapsed,
                    "failures": observed,
                    "baseline_source": baseline_source,
                    "new_failures": new,
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
        if new:
            print("NEW FAILURES — a landing would be refused:")
            for name in new:
                print("  " + name)
        else:
            print("no new failures")

    return 1 if new else 0


if __name__ == "__main__":
    sys.exit(main())
