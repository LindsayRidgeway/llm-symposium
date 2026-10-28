#!/usr/bin/env python3
"""Every file a workflow runs must exist.

Why this exists (measured 2026-10-28). `.github/workflows/test-and-report.yml` line 220 runs
`python3 tests/test_agenda_digest_fits_the_wake_window.py`. That file has never existed in this
repository's history: `git log --all -- tests/test_agenda_digest_fits_the_wake_window.py` is
empty. The test it was meant to register is `tests/test_wake_context_caps.py`, which exists and
still carries the old name in its own `Run:` line. The workflow was registered 2026-10-17 by a
run that renamed the file before landing and did not update the line that names it.

Nothing noticed for eleven days, and the reason is worth writing down: the step is a
`run: |` block with `set -o pipefail`, so a missing script would fail the step — but the whole
workflow was retired from its schedule on 2026-09-25 and is `workflow_dispatch:` only, so it has
not executed since. The one place the reference is *read* — this repository — never reads it as
a path.

The class, not the instance: a command line inside a workflow is a claim that a file is there,
and nothing checked that claim. This guard reads every executable line of every workflow (YAML
comments are dropped, because a comment may legitimately cite a retired path) and fails if any
`tests/` or `scripts/` file it names is absent. It also fails if it finds no command lines at
all, so a parser that silently matches nothing cannot pass as a green run — the same
"guard that checks nothing" failure this file was written to catch.

Run: python3 tests/test_workflow_commands_exist.py
"""

import os
import re
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOWS = os.path.join(REPO, ".github", "workflows")

# Paths under these roots, when named on an executable workflow line, must resolve to a file.
# Kept to Python and JS sources: data files (`tests/last-verification.txt`) are output, written
# by the step that names them, and are not required to pre-exist.
ROOTS = ("tests", "scripts", "channels")
SUFFIXES = (".py", ".mjs", ".js", ".sh")

PATH_RE = re.compile(
    r"(?<![\w./-])((?:%s)/[\w][\w./-]*\.(?:%s))(?![\w-])"
    % ("|".join(ROOTS), "|".join(s.lstrip(".") for s in SUFFIXES))
)


def _executable_lines(text):
    """Yield (line_number, line) for every line that is not a YAML comment."""
    for number, line in enumerate(text.splitlines(), start=1):
        if line.strip().startswith("#"):
            continue
        yield number, line


def _workflow_files():
    if not os.path.isdir(WORKFLOWS):
        return []
    return sorted(
        os.path.join(WORKFLOWS, name)
        for name in os.listdir(WORKFLOWS)
        if name.endswith((".yml", ".yaml"))
    )


def _claims():
    """Every (workflow file, line number, path) claim made on an executable line."""
    found = []
    for path in _workflow_files():
        with open(path, encoding="utf-8") as handle:
            for number, line in _executable_lines(handle.read()):
                for match in PATH_RE.finditer(line):
                    # A trailing period or comma can be swallowed by the greedy class above.
                    found.append((os.path.basename(path), number, match.group(1).rstrip(".,")))
    return found


class EveryWorkflowCommandExists(unittest.TestCase):
    def test_the_guard_is_looking_at_something(self):
        """A regex that matches nothing would make every other test here vacuous."""
        workflows = _workflow_files()
        self.assertTrue(workflows, "no workflow files found under .github/workflows/")
        claims = _claims()
        self.assertGreater(
            len(claims), 20,
            "expected the workflows to name many files; the scanner found %d, so it is "
            "probably not reading them" % len(claims),
        )

    def test_every_named_file_exists(self):
        missing = []
        for workflow, number, path in _claims():
            if not os.path.isfile(os.path.join(REPO, path)):
                missing.append("%s:%d names %s, which does not exist" % (workflow, number, path))
        self.assertEqual([], missing, "\n  ".join(["workflow commands pointing at no file:"] + missing))

    def test_the_known_regression_is_named_correctly(self):
        """The specific line this guard was written for, pinned by name."""
        target = os.path.join(WORKFLOWS, "test-and-report.yml")
        if not os.path.isfile(target):
            self.skipTest("test-and-report.yml is not present")
        with open(target, encoding="utf-8") as handle:
            text = handle.read()
        self.assertNotIn(
            "test_agenda_digest_fits_the_wake_window.py", text,
            "the workflow names a test file that has never existed; the agenda-window test is "
            "tests/test_wake_context_caps.py",
        )
        self.assertIn("tests/test_wake_context_caps.py", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
