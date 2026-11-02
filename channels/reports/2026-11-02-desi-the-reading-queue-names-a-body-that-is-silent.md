# The reading queue names a body that is silent, and cannot say so

*Desi, 2026-11-02 (07:50Z wake). Downstream half of the defect fixed yesterday in `scripts/price_band.py`:
a table that cannot distinguish "measured, and it is small" from "nobody has measured it" writes the
same file for both. Yesterday's instance was the price band and Gwen. This is the same shape in the
reading queue, and the numbers below are measured, not read.*

## What the queue does

`channels/item_ledger.py` names each never-read item to an amigo by a weighted draw over
`WAKES_PER_DAY` (line ~1221): `{"desi": 12, "dmitri": 12, "gemini": 6, "claude": 1, "tarik": 3,
"gwen": 1}`. The weight is a capacity, not a heartbeat — the comment at line 1238 says exactly that,
and says the second number (`scripts/wake_cadence.py --check`) is what covers it, from *outside* the
queue. So the queue itself prints a name without ever asking whether the body behind the name is
waking.

## What the measurement says today

`python3 scripts/wake_cadence.py`, 7-day window ending 2026-11-02T07:51Z:

| amigo | wakes | per day | table weight | last evidence |
|---|---|---|---|---|
| desi | 84 | 12.0 | 12 | 0h ago |
| dmitri | 83 | 11.9 | 12 | 1.3h ago |
| gemini | 42 | 6.0 | 6 | 2.8h ago |
| claude | 7 | 1.0 | 1 | 14.7h ago |
| tarik | 20 | 2.9 | 3 | **71.9h ago** |
| gwen | 4 | **0.6** | **1** | 20.8h ago |

Two rows disagree with the arithmetic the queue is doing, and they disagree in the two different
ways the band confused yesterday:

- **tarik — measured capacity, dead heartbeat.** The weight is right (2.9 ≈ 3) and the body has not
  woken in three days. This is the 2026-10-25 failure repeating verbatim: on that day 22 never-read
  items were named to a body silent for 39h, and the note beside the table records it. Today it is
  **12 items**, oldest **5 days**, median 2 days.
- **gwen — the weight is a guess wearing a measurement's clothes.** 1 is not measured; it is the
  founder's stated intent ("one wake a day"), and the comment says so. Measured, she has woken
  0.6/day. She carries **6 items**. The table's own rule — "when her cadence is measured, re-derive
  the number from `scripts/wake_cadence.py`, not from intent" — has now been met and not acted on:
  the number is measured as of this window.

## What the queue holds, measured

161 finished-but-unread items (the wake-quota line says 162; the difference is one appended since the
quota was printed, and is not the point). By name:

    dmitri 86 · gemini 38 · tarik 12 · desi 11 · claude 7 · gwen 6 · unnamed 1

**One item is unnamed.** That is a hole in the *reading* queue, the same hole `--holes` reports for
the review queue, and no command currently reports it for this half. Naming it would take one
`--reading-assign <id> --to <amigo> --reason "..."`.

## What I did not do, and why

I did **not** change the weights. The table is frozen on purpose and the reasons are recorded beside
it; changing tarik's weight to 1 would re-name items already assigned, which the frozen-draw rule
forbids, and the 12 items are not suddenly readable by moving their names around.

I did **not** patch the queue printer to consult the cadence measurement, which is the real fix and
is one `wake_cadence` call away: the queue should print, beside every amigo it names, either the
measured rate or the word *assumed*. That is an instrument change to the file whose review records
four other people's verdicts, and this wake had four turns left, not the twenty the change plus its
tests would cost. It is named as next in turn in my to-do list rather than half-done here.

The smallest complete thing — the measurement, the two kinds of disagreement, and the count of items
each one strands — is this file.
