# What is actually in W

*Generated 2026-10-10T22:57:14Z by `scripts/waiting_pile.py` (read-only).*

Waiting items (W): **243**
  carried by name: desi=59, dmitri=152, gemini=6
  holes (no name): 26
  oldest still waiting: 2026-09-15 · newest: 2026-10-10

## Do the paths each item names exist on main?

  all_present    132   every path this run named exists on main now
  some_present    94   part of it exists
  none_present    17   none of it exists on main
  no_paths         0   the run recorded no paths

So **132 of 243** waiting items (54%) name only paths that are on main. Those are at least *delivered in some form*; whether *that run's* version landed cannot be told from presence alone, so this is an upper bound on delivery, not a proof of it.

## How many can the ledger ever close on its own?

  The landing pipeline's first commit is 2026-09-25. The ledger closes a run only when a `land(wake)` commit names it.
  filed before that date and still waiting: **66**
  filed on or after that date and still waiting: 177

The **66** pre-pipeline items are a *floor* on W, not a backlog: no reviewer and no lander can retire them, because the only automated closer cannot name them. Every daily report that counts them as 'waiting for review' is counting delivery as effort. They need a rule of their own (a closer that closes pre-pipeline work by hand, once), not more looking.
