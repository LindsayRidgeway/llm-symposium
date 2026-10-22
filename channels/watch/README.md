# The daily review check

One machine task, once a day, that measures whether the review queue is draining, repairs what can
be repaired mechanically, and tells the human in one Telegram message. It exists because the
question "is the queue draining?" has a single numeric answer and was, for a week, being answered by
guesswork while the queue grew from 11 to 72.

## What runs

| | |
|---|---|
| script | `scripts/ledger_watch.py` |
| schedule | `~/Library/LaunchAgents/com.lindsay.ledgerwatch.plist`, daily at **07:45** local |
| log | `~/LLM/ledger-watch.log` |
| records | this directory: `YYYY-MM-DD.md` per run, `history.jsonl` appended once per run |
| message | Telegram to the human, sent by `scripts/tell_human.py --amigo desi --force` |
| exit code | 0 when the human's drain rule is met, 1 when not, 2 if the check could not run |

Run it by hand any time:

```bash
python3 scripts/ledger_watch.py --dry-run   # measure only: change nothing, send nothing
python3 scripts/ledger_watch.py --no-send   # repair and record, no message
python3 scripts/ledger_watch.py --force     # a second real run today
```

## The rule it is judged against

The human's rule, in his own terms (2026-10-21): *pending reviews must never exceed the number of
new items needing review in the last 24 hours.* It prints PASS or FAIL against that and nothing
else. Being under the line is not the same as making progress, so the message also carries the
day-over-day change.

## What it repairs, and why those three

1. **Verdicts a refused landing ate.** The landing gate judges a patch all-or-nothing, so a finished
   review sharing a patch with an unrelated failing test is discarded — the review was done, the
   ledger was never told, and the next wake reviews the same item again. On 2026-10-22 this
   recovered 4 verdicts from 8 refused patches. The *first* real verdict wins when an item was
   reviewed twice, because the second review is evidence of the loop.
2. **Items nobody filed** (`--collect`): nothing on this machine runs it — not launchd, not the
   tick, not any wake prompt. Arrivals under-report until a wake happens to run it.
3. **Items whose run has since landed** (`--reconcile`): the same, in the other direction. On
   2026-10-22 this closed 24 items that had landed days earlier, and moved the queue from 72 to 44
   without a single review happening — proof that a part of the backlog was bookkeeping, not work.

## What it does NOT do

It does not invent a fix for a cause it has not seen before, and it does not write to the prompt
files. Those need a wake with turns. When the numbers say the mechanism is still broken, the message
says so and the next wake inherits it.

## Turning it off

```bash
launchctl unload ~/Library/LaunchAgents/com.lindsay.ledgerwatch.plist
```

The records in this directory stay; they are the history of the measurement, not of the job.
