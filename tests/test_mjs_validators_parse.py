#!/usr/bin/env python3
"""Guard: every JavaScript harness in this repo must at least parse.

Why this file exists (measured, 2026-09-30). `tests/validate_retraction_page.mjs` had a
hard syntax error for three days — the wake that landed run 20260927T200258Z-4e5ddbe3
appended `const pageText = ...` onto the tail of a comment line, so the whole statement
was swallowed by the comment and the next line began with `.replace(...)`. The file could
not be loaded by Node at all. Nobody noticed, because no automated run ever executes the
`.mjs` harnesses: they are not in `.github/workflows/test-and-report.yml`, so a syntax
error is invisible until a person happens to run one by hand. Meanwhile the page it guards
(`docs/works/retraction.html`) still told the reader it was "Checked by
tests/validate_retraction_page.mjs", and three other documents cite it as a 65-check pass.

The same trap applies to every page and app script under `docs/`. A JavaScript file that
cannot parse is a silent hole: the browser throws before any of its behaviour runs.

This test does not need a network and does not execute the harnesses (several of them call
live public APIs on purpose). It only asks Node to parse each file: `node --check <file>`.
That is exactly the check that would have caught the 2026-09-27 corruption on the day it
landed. If Node is not installed the test skips rather than fails, so a checkout without a
JS toolchain is not turned red by a tooling gap.

Run: python3 tests/test_mjs_validators_parse.py
"""

import glob
import os
import shutil
import subprocess
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODE = shutil.which("node")


def _js_files():
    """Every JS file that ships in the repo: the page harnesses and the site scripts."""
    files = glob.glob(os.path.join(REPO, "tests", "*.mjs"))
    files += glob.glob(os.path.join(REPO, "docs", "**", "*.js"), recursive=True)
    return sorted(f for f in files if os.path.isfile(f))


def _parse_error(path):
    """Return Node's error output for a file that will not parse, else None."""
    proc = subprocess.run([NODE, "--check", path], capture_output=True, text=True)
    if proc.returncode == 0:
        return None
    return (proc.stderr or proc.stdout or "node --check failed").strip()


@unittest.skipIf(NODE is None, "node not installed; cannot parse-check the JS harnesses")
class TestJsHarnessesParse(unittest.TestCase):
    def test_every_js_file_parses(self):
        failures = {p: err for p in _js_files() if (err := _parse_error(p))}
        detail = "\n\n".join(f"  {os.path.relpath(p, REPO)}:\n{err}" for p, err in failures.items())
        self.assertEqual(failures, {}, f"JavaScript that will not parse:\n{detail}")

    def test_the_check_is_not_vacuous(self):
        """Reading no files and finding no errors is not a pass."""
        self.assertGreater(len(_js_files()), 8, "too few JS files seen — is the glob wrong?")

    def test_the_2026_09_27_regression(self):
        """The exact corruption that started this: the section-8 comment must end in a
        newline, not run straight into `const pageText`. Asserted on the text so the fix is
        pinned even if a future edit reintroduces the same join."""
        path = os.path.join(REPO, "tests", "validate_retraction_page.mjs")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        self.assertIn("shipped HTML ---------------\nconst pageText = html.replace(", text)
        self.assertNotIn("---------------const pageText", text)

    def test_harnesses_can_run_without_an_argument(self):
        """A harness that reads `process.argv[2]` with no fallback throws on `undefined`.
        `validate_trials_page.mjs` did exactly that until 2026-09-30; anything named as a
        self-checking harness should be runnable as `node tests/<name>.mjs`."""
        import re

        offenders = []
        for path in glob.glob(os.path.join(REPO, "tests", "*.mjs")):
            with open(path, encoding="utf-8") as f:
                text = f.read()
            if "process.argv[2]" in text and "process.argv[2] ||" not in text and \
                    "process.argv[2] ??" not in text:
                offenders.append(os.path.relpath(path, REPO))
        self.assertEqual(offenders, [], f"these harnesses need a CLI argument to run: {offenders}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
