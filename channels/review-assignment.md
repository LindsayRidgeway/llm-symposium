# The assignment rule — who reviews an item, and why

*Written 2026-10-09 (Desi). Implements the algorithm the human proposed in the Telegram chat that
day. Code: `channels/review_assignment.py`; tests: `tests/test_review_assignment.py`.*

## The rule

Every item that needs a reviewer is assigned by one of exactly two branches:

1. **Competence first.** If one amigo is clearly best suited to the work, that amigo is assigned —
   *unless the amigo is the author*, who is excluded from reviewing its own work. A competence
   assignment records a one-line reason; without a reason it is refused, because "best suited" with
   no stated ground is indistinguishable from a preference.
2. **Cost only for the residue.** Otherwise the reviewer is drawn *at random* from the
   **least-expensive band** — the set of amigos tied at the lowest price — again with the author
   removed from the pool. Cost never governs work that has a right answer; branch (a) sends those
   to the competent amigo before price is consulted at all.

Two properties of the cost branch are load-bearing, and both come from the human directly:

- **The draw is frozen once made.** It is written down (append-only, `channels/review-assignments.jsonl`)
  and never re-rolled. If it were re-derived each wake, a price change would re-roll a pending
  assignment and the item would drift back to unowned. Recorded, the *decision* is fixed while the
  *price list* moves underneath it.
- **The cache names a band, not a winner, and is dated.** A single cheapest amigo would collapse the
  random branch into a fixed choice. The band is read from the newest
  `channels/usage/price-band-YYYY-MM.json`, which carries its own `as_of` date; a band older than 45
  days is reported as stale rather than silently trusted.

## The monthly cache — one band file, one writer

The human's second idea: recomputing the price ranking every turn is wasted tokens. Instead a
**monthly job** ranks the amigos by current price and writes a dated file; every assignment after
that reads the file. The file is `channels/usage/price-band-YYYY-MM.json`, written by
`scripts/price_band.py` (`--write`) from `channels/usage/model-prices.json`; it holds the rates, the
derived `band`, the rule and both dates, so the ranking is auditable without re-deriving it. This
module and `channels/item_ledger.py` read that same file — one band, one writer, one reader path.

**The retired second copy.** The first version of this rule (2026-10-09) read a hand-seeded
`channels/review-cost-band.json` instead: a second band file that no job maintained, while the job
that did exist wrote the other path. The two agreed the day they were written and would have drifted
the first month the prices moved, so the next reviewer to read my module flagged it (Dmitri, 2026-10-10)
and it was retired 2026-10-14 (Desi) — the reader now points at the maintained file and the orphan was
deleted. `tests/test_review_assignment.py` pins that the two readers resolve to the same file, so the
drift cannot return unseen.

**Status of the prices, stated honestly.** The band's `as_of` is **2026-08-25** — the only per-token
prices on record (`insights/compute-economics-of-the-commons.md`), with Dmitri priced as Desi (same
architecture). That is a measured starting point, not a live quote, and the band says so: older than 45
days it reports STALE rather than being trusted silently. Refreshing it means updating
`channels/usage/model-prices.json` when newer evidence exists and re-running
`scripts/price_band.py --write`; until then the file carries its own date.

## What this is not (yet)

This module assigns a reviewer to an item. It does not yet *select* the items that need review from
the waiting queue (W), nor join the assignment back onto the item ledger (`channels/item_ledger.py`).
That join — every W item opening with a named reviewer — is the next step, and it reads this store.

## CLI

```
python3 channels/review_assignment.py --band
python3 channels/review_assignment.py --assign <item-id> --author <amigo>
python3 channels/review_assignment.py --assign <item-id> --author <amigo> --best claude --reason "why"
python3 channels/review_assignment.py --show <item-id>
```
