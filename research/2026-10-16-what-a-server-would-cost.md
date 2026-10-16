# What a server would cost — the real quotes

*Written 2026-10-16 by Desi (wake `20261016T025842Z-6f893f7b`). The companion check is
`scripts/cloud_price_survey.py`.*

## Why this file exists

On 2026-10-15 the founder asked whether the commons could move off his Mac onto a rented
server. The answer given that day was "doable, cheap — roughly $4–6 a month." **That was an
estimate, not a quote.** The to-do item that follows from it says, in the founder's own
instruction, *"price it for real … do not ask him to approve a guess."* So this file replaces
the estimate with numbers taken from the providers' own pages and APIs on 2026-10-16, each
with its source, so the figure can be checked rather than believed.

The estimate turned out to be **right** — the entry tier is $3.50–$5 a month, quoted below. The
point of writing it down is not that the number moved; it is that "about five dollars" with no
source is a guess, and a guess is what he told us not to bring him.

## What we actually need — so the cheapest tier is a decision, not a hope

If the box has to run more than we are pricing for, the quote is worthless. This is the
workload, measured from the repository rather than imagined:

- **What runs.** Five bot processes (Claude, Desi, Dmitri, Gemini, Tarik) plus the landing and
  test scripts. A wake is a Python process that calls a language-model API over HTTPS and does
  `git`; the daily jobs are short bursts. The work is **network-bound, not CPU-bound** — the
  waiting is for someone else's server.
- **Disk.** This repository is **150 MB**, of which **102 MB is `.git`**. A second working copy
  (the checkout a body runs in) plus the OS fits inside 20 GB with room to spare.
- **Memory.** Minutes of wall clock and tens of megabytes per wake; nothing here holds a large
  working set. 512 MB runs one body; 1 GB is comfortable for all five.
- **Network.** Outbound only: to the four model providers, to Telegram (long-poll), and to
  GitHub. There is **no inbound service** — no web server, nothing the world connects *to* — so
  no firewall rule, no domain, no TLS certificate is required for the bots themselves. Transfer
  used is small (API calls and `git` pushes are text).

**Conclusion:** 1 vCPU / 1 GB RAM / 25 GB disk is comfortable, and 512 MB is enough for the
"prove one body runs there for a week" test the plan calls for. The cheapest tier is not a
compromise; it is the right size.

## The quotes, fetched 2026-10-16

Prices are USD per month, in the provider's own words. Only what was actually fetched is in
this table.

| Provider | Plan | vCPU | RAM | Disk | Transfer | **Price/mo** | Source |
|---|---|---|---|---|---|---|---|
| **Vultr** | `vc2-1c-1gb` | 1 | 1 GB | 25 GB | 1 TB | **$5.00** | `api.vultr.com/v2/plans` (live, no key) |
| **Vultr** | `vc2-1c-0.5gb` | 1 | 512 MB | 10 GB | 512 GB | **$3.50** | `api.vultr.com/v2/plans` (live, no key) |
| **Vultr** | `vc2-1c-0.5gb-v6` | 1 | 512 MB | 10 GB | 512 GB | **$2.50** | same — **IPv6-only**, no IPv4 |
| **AWS Lightsail** | Linux, 512 MB | 2 | 512 MB | 20 GB SSD | 1 TB | **$3.50** | `aws.amazon.com/lightsail/pricing/` |
| **AWS Lightsail** | Linux, 1 GB | 2 | 1 GB | 40 GB SSD | 2 TB | **$5.00** | `aws.amazon.com/lightsail/pricing/` |

Vultr also lists a **$0 plan** (`vc2-1c-0.5gb-free`: 1 vCPU / 512 MB / 10 GB, 3 regions) — but
its transfer allowance is **0 GB**, so it is a promotional tryout, not a home. It is exactly the
right thing to put a one-body, one-week proof on, and the wrong thing to move the commons to.

Two more providers belong on this list and are **deliberately not quoted**, because their
pricing pages did not yield a figure to a direct fetch on 2026-10-16 (the pages render their
prices in JavaScript, and a curl gets an empty shell). They are named so the gap is visible and
not filled from memory:

- **Hetzner Cloud** — historically the cheapest of the reputable European options. **Check by
  hand; do not quote a number from memory.**
- **DigitalOcean** — entry droplet in the same $5–$6 band in the past. **Check by hand.**
- **Oracle Cloud "Always Free"** — an ARM instance (Ampere A1, up to 4 cores / 24 GB) at **$0**,
  which would make the server cost nothing at all. Two honest caveats: signup wants a card and
  sometimes refuses, and a free tier is a courtesy the provider can reclaim, so it is a fine
  place to *prove one body runs for a week*, and a poor place to make the commons' only home.

## The recommendation, and the price of it

**$5 a month, $60 a year** — Vultr `vc2-1c-1gb` (1 vCPU / 1 GB / 25 GB, 1 TB transfer, IPv4,
31 regions) or AWS Lightsail's 1 GB plan at the same $5. That is the real, sourced figure the
earlier estimate was reaching for. The cheapest IPv4 tier at Vultr is $3.50; the difference
buys headroom, not a feature, and either is defensible.

The caveats are part of the quote, not a footnote:

- **This removes the Mac, not the card.** A rented server replaces the hardware; it does not
  touch the API bills, which are the larger number and the ones nobody has measured yet. The
  server is the cheap half of "the commons outlives this laptop."
- **Keep the account's password and second factor off the rented box.** The box may push; it
  must never administer. (Same rule stated in the provider-death handover page.)
- **Keep Dawn and the two rovers on the Mac** — they need the founder's hardware and cannot move.
- **Prove one body runs there for a week before moving the rest.** The 512 MB tier is enough for
  exactly that test.
- **A price is a moment, not a subscription.** Entry tiers move (both DigitalOcean's and
  Lightsail's have stepped up over the years). Re-run `scripts/cloud_price_survey.py` before
  relying on this figure.
- **An endowment sized on this buys decades, not millennia** — the same caveat as in
  `PRESERVATION.md`. Renting a server is a recurring cost, not a purchase.

## Re-checking it

    python3 scripts/cloud_price_survey.py            # offline: print the pinned table and its date
    python3 scripts/cloud_price_survey.py --fetch    # live: re-query Vultr's public plan list

The script re-queries the one source that answers a machine without a key (Vultr's plan API) and
reports the cheapest IPv4 plan and the 1c/1GB plan. The test is
`tests/test_cloud_price_survey.py`.

## What is still owed before money changes hands

1. **A real burn figure.** The server is $5/mo; the APIs are the unknown. Measuring a week of
   ordinary running is a separate to-do item and must come before anyone sizes an endowment.
2. **The founder's yes.** A spend is the half only his hands can do; file it as a REQUEST with
   this figure attached, not before.
3. **The week's proof.** Rent the 512 MB tier, run one body on it for a week, then decide.
