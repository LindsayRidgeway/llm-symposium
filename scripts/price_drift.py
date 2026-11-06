#!/usr/bin/env python3
# Owner: Dmitri
"""Which model each seat is priced as, against which model its runs actually name.

Why this exists. `scripts/burn_ledger.py` prices a run by the *seat* that ran it: Desi's tokens
are multiplied by Desi's blended rate, whoever's model was under them. On 2026-10-26 Desi's report
`channels/reports/2026-10-26-desi-two-ways-to-price-a-wake.md` measured the consequence and left it
as an unrepeatable paragraph: four of five seats were priced at a model version that no longer ran,
and one seat had spent 10.7M tokens on another architecture's model while paying its own rate. The
report's own sentence is the argument for this file — a dated price list with the wrong model names
on it is a guess with a date on it, and the layer that would notice did not exist.

This is that layer. It reads the same run records `burn_ledger.py` reads and the same price file it
prices from, and prints, per seat, the model the file names beside the models the runs name, with
the token share of each. It prices nothing and changes nothing: it is a drift detector, not a bill.

A run "matches" its seat's price when the priced model string is the run model or a `-`-separated
suffix of it, case-insensitively. That is deliberately strict: `v4-flash` matches `deepseek-v4-flash`
and does *not* match `deepseek-v4-flash-vision-exp`, because the run that used the experimental
variant is exactly the case worth seeing.

Usage:
    python3 scripts/price_drift.py              # every run record under ~/LLM
    python3 scripts/price_drift.py --days 7     # only run ids in the last 7 days
    python3 scripts/price_drift.py --json
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PRICES = REPO / "channels" / "usage" / "model-prices.json"

CURRENT = "current"      # every run matches the priced model
PARTIAL = "partial"      # some runs match, some name a different model
DRIFTED = "drifted"      # no run matches the priced model
UNPRICED = "unpriced"    # the seat has no rate row at all


def _burn_ledger():
    """Load `scripts/burn_ledger.py` by path, so the two instruments cannot count differently."""
    spec = importlib.util.spec_from_file_location("burn_ledger_for_drift",
                                                  REPO / "scripts" / "burn_ledger.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def load_prices(path: Path = PRICES) -> dict:
    """The `rates_usd_per_million` map, or an empty map when the file is absent or unreadable."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    rates = data.get("rates_usd_per_million") or {}
    return rates if isinstance(rates, dict) else {}


def matches(priced: str, ran: str) -> bool:
    """True when `priced` is the run model or a `-`-separated suffix of it."""
    priced = (priced or "").strip().lower()
    ran = (ran or "").strip().lower()
    if not priced or not ran:
        return False
    return ran == priced or ran.endswith("-" + priced)


def drift_rows(records: list[dict], rates: dict, days: int | None = None) -> list[dict]:
    """Pure: one row per seat, priced model against the models its runs actually named.

    `records` is `burn_ledger.collect()`'s list of `{amigo, model, tokens, date, run_id}` dicts.
    A seat with no rate row is reported as UNPRICED rather than priced at zero, so a gap in the
    file narrows the claim instead of hiding inside a total.
    """
    if days is not None:
        dates = sorted(r["date"] for r in records if r.get("date"))
        if dates:
            newest = dt.date(int(dates[-1][:4]), int(dates[-1][4:6]), int(dates[-1][6:8]))
            floor = (newest - dt.timedelta(days=days - 1)).strftime("%Y%m%d")
            records = [r for r in records if r.get("date") and r["date"] >= floor]

    per: dict[str, dict] = {}
    for r in records:
        who = r.get("amigo") or "?"
        row = per.setdefault(who, {"runs": 0, "tokens": 0, "models": {}})
        row["runs"] += 1
        row["tokens"] += int(r.get("tokens") or 0)
        model = r.get("model") or "?"
        row["models"][model] = row["models"].get(model, 0) + int(r.get("tokens") or 0)

    rows = []
    for who, row in sorted(per.items()):
        rate = rates.get(who) or {}
        priced = rate.get("model") or ""
        models = sorted(row["models"].items(), key=lambda kv: -kv[1])
        if not priced:
            status = UNPRICED
        else:
            hit = sum(t for m, t in models if matches(priced, m))
            miss = sum(t for m, t in models if not matches(priced, m))
            status = CURRENT if miss == 0 else (PARTIAL if hit else DRIFTED)
        rows.append({
            "amigo": who,
            "priced_as": priced,
            "rate_usd_per_million": rate.get("blended"),
            "status": status,
            "runs": row["runs"],
            "tokens": row["tokens"],
            "models": [{"model": m, "tokens": t,
                        "share": round(t / row["tokens"], 4) if row["tokens"] else 0.0,
                        "matches_price": matches(priced, m) if priced else None}
                       for m, t in models],
        })
    return rows


def render(rows: list[dict]) -> str:
    """The table a person reads: one seat per line, then the models underneath it."""
    out = [f"{'amigo':9} {'runs':>5} {'tokens(M)':>9}  {'status':8} priced as -> actually ran"]
    for r in rows:
        out.append(f"{r['amigo']:9} {r['runs']:>5} {r['tokens'] / 1e6:>9.1f}  {r['status']:8} "
                   f"{r['priced_as'] or '(no rate row)'}")
        for m in r["models"]:
            mark = " " if m["matches_price"] in (True, None) else "!"
            out.append(f"{'':27} {mark} {m['model']:<38} {m['share'] * 100:5.1f}% of tokens")
    bad = [r["amigo"] for r in rows if r["status"] in (PARTIAL, DRIFTED, UNPRICED)]
    if bad:
        out.append("")
        out.append(f"drifted from the price file: {', '.join(bad)} — the cost column prices each "
                   f"seat at its own rate whoever's model ran, so a ! is a token count priced by "
                   f"the wrong name, not a rounding error.")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=None, help="a different runs tree")
    ap.add_argument("--days", type=int, default=None, help="only run ids in the last N days")
    ap.add_argument("--json", action="store_true", help="machine-readable rows")
    args = ap.parse_args(argv)

    burn = _burn_ledger()
    root = args.root or burn.DEFAULT_ROOT
    rates = load_prices()
    rows = drift_rows(burn.collect(root), rates, days=args.days)
    if args.json:
        json.dump(rows, sys.stdout, indent=1)
        print()
    elif not rows:
        print("price_drift: no run records found under "
              f"{root} — nothing to compare, which is not the same as no drift")
    else:
        print(render(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
