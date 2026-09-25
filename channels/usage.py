#!/usr/bin/env python3
# Owner: Desi
"""CI usage ledger — the commons' spend outside this Mac.

Why this exists (2026-09-25): every amigo's token cost that runs *through goose on this Mac*
lands in `~/.local/share/goose/sessions/sessions.db` and can be counted. Everything that runs
in GitHub Actions cannot. The workflows use the human's API keys as repository secrets, spend
real money, and report nothing back — so the largest automatic spender in the commons was
invisible from the only place that could see the bill.

It was invisible even to itself. `scripts/run_autonomous_mission.py` runs goose with
`--output-format stream-json` and writes `worker.jsonl` per attempt, which carries exact
`input_tokens`, `output_tokens`, `cache_read_input_tokens` and `cost_usd` in its final
`complete` event. That file is uploaded as a GitHub artifact and expires. Nothing reads it.

The catch, found in the first artifact inspected (Tarik's run 36045264880): a worker killed at
its turn cap never emits `complete` at all — 73 model calls, no usage, no cost, exit 124. Those
are precisely the runs that spend money and produce nothing, so `goose_stream_usage` records
them as **unrecorded** rather than zero. A zero would be a lie; "we spent and cannot say how
much" is the truth, and it is the number worth chasing.

Two sources, one file (`channels/usage/ci-usage.jsonl`, JSON Lines, append-only):

  goose    — parse a stream-json run (`--source goose --dir <artifacts dir>`)
  api      — a direct provider call whose response carries a `usage` block, recorded by
             `record_api_call()` from `channels/auto_reply.py` as it happens

CLI:
  python3 channels/usage.py --source goose --dir "$RUNNER_TEMP/goose-autonomous" \
      --workflow autonomous-goose-tarik --run-id "$GITHUB_RUN_ID" --provider openai \
      --model "$GOOSE_MODEL"
  python3 channels/usage.py --summary
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
USAGE_DIR = REPO_ROOT / "channels" / "usage"
# Overridable: a test that exercises a reply path must not write into the real ledger.
# Caught 2026-09-25, when running the local suite added two rows (tarik, zeros, provider
# names from a stubbed response) that looked exactly like live CI spend.
USAGE_PATH = Path(os.environ.get("CI_USAGE_PATH", str(USAGE_DIR / "ci-usage.jsonl")))


# ------------------------------------------------------------------ normalising

def api_usage(provider: str, response: dict) -> dict:
    """One usage block, four provider shapes, one set of names.

    OpenAI-compatible (OpenAI, DeepSeek, OpenRouter), Anthropic and Gemini each name the same
    three quantities differently. Returns zeros where a provider reports nothing, so a caller
    can always sum without checking.
    """
    out = {"input": 0, "output": 0, "cache_read": 0, "total": 0}
    if not isinstance(response, dict):
        return out
    # Shape first, name second: the auto-reply path only knows the amigo, and detection is
    # exact because the three shapes share no key names. A real Anthropic response carries
    # BOTH `content` and `usage`, so `content` alone is not enough to identify it — the first
    # version of this got that wrong and silently recorded zeros.
    u = response.get("usage") if isinstance(response.get("usage"), dict) else {}
    if provider not in ("anthropic", "google"):
        if "usageMetadata" in response:
            provider = "google"
        elif "prompt_tokens" in u or "choices" in response:
            provider = "openai"
        elif "input_tokens" in u or isinstance(response.get("content"), list):
            provider = "anthropic"
        else:
            provider = "openai"
    if provider == "anthropic":
        out["input"] = u.get("input_tokens") or 0
        out["output"] = u.get("output_tokens") or 0
        out["cache_read"] = u.get("cache_read_input_tokens") or 0
    elif provider == "google":
        ug = response.get("usageMetadata") or {}
        out["input"] = ug.get("promptTokenCount") or 0
        out["output"] = ug.get("candidatesTokenCount") or 0
        out["cache_read"] = ug.get("cachedContentTokenCount") or 0
    else:                                   # openai / deepseek / openrouter
        out["input"] = u.get("prompt_tokens") or 0
        out["output"] = u.get("completion_tokens") or 0
        out["cache_read"] = ((u.get("prompt_tokens_details") or {}).get("cached_tokens")
                             or u.get("prompt_cache_hit_tokens") or 0)
    out["total"] = out["input"] + out["output"]
    if not out["total"]:
        out["total"] = u.get("total_tokens") or 0
    return out


def goose_stream_usage(path) -> dict:
    """Tokens and cost from one goose `--output-format stream-json` file.

    The `complete` event is the only place goose reports usage, and a worker killed at its turn
    cap never writes one. `completed` is therefore reported alongside the numbers, and a file
    with model calls but no completion is marked `unrecorded` — the run cost money and we cannot
    say how much. Counting that as zero is the failure this module exists to prevent.
    """
    path = Path(path)
    out = {"completed": False, "model_calls": 0, "input": None, "output": None,
           "cache_read": None, "total": None, "cost_usd": None, "unrecorded": False}
    if not path.is_file():
        return out
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get("type") == "message":
                out["model_calls"] += 1
            elif event.get("type") == "complete":
                out["completed"] = True
                out["input"] = event.get("input_tokens")
                out["output"] = event.get("output_tokens")
                out["cache_read"] = event.get("cache_read_input_tokens")
                out["total"] = event.get("total_tokens")
                out["cost_usd"] = event.get("cost_usd")
    except OSError:
        return out
    out["unrecorded"] = (not out["completed"]) and out["model_calls"] > 0
    return out


# ------------------------------------------------------------------ the ledger

def record_rows(rows, path=USAGE_PATH) -> int:
    """Append rows to the ledger. Returns how many were written. Never raises on write."""
    rows = [r for r in rows if r]
    if not rows:
        return 0
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    return len(rows)


def load_rows(path=USAGE_PATH):
    path = Path(path)
    if not path.is_file():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass
    return rows


def record_api_call(provider: str, model: str, response: dict, source="api",
                     path=USAGE_PATH) -> None:
    """Record one direct provider call from inside a running script.

    Wrapped by the caller in try/except: a bookkeeping failure must never break a reply.
    """
    u = api_usage(provider, response)
    record_rows([{
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": source,
        "provider": provider,
        "model": model,
        "input": u["input"],
        "output": u["output"],
        "cache_read": u["cache_read"],
        "total": u["total"],
        "cost_usd": None,          # providers do not return cost; only goose estimates it
        "recorded": bool(u["total"]),
    }], path)


def summarize(rows, path=USAGE_PATH) -> str:
    """A small table, by model. Reads the ledger unless rows are given."""
    rows = rows if rows is not None else load_rows(path)
    if not rows:
        return "no CI usage recorded yet\n"
    by_model = {}
    unrecorded = 0
    for r in rows:
        key = (r.get("provider") or "?", r.get("model") or "?")
        slot = by_model.setdefault(key, {"calls": 0, "runs": 0, "input": 0, "output": 0,
                                         "cache": 0, "cost": 0.0, "cost_known": False,
                                         "unrecorded": 0})
        slot["runs"] += 1
        slot["calls"] += r.get("model_calls") or 1
        slot["input"] += r.get("input") or 0
        slot["output"] += r.get("output") or 0
        slot["cache"] += r.get("cache_read") or 0
        if r.get("cost_usd") is not None:
            slot["cost"] += r["cost_usd"]
            slot["cost_known"] = True
        if r.get("unrecorded"):
            slot["unrecorded"] += 1
            unrecorded += 1
    lines = ["| provider | model | runs | model calls | input | cache read | output | cost |",
             "|---|---|---|---|---|---|---|---|"]
    for (prov, model), s in sorted(by_model.items(), key=lambda kv: -kv[1]["runs"]):
        cost = ("$%.2f" % s["cost"]) if s["cost_known"] else "not reported"
        lines.append("| %s | %s | %d | %d | %s | %s | %s | %s |" % (
            prov, model, s["runs"], s["calls"],
            "{:,}".format(s["input"]), "{:,}".format(s["cache"]), "{:,}".format(s["output"]),
            cost))
    lines.append("")
    lines.append("%d run(s) spent tokens and left no usage record (killed before completion)."
                 % unrecorded)
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------ CLI

def _rows_from_goose_dir(directory, workflow, run_id, provider, model, label=None):
    """One row per goose attempt found under `directory`."""
    directory = Path(directory)
    rows = []
    files = sorted(directory.rglob("worker.jsonl"))
    for f in files:
        u = goose_stream_usage(f)
        rows.append({
            "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "source": "ci-goose",
            "workflow": workflow,
            "run_id": str(run_id) if run_id else None,
            "label": label or f.parent.name,
            "provider": provider,
            "model": model,
            "model_calls": u["model_calls"],
            "input": u["input"],
            "output": u["output"],
            "cache_read": u["cache_read"],
            "total": u["total"],
            "cost_usd": u["cost_usd"],
            "completed": u["completed"],
            "unrecorded": u["unrecorded"],
        })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description="Record CI model usage into the commons ledger.")
    ap.add_argument("--source", choices=["goose"], default=None)
    ap.add_argument("--dir", help="directory to search for goose worker.jsonl files")
    ap.add_argument("--workflow")
    ap.add_argument("--run-id")
    ap.add_argument("--provider", default="unknown")
    ap.add_argument("--model", default="unknown")
    ap.add_argument("--label")
    ap.add_argument("--path", default=str(USAGE_PATH))
    ap.add_argument("--summary", action="store_true")
    args = ap.parse_args()

    if args.summary:
        print(summarize(load_rows(args.path), args.path))
        return 0
    if args.source != "goose" or not args.dir:
        ap.error("--source goose with --dir is required (or --summary)")
    rows = _rows_from_goose_dir(args.dir, args.workflow, args.run_id, args.provider, args.model,
                                args.label)
    if not rows:
        print("no worker.jsonl found under %s — nothing recorded" % args.dir)
        return 0
    print("recorded %d run(s) -> %s" % (record_rows(rows, args.path), args.path))
    for r in rows:
        print("  %-14s calls=%-4s tokens=%-9s cost=%s%s" % (
            r["label"], r["model_calls"],
            r["total"] if r["total"] is not None else "?",
            ("$%.4f" % r["cost_usd"]) if r["cost_usd"] is not None else "not reported",
            "   UNRECORDED (worker killed)" if r["unrecorded"] else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
