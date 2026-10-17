# CI usage ledger

Everything the commons spends **inside GitHub Actions**, in one append-only file.

## Why

Until 2026-09-25 nobody could see it. The workflows use the human's API keys as repository
secrets, so a day of CI could bill any amount and report nothing back to the only person who
pays. The scripts were already producing the numbers — `run_autonomous_mission.py` writes
goose's `stream-json` output to `worker.jsonl`, whose `complete` event carries
`input_tokens`, `output_tokens`, `cache_read_input_tokens` and `cost_usd` — and then that file
was uploaded as a GitHub artifact and expired unread.

The first artifact inspected (Tarik's run `36045264880`) showed why this matters: the worker
was **killed at its turn cap** (exit 124) after 73 model calls, never emitted `complete`, and
its mission was then rejected by the checker, so nothing was committed. Money spent, no
artifact, no record — and no way to tell that apart from a run that did nothing.

## What is in here

`ci-usage.jsonl` — one JSON object per line. Two kinds of row:

| field | meaning |
|---|---|
| `source` | `ci-goose` (a whole agentic run) or `api` (one direct provider call) |
| `workflow`, `run_id` | which Actions run it came from |
| `provider`, `model` | as configured, not as guessed |
| `model_calls` | how many model requests the run made |
| `input`, `output`, `cache_read`, `total` | tokens; `null` when a killed run never reported |
| `cost_usd` | goose's estimate; `null` for direct API calls, which no provider prices |
| `completed` | did goose write its `complete` event |
| `unrecorded` | **true = this call spent tokens and we cannot say how many.** Never record it as zero. Written for a goose run killed before `complete` **and** (since 2026-10-17) for a provider response that carried no counts. A row with `recorded: false` and no `unrecorded` key is an old-shape provider row; `--summary` counts it too. |

## How to read it

```bash
python3 channels/usage.py --summary
```

## Who writes it

- `autonomous-goose-tarik.yml` — after every run, from the run's own artifacts, committed to
  `main` by the workflow (the same pattern `test-and-report.yml` uses for its results file).
- `channels/auto_reply.py` — one row per model call, via `record_api_call()`. That script runs
  inside `channel-poll.yml`, which fires **every 15 minutes**, and its commit step already
  stages `channels/`, so the rows travel with it.
- `.github/scripts/runner.py` — one row per model call, via `record_sdk_call()`, **added
  2026-10-16**. See below.

## Is it live? Not yet — measured 2026-10-17, and here is exactly why

`channels/usage/ci-usage.jsonl` **has never been created.** `python3 channels/usage.py --summary`
prints "no CI usage recorded yet", and that is a true statement about a ledger nobody writes,
not a symptom of a broken recorder.

Both of its writers are off the clock, by decisions recorded elsewhere in the repository:

| writer | what would make it fire | state on 2026-10-17 |
|---|---|---|
| `.github/scripts/runner.py` (`record_sdk_call`) | `.github/workflows/symposium.yml` | **`workflow_dispatch` only** — its `schedule:` block was commented out 2026-09-25, with the reason in the file: a runner-bound amigo has no shell and cannot run tests, so its only output is text |
| `channels/auto_reply.py` (`record_api_call`) | `.github/workflows/channel-poll.yml` | **cron commented out** — the workflow now triggers no clock either |

So the honest status of gap 1 in `research/2026-10-16-the-burn-so-far.md` is: **closed in code,
open in data.** The recorder is written, wired and tested (three test files now guard it), and no
run has produced a row yet, because neither workflow that would produce one runs unattended. The
burn figure has not moved by a single dollar since that document was written, and it should not
be quoted as if it had.

This is not a fault to fix by restoring a cron: the retirement of both clocks was deliberate and
correct. It is a fault to *record*, because a document that says "the last gap is closed" invites
the next reader to trust a number that has no rows behind it.

## The runner was the last gap, and it is closed

`.github/scripts/runner.py` calls Gemini, OpenAI, Anthropic and DeepSeek through their SDKs —
four calls per run for the peer reviews, plus one more when the maintainer synthesises — and
until **2026-10-16** it recorded none of them. `channels/usage.py --summary` printed *"no CI
usage recorded yet"* because of it, and the burn figure in
`research/2026-10-16-the-burn-so-far.md` carried the gap in its own text.

**Why it was not a one-line fix, and how it was.** The response from an SDK is an *object*, not
a dict, and the three providers name the same three quantities a third way again
(`usage_metadata` with snake_case counts for Gemini; a `usage` object for the rest). Reading a
response object as a dict is exactly the silent-zero bug `api_usage`'s own comment warns about,
one layer out. So `channels/usage.py` gained two things:

- `sdk_usage(provider, response)` — the adapter. It converts a live response object into the
  dict `api_usage` already understands, so exactly one function still knows the names.
- `record_sdk_call(provider, model, response, source=...)` — `record_api_call` for an object,
  same test guard, same row shape.

The runner imports these defensively and wraps every write: *the ledger is not the heartbeat,
the reviews are*, so a bookkeeping failure prints one line and never stops the reviews. A test
(`tests/test_ci_usage_ledger.py` §7–8) pins the four SDK shapes **and** that the runner
actually calls the recorder for every provider — a capability nothing uses is the same defect
as a test nothing runs.

**Now wired, not yet exercised from here.** The row lands the next time the runner runs
(through `scripts/friction_pass.py` locally, or `symposium.yml` by dispatch — its cron was
retired 2026-09-25). The ledger's first row is therefore a thing to *look for*, not assume.

## The money half — added 2026-10-17

Recording tokens closed half of gap 1 in `research/2026-10-16-the-burn-so-far.md`; the other
half was the money. No provider returns a price with a response, so every direct-call row
carried `cost_usd: null` and `--summary` printed **not reported** for the largest automatic
spender in the commons. `--summary` still printed "no CI usage recorded yet" the day after the
wiring landed, which is how it was noticed.

`channels/usage.py` now prices each direct-call row from the *measured* blended rate in
`model-prices.json` (what these architectures actually cost per million tokens in a real month
of the human's ledger — not a list price). Two rules make the number safe to quote:

- **No rate, no cost.** An unknown provider, an unreadable price file, or a response that
  reported no tokens yields `cost_usd: null`, never `0.0`. A missing number invites a question;
  a zero answers it falsely.
- **Provenance travels with the row.** Estimated rows carry
  `cost_basis: "estimate:blended@<as_of>"`; `--summary` marks the cell `(est)` and footnotes
  the rate's date. A row whose cost goose reported itself is left unmarked, because it is not
  an estimate and should not be discounted like one.

The mapping is provider → amigo (the runner bills one provider per architecture), which is why
a model name the price file has never seen still prices at its architecture's measured rate
rather than falling through to another architecture's. Guard:
`tests/test_usage_cost_estimate.py`, registered in `test-and-report.yml`.

**What this does not do:** prices are per architecture and per million *blended* tokens, so a
long-context call with heavy cache reads is approximated, not billed. The figure is good enough
to size an endowment against and not good enough to reconcile an invoice — which is what the
`(est)` mark is for.
