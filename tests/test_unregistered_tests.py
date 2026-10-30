#!/usr/bin/env python3
"""Tests for scripts/unregistered_tests.py — the census of test files against the workflows.

Written 2026-10-30 (Desi). The script exists because the same defect recurred three times: a test file
landed with a runner, and nothing in CI ever invoked it. A gate for that defect has to be right about
what "runs" means, and its own first draft was not — it called six working test files no-ops because
their checks are module-level statements rather than a `__main__` block. Two of the cases below pin
that, so the mistake cannot come back quietly.

Offline, temp directories, about a second.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts import unregistered_tests as U  # noqa: E402

MAIN_BLOCK = '\nif __name__ == "__main__":\n    sys.exit(0)\n'
BARE_SCRIPT = '\nfails = []\nprint("all checks passed")\nsys.exit(1 if fails else 0)\n'
PYTEST_STYLE = '\ndef test_one():\n    assert True\n'
TESTCASE_STYLE = '\nclass Foo(unittest.TestCase):\n    def test_one(self):\n        pass\n'
UNITTEST_MAIN = '\nif __name__ == "__main__":\n    unittest.main()\n'


class Fixture:
    """A throwaway tests/ directory and workflows/ directory, so the real repository is never read."""

    def __init__(self, files: dict[str, str], workflows: dict[str, str]):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.tests = root / "tests"
        self.workflows = root / ".github" / "workflows"
        self.tests.mkdir(parents=True)
        self.workflows.mkdir(parents=True)
        for name, body in files.items():
            (self.tests / name).write_text("import sys, unittest\n" + body, encoding="utf-8")
        for name, body in workflows.items():
            (self.workflows / name).write_text(body, encoding="utf-8")

    def result(self) -> dict[str, list[dict]]:
        return U.classify(self.tests, self.workflows)

    def close(self) -> None:
        self.tmp.cleanup()


def run(files, workflows):
    f = Fixture(files, workflows)
    try:
        return f.result()
    finally:
        f.close()


class ClassificationTests(unittest.TestCase):
    def test_a_registered_runner_is_the_silent_good_state(self):
        r = run({"test_a.py": MAIN_BLOCK}, {"ci.yml": "python3 tests/test_a.py\n"})
        self.assertEqual(r["missing"], [])
        self.assertEqual(r["no_op"], [])
        self.assertEqual(r["exempt"], [])

    def test_a_runner_no_workflow_names_is_missing(self):
        r = run({"test_a.py": MAIN_BLOCK}, {"ci.yml": "python3 tests/test_b.py\n"})
        self.assertEqual([x["test"] for x in r["missing"]], ["test_a.py"])
        self.assertEqual(r["dangling"][0]["test"], "test_b.py")

    def test_unittest_main_counts_as_a_runner(self):
        r = run({"test_a.py": UNITTEST_MAIN}, {"ci.yml": "echo nothing\n"})
        self.assertEqual([x["test"] for x in r["missing"]], ["test_a.py"])

    def test_a_bare_script_is_not_a_no_op(self):
        """The first draft's mistake: module-level checks are a runner too, and six real files run that way."""
        r = run({"test_a.py": BARE_SCRIPT}, {"ci.yml": "python3 tests/test_a.py\n"})
        self.assertEqual(r["no_op"], [])
        self.assertEqual(r["missing"], [])

    def test_an_unregistered_bare_script_is_missing_not_exempt(self):
        r = run({"test_a.py": BARE_SCRIPT}, {"ci.yml": "echo nothing\n"})
        self.assertEqual([x["test"] for x in r["missing"]], ["test_a.py"])
        self.assertEqual(r["exempt"], [])

    def test_pytest_style_registered_is_a_no_op(self):
        r = run({"test_a.py": PYTEST_STYLE}, {"ci.yml": "python3 tests/test_a.py\n"})
        self.assertEqual([x["test"] for x in r["no_op"]], ["test_a.py"])

    def test_testcase_without_an_entry_point_is_a_no_op(self):
        r = run({"test_a.py": TESTCASE_STYLE}, {"ci.yml": "python3 tests/test_a.py\n"})
        self.assertEqual([x["test"] for x in r["no_op"]], ["test_a.py"])

    def test_pytest_style_unregistered_is_exempt(self):
        r = run({"test_a.py": PYTEST_STYLE}, {"ci.yml": "echo nothing\n"})
        self.assertEqual([x["test"] for x in r["exempt"]], ["test_a.py"])
        self.assertEqual(r["missing"], [])

    def test_a_path_named_only_in_a_comment_is_not_a_registration(self):
        """This is the case that hid test_item_evidence_lint.py for eleven days."""
        r = run({"test_a.py": MAIN_BLOCK},
                {"ci.yml": "#  python3 tests/test_a.py  is discussed here, not run\npython3 tests/test_b.py\n"})
        self.assertEqual([x["test"] for x in r["missing"]], ["test_a.py"])

    def test_comment_lines_are_skipped_even_with_leading_whitespace(self):
        r = run({"test_a.py": MAIN_BLOCK}, {"ci.yml": "    # python3 tests/test_a.py\n"})
        self.assertEqual([x["test"] for x in r["missing"]], ["test_a.py"])

    def test_unittest_module_form_counts(self):
        r = run({"test_a.py": MAIN_BLOCK}, {"ci.yml": "python3 -m unittest tests.test_a\n"})
        self.assertEqual(r["missing"], [])

    def test_every_workflow_is_scanned_not_only_the_big_one(self):
        r = run({"test_a.py": MAIN_BLOCK}, {"a.yml": "x\n", "b.yaml": "python3 tests/test_a.py\n"})
        self.assertEqual(r["missing"], [])

    def test_workflows_recorded_per_test(self):
        r = run({"test_a.py": MAIN_BLOCK}, {"a.yml": "python3 tests/test_a.py\n", "b.yml": "x\n"})
        self.assertEqual(r["missing"], [])
        f = Fixture({"test_a.py": MAIN_BLOCK}, {"a.yml": "python3 tests/test_a.py\n"})
        try:  # keep the fixture alive: its temp dir is removed when the object is collected
            self.assertEqual(U.registered_names(f.workflows)["test_a"], ["a.yml"])
        finally:
            f.close()

    def test_dangling_names_a_file_that_does_not_exist(self):
        r = run({"test_a.py": MAIN_BLOCK}, {"ci.yml": "python3 tests/test_a.py\npython3 tests/test_gone.py\n"})
        self.assertEqual([x["test"] for x in r["dangling"]], ["test_gone.py"])


class RenderAndExitTests(unittest.TestCase):
    def test_report_prints_all_four_headings(self):
        text = U.render({"missing": [{"test": "test_x.py", "workflows": []}],
                         "no_op": [], "dangling": [], "exempt": []})
        for word in ("MISSING", "NO-OP", "DANGLING", "EXEMPT"):
            self.assertIn(word, text)
        self.assertIn("test_x.py", text)

    def test_empty_result_still_prints_the_headings(self):
        text = U.render({"missing": [], "no_op": [], "dangling": [], "exempt": []})
        self.assertIn("none", text)

    def test_default_run_exits_zero_even_with_findings(self):
        """Report first: a gate that turns landing red on day one blocks every amigo."""
        with tempfile.TemporaryDirectory() as tmp:
            tests = Path(tmp) / "tests"
            tests.mkdir()
            (tests / "test_a.py").write_text("import sys" + MAIN_BLOCK, encoding="utf-8")
            empty = Path(tmp) / "wf"
            empty.mkdir()
            self.assertEqual(U.main(["--tests", str(tests), "--workflows", str(empty)]), 0)
            self.assertEqual(U.main(["--tests", str(tests), "--workflows", str(empty), "--strict"]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
