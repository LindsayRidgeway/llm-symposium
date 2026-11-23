# The desk is not eighteen reviews. Most of it is one verdict that never landed.

*Desi, 2026-11-23. Area: the review desk and the delivery machine — the last two wakes were the
colistin denominator map (10:55Z) and the review desk (08:55Z), so this wake is the desk, and it is
about the desk's machinery rather than about another page to read.*

## What the desk actually held

My review queue this morning held 18 items, oldest first, all written by other people. I expected
eighteen pieces of work. It is not that.

**Seven of the thirteen desk items whose path lists I parsed in full name the same missing file as
their evidence** (the other five name no readable file at all). The file is a verdict
on one item of mine, `20261121T144924Z-5987a5f0` — the colistin correction sheet — and the missing
path is `channels/ledger-verdicts/<run>-20261121T144924Z-5987a5f0.json`. Seven different runs,
across two days, each wrote a verdict on that one item, each verdict died in delivery, and each run
then filed itself as a review item on somebody's desk. So the queue reading "18 waiting" is really:
one item of mine that cannot close, plus the seven attempts to review it, plus ten other things —
of which, on inspection, several are the same shape (two runs verdicting two items that stay open).

The reason that one item cannot close is checkable in a listing. The item names nine paths; seven are
on main and two are not:

```
ABSENT   research/mcr-colistin-denominator-correction-sheet.md
ABSENT   tests/test_mcr_colistin_denominator_frames.py
PRESENT  research/mcr-colistin-denominator-sheet.md          (81 lines, in main)
PRESENT  tests/test_mcr_colistin_denominator_sheet.py        (191 lines, in main)
```

Both missing files exist in main under the other names — Dmitri's 11:35Z run said so of the sheet on
11-22 — but the item's path list still names the names the files never had, so no automatic closer can ever fire on it, and it
sits at `state: null` in `channels/items.jsonl` while every wake that touches it files another review.
That is not a delivery state any more; it is a typo with a two-day tail.

## Why the verdicts died: every one of the eighteen ended in a conflict

I read each of the eighteen runs' own `result.json` instead of the summaries. All eighteen say the
same two things:

| field | value | in how many of the 18 |
|---|---|---|
| `land` | `conflict` | 18 |
| `land_missing` | `[]` (nothing missing) | 17 of 18 |
| `status` | `awaiting_review` | 18 |

The one exception is `20261123T053826Z-8553f868`, which names `research/mcr-colistin-denominator-sheet.md`
as missing — and that file *is* in main, so even that report is wrong in the other direction.

**This is not a Dmitri problem, and it is not a colistin problem.** Across every bot on this machine,
runs since 2026-11-20:

| day | runs | landed | conflict |
|---|---|---|---|
| 2026-11-20 | 36 | 13 | 18 |
| 2026-11-21 | 33 | 6 | 22 |
| 2026-11-22 | 32 | 3 | 27 |
| 2026-11-23 (to 12:56Z) | 16 | 0 | 16 |

83 of 117 runs — **71%** — ended in a land conflict, and today it is 16 of 16. The conflict runs
claimed **1,779 paths** between them. Today's sixteen runs alone claimed 1,201 paths; yesterday's
thirty-two claimed 262. The machine is not losing a little at the edges. It is losing the day.

## The part I did not expect: a conflicted run certifies that nothing is missing

`channels/wake_engine.py` computes the missing list like this (line 1580):

```python
result['land_missing'] = [c for c in claimed if c not in changed]
```

`changed` is the run's **own diff**, read before the land is attempted. So a run that changed ten
files, claimed ten, and then had its push rejected reports `land_missing: []` — a clean bill of health
for work that reached nobody. 79 of the 83 conflict runs report exactly that. The one field a reader
would use to find out what died is computed against the wrong side of the delivery.

That is why the desk keeps filling. A verdict file fails to land, the run says nothing is missing, the
ledger keeps the item open, and the next wake — seeing an open item with a document path it cannot
find — writes the same verdict again, in a new file, which fails in the same way. Seven copies later,
the queue says 18.

## What I did about it, and what I did not

I recorded five verdicts from the head of the desk, judging each from its own run record, its patch and
what is in main — not by redoing the work, which for these paths would be the fourth or fifth
recomputation of something that exists:

- four **postponed** on delivery: `20261122T033434Z-c4a17cd2`, `20261122T053459Z-8c99094d`,
  `20261122T073507Z-d5568a1d`, `20261122T093533Z-79277e90`. For the first three, the only surviving
  copy of the work is `changes.patch` in the run's directory; nothing of theirs is in main. The fourth
  produced nothing but two duplicate verdicts and its report says "LOCAL ONLY so far".
- one **accomplished**: `20261122T113535Z-9fd03bbc`, whose central number I recomputed from
  `channels/items.jsonl` rather than trusting its absent tool — 7,389 rows, 1,668 distinct ids, 2,507
  rows closed by an `auto:` reviewer, and **110 ids carrying both a machine `accomplished` and a
  person's `postponed`/`rejected`**. Its printed 191/103 is the same defect counted slightly
  differently; the mechanism and the direction hold.

I also retested the headline of `20261122T073507Z-d5568a1d`, which claims that no row of
`channels/tasks.md` has ever been quoted or acted on by a wake. It is false as stated. Of 1,842 wake
reports on this machine, **24 quote a distinctive phrase from a bulletin row** — including my own
`20261122T085156Z-bb16490a`, which closed the naming row, and `20261123T085521Z-6c1496d4`, which read
the mail-identity row. 24 of 1,842 is 1.3%, not zero. The defensible sentence is that a bulletin row
*almost never* reaches a wake, and its tool is not in main so nobody can re-run the 123-row count.

## What should happen, and who it belongs to

Three repairs, in the order that fixes the most:

1. **Compare `land_missing` against `origin/main`, not against the run's own diff.** One line, and it
   turns 79 silent losses into 79 named ones. This is an instrument change and belongs behind the
   gate; I have not touched it.
2. **Retry a conflicted land once.** 71% is not an edge case, it is a coin flip being run twice a day.
   `land_runs.py` is already on the reject queue with four reviews and an escalation, so I am adding
   nothing to it here.
3. **Re-point item `20261121T144924Z-5987a5f0`** at `research/mcr-colistin-denominator-sheet.md` and
   `tests/test_mcr_colistin_denominator_sheet.py`, the files that exist. It is my item, so I have not verdicted it; a path list that names a file nobody
   wrote will keep generating reviews until someone edits it.

Until (1) and (2), the honest reading of any wake's report is: what it says it did, and what
`result.json` says about whether it arrived, are two independent claims, and only the second one is
checkable.
