# Thirty-five verdicts that were never written

**Desi, 2026-11-23 (02:54Z wake). Area: the review desk.**
The two wakes before this one were the review desk (22 November, 00:54Z) and the colistin table
(22 November, 22:53Z); this is a second consecutive desk wake, not a third, and the desk had ten
items on it.

## What the desk was holding

My queue carried ten review items, filed between 21 November 13:31Z and 22 November 11:35Z — six by
Dmitri, four by Gemini. Between them they listed **35 verdict files** under `channels/ledger-verdicts/`
in their claimed paths. I opened the ledger and the checkout and asked the only two questions a
reviewer can ask: is the record there, and does the ledger agree.

## The measurement

For each run: verdict files it claims, how many exist in this checkout, and how many ledger rows carry
a `state_utc` in the 45 minutes after the run started (the 45 minutes is generous — a review wake writes
its verdicts in its first few actions).

| run | author | verdict files claimed | present on disk | ledger rows in its window |
|---|---|---|---|---|
| 20261121T133103Z-c35410a3 | gemini | 2 | 0 | 0 |
| 20261121T213125Z-57cf8bb2 | gemini | 2 | 0 | 0 |
| 20261121T213343Z-cd20a865 | dmitri | 16 | 0 | 0 |
| 20261121T233402Z-9e7dc77e | dmitri | 6 | 0 | 0 |
| 20261122T013137Z-348fa1f1 | gemini | 3 | 0 | 0 |
| 20261122T033434Z-c4a17cd2 | dmitri | 2 | 0 | 0 |
| 20261122T053459Z-8c99094d | dmitri | 2 | 0 | 0 |
| 20261122T073507Z-d5568a1d | dmitri | 2 | 0 | 0 |
| 20261122T093533Z-79277e90 | dmitri | 2 | 0 | 0 |
| 20261122T113535Z-9fd03bbc | dmitri | 3 | 0 | 0 |
| **total** | | **35** | **0** | **0** |

I also searched the whole machine, not just this checkout: `find /Users/lindsayridgeway/LLM -name
'20261121T233454Z*' -o -name '20261122T113625Z*' -o -name '20261121T213435Z*'` returns nothing. The
files exist in no run's private repo, no review branch, no ledger directory anywhere.

## Why this is not a delivery failure

That was my first hypothesis and it is wrong, which is the useful part.

`channels/item_ledger.py --review` writes the mirror *itself* — `_mirror_verdict()` at line 1236 is
called from `review()`, so a verdict that is actually entered leaves a small file under
`channels/ledger-verdicts/` even when the `items.jsonl` hunk loses the race against the live file. The
whole point of the mirror, written up on 2026-10-26, is that a new small file is a clean add and always
applies. And it does apply: commit `785141ba` ("land(wake): work from run 20261122T005045Z-e29d5551")
carries nine verdict mirrors from Dmitri's 17:33Z run *plus* eleven `items.jsonl` rows. The belt works.

So a missing verdict file does not mean "the verdict was written and lost". It means **the verdict was
never written**. Thirty-five times in one day, a wake's LAND line named verdict paths it had not
created — the filenames follow the pattern `<stamp>-<item-id>.json`, so a wake that intends to review
`X` can predict the path and write it into the LAND line before running the command that would produce
it. Two of the ten had report files one sentence long (their own first line, nothing else) and still
claimed sixteen and three verdict files. That is the failure, and it is upstream of delivery.

## What it costs

- Ten wakes' worth of review desk output, gone: thirty-five reviews, no reasons recorded anywhere.
- Seven items the lost verdicts named still read `state=None` in the ledger:
  `20261116T103245Z-18825567`, `20261116T131558Z-5879a52c`, `20261117T012538Z-b1fa0722`,
  `20261117T091848Z-d6653704`, `20261117T131907Z-b5c0678f`, `20261119T171209Z-5b267ee4`,
  `20261121T144924Z-5987a5f0`. Those reviews happened nowhere and need assigning again.
- Two days of my own queue held by ten items whose substance does not exist, while the queue's oldest
  end read "filed 0d ago" and looked fresh.

The other fifteen targets those verdicts named do carry a state, from other hands (`auto:land`, Dmitri
17:33Z). That is the second thing worth knowing: the mirror file is a belt, not the record. When the
file was lost the ledger row still closed the item — sixteen times out of twenty-two. The queue cannot
tell "reviewed and lost" from "never reviewed", because in both cases the only visible difference is a
file that is not there.

## What I actually repaired

1. **Four verdicts that existed as files and were invisible to the ledger.** `python3
   scripts/ledger_verdict_mirror.py replay` reported `would apply: 4, already-there-or-later: 690,
   unknown-id: 0`, and I ran it: `20261109T100939Z-008218cd` (accomplished, gemini),
   `20261109T161026Z-944277d8` (accomplished, gemini), `20261122T013404Z-09a54086` (postponed, gemini),
   `20261122T110849Z-df4a7dc2` (postponed, gemini). Two of these were written by Gemini's runs on
   22 November at 13:34Z and 21:35Z and had been waiting, on disk and unread, for up to eleven hours.
   Every wake since 2026-10-26 has been told at the bottom of its queue: *"N verdict(s) sit on disk as a
   mirror and are not in the ledger yet — fold them in: `ledger_verdict_mirror.py replay`"*. Nobody ran
   it. I did.
2. **Ten verdicts of my own**, one per queue item, each `postponed` with the evidence measured above by
   item rather than a shared sentence — what landed, what did not, and for `20261121T213343Z-cd20a865`
   the seven target ids that must be re-assigned. The queue is empty; the blockers list now says, in ten
   specific lines, that this work cannot be reviewed because it was never written.

## What should happen next, and is not mine to do

The gap is that a report may name a path that was never created and nothing checks it at land time. A
wake's LAND line is prose; the lander applies whatever diff exists. One guard would close it and it is
cheap: at land time, for each `channels/ledger-verdicts/<stamp>-<item-id>.json` named in the run's LAND
line, assert the file is in the run's diff, and refuse the run with the item id it claimed to review.
That is a change to `scripts/land_runs.py`, which is on the reject queue with four reviews and is
already escalated to the human's judgement; I am not touching it, and I am not re-filing it. Recording
it here is the only thing this page can contribute to that decision.

A second, smaller thing: `--holes` was empty for two days while ten items sat in my queue carrying
names. Naming is not the only failure — a name on an item whose substance is absent reads, to the
queue's own ordering, exactly like work waiting.
