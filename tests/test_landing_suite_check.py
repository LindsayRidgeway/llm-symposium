#!/usr/bin/env python3
"""Tests for the failure half of the landing preflight (2026-10-19).

`scripts/landing_suite_check.py` answers the question the landing gate answers
too late: does this tree have test failures that main does not? These tests use
throwaway test directories, never the real suite, so they pin the classification
and the exit codes rather than the repository's health.

The numbers that motivated it (measured 2026-10-19, main at 678760d1): 116 test
files, 101.9 s, one pre-existing failure (`test_gen_index.py`). The two wakes
before it were each refused after they ended — on `test_evidence_table_registration.py`
and on `test_test_registration_audit.py` — for failures this could have named
while the wake was still running.

Run directly:  python3 tests/test_landing_suite_check.py
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "landing_suite_check", ROOT / "scripts" / "landing_suite_check.py"
)
lsc = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(lsc)

PASSING = "import unittest\n\n\nclass T(unittest.TestCase):\n    def test_ok(self):\n        pass\n\n\nif __name__ == '__main__':\n    unittest.main()\n"
FAILING = "import unittest\n\n\nclass T(unittest.TestCase):\n    def test_bad(self):\n        self.assertEqual(1, 2)\n\n\nif __name__ == '__main__':\n    unittest.main()\n"


def _tree(*names_and_bodies):
    """A throwaway directory holding the named test files."""
    tmp = Path(tempfile.mkdtemp(prefix="landing-suite-test-"))
    tests = tmp / "tests"
    tests.mkdir()
    for name, body in names_and_bodies:
        (tests / name).write_text(body, encoding="utf8")
    return tests


class ClassificationTest(unittest.TestCase):
    def test_a_passing_tree_has_no_failures(self):
        tests = _tree(("test_a.py", PASSING), ("test_b.py", PASSING))
        self.assertEqual(lsc.failures(lsc.run_suite(tests)), [])

    def test_a_failing_file_is_named_and_nothing_else_is(self):
        tests = _tree(("test_a.py", PASSING), ("test_b.py", FAILING))
        self.assertEqual(lsc.failures(lsc.run_suite(tests)), ["test_b.py"])

    def test_the_order_is_the_suite_order_not_a_set(self):
        # Two failures, discovered alphabetically: the report is readable only
        # if the reader can match it against the suite they just ran.
        tests = _tree(("test_z.py", FAILING), ("test_b.py", FAILING))
        self.assertEqual(lsc.failures(lsc.run_suite(tests)), ["test_b.py", "test_z.py"])

    def test_a_recorded_baseline_makes_an_old_failure_not_new(self):
        self.assertEqual(lsc.new_failures(["test_gen_index.py"], ["test_gen_index.py"]), [])

    def test_a_failure_absent_from_the_baseline_is_new(self):
        self.assertEqual(
            lsc.new_failures(["test_gen_index.py", "test_new.py"], ["test_gen_index.py"]),
            ["test_new.py"],
        )

    def test_no_baseline_means_every_failure_is_new(self):
        # The safe direction: "we could not tell" must not read as "safe to land".
        self.assertEqual(lsc.new_failures(["test_a.py"], None), ["test_a.py"])

    def test_a_baseline_that_no_longer_fails_is_not_a_new_failure(self):
        # A repaired test is good news; it must not be reported as a regression.
        self.assertEqual(lsc.new_failures([], ["test_gen_index.py"]), [])


class TimeoutTest(unittest.TestCase):
    def test_a_test_that_outlives_its_limit_counts_as_a_failure(self):
        # The gate would see the hang as a failure too, and a hang is the one
        # outcome a wake most needs warning about: it eats the whole budget.
        tests = _tree(("test_slow.py", "import time\ntime.sleep(30)\n"))
        rows = lsc.run_suite(tests, timeout=1)
        self.assertEqual(rows[0]["rc"], "TIMEOUT")
        self.assertEqual(lsc.failures(rows), ["test_slow.py"])


class BaselineFileTest(unittest.TestCase):
    def test_a_missing_baseline_reads_as_none(self):
        self.assertIsNone(lsc.load_baseline(Path(tempfile.mkdtemp()) / "absent.json"))

    def test_a_corrupt_baseline_reads_as_none_rather_than_crashing(self):
        path = Path(tempfile.mkdtemp()) / "bad.json"
        path.write_text("{not json", encoding="utf8")
        self.assertIsNone(lsc.load_baseline(path))

    def test_a_baseline_with_the_wrong_shape_reads_as_none(self):
        path = Path(tempfile.mkdtemp()) / "shape.json"
        path.write_text(json.dumps({"failures": "oops"}), encoding="utf8")
        self.assertIsNone(lsc.load_baseline(path))

    def test_writing_a_baseline_records_only_failures_and_the_commit(self):
        tests = _tree(("test_a.py", PASSING), ("test_b.py", FAILING))
        rows = lsc.run_suite(tests)
        path = Path(tempfile.mkdtemp()) / "landing-baseline.json"
        written = lsc.write_baseline(rows, "abc1234", path)
        self.assertEqual(written["commit"], "abc1234")
        self.assertEqual(written["failures"], ["test_b.py"])
        self.assertEqual(written["files"], 2)
        self.assertEqual(lsc.load_baseline(path)["failures"], ["test_b.py"])


class ExitCodeTest(unittest.TestCase):
    def test_a_failing_tree_with_no_baseline_exits_one(self):
        tests = _tree(("test_b.py", FAILING))
        code = lsc.main(
            ["--tests-dir", str(tests), "--baseline", str(tests / "absent.json")]
        )
        self.assertEqual(code, 1)

    def test_a_known_failure_with_a_baseline_exits_zero(self):
        tests = _tree(("test_b.py", FAILING))
        baseline = tests / "baseline.json"
        baseline.write_text(json.dumps({"commit": "abc", "failures": ["test_b.py"]}))
        code = lsc.main(["--tests-dir", str(tests), "--baseline", str(baseline)])
        self.assertEqual(code, 0)

    def test_a_new_failure_beside_a_known_one_exits_one(self):
        tests = _tree(("test_a.py", FAILING), ("test_b.py", FAILING))
        baseline = tests / "baseline.json"
        baseline.write_text(json.dumps({"commit": "abc", "failures": ["test_a.py"]}))
        code = lsc.main(["--tests-dir", str(tests), "--baseline", str(baseline)])
        self.assertEqual(code, 1)

    def test_an_empty_directory_is_a_setup_error_not_a_pass(self):
        empty = Path(tempfile.mkdtemp())
        self.assertEqual(lsc.main(["--tests-dir", str(empty)]), 2)

    def test_a_missing_directory_is_a_setup_error(self):
        self.assertEqual(lsc.main(["--tests-dir", "/nonexistent/tests"]), 2)


class LiveAgainstTest(unittest.TestCase):
    def test_a_revision_is_measured_in_a_worktree_that_is_then_removed(self):
        repo = Path(tempfile.mkdtemp())
        git = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]

        def run(*args):
            return subprocess.run(
                [*git, *args], cwd=str(repo), capture_output=True, text=True
            )

        run("init", "-q")
        (repo / "tests").mkdir()
        (repo / "tests" / "test_a.py").write_text(PASSING, encoding="utf8")
        run("add", "-A")
        run("commit", "-q", "-m", "one")
        run("tag", "base")
        (repo / "tests" / "test_a.py").write_text(FAILING, encoding="utf8")
        run("commit", "-q", "-am", "two")

        baseline, rows = lsc.measure_revision("base", repo=repo, timeout=60)
        self.assertEqual(baseline, [])  # base was clean
        self.assertEqual(len(rows), 1)

        listed = subprocess.run(
            ["git", "-C", str(repo), "worktree", "list"],
            capture_output=True,
            text=True,
        ).stdout
        self.assertNotIn("landing-suite-", listed)  # no worktree left behind


if __name__ == "__main__":
    unittest.main(verbosity=2)
