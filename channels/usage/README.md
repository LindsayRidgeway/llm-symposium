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
| `unrecorded` | **true = this run spent tokens and we cannot say how many.** Never record it as zero. |

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
