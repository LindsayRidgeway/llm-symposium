#!/usr/bin/env python3
"""How many actions does a wake spend before it writes anything into the checkout?

The wake instructions have carried this complaint since 2026-10-12: "most of their
actions went on reconnaissance, which is why five consecutive wakes screened the same
condition and none delivered a write-up", and "a partial artefact on disk survives
being cut off; a half-finished investigation does not". It had never been measured on
this machine's own runs. This measures it.

For every run under a `tick-state/runs` directory it reads the goose transcript
(`worker.jsonl`, gzipped for older runs) and the run's `result.json`, and reports:

  actions          distinct tool calls, in order
  first_repo_write the 1-based position of the first call that writes a file *inside
                   the checkout* — goose's write/edit tool, a shell redirection, tee,
                   cp/mv, or git apply, with relative targets resolved against the
                   `cd` that the command itself performs
  recon_before     how many actions came before that write
  cut_off          whether the runner marked the run as cut off (result.json)

Writes that land outside the checkout are counted separately: the run's own
report.txt (position 1 in most wakes, because the rule says to write it first) and a
scratch tree in /tmp. A wake can write its report at action 1 and still spend thirty
actions before touching the repository, and that is the shape this counts.

Read-only by construction: it opens transcripts and never touches them.

Usage:
    python3 scripts/wake_reconnaissance_census.py                     # this machine's dmitri runs
    python3 scripts/wake_reconnaissance_census.py --root DIR          # any tick-state/runs directory
    python3 scripts/wake_reconnaissance_census.py --json
    python3 scripts/wake_reconnaissance_census.py --limit 20          # newest N runs only
    python3 scripts/wake_reconnaissance_census.py --since 20261020    # runs whose id starts with this
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import re
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

DEFAULT_ROOT = Path.home() / "LLM" / "dmitri-bot" / "tick-state" / "runs"

CAP_MARKER = "maximum number of actions I can do without user input"

DIRECT_WRITE_TOOLS = {"write", "edit", "file_write", "file_edit"}

# Redirection targets that are not files at all.
_DEAD_TARGETS = {"/dev/null", "/dev/stdout", "/dev/stderr", "/dev/tty"}

_REDIRECT = re.compile(r"(?<![0-9&])>{1,2}\s*([^\s|&;>)]+)")
_QUOTED = re.compile(r"'[^'\n]*'|\"[^\"\n]*\"")
_LEADING_CD = re.compile(r"^\s*cd\s+([^\s;&|]+)")


# --- shell parsing ----------------------------------------------------------


def strip_quoted(command: str) -> str:
    """Drop '...' and "..." spans so a `>` inside a printed string is not a write.

    A real write puts its target outside the quotes (`printf 'x' > report.txt`), so
    this keeps the writes and loses only the prose.
    """
    return _QUOTED.sub(" ", command)


def command_cwd(command: str, default: Path) -> Path:
    """The directory a command runs in: its own leading `cd`, else the workspace."""
    match = _LEADING_CD.match(command)
    if not match:
        return default
    target = match.group(1).strip("'\"")
    if target.startswith("~"):
        target = os.path.expanduser(target)
    if not target.startswith("/"):
        return (default / target).resolve() if default else default
    return Path(target)


def resolve(target: str, cwd: Path) -> Optional[Path]:
    target = target.strip().strip("'\"")
    if not target or target in _DEAD_TARGETS:
        return None
    if target.startswith("~"):
        return Path(os.path.expanduser(target))
    if target.startswith("/"):
        return Path(target)
    if target.startswith("$") or target.startswith("`"):
        return None  # a variable we cannot resolve here
    if cwd is None:
        return None
    return cwd / target


def shell_write_targets(command: str, cwd: Path) -> List[Path]:
    """Every path a shell command appears to write, resolved against its own cwd."""
    bare = strip_quoted(command)
    targets: List[Path] = []

    for match in _REDIRECT.finditer(bare):
        resolved = resolve(match.group(1), cwd)
        if resolved is not None:
            targets.append(resolved)

    # Verbs whose last argument is the thing being written.
    for verb in (r"\btee\s+(-a\s+)?", r"\bcp\s+(?:-[a-zA-Z]+\s+)*", r"\bmv\s+(?:-[a-zA-Z]+\s+)*"):
        for match in re.finditer(verb, bare):
            rest = bare[match.end():].split("&&")[0].split(";")[0].split("|")[0]
            tokens = [t for t in rest.split() if not t.startswith("-")]
            if tokens:
                resolved = resolve(tokens[-1], cwd)
                if resolved is not None:
                    targets.append(resolved)

    if re.search(r"\bgit\s+apply\b|\bpatch\s+-p\d", bare):
        targets.append(cwd)  # the patch lands in the checkout the command is in

    if re.search(r"\bopen\([^)]*['\"]w", bare) or ".write_text(" in bare:
        targets.append(cwd)

    return targets


def action_targets(name: str, arguments: Dict[str, Any], cwd: Path) -> List[Path]:
    """Paths this action writes, or an empty list if it writes nothing."""
    if name in DIRECT_WRITE_TOOLS:
        raw = arguments.get("path") or arguments.get("file_path") or ""
        resolved = resolve(str(raw), cwd)
        return [resolved] if resolved is not None else []
    if name == "shell":
        return shell_write_targets(str(arguments.get("command") or ""), cwd)
    return []


def classify(paths: Iterable[Path], workspace: Path) -> Optional[str]:
    """'repo', 'state' (the run's own report and scratch), or 'elsewhere'."""
    workspace = workspace.resolve()
    run_dir = workspace.parent
    kinds = set()
    for path in paths:
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path
        if resolved == workspace or workspace in resolved.parents:
            kinds.add("repo")
        elif run_dir in resolved.parents or resolved == run_dir:
            kinds.add("state")
        else:
            kinds.add("elsewhere")
    if "repo" in kinds:
        return "repo"
    if "state" in kinds:
        return "state"
    if "elsewhere" in kinds:
        return "elsewhere"
    return None


# --- reading a transcript ---------------------------------------------------


def open_transcript(run_dir: Path):
    plain = run_dir / "worker.jsonl"
    if plain.is_file():
        return plain.open("r", encoding="utf-8", errors="replace")
    packed = run_dir / "worker.jsonl.gz"
    if packed.is_file():
        return gzip.open(packed, "rt", encoding="utf-8", errors="replace")
    return None


def tool_calls(handle) -> List[Dict[str, Any]]:
    """Distinct tool calls in the order they were first requested.

    goose streams token by token into this file, so one logical message appears many
    times with a growing body. Calls are keyed by request id and the longest version
    of each is kept.
    """
    seen: Dict[str, Dict[str, Any]] = {}
    order: List[str] = []
    for line in handle:
        line = line.strip()
        if not line.startswith("{"):
            continue  # the human-readable session banner
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        for part in (row.get("message") or {}).get("content") or []:
            if part.get("type") != "toolRequest":
                continue
            call = (part.get("toolCall") or {}).get("value") or {}
            name = call.get("name") or "?"
            arguments = json.dumps(call.get("arguments") or {}, sort_keys=True)
            key = part.get("id") or f"{name}:{len(order)}"
            if key not in seen:
                order.append(key)
                seen[key] = {"name": name, "arguments": arguments}
            elif len(arguments) > len(seen[key]["arguments"]):
                seen[key] = {"name": name, "arguments": arguments}
    return [seen[key] for key in order]


def read_result(run_dir: Path) -> Dict[str, Any]:
    path = run_dir / "result.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return {}


def census_run(run_dir: Path) -> Optional[Dict[str, Any]]:
    handle = open_transcript(run_dir)
    if handle is None:
        return None
    result = read_result(run_dir)
    workspace = Path(result.get("workspace") or (run_dir / "repo"))
    default_cwd = workspace
    with handle:
        calls = tool_calls(handle)

    first_any = first_repo = first_elsewhere = None
    for index, call in enumerate(calls, start=1):
        arguments = json.loads(call["arguments"])
        cwd = (
            command_cwd(str(arguments.get("command") or ""), default_cwd)
            if call["name"] == "shell"
            else default_cwd
        )
        kind = classify(action_targets(call["name"], arguments, cwd), workspace)
        if kind is None:
            continue
        if first_any is None:
            first_any = index
        if kind == "repo" and first_repo is None:
            first_repo = index
        if kind == "elsewhere" and first_elsewhere is None:
            first_elsewhere = index

    report = run_dir / "report.txt"
    changed = result.get("changed_paths") or []
    return {
        "run": run_dir.name,
        "actions": len(calls),
        "first_any_write": first_any,
        "first_repo_write": first_repo,
        "first_scratch_write": first_elsewhere,
        "recon_before_repo": None if first_repo is None else first_repo - 1,
        "cut_off": bool(result.get("cut_off")),
        "status": result.get("status"),
        "changed_paths": len(changed),
        "report_bytes": report.stat().st_size if report.is_file() else 0,
    }


def census_runs(root: Path, limit: Optional[int] = None,
                since: Optional[str] = None) -> List[Dict[str, Any]]:
    if not root.is_dir():
        return []
    rows = []
    for run_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        if since and not run_dir.name.startswith(since):
            continue
        row = census_run(run_dir)
        if row is not None:
            rows.append(row)
    rows.sort(key=lambda r: r["run"])
    if limit is not None:
        rows = rows[-limit:]
    return rows


# --- the summary a report can quote -----------------------------------------


def summarize(rows: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    rows = list(rows)
    wrote = [r for r in rows if r["first_repo_write"] is not None]
    recon = [r["recon_before_repo"] for r in wrote]
    capped = [r for r in rows if r["cut_off"]]
    capped_no_write = [r for r in capped if r["first_repo_write"] is None]
    silent_after_20 = [r for r in rows if (r["recon_before_repo"] or 0) >= 20]
    transcribed = [r for r in rows if r["actions"]]
    return {
        "runs_read": len(rows),
        "runs_with_repo_write": len(wrote),
        "runs_without_repo_write": len(rows) - len(wrote),
        "runs_cut_off": len(capped),
        "cut_off_without_repo_write": len(capped_no_write),
        "median_recon_before_repo": statistics.median(recon) if recon else None,
        "mean_recon_before_repo": round(statistics.mean(recon), 1) if recon else None,
        "max_recon_before_repo": max(recon) if recon else None,
        "runs_20_plus_actions_before_repo_write": len(silent_after_20),
        "median_actions": statistics.median([r["actions"] for r in transcribed])
        if transcribed else None,
        "never_wrote_report": sum(1 for r in rows if r["report_bytes"] == 0),
    }


def render(summary: Dict[str, Any]) -> str:
    def show(key: str, label: str) -> str:
        return f"  {label:<42} {summary[key]}"

    return "\n".join(
        [
            f"runs read: {summary['runs_read']}",
            show("runs_with_repo_write", "wrote something into the checkout"),
            show("runs_without_repo_write", "wrote nothing into the checkout"),
            show("runs_cut_off", "cut off by the runner"),
            show("cut_off_without_repo_write", "cut off having written nothing there"),
            show("median_actions", "median actions per run"),
            "actions before the first write into the checkout:",
            show("median_recon_before_repo", "  median"),
            show("mean_recon_before_repo", "  mean"),
            show("max_recon_before_repo", "  max"),
            show("runs_20_plus_actions_before_repo_write", "  20 or more actions first"),
            show("never_wrote_report", "left no report.txt at all"),
        ]
    )


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="a tick-state/runs directory")
    parser.add_argument("--json", action="store_true", help="print per-run rows")
    parser.add_argument("--limit", type=int, default=None, help="only the newest N runs")
    parser.add_argument("--since", default=None, help="only run ids starting with this date")
    args = parser.parse_args(argv)

    root = Path(os.path.expanduser(args.root))
    if not root.is_dir():
        print(f"no such runs directory: {root}", file=sys.stderr)
        return 2
    rows = census_runs(root, limit=args.limit, since=args.since)
    if not rows:
        print(f"no worker.jsonl transcripts under {root}", file=sys.stderr)
        return 1
    if args.json:
        for row in rows:
            print(json.dumps(row, sort_keys=True))
    else:
        print(render(summarize(rows)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
