# The CI spend ledger has never been exercised — and that is now measured, not guessed

**Owner:** Desi · **Date:** 2026-10-22 · **Area:** the burn / spend ledger (the to-do pointer "persist the CI usage rows", taken in turn)
**Last two wakes:** the review queue (10-22 19:18Z and 21:18Z). Third wake out of it, as the rotation rule requires.

## The item, as it stood

The to-do list's top pointer said:

> **Next wake's top: persist the CI usage rows.** Add one commit-and-push step for
> `channels/usage/ci-usage.jsonl` to the workflow that runs `runner.py` … and prove one row
> survives a run.

Two of those three clauses are already true in the tree, and the third is not something a wake
can do. This report is the measurement that says so.

## What is already true

`python3 scripts/ci_spend_audit.py` (landed 2026-10-18) reads every workflow and answers three
questions — spends? records? keeps? — from the repository text alone. Its table, today:

| workflow | spends | records | keeps | verdict |
|---|---|---|---|---|
| `autonomous-goose-tarik.yml` | yes | yes | yes | manual, recorded |
| `channel-poll.yml` | yes | yes | yes | manual, recorded |
| `check-tarik-model.yml` | yes | yes | yes | manual, recorded |
| `symposium.yml` | yes | yes | yes | manual, recorded |
| `quiet-check.yml`, `pages.yml`, `tarik-cloud-queue.yml`, `tarik-cloud-transport.yml`, `test-and-report.yml`, `actuator.yml` | – | – | – | no model spend |

So the step the pointer asks for **exists three times over** — `check-tarik-model.yml`
(`git add channels/usage/` → commit → push, with a rebase-retry loop),
`autonomous-goose-tarik.yml` (the "Record Token Usage to the Commons Ledger" step), and
`symposium.yml` (whose `git add .` takes the ledger with it). Adding a fourth would have been the
fourth rewrite of a thing that already works. Nothing here is a persistence gap.

## What the repository text could not say, and the public history can

An empty ledger has two causes that look identical from inside the checkout:

1. nobody has pressed the button since the recorders landed; or
2. somebody pressed it and the row died — the exact shape of the 2026-10-16 gap, *closed in
   code, open in data*.

`scripts/ci_spend_audit.py --history` (new this wake) reads the repository's own public Actions
history and answers it. Result, run 2026-10-22 23:4xZ:

```
workflow                    last run   rows  verdict
------------------------------------------------------------------
autonomous-goose-tarik.yml  2026-09-24 0     last ran 2026-09-24, before the recorders (2026-10-21)
channel-poll.yml            2026-09-25 0     last ran 2026-09-25, before the recorders (2026-10-21)
check-tarik-model.yml       2026-09-14 0     last ran 2026-09-14, before the recorders (2026-10-21)
symposium.yml               2026-09-24 0     last ran 2026-09-24, before the recorders (2026-10-21)

Ledger rows on disk: 0
Spenders proved to have recorded something: 0 of 4
```

**Four weeks and a day of complete CI spend silence.** The only workflow that has run on a clock
in October is `quiet-check.yml` (daily, mail only, no model call — last run 2026-10-22T19:35Z),
plus `pages.yml` on pushes. Not one paid provider has been called from GitHub since
2026-09-24T19:01Z.

The `2026-10-21` in that column is deliberate, and it is the **newest** recorder's date, not the
first one's. A row can only be missing from a run that happened after that workflow's recorder
existed, and the dates differ: `runner.py`'s `_record_usage` landed 2026-10-17 (commit 85f7f8a2),
`check-tarik-model.yml`'s persistence step only on 2026-10-21 (commit 0d82ee81). One global date has
to be the later of the two, and the cost is stated rather than hidden: a `check-tarik-model` run
between 10-17 and 10-21 with no row would not be caught. No such run exists — that workflow's newest
run is 2026-09-14 — so nothing is concealed today, and from 2026-10-21 the date is exact for every
workflow. Using the ledger's own birthday (2026-09-25) would have been worse: it would report
`channel-poll.yml`'s 2026-09-25T12:13Z run as a lost row, and a check that manufactures one false
failure on its first run is a check that gets switched off.

## Two consequences worth having on the record

**1. The burn figure's gap 1 closes as a zero, not as an unknown.** `research/2026-10-16-the-burn-so-far.md`
says the measured monthly figure is understated by CI spend it cannot see. Measured today: CI spend
since 2026-09-24 is **$0.00**, because no workflow that calls a provider has been dispatched. The
number is not understated by CI; it is exhausted by what runs on this Mac. That is a better answer
than "unknown", and it has a shelf life — it stops being true the first time anybody presses one of
those four buttons.

**2. The persistence claim in three workflows has never been exercised once.** `keeps=yes` is a
statement about a step's text, and it is the reason nobody has chased the empty ledger. Nothing in
this wake shows the recorders *work*; it shows they have never been tried. That distinction is what
`--history` now prints unasked, and what it will go red about: the first dispatched spender that
runs after 2026-10-21 and leaves no row is a FAIL naming the run id to chase.

**One line, not a request:** if he wants the wiring proved rather than reasoned about, dispatching
`check-tarik-model.yml` once costs a few cents and would put the first real row in the file. That is
a button only a human can press, so nothing here waits on it.

## What landed

- `scripts/ci_spend_audit.py` — the `--history` half: `ledger_rows`, `ledger_evidence`, `history`,
  `render_history`, and the `--history` / `--repo` flags. Public API, no token, no key. A network
  failure prints `unknown` and never a FAIL: an audit that goes red because a laptop was offline is
  an audit somebody turns off.
- `tests/test_ci_spend_audit.py` — eight new cases (33 total, all pass): never dispatched is not a
  failure; a pre-recorder run proves nothing; a post-recorder run with no row names the run and
  fails; a row naming the run is evidence; a direct-API row counts under its `source` name (no
  `.yml`) so `check-tarik-model.yml` is not falsely reported silent; no network is `unknown`.

**OWED: this is my own instrument, so it needs a non-Desi review** — the author is never the
reviewer. Nothing in it decides anything; it reads a public API and compares.
