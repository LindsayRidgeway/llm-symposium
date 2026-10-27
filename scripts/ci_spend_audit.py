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

The three questions it answers per workflow:

  spends?   a script the workflow executes talks to a paid provider — an SDK import
            (openai / anthropic / google.genai), a provider endpoint, or a goose run
            (which bills whatever provider it is pointed at)
  records?  that script touches the usage ledger — `record_sdk_call`, `record_api_call`,
            `channels.usage`, or runner.py's `_record_usage`
  persists? a step after it stages the ledger path, commits, and pushes — a row written
            into a runner's filesystem and never committed is indistinguishable from no
            row at all, which is the exact shape of the 2026-10-16 gap ("closed in code,
            open in data"): a recorder that works, and a file that does not survive the job.

Exit code is 1 when an on-the-clock spender does not record, **or when any spender records
into a file the runner throws away**. A `workflow_dispatch`-only workflow that records
nothing is reported but never fails the check: a human pressing a button knows they are
spending, and that is the whole point of the retirement. A manual workflow that *does*
record is held to the persistence test — the money is the same whichever hand pressed it.

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


LEDGER_PATH = "channels/usage/ci-usage.jsonl"


def _covers_ledger(pathspec: str) -> bool:
    """Does this `git add` pathspec take `channels/usage/ci-usage.jsonl` with it?

    `git add .` and `git add -A` do. So does any directory above the file (`channels/`,
    `channels/usage/`) and the file itself. `git add tests/…` does not, and neither does a
    pathspec that only looks like a parent — `channels/usage-notes/` must not pass.
    """
    p = pathspec.strip().strip("'\"")
    if p in ("-A", "--all", ".", ":/", "*"):
        return True
    p = p.rstrip("/")
    if p in ("", "channels", "channels/usage"):
        return True
    if p.startswith("*") or "*" in p:         # `channels/usage/*.jsonl`
        prefix = p.split("*")[0].rstrip("/")
        return LEDGER_PATH.startswith(prefix + "/") or prefix == ""
    return p == LEDGER_PATH or LEDGER_PATH.startswith(p + "/")


def persistence(text: str) -> dict:
    """Can a row written to `channels/usage/ci-usage.jsonl` reach `main` from this workflow?

    Three things are needed and each one alone is a false positive: staging without a commit
    leaves the row in the index, a commit without a push leaves it in the runner's clone, and a
    push alone sends whatever was already committed. Commented-out lines do not count — the
    repository is full of retired steps, and reading one as live is the failure this file
    exists to avoid.
    """
    stages = commits = pushes = False
    evidence = []
    for raw in text.splitlines():
        line = _strip_comment(raw).strip()
        if not line:
            continue
        # `git` may sit behind a conditional or a loop — `if git push …; then`, `for …; do git
        # commit …` — so each command is searched for anywhere in the line, not only at its
        # start. The first version of this required `^git` and reported two real pushes as
        # absent, which would have turned a working workflow into a FAIL.
        add = re.search(r"\bgit\s+add\b(.*)", line)
        if add:
            rest = re.split(r"&&|\|\||[;|]", add.group(1))[0]
            args = [a for a in rest.split() if a != "--"]
            if any(_covers_ledger(a) for a in args):
                stages = True
                evidence.append(line)
        if re.search(r"\bgit\b[^\n]*?\bcommit\b", line):
            commits = True
            evidence.append(line)
        if re.search(r"\bgit\b[^\n]*?\bpush\b", line):
            pushes = True
            evidence.append(line)
    return {"stages": stages, "commits": commits, "pushes": pushes,
            "persists": stages and commits and pushes, "evidence": evidence}


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
        keep = persistence(text)
        rows.append({
            "workflow": wf.name,
            "triggers": triggers,
            "on_clock": on_clock,
            "spends": spends,
            "spends_because": why,
            "records": records if spends else None,
            # Only asked of a workflow that records: "persists" of a workflow with nothing to
            # persist is a column that would answer a question nobody asked.
            "persists": keep["persists"] if (spends and records) else None,
            "persists_because": keep["evidence"] if (spends and records) else [],
            "verdict": _verdict(spends, records, on_clock, keep["persists"]),
        })
    return rows


def _verdict(spends: bool, records: bool, on_clock: list, persists=None) -> str:
    if not spends:
        return "no model spend"
    if records and persists is False:
        # The row is real and the file dies with the job. This is not a lesser failure than
        # recording nothing: it is the same silence with a receipt that says it was fixed.
        return "FAIL: records rows the runner throws away"
    if on_clock and not records:
        return "FAIL: on the clock and unrecorded"
    if on_clock and records:
        return "on the clock, recorded"
    if records:
        return "manual, recorded"
    return "manual, unrecorded"


def render(rows: list) -> str:
    w = max([len(r["workflow"]) for r in rows] + [8])
    out = [f"{'workflow'.ljust(w)}  {'clock':<10} {'spends':<7} {'records':<8} "
           f"{'keeps':<6} verdict",
           "-" * (w + 46)]
    for r in rows:
        clock = ",".join(r["on_clock"]) if r["on_clock"] else "-"
        spends = "yes" if r["spends"] else "-"
        records = "-" if r["records"] is None else ("yes" if r["records"] else "NO")
        keeps = "-" if r.get("persists") is None else ("yes" if r["persists"] else "NO")
        out.append(f"{r['workflow'].ljust(w)}  {clock:<10} {spends:<7} {records:<8} "
                   f"{keeps:<6} {r['verdict']}")
    clocked = [r for r in rows if r["on_clock"] and r["spends"]]
    out.append("")
    if not clocked:
        out.append("On the clock and spending: none. Every workflow that can reach a paid "
                   "provider waits for a human to dispatch it.")
    else:
        out.append(f"On the clock and spending: {len(clocked)} "
                   f"({', '.join(r['workflow'] for r in clocked)})")
    failures = [r for r in rows if r["verdict"].startswith("FAIL")]
    unrecorded = [r for r in failures if "unrecorded" in r["verdict"]]
    out.append("Unrecorded on-the-clock spend: "
               f"{len(unrecorded)}" + (" — " + ", ".join(r["workflow"] for r in unrecorded)
                                       if unrecorded else " (the ledger's zero is explained)"))
    lost = [r for r in rows if r["verdict"] == "FAIL: records rows the runner throws away"]
    out.append("Rows a recording workflow loses with its runner: "
               f"{len(lost)}" + (" — " + ", ".join(r["workflow"] for r in lost)
                                 if lost else " (every recorder stages, commits and pushes "
                                              "the ledger)"))
    return "\n".join(out)


# ------------------------------------------------------------------ history (--history)
#
# Why this second half exists (2026-10-22). The table above answers "does CI spend money?" from
# the repository text alone, and on 2026-10-18 it answered "the ledger's zero is explained:
# every spender is manual". That is true and it is not enough. Three workflows claim `keeps=yes`
# — they stage, commit and push the ledger — and a claim about a step is not evidence that the
# step has ever run. Zero rows in the ledger has two causes that look identical from the repo:
# nobody pressed the button, or somebody pressed it and the row died. Only the public Actions
# history can tell them apart, so this half reads it.
#
# The rule, and why its date is 2026-10-21 rather than the ledger's own birthday: a row can only
# be missing from a run that happened after *that workflow's* recorder existed. The dates differ
# — `runner.py`'s `_record_usage` landed 2026-10-17 (commit 85f7f8a2), `check-tarik-model.yml`'s
# persistence step only on 2026-10-21 (commit 0d82ee81) — so one global date has to be the newest
# of them, and the cost is stated rather than hidden: a `check-tarik-model` run between 10-17 and
# 10-21 that left no row would not be caught here. No such run exists (that workflow's newest run
# is 2026-09-14), so nothing is being concealed today, and after 2026-10-21 the date is exact for
# every workflow. Using the ledger's own birthday would be worse: it would report
# `channel-poll.yml`'s 2026-09-25 run as a lost row, and a check that manufactures one false
# failure on its first run is a check that gets switched off.

RECORDER_EPOCH = "2026-10-21"
DEFAULT_REPO = "LindsayRidgeway/llm-symposium"
LEDGER_FILE = ROOT / "channels" / "usage" / "ci-usage.jsonl"


def ledger_rows(path: Path = LEDGER_FILE) -> list:
    """The recorded rows, tolerating a missing file (the current state: no row has ever landed)."""
    path = Path(path)
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def ledger_evidence(rows: list) -> dict:
    """Which workflows the ledger has a row for, and under which run ids.

    Two row shapes have to count, because the ledger has two writers: a goose row carries
    `workflow` + `run_id`, and a direct API row carries `source` and no run id at all. Matching
    only `workflow` would report `check-tarik-model.yml` as silent while its rows sat in the file.
    """
    names, run_ids = {}, set()
    for r in rows:
        for key in ("workflow", "source"):
            name = r.get(key)
            if isinstance(name, str) and name:
                names.setdefault(name, 0)
                names[name] += 1
        if r.get("run_id"):
            run_ids.add(str(r["run_id"]))
    return {"names": names, "run_ids": run_ids}


def _http_json(url: str):
    """Public GitHub API, no token: anonymous reads of a public repository's run history."""
    import urllib.request
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": "llm-symposium-ci-spend-audit"})
    try:
        with urllib.request.urlopen(req, timeout=25) as fh:
            return json.loads(fh.read().decode("utf-8", "replace"))
    except Exception:
        return None


def workflow_ids(repo: str = DEFAULT_REPO, get=_http_json) -> dict:
    """`filename.yml` → workflow id, from the public API. Empty when the network is unavailable."""
    data = get(f"https://api.github.com/repos/{repo}/actions/workflows?per_page=100")
    if not isinstance(data, dict):
        return {}
    out = {}
    for w in data.get("workflows") or data.get("workflow_runs") or []:
        path = w.get("path") or ""
        if path:
            out[path.rsplit("/", 1)[-1]] = w.get("id")
    return out


def history(rows=None, repo: str = DEFAULT_REPO, get=_http_json,
            ledger: list = None, epoch: str = RECORDER_EPOCH, per_page: int = 10) -> list:
    """For every workflow that can spend: when it last ran, and whether the ledger noticed.

    A verdict of `unknown` is deliberate and never a failure: an audit that turns red because a
    laptop had no network is an audit somebody switches off, and the honest state of "cannot see
    the history" is the same word the CI check already prints for an unreadable invitation list.
    """
    rows = audit() if rows is None else rows
    ledger = ledger_rows() if ledger is None else ledger
    ev = ledger_evidence(ledger)
    ids = workflow_ids(repo, get) if get is not None else {}
    out = []
    for r in rows:
        if not r["spends"]:
            continue
        wid = ids.get(r["workflow"])
        if wid is None:
            verdict, last, run_id = "unknown", None, None
        else:
            data = get(f"https://api.github.com/repos/{repo}/actions/workflows/{wid}"
                       f"/runs?per_page={per_page}")
            runs = (data or {}).get("workflow_runs") if isinstance(data, dict) else None
            if runs is None:
                verdict, last, run_id = "unknown", None, None
            elif not runs:
                verdict, last, run_id = "never dispatched", None, None
            else:
                last = runs[0].get("created_at") or ""
                run_id = runs[0].get("id")
                named = (r["workflow"] in ev["names"]) or (r["workflow"][:-4] in ev["names"])
                if last and last[:10] < epoch:
                    verdict = f"last ran {last[:10]}, before the recorders ({epoch})"
                elif named or str(run_id) in ev["run_ids"]:
                    verdict = f"ran {last[:10]}, row in the ledger"
                else:
                    verdict = (f"FAIL: ran {last[:10]} and left no row "
                               f"(run {run_id}) — the recorder is unproven")
        out.append({"workflow": r["workflow"], "id": wid, "last_run": last,
                    "run_id": run_id, "ledger_rows": ev["names"].get(r["workflow"], 0)
                    + ev["names"].get(r["workflow"][:-4], 0), "verdict": verdict})
    return out


def render_history(hist: list, ledger: list = None) -> str:
    if not hist:
        return "No workflow in this tree can reach a paid provider."
    w = max(len(h["workflow"]) for h in hist)
    out = [f"{'workflow'.ljust(w)}  {'last run':<10} {'rows':<5} verdict", "-" * (w + 40)]
    for h in hist:
        out.append(f"{h['workflow'].ljust(w)}  {(h['last_run'] or '-')[:10]:<10} "
                   f"{h['ledger_rows']:<5} {h['verdict']}")
    n = len(ledger or [])
    exercised = [h for h in hist if h["verdict"].startswith("ran ")]
    out.append("")
    out.append(f"Ledger rows on disk: {n}")
    out.append(f"Spenders proved to have recorded something: {len(exercised)} of {len(hist)}")
    blind = [h["workflow"] for h in hist if h["verdict"] == "unknown"]
    if blind:
        out.append("Cannot see the run history for: " + ", ".join(blind)
                   + " (no network or no API answer; nothing is claimed about them)")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Audit which CI workflows can spend model keys.")
    ap.add_argument("--json", action="store_true", help="machine-readable rows")
    ap.add_argument("--history", action="store_true",
                    help="also ask the public Actions API whether the spenders ever ran")
    ap.add_argument("--repo", default=DEFAULT_REPO, help="owner/name for --history")
    args = ap.parse_args(argv)
    if args.history:
        hist = history(repo=args.repo)
        if args.json:
            print(json.dumps(hist, indent=2))
        else:
            print(render(audit()))
            print()
            print(render_history(hist, ledger_rows()))
        return 1 if any(h["verdict"].startswith("FAIL") for h in hist) else 0

    rows = audit()
    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        print(render(rows))
    return 1 if any(r["verdict"].startswith("FAIL") for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
