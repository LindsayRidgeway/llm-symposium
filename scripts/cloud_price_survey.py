#!/usr/bin/env python3
"""What a rented server would cost the commons — the check behind
`research/2026-10-16-what-a-server-would-cost.md`.

Why this exists. The founder asked (2026-10-15) whether the commons could move off
his Mac; the answer was "about $4-6 a month," which was an estimate, not a quote.
A price is a moment, not a subscription — entry tiers move — so this file both
pins the figure that was fetched and re-fetches it on demand.

Design:
  * `QUOTES` is the pinned table: what was actually read, and when. It is the
    offline default, so this runs with no network and reports a dated fact.
  * `survey(plans)` is pure — it takes Vultr's plan JSON and returns the picks.
    Network lives only in `fetch_vultr()`. A test that needs someone else's API
    to be up is a test that fails for the wrong reason.
  * Vultr is the one provider whose prices answer a machine with no key
    (`/v2/plans`); AWS Lightsail's page is fetched by hand and pinned below.

Usage:
    python3 scripts/cloud_price_survey.py            # offline: print the pinned table
    python3 scripts/cloud_price_survey.py --fetch    # live: re-query Vultr and compare
    python3 scripts/cloud_price_survey.py --fetch --json
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request

VULTR_PLANS_URL = "https://api.vultr.com/v2/plans"

# What was actually read on 2026-10-16, and where. Keep the date honest: this is
# the offline answer, and a stale date is the whole reason the file exists.
FETCHED_ON = "2026-10-16"
QUOTES = [
    # provider, plan, vcpu, ram_mb, disk_gb, transfer, price_usd_mo, source
    ("Vultr", "vc2-1c-1gb", 1, 1024, 25, "1 TB", 5.00, "api.vultr.com/v2/plans"),
    ("Vultr", "vc2-1c-0.5gb", 1, 512, 10, "512 GB", 3.50, "api.vultr.com/v2/plans"),
    ("Vultr", "vc2-1c-0.5gb-v6 (IPv6 only)", 1, 512, 10, "512 GB", 2.50, "api.vultr.com/v2/plans"),
    ("AWS Lightsail", "Linux 512 MB", 2, 512, 20, "1 TB", 3.50, "aws.amazon.com/lightsail/pricing/"),
    ("AWS Lightsail", "Linux 1 GB", 2, 1024, 40, "2 TB", 5.00, "aws.amazon.com/lightsail/pricing/"),
]

# The two rows we actually care about when the live API answers.
INTERESTING = ("vc2-1c-1gb", "vc2-1c-0.5gb")


def survey(plans):
    """Pure: given Vultr's plan list, return the picks worth quoting.

    Returns a dict with:
      cheapest_ipv4  — the cheapest *payable* plan with a real IPv4 address: cost
                       above zero, not a `-v6` (IPv6-only) id. The promotional
                       `...-free` tier is excluded here and returned separately,
                       because it is a courtesy the provider can withdraw and it
                       ships no bandwidth — a fine tryout, a poor home.
      free_tier      — the $0 promotional plan, if the list has one.
      one_c_one_gb   — the 1 vCPU / 1 GB plan, the size this commons needs.
    Any value may be None if the list does not contain one.
    """
    def monthly(p):
        c = p.get("monthly_cost")
        return float(c) if c is not None else None

    def is_ipv4(p):
        # Vultr marks IPv6-only plans with a `-v6` suffix in the id.
        return "v6" not in str(p.get("id", ""))

    free_tier = next((p for p in plans if monthly(p) == 0.0), None)
    candidates = [p for p in plans
                  if monthly(p) is not None and monthly(p) > 0 and is_ipv4(p)]
    cheapest_ipv4 = min(candidates, key=monthly) if candidates else None
    one_c_one_gb = next((p for p in plans if p.get("id") in INTERESTING
                         and p.get("ram") == 1024), None)
    return {"cheapest_ipv4": cheapest_ipv4, "free_tier": free_tier,
            "one_c_one_gb": one_c_one_gb}


def fetch_vultr(timeout=30):
    """Live: Vultr's public plan list. No key needed."""
    req = urllib.request.Request(VULTR_PLANS_URL, headers={"User-Agent": "llm-symposium/cloud-price-survey"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r).get("plans", [])


def _row(p):
    return (p.get("id"), p.get("vcpu_count"), p.get("ram"), p.get("disk"),
            p.get("monthly_cost"), len(p.get("locations", [])))


def print_pinned():
    print(f"What a server costs — pinned quotes, read {FETCHED_ON}")
    print()
    print(f"{'provider':<14} {'plan':<28} {'vCPU':>4} {'RAM':>6} {'disk':>6} {'xfer':>7} {'$/mo':>6}")
    for prov, plan, vcpu, ram, disk, xfer, price, _src in QUOTES:
        print(f"{prov:<14} {plan:<28} {vcpu:>4} {str(ram)+'MB':>6} {str(disk)+'GB':>6} {xfer:>7} {price:>6.2f}")
    print()
    print("Not quoted (JavaScript pricing pages; check by hand, do not quote from memory):")
    print("  Hetzner Cloud, DigitalOcean, Oracle Cloud 'Always Free' (ARM, $0).")
    print()
    print("Re-fetch the machine-readable one:  python3 scripts/cloud_price_survey.py --fetch")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fetch", action="store_true", help="re-query Vultr's public plan API")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    if not args.fetch:
        print_pinned()
        return 0

    plans = fetch_vultr()
    picks = survey(plans)
    if args.json:
        print(json.dumps({k: (v and {kk: v.get(kk) for kk in
              ("id", "vcpu_count", "ram", "disk", "monthly_cost")}) for k, v in picks.items()}, indent=2))
        return 0
    print(f"Live from {VULTR_PLANS_URL}")
    for name, p in picks.items():
        if p is None:
            print(f"  {name}: not found")
        else:
            print(f"  {name}: {p['id']}  {p.get('vcpu_count')}c / {p.get('ram')}MB / "
                  f"{p.get('disk')}GB  ${p.get('monthly_cost')}/mo")
    print()
    print(f"Pinned table dates from {FETCHED_ON}; if these differ, update "
          f"research/2026-10-16-what-a-server-would-cost.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
