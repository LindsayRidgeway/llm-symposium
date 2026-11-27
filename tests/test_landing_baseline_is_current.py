#!/usr/bin/env python3
"""Can the committed landing baseline excuse a failure it never saw?

Why this exists (2026-11-27, Desi). Value queue item `red-tests-on-main` was filed
because the landing gate refuses with a count — "4 already failing on main before
this diff" — and names none of them, so a fifth real failure hides among the four.
Three of its four closing conditions are met: the four were named by a live
measurement, the one that was real was repaired, and the baseline was re-recorded
at a named commit. The fourth — *a registered test fails when main carries a
failure the baseline does not name* — was recorded as unmet because nothing in this
repository read `tests/landing-baseline.json`; the file had no consumer to guard.

It has one now, and the reason is a measurement rather than a preference. On
2026-11-27 the committed baseline said `"files": 242` while `tests/` held 243
`test_*.py` — one file had been added after the baseline was written, and any
failure in it would have been excused by a baseline that never ran it. That is the
same defect one layer down: the count was believed, the names were not kept.

So `scripts/landing_suite_check.py` now records `measured_files` on every write,
and `baseline_problems()` returns a named string for each way the committed file
can lie. This test applies it to the real baseline at every landing, and mutates a
good baseline so the detector is proven able to fail rather than merely proven able
to pass.

What it does *not* do, said plainly because the queue's condition asks for it: it
does not measure `main`. Deciding "main now carries a failure the baseline does not
name" requires running the suite (about five minutes), which cannot be a test that
every landing runs. The cheap half is the half that can be enforced here — a
baseline may not excuse a file it never executed, and may not excuse a failure
without writing down why it stays red.

Run directly:  python3 tests/test_landing_baseline_is_current.py
"""
from __future__ import annotations

import importlib.util
import json
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

TREE = sorted(path.name for path in (ROOT / "tests").glob("test_*.py"))

PASSING = "import unittest\n\n\nclass T(unittest.TestCase):\n    def test_ok(self):\n        pass\n\n\nif __name__ == '__main__':\n    unittest.main()\n"
FAILING = "import unittest\n\n\nclass T(unittest.TestCase):\n    def test_bad(self):\n        self.assertEqual(1, 2)\n\n\nif __name__ == '__main__':\n    unittest.main()\n"


def _tree(*names_and_bodies):
    """A throwaway directory holding the named test files, as `tests/` would."""
    tmp = Path(tempfile.mkdtemp(prefix="landing-baseline-test-"))
    tests = tmp / "tests"
    tests.mkdir()
    for name, body in names_and_bodies:
        (tests / name).write_text(body, encoding="utf8")
    return tests


def _baseline(**overrides):
    """A baseline that is sound against `["test_a.py", "test_b.py"]`."""
    data = {
        "commit": "abc1234",
        "measured_at": "2026-11-27T00:00:00Z",
        "files": 2,
        "seconds": 1.0,
        "failures": [],
        "measured_files": ["test_a.py", "test_b.py"],
        "notes": [],
    }
    data.update(overrides)
    return data


TWO_FILES = ["test_a.py", "test_b.py"]


class TheCommittedBaselineTest(unittest.TestCase):
    """The real file, against the real tests directory. This is the gate."""

    def test_the_committed_baseline_cannot_excuse_anything_it_never_saw(self):
        baseline = lsc.load_baseline(lsc.BASELINE_PATH)
        self.assertIsNotNone(baseline, "no readable tests/landing-baseline.json")
        self.assertEqual(lsc.baseline_problems(baseline, TREE), [])

    def test_the_tree_being_compared_is_the_real_one(self):
        # If this fails, the comparison above is against some other directory and
        # its silence means nothing.
        self.assertIn("test_landing_baseline_is_current.py", TREE)
        self.assertGreater(len(TREE), 200)

    def test_the_baseline_names_the_commit_it_measured(self):
        baseline = lsc.load_baseline(lsc.BASELINE_PATH)
        commit = str(baseline.get("commit", ""))
        self.assertRegex(commit, r"^[0-9a-f]{7,40}$")

    def test_the_measured_set_is_the_whole_tree_not_a_count(self):
        baseline = lsc.load_baseline(lsc.BASELINE_PATH)
        self.assertEqual(sorted(baseline.get("measured_files") or []), TREE)

    def test_every_excused_failure_is_given_a_reason(self):
        # Vacuous while the list is empty, which is the correct direction. It stops
        # the first time a wake adds a name without saying why it stays red.
        baseline = lsc.load_baseline(lsc.BASELINE_PATH)
        notes = " ".join(str(note) for note in (baseline.get("notes") or []))
        for name in baseline.get("failures") or []:
            self.assertIn(name, notes)


class AFileTheBaselineNeverMeasuredTest(unittest.TestCase):
    """The defect measured on 2026-11-27: 242 files recorded, 243 in the tree."""

    def test_a_new_test_file_is_named_as_unmeasured(self):
        problems = lsc.baseline_problems(_baseline(), TWO_FILES + ["test_c.py"])
        self.assertEqual(
            problems, ["test file not measured by this baseline: test_c.py"]
        )

    def test_a_baseline_older_than_the_tree_is_what_the_real_file_was(self):
        # The exact shape of the committed file on 2026-11-27, one key absent.
        stale = _baseline(files=2)
        stale.pop("measured_files")
        problems = lsc.baseline_problems(stale, TWO_FILES + ["test_c.py"])
        self.assertEqual(len(problems), 1)
        self.assertIn("no measured_files", problems[0])

    def test_a_measured_file_that_is_gone_is_named(self):
        problems = lsc.baseline_problems(_baseline(), ["test_a.py"])
        self.assertEqual(
            problems, ["baseline measured a test file that is gone: test_b.py"]
        )

    def test_the_count_must_agree_with_the_names(self):
        problems = lsc.baseline_problems(_baseline(files=3), TWO_FILES)
        self.assertEqual(len(problems), 1)
        self.assertIn("says 3 files but measured_files names 2", problems[0])

    def test_an_excused_failure_outside_the_measured_set_is_named(self):
        problems = lsc.baseline_problems(
            _baseline(failures=["test_z.py"], notes=["test_z.py stays red"]), TWO_FILES
        )
        self.assertEqual(
            problems, ["baseline excuses a failure it never measured: test_z.py"]
        )


class AReasonIsRequiredTest(unittest.TestCase):
    def test_an_excused_failure_without_a_reason_is_named(self):
        problems = lsc.baseline_problems(_baseline(failures=["test_a.py"]), TWO_FILES)
        self.assertEqual(
            problems,
            ["baseline excuses a failure with no reason in notes: test_a.py"],
        )

    def test_an_excused_failure_with_a_reason_passes(self):
        problems = lsc.baseline_problems(
            _baseline(
                failures=["test_a.py"],
                notes=["test_a.py stays red until the auditor is re-run"],
            ),
            TWO_FILES,
        )
        self.assertEqual(problems, [])

    def test_a_reason_for_a_different_file_does_not_excuse_this_one(self):
        problems = lsc.baseline_problems(
            _baseline(
                failures=["test_a.py", "test_b.py"], notes=["test_a.py: known"]
            ),
            TWO_FILES,
        )
        self.assertEqual(
            problems, ["baseline excuses a failure with no reason in notes: test_b.py"]
        )


class TheSafeDirectionsTest(unittest.TestCase):
    def test_no_baseline_at_all_is_a_named_problem_not_a_crash(self):
        self.assertEqual(
            lsc.baseline_problems(None, TWO_FILES),
            ["no recorded baseline: every failure counts as new"],
        )

    def test_a_sound_baseline_has_no_problems(self):
        self.assertEqual(lsc.baseline_problems(_baseline(), TWO_FILES), [])


class TheWriterRecordsWhatItRanTest(unittest.TestCase):
    """The key has to be written, or the guard above can never be satisfied."""

    def test_writing_a_baseline_records_every_measured_file(self):
        tests = _tree(("test_a.py", PASSING), ("test_b.py", FAILING))
        rows = lsc.run_suite(tests)
        path = Path(tempfile.mkdtemp()) / "landing-baseline.json"
        written = lsc.write_baseline(rows, "abc1234", path)
        self.assertEqual(written["measured_files"], ["test_a.py", "test_b.py"])
        self.assertEqual(written["files"], 2)
        self.assertEqual(
            json.loads(path.read_text(encoding="utf8"))["measured_files"],
            ["test_a.py", "test_b.py"],
        )

    def test_a_written_baseline_then_needs_a_reason_for_its_failure(self):
        tests = _tree(("test_a.py", PASSING), ("test_b.py", FAILING))
        path = Path(tempfile.mkdtemp()) / "landing-baseline.json"
        lsc.write_baseline(lsc.run_suite(tests), "abc1234", path)
        problems = lsc.baseline_problems(lsc.load_baseline(path), ["test_a.py", "test_b.py"])
        self.assertEqual(
            problems, ["baseline excuses a failure with no reason in notes: test_b.py"]
        )

    def test_a_written_baseline_covers_a_tree_gaining_a_file(self):
        tests = _tree(("test_a.py", PASSING))
        path = Path(tempfile.mkdtemp()) / "landing-baseline.json"
        lsc.write_baseline(lsc.run_suite(tests), "abc1234", path)
        problems = lsc.baseline_problems(
            lsc.load_baseline(path), ["test_a.py", "test_added_later.py"]
        )
        self.assertEqual(
            problems,
            ["test file not measured by this baseline: test_added_later.py"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
