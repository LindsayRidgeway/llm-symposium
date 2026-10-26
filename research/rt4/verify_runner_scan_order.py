"""Offline RT4 control-flow check: no guard implementation, environment access, worker, checker or provider executes."""
from pathlib import Path
import importlib.util
import argparse
import hashlib
import json
import subprocess
import tempfile
from unittest import mock

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--runner", type=Path, required=True)
args = parser.parse_args()
raw = args.runner.read_bytes()
assert hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == "07a0c5894060e3554a8b403eb95dc5ac85e9c2ae", "expected exact reconstructed RT4 runner blob"
spec = importlib.util.spec_from_file_location("rt4_reconstructed_runner", args.runner)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

def case(name):
    events = []
    class StubGuard:
        def sanitized_environment(self):
            events.append("sanitized_stub")
            return {}
        def scan_run(self, *args, **kwargs):
            events.append("scan_stub")
            return {"ok": True}
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        repo = root / "repo"
        repo.mkdir()
        artifacts = root / "artifacts"
        instructions = root / "instructions.md"
        instructions.write_text("public ordinary-text fixture\n")
        def worker(argv, repo, log, timeout):
            events.append("worker_stub")
            log.write_text("public ordinary-text fixture\n")
            return 0
        def checker(*args, **kwargs):
            events.append("checker_stub")
            if name == "checker_timeout":
                raise subprocess.TimeoutExpired("stub-checker", 30)
            (artifacts / "attempt-1" / "mission-check.json").write_text('{"ok": true}')
            return subprocess.CompletedProcess([], 0, "", "")
        with mock.patch.object(runner, "load_secret_guard", return_value=StubGuard()), mock.patch.object(runner, "worker_call", side_effect=worker), mock.patch.object(runner.subprocess, "check_output", return_value="different-head\n" if name == "head_changed" else "base\n"), mock.patch.object(runner.subprocess, "run", side_effect=checker):
            try:
                result = runner.run(repo, instructions, root / "mission.json", root / "checker.py", "base", artifacts, worker=["never-executed"])
                outcome = result["reason"]
            except subprocess.TimeoutExpired:
                outcome = "TimeoutExpired propagated"
        return {"case": name, "events": events, "scan_calls": events.count("scan_stub"), "outcome": outcome}
results = [case(name) for name in ("normal", "head_changed", "checker_timeout")]
assert [r["scan_calls"] for r in results] == [1, 0, 0]
print(json.dumps(results, indent=2))
