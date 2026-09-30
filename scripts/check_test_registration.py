#!/usr/bin/env python3
"""Fail the build when a test file exists on disk but no CI workflow ever runs it.

Why this exists (2026-09-30, Desi). The 04:10Z wake found one case of a research
write-up claiming a test that had never been written. Looking wider in the 08:11Z
wake — cut off before it wrote anything — the same class of hole sits one level up:
test files that DO exist but that the verification suite never invokes. A test nobody
runs is not a test; it is a comment that happens to be executable. It cannot fail, so
it cannot warn anyone, and it decays silently. Two of the files this check first
found were in fact broken (a syntax error, and a missing default argument), and had
been for as long as they had existed, because nothing ever called them.

Two ways a test file can be invisible:
  1. it is named in no workflow at all — nothing runs it, ever; or
  2. it needs an argument/workflow the suite does not supply — it runs and dies on
     the first line. Case 1 is what this script catches mechanically. Case 2 is what
     running each newly-registered test by hand caught; both first-found examples
     were case 2 hiding behind case 1.

What counts as "run". A test file is registered if its path appears anywhere under
`.github/workflows/` — as `python3 tests/foo.py` in the offline suite, or as the
subject of a dedicated job. Matching the path rather than a job name keeps the check
honest about how many test files are actually invoked.

Tests that a workflow genuinely cannot run — because they go to the live network and
the verification suite is offline by design — are listed in EXEMPT below, each with a
reason. The list is not an excuse pile: the check also fails if an entry names a file
that does not exist, so the exempt list cannot rot into fiction.

Usage:
    python3 scripts/check_test_registration.py            # repo root, exit 1 on a hole
    python3 scripts/check_test_registration.py --quiet    # summary line only
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = ROOT / "tests"
WORKFLOWS_DIR = ROOT / ".github" / "workflows"

# Test files deliberately not run by the verification workflow, each with the reason.
# These are the ones whose whole point is a live external service, which the offline
# suite must not depend on. They are run by hand when the page they check changes;
# tests/validate_retraction_page.mjs and tests/validate_trials_page.mjs were both
# repaired on 2026-09-30 after this check made them visible.
EXEMPT: dict[str, str] = {
    "validate_retraction_page.mjs": "fetches OpenAlex/Crossref live; not run in the offline suite",
    "validate_trials_page.mjs": "fetches the live clinical-trials registry; not run in the offline suite",
    "validate_recalls_page.mjs": "fetches the live openFDA enforcement API; not run in the offline suite",
    "validate_food_safety_page.mjs": "fetches the live openFDA food-enforcement API; not run in the offline suite",
    "validate_unreported_trials_page.mjs": "fetches the live registry; not run in the offline suite",
    "validate_fetchable_page.mjs": "fetches the pages it checks over the live network; not run in the offline suite",
}

# A test file is any tests/*.py named test_* or any tests/*.mjs named validate_*.
TEST_FILE_RE = re.compile(r"^test_.*\.py$|^validate_.*\.mjs$")
# A reference to a test file from inside a workflow (any path segment under tests/).
REFERENCE_RE = re.compile(r"tests/([A-Za-z0-9_.-]+\.(?:py|mjs))")


def collect_test_files(tests_dir: Path) -> list[str]:
    """Every test file that lives in tests/, by basename, sorted."""
    names = [p.name for p in tests_dir.iterdir() if p.is_file() and TEST_FILE_RE.match(p.name)]
    return sorted(names)


def collect_registered(workflows_dir: Path) -> set[str]:
    """Every test-file basename mentioned by any workflow, by basename."""
    registered: set[str] = set()
    if not workflows_dir.is_dir():
        return registered
    for wf in sorted(workflows_dir.glob("*.yml")) + sorted(workflows_dir.glob("*.yaml")):
        text = wf.read_text(encoding="utf-8", errors="replace")
        registered.update(REFERENCE_RE.findall(text))
    return registered


def find_unregistered(tests_dir: Path, workflows_dir: Path, exempt: dict[str, str]) -> list[str]:
    """Test files that exist, are not named in any workflow, and are not exempt."""
    registered = collect_registered(workflows_dir)
    return [n for n in collect_test_files(tests_dir) if n not in registered and n not in exempt]


def stale_exemptions(tests_dir: Path, exempt: dict[str, str]) -> list[str]:
    """Exempt entries that no longer name a test file on disk."""
    present = set(collect_test_files(tests_dir))
    return [n for n in exempt if n not in present]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quiet", action="store_true", help="print only the summary line")
    args = ap.parse_args()

    tests_dir, workflows_dir = TESTS_DIR, WORKFLOWS_DIR
    all_tests = collect_test_files(tests_dir)
    registered = collect_registered(workflows_dir)
    unregistered = find_unregistered(tests_dir, workflows_dir, EXEMPT)
    stale = stale_exemptions(tests_dir, EXEMPT)

    if not args.quiet:
        print(f"test files on disk:  {len(all_tests)}")
        print(f"named by a workflow: {len(all_tests) - len(unregistered) - len([n for n in all_tests if n in EXEMPT])}")
        print(f"exempt (live net):   {len([n for n in all_tests if n in EXEMPT])}")

    problems: list[str] = []
    for name in unregistered:
        problems.append(f"UNRUN TEST: tests/{name} is named by no workflow — nothing ever runs it")
    for name in stale:
        problems.append(f"STALE EXEMPTION: {name} is exempt but no longer exists on disk")

    if problems:
        if not args.quiet:
            print()
            for line in problems:
                print("  " + line)
        print(f"check_test_registration: {len(problems)} problem(s)")
        return 1

    print(f"check_test_registration: OK ({len(all_tests)} test files, all either run or exempt)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
