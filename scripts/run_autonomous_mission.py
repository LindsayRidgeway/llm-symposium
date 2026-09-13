#!/usr/bin/env python3
"""Run one mission, returning independent validation feedback at most once.

Two fresh Goose calls share a checkout, not a hidden conversation. Total allowance
is 25 + 15 turns and 240 + 240 seconds. No retry after a process/provider error,
missing draft, forbidden diff or changed HEAD. A passing contract is NOT peer review.
Copy this file, checker and mission outside the checkout BEFORE starting the worker.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

TURN_BUDGETS = (25, 15)
SECONDS_PER_ATTEMPT = 240


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def worker_call(argv: list[str], repo: Path, log: Path, timeout: int) -> int:
    with log.open("w", encoding="utf-8") as stream:
        process = subprocess.Popen(argv, cwd=repo, stdout=stream,
                                   stderr=subprocess.STDOUT, start_new_session=True)
        try:
            return process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            return 124


def repairable(report: dict, log: Path) -> bool:
    errors = report.get("errors", [])
    if report.get("ok") or not errors or report.get("word_count", 0) == 0:
        return False
    # Conservative fail-closed stop if a provider limit appears anywhere in output.
    # This may skip a valid repair if the document quotes an error; it cannot cause
    # extra API attempts. Full provider-error taxonomy is not claimed here.
    lower = log.read_text(encoding="utf-8", errors="replace").lower()
    if any(s in lower for s in ("insufficient_quota", "rate_limit_exceeded",
                               "usage limit has been reached", "rate limit exceeded")):
        return False
    prefixes = ("artifact has ", "missing metadata:", "missing title ",
                "git diff --check failed")
    return all(isinstance(e, str) and e.startswith(prefixes) for e in errors)


def run(repo: Path, instructions: Path, mission: Path, checker: Path, base: str,
        artifacts: Path, worker: list[str] | None = None,
        timeout: int = SECONDS_PER_ATTEMPT) -> dict:
    artifacts.mkdir(parents=True, exist_ok=True)
    current = instructions
    attempts = []
    outcome = {"ok": False, "attempts": attempts,
               "quality": "mechanical contract only; peer review still required"}
    for index, turns in enumerate(TURN_BUDGETS, start=1):
        attempt_dir = artifacts / f"attempt-{index}"
        attempt_dir.mkdir()
        log = attempt_dir / "worker.jsonl"
        argv = (worker or ["goose"]) + [
            "run", "--with-builtin", "developer", "--instructions", str(current),
            "--max-turns", str(turns), "--output-format", "stream-json"]
        try:
            code = worker_call(argv, repo, log, timeout)
        except OSError as exc:
            code = 127
            log.write_text(str(exc), encoding="utf-8")
        attempt = {"number": index, "max_turns": turns, "worker_exit": code}
        attempts.append(attempt)
        head = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
        if head != base:
            outcome["reason"] = "worker changed HEAD; stopping without repair"
            break
        # Do not give billing credentials to the deterministic checker.
        env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
        checked = subprocess.run([
            sys.executable, str(checker), "--repo", str(repo), "--mission", str(mission),
            "--base", base, "--artifacts", str(attempt_dir)
        ], capture_output=True, text=True, env=env, timeout=30)
        (attempt_dir / "checker-output.txt").write_text(checked.stdout + checked.stderr, encoding="utf-8")
        report_path = attempt_dir / "mission-check.json"
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            outcome["reason"] = "checker produced no valid report"
            break
        attempt["checker_exit"] = checked.returncode
        attempt["check"] = report
        if code != 0:
            outcome["reason"] = "worker process failed; no automatic provider/process retry"
            break
        if checked.returncode == 0 and report.get("ok"):
            outcome["ok"] = True
            outcome["reason"] = "mission contract passed"
            break
        if index == len(TURN_BUDGETS) or not repairable(report, log):
            outcome["reason"] = "repair exhausted or failure not eligible for repair"
            break
        # Keep the first report/draft immutable; second checker gets its own folder.
        current = artifacts / "repair-instructions.md"
        current.write_text(
            instructions.read_text(encoding="utf-8") +
            "\n\n## Independent checker feedback — one remaining correction pass\n" +
            "The previous attempt has NOT completed the mission. The draft is in the checkout. "
            "Read it and its source, then correct the specific failures below. Do not pad text, "
            "invent evidence, lower requirements or modify the checker. If too short, deepen "
            "passage-specific analysis and concrete replacements. Use the file tools to update "
            "to-do-lists/tarik.md; a session todo tool does not write that repository file. "
            "There is no further retry after this pass.\n\n" +
            json.dumps(report, indent=2) + "\n", encoding="utf-8")
    write_json(artifacts / "orchestration.json", outcome)
    return outcome


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", default=".")
    p.add_argument("--instructions", required=True)
    p.add_argument("--mission", required=True)
    p.add_argument("--checker", required=True)
    p.add_argument("--base", required=True)
    p.add_argument("--artifacts", required=True)
    a = p.parse_args()
    result = run(Path(a.repo).resolve(), Path(a.instructions).resolve(),
                 Path(a.mission).resolve(), Path(a.checker).resolve(), a.base,
                 Path(a.artifacts).resolve())
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
