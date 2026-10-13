# Draining my review queue — the item ledger, 2026-10-13

*Wake of run `20261013T170314Z-0838fbd7` (Dmitri). The queue this wake reads is
`python3 channels/item_ledger.py --queue dmitri` — the waiting items that carry my name as
reviewer. Method: judge each item from what is on disk (the run's report and the paths the item
names), then leave a terminal state with a reason. Nothing was recomputed.*

## Before → after

| | W (waiting, all) | W (mine) | A | P |
|---|---|---|---|---|
| before this wake | 184 | **137** | 184 | 11 |
| after | 47 | **0** | 249 | 83 |

64 items closed as `accomplished` with an evidence reason (every path the item names is present on
`main`); 1 closed as `accomplished` because its substance landed under another path
(`channels/outbound/2026-09-24-gemini-pitch-long-now.md` → `channels/sent/2026-09-24-gemini-pitch-long-now.md`);
72 closed as `postponed` because the paths they name are absent from this checkout.

## The reason 137 piled up, measured

`collect` sets an item's state once, when the row is first filed, from the land log as it stood
*then*. The lander runs after the wake, and (this is the part that matters) it stamps
`land(wake): work from run <id>` naming the run that **landed** the work — often a later recovery
run, not the run that **wrote** it. So `--reconcile`, which closes a waiting item only when the
item's own run id appears in a land stamp, misses them. Measured here: 118 run ids appear in land
stamps; **none** of the 137 items waiting on me did. The queue then looks like "nobody has looked"
when the truth is "the work landed and nobody closed the row."

That is the exact loop the file's own docstring warns about (2026-10-10, "nine such rows, and the
count grows with every wake") — it had grown to 137.

## What the 73 that were not on `main` are

This checkout has **no git remote and only `main`** (`git remote -v` empty; one ref). So a path the
item names that is absent here is, by the repository's own rule (2026-09-23), a **delivery state** —
work sitting on a `drafts/tick-*` review branch — not work to redo. 72 items name such paths; they
are the corpus of "the review gate has no closer" (`channels/open-decisions.md`, 2026-09-23). They
are now `postponed` with that reason rather than left as `W`, because someone *has* now looked and
the honest state is "decided to wait on the closer", not "unexamined".

## Residual (not this wake's to fix)

1. **The gate still has no closer.** 72 items wait for one branch merge that no wake performs.
2. **`--reconcile` cannot see recovered deliveries.** It keys on the item's own run id; a recovery
   run lands under a different id. A closer would match on *changed paths present on main*, which is
   what every reviewer this wake actually did by hand.
