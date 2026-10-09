#!/usr/bin/env python3
"""A test that is never run is not a guard.

Defect class this closes (measured 2026-10-09, Dmitri): `tests/` held 58 `test_*.py`
files but `.github/workflows/test-and-report.yml` invoked only 36 of them. Twenty-two
tests — including `tests/test_reject_queue_sweep.py`, whose own docstring says it was
written *because* nothing ran the sweep, and then was itself never registered — were
present, passing, and executed by nothing. This is the same class the workflow's own
comments already record four times: a `.mjs` validator that carried a syntax error for
three days, `compile_agenda.py --check`, evidence-table pins named by an artefact but
never run, and a pin named for a file that did not exist. A guard on a clock that never
fires is not a guard.

What it enforces:
  * every `tests/test_*.py` is either invoked by the verification workflow, or named in
    `EXEMPT` below with a one-line reason;
  * nothing sits in `EXEMPT` that no longer exists, so an exemption cannot rot into a
    silent omission;
  * the workflow's invocation list is *parsed*, not trusted, and no test it names may be
    a file that does not exist.

Offline; reads only the workflow and the tests directory.
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "test-and-report.yml"
INVOKE_RE = re.compile(r"python3\s+tests/(?P<name>[A-Za-z0-9_]+\.py)")

# Tests deliberately NOT run on every landing, each with the reason. Empty is the healthy
# state: if a test is worth keeping, it is worth running where the answer can differ.
EXEMPT: dict[str, str] = {}


def invoked() -> set[str]:
    return {m.group("name") for m in INVOKE_RE.finditer(WORKFLOW.read_text(encoding="utf-8"))}


def declared() -> list[str]:
    return sorted(p.name for p in (ROOT / "tests").glob("test_*.py"))


class SuiteRegistration(unittest.TestCase):
    def test_workflow_invokes_something(self):
        """A parse that finds almost nothing means the workflow's shape changed under us."""
        self.assertGreater(len(invoked()), 10,
                           "the workflow parses to almost nothing — has its shape changed?")

    def test_every_test_is_run_or_explicitly_exempt(self):
        missing = [n for n in declared() if n not in invoked() and n not in EXEMPT]
        self.assertEqual(
            missing, [],
            "these tests exist but no landing runs them; register each in "
            ".github/workflows/test-and-report.yml or add it to EXEMPT with a reason: %r" % missing,
        )

    def test_exemptions_do_not_rot(self):
        present = set(declared())
        for name, reason in EXEMPT.items():
            self.assertIn(name, present, "EXEMPT names %r, which no longer exists" % name)
            self.assertTrue(reason.strip(), "EXEMPT entry %r has no reason" % name)

    def test_the_workflow_names_no_ghost_test(self):
        present = set(declared())
        ghost = sorted(n for n in invoked() if n not in present)
        self.assertEqual(ghost, [], "the workflow invokes tests that do not exist: %r" % ghost)


if __name__ == "__main__":
    unittest.main(verbosity=2)
