"""Offline finalization regression checks; all guards, workers and subprocesses are stubs."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

parser = argparse.ArgumentParser()
parser.add_argument("--runner", type=Path, required=True)
args, rest = parser.parse_known_args()
spec = importlib.util.spec_from_file_location("rt4_runner_under_test", args.runner)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

class FinalizationTests(unittest.TestCase):
    def execute(self, mode):
        events = []
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = root / "repo"
            repo.mkdir()
            artifacts = root / "artifacts"
            instructions = root / "instructions.md"
            instructions.write_text("ordinary public fixture\n")
            class StubGuard:
                def sanitized_environment(self):
                    return {}
                def scan_run(self, repo, target, base, redact):
                    final = target == artifacts
                    events.append("root_scan" if final else "attempt_scan")
                    if final and mode == "scan_raises":
                        raise ValueError("ordinary fixture exception")
                    if final and mode == "scan_invalid":
                        return []
                    return {"ok": not (final and mode == "scan_blocks")}
            def load():
                if mode == "load_fails":
                    raise RuntimeError("ordinary fixture exception")
                return StubGuard()
            def worker(argv, repo, log, timeout):
                events.append("worker")
                log.write_text("ordinary public fixture\n")
                if mode == "worker_raises":
                    raise ValueError("ordinary fixture exception")
                return 0
            def checker(*a, **kw):
                events.append("checker")
                if mode == "checker_timeout":
                    raise subprocess.TimeoutExpired("stub", 30)
                (artifacts / "attempt-1" / "mission-check.json").write_text('{"ok":true}')
                return subprocess.CompletedProcess([], 0, "", "")
            with mock.patch.object(runner, "load_secret_guard", side_effect=load), mock.patch.object(runner, "worker_call", side_effect=worker), mock.patch.object(runner.subprocess, "check_output", return_value="changed\n" if mode == "head_changed" else "base\n"), mock.patch.object(runner.subprocess, "run", side_effect=checker):
                result = runner.run(repo, instructions, root / "mission.json", root / "checker.py", "base", artifacts, worker=["never-executed"])
            saved = json.loads((artifacts / "orchestration.json").read_text())
            self.assertEqual(result, saved)
            return result, events

    def test_normal_scans_root_and_preserves_success(self):
        r, events = self.execute("normal")
        self.assertTrue(r["ok"])
        self.assertEqual(events.count("root_scan"), 1)
        self.assertTrue(r["final_secret_guard"]["ok"])

    def test_changed_head_still_scans_root(self):
        r, events = self.execute("head_changed")
        self.assertFalse(r["ok"])
        self.assertIn("changed HEAD", r["reason"])
        self.assertEqual(events.count("root_scan"), 1)
        self.assertNotIn("checker", events)

    def test_checker_timeout_still_scans_root(self):
        r, events = self.execute("checker_timeout")
        self.assertFalse(r["ok"])
        self.assertIn("TimeoutExpired", r["reason"])
        self.assertEqual(events.count("root_scan"), 1)
        self.assertEqual(events.count("worker"), 1)

    def test_worker_exception_still_scans_root(self):
        r, events = self.execute("worker_raises")
        self.assertFalse(r["ok"])
        self.assertIn("ValueError", r["reason"])
        self.assertEqual(events.count("root_scan"), 1)

    def test_final_scan_block_overrides_success(self):
        r, events = self.execute("scan_blocks")
        self.assertFalse(r["ok"])
        self.assertFalse(r["final_secret_guard"]["ok"])
        self.assertIn("final", r["reason"])

    def test_final_scan_exception_fails_closed(self):
        r, events = self.execute("scan_raises")
        self.assertFalse(r["ok"])
        self.assertFalse(r["final_secret_guard"]["ok"])
        self.assertIn("ValueError", r["final_secret_guard"]["error"])

    def test_invalid_final_report_fails_closed(self):
        r, events = self.execute("scan_invalid")
        self.assertFalse(r["ok"])
        self.assertFalse(r["final_secret_guard"]["ok"])

    def test_missing_guard_fails_closed_without_worker(self):
        r, events = self.execute("load_fails")
        self.assertFalse(r["ok"])
        self.assertFalse(r["final_secret_guard"]["ok"])
        self.assertNotIn("worker", events)

if __name__ == "__main__":
    unittest.main(argv=["finalization-tests", *rest])
