#!/usr/bin/env python3
"""A pytest-style test file must have a runner, because pytest is not installed (Desi, 2026-11-26).

The defect this holds shut, twice in one day:

  * `tests/test_no_zeroed_tracked_files.py` guarded against a landing emptying or half-deleting a
    file. It was bare `def test_` functions with no `__main__` block, so the landing gate — which
    executes every `tests/test_*.py` **as a script** — ran it, collected nothing, and read exit 0 as
    "pass". The tracked 0-byte leftover it existed to catch sat in main for a week, and a wake's own
    record called the gate red on the strength of a test that could not go red.
  * three more files (retention, ledger mirror folding, window land collision) carried 15 assertions
    that ran nowhere for the same reason. The census excused them in a bucket named EXEMPT —
    "pytest-style, not registered" — which named the excuse and removed the finding.

The rule is narrow on purpose: a file whose tests are plain `def test_...` functions (or
`TestCase` classes with no runner) needs a `__main__` block or a `unittest.main()` call. Files that
run their checks at module level and `sys.exit(1)` on failure — `test_rover_pilot.py`,
`test_usage_silent_zero.py` — are already reachable and are not this test's business. A workflow
mention is *not* a substitute: `python3 tests/test_foo.py` on a pytest-style file prints nothing and
exits 0, which is the NO-OP shape the census already names.

`tests/_minirunner.py` exists for the pytest-style ones, including the `tmp_path` fixture they use.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"

RUNNER = re.compile(r"""__name__\s*==\s*['"]__main__['"]|unittest\.main\s*\(""")
# Top-level pytest-style definitions: a bare `def test_` at column 0, or a TestCase class.
PYTEST_STYLE = re.compile(
    r"^(?:def test_\w+\s*\(|class \w+\s*\(\s*(?:unittest\.)?TestCase\s*\))", re.MULTILINE)


def _test_files():
    return sorted(p for p in TESTS.glob("test_*.py") if p.is_file())


def runs_nowhere(text):
    """True when the file's assertions are never executed by anything on this machine."""
    return bool(PYTEST_STYLE.search(text)) and not RUNNER.search(text)


class EveryTestFileCanRun(unittest.TestCase):
    def test_no_test_file_is_unreachable(self):
        dead = [p.name for p in _test_files()
                if runs_nowhere(p.read_text(encoding="utf-8", errors="replace"))]
        self.assertEqual(
            dead, [],
            "these test files define `def test_...` functions and have no runner, so on this machine "
            "they are executed by the landing gate as scripts, collect nothing, exit 0, and report "
            "'pass' without reading anything — pytest is not installed. Give each one "
            "`if __name__ == \"__main__\":` with tests/_minirunner.py, or rewrite it as unittest: "
            + ", ".join(dead))

    def test_the_detector_can_see_a_dead_file(self):
        # A guard that cannot fail is the defect it guards against, so the detector is exercised on
        # the shape that caused this: pytest-style functions, no runner.
        self.assertTrue(runs_nowhere("def test_x():\n    assert True\n"))
        self.assertTrue(runs_nowhere("import unittest\n\nclass T(unittest.TestCase):\n    pass\n"))
        self.assertFalse(runs_nowhere('def test_x():\n    pass\n\nif __name__ == "__main__":\n'
                                      '    run(globals())\n'))
        self.assertFalse(runs_nowhere("import unittest\nif __name__ == '__main__':\n"
                                      "    unittest.main()\n"))
        # A hand-rolled module-level runner is reachable and must not be flagged.
        self.assertFalse(runs_nowhere("ok = True\nok &= check()\nif not ok:\n    sys.exit(1)\n"))

    def test_the_files_that_bit_us_are_now_reachable(self):
        for name in ("test_no_zeroed_tracked_files.py", "test_enforce_retention.py",
                     "test_ledger_mirror_folding.py", "test_window_land_collision.py",
                     "test_land_runs_reports_dropped_paths.py"):
            path = TESTS / name
            self.assertTrue(path.is_file(), name)
            self.assertFalse(runs_nowhere(path.read_text(encoding="utf-8")), name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
