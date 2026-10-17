#!/usr/bin/env python3
"""What a wake spends its actions on — measured from the runs' own transcripts.

Why this exists (agenda item 20, "creating motive", first step; and item 06's standing
worry about runs that reconnoitre instead of delivering). The wake instruction says, as
of 2026-09-25:

    "Measured over 35 runs: 30 of them were cut off at goose's own action cap and most
     of their actions went on reconnaissance, which is why five consecutive wakes
     screened the same condition and none delivered a write-up."

That sentence is the justification for three rules (start with the artefact, rotate the
subject, rotate the to-do list) and it has never been checked against the transcripts it
describes. This script checks it and keeps checking it: every goose run leaves a
`worker.jsonl` in its run directory, and every tool call a run made is a line in that
file. So the division of a run's actions into *reading* and *writing* is a measurement,
not an impression.

What is measured, per run
-------------------------
  actions     every tool request the wake issued (one per assistant tool call)
  read        actions that only looked: ls/find/cat/head/tail/sed/grep/rg/wc/git log/
              git diff/git show/git status, and the `tree`/`analyze`/`read_image` tools
  write       actions that changed the disk: write/edit/todo, shell with a redirection
              to a file, tee/cp/mv/rm/mkdir/touch/chmod, git add/commit
  other       everything else: python scripts whose effect cannot be read off the
              command line, network fetches, curl to an unknown destination, mail

The classifier is a heuristic and is stated as one. A shell command is split on `&&` and
`;` into segments, `cd`/`export` prefixes are dropped, and the first remaining segment
that names a known command decides the action. A compound command that reads and writes
in one call is counted once, by its first known segment. That is a small error on a large
number; it is not a large error on a small one, and the report says so.

Usage
-----
    python3 scripts/wake_shape_audit.py                 # summary table to stdout
    python3 scripts/wake_shape_audit.py --csv out.csv   # one row per run
    python3 scripts/wake_shape_audit.py --root ~/LLM   # a different run root
"""

from __future__ import annotations

import argparse
import csv
import glob
import gzip
import json
import os
import re
import statistics
import sys

READ_TOOLS = {"tree", "analyze", "read_image"}
WRITE_TOOLS = {"write", "edit", "apps__create_app", "apps__iterate_app"}
BOOKKEEPING_TOOLS = {"todo__todo_write"}
READ_CMDS = {
    "ls", "cat", "head", "tail", "sed", "grep", "rg", "find", "wc", "stat", "du", "df",
    "file", "which", "pwd", "awk", "sort", "uniq", "cut", "diff", "jq",
    "python3", "python",  # see --assume-python-read: counted as other unless asked
    "git",
}
WRITE_CMDS = {"tee", "cp", "mv", "rm", "mkdir", "touch", "chmod", "chown", "ln", "install"}
GIT_WRITE_SUB = {"add", "commit", "checkout", "switch", "merge", "rebase", "push", "stash"}
GIT_READ_SUB = {"log", "diff", "show", "status", "ls-files", "grep", "rev-parse", "blame", "branch"}

SPLIT_RE = re.compile(r"\s*(?:&&|\|\||;)\s*")
ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
# A redirection that writes a file. 2>&1, >/dev/null and here-doc openings are not writes.
REDIRECT_RE = re.compile(r"(?<![0-9])>{1,2}(?!&)(?!/dev/null)(?=\s*\S)")


def _first_command(segment: str) -> str:
    """The command word of a segment, after dropping VAR=value and `cd x` prefixes."""
    words = segment.strip().split()
    i = 0
    while i < len(words) and (ASSIGN_RE.match(words[i]) or words[i] in {"cd", "export", "set", "source"}):
        i += 1
        # `cd <dir>` consumes its argument; `export A=1` does not
        if words[i - 1] == "cd" and i < len(words):
            i += 1
    return os.path.basename(words[i]) if i < len(words) else ""


FETCH_RE = re.compile(r"https?://|\bcurl\b|\bwget\b|urllib|requests\.|\bPubMed\b|eutils|europepmc", re.I)
# A redirection that writes the run's own bookkeeping (its report, its to-do, /tmp) is not
# a change to the repository; measured 2026-10-17 because counting report.txt as "write"
# inflated every amigo's write share, and Gemini writes its report first on almost every run.
BOOKKEEPING_RE = re.compile(r"report\.txt|/tick-state/|^/tmp/|\s/tmp/")


def classify_shell(command: str) -> str:
    """read / write / fetch / other, by the first segment that names a command we know."""
    command = (command or "").strip()
    if not command:
        return "other"
    redirect = REDIRECT_RE.search(command.replace("2>&1", ""))
    if redirect:
        target = command[redirect.start():].lstrip(">").strip()
        if BOOKKEEPING_RE.search(target.split()[0] if target.split() else ""):
            return "bookkeeping"
        return "write"
    if FETCH_RE.search(command):
        return "fetch"
    for segment in SPLIT_RE.split(command):
        word = _first_command(segment)
        if not word:
            continue
        if word == "git":
            parts = segment.split()
            try:
                sub = parts[parts.index("git") + 1]
            except (ValueError, IndexError):
                return "read"
            if sub in GIT_WRITE_SUB:
                return "write"
            if sub in GIT_READ_SUB:
                return "read"
            return "other"
        if word in WRITE_CMDS:
            return "write"
        if word in {"python3", "python", "node", "curl"}:
            return "other"
        if word in READ_CMDS:
            return "read"
    return "other"


def classify_tool(name: str, args: dict) -> str:
    if name in BOOKKEEPING_TOOLS:
        return "bookkeeping"
    if name in WRITE_TOOLS:
        return "write"
    if name in READ_TOOLS:
        return "read"
    if name == "shell" or name.endswith("__shell"):
        cmd = args.get("command") or args.get("cmd") or ""
        return classify_shell(cmd if isinstance(cmd, str) else "")
    return "other"


def transcript_path(run_dir: str) -> str:
    """The run's transcript: plain `worker.jsonl`, or the gzipped copy older runs keep.

    Measured 2026-10-17: 675 of 690 run directories hold `worker.jsonl.gz` and only 15
    hold the plain file — the runner gzips a finished run's transcript. A reader that
    opened only the plain name saw 15 runs and would have reported a corpus of 15.
    """
    plain = os.path.join(run_dir, "worker.jsonl")
    if os.path.exists(plain):
        return plain
    gz = plain + ".gz"
    return gz if os.path.exists(gz) else ""


def tool_requests(worker_jsonl: str):
    """Yield (tool_name, arguments) for every tool call in a run transcript."""
    try:
        if worker_jsonl.endswith(".gz"):
            fh = gzip.open(worker_jsonl, "rt", encoding="utf-8", errors="replace")
        else:
            fh = open(worker_jsonl, encoding="utf-8", errors="replace")
    except OSError:
        return
    with fh:
        for line in fh:
            line = line.strip()
            if not line.startswith("{"):
                continue  # goose's banner lines
            try:
                msg = json.loads(line).get("message") or {}
            except ValueError:
                continue
            for block in msg.get("content") or []:
                if not isinstance(block, dict) or block.get("type") != "toolRequest":
                    continue
                value = ((block.get("toolCall") or {}).get("value")) or {}
                name = value.get("name") or ""
                args = value.get("arguments") or {}
                yield name, args if isinstance(args, dict) else {}


def measure_run(run_dir: str) -> dict:
    run_id = os.path.basename(run_dir.rstrip("/"))
    bot = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(run_dir.rstrip("/")))))
    amigo = bot[: -len("-bot")] if bot.endswith("-bot") else bot
    row = {
        "amigo": amigo,
        "run_id": run_id,
        "date": run_id[:8],
        "actions": 0,
        "read": 0,
        "write": 0,
        "other": 0,
        "fetch": 0,
        "bookkeeping": 0,
        "changed_paths": 0,
        "dup_reads": 0,
        "max_repeat": 0,
        "status": "",
        "cut_off": "",
        "total_tokens": "",
        "session_id": "",
        "land_claimed_paths": "",
    }
    reads: dict[str, int] = {}
    for name, args in tool_requests(transcript_path(run_dir)):
        kind = classify_tool(name, args)
        row["actions"] += 1
        row[kind] += 1
        if kind == "read":
            # a repeated identical read is the signature of going round in a circle
            key = name + "\x00" + str(args.get("command") or args.get("path") or args)[:400]
            reads[key] = reads.get(key, 0) + 1
    row["dup_reads"] = sum(n - 1 for n in reads.values())
    row["max_repeat"] = max(reads.values()) if reads else 0
    try:
        with open(os.path.join(run_dir, "result.json"), encoding="utf-8") as fh:
            data = json.load(fh)
        row["changed_paths"] = len(data.get("changed_paths") or [])
        row["status"] = data.get("status") or ""
        row["cut_off"] = "yes" if data.get("cut_off") else ("no" if data.get("cut_off") is False else "")
        row["total_tokens"] = data.get("total_tokens") or ""
        row["session_id"] = data.get("session_id") or ""
        row["land_claimed_paths"] = len(data.get("land_claimed") or [])
    except (OSError, ValueError):
        row["status"] = "(no result.json)"
    return row


def collect(root: str) -> list[dict]:
    dirs = sorted(glob.glob(os.path.join(os.path.expanduser(root), "*-bot", "tick-state", "runs", "*")))
    rows = []
    for d in dirs:
        if os.path.isdir(d):
            rows.append(measure_run(d))
    return rows


def _median(values):
    values = [v for v in values if isinstance(v, (int, float))]
    return statistics.median(values) if values else float("nan")


def summary(rows: list[dict]) -> str:
    measured = [r for r in rows if r["actions"] > 0]
    out = []
    out.append(f"runs found: {len(rows)}   with a readable transcript: {len(measured)}")
    total = sum(r["actions"] for r in measured)
    out.append(
        "actions: {} total, median {:.0f} per run; read {} ({:.1f}%), write {} ({:.1f}%), fetch {} ({:.1f}%), bookkeeping/other {} ({:.1f}%)".format(
            total,
            _median([r["actions"] for r in measured]),
            sum(r["read"] for r in measured), 100.0 * sum(r["read"] for r in measured) / max(total, 1),
            sum(r["write"] for r in measured), 100.0 * sum(r["write"] for r in measured) / max(total, 1),
            sum(r["fetch"] for r in measured), 100.0 * sum(r["fetch"] for r in measured) / max(total, 1),
            sum(r["other"] for r in measured) + sum(r["bookkeeping"] for r in measured),
            100.0 * (sum(r["other"] for r in measured) + sum(r["bookkeeping"] for r in measured)) / max(total, 1),
        )
    )
    out.append("")
    out.append(f"{'amigo':10} {'runs':>5} {'actions':>8} {'med':>5} {'read%':>6} {'write%':>7} "
               f"{'cut_off':>8} {'med paths':>10} {'zero-path runs':>15}")
    by_amigo: dict[str, list[dict]] = {}
    for r in measured:
        by_amigo.setdefault(r["amigo"], []).append(r)
    for amigo in sorted(by_amigo, key=lambda a: -len(by_amigo[a])):
        rs = by_amigo[amigo]
        acts = sum(r["actions"] for r in rs)
        reads = sum(r["read"] for r in rs)
        writes = sum(r["write"] for r in rs)
        cutoff = sum(1 for r in rs if r["cut_off"] == "yes" and r["status"] != "(no result.json)")
        known = sum(1 for r in rs if r["cut_off"] in ("yes", "no"))
        zero = sum(1 for r in rs if r["changed_paths"] == 0 and r["status"] != "(no result.json)")
        out.append(
            f"{amigo:10} {len(rs):>5} {acts:>8} {_median([r['actions'] for r in rs]):>5.0f} "
            f"{100.0*reads/max(acts,1):>5.1f}% {100.0*writes/max(acts,1):>6.1f}% "
            f"{(f'{cutoff}/{known}' if known else '-'):>8} {_median([r['changed_paths'] for r in rs]):>10.0f} "
            f"{f'{zero}/{len(rs)}':>15}"
        )
    out.append("")
    # the claim under test: cut-off runs spend most of their actions reading
    cut = [r for r in measured if r["cut_off"] == "yes"]
    full = [r for r in measured if r["cut_off"] == "no"]
    for label, group in (("cut off at the action cap", cut), ("finished under the cap", full)):
        acts = sum(r["actions"] for r in group)
        if not acts:
            continue
        out.append(
            f"{label}: {len(group)} runs, {acts} actions, read {100.0*sum(r['read'] for r in group)/acts:.1f}%, "
            f"write {100.0*sum(r['write'] for r in group)/acts:.1f}%, "
            f"median actions {_median([r['actions'] for r in group]):.0f}, "
            f"median changed paths {_median([r['changed_paths'] for r in group]):.0f}"
        )
    # Claims without artefacts: a report named LAND paths; the run changed nothing on disk.
    claimed = [r for r in measured if str(r.get("land_claimed_paths", "")).strip() not in ("", "0")]
    if claimed:
        hollow = [r for r in claimed if r["changed_paths"] == 0]
        out.append("")
        out.append(
            "reports that named LAND paths: {}; of those, runs that changed no file at all: {} ({:.1f}%)".format(
                len(claimed), len(hollow), 100.0 * len(hollow) / len(claimed)
            )
        )
        by = {}
        for r in claimed:
            by.setdefault(r["amigo"], [0, 0])
            by[r["amigo"]][0] += 1
            by[r["amigo"]][1] += 1 if r["changed_paths"] == 0 else 0
        for amigo in sorted(by, key=lambda a: -by[a][1]):
            n, h = by[amigo]
            out.append(f"  {amigo:10} {h}/{n} claim-bearing runs changed nothing ({100.0*h/n:.0f}%)")

    # Loops: an identical read repeated inside one run.
    out.append("")
    reps = [r["max_repeat"] for r in measured]
    out.append(
        "repeated reads: median most-repeated single read per run {:.0f}; runs that issued the same "
        "read 3+ times: {}/{}".format(
            _median(reps), sum(1 for n in reps if n >= 3), len(measured)
        )
    )

    # The 2026-09-25 instruction change ("start with the artefact, not with the research"),
    # measured on the runs on either side of it.
    out.append("")
    out.append("period         runs  actions  read%  write%  zero-path%")
    for label, lo, hi in (
        ("before 09-25", "00000000", "20260925"),
        ("09-25 onward ", "20260925", "99999999"),
    ):
        group = [r for r in measured if lo <= r["date"] < hi]
        acts = sum(r["actions"] for r in group)
        if not acts:
            continue
        zero = sum(1 for r in group if r["changed_paths"] == 0)
        out.append(
            f"{label} {len(group):>5} {acts:>8} {100.0*sum(r['read'] for r in group)/acts:>5.1f}% "
            f"{100.0*sum(r['write'] for r in group)/acts:>5.1f}% {100.0*zero/len(group):>9.1f}%"
        )
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default="~/LLM", help="directory holding *-bot/tick-state/runs")
    ap.add_argument("--csv", help="write one row per run here")
    ap.add_argument("--quiet", action="store_true", help="no summary on stdout")
    args = ap.parse_args(argv)
    rows = collect(args.root)
    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else ["amigo"])
            writer.writeheader()
            writer.writerows(rows)
    if not args.quiet:
        print(summary(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
