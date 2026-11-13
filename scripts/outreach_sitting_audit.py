#!/usr/bin/env python3
"""Does an outreach chat leave an artifact behind?

Written 2026-11-13 (Desi), in the first outreach chat the founder opened. The device is a chat
window per amigo dedicated to outreach. The defect it inherits is the commons' oldest one: the
commons knows something and the amigo does not, and a chat is a place where work happens and a
wretched place for record. A conversation that sends nothing and registers nothing is
indistinguishable, later, from a conversation that never happened — and the four-month record of
outreach says most of them were the second kind.

So the rule this file enforces: **a sitting in an outreach chat owes the repository one of two
things — an artifact, or the word `nothing` with a reason.** The register is
`channels/outreach/sittings.md`. This script reads it and reports:

  1. ARTIFACT MISSING — a row names a path that does not exist.
  2. NO REASON — a row says `nothing` and does not say why, in a sentence.
  3. UNDECLARED SITTING — a commit touched channels/outbound/ (a letter queued to leave) on a date
     on or after the register's first row, and no row exists for that date.
  4. UNDECLARED SITTING — the prospect ledger names a `sent` letter dated on or after the register's
     first row, and no row exists for that date. Checks 3 and 4 are the ones with teeth: they catch
     the sitting nobody wrote down, which is exactly the failure that produced the register.

What it cannot do is make a chat write a row. The honest statement of the guarantee: **work that
reaches the sending paths cannot stay undeclared; a sitting that reached nothing can only be
declared by the amigo who sat in it.** Check 3 is why the first half is not a promise but a test.

Usage:
    python3 scripts/outreach_sitting_audit.py            # report
    python3 scripts/outreach_sitting_audit.py --check    # exit 1 if any problem is found
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REGISTER = REPO / "channels" / "outreach" / "sittings.md"
PIPELINE = REPO / "channels" / "outreach" / "pipeline.json"
# Deliberately NOT channels/sent/: that directory also holds the letters the amigos write to each
# other, which are not outreach and have no sitting to declare. A letter counts as outreach when the
# prospect ledger says it was sent (check 4) or when the commit touched the outreach tree.
SENDING_PATHS = ("channels/outbound",)
MIN_REASON_WORDS = 8

# | 01 | 2026-11-13 | Desi Outreach #01 | desi | channels/sent/x.md | what left the building |
ROW_RE = re.compile(r"^\|\s*([^|]+?)\s*\|")


def parse_register(text: str) -> list[dict[str, str]]:
    """Rows of the register's main table, as dicts keyed by lowercased header names.

    Tolerant on purpose: header names are read from the table rather than assumed, so the register
    can gain a column without silently shifting every row's meaning.
    """
    rows: list[dict[str, str]] = []
    header: list[str] | None = None
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            header = None if not line else header
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(set(c) <= set("-: ") for c in cells):
            continue  # separator row
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if len(cells) != len(header):
            continue
        rows.append(dict(zip(header, cells)))
    return rows


def register_start(rows: list[dict[str, str]]) -> str | None:
    """The earliest date any row declares — the point from which check 3 applies."""
    dates = sorted(r.get("date", "") for r in rows if re.fullmatch(r"\d{4}-\d{2}-\d{2}", r.get("date", "")))
    return dates[0] if dates else None


def row_problems(row: dict[str, str], exists=os.path.exists) -> list[str]:
    """Problems with one row, independent of git."""
    problems = []
    where = f"row {row.get('no', '?')} ({row.get('date', '?')}, {row.get('who', '?')})"
    artifact = (row.get("artifact") or "").strip().strip("`")
    outcome = (row.get("what left the building") or row.get("outcome") or "").strip()
    if not artifact:
        problems.append(f"NO ARTIFACT COLUMN — {where} names no artifact and does not say 'nothing'")
        return problems
    if artifact.lower() == "nothing":
        if len(outcome.split()) < MIN_REASON_WORDS:
            problems.append(
                f"NO REASON — {where} says nothing left the building and does not say why "
                f"({len(outcome.split())} words, {MIN_REASON_WORDS} required)"
            )
        return problems
    if not exists(str(artifact)):
        problems.append(f"ARTIFACT MISSING — {where} names {artifact}, which is not in the tree")
    return problems


def declared_dates(rows: list[dict[str, str]]) -> set[str]:
    return {r["date"] for r in rows if re.fullmatch(r"\d{4}-\d{2}-\d{2}", r.get("date", ""))}


def commit_dates_touching(paths=SENDING_PATHS, since: str | None = None, repo: Path = REPO) -> dict[str, list[str]]:
    """date -> subjects of commits that touched a sending path on or after `since`.

    Returns an empty mapping when git cannot be run (a bare checkout, a CI image without history);
    the caller keeps that distinct from "no commits", so an unavailable check never reads as a pass.
    """
    cmd = ["git", "-C", str(repo), "log", "--date=short", "--format=%ad%x09%s", "--name-only", "--"]
    cmd += list(paths)
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return {}
    found: dict[str, list[str]] = {}
    date, subject = "", ""
    for line in out.splitlines():
        if "\t" in line and re.match(r"^\d{4}-\d{2}-\d{2}\t", line):
            date, subject = line.split("\t", 1)
            continue
        if not line.strip():
            continue
        # a file name line: this commit touched a sending path
        if since and date >= since:
            found.setdefault(date, [])
            if subject not in found[date]:
                found[date].append(subject)
    return found


def pipeline_sent_dates(pipeline_path: Path = PIPELINE) -> dict[str, str]:
    """date -> prospect id, for every ledger row that names a letter it has sent.

    Read from the ledger rather than from channels/sent/, because channels/sent/ holds inter-amigo
    letters too. A prospect whose `sent` path carries a date prefix is a letter to a stranger, and a
    letter to a stranger is what the register exists to record.
    """
    import json

    try:
        data = json.loads(pipeline_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    found: dict[str, str] = {}
    for p in data.get("prospects", []):
        sent = str(p.get("sent") or "")
        m = re.search(r"(\d{4}-\d{2}-\d{2})", sent)
        if m:
            found.setdefault(m.group(1), str(p.get("id") or "?"))
    return found


def undeclared(rows: list[dict[str, str]], since: str | None, commits: dict[str, list[str]],
               pipeline_sends: dict[str, str] | None = None) -> list[str]:
    declared = declared_dates(rows)
    problems = []
    for date in sorted(commits):
        if since and date < since:
            continue
        if date not in declared:
            which = "; ".join(commits[date][:3])
            problems.append(f"UNDECLARED SITTING — {date} touched a sending path with no register row: {which}")
    for date, pid in sorted((pipeline_sends or {}).items()):
        if since and date < since:
            continue
        if date not in declared:
            problems.append(
                f"UNDECLARED SITTING — {date} the prospect ledger says a letter went to '{pid}' "
                f"and no register row exists for that date"
            )
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Audit channels/outreach/sittings.md")
    ap.add_argument("--check", action="store_true", help="exit 1 if any problem is found")
    args = ap.parse_args(argv)

    if not REGISTER.is_file():
        print(f"outreach sittings: register missing at {REGISTER.relative_to(REPO)}")
        return 1 if args.check else 0

    rows = parse_register(REGISTER.read_text(encoding="utf-8"))
    problems = [p for r in rows for p in row_problems(r)]
    since = register_start(rows)
    commits = commit_dates_touching(since=since)
    history_available = bool(commits) or _git_available()
    sends = pipeline_sent_dates()
    problems += undeclared(rows, since, commits, sends)

    print(f"outreach sittings — {len(rows)} declared, register applies from {since or 'no row yet'}")
    for row in rows:
        art = (row.get("artifact") or "").strip().strip("`")
        print(f"  {row.get('no', '?'):>2}  {row.get('date', '?'):<10}  {row.get('who', '?'):<7}  {art}")
    if not history_available:
        print("  NOTE: git history unavailable here — the undeclared-sitting check did not run")
    for p in problems:
        print("  " + p)
    if not problems:
        print("  no problems found")
    return 1 if (problems and args.check) else 0


def _git_available() -> bool:
    try:
        subprocess.run(["git", "-C", str(REPO), "rev-parse", "--git-dir"],
                       capture_output=True, check=True)
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


if __name__ == "__main__":
    sys.exit(main())
