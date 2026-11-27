#!/usr/bin/env python3
"""How many test methods each file in tests/ carries, and whether any of them went missing (Desi, 2026-11-27).

The queue item's own example, and it is a true one: commit `f8476bb2` ("the rest of
red-tests-on-main") carried `tests/test_landing_baseline_is_current.py` back from **29** test methods
to **18**. Nothing failed. The file still ran, still printed OK, and was a third smaller than the one
that had landed an hour earlier — because the commit restored an older copy of the file over a newer
one. It was caught by a reader (a wake filing `test-count-cannot-quietly-drop`), not by a guard, and
in the meantime a repaired baseline was checked by eleven fewer assertions than its author believed.

A file that loses tests is the quietest failure this repository has: every remaining test passes, the
suite is green, and the coverage that disappeared was exactly the coverage nobody was watching. `git
diff --stat` shows a line count; it does not say that a file went from 29 checks to 18.

WHAT THIS MEASURES. `def test_` per file — the same shape in unittest, in the minirunner ports, and in
the hand-rolled pytest-style files. It is a proxy, not a proof: a test rewritten as a loop counts as
one, and a deleted test replaced by a stronger one is still a loss by this count. That is the right
bias for a guard — it asks a human to say "yes, fewer, on purpose" rather than letting the drop pass.

    python3 scripts/test_count_baseline.py --write     # record the counts, with the commit and date
    python3 scripts/test_count_baseline.py --check     # exit 1 if any file lost tests
    python3 scripts/test_count_baseline.py --check --json

A drop can be allowed, but only by naming it: add the file to `allowed_drops` in the baseline with the
new count and a reason. A reason that is not written down is how "it went down and nobody minded" is
how this file would become decoration.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BASELINE = REPO / "tests" / "test-count-baseline.json"
TESTS = REPO / "tests"
COUNT = re.compile(r"(?m)^\s*def test_")


def counts(tests_dir: Path = TESTS) -> dict:
    """{file name: number of `def test_` in it} for every tests/test_*.py."""
    out = {}
    for path in sorted(tests_dir.glob("test_*.py")):
        try:
            out[path.name] = len(COUNT.findall(path.read_text(encoding="utf-8", errors="replace")))
        except OSError:
            continue
    return out


def head(repo: Path = REPO) -> str:
    try:
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True, timeout=20).stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def problems(baseline: dict, now: dict) -> list:
    """Files that lost tests, or vanished, without being named. Pure: both arguments are given."""
    if not isinstance(baseline, dict) or not isinstance(baseline.get("counts"), dict):
        return ["no recorded counts: every file is unmeasured, so a drop cannot be seen"]
    recorded = baseline["counts"]
    allowed = baseline.get("allowed_drops") or {}
    found = []
    for name, was in sorted(recorded.items()):
        if name not in now:
            if name in allowed:
                continue
            found.append("%s is gone from tests/ (it had %d test methods)" % (name, was))
            continue
        if now[name] < was and name not in allowed:
            found.append("%s went from %d to %d test methods (%d fewer) and no reason is recorded"
                         % (name, was, now[name], was - now[name]))
    for name, why in sorted(allowed.items()):
        if not isinstance(why, dict) or not why.get("because"):
            found.append("%s is allowed to lose tests with no `because` written down" % name)
    return found


def write(tests_dir: Path = TESTS, path: Path = BASELINE, repo: Path = REPO) -> dict:
    baseline = {
        "commit": head(repo),
        "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "note": ("How many `def test_` each file in tests/ carried when this was recorded. A landing "
                 "that reduces one must say so in allowed_drops, with a reason. See "
                 "scripts/test_count_baseline.py for why a drop is invisible otherwise."),
        "counts": counts(tests_dir),
        # Kept across re-recordings: a reason once given is still the reason.
        "allowed_drops": (json.loads(path.read_text(encoding="utf-8")).get("allowed_drops")
                          if path.is_file() else {}),
    }
    path.write_text(json.dumps(baseline, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return baseline


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="record the counts now")
    ap.add_argument("--check", action="store_true", help="compare and exit 1 on an unexplained drop")
    ap.add_argument("--tests", type=Path, default=TESTS)
    ap.add_argument("--baseline", type=Path, default=BASELINE)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.write:
        b = write(args.tests, args.baseline)
        total = sum(b["counts"].values())
        print("recorded %d file(s), %d test method(s) at %s" % (len(b["counts"]), total, b["commit"]))
        return 0

    try:
        baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        baseline = None
        if args.json:
            print(json.dumps({"problems": ["no readable baseline: %s" % exc]}))
        else:
            print("test_count_baseline: no readable baseline at %s (%s)" % (args.baseline, exc))
        return 2

    found = problems(baseline, counts(args.tests))
    if args.json:
        print(json.dumps({"problems": found, "recorded_commit": baseline.get("commit")}, indent=2))
    elif found:
        print("test_count_baseline: %d file(s) lost tests, unexplained:" % len(found))
        for line in found:
            print("  " + line)
        print("\nIf the loss is deliberate, add it to `allowed_drops` in %s with a `because`."
              % args.baseline.name)
    else:
        print("test_count_baseline: no file lost tests since %s" % baseline.get("commit"))
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
