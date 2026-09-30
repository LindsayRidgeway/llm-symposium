#!/usr/bin/env python3
"""Pin `scripts/check_test_registry.py` — the check that every test file is actually run.

Two halves:

  - the live repository is complete: every `tests/test_*.py` and `tests/validate_*.mjs` is
    invoked by some workflow, and every test a workflow invokes exists on disk. This is the
    assertion that would have failed on 2026-09-30, when 22 test files were on disk and
    unrun.
  - the checker itself is not vacuous: given a directory holding one unregistered test, it
    must report it; given a workflow that runs a file that is gone, it must report that too;
    given an exemption naming a missing file, it must report that. A checker that always
    returns "fine" would pass the first half for the wrong reason.

Run: python3 tests/test_test_registry.py
"""
from __future__ import annotations

import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import check_test_registry as ctr  # noqa: E402

PASSED = 0
FAILED = 0


def check(label: str, ok: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if ok:
        PASSED += 1
        print(f"PASS  {label}" + (f"  {detail}" if detail else ""))
    else:
        FAILED += 1
        print(f"FAIL  {label}  {detail}")


def _write(path: str, text: str = "") -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def with_tree(files: dict[str, str], workflow: str):
    """Build a throwaway tests/ + workflows/ pair and hand back the two directories."""
    root = tempfile.mkdtemp(prefix="test-registry-")
    tests = os.path.join(root, "tests")
    flows = os.path.join(root, "workflows")
    for name, body in files.items():
        _write(os.path.join(tests, name), body)
    _write(os.path.join(flows, "ci.yml"), workflow)
    return tests, flows


# --- the live repository ----------------------------------------------------

disk = ctr.find_test_files()
check("the tests directory yields test files", len(disk) >= 30, f"{len(disk)} on disk")

unrun = ctr.unregistered_tests()
check("every test file on disk is run by a workflow", not unrun,
      "" if not unrun else f"unrun: {', '.join(unrun)}")

missing = ctr.missing_tests()
check("every test a workflow runs exists on disk", not missing,
      "" if not missing else f"stale: {missing}")

check("no exemption is empty-handed (EXEMPT names no missing file)",
      not ctr.exempt_errors(), str(ctr.exempt_errors()))

# Counted separately from the checks above so that a test renamed out of the naming
# convention is noticed: the two node validators that do live fetches must be registered
# too, not quietly dropped.
names = {os.path.basename(p) for p in disk}
check("the node page-validators are part of the registry",
      any(n.endswith(".mjs") for n in names) and len([n for n in names if n.endswith(".mjs")]) == 7,
      f"{len([n for n in names if n.endswith('.mjs')])} node validators")

# --- the checker's own detection --------------------------------------------

tests, flows = with_tree(
    {"test_ran.py": "", "test_ignored.py": ""},
    "      - run: python3 tests/test_ran.py\n")
unrun = ctr.unregistered_tests(tests, flows)
check("a test file that no workflow runs is reported", unrun == ["tests/test_ignored.py"],
      str(unrun))

tests, flows = with_tree(
    {"test_ran.py": ""},
    "      - run: python3 tests/test_ran.py\n      - run: node tests/test_gone.py\n")
missing = ctr.missing_tests(tests, flows)
check("a workflow running a test that is not on disk is reported",
      missing == [("tests/test_gone.py", "ci.yml:2")], str(missing))

tests, flows = with_tree({}, "      # run: python3 tests/test_commented.py\n")
check("a test naming in a comment is not mistaken for a run",
      ctr.registered_tests(flows) == {}, str(ctr.registered_tests(flows)))

tests, flows = with_tree(
    {"test_a.py": "", "not_a_test.py": "", "helper.mjs": ""},
    "      - run: python3 tests/test_a.py\n")
check("only test_*.py and validate_*.mjs are registry material",
      ctr.find_test_files(tests) == ["tests/test_a.py"], str(ctr.find_test_files(tests)))

tests, flows = with_tree({"test_a.py": ""}, "")
saved = ctr.EXEMPT.copy()
try:
    ctr.EXEMPT["tests/missing.py"] = "runs nowhere"
    check("an exemption for a file that does not exist is an error",
          ctr.exempt_errors(tests) == ["tests/missing.py"], str(ctr.exempt_errors(tests)))
finally:
    ctr.EXEMPT.clear()
    ctr.EXEMPT.update(saved)

print(f"{PASSED}/{PASSED + FAILED} tests passed")
sys.exit(1 if FAILED else 0)
