#!/usr/bin/env python3
"""Guard: a live-network page-harness must survive an upstream outage without crashing.

Why this file exists (measured, 2026-10-04). Two of this repo's page-harnesses run the
shipped page against a live public API. Both were written without error handling around
their live blocks, so a transient upstream error did not make a check *unverified* — it
made the whole run *throw*:

  * `tests/validate_unreported_trials_page.mjs` — Europe PMC answered a transient **HTTP
    503** on the 2026-10-04 10:22Z wake; the uncaught throw exited 1 and discarded the 33
    checks that had already passed. Guarded and pinned the same day.
  * `tests/validate_recalls_page.mjs` — openFDA; the same defect, found by the 2026-10-04
    audit in `research/live-harness-guard-audit.md`. Guarded and pinned here.

The rule both now follow: a **5xx or a transport error** is reported as SKIP and the process
still exits 0 (an upstream that is down makes a check *unverified*, not *broken*); a **4xx** is
still a failure, because a 4xx means the request the page itself builds was rejected — a page
bug, not a flaky server. The status line says the live checks were skipped rather than passed.

Each harness exposes a switch (`RECALLS_LIVE_FAIL`, `UAT_LIVE_FAIL`): setting it to a status
code forces the live blocks to throw `HTTP <code>` before any network call, so this test is
fully offline and hermetic. No network is touched here.

This is the generalisation of `tests/test_unreported_trials_validator_guard.py`; it runs both
guarded harnesses so the pattern cannot silently regress in one of them.

Run: python3 tests/test_live_harness_guards.py
"""

import os
import shutil
import subprocess
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODE = shutil.which("node")

# (harness, forced-failure env var, an offline check that must still run during an outage)
HARNESSES = [
    ("tests/validate_unreported_trials_page.mjs", "UAT_LIVE_FAIL",
     "the card escapes registry text"),
    ("tests/validate_recalls_page.mjs", "RECALLS_LIVE_FAIL",
     "the card escapes the record's own text"),
]


def _run(harness, switch, status):
    env = dict(os.environ, **{switch: str(status)})
    path = os.path.join(REPO, harness)
    return subprocess.run([NODE, path], cwd=REPO, capture_output=True, text=True, env=env)


@unittest.skipIf(NODE is None, "node not installed; cannot exercise the JS harnesses")
class TestLiveHarnessGuards(unittest.TestCase):
    def test_both_harnesses_carry_the_guard_scaffolding(self):
        """The guard must be present in the source, not merely observed once by hand."""
        for harness, _switch, _offline in HARNESSES:
            with open(os.path.join(REPO, harness), encoding="utf-8") as f:
                src = f.read()
            self.assertIn("const isTransient =", src, harness)
            self.assertIn("skipped", src, harness)

    def test_transient_5xx_is_skipped_and_green(self):
        """A 503 from an upstream must not fail the run; it must say SKIP and exit 0."""
        for harness, switch, _offline in HARNESSES:
            proc = _run(harness, switch, 503)
            with self.subTest(harness=harness):
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertIn("SKIP", proc.stdout)
                self.assertIn("skipped — upstream unavailable", proc.stdout)
                self.assertNotIn("FAIL", proc.stdout)

    def test_4xx_is_still_a_failure(self):
        """A rejected request (the page built a bad query) must still fail the run."""
        for harness, switch, _offline in HARNESSES:
            proc = _run(harness, switch, 400)
            with self.subTest(harness=harness):
                self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
                self.assertIn("CHECK(S) FAILED", proc.stdout)

    def test_offline_checks_survive_a_live_outage(self):
        """The whole point: an outage must not discard the checks that need no network."""
        for harness, switch, offline_check in HARNESSES:
            proc = _run(harness, switch, 503)
            with self.subTest(harness=harness):
                self.assertIn(offline_check, proc.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
