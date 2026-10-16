#!/usr/bin/env python3
# Owner: Desi
"""The burn — what the autonomous runner actually spends, measured from its own run records.

Why this exists. `insights/compute-economics-of-the-commons.md` (the first month's ledger)
records a cost per million tokens for each architecture, but ends on a hole it names itself:
*"The autonomous runner's costs are invisible in session ledgers... A future audit should
instrument the runner itself if it wants true total cost of ownership."* The interactive chat
ledger cannot see a wake; a wake is a headless process. So every figure the commons has quoted
to the founder ("$5-10 a month") has been the *library* — the chats — with the runner missing.

This file is that audit. Every tick run the bots write ends with a `result.json` carrying
`model`, `provider` and `total_tokens`. Summing `total_tokens` is the billed token count for
that run (an agentic run re-sends its context every turn, so the field is large by design), and
pricing it at the blended rates already on file turns the invisible half of the bill into a
number with a date on it.

Honest limits, stated here rather than discovered later:
  * The rates are the *blended* $/1M from `channels/usage/model-prices.json` (measured from the
    founder's interactive session ledger, `as_of` dated). Applying a chat-blended rate to a
    runner's tokens is an estimate, not an invoice: the runner uses slightly different model
    versions (e.g. `deepseek-v4-flash-vision-exp`, `claude-sonnet-5`) than the ledger priced.
  * Only the run records are counted. The daily GitHub Actions pipeline and the mail replies are
    not in this sum; if anything, the true burn is higher.
  * A provider's own console (Usage → Export) is the only ground truth, and it needs the human's
    login. This file is the check we can run without him.

Usage:
    python3 scripts/burn_ledger.py                 # all run records under ~/LLM
    python3 scripts/burn_ledger.py --days 7        # the last 7 days of run-id dates
    python3 scripts/burn_ledger.py --root DIR      # a different runs tree
    python3 scripts/burn_ledger.py --json
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import sys
from pathlib import Path

DEFAULT_ROOT = Path.home() / "LLM"
PRICES = Path(__file__).resolve().parent.parent / "channels" / "usage" / "model-prices.json"

# run dirs live at <root>/<amigo>-bot/tick-state/runs/<run_id>/result.json
RUN_GLOB = "*-bot/tick-state/runs/*/result.json"


def amigo_of(path: str) -> str | None:
    """The amigo that owns a run, read from the `<amigo>-bot` component of its path."""
    parts = Path(path).parts
    for part in reversed(parts):
        if part.endswith("-bot"):
            return part[: -len("-bot")]
    return None


def run_date(run_id: str) -> str | None:
    """The YYYYMMDD date a run id starts with, or None if it does not carry one."""
    head = str(run_id)[:8]
    return head if len(head) == 8 and head.isdigit() else None


def collect(root: Path = DEFAULT_ROOT) -> list[dict]:
    """Every run record under `root` that carries a token count. Network-free, read-only."""
    records = []
    for path in glob.glob(str(root / RUN_GLOB)):
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        amigo = amigo_of(path)
        if amigo is None:
            continue
        records.append({
            "amigo": amigo,
            "run_id": str(data.get("run_id", "")),
            "date": run_date(data.get("run_id", "")),
            "model": data.get("model") or "?",
            "tokens": int(data.get("total_tokens") or 0),
        })
    return records


def summarize(records: list[dict], rates: dict, days: int | None = None) -> dict:
    """Pure: total the tokens per amigo and price them.

    `rates` is the `rates_usd_per_million` map from model-prices.json. An amigo with no rate is
    still counted in tokens and reported with `cost: None`, so a missing price narrows the claim
    instead of silently pricing someone at zero.
    """
    if days is not None:
        dates = sorted(r["date"] for r in records if r["date"])
        if dates:
            newest = dt.date(int(dates[-1][:4]), int(dates[-1][4:6]), int(dates[-1][6:8]))
            floor = (newest - dt.timedelta(days=days - 1)).strftime("%Y%m%d")
            records = [r for r in records if r["date"] and r["date"] >= floor]

    per: dict[str, dict] = {}
    for r in records:
        who = r["amigo"]
        row = per.setdefault(who, {"runs": 0, "tokens": 0, "models": {}})
        row["runs"] += 1
        row["tokens"] += r["tokens"]
        row["models"][r["model"]] = row["models"].get(r["model"], 0) + r["tokens"]

    for who, row in per.items():
        rate = rates.get(who, {}).get("blended")
        row["rate_usd_per_million"] = rate
        row["cost_usd"] = round(row["tokens"] / 1e6 * rate, 2) if rate is not None else None

    total_tokens = sum(row["tokens"] for row in per.values())
    known = [(row["cost_usd"], row["tokens"]) for row in per.values() if row["cost_usd"] is not None]
    total_cost = round(sum(c for c, _ in known), 2)
    priced_tokens = sum(t for _, t in known)
    return {
        "per_amigo": per,
        "total_runs": sum(row["runs"] for row in per.values()),
        "total_tokens": total_tokens,
        "total_cost_usd": total_cost,
        "tokens_without_a_price": total_tokens - priced_tokens,
        "window_days": days,
    }


def load_rates(path: Path = PRICES) -> dict:
    return json.loads(path.read_text(encoding="utf-8")).get("rates_usd_per_million", {})


def render(summary: dict) -> str:
    out = [f"{'amigo':8s} {'runs':>5s} {'tokens(M)':>10s} {'rate$/M':>8s} {'cost$':>9s}"]
    for who in sorted(summary["per_amigo"], key=lambda w: -summary["per_amigo"][w]["tokens"]):
        row = summary["per_amigo"][who]
        rate = row["rate_usd_per_million"]
        out.append(
            f"{who:8s} {row['runs']:5d} {row['tokens']/1e6:10.1f} "
            f"{(rate if rate is not None else float('nan')):8.2f} {row['cost_usd']:9.2f}")
    out.append(f"{'TOTAL':8s} {summary['total_runs']:5d} "
               f"{summary['total_tokens']/1e6:10.1f} {'':>8s} {summary['total_cost_usd']:9.2f}")
    if summary["tokens_without_a_price"]:
        out.append(f"  (+{summary['tokens_without_a_price']/1e6:.1f}M tokens have no price on file "
                   f"and are not in the dollar total)")
    if summary["window_days"]:
        cost = summary["total_cost_usd"]
        per_day = cost / summary["window_days"]
        out.append(f"  window: last {summary['window_days']} days of run dates "
                   f"= ${per_day:.2f}/day, ~${per_day*30:.0f}/month at this rate")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--days", type=int, default=None, help="last N days of run-id dates")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    records = collect(args.root)
    summary = summarize(records, load_rates(), days=args.days)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(render(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
