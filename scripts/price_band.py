#!/usr/bin/env python3
# Owner: Desi
"""The monthly price band — who is cheap *this month*, so assignment never hardcodes it.

Why this exists (2026-10-09, the human's suggestion in the Telegram session where review
assignment was designed). The reviewer-assignment rule has two branches: name the best-suited
amigo, or draw at random among the least expensive. The second branch needs to know who is least
expensive — and the wrong way to give it that is a constant in the code, because "assign to the
cheapest" freezes today's price list into the program and a price change silently makes the rule
wrong. His fix, adopted as given: one job a month produces the list, and every assignment after
that reads the file. The lookup stops being a per-turn cost and becomes a monthly one.

Three properties, all of them his, and all of them the reason this is a file rather than a function:

    it names a BAND, not a winner   — the single cheapest collapses the random branch to one
                                      amigo, and a branch with one member is not a random branch
    it is DATED                     — a stale list must be visible, not silently authoritative
    it is written once a month      — the pool stays current; the decision stays frozen

Input:  `channels/usage/model-prices.json` — per-amigo blended $/1M tokens, hand-maintained, with
        its own `as_of` date and the source it came from.
Output: `channels/usage/price-band-YYYY-MM.json` — the band, the rule, the rates, both dates, and a
        staleness note when the prices behind it are old.

CLI:
    python3 scripts/price_band.py --write     # write this month's band (idempotent)
    python3 scripts/price_band.py --show      # read the newest band and explain it
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
USAGE = REPO / "channels" / "usage"
PRICES = USAGE / "model-prices.json"

# How far above the cheapest an amigo may be and still be in the band. 2x is chosen so the cheap
# tier stays a tier: if a provider halves its prices tomorrow, the band widens without anyone
# editing this file, and if a cheap model disappears the band narrows by itself.
BAND_MULTIPLIER = 2.0

# Older than this and the band says so in plain words. Prices are usually stable for months; the
# number exists so that "stable" is a claim with a date on it rather than an assumption.
STALE_DAYS = 120


def load_prices(path: Path = PRICES) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    rates = data.get("rates_usd_per_million") or {}
    if not rates:
        raise ValueError(f"{path} names no rates")
    for who, entry in rates.items():
        if not isinstance(entry.get("blended"), (int, float)):
            raise ValueError(f"{path}: {who} has no numeric blended rate")
    return data


def build(data: dict, today: dt.date | None = None) -> dict:
    """The band: everyone within BAND_MULTIPLIER of the cheapest, plus the dates and the rule."""
    today = today or dt.date.today()
    rates = data["rates_usd_per_million"]
    cheapest = min(rates, key=lambda who: rates[who]["blended"])
    floor = rates[cheapest]["blended"]
    band = sorted(who for who in rates if rates[who]["blended"] <= floor * BAND_MULTIPLIER)
    price_date = str(data.get("as_of", "?"))
    try:
        age = (today - dt.date.fromisoformat(price_date)).days
    except ValueError:
        age = -1
    note = ("prices are current" if 0 <= age <= STALE_DAYS else
            f"PRICES ARE STALE: the rates behind this band are {age} days old ({price_date}); "
            f"refresh channels/usage/model-prices.json before trusting the band")
    return {
        "as_of": price_date,
        "written": today.isoformat(),
        "rule": f"within {BAND_MULTIPLIER:g}x of the cheapest blended rate",
        "cheapest": cheapest,
        "band": band,
        "rates_usd_per_million": {who: rates[who]["blended"] for who in sorted(rates)},
        "basis": data.get("basis", ""),
        "note": note,
    }


def path_for(today: dt.date | None = None, usage: Path = USAGE) -> Path:
    today = today or dt.date.today()
    return usage / f"price-band-{today:%Y-%m}.json"


def write(usage: Path = USAGE, today: dt.date | None = None) -> Path:
    today = today or dt.date.today()
    out = path_for(today, usage)
    out.write_text(json.dumps(build(load_prices(usage / "model-prices.json"), today),
                             indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def newest(usage: Path = USAGE) -> Path | None:
    files = sorted(usage.glob("price-band-*.json"))
    return files[-1] if files else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="write this month's band")
    ap.add_argument("--show", action="store_true", help="read the newest band and explain it")
    args = ap.parse_args()

    if args.write or not args.show:
        out = write()
        band = build(load_prices())
        print(f"price_band: wrote {out.relative_to(REPO)} — band {', '.join(band['band'])} "
              f"(cheapest {band['cheapest']}, {band['rule']})")
        if "STALE" in band["note"]:
            print(f"price_band: WARNING — {band['note']}")
        return 0

    latest = newest()
    if latest is None:
        print("price_band: no band has been written yet; run --write")
        return 0
    data = json.loads(latest.read_text(encoding="utf-8"))
    print(f"price_band: {latest.relative_to(REPO)} (written {data['written']}, prices as of "
          f"{data['as_of']})")
    print(f"  rule:   {data['rule']}")
    print(f"  band:   {', '.join(data['band'])}")
    for who, rate in data["rates_usd_per_million"].items():
        mark = " ←" if who in data["band"] else ""
        print(f"    {who:7s} ${rate:.2f}/M{mark}")
    print(f"  note:   {data['note']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
