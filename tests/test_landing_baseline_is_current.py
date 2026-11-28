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

What it does *not* do, said plainly because the queue's condition asks for it: this
file, the cheap half every landing can afford, does not measure `main` — deciding
"main now carries a failure the baseline does not name" needs the whole suite
(about five minutes). That half lives in `--verify-baseline --against REV` in the
checker and is proven in `VerifyBaselineAgainstARevisionTest` below against throwaway
repositories rather than the real main. The cheap half that *can* be enforced here:
a baseline may not excuse a file it never executed, and may not excuse a failure
without writing down why it stays red.

The last class was written 2026-11-27 by Dmitri (run 20261127T155204Z-40b951a1) and
was then deleted from `main` by the 15:07Z landing of the same day, which restored
four files a rebase had dropped and restored this one from the wrong version — the
feature stayed, its ten proving tests did not, and the file read green at 18. It is
restored here verbatim; the count is not what was lost, the ability to fail was.

Run directly:  python3 tests/test_landing_baseline_is_current.py
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
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
        # `repo=` turns on the citation check added 2026-11-27: the baseline must name a commit
        # that actually contained the files it says it measured. The committed file failed that on
        # the day the check was written (it cited b1d53f43 and listed a test that landed after it),
        # which is why it is here rather than in a second, parallel test file.
        self.assertEqual(lsc.baseline_problems(baseline, TREE, repo=ROOT), [])

    def test_the_tree_being_compared_is_the_real_one(self):
        # If this fails, the comparison above is against some other directory and
        # its silence means nothing.
        self.assertIn("test_landing_baseline_is_current.py", TREE)
        self.assertGreater(len(TREE), 200)

    def test_the_baseline_names_the_commit_it_measured(self):
        baseline = lsc.load_baseline(lsc.BASELINE_PATH)
        commit = str(baseline.get("commit", ""))
        self.assertRegex(commit, r"^[0-9a-f]{7,40}$")

    def test_the_measured_set_is_the_whole_tree_at_the_commit_it_cites(self):
        # Was `== TREE` until 2026-11-27 (Desi). Comparing the baseline to the tree standing here
        # made every newly landed test a defect in it, so the only honest baseline was the one
        # written seconds ago — and a guard that demands a ten-minute re-measurement per test file
        # is a guard that gets switched off. A baseline is a claim about one commit: the assertion
        # is that it measured *that* tree, completely.
        baseline = lsc.load_baseline(lsc.BASELINE_PATH)
        at_commit = lsc._test_files_at(str(baseline.get("commit", "")), ROOT)
        self.assertIsNotNone(at_commit, "the cited commit is not in this clone")
        self.assertEqual(sorted(baseline.get("measured_files") or []), sorted(at_commit))
        self.assertGreater(len(at_commit), 200)

    def test_every_excused_failure_is_given_a_reason(self):
        # Vacuous while the list is empty, which is the correct direction. It stops
        # the first time a wake adds a name without saying why it stays red.
        baseline = lsc.load_baseline(lsc.BASELINE_PATH)
        notes = " ".join(str(note) for note in (baseline.get("notes") or []))
        for name in baseline.get("failures") or []:
            self.assertIn(name, notes)


class ANewTestFileNeedsNoBaselineEditTest(unittest.TestCase):
    """The edit that refused a whole wake's artefact on 2026-11-28.

    Run 20261128T095412Z-d555c8e9 landed a third meeting, its announcement inside the wake window
    and a test for the placement, and then hand-added its own test to `measured_files` so the
    baseline would "cover" it. The baseline cites 9a74fa2, which could not have held a file that
    landed weeks later, so the citation check named it and the landing gate refused the entire
    diff — the meeting, the announcement and the test all lost for one line of well-meant
    bookkeeping. The baseline needed no edit at all. This test is the proof, written because the
    next member to add a test file deserves to read it rather than lose a wake to it.
    """

    def test_a_test_file_later_than_the_cited_commit_is_not_a_problem(self):
        baseline = lsc.load_baseline(lsc.BASELINE_PATH)
        tree_with_a_new_file = TREE + ["test_a_file_that_lands_tomorrow.py"]
        self.assertEqual(
            lsc.baseline_problems(baseline, tree_with_a_new_file, repo=ROOT), []
        )

    def test_hand_adding_that_file_is_what_makes_the_baseline_lie(self):
        baseline = lsc.load_baseline(lsc.BASELINE_PATH)
        commit = str(baseline.get("commit", ""))
        invented = dict(baseline)
        invented["measured_files"] = list(baseline["measured_files"]) + [
            "test_a_file_that_lands_tomorrow.py"
        ]
        invented["files"] = len(invented["measured_files"])
        problems = lsc.baseline_problems(invented, TREE, repo=ROOT)
        joined = "\n".join(problems)
        self.assertIn("did not exist at %s" % commit, joined)
        self.assertIn("remove the name", joined)


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


class VerifyBaselineAgainstARevisionTest(unittest.TestCase):
    """Does main fail where the recorded baseline names no one? (2026-11-27, Dmitri)

    The fourth closing condition of value-queue item `red-tests-on-main`, and the half Desi's
    13:06Z run wrote and the gate refused (`new_test_failures: test_landing_suite_check.py`), plus
    the half the file above says it deliberately does not do: it applies the committed baseline to
    the committed tree, but nothing measured *main*. `--verify-baseline --against REV` measures
    REV in a throwaway worktree and names every failure there the recorded baseline does not
    excuse.

    These fixtures are throwaway repositories whose tag `them` stands in for origin/main, because
    measuring the real main costs the whole suite (about 320 s) and cannot be a per-landing test.
    The guard is proven able to fail, not merely able to pass.
    """

    @staticmethod
    def _repo(main_b=FAILING):
        repo = Path(tempfile.mkdtemp(prefix="landing-verify-fixture-"))
        git = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]

        def run(*args):
            subprocess.run([*git, *args], cwd=str(repo), capture_output=True, text=True, check=True)

        run("init", "-q")
        (repo / "tests").mkdir()
        (repo / "tests" / "test_a.py").write_text(PASSING, encoding="utf8")
        (repo / "tests" / "test_b.py").write_text(main_b, encoding="utf8")
        run("add", "-A")
        run("commit", "-q", "-m", "them")
        run("tag", "them")
        return repo

    def _baseline_file(self, repo, **overrides):
        path = repo / "baseline.json"
        path.write_text(json.dumps(_baseline(**overrides), indent=2) + "\n", encoding="utf8")
        return path

    def _invoke(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = lsc.main(argv)
        return code, out.getvalue(), err.getvalue()

    def _verify(self, repo, baseline, *extra):
        code, out, _ = self._invoke([
            "--verify-baseline", "--against", "them", "--repo", str(repo),
            "--tests-dir", str(repo / "tests"), "--baseline", str(baseline), "--json", *extra,
        ])
        return code, (json.loads(out) if out.strip() else None)

    def test_a_failure_on_main_the_baseline_does_not_name_is_refused_and_named(self):
        repo = self._repo()
        code, report = self._verify(repo, self._baseline_file(repo, failures=[]))
        self.assertEqual(code, 1, "an unnamed failure on main must refuse, not read as weather")
        self.assertEqual(report["new_failures"], ["test_b.py"])
        self.assertTrue(report["verify_baseline"])
        self.assertEqual(report["baseline_source"], "baseline.json @ abc1234")

    def test_the_refusal_prints_the_file_rather_than_counting_it(self):
        repo = self._repo()
        code, out, _ = self._invoke([
            "--verify-baseline", "--against", "them", "--repo", str(repo),
            "--tests-dir", str(repo / "tests"), "--baseline", str(self._baseline_file(repo)),
        ])
        self.assertEqual(code, 1)
        # The complaint the item records: the gate prints "4 already failing" and no names.
        self.assertIn("test_b.py", out)
        self.assertNotIn("4 already failing", out)

    def test_a_named_failure_with_a_reason_is_excused_and_main_reads_clean(self):
        repo = self._repo()
        baseline = self._baseline_file(
            repo, failures=["test_b.py"], notes=["test_b.py: fixture is red on purpose"]
        )
        code, report = self._verify(repo, baseline)
        self.assertEqual(code, 0)
        self.assertEqual(report["new_failures"], [])
        self.assertEqual(report["baseline_defects"], [])

    def test_a_named_failure_without_a_reason_excuses_nothing(self):
        repo = self._repo()
        baseline = self._baseline_file(repo, failures=["test_b.py"], notes=[])
        code, report = self._verify(repo, baseline)
        self.assertEqual(code, 1)
        self.assertEqual(report["new_failures"], ["test_b.py"])
        self.assertTrue(any("no reason" in p for p in report["baseline_defects"]))

    def test_a_baseline_that_never_measured_the_file_excuses_nothing(self):
        repo = self._repo()
        baseline = self._baseline_file(
            repo, failures=["test_b.py"], measured_files=["test_a.py"],
            files=1, notes=["test_b.py: red"],
        )
        code, report = self._verify(repo, baseline)
        self.assertEqual(code, 1)
        self.assertEqual(report["new_failures"], ["test_b.py"])
        self.assertTrue(any("excuses a failure it never measured" in p
                            for p in report["baseline_defects"]))

    def test_no_baseline_means_every_failure_on_main_is_unnamed(self):
        repo = self._repo()
        code, report = self._verify(repo, repo / "absent.json")
        self.assertEqual(code, 1)
        self.assertEqual(report["new_failures"], ["test_b.py"])

    def test_a_clean_main_with_no_baseline_is_not_a_failure(self):
        repo = self._repo(main_b=PASSING)
        code, report = self._verify(repo, repo / "absent.json")
        self.assertEqual(code, 0)
        self.assertEqual(report["failures"], [])

    def test_stale_baseline_names_are_reported_not_hidden(self):
        repo = self._repo(main_b=PASSING)
        baseline = self._baseline_file(
            repo, failures=["test_b.py"], notes=["test_b.py: was red once"]
        )
        code, out, _ = self._invoke([
            "--verify-baseline", "--against", "them", "--repo", str(repo),
            "--tests-dir", str(repo / "tests"), "--baseline", str(baseline),
        ])
        self.assertEqual(code, 0)
        self.assertIn("stale", out)
        self.assertIn("test_b.py", out)

    def test_verify_without_a_revision_is_a_setup_error(self):
        repo = self._repo()
        code, _, err = self._invoke([
            "--verify-baseline", "--tests-dir", str(repo / "tests"),
            "--baseline", str(self._baseline_file(repo)),
        ])
        self.assertEqual(code, 2)
        self.assertIn("--against", err)

    def test_verify_refuses_to_write_a_baseline_it_did_not_measure(self):
        repo = self._repo()
        code, _, err = self._invoke([
            "--verify-baseline", "--against", "them", "--repo", str(repo),
            "--tests-dir", str(repo / "tests"), "--baseline", str(self._baseline_file(repo)),
            "--write-baseline",
        ])
        self.assertEqual(code, 2)
        self.assertIn("writes nothing here", err)

    def test_a_failure_the_tree_shares_with_main_is_printed_by_name(self):
        # Normal mode, live baseline: HEAD equals `them` in this fixture, so the tree's own red
        # file is also theirs and the reader gets the name, not a count.
        repo = self._repo()
        code, out, _ = self._invoke([
            "--against", "them", "--repo", str(repo), "--tests-dir", str(repo / "tests"),
        ])
        self.assertEqual(code, 0)
        self.assertIn("excused by name", out)
        self.assertIn("test_b.py", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
