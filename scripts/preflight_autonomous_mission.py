#!/usr/bin/env python3
"""Decide whether a queued mission warrants starting a paid worker.

Retirement is explicit, backed by a committed completion artifact. An existing
required output also prevents duplicate generation, but is NOT treated as proof
of review/acceptance. Invalid or inconsistent state fails before model startup.
Uses repository files and git only; this is not a Goose recipe schema.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
import subprocess

from check_autonomous_mission import read_contract, safe_file


def field(text: str, name: str, required: bool = False) -> str | None:
    values = re.findall(rf"^\*\*{re.escape(name)}:\*\* ([^\n]+)$", text, re.M)
    if not values and not required:
        return None
    if len(values) != 1:
        raise ValueError(f"mission needs exactly one {name} field")
    return values[0].strip()


def committed(repo: Path, name: str) -> bool:
    return bool(subprocess.check_output(
        ["git", "-C", str(repo), "ls-tree", "--name-only", "HEAD", "--", name],
        text=True, stderr=subprocess.PIPE).strip())


def decide(repo: Path, mission_path: str) -> dict:
    mission = safe_file(repo, mission_path)
    text = mission.read_text(encoding="utf-8")
    state = field(text, "State") or "active"  # legacy mission files remain valid
    if state not in ("active", "retired"):
        raise ValueError("State must be active or retired")
    target, _ = read_contract(mission)
    output = safe_file(repo, target)
    if state == "retired":
        raw = field(text, "Completion artifact", required=True)
        match = re.fullmatch(r"`([^`]+)`", raw)
        if not match:
            raise ValueError("Completion artifact must be one backtick-quoted path")
        name = match[1]
        completion = safe_file(repo, name)
        if not completion.is_file() or not committed(repo, name):
            raise ValueError("retired mission's completion artifact must exist and be committed")
        return {"run_worker": False, "state": "retired", "completion": name,
                "reason": "explicitly retired; no model work requested"}
    if output.exists():
        if not output.is_file() or not committed(repo, target):
            raise ValueError("required output exists but is not a committed regular file")
        return {"run_worker": False, "state": "already_present", "target": target,
                "reason": "output already committed; acceptance must be checked separately"}
    return {"run_worker": True, "state": "ready", "target": target,
            "reason": "active mission with absent output"}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", default=".")
    p.add_argument("--mission", required=True)
    p.add_argument("--report", required=True)
    p.add_argument("--github-output")
    args = p.parse_args()
    try:
        report = decide(Path(args.repo).resolve(), args.mission)
        code = 0
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        report = {"run_worker": False, "state": "invalid", "reason": str(exc)}
        code = 1
    path = Path(args.report)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.github_output:
        with Path(args.github_output).open("a", encoding="utf-8") as f:
            f.write(f"run_worker={str(report['run_worker']).lower()}\n")
            f.write(f"state={report['state']}\n")
    print(json.dumps(report, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
