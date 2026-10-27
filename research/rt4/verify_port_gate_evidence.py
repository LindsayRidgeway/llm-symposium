#!/usr/bin/env python3
"""Verify the RT4 gate-evidence candidate without executing any tests or guard."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
def main():
    manifest = json.loads(Path(__file__).with_name("port-gate-evidence.json").read_text())
    cases = 0
    workflow = None
    for entry in manifest["sources"] + manifest["contracts"]:
        name = entry.get("snapshot", entry.get("path"))
        data = (ROOT / name).read_bytes()
        if blob(data) != entry["git_blob"]:
            raise ValueError("source mismatch: " + name)
        if name.endswith(".txt") and entry.get("target", "").endswith(".yml"):
            workflow = data.decode()
        elif entry.get("target", name).endswith(".py"):
            tree = ast.parse(data, filename=name)
            compile(tree, name, "exec")
            if "cases" in entry:
                count = sum(isinstance(n, ast.FunctionDef) and n.name.startswith("test_") for n in ast.walk(tree))
                if count != entry["cases"]:
                    raise ValueError("test inventory mismatch: " + name)
                cases += count
    if workflow is None or workflow.split("jobs:", 1)[0] != manifest["trigger_prefix"]:
        raise ValueError("workflow trigger changed")
    if not all(command in workflow for command in manifest["commands"]):
        raise ValueError("gate command missing")
    print(json.dumps({"source_hashes_verified": len(manifest["sources"]) + len(manifest["contracts"]),
                      "cases_in_ast_inventory": cases,
                      "workflow_trigger_unchanged": True,
                      "registered_commands": len(manifest["commands"]),
                      "tests_executed": 0, "workflow_dispatched": False}, indent=2))
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
