# The 24-hour status audit — B is taken, and the trail does not balance

*Desi, 2026-10-19 01:1xZ. The human's protocol of 2026-10-17: count the six states at time A,
count them again 24 hours later at B, list every logged transition in between with the amigo who
made it, then check that applying those transitions to A reproduces B exactly.*

- **A** = `channels/census/20261017T232914Z.json` (2026-10-17T23:29:14Z, taken by the 10-17 wake)
- **B** = `channels/census/20261019T010907Z.json` (2026-10-19T01:09:07Z, taken this wake — ~25¾ h later)
- Command: `python3 scripts/status_census.py --census`, then `--window A B`

## The two counts

| Status | what it means | A | B | change |
|---|---|---:|---:|---:|
| 1 | done and checked — another model read it and said it holds | 180 | 190 | **+10** |
| 2 | done, not checked — landed by the bot, no model has read it | 175 | 193 | **+18** |
| 3 | waiting, with a name | 5 | 6 | **+1** |
| 4 | waiting, with no name | 0 | 0 | 0 |
| 5 | postponed — a model named what stops it | 117 | 120 | **+3** |
| 6 | rejected — should never be done | 16 | 16 | 0 |
| | **total** | **493** | **525** | **+32** |

## The trail, as logged — 39 transitions

By amigo: **desi 16, auto:land 8, dmitri 8, tarik 7.**
By kind: filed 18 (desi 5, dmitri 6, tarik 7), closed by another model 13 (desi 11, dmitri 2),
closed by the landing bot 8.
By move: absent → 3 (10), absent → 4 (8), 4 → 2 (8), 3 → 1 (10), 3 → 5 (3).

The shape is worth naming plainly: **every closure in the window is by a DeepSeek body or by the
bot.** No Claude, Gemini or Tarik review closed anything in 25 hours; Tarik's seven entries are all
items filed *for* someone else to read. That is the same concentration the reviewer-band item on my
to-do list is about, now with a number attached to one day.

## Validation: FAIL, and the failure is not the one the message suggests

```
validation: FAIL — 39 transitions explain 39 status changes
  UNACCOUNTED 20261017T130246Z-0cc40ab8: predicted Status -, counted Status 2
  … nine more, all the same shape …
```

The count of items grew by **32**, but only **18** arrivals appear in the trail. So ten items are
named as unaccounted, and — this is the part the current script cannot see — **four more are invisible
because they would have passed.** Both sets are rows that entered `channels/items.jsonl` *during* the
window but carry an event timestamp *earlier* than A:

**Ten unaccounted** (each written twice, both rows `source: derived`, `filed_utc == state_utc`,
`reviewer: auto:land`, so filed and closed by the landing bot at one instant):

`20261017T130246Z-0cc40ab8` (13:02), `…131257Z-24b060ca` (13:12), `…150306Z-623fbbfd` (15:03),
`…151323Z-76eed32c` (15:13), `…170319Z-ac2005b9` (17:03), `…170442Z-114b9c12` (17:04),
`…190345Z-537d0f83` (19:03), `…191357Z-b614ee36` (19:13), `…210353Z-c8fdbcae` (21:03),
`…230415Z-ff952369` (23:04) — every timestamp before A = 23:29:14Z, every row appended after it.

**Four masked** — filed 10-17 between 17:02 and 23:14, so also before A, but each has a *second*
transition inside the window (a naming at 12:00:06Z on 10-18, then a close at 13:08Z) that overwrites
the prediction:

`20261017T170206Z-8a55cbf7` (→1), `…171350Z-7a120825` (→5), `…211405Z-067ec72a` (→5),
`…231430Z-2ab19e80` (→1).

For those four the validator says nothing: it starts from A, finds no such item, then applies the
in-window close and lands on exactly the value B counts. **A window could therefore pass while
fourteen items entered the ledger unnoticed.** That is the finding of this audit, and it is worth
more than the FAIL: a check that can be satisfied by an arrival it never counted is the same defect
as a register that cannot tell a cancellation from a lost credential.

## Why it happens, and the repair

`channels/items.jsonl` is append-only and every row carries *event* time (`filed_utc`,
`state_utc`) — the time the run happened — and **no write time**. When a later process appends a row
for an older run (`--backfill`, `--collect` of a finished run, the recovery pass that wrote these
ten), the row is dated months-of-minutes earlier and is invisible to any window that starts after
that date. The ledger cannot distinguish "this happened before A" from "we learned of it after A".

The repair has two halves, both in this change:

1. **`channels/item_ledger.py` stamps `recorded_utc` on every row at write time.** Event time stays
   as it is; the new field answers a different question — *when did the record learn this* — and it
   is the only thing that can place a backdated arrival in a window. Archive rows written before
   today have no stamp and are handled by (2).
2. **`scripts/status_census.py` classifies what it cannot account for, instead of printing one word
   for three different facts.** Arrivals are placed by `recorded_utc` when it exists, so a backdated
   row becomes a real `- → status` transition at the minute it was written; and the validator reports
   **MASKED ARRIVAL** when an item missing from A is carried to the right answer by an in-window
   transition (the four above), so a PASS can no longer hide them. `tests/test_status_census.py`
   pins all four shapes: clean window passes; backdated arrival fails and is named; masked arrival is
   named even though the raw comparison agrees; a status change with no logged transition fails as a
   lost update.

**What this window proves, and what it does not.** It proves the audit trail did not account for 14
of the 32 items that appeared, and it names them. It does not prove any one of them is bad work: the
ten are the landing bot's own closures of runs from 10-17, and the four are items a later wake read
and closed. The defect is in the *record's ability to place them*, not in what the wakes did. Under
the human's protocol that is still a FAIL, and B stands as it is — it is not re-taken after the fix,
because a count that is corrected after the fact stops being a count.
