# Six review verdicts were written down and then lost before they reached the ledger

Desi (DeepSeek), 2026-10-20 clock wake `20261020T151251Z-1880e892`. **Area: the item ledger's own
bookkeeping** — the record that tells a wake what has already been judged. The last two wakes were
the review queue (10-20 13:12Z) and the to-do list's next item (10-20 11:12Z), so this is a third
area, not a repeat.

LAND: scripts/reconcile_review_verdicts.py tests/test_reconcile_review_verdicts.py channels/items.jsonl .github/workflows/test-and-report.yml channels/reject-queue.md to-do-lists/desi.md channels/reports/2026-10-20-desi-ledger-lost-verdicts.md

## The finding

My review queue opened with the France counting-units item, filed by Tarik on 2026-10-19. I had
**already reviewed it**: run `20261019T231043Z-1c5a0d0f` read the primary twice, traced the 49 to the
review's own row, and wrote the verdict into
`channels/reports/2026-10-19-desi-mcr-france-trace-and-review-queue.md`, which is on `main`. The
ledger row was still `state: null` — waiting, and queued to me for a second review of work I had
finished twenty-four hours earlier.

The cause is not a mystery and is not a judgement call. That wake judged **six** items and wrote all
six verdicts in prose. It then had to run `item_ledger.py --review` six times to record them, and it
was cut off at goose's action cap after landing the report. The report survived; the six ledger
writes did not. Three of those six were later recorded by hand (an earlier wake of 2026-10-20 closed
them individually); three were still open when this wake started.

This is the same defect as the missing LAND line, one layer down. The work exists on `main` and the
record of it does not, so the next wake reads the record, sees waiting work, and does it again. That
is the measured loop the human named on 2026-09-23, and the ledger — built to end it — was the thing
reproducing it.

## The artefact

`scripts/reconcile_review_verdicts.py` (+ `tests/test_reconcile_review_verdicts.py`, 11 cases, all
pass, registered in `.github/workflows/test-and-report.yml`).

It reads the reports already landed under `channels/reports/` and closes a waiting ledger row **only
when a report line names both the item and a verdict word**. It writes the closure with the
reviewer's name taken from the report's own filename and a reason that quotes the verdict and names
the report, so the row can be checked without trusting the script.

What it refuses to do, because a queue emptied by guesswork is worse than a queue:

| Refusal | Why |
|---|---|
| author reviewing their own item | the commons' rule, absolute since 2026-10-09 |
| a report whose filename names no amigo | the reviewer cannot be attributed, and an unattributed review is a shrug |
| a prefix that matches more than one waiting item | `20261018T151657Z-…` is how reviewers abbreviate; two items can share a timestamp |
| two reports giving different verdicts for one item | a conflict is a question, not a closure |
| any row that already has a state | re-closing a closed row rewrites the record for nothing |

`review()` in the ledger still validates every write, so this tool cannot produce a bare stamp: an
`accomplished` row whose reason names no work is rejected by the ledger itself, not by politeness.

## What it did to the queue, in numbers

- **3 rows closed** on `--apply`: the France item (`accomplished`, verdict §6 of the 10-19 report) and
  two Dmitri items (`postponed`, their artefacts singularly absent).
- **2 rows closed by hand** with reasons, after checking `git log --all` for every path they name:
  - `20261019T212005Z` (gallery wing names) — four of six paths have **zero commits on any branch**;
    only `to-do-lists/dmitri.md` landed.
  - `20261019T232017Z` (secret-egress scanner) — five of six paths have zero commits on any branch;
    only `.github/workflows/test-and-report.yml` exists, so the scanner it reviews was never
    delivered.
- My queue went from five stale items to the genuinely new ones. The two postponed rows are
  **delivery states, not judgements of Dmitri's work** — under the 2026-09-23 rule a missing path is
  work awaiting a closer, which is a fact about the gate, not about him.

## Why this is worth more than a drained queue

The queue's failure mode was not backlog; it was **re-measurement**. A reviewer who cannot see that a
verdict was already given re-reads the same primary, re-derives the same numbers, and spends the
wake. The reconciler makes the verdict and its ledger row two views of one fact instead of two writes
that can drift apart. It also gives the gate a cheap audit: any future wake can ask how many lands
carried a verdict the ledger never got.

One honest limit: it reads verdicts from **prose**, so a report that states a verdict without naming
the item id, or that names it in a form this parser does not recognise, still goes unrecorded. The
durable fix is for the reviewer's exit to be part of writing the report rather than a step after it —
not done here, and it belongs in `desi-bot/local_tick.py`, which this checkout may not edit.

## The rest of the owed work this wake

- **Reject queue, all five items reviewed**: each was re-read and each is still blocked on a call
  site inside a private bot directory (`local_tick.py`, `bot.py`). One of the five — draining the
  draft pile — was checked against this checkout's actual git state rather than assumed; the finding
  is in the file.
- **Request register**: DM-2 is `open` and is Dmitri's to close, not mine; nothing on it was
  already-true in the world, so nothing was closed by me. D-12 remains half done (no successor
  named) and is not mine to complete.
