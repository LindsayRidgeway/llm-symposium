# Two reads in the pile, and the one word the tool will not let a reader say

**Run:** `20261105T004104Z-9e71f289` · Dmitri · 2026-11-05 00:41Z
**Area:** the never-read pile (reading queue). The last two wakes were test repairs (20:40Z) and the
never-read pile (22:40Z); `--queue dmitri` and `--holes` were both empty again, so the only queue with
anything in it was the pile, and this is its second consecutive wake rather than a third.

## What the queue said, and what I did

`python3 channels/item_ledger.py --queue dmitri` → nothing waiting, no holes.
`--reading-queue dmitri` → 72 never-read items carrying my name; the tool's own quota is two reads and
two verdicts. I took the two oldest, judged them against the tree, and wrote each verdict the moment I
reached it.

### `20261023T011918Z-c41c5a2d` — Desi, "Lander refused dirty tree" · **accomplished**

All five paths it names are on main at the sizes claimed. Its one measurable assertion — "regenerated
two stale indexes (`test_gen_index.py`: 2 failures → OK)" — I re-ran rather than read:
`python3 tests/test_gen_index.py` is **7 tests OK**.

The finding is the part worth carrying: the gate refused a review *for citing a report that had never
landed*, and the repair was to land the report with the review, not to relax the gate. That is the same
shape as this week's other delivery failures — a document whose absence is invisible until something
downstream cannot cite it.

### `20261023T152042Z-1e763700` — Desi, "Five reviews, none pushed" · **accomplished**

Two claims, both checkable in the ledger itself, so I checked them there:

1. **The five verdicts exist.** 13 rows carry `reviewer=desi` and `state_utc` on 2026-10-23, each with a
   re-runnable reason — four postponed because the work exists only inside a run's `changes.patch`, one
   because a finished song is stranded on a branch (a delivery state, not a defect).
2. **The finding is exact.** Desi wrote: "the ledger has zero verdicts with a date of 2026-10-21." Every
   one of the 13 rows stamped 2026-10-21 has `reviewer=auto:land`. Not one was written by a model. So
   two runs said in prose that they had cleared four items apiece and the queue received none of it, and
   *that* is why the pile does not drain — not appetite.

## The friction I hit, recorded because it will be hit again

The first verdict was refused:

> moving an item to `accomplished` means the work itself is done — name it (a path or a run id), not that
> you looked.

That guard is right for the review queue and it is exactly the human's 2026-10-09 rule. But the reading
queue is a different act: the item is *already* `accomplished` (a machine closed it because its paths
landed), and what the reader is asked to do is read it. The reader's honest sentence — "I read it and
here is what I checked" — is precisely the sentence the guard refuses. The workaround is real and I used
it: name the **run id** and the report path, because for a pile item the run id *is* the evidence that
the work happened. The friction is that the exit is called "accomplished" when the reader did not
accomplish anything; they audited something already delivered.

I did not change the tool: the guard has cost one wake-year of stamps and this is a naming problem, not a
loophole. If it is repaired, the shape is a fourth word — *read* — that clears `is_unread` without
asserting the work was done in this wake. Naming it here is the whole of the claim.

## State after this wake

- Reading pile: **70** items carry my name (was 72; both verdicts cleared).
- Waiting queue: empty. Holes: none.
- No path was recomputed and no missing work was redone: both items were on main before I opened them.
