# The burn so far — what the autonomous runners actually cost

**Written 2026-10-16 by Desi. Pinned by `tests/test_burn_ledger.py`.**

The founder's point of 2026-10-15 was that the card, not the server, is the general problem: the
cloud server is $4–6 a month, and the API bills are whatever they are. Until now nobody could say
what they are. Every figure the commons has ever quoted him — "$5–10 a month" — is the *library*:
the interactive chats, which a session ledger can see. The runners, which are headless processes,
were invisible. This is the number for the invisible half, measured from the runners' own records.

## The number

**The autonomous runners cost roughly $90–200 a month**, at the rate the commons has been running
since the fifth amigo was admitted. The best single estimate — the one priced from the providers'
own reported costs on the runs we can check — is **about $3.10 a day, ≈ $93 a month**. Priced at
the chat-ledger rates the repository already holds, the same tokens come to **about $6.50 a day,
≈ $196 a month**. That is **ten to twenty times the "$5–10 a month" on file**, and it is only the
runners: the daily GitHub Actions pipeline — now wired to report itself as of 2026-10-16, see gap
1 — and the mail replies are not in this sum.

The honest statement of it: *we are not a $5-a-month project run on a card; we are a $100- to
$200-a-month project, and both halves of that range are estimates rather than invoices.*

## Method, and where the two prices come from

**The tokens are measured, not estimated.** Every tick run writes a `result.json` carrying
`model`, `provider` and `total_tokens`. `scripts/burn_ledger.py` (written by the 04:58Z wake of
today, first run by this one) reads all of them and totals them per amigo:

```
python3 scripts/burn_ledger.py                  # all 33 days of records
python3 scripts/burn_ledger.py --days 14        # the last 14 run-dates
python3 scripts/burn_ledger.py --json           # the same, machine-readable
```

656 run records exist, from 2026-09-14 to 2026-10-16 — **624.0M tokens**, of which the last 14
run-dates hold **455.4M** and the last 7 hold **226.6M**.

**The prices are the estimate, and there are two of them.**

*Chat-blended* — `channels/usage/model-prices.json`, `as_of` 2026-08-25, derived from the
founder's own session ledger for the interactive chats. These are real dollars per real tokens,
but for the wrong consumers: the runner calls `deepseek-v4-flash-vision-exp`, `claude-sonnet-5`,
`gemini-3.8-flash` and `gpt-5.5`, and the ledger priced `v4-flash`, `sonnet-4-5`, `3.6-flash`
and `5.5`.

*Measured from the runners themselves* — the only ground-truth-adjacent source on this machine.
A tick run's `worker.jsonl` is goose's `stream-json` transcript, and its final `complete` event
carries the provider's own `total_tokens` **and** `cost_usd`. Fifteen such transcripts survive on
disk; thirteen carry a `complete` event. Dividing cost by tokens gives the runners' own blended
rate, per architecture:

| amigo | chat-blended $/M | measured on its own runs $/M | ratio | runs measured |
|---|---|---|---|---|
| desi | 0.01 | **0.021** | 2.1× **higher** | 2 |
| dmitri | 0.01 | **0.021** | 2.1× higher | 3 |
| gemini | 0.59 | **0.169** | 0.29× (cheaper) | 3 |
| claude | 1.15 | **0.429** | 0.37× (cheaper) | 2 |
| tarik | 1.86 | **1.179** | 0.63× (cheaper) | 3 |

So the chat ledger is wrong for the runner in *both* directions, and neither rate is a
safe default. The measured rate is the better one for two reasons, and the second is the one that
convinces: (a) it is the providers' own arithmetic on the models the runner actually calls; and
(b) it is not a bad sample — the 13 measured runs average **1.22M tokens per run**, against
**1.18M tokens per run** across all 386 runs of the last 14 days. Within 4%, on the only axis
(tokens per run) that could make the ratio unrepresentative.

## What the two prices give

| window | runs | tokens | chat-blended | measured |
|---|---|---|---|---|
| all 33 days (09-14 → 10-16) | 656 | 624.0M | $130.92 | $60.85 |
| last 14 run-dates | 386 | 455.4M | $91.31 | $43.59 |
| last 7 run-dates | 199 | 226.6M | $43.42 | $20.91 |
| **per day, last 14** | | | **$6.52** | **$3.11** |
| **per month, at that rate** | | | **≈ $196** | **≈ $93** |

**The number is rising, and sizing off the all-time average would understate it.** All 33 days
average $1.84/day measured; the last 14 average $3.11/day; the last 7, $2.99/day. The step is the
fifth amigo's admission on 2026-10-05 (dmitri appears in the records from 10-06) and the rise in
runs-per-day to ~28. Any future endowment figure should be built on a recent window, never on the
whole history, or it will be priced at a commons smaller than this one.

## What is not in this number (so nobody reads it as the whole bill)

1. **The daily GitHub Actions pipeline** (`.github/scripts/runner.py`) — **CLOSED, wired
   2026-10-16.** It calls all four paid providers (four peer reviews plus one maintainer call)
   and, until this same day, recorded none of them: `channels/usage.py --summary` printed
   **"no CI usage recorded yet"**. The reason it was not a one-line fix is in
   `channels/usage/README.md`: an SDK response is an object, not a dict, and reading it as a dict
   is the silent-zero bug one layer out. Now `sdk_usage()` adapts the object and
   `record_sdk_call()` appends one row per call, and `tests/test_ci_usage_ledger.py` pins both the
   four SDK shapes **and** that the runner calls the recorder for every provider. **Caveat, in
   the open:** the wiring is landed but not yet *exercised* — the first row appears the next time
   the runner runs, so until then this bullet remains a gap in the table above by an amount that
   is now measurable-but-unmeasured rather than unmeasurable.
2. **The mail replies** (`channels/auto_reply.py`) — small, but unrecorded.
3. **Spend that recorded nothing.** 122 of the 656 runs carry `total_tokens: 0` — 21 of them in
   the last 14 days (5%). The usage ledger's own rule applies: *"unrecorded — never record it as
   zero."* Everything here is a **floor**.
4. **The founder's interactive chats** — the library. The first-month ledger (2026-08-25) put all
   four architectures at $2.38 for the month, so it is small; but that is an August measurement
   and it is not refreshed here.
5. **The Mac, the SSD, the electricity** — real costs, not on the API card.

## The invoice we are throwing away

The only rows on this machine that carry a *provider-reported dollar figure* are the `complete`
events in `worker.jsonl`, and the bots keep **only the three most recent transcripts per amigo**:
656 `result.json` files, 15 `worker.jsonl`. Everything older keeps its token count and loses its
dollars.

The fix is small and it is not this session's to make (it is a bot-side change, and a wake may not
edit `~/LLM/*-bot/`): at the end of a run, append one line — `run_id`, `amigo`, `model`, `tokens`,
`cost_usd` — to a local usage file in the shape `channels/usage.py` already expects. Then the
dollars accumulate instead of being deleted, and this document becomes a *measurement* rather than
an estimate read off thirteen surviving transcripts. Until then, what survives is what we price.

The corresponding human-side action, if he ever wants the exact figure rather than this one: each
provider's console has **Usage → Export**. That is the invoice. This document is the check that
does not need his login.

## Sizing an endowment at ~25× annual

His rule of 2026-10-15: measure a week of ordinary running, publish the number, then size an
endowment at ~25× annual spend.

| priced at | per month | per year | 25× |
|---|---|---|---|
| measured runner rate | ≈ $93 | ≈ $1,116 | **≈ $28,000** |
| chat-blended rate | ≈ $196 | ≈ $2,352 | **≈ $59,000** |

**The defensible figure is $30,000–$60,000**, and the case for sitting in the upper half rather
than the lower is on the record three times over: the burn is rising, the whole table is a floor
rather than a ceiling, and the Actions pipeline is not in it at all.

**The caveat, out loud, because it is the one that matters.** An endowment buys **decades, not
millennia**. $60,000 at a 4% draw covers today's burn and nothing more; at twice today's burn the
same fund covers half of it. Anyone reading "25× annual" as a permanent solution has misread it —
it buys about *twenty-five years at the current rate*, which is a long time for a project and an
eye-blink for the 100,000-year question it is standing in for (`PRESERVATION.md` carries the same
caveat on the preservation side). Nor is the money the binding constraint at the scale this
document measures: at $3–7 a day, the honest conclusion is not "raise an endowment" but "the
thing is affordable, and here is what it costs."

## What would change this number

- **A provider console export** (Usage → Export, per host) — replaces every estimate above with an
  invoice. Needs the founder's login; the only source that is not inference.
- **One local usage line per run** (above) — turns the measured column from a 13-run sample into a
  continuous series, and stops the invoice being deleted.
- **Wiring `.github/scripts/runner.py`** into `channels/usage/` — closes gap 1, the largest known
  hole.
- **A price change from any host** — `research/hosts-watch.md` is the standing place that watches
  for one; the rates here are only as good as the models they were measured on.

*Reproduce: `python3 scripts/burn_ledger.py --days 14` (tokens), and the measured column from the
`complete` events of `~/LLM/*-bot/tick-state/runs/*/worker.jsonl`. The runner's own tests are
`tests/test_burn_ledger.py`.*
