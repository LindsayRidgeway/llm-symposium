#!/usr/bin/env python3
# Owner: Desi
"""Which GitHub workflows spend the human's API keys on a clock, and which of them say so.

Why this exists (2026-10-19). `research/2026-10-16-the-burn-so-far.md` sizes an endowment and
carries a known hole, gap 1: "the daily GitHub Actions pipeline calls all four paid providers and
is recorded nowhere, so the true monthly figure is higher by an unknown amount." On 2026-10-19 the
wiring that would close it was already on main, `channels/usage/ci-usage.jsonl` held no rows, and
the reason was not a broken recorder: **there is no daily pipeline.** Three workflows still carry
their retired cron lines as comments — `symposium.yml`, `channel-poll.yml`, `actuator.yml`, all
retired 2026-09-25 — so any reader grepping for `cron:` sees a busy CI and a naive reader of
comments sees a spender that stopped a month ago. Only `quiet-check.yml` still runs on a schedule,
and it calls no model.

That is the defect this script closes: **a commented-out cron is not a schedule, and a schedule
that spends without recording is not a bill you can see.** It parses the workflows with comments
stripped, resolves each workflow's entrypoints, and asks two questions of each:

  * does it spend?  — the entrypoint imports a provider SDK, or the workflow invokes `goose`
  * does it record? — the entrypoint or the workflow names `record_sdk_call`, `record_api_call`,
    `record_rows`, `CI_USAGE_PATH`, or `channels/usage.py`

Exit 1 only when a **scheduled** workflow spends and does not record. A manual workflow that
spends is reported, not failed: it spends when a person asks it to, and the figure for that is
"unknown per dispatch", not "unknown per month". Conflating the two is how a monthly hole gets
budgeted for work that is not happening.

This is a text heuristic, deliberately. It does not import the entrypoints (they need provider
SDKs and keys); it is a tripwire for the next silent spender, not a proof of absence.

CLI:
  python3 scripts/scheduled_spend_audit.py            # table, exit 1 on the defect
  python3 scripts/scheduled_spend_audit.py --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TRIGGERS = ("schedule", "workflow_dispatch", "push", "pull_request",
            "workflow_run", "repository_dispatch", "workflow_call")

# What spending looks like from outside the code: a provider SDK import, a provider key read
# from the environment, or the goose CLI. Deliberately anchored to import/key lines: the first
# version matched the bare word, and `probes/ticktick_recurrence_probe.py` was reported as a
# spender because its docstring cites `discussions/deepseek-review.md`. A tripwire that cries
# wolf on a citation is worse than no tripwire.
SPEND_SIGNALS = re.compile(
    r"^[ \t]*(?:from|import)[ \t]+(?:openai|anthropic)\b"
    r"|^[ \t]*(?:from[ \t]+google[ \t]+import[ \t]+genai|from[ \t]+google\.genai|import[ \t]+google\.genai)"
    r"|(?:DEEPSEEK|OPENROUTER|ANTHROPIC|OPENAI|GOOGLE)_API_KEY",
    re.I | re.M,
)
GOOSE_CLI = re.compile(r"\bgoose\s+(?:run|sessions|recipe)\b")

# What recording looks like. `channels/usage.py` itself is the recorder, not a spender.
RECORD_SIGNALS = re.compile(
    r"(record_sdk_call|record_api_call|record_rows|CI_USAGE_PATH|channels/usage\.py)"
)

ENTRYPOINT = re.compile(r"^\s*(?:-\s*)?(?:run:\s*)?(?:python3?|node|bash|sh)\s+([^\s;|&]+)", re.M)


def strip_comments(text: str) -> str:
    """Drop whole-line YAML comments. A retired cron lives in one, and that is the point."""
    return "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("#"))


def on_block(text: str) -> str:
    """The text under the top-level `on:` key, comments already stripped."""
    m = re.search(r"^on:(.*?)(?=^\S)", text, re.S | re.M)
    return m.group(1) if m else ""


def parse_workflow(path: Path, root: Path | None = None) -> dict:
    root = root or path.parent.parent.parent
    raw = path.read_text(encoding="utf-8", errors="replace")
    live = strip_comments(raw)
    blk = on_block(live)

    triggers = [t for t in TRIGGERS if re.search(rf"^\s*{t}:", blk, re.M)]
    crons = re.findall(r"cron:\s*['\"]([^'\"]+)['\"]", blk)

    entrypoints = []
    for e in ENTRYPOINT.findall(live):
        e = e.strip('"\'')
        if not e or e.startswith("-") or "$" in e:
            continue
        if e not in entrypoints:
            entrypoints.append(e)

    spends_on, records_on = [], []
    for e in entrypoints:
        p = (root / e).resolve()
        if not p.is_file():
            continue
        # A test is not a spender: a stubbed provider is the point of a test.
        if "tests" in p.parts:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        # The recorder is not a spender, whatever words its docstring uses.
        if p.name == "usage.py" and p.parent.name == "channels":
            continue
        if SPEND_SIGNALS.search(text):
            spends_on.append(e)
        if RECORD_SIGNALS.search(text):
            records_on.append(e)
    if GOOSE_CLI.search(live):
        spends_on.append("goose CLI (workflow)")
    if RECORD_SIGNALS.search(live):
        records_on.append("workflow")

    scheduled = "schedule" in triggers and bool(crons)
    spends = bool(spends_on)
    records = bool(records_on)
    if spends and records:
        verdict = "spends-recorded"
    elif spends:
        verdict = "spends-unrecorded"
    elif scheduled:
        verdict = "scheduled-no-spend"
    else:
        verdict = "no-spend"

    return {
        "workflow": path.name,
        "triggers": triggers,
        "crons": crons,
        "scheduled": scheduled,
        "entrypoints": entrypoints,
        "spends_on": spends_on,
        "records_on": records_on,
        "spends": spends,
        "records": records,
        "verdict": verdict,
    }


def audit(directory: Path, root: Path | None = None) -> list[dict]:
    root = root or directory.parent.parent
    return [parse_workflow(p, root) for p in sorted(directory.glob("*.yml"))]


def failures(rows: list[dict]) -> list[dict]:
    """The one defect: a schedule that spends and says nothing."""
    return [r for r in rows if r["scheduled"] and r["spends"] and not r["records"]]


def render(rows: list[dict]) -> str:
    out = []
    for r in rows:
        when = ("cron " + ",".join(r["crons"])) if r["scheduled"] else \
               ("manual (" + "/".join(r["triggers"]) + ")" if r["triggers"] else "no trigger")
        spend = ",".join(r["spends_on"]) or "-"
        rec = ",".join(r["records_on"]) or "-"
        out.append(f"{r['workflow']:30s} {when:28s} {r['verdict']:20s} spends={spend[:40]:40s} records={rec[:30]}")
    sched = [r for r in rows if r["scheduled"]]
    spend_sched = [r for r in sched if r["spends"]]
    out.append("")
    out.append(f"{len(rows)} workflow(s): {len(sched)} scheduled, "
               f"{len(spend_sched)} of them spend money, "
               f"{len(failures(rows))} spend without recording.")
    manual_spend = [r for r in rows if r["spends"] and not r["scheduled"]]
    if manual_spend:
        out.append("Manual spenders (unknown per dispatch, not per month): "
                   + ", ".join(r["workflow"] for r in manual_spend))
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dir", default=str(ROOT / ".github" / "workflows"))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    directory = Path(args.dir)
    rows = audit(directory)
    if args.json:
        print(json.dumps({"workflows": rows, "failures": [r["workflow"] for r in failures(rows)]},
                         indent=2))
    else:
        print(render(rows))
    bad = failures(rows)
    if bad:
        print("\nFAIL: scheduled spend with no usage record: "
              + ", ".join(r["workflow"] for r in bad), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
