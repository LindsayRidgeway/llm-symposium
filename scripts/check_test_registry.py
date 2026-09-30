#!/usr/bin/env python3
"""Fail when a test file exists on disk that no workflow ever runs, or when a workflow
runs a test path that no longer exists.

Why it exists. On 2026-09-30 the verification suite (`test-and-report.yml`) invoked 19 of
the 36 python test files in `tests/` and none of the 7 node page-validators. Seventeen
python tests and every node test had been written, committed, and never executed by
anything. `tests/validate_retraction_page.mjs` had a syntax error and had never once
parsed, and nothing said so, because a test that is never run cannot fail. A test you have
not run is not a test you have; only something that enumerates the directory can tell the
two apart, and no one was enumerating it.

What it checks, in both directions:

  - every `tests/test_*.py` and `tests/validate_*.mjs` is invoked by some workflow step
    (`python3 tests/...` or `node tests/...`), unless it is named in EXEMPT below;
  - every test path a workflow invokes exists on disk — a stale line after a rename is the
    same false claim in the other direction.

Exemptions are printed on every run, and an exemption naming a file that is not on disk is
itself an error, so the list cannot quietly rot into the place where work goes to die.

Usage:
    python3 scripts/check_test_registry.py          # exit 1 if any test file is unrun
    python3 scripts/check_test_registry.py --json
    python3 scripts/check_test_registry.py --tests DIR --workflows DIR   # for the tests
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_TESTS = os.path.join(REPO, "tests")
DEFAULT_WORKFLOWS = os.path.join(REPO, ".github", "workflows")

# Test files deliberately not run by a workflow, with the reason. Keep this empty if you
# can: an entry here is a test the suite does not run, which is the whole defect this
# script exists to name. Every entry must point at a file that exists.
EXEMPT: dict[str, str] = {}

# A test file is anything named tests/test_*.py or tests/validate_*.mjs.
_TEST_FILE = re.compile(r"^(test_[A-Za-z0-9_]+\.py|validate_[A-Za-z0-9_]+\.mjs)$")
# An invocation: an interpreter, whitespace, then a tests/ path. Comment lines are ignored
# so that a test merely *mentioned* in a workflow comment is not counted as run.
_INVOKE = re.compile(r"\b(?:python3?|node)\s+(tests/[A-Za-z0-9_./-]+\.(?:py|mjs))")


def find_test_files(tests_dir: str | None = None) -> list[str]:
    """Every test file on disk, as repo-relative paths, sorted."""
    tests_dir = tests_dir or DEFAULT_TESTS
    if not os.path.isdir(tests_dir):
        return []
    found = [name for name in os.listdir(tests_dir) if _TEST_FILE.match(name)]
    return sorted("tests/" + name for name in found)


def registered_tests(workflows_dir: str | None = None) -> dict[str, str]:
    """Map each test path a workflow runs to the `file:line` that runs it."""
    workflows_dir = workflows_dir or DEFAULT_WORKFLOWS
    found: dict[str, str] = {}
    if not os.path.isdir(workflows_dir):
        return found
    for name in sorted(os.listdir(workflows_dir)):
        if not name.endswith((".yml", ".yaml")):
            continue
        path = os.path.join(workflows_dir, name)
        with open(path, encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, 1):
                if line.lstrip().startswith("#"):
                    continue
                for match in _INVOKE.finditer(line):
                    found.setdefault(match.group(1), f"{name}:{lineno}")
    return found


def unregistered_tests(tests_dir: str | None = None,
                       workflows_dir: str | None = None) -> list[str]:
    """Test files on disk that no workflow runs and that are not exempted."""
    registered = registered_tests(workflows_dir)
    return [p for p in find_test_files(tests_dir)
            if p not in registered and p not in EXEMPT]


def missing_tests(tests_dir: str | None = None,
                  workflows_dir: str | None = None) -> list[tuple[str, str]]:
    """Workflow lines that run a test file which is not on disk, as (path, where)."""
    tests_dir = tests_dir or DEFAULT_TESTS
    on_disk = set(find_test_files(tests_dir))
    return sorted((p, where) for p, where in registered_tests(workflows_dir).items()
                  if p not in on_disk)


def exempt_errors(tests_dir: str | None = None) -> list[str]:
    """Exemptions naming a file that does not exist."""
    on_disk = set(find_test_files(tests_dir))
    return sorted(p for p in EXEMPT if p not in on_disk)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tests", default=None, help="tests directory")
    ap.add_argument("--workflows", default=None, help="workflows directory")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    on_disk = find_test_files(args.tests)
    registered = registered_tests(args.workflows)
    unregistered = unregistered_tests(args.tests, args.workflows)
    missing = missing_tests(args.tests, args.workflows)
    bad_exempt = exempt_errors(args.tests)

    if args.json:
        print(json.dumps({
            "test_files": len(on_disk),
            "registered": len(registered),
            "unregistered": unregistered,
            "missing": [{"path": p, "where": w} for p, w in missing],
            "exempt_errors": bad_exempt,
            "exempt": EXEMPT,
        }, indent=2))
    else:
        print(f"test files on disk: {len(on_disk)}; run by a workflow: "
              f"{len(on_disk) - len(unregistered) - len(EXEMPT)}; exempt: {len(EXEMPT)}")
        for path, reason in sorted(EXEMPT.items()):
            print(f"  exempt  {path} — {reason}")
        if unregistered:
            print("not run by any workflow:")
            for path in unregistered:
                print(f"  UNRUN   {path}")
            runner = "node" if unregistered[0].endswith(".mjs") else "python3"
            print(f"add a `{runner} {unregistered[0]}` line to a workflow, or name it in "
                  "EXEMPT in this script with a reason.")
        if missing:
            print("a workflow runs a test that is not on disk:")
            for path, where in missing:
                print(f"  STALE   {path}  (invoked at {where})")
        if bad_exempt:
            print("EXEMPT names a file that does not exist:")
            for path in bad_exempt:
                print(f"  DEAD    {path}")

    return 1 if (unregistered or missing or bad_exempt) else 0


if __name__ == "__main__":
    sys.exit(main())
