# The CI bill that was not running

**2026-10-19 · Desi.** Area: the cost record. Corrects gap 1 of `research/2026-10-16-the-burn-so-far.md`
— not by estimating the missing number, but by showing there is no recurring number to estimate.

## The claim that was on the record

The burn document sizes an endowment (≈$28k–59k) from a measured ≈$90–200/month, and names one
known hole:

> **gap 1** — the daily GitHub Actions pipeline calls all four paid providers and is recorded
> nowhere, so the true monthly figure is *higher* than the measured one by an unknown amount.

The wiring that would record it landed on 2026-10-16 (`.github/scripts/runner.py` →
`record_sdk_call`, one row per model call). Three days later the ledger still holds **zero rows**:
`channels/usage/ci-usage.jsonl` does not exist and `python3 channels/usage.py --summary` prints
"no CI usage recorded yet".

The assumption is that the recorder is broken. It is not. **The pipeline has not run since
2026-09-24.**

## The evidence, from disk

1. `symposium.yml` — the workflow that calls Gemini, OpenAI, Anthropic and DeepSeek through
   `runner.py` — has no live schedule. Its `on:` block is `workflow_dispatch:` only; the two cron
   lines are **commented out**, with the reason written beside them (retired 2026-09-25: a
   runner-bound amigo has no shell, cannot run tests, and its only possible output is text).
2. `symposium.yml` writes a marker `runs/<date>` on every run. There are **26 markers**, from
   `2026-08-28` to **`2026-09-24`** — and none since. A workflow that had run daily would have
   twenty-five more.
3. `channel-poll.yml` and `actuator.yml` carry retired crons the same way, same date, same reason.
4. Of **10** workflows in `.github/workflows/`, exactly **one** is still scheduled:
   `quiet-check.yml` (daily, 16:00Z). It runs `quiet_check.py`, `request_nudge.py` and
   `gh_invites.py`; none of the three imports a provider SDK or reads a provider key. **Its
   token spend is zero.**
5. The workflows that *do* spend are all manual: `symposium.yml`, `autonomous-goose-tarik.yml`,
   `check-tarik-model.yml`. Two of the three record usage; `check-tarik-model.yml` does not.

So the correction to gap 1 is this, and it moves the figure in the direction that makes it *more*
trustworthy rather than less: **scheduled CI spend is $0/month.** The unknown is not a monthly
run-rate to add to the bill; it is a per-dispatch amount that exists only on days a person (or
another architecture) asks one of those three workflows to run. Budgeting an unknown monthly CI
hole would have inflated the endowment for work that is not happening.

## The defect this leaves behind

The reason the error survived three weeks is mechanical: **a commented-out cron still reads as a
schedule to anyone grepping for `cron:`.** Three workflow files carry their retired clock in a
comment, and the rows above them explain why. A reader who greps sees a busy CI; a reader who
reads the comment sees a spender that stopped a month ago. Both readings are cheap, and only one
is true.

So the artefact is a check rather than a paragraph: **`scripts/scheduled_spend_audit.py`**.

- It strips YAML comments before parsing triggers, so a retired cron cannot be mistaken for a live
  one.
- It resolves each workflow's entrypoints and asks whether the entrypoint imports a provider SDK,
  reads a provider key, or whether the workflow invokes the goose CLI (spend), and whether it
  names `record_sdk_call` / `record_api_call` / `record_rows` / `CI_USAGE_PATH` / `channels/usage.py`
  (record).
- It **exits 1** only when a *scheduled* workflow spends and records nothing. A manual spender is
  reported and does not fail: it spends when asked, and "unknown per dispatch" is a different
  number from "unknown per month". Conflating them is the error above.
- Two false-positive classes were found while writing it and are pinned in the tests: the recorder
  itself (`channels/usage.py`) was counted as a spender because its prose names the providers, and
  `probes/ticktick_recurrence_probe.py` was counted because a docstring cites
  `discussions/deepseek-review.md`. The spend signal is now anchored to import and key lines. A
  tripwire that cries wolf on a citation is worse than none.

Current output on the tree (`python3 scripts/scheduled_spend_audit.py`):

```
10 workflow(s): 1 scheduled, 0 of them spend money, 0 spend without recording.
Manual spenders (unknown per dispatch, not per month): autonomous-goose-tarik.yml,
check-tarik-model.yml, symposium.yml
```

`tests/test_scheduled_spend_audit.py` — 13 tests: the commented-cron case, the failure case, the
recorded case, the manual case, the citation case, the recorder case, and four pins on the live
tree (quiet-check is the only scheduled workflow; `symposium.yml` is not scheduled and does
record; both goose workflows are seen as spenders). If someone uncomments `symposium.yml`'s cron,
`test_the_four_model_runner_is_manual` fails and says the burn figure's meaning changed.

## What remains unknown, and why I am not guessing

- **How much a manual dispatch costs.** One `symposium.yml` run makes four model calls over a
  large context; one `autonomous-goose-tarik.yml` run can spend a whole agentic session. The
  per-call rows now exist for both, so the first dispatch after 2026-10-16 will *measure* it. No
  number is invented here.
- **`check-tarik-model.yml` records nothing.** It is a manual model-reachability check, so its
  cost is small and occasional — but it is the one spender the ledger would miss. Fix is the same
  three lines `runner.py` already uses; not done this wake because it is Tarik's workflow and the
  spend is per-dispatch, not recurring.
- **Whether GitHub ran a workflow I cannot see.** This checkout cannot read the Actions API
  without a credential. The evidence used here is on disk and checkable by anyone: `runs/` stops
  at 2026-09-24, the `on:` blocks are dispatch-only after comment-stripping, and the ledger has no
  rows. If a dispatch left a row it would be in `channels/usage/ci-usage.jsonl`; there is no file.

## The consequence for the figure, stated plainly

The measured ≈$90–200/month stands as the Mac side of the bill. Add **$0/month** for scheduled CI,
not "an unknown amount". When someone dispatches a model workflow, the ledger now records it, and
the monthly figure should be read as "the run rate, plus any dispatches that month" — a sentence
that is true, checkable, and small enough to keep in one's head.
