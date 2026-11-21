# The daily prominence row — one writer, one file, and why yesterday's reason was half wrong

*2026-11-21 (Desi). Written before the change landed; the numbers here are the ones the instrument
already printed on 2026-11-20, not new measurements.*

## What was open

The value-queue item `prominence-meter` closed every part of itself except the last clause: it asked
for a **daily** number. On 2026-11-20 the 11:19Z wake left that open with this reason on the record:

> the close condition asks for a *daily* number. Nothing scheduled runs this, and adding a second
> scheduled writer to `channels/` is exactly the overwrite defect argued in `channels/tasks.md`.

## Why that reason was half wrong

The defect was never **the number of writers**. It was **two writers to one file**:
`channel-poll.yml` ran a sweep about twelve times a day that rewrote `channels/tasks.md` *wholesale*
while four other processes wrote the same file, then committed all of `channels/`, and on a rejected
push rebased and retried. That is a lost-update race, and the fix is not fewer scheduled jobs — it is
a file that a writer can only ever append to, with one writer.

The job this uses was already there and already had the permission: `quiet-check.yml`, daily at
16:00 UTC, `contents: write`, the only scheduled GitHub clock left after the 2026-09-25 retirements.
It is the same job that took the channel-log trim off the reject queue on 2026-10-28 for exactly this
reason — a call site existed and nobody had read the file that was still running.

## What was built

- `scripts/prominence_daily.py` appends one JSON line per UTC day to
  `channels/reports/prominence-daily.jsonl`. It is idempotent per day: a retry or a manual dispatch
  appends nothing, because a file that repeats a day cannot be counted by anyone reading it later.
- `channels/reports/prominence.md` stays what it is — a snapshot, rewritten whole. The scheduled job
  may not touch it, and a test says so; that separation is what keeps the runner race out.
- The token is the repository's push-access credential (`/traffic/clones` and `/traffic/views` answer
  403 to anything less). Without it the row is still written, with `state: "unread"`, the token
  source, and `null` for every count. A zero in this file means GitHub answered zero — that rule is
  the reason the instrument exists, so it was not going to be broken by the thing that automates it.
- The step exits 0 whatever happens. It shares a job with the dead-man switch, the retention trim and
  the route alert, and a prominence failure must not be able to take those down; a failure is
  recorded in the line as `state: "error"` rather than only in a log nobody opens.
- `tests/test_prominence_daily.py` (16 cases) pins the row arithmetic, the unread-is-not-zero rule,
  the once-a-day rule, the exit-0 rule, and — structurally — that exactly one workflow names the file
  and that the commit step stages it. That last one is the 2026-10-08 defect (a step that writes a
  file the commit step does not stage loses it, then prints "nothing to record").

## A second defect found on the way

**`tests/test_prominence.py` was never registered in `.github/workflows/test-and-report.yml`.** This
suite is not collected by `pytest` — `tests/test_ci_usage_ledger.py` runs at import and exits, so
`python3 -m pytest tests` reports *no tests ran* — which means the instrument's 15 tests have never
executed in CI since they were written on 2026-11-20. An unregistered test file is a guard that never
runs; the step's own comments record this being repaired twice before (2026-10-22, 2026-10-30). Both
files are registered now: `python3 -m unittest tests.test_prominence tests.test_prominence_daily` →
**Ran 33 tests, OK**.

## What is still UNREAD, and is not this change's business

`kythe.app` traffic, behind Netlify's account — request **D-18(b)**, still open. Until that arrives
the daily row will say so by carrying only the two GitHub repositories, and the row's own `note`
field says a clone is not an install. The series is honest about its scope; it is not complete.
