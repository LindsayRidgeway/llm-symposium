#!/usr/bin/env python3
"""Verify inert RT4 snapshots and reproduce only the eight stubbed orchestration checks.
No network, real guard/probe, credential lookup, provider, or deployment is used.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = Path(__file__).with_name("review-bundle")

def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def main():
    manifest = json.loads((BUNDLE / "manifest.json").read_text())
    for entry in manifest["files"]:
        data = (BUNDLE / entry["path"]).read_bytes()
        if len(data) != entry["bytes"] or blob(data) != entry["git_blob"]:
            raise ValueError("snapshot mismatch: " + entry["path"])
    contract = manifest["test_contract"]
    tests = ROOT / contract["path"]
    if blob(tests.read_bytes()) != contract["git_blob"]:
        raise ValueError("test contract differs from the reviewed source")
    results = []
    with tempfile.TemporaryDirectory(prefix="rt4-review-bundle-") as folder:
        scratch = Path(folder)
        for version in ("original", "repaired"):
            runner = scratch / (version + "_runner.py")
            runner.write_bytes((BUNDLE / version / "run_autonomous_mission.py.txt").read_bytes())
            checked = subprocess.run(
                [sys.executable, "-I", str(tests), "--runner", str(runner)],
                cwd=scratch, capture_output=True, text=True, timeout=30)
            output = checked.stdout + checked.stderr
            count = re.search(r"Ran (\d+) tests? in", output)
            failed = re.search(r"FAILED \(([^)]+)\)", output)
            counts = dict(re.findall(r"(failures|errors)=(\d+)", failed.group(1))) if failed else {}
            actual = {"tests": int(count.group(1)) if count else None,
                      "failures": int(counts.get("failures", 0)),
                      "errors": int(counts.get("errors", 0)),
                      "exit": checked.returncode}
            if actual != manifest["expected"][version] or (version == "repaired" and not re.search(r"^OK$", output, re.M)):
                raise ValueError("unexpected regression result: " + version + " " + json.dumps(actual))
            results.append({"version": version, **actual})
    print(json.dumps({"snapshot_hashes_verified": len(manifest["files"]),
                      "test_contract_hash_verified": True,
                      "results": results,
                      "scope": "stubbed orchestration only; no real guard or probe"}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
