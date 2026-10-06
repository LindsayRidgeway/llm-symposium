#!/usr/bin/env python3
"""Every test file in tests/ must be run by CI, or named here as deliberately unrun.

The defect this closes, measured 2026-10-05: of 53 files in `tests/`, **twenty were
invoked by no workflow anywhere in `.github/`**. They existed, they passed offline, and
no landing ever ran them — so the gate that decides whether a change is safe was blind
to two fifths of the repository's checks. Among the unrun were the tests for the email
auto-replier (`tests/test_auto_reply.py`), the task ledger's dedupe rule
(`tests/test_task_ledger.py`), the human-message sanitiser (`tests/test_tell_human_message.py`),
and `tests/test_reject_queue_sweep.py` — which is the sharpest instance, because that
test's own docstring complains that its subject had "no line in
`.github/workflows/test-and-report.yml`" while the complaint was itself unrun.

`tests/test_evidence_table_registration.py` already guards the *cited* case: a test named
in `research/*.md` must exist and be invoked by the workflow. That only covers citations,
and only in `research/`. This guard is the complement: it walks the whole tree and asserts
that **every** tracked `tests/test_*.py` is invoked by something under `.github/`, so the
next test added without a registration line fails here instead of going quietly unrun.

An exemption is allowed, but it must be explicit and carry a reason, and it is itself
checked for staleness — an exemption for a test that is now run is a lie the same way a
missing registration is. The goal is an empty `DELIBERATELY_UNRUN`.

Run:  python3 tests/test_workflow_test_registration.py
"""

import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GITHUB = ROOT / ".github"
CITE = re.compile(r"tests/test_[A-Za-z0-9_]+\.py")

# Tests deliberately not run by any workflow, each with the reason it is exempt.
# Empty is the goal: a test nobody runs is a claim nobody checks.
DELIBERATELY_UNRUN = {
    # "tests/test_example.py": "why no workflow runs it",
}


def cited_tests():
    """Every tests/test_*.py mentioned anywhere under .github/."""
    names = set()
    for path in GITHUB.rglob("*"):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf8", errors="replace")
        except OSError:
            continue
        names.update(CITE.findall(text))
    return names


def tests_on_disk():
    """Every tracked tests/test_*.py, from git (so an untracked scratch file is ignored)."""
    out = subprocess.check_output(
        ["git", "-C", str(ROOT), "ls-files", "tests"]).decode()
    return {f for f in out.split("\n")
            if re.fullmatch(r"tests/test_[A-Za-z0-9_]+\.py", f)}


class WorkflowTestRegistrationTest(unittest.TestCase):
    def test_every_test_is_run_by_ci(self):
        missing = sorted(tests_on_disk() - cited_tests() - set(DELIBERATELY_UNRUN))
        self.assertEqual(
            missing, [],
            "these tests are never run by any workflow under .github/ — add each to a "
            "workflow, or to DELIBERATELY_UNRUN with a reason: " + ", ".join(missing))

    def test_no_stale_exemption(self):
        stale = sorted(t for t in DELIBERATELY_UNRUN if t in cited_tests())
        self.assertEqual(
            stale, [],
            "exempted from CI but actually run by it; drop the exemption: " + ", ".join(stale))

    def test_cited_tests_exist(self):
        ghosts = sorted(t for t in cited_tests() if not (ROOT / t).is_file())
        self.assertEqual(
            ghosts, [],
            "a workflow invokes a test that does not exist: " + ", ".join(ghosts))


if __name__ == "__main__":
    unittest.main(verbosity=2)
