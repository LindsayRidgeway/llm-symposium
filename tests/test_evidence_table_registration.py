#!/usr/bin/env python3
"""Every test a research artefact says pins it must exist, and must actually be run.

Two defects of the same shape, both found by a person reading rather than by a check:

  * 2026-09-30, the wake that hand-registered four evidence-table tests in the CI workflow: they
    existed but were never run, so every artefact that said "pinned by `tests/X.py`" was claiming a
    check that did not happen. One hand-registration fixes today's four; it does not stop the fifth.
  * the same day, `research/gambling-algorithmic-exploitation.md` closed by naming
    `tests/test_gambling_source_table.py` as its provenance check — a file that had never existed.
    A promising-sounding path in a code span is exactly the failure the artifact-existence checker
    (`tests/test_artifact_claims.py`) was built for; that checker scans HTML attributes and
    `channels/tasks.md`, and the research directory was outside it.

This test closes that gap mechanically: it scans every `research/*.md`, collects each
backtick-quoted `tests/test_*.py` citation, and asserts the file exists and is invoked by
`.github/workflows/test-and-report.yml` — the workflow is where the commons records what runs on
every landing. The failure message names the artefact and the missing side, so the fix is a line,
not an investigation.

Scope is deliberately narrow: `research/*.md` only. Backtick citations elsewhere in the repo (a
to-do list's note that a test *will* be written, the ledger's history of a test renamed away)
describe intentions or history, not a claim that a check runs now, and treating them as the same
thing would make this guard fail on prose that is correct.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
WORKFLOW = ROOT / ".github" / "workflows" / "test-and-report.yml"
CITE = re.compile(r"`(tests/test_[a-z0-9_]+\.py)`")


class EvidenceTableRegistrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text()
        cls.citations = {}
        for md in sorted(RESEARCH.glob("*.md")):
            for test in CITE.findall(md.read_text()):
                cls.citations.setdefault(test, set()).add(md.name)

    def test_the_scan_is_not_vacuous(self):
        # If the citation pattern or the directory ever drifts, this guard would pass by finding
        # nothing. Assert it is looking at real material.
        self.assertGreaterEqual(
            len(self.citations), 3,
            "no evidence-table test citations found in research/ — the scan has gone blind")
        self.assertTrue(WORKFLOW.exists(), "the CI workflow this guard checks is missing")

    def test_every_cited_test_exists_and_is_registered(self):
        problems = []
        for test, where in sorted(self.citations.items()):
            artefact = ", ".join(sorted(where))
            if not (ROOT / test).exists():
                problems.append(f"{test} is named as a pin by {artefact}, but the file does not exist")
            elif test not in self.workflow:
                problems.append(
                    f"{test} is named as a pin by {artefact}, but .github/workflows/"
                    f"test-and-report.yml never runs it")
        self.assertEqual(problems, [], "\n".join(problems))

    def test_the_guard_itself_is_registered(self):
        # A guard outside the register protects nothing.
        self.assertIn("tests/test_evidence_table_registration.py", self.workflow)


if __name__ == "__main__":
    unittest.main(verbosity=2)
