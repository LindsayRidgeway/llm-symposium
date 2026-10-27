#!/usr/bin/env python3
"""Tests for scripts/suite_census.py — the census has to see what the gate cannot.

The whole reason this tool exists is that a set of *file names* cannot answer three questions
about a repository whose suite is 144 files: what is red right now, what became red inside a
file that was already red, and what stopped being red. So these tests are about exactly those
three answers, plus the one thing that makes the tool worth running at all — that its record
can be compared to the next record and mean something.

Nothing here runs the real suite: the census is exercised against small fake repositories in a
temp directory, because a test that cost minutes would be a test nobody runs (the failure mode
this tool was written to end).

Run: python3 tests/test_suite_census.py
"""

import json
import os
import shutil
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))

import suite_census  # noqa: E402


GREEN = "print('OK')\n"
RED = (
    "print('FAIL: test_one (test_mod.TestThings.test_one)')\n"
    "print('FAIL: test_two (test_mod.TestThings.test_two)')\n"
    "raise SystemExit(1)\n"
)
FIXED = "print('OK')\n"
SLOW = "import time\ntime.sleep(20)\nprint('OK')\n"


def fake_repo(files):
    """A throwaway repository root holding a tests/ directory of the named files."""
    root = tempfile.mkdtemp(prefix="census-")
    os.makedirs(os.path.join(root, "tests"))
    for name, body in files.items():
        with open(os.path.join(root, "tests", name), "w", encoding="utf8") as handle:
            handle.write(body)
    return root


class TestParsing(unittest.TestCase):
    def test_unittest_failure_headers_become_case_names(self):
        output = ("FAIL: test_one (test_mod.TestThings.test_one)\n"
                  "ERROR: test_two (test_mod.TestThings.test_two)\n"
                  "Ran 12 tests in 0.4s\nFAILED (failures=1, errors=1)\n")
        self.assertEqual(suite_census.parse_cases(output), ["test_one", "test_two"])

    def test_print_style_harness_failures_are_seen_too(self):
        """Most of this repository's suites print their own verdicts; the census must read them."""
        output = "OK   the door opens\nFAIL  the door closes behind you\n3 checks, 1 failed\n"
        self.assertEqual(suite_census.parse_cases(output), ["the door closes behind you"])

    def test_a_pass_line_is_not_a_failure(self):
        """`all checks passed` and a bare OK must not be mistaken for a broken case."""
        self.assertEqual(suite_census.parse_cases("OK   a thing\nall checks passed\n"), [])

    def test_test_count_comes_from_the_summary_line(self):
        self.assertEqual(suite_census.parse_tests_run("Ran 23 tests in 1.8s\nOK\n"), 23)
        self.assertIsNone(suite_census.parse_tests_run("46 checks, 0 failed\n"))


class TestCensus(unittest.TestCase):
    def setUp(self):
        self.root = fake_repo({"test_aaa_green.py": GREEN,
                               "test_bbb_red.py": RED,
                               "test_ccc_slow.py": SLOW})

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_a_green_file_is_ok_and_a_red_one_is_red(self):
        files = suite_census.census(self.root, timeout=5, jobs=3)
        self.assertEqual(files["test_aaa_green.py"]["status"], "ok")
        self.assertEqual(files["test_bbb_red.py"]["status"], "fail")
        self.assertEqual(files["test_bbb_red.py"]["exit"], 1)

    def test_a_red_file_names_the_cases_that_failed(self):
        """The gate holds the file name; this is the part it drops on the floor."""
        files = suite_census.census(self.root, timeout=5, jobs=3)
        self.assertEqual(files["test_bbb_red.py"]["cases_failed"], ["test_one", "test_two"])
        self.assertEqual(files["test_aaa_green.py"]["cases_failed"], [])

    def test_a_file_that_never_returns_is_a_timeout_not_a_failure(self):
        """A hang and a broken assertion are different problems and must not look alike."""
        files = suite_census.census(self.root, only="slow", timeout=1, jobs=1)
        self.assertEqual(files["test_ccc_slow.py"]["status"], "timeout")
        self.assertIsNone(files["test_ccc_slow.py"]["exit"])

    def test_only_narrows_the_census_to_one_file(self):
        files = suite_census.census(self.root, only="aaa", timeout=5, jobs=1)
        self.assertEqual(list(files), ["test_aaa_green.py"])


class TestDiff(unittest.TestCase):
    """The three things a set of file names cannot say, said one at a time."""

    def record(self, **files):
        return {"generated_at": "2026-10-27T00:00:00Z",
                "files": {name: {"status": "ok" if ok else "fail",
                                 "cases_failed": cases,
                                 "exit": 0 if ok else 1}
                          for name, (ok, cases) in files.items()}}

    def test_a_green_file_turning_red_is_damage(self):
        report = suite_census.diff(self.record(**{"a.py": (True, [])}),
                                   self.record(**{"a.py": (False, ["test_x"])}))
        self.assertEqual(report["newly_red"], ["a.py"])
        self.assertTrue(report["damage"])

    def test_a_new_case_inside_an_already_red_file_is_damage_the_gate_cannot_see(self):
        """This is the mask: same file name in both sets, so the landing gate reads 'unchanged'."""
        report = suite_census.diff(self.record(**{"a.py": (False, ["test_x"])}),
                                   self.record(**{"a.py": (False, ["test_x", "test_y"])}))
        self.assertEqual(report["newly_red"], [])
        self.assertEqual(report["new_cases"], [("a.py", ["test_y"])])
        self.assertTrue(report["damage"], "a second failure in a red file is still new damage")

    def test_a_red_file_turning_green_is_recorded_not_ignored(self):
        report = suite_census.diff(self.record(**{"a.py": (False, ["test_x"])}),
                                   self.record(**{"a.py": (True, [])}))
        self.assertEqual(report["newly_green"], ["a.py"])
        self.assertFalse(report["damage"], "a fix is not damage — and it must not read as one")

    def test_a_case_that_stops_failing_in_a_still_red_file_is_named(self):
        report = suite_census.diff(self.record(**{"a.py": (False, ["test_x", "test_y"])}),
                                   self.record(**{"a.py": (False, ["test_y"])}))
        self.assertEqual(report["fixed_cases"], [("a.py", ["test_x"])])
        self.assertFalse(report["damage"])


class TestRecordAndCli(unittest.TestCase):
    def setUp(self):
        self.root = fake_repo({"test_aaa_green.py": GREEN, "test_bbb_red.py": RED})
        self.record = os.path.join(self.root, "channels", "suite-census.json")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_a_record_round_trips_and_stays_comparable(self):
        files = suite_census.census(self.root, timeout=5, jobs=2)
        suite_census.save(self.record, {"files": files, "generated_at": "now"})
        loaded = suite_census.load(self.record)
        self.assertEqual(sorted(loaded["files"]), ["test_aaa_green.py", "test_bbb_red.py"])
        self.assertFalse(suite_census.diff(loaded, loaded)["damage"])

    def test_the_cli_writes_a_record_and_reports_no_change_against_it(self):
        first = suite_census.main(["--repo", self.root, "--jobs", "2", "--timeout", "5",
                                   "--record", self.record, "--write", "--diff"])
        self.assertEqual(first, 0, "a census of a repo with a red file is not itself damage")
        self.assertTrue(os.path.exists(self.record))
        with open(self.record, encoding="utf8") as handle:
            saved = json.load(handle)
        self.assertEqual(saved["summary"]["red"], 1)

    def test_the_cli_exits_non_zero_when_the_record_says_damage_appeared(self):
        """A guard that cannot fail is a decoration: break the recorded baseline and check."""
        suite_census.save(self.record, {"generated_at": "earlier", "files": {
            "test_bbb_red.py": {"status": "ok", "cases_failed": [], "exit": 0}}})
        code = suite_census.main(["--repo", self.root, "--only", "bbb", "--jobs", "1",
                                  "--timeout", "5", "--record", self.record, "--diff"])
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
