#!/usr/bin/env python3
"""The review-gate closer must actually classify a branch, and not by accident.

`scripts/review_gate_report.py` exists to answer one question the pile never could: *does this
`drafts/tick-*` branch still hold work that is not on `main`?* If it answers wrong in either
direction the gate fails differently — a false CLEAN deletes unlanded work, a false HOLDING
perpetuates the recompute loop that lost ten wakes to it. So the test builds real branches in a
throwaway git repo and asserts both verdicts against real two-dot diffs, not mocked ones.

Offline. Writes only inside a temp directory.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import review_gate_report as rg  # noqa: E402


class ReviewGateReportTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        self._git("init")
        self._git("symbolic-ref", "HEAD", "refs/heads/main")
        self._git("config", "user.email", "test@example.com")
        self._git("config", "user.name", "Test")
        (self.repo / "to-do-lists").mkdir()
        (self.repo / "src").mkdir()
        (self.repo / "to-do-lists" / "dmitri.md").write_text("queue\n")
        (self.repo / "src" / "a.py").write_text("VALUE = 1\n")
        self._git("add", "-A")
        self._git("commit", "-m", "init")

    def tearDown(self):
        self._tmp.cleanup()

    def _git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), *args],
                              capture_output=True, text=True, check=True).stdout

    def _branch(self, name):
        self._git("checkout", "-b", name, "main")

    def test_clean_branch_holds_only_housekeeping(self):
        """A branch that changed only a to-do file is CLEAN — the pile's most common case."""
        self._branch("drafts/tick-clean")
        (self.repo / "to-do-lists" / "dmitri.md").write_text("queue\nmore\n")
        self._git("add", "-A")
        self._git("commit", "-m", "chore")

        rec = rg.classify_branch(self.repo, "main", "drafts/tick-clean")
        self.assertEqual(rec["state"], "CLEAN")
        self.assertEqual(rec["relevant"], [])
        self.assertEqual([e["path"] for e in rec["ignored"]], ["to-do-lists/dmitri.md"])

    def test_holding_branch_lists_the_differing_path(self):
        """A branch that changed real content is HOLDING and names the path."""
        self._branch("drafts/tick-hold")
        (self.repo / "src" / "a.py").write_text("VALUE = 2\n")
        self._git("add", "-A")
        self._git("commit", "-m", "work")

        rec = rg.classify_branch(self.repo, "main", "drafts/tick-hold")
        self.assertEqual(rec["state"], "HOLDING")
        self.assertEqual(rec["relevant"], [{"status": "M", "path": "src/a.py"}])
        self.assertEqual(rec["ahead"], 1)

    def test_added_file_is_detected_as_holding(self):
        """A branch adding a file main lacks must be HOLDING with status A."""
        self._branch("drafts/tick-new")
        (self.repo / "src" / "b.py").write_text("NEW = True\n")
        self._git("add", "-A")
        self._git("commit", "-m", "add")

        rec = rg.classify_branch(self.repo, "main", "drafts/tick-new")
        self.assertEqual(rec["state"], "HOLDING")
        self.assertEqual(rec["relevant"], [{"status": "A", "path": "src/b.py"}])

    def test_no_branches_is_a_clear_gate(self):
        report = rg.build_report(self.repo)
        self.assertEqual(report["summary"]["total"], 0)

    def test_cli_reports_json_and_gates_on_holding(self):
        """End-to-end: the CLI emits parseable JSON and exits 2 under --fail-on-holding."""
        self._branch("drafts/tick-clean")
        (self.repo / "to-do-lists" / "dmitri.md").write_text("x\n")
        self._git("add", "-A")
        self._git("commit", "-m", "chore")
        self._branch("drafts/tick-hold")
        (self.repo / "src" / "a.py").write_text("VALUE = 3\n")
        self._git("add", "-A")
        self._git("commit", "-m", "work")

        out = self.repo / "report.json"
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "review_gate_report.py"),
             "--repo", str(self.repo), "--json", str(out), "--fail-on-holding"],
            capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 2, proc.stderr)
        data = json.loads(out.read_text())
        self.assertEqual(data["summary"]["total"], 2)
        self.assertEqual(data["summary"]["clean"], 1)
        self.assertEqual(data["summary"]["holding"], 1)
        self.assertEqual(data["summary"]["distinct_holding_paths"], ["src/a.py"])
        self.assertIn("drafts/tick-hold", data["summary"]["holding_branches"])
        self.assertIn("drafts/tick-clean", data["summary"]["clean_branches"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
