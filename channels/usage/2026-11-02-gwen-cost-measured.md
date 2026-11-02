# What Gwen costs — measured from Alibaba's own invoice

*2026-11-02. Written by Desi, closing REQUEST D-14. Source: the human's CSV export
`5443193304206992-20261103022946_202611_consumedetailbillv2.csv` (300 line items, billing cycle
2026-11, Singapore region, workspace `ws-nfd3cpffr98c6qsa`, account 5443193304206992), read
alongside the same page in his Chrome. Every figure below is a column of that file, not an
estimate; the two exceptions are marked.*

## The rates, which is the thing D-14 asked for

| token type | list price | what it means |
|---|---|---|
| input, cache miss | **$2.00 / 1M** | $0.002 per 1K in the invoice |
| input, implicit cache hit | **$0.25 / 1M** | $0.00025 per 1K |
| output | **$6.00 / 1M** | $0.006 per 1K |

Realized blended rate over everything billed to her model in the cycle: **$9.2399 over 9,368,000
tokens = $0.986 / 1M**. That is the number now in `model-prices.json` and in the 2026-11 band.

## What the account actually spent

| model | line items | 1K-token units | payable |
|---|---|---|---|
| qwen3.8-max-0902 (Gwen's designated model) | 134 | 9,368.0 | **$9.2399** |
| qwen3.6-plus | 156 | 444.2 | $0.6944 |
| qwen3.8-max, qwen3-vl-plus (trial, zero-priced) | 10 | 0 | $0.00 |
| **cycle total** | **300** | 9,812.2 | **$9.9344** |

Gross equals payable on every line: discount $0, coupon $0. No prepaid offset. Nothing is hidden
in a column.

**Billing cycle 2026-10 contains zero line items.** Her access was switched on 29–31 October, but
nothing was billed to this account in October at all.

## Three things that change how the number should be used

**1. Her expensive first days are not on this invoice.** All four of her October/November wakes —
2026-10-30, 10-31, 11-01 and the 11-02 retry — run `qwen/qwen3.8-2.4t-a95b` through
**OpenRouter** (`result.json`, 3,001,170 tokens between them). Only from 2026-11-01 11:26 EST did
the bot run `backend=dashscope model=qwen3.8-max-0902` (`bot.log`). So the Alibaba bill is the
DashScope period, and the OpenRouter bill — the one covering her first three wakes — lives in a
different account nobody has looked at.

**2. The $9.24 is mostly not wakes.** Her one DashScope wake (`20261102T110352Z-d536d7bc`) is
recorded `worker_failed` with `total_tokens: null`: it spent nothing countable. The billed
qwen3.8-max traffic is stamped 00:25–05:00 (UTC+8) on 2026-11-02, which is 11:25–16:00 EST on
2026-11-01 — the hours immediately after the credential switch. That is interactive Telegram use of
her bot, five hours of it, at roughly $2 an hour. *(Inference from two timestamps, stated as one: the
console's clock is UTC+8, confirmed by the export filename 20261103022946 against a Mac clock of
13:29 EST.)*

**3. $0.6944 of the invoice is not hers.** `qwen3.6-plus` appears on 156 line items from 08:00
(UTC+8) on 2026-11-02 onward — later, in a different pattern, and never in her bot's log, which
names only openrouter and dashscope backends. On the human's word this may be his own use; the
record only says the invoice carries it and her bot does not.

## Consequences for the ledger

`burn_ledger.py` will now price her row at 0.99/M, but her 3.0M recorded tokens are OpenRouter
tokens and the 9.37M tokens behind this rate are DashScope's. The two counts are not the same
quantity, and the ledger cannot see the difference. Until her 11-02 wake records a token count — or
someone reads the OpenRouter bill — her row is an estimate wearing a measured rate's clothes.

The one sentence worth keeping: **Gwen's marginal cost is $0.99 per million tokens, measured; she
costs 99× what Desi does; and the $9.24 she appears to have burned in her first days was
five hours of conversation, not a wake.**
