#!/usr/bin/env python3
# Owner: Desi
"""Run the whole offline check suite from one command, so the list cannot go stale.

Written 2026-09-29 after counting what the CI verification job actually ran: it named
**thirteen** test files by hand, and `tests/` held **forty**. The other twenty-seven —
every check added since 2026-09-17, including the ones that pin this month's work — were
never run by anything but a wake that remembered to run them. A hand-kept list of tests is
the same defect as a hand-kept index: it looks complete, it silently omits, and nobody
notices until the omission has already cost something.

This script discovers the tests instead of naming them:

  * every `tests/test_*.py`, run in its own process with its own timeout;
  * every `tests/validate_*.mjs` (the browser-page validators), run with `node` when one
    is on PATH and **reported as skipped** when none is — a skipped check is printed, never
    silently counted as a pass.

A failing test does not stop the others: the point of one run is the whole picture, and a
run that stops at the first failure teaches you only the first thing that is wrong. The
exit code is non-zero if anything failed, so it drops straight into the landing gate that
holds a run's work to "no new failures".

Usage:
  python3 scripts/run_tests.py              # everything
  python3 scripts/run_tests.py --list       # what it would run, then stop
  python3 scripts/run_tests.py --only mail  # only tests whose path contains "mail"
  python3 scripts/run_tests.py --timeout 120
  python3 scripts/run_tests.py --verbose    # print each test's own output, not just failures

Nothing here needs the network, a credential, or a paid model call.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = REPO_ROOT / "tests"
DEFAULT_TIMEOUT = 300


def discover(tests_dir: Path) -> list[Path]:
    """Every check on disk, python first, then the node validators. Sorted, stable."""
    py = sorted(p for p in tests_dir.glob("test_*.py") if p.is_file())
    mjs = sorted(p for p in tests_dir.glob("validate_*.mjs") if p.is_file())
    return py + mjs


def _interpreter(path: Path) -> list[str] | None:
    if path.suffix == ".py":
        return [sys.executable, str(path)]
    if path.suffix == ".mjs":
        node = shutil.which("node")
        return [node, str(path)] if node else None
    return None


def run_one(path: Path, timeout: int) -> dict:
    """Run one check. Never raises: a crash, a timeout and a failure are all results."""
    started = time.time()
    argv = _interpreter(path)
    if argv is None:
        return {"path": path, "status": "skipped", "seconds": 0.0,
                "out": "no node on PATH; browser-page validator not run"}
    try:
        p = subprocess.run(argv, cwd=str(REPO_ROOT), capture_output=True, text=True,
                           timeout=timeout)
        out = (p.stdout or "") + (p.stderr or "")
        status = "passed" if p.returncode == 0 else "failed"
        code = p.returncode
    except subprocess.TimeoutExpired:
        out, status, code = "timed out after %ds" % timeout, "failed", -1
    except OSError as e:  # not executable, interpreter gone
        out, status, code = "could not run: %s" % e, "failed", -1
    return {"path": path, "status": status, "seconds": time.time() - started,
            "out": out, "code": code}


def run_suite(paths: list[Path], timeout: int, verbose: bool, stream=sys.stdout) -> int:
    results = []
    for path in paths:
        r = run_one(path, timeout)
        results.append(r)
        print("%-4s %-46s %6.1fs" % (r["status"].upper(), path.name, r["seconds"]),
              file=stream, flush=True)
        if r["status"] == "failed":
            tail = "\n".join(r["out"].strip().splitlines()[-25:])
            print("      ---- output ----", file=stream)
            for line in tail.splitlines():
                print("      " + line, file=stream)
        elif verbose and r["out"].strip():
            for line in r["out"].strip().splitlines():
                print("      " + line, file=stream)
    passed = [r for r in results if r["status"] == "passed"]
    failed = [r for r in results if r["status"] == "failed"]
    skipped = [r for r in results if r["status"] == "skipped"]
    total = sum(r["seconds"] for r in results)
    print("\n%d check(s): %d passed, %d failed, %d skipped — %.1fs"
          % (len(results), len(passed), len(failed), len(skipped), total), file=stream)
    if failed:
        print("failed:", file=stream)
        for r in failed:
            print("  • %s" % r["path"].name, file=stream)
    if skipped:
        print("skipped (not run — do not read this as a pass):", file=stream)
        for r in skipped:
            print("  • %s" % r["path"].name, file=stream)
    return 1 if failed else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Run every offline check in tests/.")
    ap.add_argument("--list", action="store_true", help="print what would run, then stop")
    ap.add_argument("--only", default=None, metavar="SUBSTRING",
                    help="run only checks whose filename contains this")
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT,
                    help="seconds allowed per check (default %d)" % DEFAULT_TIMEOUT)
    ap.add_argument("--dir", default=str(TESTS_DIR), help=argparse.SUPPRESS)
    ap.add_argument("--verbose", action="store_true", help="print every check's output")
    args = ap.parse_args(argv)

    paths = discover(Path(args.dir))
    if args.only:
        paths = [p for p in paths if args.only in p.name]
    if not paths:
        print("no checks found in %s" % args.dir)
        return 0
    if args.list:
        for p in paths:
            print(p.name)
        print("%d check(s)" % len(paths))
        return 0
    return run_suite(paths, args.timeout, args.verbose)


if __name__ == "__main__":
    raise SystemExit(main())
