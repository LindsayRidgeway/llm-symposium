#!/usr/bin/env python3
"""Run every test in tests/ and name what fails (Desi, 2026-11-27).

Why this exists. The landing gate runs `tests/test_*.py` only when a wake lands, and it compares the
result against what main was already doing — so a test that goes red on main is nobody's failure and
nobody's alarm. Two instances, both measured on 2026-11-27:

  * `tests/test_mjs_validators_parse.py` was red on main from 759aaba5 onwards, because a substring
    scan could not tell `process.argv[2] === "record"` from a read. Found by running the suite by hand.
  * nothing else would have found it: the workflow runs a named subset, and the gate runs the rest
    only during a landing.

So: once a day, run the lot, write down what happened, and say the names. The report is the point —
this does not page anyone (the founder asked in November for the daily Telegram reports to stop).
A red suite has to be visible in the record before it can be anybody's job to fix it.

    python3 scripts/suite_watch.py                 # all of tests/test_*.py, 6 at a time
    python3 scripts/suite_watch.py --jobs 1        # one at a time, for a quiet machine
    python3 scripts/suite_watch.py --only test_landing --json
    python3 scripts/suite_watch.py --list          # what it would run

Exit: 0 all green, 1 something failed or timed out, 2 could not measure (no tests found).
Two traps this is built around, both seen in this repository:
  * a runner that collects nothing reports success, so an empty test list is a defect, not a rest;
  * one genuinely slow file (`test_declutter_audit.py`, 327 s) is not a hang, so the timeout is
    per file and generous, and a timeout is reported as its own outcome rather than as a failure.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TESTS = REPO / "tests"
PYTHON = sys.executable
TIMEOUT = 900
JOBS = 6
REPORT_DIR = REPO / "channels" / "reports" / "suite"


def test_files(tests_dir: Path = TESTS) -> list:
    return sorted(p for p in Path(tests_dir).glob("test_*.py") if p.is_file())


def head(repo: Path = REPO) -> str:
    try:
        r = subprocess.run(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
                           capture_output=True, text=True, timeout=30)
        return (r.stdout or "").strip() or "unknown"
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"


def run_one(path: Path, timeout: int = TIMEOUT) -> dict:
    started = time.time()
    try:
        r = subprocess.run([PYTHON, str(path)], capture_output=True, text=True,
                           cwd=str(REPO), timeout=timeout,
                           # The amigo jobs set no PATH, and these tests look for node and for
                           # git; give the child the same ordinary environment a person has.
                           env=dict(os.environ, PATH=os.environ.get(
                               "PATH", "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin")))
    except subprocess.TimeoutExpired:
        return {"file": path.name, "outcome": "timeout", "seconds": round(time.time() - started, 1),
                "tail": "no exit after %d s" % timeout}
    except OSError as exc:
        return {"file": path.name, "outcome": "could_not_run", "seconds": 0.0,
                "tail": "%s: %s" % (type(exc).__name__, exc)}
    body = ((r.stdout or "") + (r.stderr or "")).strip()
    return {"file": path.name,
            "outcome": "ok" if r.returncode == 0 else "failed",
            "rc": r.returncode,
            "seconds": round(time.time() - started, 1),
            "tail": "\n".join(body.splitlines()[-6:])}


def run_suite(files: list, jobs: int = JOBS, timeout: int = TIMEOUT) -> list:
    files = list(files)
    if not files:
        return []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
        return list(pool.map(lambda p: run_one(p, timeout=timeout), files))


def summarise(results: list) -> dict:
    by = {"ok": [], "failed": [], "timeout": [], "could_not_run": []}
    for row in results:
        by.setdefault(row["outcome"], []).append(row["file"])
    return {"ran": len(results), "ok": by.pop("ok", []), **by}


def report(results: list, commit: str, seconds: float) -> dict:
    return {"commit": commit, "measured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "seconds": round(seconds, 1), "summary": summarise(results), "results": results}


def write_report(data: dict, report_dir: Path = REPORT_DIR) -> Path:
    report_dir = Path(report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    stamp = data["measured_at"].replace(":", "").replace("-", "")
    latest = report_dir / "latest.json"
    path = report_dir / ("%s-%s.json" % (stamp, data.get("commit", "unknown")))
    body = json.dumps(data, indent=1) + "\n"
    path.write_text(body, encoding="utf-8")
    latest.write_text(body, encoding="utf-8")
    return latest


def lines(data: dict) -> list:
    """What a reader needs, in the order they need it: the names first, the totals after."""
    s = data["summary"]
    out = []
    for row in data["results"]:
        if row["outcome"] == "ok":
            continue
        out.append("%-14s %s (%s s)%s" % (row["outcome"], row["file"], row["seconds"],
                                          (": " + row["tail"].splitlines()[-1][:160])
                                          if row.get("tail") else ""))
    out.append("suite_watch: %d file(s) at %s — %d ok, %d failed, %d timeout, %d could not run (%.0f s)"
               % (s["ran"], data.get("commit", "?"), len(s.get("ok") or []), len(s.get("failed") or []),
                  len(s.get("timeout") or []), len(s.get("could_not_run") or []), data.get("seconds", 0)))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", help="run only files whose name contains this")
    ap.add_argument("--jobs", type=int, default=JOBS)
    ap.add_argument("--timeout", type=int, default=TIMEOUT)
    ap.add_argument("--tests-dir", default=str(TESTS))
    ap.add_argument("--no-report", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    files = test_files(Path(args.tests_dir))
    if args.only:
        files = [p for p in files if args.only in p.name]
    if args.list:
        for p in files:
            print(p.name)
        return 0
    if not files:
        print("suite_watch: no test files under %s — a run that measures nothing must not report "
              "success" % args.tests_dir)
        return 2

    started = time.time()
    results = run_suite(files, jobs=args.jobs, timeout=args.timeout)
    data = report(results, head(), time.time() - started)
    if not args.no_report:
        path = write_report(data)
        data["report"] = str(path)
    if args.json:
        print(json.dumps(data, indent=1))
    else:
        for line in lines(data):
            print(line)
    bad = len(data["summary"].get("failed") or []) + len(data["summary"].get("timeout") or []) \
        + len(data["summary"].get("could_not_run") or [])
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
