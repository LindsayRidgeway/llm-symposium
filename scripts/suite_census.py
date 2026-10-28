#!/usr/bin/env python3
"""Suite census — what is red right now, per file *and* per test case, written down with a date.

**Why this exists (Desi, 2026-10-27).** The landing gate decides whether a diff may land by
comparing two **sets of test file names** before and after the patch is applied
(`failing_tests()` in the landing machine; see the 2026-10-27T17:31Z report). That answer is
correct as far as it goes and blind in two directions:

  * a **second** failure inside a file that was already red cannot be reported — the name is
    already in the "before" set, so the diff looks unchanged;
  * a **fix** cannot be reported either, so a file can go green and stay listed as red.

Which produces the state the to-do list was in this afternoon: it carried a red list —
"`test_cited_path_gate` (2), `test_daily_report` (1)" — written from a measurement at 17:31Z
and repeated by the 19:31Z wake, which was cut off before it checked. Measured at 21:40Z, all
four of those files pass, under both runners:

    python3 tests/test_cited_path_gate.py      -> exit 0, 23 tests OK
    python3 tests/test_daily_report.py         -> exit 0, 52 tests OK
    python3 tests/test_rover_wake.py           -> exit 0, 46 checks, 0 failed
    python3 tests/test_telegram_media_intake.py-> exit 0, all checks passed

A red list with no date on it is a rumour, and a rumour costs the next wake its whole budget:
144 test files is minutes of wall clock per look, so nobody re-measures and everybody repeats.

**What it does.** Runs every `tests/test_*.py` exactly the way the gate runs it (as a script,
`cwd` and `PYTHONPATH` at the repository root, one subprocess per file, per-file timeout) and
records for each file: status, exit code, elapsed, how many tests it ran, and — the part the
gate cannot hold — the **names of the individual test cases that failed**, parsed from the
output. `--write` saves the record; `--diff` compares it to the record already on disk and
names what is new: newly red files, newly green files, and new failing cases *inside a file
that was already red*.

Usage:

    python3 scripts/suite_census.py                 # census, print, change nothing
    python3 scripts/suite_census.py --write         # census and record it
    python3 scripts/suite_census.py --diff          # census, compare to the record, exit 1 on new damage

Run: python3 tests/test_suite_census.py
"""

import argparse
import json
import os
import re
import pathlib
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_RECORD = os.path.join(REPO, "channels", "suite-census.json")

#: unittest prints `FAIL: test_name (module.Class.test_name)` / `ERROR: ...` for each failure.
#: The print-style harnesses in this repository (`OK   name`, `46 checks, 0 failed`) print a
#: bare `FAIL` line instead, so both shapes are collected; anything else is left to the exit
#: code, which is what the gate uses anyway.
CASE_PATTERNS = (
    re.compile(r"^(?:FAIL|ERROR):\s+(\S+)"),
    re.compile(r"^(?:FAIL|not ok)\b[:\s]+(.*\S)\s*$"),
)
TESTS_RUN = re.compile(r"^Ran (\d+) tests?", re.MULTILINE)


def parse_cases(output):
    """The individual failing test cases named in a suite's output, in the order printed."""
    seen, cases = set(), []
    for line in output.splitlines():
        line = line.strip()
        for pattern in CASE_PATTERNS:
            found = pattern.match(line)
            if not found:
                continue
            name = found.group(1).strip()
            if name.lower() in ("failed", "failure", "failed)"):
                continue
            if name not in seen:
                seen.add(name)
                cases.append(name)
            break
    return cases


def parse_tests_run(output):
    found = TESTS_RUN.search(output)
    return int(found.group(1)) if found else None


def _as_text(stream):
    """One captured stream as text, whatever subprocess handed back: bytes, str, or None."""
    if stream is None:
        return ""
    if isinstance(stream, bytes):
        return stream.decode("utf8", "replace")
    return stream


def run_one(path, repo=REPO, timeout=120):
    """Run one test file the way the landing gate runs it: as a script, from the repo root."""
    env = dict(os.environ)
    env["PYTHONPATH"] = str(repo) + os.pathsep + env.get("PYTHONPATH", "")
    started = time.time()
    try:
        proc = subprocess.run([sys.executable, str(path)], capture_output=True, text=True,
                              cwd=str(repo), env=env, timeout=timeout)
        output = (proc.stdout or "") + (proc.stderr or "")
        code, status = proc.returncode, ("ok" if proc.returncode == 0 else "fail")
    except subprocess.TimeoutExpired as expired:
        # Each stream is coerced on its own: subprocess hands back *bytes* for both even when
        # text=True (CPython 3.9), and either one may be None. Concatenating first and decoding
        # afterwards raises TypeError on the first mixed pair — bytes stdout + None stderr is the
        # ordinary shape when a file prints and then hangs — and the exception escaped this
        # handler, killing the whole census for one file's timeout.
        output = _as_text(expired.stdout) + _as_text(expired.stderr)
        code, status = None, "timeout"
    lines = [l for l in output.splitlines() if l.strip()]
    return {
        "status": status,
        "exit": code,
        "elapsed": round(time.time() - started, 1),
        "tests_run": parse_tests_run(output),
        "cases_failed": parse_cases(output) if status != "ok" else [],
        "last_line": (lines[-1].strip() if lines else ""),
    }


def census(repo=REPO, only=None, jobs=4, timeout=120):
    """Every test file in the repository, measured in parallel and keyed by file name."""
    root = pathlib.Path(repo) / "tests"
    files = sorted(p for p in root.glob("test_*.py") if not only or only in p.name)
    results = {}

    def measure(path):
        return path.name, run_one(path, repo=repo, timeout=timeout)

    with ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
        for name, result in pool.map(measure, files):
            results[name] = result
    return results


def diff(old, new):
    """What changed between two census records — the question a set of names cannot answer."""
    old_files, new_files = old.get("files", {}), new.get("files", {})
    report = {
        "new_files": sorted(set(new_files) - set(old_files)),
        "gone_files": sorted(set(old_files) - set(new_files)),
        "newly_red": [],       # green before, red now: the gate sees this one too
        "newly_green": [],     # red before, green now: the gate cannot see this one
        "new_cases": [],       # a *new* failure inside a file that was already red: the mask
        "fixed_cases": [],     # a named case that stopped failing inside a file still red
    }
    for name in sorted(set(old_files) & set(new_files)):
        before, after = old_files[name], new_files[name]
        was_red, is_red = before.get("status") != "ok", after.get("status") != "ok"
        if is_red and not was_red:
            report["newly_red"].append(name)
        elif was_red and not is_red:
            report["newly_green"].append(name)
        elif was_red and is_red:
            appeared = [c for c in after.get("cases_failed", [])
                        if c not in before.get("cases_failed", [])]
            vanished = [c for c in before.get("cases_failed", [])
                        if c not in after.get("cases_failed", [])]
            if appeared:
                report["new_cases"].append((name, appeared))
            if vanished:
                report["fixed_cases"].append((name, vanished))
    report["damage"] = bool(report["newly_red"] or report["new_cases"])
    return report


def label(path, repo=REPO):
    """A path as the reader sees it: relative inside the repository, absolute outside it."""
    relative = os.path.relpath(path, repo)
    return path if relative.startswith("..") else relative


def load(path):
    try:
        with open(path, encoding="utf8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return None


def save(path, record):
    directory = os.path.dirname(path)
    if directory and not os.path.isdir(directory):
        os.makedirs(directory)
    with open(path, "w", encoding="utf8") as handle:
        json.dump(record, handle, indent=1, sort_keys=True)
        handle.write("\n")


def print_census(files, stream=sys.stdout):
    red = {n: r for n, r in files.items() if r["status"] != "ok"}
    for name, result in sorted(red.items()):
        cases = ", ".join(result["cases_failed"][:4]) or result["last_line"][:70]
        stream.write("%-8s %-44s %s\n" % (result["status"].upper(), name, cases))
    stream.write("\n%d file(s): %d ok, %d red\n"
                 % (len(files), len(files) - len(red), len(red)))


def print_diff(report, stream=sys.stdout):
    if not any(report[key] for key in ("newly_red", "newly_green", "new_cases",
                                      "fixed_cases", "new_files", "gone_files")):
        stream.write("no change since the recorded census\n")
        return
    for name in report["newly_red"]:
        stream.write("NEWLY RED   %s\n" % name)
    for name, cases in report["new_cases"]:
        stream.write("NEW CASES   %s: %s\n" % (name, ", ".join(cases[:6])))
    for name in report["newly_green"]:
        stream.write("now green   %s\n" % name)
    for name, cases in report["fixed_cases"]:
        stream.write("case fixed  %s: %s\n" % (name, ", ".join(cases[:6])))
    for name in report["new_files"]:
        stream.write("new file    %s\n" % name)
    for name in report["gone_files"]:
        stream.write("gone        %s\n" % name)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=REPO, help="repository root (default: this one)")
    parser.add_argument("--only", default=None, help="census only files whose name contains this")
    parser.add_argument("--jobs", type=int, default=4, help="how many files to run at once")
    parser.add_argument("--timeout", type=int, default=120, help="per-file timeout in seconds")
    parser.add_argument("--record", default=DEFAULT_RECORD, help="where the census is recorded")
    parser.add_argument("--write", action="store_true", help="record this census")
    parser.add_argument("--diff", action="store_true",
                        help="compare with the recorded census; exit 1 on new damage")
    args = parser.parse_args(argv)

    files = census(args.repo, only=args.only, jobs=args.jobs, timeout=args.timeout)
    record = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "runner": "python3 <file> (cwd=repo root, PYTHONPATH=repo root) — the gate's shape",
        "files": files,
        "summary": {"total": len(files),
                    "red": sum(1 for r in files.values() if r["status"] != "ok")},
    }
    print_census(files)

    previous = load(args.record) if (args.diff or args.write) else None
    report = diff(previous, record) if previous else None
    if report:
        sys.stdout.write("\nagainst %s (%s)\n"
                         % (label(args.record, args.repo),
                            previous.get("generated_at", "undated")))
        print_diff(report)
    if args.write:
        save(args.record, record)
        sys.stdout.write("\nrecorded: %s\n" % label(args.record, args.repo))
    if report and report["damage"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
