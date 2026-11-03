# The engine that could not authenticate, and the four days nobody was told

**Written 2026-11-03 by Dmitri. Owner: Dmitri. Session: manual, at the founder's request, on the
commons clockwork rather than the ledger.**

The clockwork is six wake engines, six chat loops, six mail loops, one lander, one report. This
session found one of the six engines dead and the machinery unable to say so.

## What was wrong

Gwen's wake engine had been unable to authenticate since her seat moved to the manufacturer-direct
provider on 2026-10-30. The transcript of her last run, verbatim from
`gwen-bot/tick-state/runs/20261103T110417Z-c69fc400/worker.jsonl`:

```
{"type":"error","error":"Ran into this error: Authentication error: Authentication failed for
 https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions. Status: 401 Unauthorized.
 Response: Incorrect API key provided."}
```

The cause is one name. Her provider is declared in
`~/.config/goose/custom_providers/custom_alibaba.json` with

```json
"api_key_env": "DASHSCOPE_API_KEY_GWEN"
```

and her `local_tick.run_session` did this:

```python
_dash = os.environ.get('DASHSCOPE_API_KEY_' + tag)   # reads DASHSCOPE_API_KEY_GWEN …
if _dash:
    env['DASHSCOPE_API_KEY'] = _dash                 # … and gives the child the plain name
```

The child session therefore carried a key under a name goose never asks for. The comment beside
that code said the mapping was right — "DashScope reads `DASHSCOPE_API_KEY` … suffixed in bot.env
and plain in goose" — and it was wrong for this provider, which names the suffixed form itself.

Her chat and her mail were unaffected: those read `DASHSCOPE_API_KEY_GWEN` directly from the
environment launchd loads. Only the wake runs in a filtered environment, so only the wake was dead.
That is why she looked alive.

## Why nobody knew

In the same 24 hours, the daily report said:

```
**Items finished, by amigo** — the last 24 hours
  desi       12
  ...
  gwen        0
```

Twelve items and nothing. Read as a scoreboard, that is an amigo having a quiet day. It was an
amigo whose engine had not completed a single run in four days.

Two decisions, each defensible, together produced the blindness:

1. **Per-wake texts are off, by the human's own instruction.** 2026-10-06: *"stop sending a report
   of what each wake did; once a day, send counts for the last 24 hours."* Every body carries
   `WAKE_SUMMARY_NOTIFY = False` with that reason beside it. So a failing wake sends nothing.
2. **The daily report counted items, not runs.** Its numbers come from the items ledger, and an
   item is written by a wake that *worked*. A wake that dies before writing anything leaves no item
   and therefore no trace in the one thing the human reads.

Nothing in the commons was broken by either decision. Between them, a dead engine had no voice.

## What changed

**`local_tick.worker_env()` — the allow-list became callable.** The six copies each held the
worker's environment inline in `run_session`, where the only way to check it was to read it, and
nobody did. It is a function now, in all six, so a test can call it and ask whether the provider
each bot names can find its own key. **Gwen passes both names**; the suffixed one is the one her
provider reads.

**`tests/test_wake_credentials.py` — the general check.** For every body: take the provider from
that body's own `AGENT_PROVIDER`, resolve the variable that provider reads its key from (the custom
provider JSON, or the catalog name for a built-in), seed the environment with that body's `bot.env`,
call its real `worker_env()`, and assert the name survives. Plus the invariants that were already
policy: no Telegram token, no other body's mail password, own mail pair present (2026-10-04).

On the code that was running, one test fails, and it names the defect:

```
AssertionError: 'DASHSCOPE_API_KEY_GWEN' not found in {...} : gwen runs custom_alibaba, which reads
DASHSCOPE_API_KEY_GWEN, and worker_env() drops it: every wake dies with HTTP 401 and worker_failed
```

That assertion originally printed the whole environment — a live API key and an app password — into
a log. Fixed in the same pass: a failure message names the missing variable and the names present,
never the values.

**The live proof.** Same binary, same provider, same model, one turn, built by calling her own
`worker_env()`:

```
key names in worker env: ['DASHSCOPE_API_KEY', 'DASHSCOPE_API_KEY_GWEN',
                          'OPENROUTER_API_KEY', 'OPENROUTER_API_KEY_GWEN']
exit: 0
authenticated: True
tail: ok
```

Her bot was restarted at 11:25 against the fix. Her next scheduled wake is 2026-11-04 11:25; the
probe is the credential path end to end, and the wake is what will confirm the whole engine.

**`scripts/daily_report.py` — the run outcomes.** A new block counts what each engine did in the
window: ran, landed, not landed, nothing due, failed, read from
`~/LLM/<bot>-bot/tick-state/runs/*/result.json` — which every wake already writes, so the block
adds no bookkeeping to the machinery and cannot itself lose anything. The separate message he reads
gets three lines only when something is wrong; a healthy fleet adds nothing.

Today's block, the first time it ran:

```
### The wake engines (this Mac, last 24h)
  amigo     ran  landed  not landed  nothing due  failed
  desi       12       6           6            0       0
  claude      1       0           1            0       0
  gemini      5       3           2            0       0
  tarik       0       0           0            0       0
  dmitri     12       9           3            0       0
  gwen        1       0           0            0       1
  failed: gwen worker_failed at 2026-11-03 06:04 EST
  not landed: desi — new_test_failures×4, conflict×2
  not landed: claude — conflict×1
  not landed: gemini — (no lander verdict)×1, conflict×1
  not landed: dmitri — new_test_failures×2, conflict×1
```

**The false positive I had to fix before shipping it.** My first version warned when a body's newest
run was older than twice its clock interval. That fired on tarik — his last run directory is
2026-10-19 — and the warning was wrong. Tarik's engine is a Codex-handoff worker: with no pending
handoff it returns `skipped_no_pending_handoff` *without writing a run*, by design. A reporter that
cannot tell "idle" from "dead" cries wolf every day and is believed on the day it is right. The clock
check now reads the body's own `timer.json` last attempt (his ticks daily), so it reports a stopped
clock and not an idle engine. The case is pinned by
`test_an_idle_engine_is_not_a_dead_one`, which is the test I would have written from the mistake
alone.

## The four red tests that were red because the policy moved

`tests/test_local_tick.py` had four failures, pre-existing, that I had previously noted and not
chased. They are not four bugs. Three encode the per-wake notification design that the 2026-10-06
instruction retired, and one encodes the pre-2026-10-04 credential policy:

| test | what it asserted | why it was red |
|---|---|---|
| `test_timeout_reported` | a failed run texts the human | per-wake texts retired 2026-10-06 |
| `test_timeout_with_report_and_changes_is_kept` | `'ran out of time' in notifications` | same |
| `test_unreported_changes_are_surfaced` | same, for parked work | same |
| `test_mail_and_telegram_credentials_not_in_worker_environment` | no mail password in the worker | 2026-10-04 passes each body its own pair |

A red test everybody has agreed to ignore is worse than either policy, because it teaches the suite
to be ignored. They now assert the policy that exists — no per-wake text, the worker carries its own
identity and nobody else's — and the requirement they were protecting is tested where it now lives:
`tests/test_wakes_block.py` asserts that a dead engine is counted and named once a day.
`tests/test_local_tick.py` is 44/44 green for the first time in a month.

## What the numbers say about the clockwork, which is the founder's actual question

From the 1,230 run directories on this Mac:

| outcome | runs | share |
|---|---|---|
| landed | 313 | 25% |
| produced work, did not land | 638 | 52% |
| nothing due | 241 | 20% |
| failed outright (no artifact) | 38 | 3% |

The trend is the good news: since 2026-11-01, 82 productive runs, 57 landed (70%), and the
dominant blocker is now `new_test_failures` (14) — the lander refusing a diff that breaks the
suite's own tests. I checked five of the most-blamed tests against a fresh clone of `origin/main`
and all five pass there, so those refusals are real, not stale baselines. The gate is working; the
rate is worth knowing, not fixing blind.

The 3% that failed outright — 29 missing reports, 5 timeouts, 2 worker failures, 2 runs that
changed files and explained nothing — are exactly the runs this session made visible.

## Named, not done

- **Tarik's engine has produced no run in 15 days.** It may be correct: his wake exists to process a
  pending Codex handoff and the queue is empty. But `skipped_no_pending_handoff` writes nothing and
  logs nothing, so "the queue is empty" and "the queue is broken" look identical from outside, and
  have since 2026-10-19. That is the same defect class as Gwen's, one layer in. A one-line log on
  the skip path would separate the two; I did not change his engine's behaviour on a session that
  was told to optimise, not to reinterpret another amigo's seat.
- **The six engines are 4,138 lines across six files, 571 to 777 each, and differ.** Only desi's
  copy has tests. Any fix has to be made six times and only one of them is checked — this session's
  fix was applied to six and tested through two, which is better than before and still not the
  same thing as one implementation.
- **The lander's own test file is red at `origin/main`** (`test_landing_suite_check`, "NEW FAILURES
  — a landing would be refused: test_b.py"), as are six other suites I confirmed are red on a clean
  clone: `test_daily_report` (1 failure, 1 error), `test_price_band`, `test_reading_queue`,
  `test_reject_queue_request_gap`, `test_reject_queue_sweep`, `test_gallery_unwired_works`. None of
  them was caused by this work. A gate that refuses runs for new failures while its own test is red
  is a gate whose alarm is easy to ignore.
