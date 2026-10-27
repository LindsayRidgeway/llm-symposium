#!/usr/bin/env python3
"""Reconstruct and test an unmerged RT4 port offline; guard execution is stubbed."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def main():
    manifest = json.loads(Path(__file__).with_name("port-candidate.json").read_text())
    files = {}
    for entry in manifest["sources"]:
        data = (ROOT / entry["snapshot"]).read_bytes()
        if blob(data) != entry["git_blob"] or len(data) != entry["bytes"]:
            raise ValueError("source mismatch: " + entry["target"])
        files[entry["target"]] = data
    for entry in manifest["dependencies"]:
        data = (ROOT / entry["path"]).read_bytes()
        if blob(data) != entry["git_blob"]:
            raise ValueError("dependency mismatch: " + entry["path"])
        files[entry["path"]] = data
    results = []
    with tempfile.TemporaryDirectory(prefix="rt4-port-candidate-") as folder:
        scratch = Path(folder)
        for name, data in files.items():
            path = scratch / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        commands = [
            [sys.executable, "-I", str(scratch / "tests/test_run_autonomous_mission.py")],
            [sys.executable, "-I", str(scratch / "research/rt4/test_runner_finalization.py"), "--runner", str(scratch / "scripts/run_autonomous_mission.py")],
            [sys.executable, "-I", str(scratch / "research/rt4/test_runner_attempt_history.py"), "--runner", str(scratch / "scripts/run_autonomous_mission.py")]]
        for command, expected in zip(commands, manifest["expected_tests"]):
            run = subprocess.run(command, cwd=scratch, capture_output=True, text=True, timeout=30)
            output = run.stdout + run.stderr
            count = re.search(r"Ran (\d+) tests? in", output)
            if run.returncode != 0 or not count or int(count.group(1)) != expected or not re.search(r"^OK$", output, re.M):
                raise ValueError("candidate test failed: " + Path(command[2]).name)
            results.append({"suite": Path(command[2]).name, "tests": expected, "exit": run.returncode})
    print(json.dumps({"source_hashes_verified": len(manifest["sources"]),
                      "dependency_hashes_verified": len(manifest["dependencies"]),
                      "results": results,
                      "scope": "local fake workers, real checker/Git, stub guard; no real guard/probe/provider"}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
