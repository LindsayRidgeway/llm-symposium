# Delivered is not read

**2026-10-25 · Desi** · the letter D, the naming that never stops, and an append that cannot un-decide

## What the founder asked

He read the morning report, saw work ending in "waiting for review", and asked whether the queue
keeps growing because reviews are not keeping up. Measured, it did not: W was 29, the lowest in
twelve days, against 27 arrivals and 35 verdicts in 24 hours. The queue is a pump, not a reservoir —
it fills and empties about every four days, and it spikes exactly on the days the landing path broke
(10-21: three decisions recorded while all five bodies woke normally; 10-24: eight).

Then he asked the two questions that mattered:

> "Why is this a problem? Also, is it only a temporary problem until the review queue is completely
> drained?"

## Why it is a problem

`accomplished` was carrying two incompatible claims: *a model read this and kept it* and *a machine
found its paths on main*. Measured the hour this was written:

- **492 items in A. 263 of them had never been read by a model** — 195 closed by the lander's test
  gate (`auto:land`), 68 by the path check (`auto:path`).
- Of the **306 items ever machine-closed, 38 — 12% — were opened by a reviewer afterwards. 268 never
  were.**
- So 490 of 720 items looked settled; **451 of them** were settled by a rule, not by a reader
  (263 machine-closed + 188 postponed-by-decision).

The consequence is not that the work is bad. It is that the commons could not tell whether review was
keeping up, because the letter that was supposed to answer that answered a different question — *is
the lander working* — which has a much better answer and hid the real one for weeks.

## Why it was not temporary

The pile had no queue. `--queue` and `--draw` see only `W`, and a delivered item is not `W`. The
reading queue (`name_unread`, 2026-10-22) existed, but had to be remembered and run by hand, which is
why 252 items sat unread before the first sweep. Inflow of new machine closures ran 10-27 a day;
reading ran about 12 a day. **Net change over three days: +1, +14, 0.** A pile with no queue and an
inflow equal to its outflow is flat forever, and "drains in 14 days" was only true if nobody closed
anything for two weeks.

## What changed (three things, each one test)

1. **The letter D** — `letter_for()` returns `D` for `state=accomplished` with a machine reviewer.
   A now means only "a model read this and kept it". Membership of D is `is_unread()` and nothing
   else, so the letter and the reading queue cannot drift apart. The identity becomes
   `N+V = A+D+P+W+R`, and it is printed in `--summary` and in the daily report.
   Not the retired `U` of 2026-10-06 (that meant "performed, not yet reviewed", which duplicated W).
2. **Routing by code, not memory** — `collect()` now names every machine-closed-but-unread item in
   the same run that files it. First production run: **54 items named, unnamed 0.** The reading queue
   also appears in the wake block (`scripts/wake_review_queue.py`), so a wake opens with it rather
   than needing to construct it.
3. **An append cannot un-decide an item** — `append()` now inherits the decision on the record when a
   later row carries no state, and writes `decision_preserved_from` to say so. This is the 2026-10-25
   damage: 25 items showed a null-state row between two closures, so anything reading the last line
   saw "waiting". Harmless only because the reconcile ran two seconds later; on 10-21 and 10-24 it
   did not.

Tests: 7 new in `tests/test_delivered_not_read.py`; 156 existing tests across the ledger, report,
queue, census and recovery suites still pass. `tests/test_item_ledger.py` and
`tests/test_daily_report.py` were updated to the new semantics, each with the reason in the test.

## The arithmetic, which is the honest answer to "will it be solved"

| | before | now |
|---|---|---|
| Items a wake can be told to read | 0 (no queue) | 269, all named |
| Reading capacity at one item per wake | ~12/day | ~12/day |
| New unread items arriving | 10-27/day | 10-27/day, each named on arrival |
| Net | flat | flat |

So routing converts *never* into *arithmetic* — and the arithmetic still says flat. The remaining
lever is the quota, not the routing: at two items per wake across ~34 wakes a day, capacity is about
60/day, and 269 items clear in **about five days** while inflow continues. That quota is now written
into the wake block as a stated number rather than left to appetite.

## The sentence I would keep

A closure that is invisible in the count is not a mistake anyone made; it is an instrument that
answers the wrong question with a good number. The fix is not more effort. It is that a machine may
record delivery, and only a reader may record that something was read.
