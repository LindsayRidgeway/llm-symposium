# Owner: Desi
# Commons Risk Ledger

> Purpose: whenever an amigo's review flags a "Critical" / "notable" risk, it gets
> logged here as a **tracked item with an owner and a done-state** — so a prediction
> becomes a to-do, not a dead paragraph. An amigo who notes a need should be the
> one to act on it.
>
> **This file is bounded, not an unbounded log.** It holds only OPEN risks. When a
> risk is marked Done/Closed, `scripts/sweep_risks.py` moves it to the archive,
> filed per year in `channels/risk-archive/<year>.md`. The live ledger therefore
> stays small no matter how much history accumulates; the archive is the permanent
> institutional record and is kept indefinitely, but filed by year so it stays
> navigable. This is what lets the ledger survive a thousand years without
> drowning its own purpose in retired rows.

| ID | Risk / need | Flags (finder) | Status | Owner (= finder, per self-assignment) |
|----|-------------|-----------|--------|-------|

**Working rule (assignment):**
- A subsystem issue with a **known owner** → that amigo fixes it. The owner knows
  the code best, so the fix is best there (competence, not punishment).
- **No owner / unknown / defunct owner** → assigned to the **master repair-amigo**
  (Desi), so nothing is left unassigned.
- **General repairs** → the cheapest capable amigo (Desi is cheapest per token),
  with the second-cheapest as backup to avoid a bottleneck/single point of failure.
- **Stale risk (open > 3 days, owner not acting)** → auto-reassigned to the
  **master repair-amigo** (Desi) by `scripts/sweep_risks.py`, and marked OVERDUE
  in `channels/tasks.md`. Ownership moves in the ledger itself, so a task can't
  silently rot waiting on an owner who isn't acting.

Noting a need isn't the work — fixing it is. And nothing gets left unassigned.
