#!/usr/bin/env python3
"""Guard: the unreported-trials harness must survive an upstream outage without crashing.

Why this file exists (measured, 2026-10-04). `tests/validate_unreported_trials_page.mjs`
runs the page's own script against two live keyless APIs (ClinicalTrials.gov v2 and
Europe PMC). On a wake this morning Europe PMC answered a transient **HTTP 503**, and the
harness — which had no error handling around its live sections — threw an uncaught
exception and exited 1, discarding the 33 checks that had already passed and printing
nothing but a stack trace. Re-run minutes later, it passed 54/54. That is the same class of
defect this repo has already been bitten by (see `tests/test_mjs_validators_parse.py`: the
retraction harness was unloadable for three days and no run noticed).

The fix, landed the same day, guards the two live blocks so that:
  * a **5xx or transport** error is reported as SKIP and does not fail the run (an upstream
    that is down makes a check *unverified*, not *broken*), while
  * a **4xx** is still a failure, because a 4xx means the request the page itself builds was
    rejected — a page bug, not a flaky server.

The harness exposes a switch for exactly this test: setting `UAT_LIVE_FAIL` to a status code
forces both live blocks to throw `HTTP <code>` before any network call, so this test is
fully offline and hermetic.

Run: python3 tests/test_unreported_trials_validator_guard.py
"""

import os
import shutil
import subprocess
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODE = shutil.which("node")
HARNESS = os.path.join(REPO, "tests", "validate_unreported_trials_page.mjs")


def _run(env_value):
    env = dict(os.environ, UAT_LIVE_FAIL=str(env_value))
    return subprocess.run([NODE, HARNESS], cwd=REPO, capture_output=True, text=True, env=env)


@unittest.skipIf(NODE is None, "node not installed; cannot exercise the JS harness")
class TestUnreportedTrialsValidatorGuard(unittest.TestCase):
    def test_source_wraps_both_live_sections(self):
        """The guard must be present in the source, not merely observed once by hand."""
        with open(HARNESS, encoding="utf-8") as f:
            src = f.read()
        self.assertIn("const isTransient =", src)
        self.assertIn("try { await runLive4(); }", src)
        self.assertIn("try { await runLive5(); }", src)

    def test_transient_5xx_is_skipped_and_green(self):
        """A 503 from an upstream must not fail the run; it must say SKIP and exit 0."""
        proc = _run(503)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("SKIP", proc.stdout)
        self.assertIn("skipped — upstream unavailable", proc.stdout)
        self.assertNotIn("FAIL", proc.stdout)

    def test_4xx_is_still_a_failure(self):
        """A rejected request (the page built a bad query) must still fail the run."""
        proc = _run(400)
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("CHECK(S) FAILED", proc.stdout)

    def test_offline_checks_survive_a_live_outage(self):
        """The whole point: an outage must not discard the checks that need no network."""
        proc = _run(503)
        self.assertIn("the card escapes registry text", proc.stdout)
        self.assertIn("only keyless public APIs are contacted", proc.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
