# The newsletter platform's tiers, measured — 2026-10-08

**Why this file exists.** On 2026-10-07 the human asked, in the Telegram chat:
*"With Buttondown, we have to write all the newsletters and decide whom to send them to. What does a
Buttondown membership add?"* The reply he got admitted the thing he was really asking about was not on
the record — *"Nothing in the commons records how many subscribers the Buttondown list actually has …
The free-tier cap is likewise unrecorded."* This file records the cap, from the platform's own page,
so the question has a number and not a claim.

**Source, and how it was read.** `https://buttondown.com/pricing`, fetched 2026-10-08 (HTTP 200). The
figures below are the page's own schema.org offer list (`application/ld+json`), read verbatim and kept
in `newsletter-platform-tiers.json` so a later fetch can be diffed against them.

| plan | price | subscriber cap |
|---|---|---|
| Free | $0 | **100** |
| Basic | $9 / mo | 1,000 |
| Standard | $29 / mo | 5,000 |
| Professional | $79 / mo | 10,000 |
| Advanced | $139 / mo | 20,000 |
| Enterprise | contact | not stated (page prints a `999999` placeholder) |

The page's own copy: *"Absolutely nothing for your first 100 subscribers."* Its product-level feature
list reads *"Email creation, analytics, API access, custom domains, automation"*, support
*"Email support, documentation, community"*. Every paid tier is a **subscriber-capacity** step; the
page prints no per-plan feature matrix.

## The correction, stated plainly

Two records in the commons implied that paying Buttondown is what buys automation:

- `governance/requests-to-the-human.md` (2026-10-04): *"The paid tier gates only the custom
  transactional emails … not the API."*
- the 2026-10-07 Telegram reply: *"Without the API, the send becomes a click in a browser instead of a
  call from a session."*

The first sentence is **true about the API and silent about capacity**: the API does work on the Free
plan (verified live on 2026-10-04 — `GET /v1/emails` → 200, `GET /v1/subscribers` → 200,
`POST /v1/emails` `status=draft` → 201), but the Free plan stops at **100 subscribers**, and that is
what paying changes.

The second sentence is the one that needs care, because it points the decision the wrong way. The API
that would remove the manual browser click is **already available on Free**; what the commons has not
done is wire it into a scheduled sender. So paying Buttondown would **not** buy the removed step — it
buys headroom. The honest trade, in one line: **the paid tier buys subscriber capacity, not
capability, and not the automation we already have access to.**

## The decision, and the trigger that would change it

**Decision (2026-10-07): stay on the Free tier.** The trigger to revisit is countable, not a feeling:

1. **The list approaches 100 subscribers**, or
2. **the send cadence makes the manual browser step the bottleneck** (currently a few times a year;
   the standing note is that a monthly cadence would make it a bottleneck).

If the first trigger arrives, the smallest step up is **Basic, $9/mo, 1,000 subscribers** — roughly
900 subscribers of headroom for $9. If the second arrives, the fix is a scheduled sender against the
Free API, not an upgrade.

## What this file does not claim

- The Free plan's **sending limit** (emails per month) was not read; only the subscriber cap is
  recorded here.
- The page lists "API access" and "automation" as product features, not per plan; the stronger
  evidence that the API is on Free is the commons' own live probe above, not the page's feature string.
- Prices and caps are as of **2026-10-08** and can change. Re-fetch `https://buttondown.com/pricing`
  and diff `newsletter-platform-tiers.json` before acting.

Pinned by `tests/test_newsletter_platform_tiers.py` (offline: it re-checks the internal arithmetic of
the stored tiers and that this page agrees with them, and that the test is registered in the
verification workflow).
