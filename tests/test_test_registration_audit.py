#!/usr/bin/env python3
"""The audit that keeps the suite's own promises — including the one it makes about itself.

Why this file exists (2026-10-19, desi). `scripts/test_registration_audit.py` reports every test
file on disk that no workflow executes. Its whole value is that a new unregistered test is caught
the moment it lands, because a test that runs nowhere is worse than no test: the artefact that
cites it reads as verified and is not. So the audit has to be right about two things the
repository makes easy to get wrong —

  * a **commented-out** command is not a registration. This repository retired most of its
    schedules by commenting the cron out and writing a paragraph about why; every workflow file
    is full of commented test invocations. A scanner that counted them would call the retired
    suite covered.
  * an **exemption** is a reason, not a bin. An exempt path that is now registered, or that no
    longer exists, fails the audit in the other direction, so the allowlist cannot rot.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from scripts import test_registration_audit as tra  # noqa: E402


def build(root: Path, workflows: dict[str, str], tests: list[str]) -> Path:
    wf = root / ".github" / "workflows"
    wf.mkdir(parents=True)
    for name, text in workflows.items():
        (wf / name).write_text(text, encoding="utf-8")
    (root / "tests").mkdir()
    for name in tests:
        (root / "tests" / name).write_text("# placeholder\n", encoding="utf-8")
    return root


class ScanTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_a_live_command_registers_a_test(self):
        build(self.root, {"ci.yml": "run: python3 tests/test_alpha.py\n"}, ["test_alpha.py"])
        self.assertEqual({"test_alpha.py": ["ci.yml"]}, tra.scan_workflows(self.root))

    def test_a_commented_out_command_does_not(self):
        """The retirement pattern: the cron is commented out and so is the test beside it."""
        build(self.root, {"ci.yml": (
            "  # Retired from the schedule 2026-09-25 (Desi).\n"
            "  #   python3 tests/test_alpha.py\n"
            "          # python3 tests/test_beta.py 2>&1 | tee -a out.txt\n")},
              ["test_alpha.py", "test_beta.py"])
        self.assertEqual({}, tra.scan_workflows(self.root))

    def test_a_command_with_a_trailing_comment_still_counts(self):
        build(self.root, {"ci.yml": "python3 tests/test_alpha.py  # the old pin\n"},
              ["test_alpha.py"])
        self.assertIn("test_alpha.py", tra.scan_workflows(self.root))

    def test_the_same_test_in_two_workflows_names_both_once_each(self):
        build(self.root, {"a.yml": "python3 tests/test_alpha.py\n",
                          "b.yml": "python3 tests/test_alpha.py\npython3 tests/test_alpha.py\n"},
              ["test_alpha.py"])
        self.assertEqual(["a.yml", "b.yml"], tra.scan_workflows(self.root)["test_alpha.py"])

    def test_prose_that_merely_names_a_file_is_not_an_execution(self):
        build(self.root, {"ci.yml": "# see tests/test_alpha.py for the guard\n"},
              ["test_alpha.py"])
        self.assertEqual({}, tra.scan_workflows(self.root))


class AuditTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        build(self.root, {"ci.yml": "python3 tests/test_runs.py\n"},
              ["test_runs.py", "test_orphan.py"])

    def test_a_test_no_workflow_runs_is_the_failure(self):
        res = tra.audit(self.root, exempt={})
        self.assertFalse(res["ok"])
        self.assertEqual(["tests/test_orphan.py"], res["unregistered"])
        self.assertEqual(2, res["on_disk"])
        self.assertEqual(1, res["registered"])

    def test_an_exemption_with_a_reason_is_a_pass(self):
        res = tra.audit(self.root, exempt={"tests/test_orphan.py": "needs the live rover host"})
        self.assertTrue(res["ok"])
        self.assertEqual([], res["unregistered"])
        self.assertEqual({"tests/test_orphan.py": "needs the live rover host"}, res["exempt"])

    def test_an_exemption_with_no_reason_is_not(self):
        res = tra.audit(self.root, exempt={"tests/test_orphan.py": "  "})
        self.assertFalse(res["ok"])
        self.assertEqual(["tests/test_orphan.py"], res["exempt_without_reason"])

    def test_an_exemption_that_is_now_registered_is_stale_not_silent(self):
        """The allowlist rots in the other direction too: someone registers the file and the
        reason for not running it stays behind, now false."""
        res = tra.audit(self.root, exempt={"tests/test_runs.py": "used to need the network"})
        self.assertFalse(res["ok"])
        self.assertEqual(["tests/test_runs.py"], res["allowlist_problems"]["now_registered"])

    def test_an_exemption_for_a_file_that_is_gone_is_stale_too(self):
        res = tra.audit(self.root, exempt={"tests/test_deleted.py": "was host-only"})
        self.assertFalse(res["ok"])
        self.assertEqual(["tests/test_deleted.py"], res["allowlist_problems"]["gone"])

    def test_no_workflow_directory_is_not_a_crash(self):
        res = tra.audit(Path(self.tmp.name) / "empty", exempt={})
        self.assertFalse(res["ok"])
        self.assertEqual(0, res["on_disk"])


class TheRepositoryTest(unittest.TestCase):
    """The pin that matters: this repository, as it will be a moment after this lands."""

    def test_every_test_on_disk_runs_somewhere_or_says_why(self):
        res = tra.audit(REPO)
        self.assertTrue(
            res["ok"],
            "unregistered: %s; stale exemptions: %s; no reason: %s"
            % (res["unregistered"], res["allowlist_problems"], res["exempt_without_reason"]))

    def test_the_retired_tarik_cloud_suite_counts_as_registered(self):
        """Registration is 'some workflow', not 'the main one': two Tarik tests live in
        `tarik-cloud-queue.yml` and the old single-workflow reading called them orphans."""
        res = tra.audit(REPO)
        self.assertIn("test_tarik_cloud_transport.py", res["workflows"])
        self.assertEqual(["tarik-cloud-queue.yml"],
                         res["workflows"]["test_tarik_cloud_transport.py"])

    def test_the_command_line_exits_zero_and_says_so(self):
        out = subprocess.run([sys.executable, str(REPO / "scripts" / "test_registration_audit.py"),
                              "--json"], capture_output=True, text=True)
        self.assertEqual(0, out.returncode, out.stdout[-2000:] + out.stderr[-2000:])
        self.assertTrue(json.loads(out.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
