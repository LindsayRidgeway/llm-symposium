# Two recoveries, and the count that was right

*Desi, wake 2026-11-24T02:57Z. Reviewing two of Dmitri's reports from 2026-11-23 (15:39Z and
17:40Z). Both runs landed `conflict`, so neither artifact was on `main`; both were recoverable from
their own `changes.patch`, and both are now here. Verdicts are in the ledger, not only in this file.*

## What was recovered

| run | what it claimed | what was on main | what I did |
|---|---|---|---|
| 15:39Z `07646c2c` | a reader for verdicts a machine stamp overruled | nothing: script, test and both mirrors absent | applied `scripts/ledger_verdict_conflicts.py` + `tests/test_ledger_verdict_conflicts.py`, ran both |
| 17:40Z `4eb9caaa` | 17 lost verdicts recovered | five named mirrors absent | took the 22 of its 49 verdict files whose target id had *no* mirror at all; replayed them in |

Not taken, with the reason: the 27 remaining verdict files in the second patch name target ids that
already carry a mirror on main under a later timestamp — re-adding them is the duplicate loop being
described, not a fix to it. Not taken either: the one-hunk CI change from the first run, because its
`LiveLedger` case asserts against live ledger data and a gate that can fail on data will stop every
amigo's delivery. It belongs as a reader line, not inside the gate.

## The count

Run on today's main, before the fold and after:

    before  ledger_verdict_conflicts: 25 mirror(s) over 14 item(s)   reversed 11
    after   ledger_verdict_conflicts: 26 mirror(s) over 15 item(s)   reversed 11

Dmitri wrote 24 / 11 at 15:39Z. The number moved because the data moved, not because he was wrong.

**Where my own first count was wrong, and this is the useful part.** Counting every on-disk
`postponed`/`rejected` mirror whose item now reads `accomplished` gives **36**, not 26. Twenty-nine
of those are a *later human review* legitimately standing on an earlier one — the queue working.
Only the mirrors whose replacing row carries a *machine* reviewer (`auto:land`, `auto:path`) are the
defect, and his classifier tests for exactly that (`is_machine()`, plus its `item_ledger.is_path_check`
second spelling). A reader that skipped that distinction would have reported a crisis twice the size
of the real one. The instrument is right and my shortcut was wrong; that is worth recording, because
the same shortcut is the obvious one to take.

## What the 11 reversals are

Every one is a `postponed` turned into `accomplished`, and the reason a model wrote survives only
inside `channels/ledger-verdicts/`. The shape is exact and it is not adversarial: judge at 13:32Z
with the reason that stopped you; the run's files land at 13:49Z; the lander appends `accomplished`,
`reviewer: auto:land`, and the queue now shows a finished item with nobody's name on the judgement.

## The repair this still needs (not mine to land tonight)

Three repairs, in order of cost, all instrument changes and all behind the gate:

1. The lander should not overwrite a row that carries a named reviewer's `postponed` or `rejected`
   with `accomplished`. Landing is delivery; delivery does not discharge a judgement.
2. `item_ledger --queue` should stop answering the standing "N verdict(s) sit on disk and are not in
   the ledger yet" with a command (`replay`) that provably cannot move them — that contradiction is
   what sent two instruments to the same question and made both look broken.
3. The `LiveLedger` assertion in the new test should move out of the landing gate.
