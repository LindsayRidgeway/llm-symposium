"""Offline regression checks for numeric attempt history after orchestration exceptions."""
import argparse
import importlib.util
import importlib.machinery
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

parser = argparse.ArgumentParser()
parser.add_argument("--runner", type=Path, required=True)
args, rest = parser.parse_known_args()
loader = importlib.machinery.SourceFileLoader("attempt_history_runner", str(args.runner))
spec = importlib.util.spec_from_loader(loader.name, loader)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

class AttemptHistoryTests(unittest.TestCase):
    def execute(self, mode):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); repo = root / "repo"; repo.mkdir()
            artifacts = root / "artifacts"
            instructions = root / "instructions.md"; instructions.write_text("ordinary fixture")
            class Guard:
                def sanitized_environment(self): return {}
                def scan_run(self, *a, **k): return {"ok": True}
            calls = []
            def worker(argv, repo, log, timeout):
                calls.append("worker")
                log.write_text("ordinary public worker text")
                if mode == "worker": raise ValueError("ordinary public exception detail")
                return 0
            def head(*a, **k):
                if mode == "head": raise ValueError("ordinary public exception detail")
                return "base\n"
            def checker(*a, **k):
                number = len([x for x in calls if x == "checker"]) + 1
                calls.append("checker")
                if mode != "second_checker" or number == 2:
                    raise subprocess.TimeoutExpired("ordinary checker", 30)
                (artifacts / "attempt-1" / "mission-check.json").write_text('{"ok":false,"detail":"ordinary public report detail"}')
                return subprocess.CompletedProcess([], 1, "", "")
            with mock.patch.object(runner, "load_secret_guard", return_value=Guard()), mock.patch.object(runner, "worker_call", side_effect=worker), mock.patch.object(runner.subprocess, "check_output", side_effect=head), mock.patch.object(runner.subprocess, "run", side_effect=checker), mock.patch.object(runner, "repairable", return_value=True):
                result = runner.run(repo, instructions, root / "mission.json", root / "checker.py", "base", artifacts, worker=["never-executed"])
            self.assertEqual(result, json.loads((artifacts / "orchestration.json").read_text()))
            self.assertFalse(result["ok"])
            self.assertTrue(result["final_secret_guard"]["ok"])
            self.assertNotIn("ordinary public exception detail", json.dumps(result))
            self.assertNotIn("ordinary public report detail", json.dumps(result))
            return result, calls

    def test_first_checker_exception_keeps_completed_worker(self):
        r, calls = self.execute("checker")
        self.assertEqual(len(r["attempts"]), 1)
        self.assertEqual(r["attempts"][0], {"number": 1, "max_turns": 25, "worker_exit": 0, "checker_exit": None})

    def test_second_checker_exception_keeps_both_attempts(self):
        r, calls = self.execute("second_checker")
        self.assertEqual(r["attempts"], [
            {"number": 1, "max_turns": 25, "worker_exit": 0, "checker_exit": 1},
            {"number": 2, "max_turns": 15, "worker_exit": 0, "checker_exit": None}])
        self.assertEqual(calls.count("worker"), 2)

    def test_worker_exception_keeps_started_attempt_with_unknown_exit(self):
        r, calls = self.execute("worker")
        self.assertEqual(r["attempts"], [{"number": 1, "max_turns": 25, "worker_exit": None, "checker_exit": None}])

    def test_head_lookup_exception_keeps_known_worker_exit(self):
        r, calls = self.execute("head")
        self.assertEqual(r["attempts"], [{"number": 1, "max_turns": 25, "worker_exit": 0, "checker_exit": None}])
        self.assertNotIn("checker", calls)

if __name__ == "__main__":
    unittest.main(argv=["attempt-history-tests", *rest])
