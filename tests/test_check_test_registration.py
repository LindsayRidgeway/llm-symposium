#!/usr/bin/env python3
"""Tests for scripts/check_test_registration.py — the guard that no test file is left unrun.

The guard exists because a test nobody runs cannot fail, so it cannot warn anyone: two of
the first test files it looked at had been broken from the day they were written. These tests
pin both halves of that claim:

  * the check is not vacuous — a test file named by no workflow is reported (case 1);
  * exemption works, and cannot rot — an exempt name that is not on disk is reported;
  * the real tree is clean — every test file in this repository is either run by a workflow
    or exempted with a reason, so the guard passes on landing rather than blocking it.
"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_test_registration", ROOT / "scripts" / "check_test_registration.py")
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)


def _tree(tmp: Path, test_names, workflow_text: str | None = None) -> tuple[Path, Path]:
    tests = tmp / "tests"
    tests.mkdir()
    for name in test_names:
        (tests / name).write_text("#!/usr/bin/env python3\n", encoding="utf-8")
    wfs = tmp / ".github" / "workflows"
    wfs.mkdir(parents=True)
    if workflow_text is not None:
        (wfs / "suite.yml").write_text(workflow_text, encoding="utf-8")
    return tests, wfs


class GuardTests(unittest.TestCase):
    def test_collects_only_test_files(self):
        with tempfile.TemporaryDirectory() as d:
            tests, _ = _tree(Path(d), ["test_a.py", "validate_b.mjs", "helper.py", "notes.md"])
            self.assertEqual(guard.collect_test_files(tests), ["test_a.py", "validate_b.mjs"])

    def test_flags_a_test_named_by_no_workflow(self):
        with tempfile.TemporaryDirectory() as d:
            tests, wfs = _tree(
                Path(d), ["test_run.py", "test_ghost.py"],
                "run: python3 tests/test_run.py\n")
            self.assertEqual(
                guard.find_unregistered(tests, wfs, {}), ["test_ghost.py"])

    def test_a_reference_from_any_workflow_counts(self):
        with tempfile.TemporaryDirectory() as d:
            tests, wfs = _tree(
                Path(d), ["test_run.py", "validate_page.mjs"],
                "run: python3 tests/test_run.py && node tests/validate_page.mjs\n")
            self.assertEqual(guard.find_unregistered(tests, wfs, {}), [])

    def test_exemption_suppresses_a_finding(self):
        with tempfile.TemporaryDirectory() as d:
            tests, wfs = _tree(Path(d), ["validate_live.mjs"], "run: python3 scripts/other.py\n")
            self.assertEqual(
                guard.find_unregistered(tests, wfs, {}), ["validate_live.mjs"])
            self.assertEqual(
                guard.find_unregistered(tests, wfs, {"validate_live.mjs": "live network"}), [])

    def test_stale_exemption_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            tests, _ = _tree(Path(d), ["test_a.py"])
            self.assertEqual(
                guard.stale_exemptions(tests, {"was_deleted.py": "gone"}), ["was_deleted.py"])
            self.assertEqual(guard.stale_exemptions(tests, {"test_a.py": "here"}), [])

    def test_no_workflows_directory_reports_everything(self):
        with tempfile.TemporaryDirectory() as d:
            tests, _ = _tree(Path(d), ["test_a.py", "test_b.py"])
            missing = Path(d) / "nope"
            self.assertEqual(
                guard.find_unregistered(tests, missing, {}), ["test_a.py", "test_b.py"])

    def test_the_real_repository_is_clean(self):
        # The whole point: on landing, this check must pass. If it does not, a test file
        # has been added without being registered or exempted, or an exemption has gone stale.
        self.assertEqual(
            guard.find_unregistered(guard.TESTS_DIR, guard.WORKFLOWS_DIR, guard.EXEMPT), [])
        self.assertEqual(guard.stale_exemptions(guard.TESTS_DIR, guard.EXEMPT), [])

    def test_the_guard_is_itself_run(self):
        # A guard that is never invoked is exactly the defect it polices. Keep the honest
        # form: the check must name itself in a workflow, or be exempt — and it is neither.
        registered = guard.collect_registered(guard.WORKFLOWS_DIR)
        self.assertIn("test_check_test_registration.py", registered)


if __name__ == "__main__":
    unittest.main(verbosity=2)
