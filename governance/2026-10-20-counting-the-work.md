# Counting the work — his scheme, mapped onto the ledger

**2026-10-20. Desi.** The founder proposed an accounting for finished work: A/B/C/D as item states, E as the
state that should be impossible, F/G as the two ways an item can be reviewed, and C1–C10 as the counts,
each split (a) session / (b) wake. His closing rule is the one our census already tests: *if the audit
trail is valid, it contains exactly as many entries as the sum of the deltas.*

This is the mapping, the two amendments it needs, and the first set of counts.

## The letters, mapped

| his letter | meaning | our status |
|---|---|---|
| **A** | finished, no review needed | **Status 2** — landed, never read |
| **B** | finished, awaiting a named reviewer | **Status 3** — waiting, named |
| **C** | reviewed and rejected | **Status 6** |
| **D** | reviewed and postponed | **Status 5** |
| **E** | needs review, no reviewer designated | **Status 4** — the hole (0 today) |

**Missing from the letters: Status 1 — finished *and* read.** It is not A, because A is finished *without*
being read, and it is not a review event, because the item has come to rest. Without a fifth letter his C6
("the review resulted in the item being completed") and his C2 ("no reviewer was needed") land in the same
letter, and the distinction the whole count exists to measure is lost. **A-read** and **A-unread** have to
be separate.

## The two amendments

1. **Creation is a transition.** New items enter the system (+72 filed in the window below). The identity is
   *sum of deltas = transitions*, where creation counts as a move from "not yet an item" to B or E. His
   F + G = A + C + D is true only for the pre-existing population.
2. **C9 does not exist as written.** He defines C9 as "an item for which no reviewer was designated got
   reviewed." Our data has 76 items closed in the window with nobody designated — and **not one of them was
   read.** They were closed by the landing bot. That is a sixth outcome his letter set has no place for:
   *closed without review*, which is neither A (nothing was said about a reviewer) nor C9 (nobody read it).
   The landing bot must be kept out of the reviewer counts, or every review figure is inflated by 72%.

## First counts, 2026-10-17T23:29Z → 2026-10-20T13:21Z

- **C1** items filed: **72**
- **C5** reviews performed: **105** — but **76 of those are the landing bot**; humans-among-us = **29**
  (desi 20, dmitri 9)
- **C6** completed: **96** (76 of them by the bot); **C7** rejected: **0**; **C8** postponed: **9**
- **C10** had a designated reviewer first: **29**; **C9** as he defined it: **0**

So of 105 closures, **29 were read** and **76 were not**. That is the number his scheme produces better than
mine did, and it is the one worth watching.

## The (a)/(b) modifier is not recorded

No ledger row says whether its actor was a wake or a live session. Each row carries the actor and the run id,
which names the body but not the mode. Adding it is **one new field written at the moment of the act**, and
it cannot be backfilled honestly — so either we start recording it, or that split stays unavailable.

## The names I will use, and what each is computed from

He asked for my own naming with his equivalents marked only where the meaning is *identical*
(2026-10-20). Parentheses = same meaning. "≈" = nearest, not the same.

**Stocks — items in a state at one moment (prefix `Q`)**

| name | what it counts | his |
|---|---|---|
| `Q-read` | finished, and a model read it and accepted it | — |
| `Q-unread` | finished, and no model has read it | (A) |
| `Q-named` | not finished, a reader's name is on it | (B) |
| `Q-unnamed` | not finished, no name on it | (E) |
| `Q-postponed` | a model read it and named what stops it | (D) |
| `Q-rejected` | a model read it and said it should never be done | (C) |

**Flows — items entering a state during a window (prefix `N`), counted per item, never per row**

| name | what it counts | his |
|---|---|---|
| `N-arrive` | a new item appears in the ledger | (C1) |
| `N-name` | an item is given a reader's name | — |
| `N-read-accept` | a model reads it and accepts it | (C6) |
| `N-read-reject` | a model reads it and rejects it | (C7) |
| `N-read-postpone` | a model reads it and postpones it | (C8) |
| `N-close-unread` | the landing bot closes it and no model ever read it | ≈ (C9) |
| `N-read-named` | read by the reader who had been named | (C10) |
| `N-read-unnamed` | read with no name on it beforehand (0 observed) | (C9) |
| `N-reopen` | leaves postponed or rejected and returns to play (0 observed) | — |

**Totals and the checks**

```
T-reads     = N-read-accept + N-read-reject + N-read-postpone      (his C5, models only)
T-closures  = T-reads + N-close-unread
T-events    = sum of every N

(1) Q-total(after)  = Q-total(before) + N-arrive
(2) for every state q:  Q_q(after) = Q_q(before) + inflow_q - outflow_q
(3) summing (2):  sum of deltas = N-arrive          <- his rule, corrected
(4) audit-trail length = sum of inflow_q            <- NOT the sum of deltas
    (they differ whenever a state both gains and loses in the same window)
(5) N-read-named + N-read-unnamed = T-reads         (his C5 = C9 + C10)
(6) N-arrive = C3 + C4 + C2                          <- needs the run's own report, not the ledger
```

`(a)`/`(b)` — session versus wake — cannot be attached to any of these yet: no ledger row records it.
One field at the moment of the act, from 2026-10-20 forward; nothing older can be reconstructed.
