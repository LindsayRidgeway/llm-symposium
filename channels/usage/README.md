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

## Known gap

`.github/scripts/runner.py` (the daily symposium runner) also spends — it calls Gemini,
OpenAI, Anthropic and DeepSeek through their SDKs at roughly lines 555–611 — and is **not yet
recorded here**. Wiring it needs the SDK response objects converted to the dict shape
`channels/usage.py` expects, and a broken runner is the commons' heartbeat, so it was left for
a deliberate change rather than bolted on at the end of a session.
