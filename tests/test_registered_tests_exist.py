#!/usr/bin/env python3
"""Registered tests must exist on disk, and must run when invoked the way CI invokes them.

Why this exists (Dmitri, 2026-10-28). The commons has a long record of the same defect one level up:
a guard that is written and never run. `tests/test_evidence_table_registration.py` closes half of it
(a research artefact's pin must exist AND be registered in CI). Nothing closed the other half — a
name registered in CI whose file is not there — and this test found one on the day it was written:

    .github/workflows/test-and-report.yml:220
    python3 tests/test_agenda_digest_fits_the_wake_window.py

That filename has never existed in the repository's history (`git log --all -- <path>` is empty). The
checks it names were renamed to `tests/test_wake_context_caps.py`, and the registration was not
renamed with them. It survived unnoticed because the step is written as

    python3 tests/X.py 2>&1 | tee -a tests/last-verification.txt

and the job sets `pipefail` but NOT `errexit`: a missing file prints one error to stderr, the script
carries on to the next line, and the step exits with the status of the LAST command. Measured in this
checkout 2026-10-28: pipeline exit code 0 with the file absent. So for as long as the name has been
wrong, the step has been green while executing nothing — the exact failure the workflow's own comment
at line 228 names ("A guard that is registered here and never fires is the defect it exists to
catch").

Two checks, both cheap and both offline:

  1. every `python3 tests/<name>.py` named in .github/workflows/*.yml has a file behind it;
  2. every such file is runnable the way CI runs it: it carries a script-run marker (`__main__`, or
     the `FAILURES` list + `sys.exit` convention this repository uses in about a third of its
     tests). A pytest-style file named here prints nothing, checks nothing, and reports green —
     which is why the workflow's own register of the twenty-two deliberately skips two of them.
     Measured 2026-10-28 before writing the check: of the 98 existing registered files, all 98
     carry one marker or the other, so this asks no file to adopt a new style.

Run: python3 tests/test_registered_tests_exist.py
"""

import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW_DIR = os.path.join(ROOT, ".github", "workflows")

# Only the form CI actually uses. `python3 -m pytest tests/` style invocations are a different
# registration and this test deliberately says nothing about them.
INVOCATION = re.compile(r"python3\s+(tests/[A-Za-z0-9_]+\.py)")

# The floor exists so the scan cannot pass by finding nothing — a broken glob, a renamed workflow
# directory, or a workflow file reformatted away from `python3 tests/X.py` would otherwise read as
# "no registration is missing". Measured 2026-10-28: 100 distinct registrations across the workflow
# files (99 in test-and-report.yml, plus this test once it is registered).
MIN_EXPECTED = 40


def registrations():
    """{relative test path: [workflow filenames that invoke it]}"""
    found = {}
    for name in sorted(os.listdir(WORKFLOW_DIR)):
        if not name.endswith((".yml", ".yaml")):
            continue
        with open(os.path.join(WORKFLOW_DIR, name), encoding="utf-8") as f:
            text = f.read()
        for match in INVOCATION.finditer(text):
            found.setdefault(match.group(1), []).append(name)
    return found


class RegisteredTestsExist(unittest.TestCase):
    def test_the_scan_finds_the_registrations(self):
        """Guard against the guard: an empty or truncated scan must fail, not pass."""
        found = registrations()
        self.assertGreaterEqual(
            len(found),
            MIN_EXPECTED,
            "the workflow scan found fewer registrations than it should — check the glob and the "
            "'python3 tests/X.py' invocation form before trusting a green result",
        )

    def test_every_registered_test_has_a_file(self):
        missing = {
            path: workflows
            for path, workflows in registrations().items()
            if not os.path.exists(os.path.join(ROOT, path))
        }
        self.assertEqual(
            {},
            missing,
            "CI runs a test file that is not in the tree, so the step prints an error and exits 0 "
            "(pipefail without errexit) — a green check that checks nothing. Either the file was "
            "renamed and the registration was not (fix the registration), or the registration is a "
            "typo. Missing: %r" % (missing,),
        )

    def test_every_registered_test_has_a_runner(self):
        """CI invokes these as scripts; a file without `__main__` checks nothing when run that way."""
        silent = []
        for path in sorted(registrations()):
            full = os.path.join(ROOT, path)
            if not os.path.exists(full):
                continue  # reported by the test above, not twice
            with open(full, encoding="utf-8") as f:
                if "__main__" not in f.read():
                    silent.append(path)
        self.assertEqual(
            [],
            silent,
            "these files are registered as `python3 tests/X.py` but have no __main__ block, so the "
            "step exits 0 having run no assertion: give them a runner or take them out of the "
            "workflow",
        )

    def test_the_known_rename_is_registered_under_its_real_name(self):
        """The regression that motivated this test, pinned so it cannot come back.

        The agenda-digest budget guard was registered as `test_agenda_digest_fits_the_wake_window.py`
        after the file had been renamed to `test_wake_context_caps.py`, and the old name stayed in
        the workflow for eleven days.
        """
        registered = registrations()
        self.assertNotIn(
            "tests/test_agenda_digest_fits_the_wake_window.py",
            registered,
            "the pre-rename filename is back in a workflow; the file is tests/test_wake_context_caps.py",
        )
        self.assertTrue(
            os.path.exists(os.path.join(ROOT, "tests/test_wake_context_caps.py")),
            "the agenda-digest guard's file is gone; if it was renamed again, the workflow must say so",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
