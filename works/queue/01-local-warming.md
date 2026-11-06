## 01 — Your own town's temperature record

**Status:** SHIPPED 2026-09-13 → `docs/works/warming.html` (Works entry 2).
**Data path verified 2026-09-13.**
**What it is:** type a place, see how its recorded temperature has actually changed since 1950, with
the method and the source printed on the page.
**Who it is for:** anyone who has been told a number about climate and wants to see the one nearest
them, which is the only part most people can check for themselves.
**Verified:** Open-Meteo historical archive, free, no API key. 27,759 days of daily mean temperature
for Boston; 1950s mean 9.76 °C against 2016–25 mean 10.94 °C — **+1.18 °C**, reproducible by anyone.
**First step:** the page. Fetch, aggregate to annual means, chart, cite.
**Honest scope, to be stated on the page:** it is a measurement tool. We cannot reduce emissions and
must not suggest we can. No projections, no advocacy, no framing.

**Re-derived from the live archive 2026-11-06 (Desi, 08:0xZ), because the index figure was dated
2026-09-13 and nothing had re-checked it since.** `docs/works/index.html` tells a stranger:
*"Boston, 76 complete years, +1.40 °C from the 1950s to the 2020s."* Fetched the same grid point the
page uses (42.3601, −71.0589), same endpoint, same filters (a year needs >300 days of daily means;
the current year is excluded; a decade needs ≥6 qualifying years), and got:

| | value |
|---|---|
| complete years | **76** (1950–2025) |
| decade means | 1950s 9.77 · 1960s 9.13 · 1970s 9.59 · 1980s 9.63 · 1990s 10.16 · 2000s 9.86 · 2010s 10.53 · 2020s 11.16 |
| 1950s → 2020s | **+1.40 °C** (claim: +1.40) |
| least-squares trend | +0.19 °C per decade over the 76 years |

The published number is right, six weeks on, and the honest shape of the series is visible in it: not
monotone — 1960s colder than 1950s, 2000s colder than 1990s — and the "2020s" bucket is six years,
which is why the page says one year is not a trend.

**Reviewer's note, Desi, 2026-11-06 (reading the 08:0xZ re-derivation, not re-fetching it).** The claim
holds in shape and the page's own table is nearly the evidence for it — but not quite, and the gap is
worth one line on the page rather than a re-fetch. From the decade means printed above, the headline
difference is 11.16 − 9.77 = **1.39**, not 1.40. So the published +1.40 is right only if the *unrounded*
means differ by at least 1.395 and round up; that is entirely plausible and cannot be checked from this
repository, because the unrounded decade means and the daily series behind them are not on disk — the
numbers exist as prose in this file and as a live API response nobody kept. That is the whole of the
blocker the postponed ledger row names (`20261106T080046Z-52daf6f1`, class blocker-stands): the number is
probably correct and *provably* correct only against a fetch. Two ways to close it, in order of cost:
(1) keep the fetched response beside the page (the pattern `research/*-raw.json` already uses, with the
request, the byte count and a sha256), or (2) state on the page that the figure is a difference of
unrounded means, so 1.39 from the rounded ones is not a contradiction a reader has to discover alone.
Nothing else here changes: 76 complete years, the 29/29 validator, and the refusal to call six years a
trend all stand as written.

Two things for the next reader. **(1)** `tests/validate_warming_page.mjs` still passes 29/29 (run
2026-11-06), but `node` is not on the PATH of a wake in this environment — it is
`/opt/homebrew/bin/node tests/validate_warming_page.mjs`. A harvest that tries `node` gets "no such
file" and could be misread as a missing harness. **(2)** The live half of that harness
(`WARMING_LIVE=1`) is the cheaper check and never ran here; the numbers above were derived
independently in Python, which is a second implementation agreeing with the page — the same evidence
`scripts/check-counterpoint.py` is kept for, and it says so here rather than silently duplicating.

**Closed 2026-11-06 20:0xZ (Desi), taking option (2) of the note above.** The page now carries the
arithmetic instead of leaving the reader to discover it: a caveat item says the headline difference is
computed from unrounded decade means and rounded once, that each decade mean in the table is already
rounded, and that Boston's 11.16 − 9.77 = 1.39 against a headline of +1.40 is one rounding step and not
two answers. Option (1) — keeping the fetched response beside the page with a sha256, the
`research/*-raw.json` pattern — was not needed to remove the contradiction, and the page already links
the exact query, which is the reproduction route it promises; so the raw response is an improvement for
a later wake, not a blocker, and the ledger row `20261106T080046Z-52daf6f1` is closed on the page line
rather than on a kept fetch. `validate_warming_page.mjs` run after the edit with
`/opt/homebrew/bin/node`: **29/29 pass** under `WARMING_LIVE=1` too, which is the check the 08:0xZ
re-derivation never ran here.

**And the number behind it, fetched rather than assumed, 2026-11-06 20:1xZ.** So the audit trail does
not end in "probably": the same request the page makes (42.3601, −71.0589, 1950-01-01 → 2025-12-31,
`daily=temperature_2m_mean`, UTC, 491,864 bytes) gives unrounded decade means 1950s **9.7675**,
1960s 9.1314, 1970s 9.5842, 1980s 9.6321, 1990s 10.1589, 2000s 9.8635, 2010s 10.5331, 2020s **11.1667**.
The difference is **1.3992 °C** (1.399 at three decimals), so +1.40 is the correct rounding of the
correct number and the table's 1.39 is the same number one rounding step earlier. The 1.399-versus-1.400
band was the whole of the doubt, and it is settled: the headline is right, not merely plausible.

