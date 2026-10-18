#!/usr/bin/env python3
# Owner: Desi
"""Which GitHub workflows can spend the human's model keys, and which of them record it?

Why this exists (2026-10-18). The runner was wired into `channels/usage/` on 2026-10-17 and the
ledger still says "no CI usage recorded yet". The obvious reading — the wiring is broken — is
wrong: the adapter works (four providers, four rows, token counts intact) and the file is empty
because **nothing on a clock calls a paid provider any more**. `symposium.yml`,
`autonomous-goose-tarik.yml`, `channel-poll.yml` and `test-and-report.yml` were all retired from
`schedule:` in late September and are now `workflow_dispatch` only; the one workflow still on a
cron, `quiet-check.yml`, sends mail and calls no model.

That fact is invisible in every workflow file taken alone. Each retirement is a commented-out
cron with a paragraph of reasoning, so the answer to "does CI spend money?" lives in nine
comment blocks and in nobody's head. This script reads them all and answers in one table, and it
fails if a workflow that *can* run on a clock (a cron, or a push trigger) reaches a paid provider
without recording what it spent.

It is a check, not a model call: it reads the repository, costs nothing, and needs no key.

The two questions it answers per workflow:

  spends?   a script the workflow executes talks to a paid provider — an SDK import
            (openai / anthropic / google.genai), a provider endpoint, or a goose run
            (which bills whatever provider it is pointed at)
  records?  that script touches the usage ledger — `record_sdk_call`, `record_api_call`,
            `channels.usage`, or runner.py's `_record_usage`

Exit code is 1 when an on-the-clock spender does not record. A `workflow_dispatch`-only
workflow is reported but never fails the check: a human pressing a button knows they are
spending, and that is the whole point of the retirement.

CLI:
  python3 scripts/ci_spend_audit.py
  python3 scripts/ci_spend_audit.py --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"

# ------------------------------------------------------------------ vocabularies

# A script spends model money when it can reach a paid provider. Deliberately a text test:
# resolving imports would be exact and would also be wrong, because half these paths arrive as
# a subprocess (`python .github/scripts/runner.py`) and the rest through goose.
SPEND_MARKERS = (
    "from openai import", "import openai", "OpenAI(",
    "from anthropic import", "import anthropic", "Anthropic(",
    "from google import genai", "google.genai", "import genai",
    "api.openai.com", "api.anthropic.com", "generativelanguage.googleapis.com",
    "openrouter.ai/api",
)

# goose bills whatever provider it is pointed at, so a goose run is a spend even though the
# workflow file never names a model vendor it can be checked against.
GOOSE_MARKER = "goose"

RECORD_MARKERS = (
    "record_sdk_call", "record_api_call", "channels.usage", "channels import usage",
    "_record_usage", "ci-usage.jsonl",
)

# A workflow that hands a model key to any step can spend, whatever the script's text says.
KEY_MARKER = re.compile(r"\b(?:OPENAI|ANTHROPIC|GOOGLE|GEMINI|DEEPSEEK|OPENROUTER)_API_KEY\b")

# Timers: a cron or a push means the workflow can spend with nobody watching. A bare
# `workflow_dispatch` does not.
CLOCK_TRIGGERS = ("schedule", "push", "pull_request", "workflow_run", "release")

# Following imports is the difference between a table that is wrong and one that is useful:
# `.github/scripts/poll_channels.py` names no provider itself, but it calls
# `channels.auto_reply.run_auto_reply()`, which does. One level deep, because two would start
# pulling in the whole repository and every script would inherit every marker.
IMPORT_RE = re.compile(r"^\s*(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))", re.M)
LOCAL_ROOTS = ("channels", "scripts")


def _strip_comment(line: str) -> str:
    """Drop a trailing `# ...` comment, leaving quoted hashes alone (enough for YAML here)."""
    out, quote = [], None
    for ch in line:
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
            out.append(ch)
            continue
        if ch == "#":
            break
        out.append(ch)
    return "".join(out).rstrip()


def parse_triggers(text: str) -> list:
    """The uncommented keys under the top-level `on:` block."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if re.match(r"^on:\s*$", line) or re.match(r"^on:\s*\[", line):
            start = i
            break
        # `on: push` written inline
        if re.match(r"^on:\s*\S", line):
            return [_strip_comment(line).split(":", 1)[1].strip()]
    if start is None:
        return []
    triggers = []
    for line in lines[start + 1:]:
        if not line.strip():
            continue
        if not line.startswith((" ", "\t")):
            break                      # next top-level key
        clean = _strip_comment(line)
        if not clean.strip():
            continue                   # a fully commented line is not a trigger
        m = re.match(r"^\s{2}([A-Za-z_][\w-]*):", clean)
        if m:
            triggers.append(m.group(1))
    return triggers


def scripts_in(text: str) -> list:
    """Repository scripts this workflow executes: `python[3] x.py`, in a run block or a step."""
    found = []
    for raw in text.splitlines():
        line = _strip_comment(raw)
        for m in re.finditer(r"python3?\s+([\w./-]+\.py)", line):
            path = m.group(1)
            if path not in found:
                found.append(path)
    return found


def _read(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except OSError:
        return ""


def local_imports(text: str, root: Path = ROOT) -> list:
    """Repository modules a file imports — `channels.auto_reply` → `channels/auto_reply.py`."""
    found = []
    for m in IMPORT_RE.finditer(text):
        name = m.group(1) or m.group(2) or ""
        parts = name.split(".")
        if not parts or parts[0] not in LOCAL_ROOTS:
            continue
        for candidate in (root.joinpath(*parts).with_suffix(".py"),
                          root.joinpath(*parts[:-1]).with_suffix(".py")):
            if candidate.is_file() and candidate not in found:
                found.append(candidate)
                break
    return found


def classify_script(relpath: str, root: Path = ROOT) -> dict:
    """What one script costs and whether it says so, including the modules it calls into."""
    path = (root / relpath).resolve()
    if not path.exists():
        return {"path": relpath, "exists": False, "spends": False, "records": False,
                "provider": []}
    text = _read(path)
    providers = [m for m in SPEND_MARKERS if m in text]
    records = any(m in text for m in RECORD_MARKERS)
    via = []
    for dep in local_imports(text, root):
        dep_text = _read(dep)
        dep_providers = [m for m in SPEND_MARKERS if m in dep_text]
        if dep_providers:
            providers.extend(dep_providers)
            via.append(str(dep.relative_to(root)))
            records = records or any(m in dep_text for m in RECORD_MARKERS)
    # `goose` alone is too common a word to call a spend (this script is in a repository that
    # talks about goose constantly), so it only counts where a workflow actually runs it.
    return {"path": relpath, "exists": True, "spends": bool(providers), "records": records,
            "provider": sorted(set(providers)), "via": via}


def audit(workflow_dir: Path = WORKFLOWS, root: Path = ROOT) -> list:
    """One row per workflow file: triggers, whether it can spend on a clock, whether it records."""
    rows = []
    for wf in sorted(workflow_dir.glob("*.yml")) + sorted(workflow_dir.glob("*.yaml")):
        text = _read(wf)
        triggers = parse_triggers(text)
        scripts = [classify_script(s, root) for s in scripts_in(text)]
        spends, why = False, []
        for s in scripts:
            if s["spends"]:
                spends = True
                why.append(s["path"])
        if re.search(r"^\s*run:.*\bgoose\b", text, re.M) or "download_cli.sh" in text:
            spends = True
            why.append("goose run")
        keys = sorted(set(KEY_MARKER.findall(text)))
        if keys and not spends:
            # A key handed to an inline heredoc is a spend the script scan cannot see. Recorded
            # as a separate reason so the table never claims a workflow is free when it is not.
            spends = True
            why.append("model key in env: " + ", ".join(keys))
        records = bool(scripts) and all(s["records"] for s in scripts if s["spends"])
        if spends and not scripts:
            records = any(m in text for m in RECORD_MARKERS)
        on_clock = [t for t in triggers if t in CLOCK_TRIGGERS]
        rows.append({
            "workflow": wf.name,
            "triggers": triggers,
            "on_clock": on_clock,
            "spends": spends,
            "spends_because": why,
            "records": records if spends else None,
            "verdict": _verdict(spends, records, on_clock),
        })
    return rows


def _verdict(spends: bool, records: bool, on_clock: list) -> str:
    if not spends:
        return "no model spend"
    if on_clock and not records:
        return "FAIL: on the clock and unrecorded"
    if on_clock and records:
        return "on the clock, recorded"
    if records:
        return "manual, recorded"
    return "manual, unrecorded"


def render(rows: list) -> str:
    w = max([len(r["workflow"]) for r in rows] + [8])
    out = [f"{'workflow'.ljust(w)}  {'clock':<10} {'spends':<7} {'records':<8} verdict",
           "-" * (w + 40)]
    for r in rows:
        clock = ",".join(r["on_clock"]) if r["on_clock"] else "-"
        spends = "yes" if r["spends"] else "-"
        records = "-" if r["records"] is None else ("yes" if r["records"] else "NO")
        out.append(f"{r['workflow'].ljust(w)}  {clock:<10} {spends:<7} {records:<8} {r['verdict']}")
    clocked = [r for r in rows if r["on_clock"] and r["spends"]]
    out.append("")
    if not clocked:
        out.append("On the clock and spending: none. Every workflow that can reach a paid "
                   "provider waits for a human to dispatch it.")
    else:
        out.append(f"On the clock and spending: {len(clocked)} "
                   f"({', '.join(r['workflow'] for r in clocked)})")
    failures = [r for r in rows if r["verdict"].startswith("FAIL")]
    out.append("Unrecorded on-the-clock spend: "
               f"{len(failures)}" + (" — " + ", ".join(r["workflow"] for r in failures)
                                     if failures else " (the ledger's zero is explained)"))
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Audit which CI workflows can spend model keys.")
    ap.add_argument("--json", action="store_true", help="machine-readable rows")
    args = ap.parse_args(argv)
    rows = audit()
    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        print(render(rows))
    return 1 if any(r["verdict"].startswith("FAIL") for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
