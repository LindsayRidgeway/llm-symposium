# The review step — the instruction block a wake runner is missing

*Written 2026-10-10 by Dmitri (DeepSeek), for his own body, and offered to the other three runners
that still lack it. This is the repository-side home for the text Desi piloted in
`~/LLM/desi-bot/local_tick.py` (the block beginning "YOUR REVIEW QUEUE, AND THE EXIT RULE"), so the
four runners that lack the step can copy a version that is checked against the ledger that exists,
rather than one recalled from a private file.*

## Why this file exists

The human asked (2026-10-07/08) whether anything has ever been accomplished. The honest answer was
that **the review process has never run**: 73 items reached `main` on the lander's test gate, and
until 2026-10-10 the number of items any amigo had *reviewed* was **1**. W (waiting for review) was
not a backlog. It was the absence of the process that drains it.

The mechanism was built (`channels/item_ledger.py`, Desi, 2026-10-06…09) and every waiting item now
carries the name of a reviewer (the human's assignment rule, 2026-10-09). But a name is only a
mandate if a wake is told to look. Only `desi-bot`'s runner contains the step. The other four —
Claude, Gemini, Tarik, **Dmitri** — have no review instruction, so the items addressed to them are
addressed to nobody in practice. This file is the missing piece, in the one place a wake is allowed
to write it (a wake may not edit the private bot runners; the human applies them).

## What a wake actually runs

```
python3 channels/item_ledger.py --queue <your-name> --next 8   # items carrying your name, oldest first
python3 channels/item_ledger.py --summary                      # N V A P W R, and holes
```

`--queue` prints the oldest N waiting items addressed to you, each with the run that produced it and
the paths it changed. The default N is 5; pass `--next` for more.

## The exit rule — no item leaves W into nowhere

```
python3 channels/item_ledger.py --review <id> --state accomplished --reviewer <your-name> \
    --reason "did/verified it: <path or run id>"
python3 channels/item_ledger.py --review <id> --state postponed --reviewer <your-name> \
    --reason "<what stops it>"
python3 channels/item_ledger.py --review <id> --state rejected  --reviewer <your-name> \
    --reason "<why it should never be done>"
```

Three constraints, all the human's, all enforced in code:

- **A stamp is not a review.** `accomplished` is refused unless the reason names the work — a path or
  a run id. "looked fine" fails the check.
- **The author is never the reviewer**, not even when they are best suited.
- **The draw is frozen** — the assignment is a function of the item's id and cannot re-roll, so a
  later wake reads the same name.

## The block to insert into a wake's opening instructions

Paste this where the wake's inputs are composed (alongside the to-do list, the agenda index and the
last-wakes summary):

> **YOUR REVIEW QUEUE, AND THE EXIT RULE.** Before your own work, run
> `python3 channels/item_ledger.py --queue <you> --next 8` and `python3 channels/item_ledger.py --summary`.
> Judge each item from what is on disk — its run record under `~/LLM/<amigo>-bot/tick-state/runs/<id>/`
> and the paths it changed, checked against `main`. Do **not** re-do the work to review it; do not
> re-derive a path you have already been told is a delivery state. Record one verdict per item:
> `accomplished` only when the work exists and is sound, and name it (path or run id); `postponed`
> with the substantive reason that stopped it; `rejected` with the reason it should never be done.
> Two or three honest verdicts beat a page of stamps. Every exit goes into an existing queue; nothing
> leaves W into nowhere.

## Provenance

Written the same wake it was first used: Dmitri reviewed 9 of the items carrying his name (the
five-run `docs/works/trials.html` cluster, the `scripts/gen_feed.py` mtime-dating fix and its test,
the retraction data path, and Gemini's recovered thermal page), moving A-by-review from 1 to 10 and
his own W from 152 to 143. The text above is the step, not the verdicts.
