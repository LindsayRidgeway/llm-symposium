#!/usr/bin/env python3
"""Every test on disk must be run by the verification suite.

Why this exists. On 2026-10-06 the repository held 55 `tests/test_*.py` files and the
verification workflow (`.github/workflows/test-and-report.yml`, the "Run Offline
Verification Suite" step) named 33 of them. Twenty-two tests — including the
reject-queue sweep, the task-ledger dedupe, the boilerplate-strip check, and the
falsy-zero screen-rule audit — existed, passed, and were run by nothing. A test that
is never run is not a guard; it is a comment with a docstring.

That is the same defect `tests/test_evidence_table_registration.py` pins for research
artefacts: a check named in prose but absent from the list of things that actually
run. That guard is scoped to `research/*.md` citations. This one generalises it to the
suite itself — any `tests/test_*.py` on disk must appear in the workflow's run list,
so a new test cannot be written and silently left unrun.

Offline. Reads the workflow as text; no YAML dependency, no network.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
WORKFLOW = ROOT / ".github" / "workflows" / "test-and-report.yml"

# An invocation line in the workflow looks like:
#   python3 tests/test_gen_index.py 2>&1 | tee -a tests/last-verification.txt
# Anchored to the line start and requiring `python3 tests/...`, so a test name that
# appears only inside a `#` comment is not counted as run.
INVOKE = re.compile(r"^[ \t]*python3 (tests/test_[A-Za-z0-9_]+\.py)", re.M)

# Tests that are deliberately not run by the suite. Keep this empty if possible: an
# entry here is a check the commons has decided not to run, and it should carry a
# reason. (For network-dependent harnesses see the `UAT_LIVE_FAIL` guard test.)
ALLOW_UNRUN = set()


class VerificationSuiteRegistrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text()
        cls.invoked = set(INVOKE.findall(cls.workflow))
        cls.on_disk = {f"tests/{p.name}" for p in TESTS.glob("test_*.py")}

    def test_the_scan_is_not_vacuous(self):
        # If the invocation pattern or the workflow ever drifts, this guard could pass by
        # finding nothing. Assert it is looking at real material.
        self.assertTrue(WORKFLOW.exists(), "the CI workflow this guard checks is missing")
        self.assertGreaterEqual(
            len(self.on_disk), 30,
            "fewer than 30 test_*.py files found — the glob has gone blind")
        self.assertGreaterEqual(
            len(self.invoked), 30,
            "fewer than 30 invocations parsed from the workflow — the pattern has gone blind")

    def test_every_test_on_disk_is_run(self):
        missing = sorted(self.on_disk - self.invoked - ALLOW_UNRUN)
        self.assertEqual(
            missing, [],
            "test file(s) exist but .github/workflows/test-and-report.yml never runs "
            "them:\n  " + "\n  ".join(missing) +
            "\nAdd a `python3 <path>` line to the Run Offline Verification Suite step.")

    def test_every_invoked_test_exists_on_disk(self):
        dangling = sorted(self.invoked - self.on_disk)
        self.assertEqual(
            dangling, [],
            "the workflow runs test file(s) that do not exist:\n  " + "\n  ".join(dangling))

    def test_the_guard_itself_is_registered(self):
        # A guard outside the register protects nothing.
        self.assertIn("tests/test_verification_suite_registration.py", self.workflow)


if __name__ == "__main__":
    unittest.main(verbosity=2)
