#!/usr/bin/env python3
"""A file in tests/ must not quietly lose test methods (Desi, 2026-11-27).

The case that motivated this is mine, and it is on the record: commit `f8476bb2` carried
`tests/test_landing_baseline_is_current.py` back from 29 test methods to 18, because it restored an
older copy of the file over a newer one that had landed an hour earlier. Nothing failed. The file still
ran, still printed OK, and checked a repaired baseline with eleven fewer assertions than its author
believed — the baseline guard was itself degraded while it reported health.

It was caught by a wake reading the tree and filing `test-count-cannot-quietly-drop`. That is a reader,
not a guard, and the whole point of the item is that this class of loss should not need one.

Two halves, both here:

  * the live comparison — `tests/test-count-baseline.json` records how many `def test_` each file
    carried, and any file below its recorded count fails by name at every landing;
  * the detector exercised on the real numbers — the 29 → 18 pair is fed to `problems()` as the
    fixture, so this file proves the guard can fail rather than merely proving it can pass.

A drop is allowed, but only written down: `allowed_drops` in the baseline, with a `because`. A reason
not written down is how "it went down and nobody minded" becomes the state of the world.
"""

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def module():
    spec = importlib.util.spec_from_file_location("tcb", ROOT / "scripts" / "test_count_baseline.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


tcb = module()
BASELINE = ROOT / "tests" / "test-count-baseline.json"


class NoFileLosesTestsUnnoticed(unittest.TestCase):
    def test_the_recorded_counts_still_hold(self):
        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        self.assertEqual(tcb.problems(baseline, tcb.counts()), [])

    def test_the_baseline_is_a_measurement_not_an_assertion(self):
        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        self.assertTrue(baseline.get("commit"), "the baseline names no commit")
        self.assertGreater(len(baseline.get("counts") or {}), 200)
        self.assertGreater(sum((baseline.get("counts") or {}).values()), 2000)


class TheDetectorFiresOnTheRealCase(unittest.TestCase):
    """29 → 18 at f8476bb2, as the fixture the queue item asked for."""

    def setUp(self):
        self.baseline = {
            "counts": {"test_landing_baseline_is_current.py": 29, "test_other.py": 4},
            "allowed_drops": {},
        }

    def test_the_drop_that_happened_is_named(self):
        now = {"test_landing_baseline_is_current.py": 18, "test_other.py": 4}
        found = tcb.problems(self.baseline, now)
        self.assertEqual(len(found), 1, found)
        self.assertIn("test_landing_baseline_is_current.py", found[0])
        self.assertIn("29 to 18", found[0])
        self.assertIn("11 fewer", found[0])

    def test_a_file_that_gained_tests_is_not_a_problem(self):
        now = {"test_landing_baseline_is_current.py": 31, "test_other.py": 4}
        self.assertEqual(tcb.problems(self.baseline, now), [])

    def test_a_file_that_disappeared_is_named(self):
        found = tcb.problems(self.baseline, {"test_other.py": 4})
        self.assertEqual(len(found), 1, found)
        self.assertIn("gone from tests/", found[0])

    def test_a_drop_with_a_written_reason_passes(self):
        self.baseline["allowed_drops"] = {
            "test_landing_baseline_is_current.py": {"to": 18, "because": "folded into two stronger tests"}}
        now = {"test_landing_baseline_is_current.py": 18, "test_other.py": 4}
        self.assertEqual(tcb.problems(self.baseline, now), [])

    def test_a_reason_that_is_not_written_down_is_itself_a_problem(self):
        self.baseline["allowed_drops"] = {"test_other.py": {"to": 1}}
        found = tcb.problems(self.baseline, {"test_landing_baseline_is_current.py": 29,
                                             "test_other.py": 1})
        self.assertTrue(any("no `because`" in f for f in found), found)

    def test_a_baseline_with_no_counts_is_not_a_pass(self):
        found = tcb.problems({"commit": "abc"}, {"test_a.py": 3})
        self.assertTrue(found and "no recorded counts" in found[0], found)


class TheRecordIsReadable(unittest.TestCase):
    def test_the_counter_counts_methods_and_functions_alike(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / "test_a.py").write_text(
                "class T(unittest.TestCase):\n"
                "    def test_one(self):\n        pass\n"
                "    def test_two(self):\n        pass\n"
                "def test_three():\n    pass\n"
                "def helper():\n    pass\n", encoding="utf-8")
            self.assertEqual(tcb.counts(d), {"test_a.py": 3})

    def test_a_file_with_no_tests_counts_zero_and_is_still_recorded(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / "test_empty.py").write_text("# nothing yet\n", encoding="utf-8")
            self.assertEqual(tcb.counts(d), {"test_empty.py": 0})


if __name__ == "__main__":
    unittest.main(verbosity=2)
