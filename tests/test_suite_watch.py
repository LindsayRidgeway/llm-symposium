#!/usr/bin/env python3
"""The guard for scripts/suite_watch.py: a run that measures nothing must not read as a pass.

Written after two measured misses on 2026-11-27. `tests/test_mjs_validators_parse.py` was red on main
from 759aaba5 and nothing said so, because the only thing that runs every test is a landing, and a
landing compares against what main was already doing. Running the suite by hand found it in five
minutes, which means the missing thing is not a check but a clock.

What this test pins, and why each one is a real failure seen in this repository:

  * one failing file is named, not counted — the refusal to print only "1 failure" is the same defect
    as a landing that says "new_test_failures (3)";
  * a timeout is its own outcome: `test_declutter_audit.py` legitimately takes 327 s, and reporting it
    as a failure would send someone to look for a hang that is not there;
  * an empty test directory exits 2 rather than 0, because a runner that collects nothing is how a
    dead guard reports a pass for a week;
  * the report it writes says which commit it measured, so a green line is not timeless.

Run directly: python3 tests/test_suite_watch.py
"""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def module():
    spec = importlib.util.spec_from_file_location("sw", ROOT / "scripts" / "suite_watch.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sw = module()

PASS = "#!/usr/bin/env python3\nprint('ok')\n"
FAIL = "#!/usr/bin/env python3\nimport sys\nprint('AssertionError: the thing is broken')\nsys.exit(1)\n"
HANG = "#!/usr/bin/env python3\nimport time\ntime.sleep(30)\n"


class AHelper:
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.root = Path(self._td.name)
        self.tests = self.root / "tests"
        self.tests.mkdir()

    def tearDown(self):
        self._td.cleanup()

    def write(self, name, body=PASS):
        p = self.tests / name
        p.write_text(body, encoding="utf-8")
        return p


class ItRunsWhatIsThere(AHelper, unittest.TestCase):
    def test_it_finds_every_test_file_and_nothing_else(self):
        self.write("test_a.py")
        self.write("test_b.py", FAIL)
        self.write("helper.py")
        self.write("not_a_test.py")
        found = [p.name for p in sw.test_files(self.tests)]
        self.assertEqual(found, ["test_a.py", "test_b.py"])

    def test_a_green_file_is_green(self):
        self.write("test_a.py")
        results = sw.run_suite(sw.test_files(self.tests), jobs=1)
        self.assertEqual([r["outcome"] for r in results], ["ok"])

    def test_an_empty_directory_is_not_a_pass(self):
        self.assertEqual(sw.main(["--tests-dir", str(self.tests), "--no-report"]), 2)


class ItNamesWhatFails(AHelper, unittest.TestCase):
    def test_a_failing_file_is_named_with_its_last_line(self):
        self.write("test_bad.py", FAIL)
        results = sw.run_suite(sw.test_files(self.tests), jobs=1)
        data = sw.report(results, "abc1234", 1.0)
        summary = data["summary"]
        self.assertEqual(summary["failed"], ["test_bad.py"])
        printed = "\n".join(sw.lines(data))
        self.assertIn("test_bad.py", printed)
        self.assertIn("the thing is broken", printed, "the report dropped the reason and kept the name")

    def test_the_exit_code_is_nonzero_when_something_fails(self):
        self.write("test_bad.py", FAIL)
        self.assertEqual(sw.main(["--tests-dir", str(self.tests), "--no-report"]), 1)

    def test_a_timeout_is_not_reported_as_a_failure(self):
        self.write("test_slow.py", HANG)
        results = sw.run_suite(sw.test_files(self.tests), jobs=1, timeout=2)
        self.assertEqual(results[0]["outcome"], "timeout")
        summary = sw.report(results, "abc1234", 2.0)["summary"]
        self.assertEqual(summary["timeout"], ["test_slow.py"])
        self.assertEqual(summary["failed"], [], "a slow file was called a failure")
        self.assertIn("no exit after 2 s", sw.lines(sw.report(results, "abc", 2.0))[0])

    def test_it_still_exits_nonzero_on_a_timeout(self):
        self.write("test_slow.py", HANG)
        self.assertEqual(sw.main(["--tests-dir", str(self.tests), "--no-report", "--timeout", "2"]), 1)


class ItWritesDownWhatItSaw(AHelper, unittest.TestCase):
    def test_the_report_names_the_commit_it_measured(self):
        self.write("test_a.py")
        data = sw.report(sw.run_suite(sw.test_files(self.tests), jobs=1), "deadbee", 0.5)
        latest = sw.write_report(data, report_dir=self.root / "reports")
        body = json.loads(latest.read_text(encoding="utf-8"))
        self.assertEqual(body["commit"], "deadbee")
        self.assertRegex(body["measured_at"], r"^\d{4}-\d{2}-\d{2}T")
        self.assertEqual(len(body["results"]), 1, "the report kept the summary and threw away the detail")

    def test_the_summary_counts_agree_with_the_results(self):
        self.write("test_a.py")
        self.write("test_b.py", FAIL)
        data = sw.report(sw.run_suite(sw.test_files(self.tests), jobs=2), "deadbee", 1.0)
        s = data["summary"]
        self.assertEqual(s["ran"], len(data["results"]))
        self.assertEqual(len(s["ok"]) + len(s["failed"]) + len(s["timeout"]) + len(s["could_not_run"]),
                         s["ran"])

    def test_the_live_tree_is_what_it_would_run(self):
        files = sw.test_files(ROOT / "tests")
        self.assertGreater(len(files), 200, "fewer than 200 test files found: the glob is wrong")


if __name__ == "__main__":
    unittest.main(verbosity=2)
