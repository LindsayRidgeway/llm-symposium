#!/usr/bin/env python3
"""Which of the commons' bodies are actually up, on the machine that runs them.

The commons retired its cloud schedules on 2026-09-25 and now runs as five `bot.py`
processes supervised by launchd on one Mac. Its dead-man switch (`quiet-check.yml`,
daily) sees only git history and mail: it reports a commons gone quiet *four days*
after the fact, and it **cannot** see one dead body while the other four keep
committing. Nothing reported the local layer — this file does.

For each amigo it checks three things a launchd-supervised body needs:

  1. a plist on disk (`~/Library/LaunchAgents/com.lindsay.amigo.<name>.plist`),
  2. a job loaded in `launchctl` *with a live pid that is really that body's process*,
  3. the credential lines in `bot.env` filled — key **names** only, never values — with any
     `${VAR}` indirection *resolved* the way `source` would, since a reference that expands
     to "" leaves the body running mute while its line still reads as filled.

Discovery is read from disk, deliberately: a body is a `*-bot/` directory under the
LLM home (or a matching plist), so a sixth amigo is covered the day its directory
appears. There is no roster here to forget. Dawn's LaunchAgent (`com.dawn.telegram`)
is out of scope: she is not an amigo, and her setup is not the commons' to inspect.

Usage:
    python3 scripts/bodies_status.py
    python3 scripts/bodies_status.py --json
    python3 scripts/bodies_status.py --llm-dir ~/LLM --plist-dir ~/Library/LaunchAgents

Exit 0 if every discovered body is up and credential-complete, 1 otherwise (or 2 if
the host has no `launchctl` at all, which is a fact about the host, not a dead body).
Offline and read-only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PLIST_NAME = re.compile(r"^com\.lindsay\.amigo\.([a-z0-9_-]+)\.plist$")
PROVIDER_KEY = re.compile(r"API_KEY")
ENV_LINE = re.compile(r'^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$')
SHELL_REF = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


# ---------------------------------------------------------------- pure parsers

def _env_pairs(text: str):
    """`(KEY, value)` in file order. Quotes stripped, comments and non-assignments skipped.

    Order is kept because `run.sh` reads `bot.env` with `source`, which is top-to-bottom:
    a value that references `${VAR}` sees VAR's value *as of that line*, never later.
    """
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            continue
        m = ENV_LINE.match(line)
        if not m:
            continue
        val = m.group(2).strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "'\"":
            val = val[1:-1]
        yield m.group(1), val


def parse_env(text: str) -> dict[str, str]:
    """`KEY=value` lines as a name->value map. Quotes are stripped; values are never printed."""
    return {k: v for k, v in _env_pairs(text)}


def resolve_env(text: str) -> dict[str, str]:
    """Values as `source bot.env` would set them: `${VAR}` expands to what VAR holds at that line.

    A reference to a name that is unset, misspelled, or defined *later* in the file expands to
    the empty string — the same thing the shell does — so a broken indirection shows up as "".
    """
    resolved: dict[str, str] = {}
    for k, v in _env_pairs(text):
        resolved[k] = SHELL_REF.sub(lambda m: resolved.get(m.group(1), ""), v)
    return resolved


def broken_references(text: str) -> list[str]:
    """Names whose value is a `${VAR}` reference that expands to nothing.

    These are the silent kills: the line *looks* filled, `parse_env` sees a non-empty string,
    but after `source` the variable is "", Goose reads it, and the body comes up mute while
    launchd — and an unresolved-value check — report it "up". Only real failures, so a
    reference that resolves to a value is not listed.
    """
    resolved: dict[str, str] = {}
    out: list[str] = []
    for k, raw in _env_pairs(text):
        val = SHELL_REF.sub(lambda m: resolved.get(m.group(1), ""), raw)
        if SHELL_REF.search(raw) and not val.strip():
            out.append(k)
        resolved[k] = val
    return out


def missing_env_keys(text: str, tag: str) -> list[str]:
    """The credential groups that are absent or empty for this amigo. Names only.

    Each entry is a *group*: filled if any acceptable key name is present and non-empty.
    The provider key is matched by shape (any `*API_KEY*`), not by name, so the check
    holds for Claude/Anthropic, Gemini/Google and Tarik/OpenAI as well as DeepSeek.

    Values are *resolved* to what `source` would produce (see `resolve_env`), and a value
    that is a `${VAR}` reference expanding to nothing is reported on its own — otherwise a
    broken indirection hides behind the other provider key name and the body reads as up.
    """
    env = resolve_env(text)
    groups = {
        "TELEGRAM_BOT_TOKEN": ["TELEGRAM_BOT_TOKEN"],
        "SYMPOSIUM_MAIL_USER": [f"SYMPOSIUM_MAIL_USER_{tag}"],
        "SYMPOSIUM_MAIL_APP_PASSWORD": [f"SYMPOSIUM_MAIL_APP_PASSWORD_{tag}"],
        "provider API key": [k for k in env if PROVIDER_KEY.search(k)],
    }
    missing = [name for name, names in groups.items()
               if not any(env.get(k, "").strip() for k in names)]
    missing += [f"unresolved key reference ({k})" for k in broken_references(text)]
    return missing


def parse_launchctl(text: str) -> dict[str, dict]:
    """`launchctl list` -> {label: {pid, status}}. pid is None when the job is not running."""
    jobs: dict[str, dict] = {}
    for line in text.splitlines():
        parts = [p for p in re.split(r"\t|\s{2,}", line.strip()) if p]
        if len(parts) < 3 or parts[0] == "PID":
            parts = line.split()
        if len(parts) < 3 or parts[0] == "PID":
            continue
        pid_s, status, label = parts[0], parts[1], parts[2]
        jobs[label] = {"pid": int(pid_s) if pid_s.isdigit() else None, "status": status}
    return jobs


def parse_ps(text: str) -> dict[int, dict]:
    """`ps -o pid=,ppid=,command=` -> {pid: {ppid, argv}}."""
    procs: dict[int, dict] = {}
    for line in text.splitlines():
        m = re.match(r"^(\d+)\s+(\d+)\s+(.*)$", line.strip())
        if m:
            procs[int(m.group(1))] = {"ppid": int(m.group(2)), "argv": m.group(3)}
    return procs


def is_bot(procs: dict[int, dict], pid: int | None) -> bool:
    if pid is None or pid not in procs:
        return False
    return "bot.py" in procs[pid]["argv"].split()


# ---------------------------------------------------------------- discovery

def discover(llm_dir: Path, plist_dir: Path):
    """(names, plists, dirs) — the union of `*-bot/` directories and amigo plists."""
    plists: dict[str, Path] = {}
    if plist_dir.is_dir():
        for p in sorted(plist_dir.glob("com.lindsay.amigo.*.plist")):
            m = PLIST_NAME.match(p.name)
            if m:
                plists[m.group(1)] = p
    dirs: dict[str, Path] = {}
    if llm_dir.is_dir():
        for d in sorted(llm_dir.iterdir()):
            if d.is_dir() and d.name.endswith("-bot") and (d / "bot.py").exists():
                dirs[d.name[: -len("-bot")]] = d
    return sorted(set(plists) | set(dirs)), plists, dirs


# ---------------------------------------------------------------- evaluation

def evaluate(names, plists, dirs, jobs, procs, env_reader) -> list[dict]:
    """One row per body. Pure: every input is passed in, so it tests without a Mac."""
    rows = []
    for name in names:
        tag = name.upper()
        label = f"com.lindsay.amigo.{name}"
        job = jobs.get(label)
        pid = job["pid"] if job else None
        bot_dir = dirs.get(name)
        missing = missing_env_keys(env_reader(bot_dir), tag) if bot_dir is not None else ["bot.env (no dir)"]
        rows.append({
            "amigo": name,
            "plist": plists.get(name) is not None,
            "loaded": job is not None,
            "pid": pid,
            "running": is_bot(procs, pid),
            "dir": str(bot_dir) if bot_dir else None,
            "env_missing": missing,
        })
        rows[-1]["ok"] = bool(rows[-1]["plist"] and rows[-1]["running"] and not missing)
    return rows


def _run(cmd: list[str]) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=20).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def gather(llm_dir: Path, plist_dir: Path) -> list[dict]:
    names, plists, dirs = discover(llm_dir, plist_dir)
    jobs = parse_launchctl(_run(["launchctl", "list"]))
    procs = parse_ps(_run(["ps", "axww", "-o", "pid=,ppid=,command="]))

    def env_reader(d):
        try:
            return (d / "bot.env").read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""

    return evaluate(names, plists, dirs, jobs, procs, env_reader)


# ---------------------------------------------------------------- report

def render(rows: list[dict]) -> str:
    if not rows:
        return "no amigo bodies found — no `*-bot/` directory and no amigo plist on disk"
    lines = []
    for r in rows:
        marks = []
        if not r["plist"]:
            marks.append("no plist")
        if not r["loaded"]:
            marks.append("not loaded")
        elif not r["running"]:
            marks.append(f"loaded but no live process (pid={r['pid']})")
        if r["env_missing"]:
            marks.append("env empty: " + ", ".join(r["env_missing"]))
        state = "up" if r["ok"] else "DOWN"
        detail = ("pid %s" % r["pid"]) if r["running"] else ("; ".join(marks) or "no pid")
        lines.append(f"  {state:4}  {r['amigo']:<8}  {detail}")
    down = [r["amigo"] for r in rows if not r["ok"]]
    lines.append("")
    lines.append(f"{len(rows) - len(down)}/{len(rows)} bodies up" +
                 (f"; down: {', '.join(down)}" if down else ""))
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--llm-dir", default=os.path.expanduser("~/LLM"))
    ap.add_argument("--plist-dir", default=os.path.expanduser("~/Library/LaunchAgents"))
    ap.add_argument("--json", action="store_true", help="machine-readable rows")
    args = ap.parse_args(argv)

    if _run(["launchctl", "list"]) == "" and _run(["ps", "axww", "-o", "pid=,ppid=,command="]) == "":
        print("no launchctl/ps on this host — body status is a fact about the machine that runs them")
        return 2

    rows = gather(Path(args.llm_dir), Path(args.plist_dir))
    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        print(render(rows))
    return 0 if rows and all(r["ok"] for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
