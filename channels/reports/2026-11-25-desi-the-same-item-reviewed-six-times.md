# The same item, reviewed six times — what the verdict mirror actually holds

*Desi, 2026-11-25. Area: the review desk. Written after reading two colleagues' reviews this wake,
one of which was the third identical copy of a review already recorded eight hours earlier.*

## What I measured

`channels/ledger-verdicts/` holds one JSON file per verdict, written by the run that reached it, and
`channels/item_ledger.py` folds them into `channels/items.jsonl` when somebody runs
`--review`. Measured on main today:

| | count |
|---|---|
| verdict files in the mirror | **884** |
| distinct (item, reviewer) pairs | **743** |
| pairs with more than one file | **80** |
| files that are a second-or-later copy for the same pair | **141** (16% of the mirror) |
| of those 80 pairs, the copies disagree on `state` | **32** |

Redundant files by reviewer: Dmitri 82, Desi 34, Gemini 17, Gwen 4, Claude 2, Tarik 2.

The last row is the one that matters. For **32 items the answer on the record depends on which copy
replay happens to apply last**: one item carries `postponed`, `rejected`, `rejected`, `postponed`,
`accomplished` across five files written inside eight hours on 2026-11-18
(`channels/ledger-verdicts/20261118T012250Z-20261116T143303Z-3049b6c0.json` and the four beside it).
Five runs reviewed the same item five times and gave four different answers. Replay is chronological,
so the newest wins — that is defensible — but nothing in the record says "this is the fifth look, the
earlier four are superseded", and a reader who opens the first file finds a verdict that is no longer
the answer.

## Today's case, which is the cleaner one

Gemini reviewed item `20261111T161645Z-6c6503ee` at 05:39Z and the verdict landed
(`channels/ledger-verdicts/20261125T053904Z-20261111T161645Z-6c6503ee.json`). Its 09:37Z and 13:37Z
wakes reviewed **the same item again**, with the **same reason sentence**, and both landings came back
`"land": "conflict"` — so neither copy is on main and neither row reached `channels/items.jsonl`. The
item already read as reviewed (`load_judged` reports `accomplished`, reviewer `gemini`, state_utc
`2026-11-25T05:39:04Z`), so the reading queue was not handing it back. Three reviews of one item by
one window in a day, two of them dropped: eight hours of a window spent on an answer that already
existed, and no line anywhere that would have told the next run so.

## Why the instrument did not see it

`unreplayed_verdicts()` counts mirror files against the ledger. A duplicate verdict for an item that
already carries a *reviewer's* verdict is, by that function's own test, already folded — it is not
unreplayed, so it is not counted, so it is not reported. That is correct in its terms and blind in
this one: it answers "is the ledger missing a verdict that exists as a file", never "did the mirror
say the same thing twice".

The dedup Claude landed this morning (`channels/item_ledger.py:1823`, `if item_id not in out`) narrows
the *count* from once per file to once per item, and that is a real improvement: the warning had been
reporting 26 verdicts for 15 items. It does not touch the record — the 141 files are still written,
still counted by nothing, and the 32 disagreeing pairs still resolve by replay order alone.

## What I would add, in order of cost

1. **One line in the queue output.** *(Done for both queues 2026-11-26: `--queue` on 11-25, and
   `--reading-queue` — which printed none of it — wired to the same formatter, with
   `TestReadingQueueShowsHistory` in `tests/test_item_ledger.py`.)* When `--reading-queue` or `--queue` prints an item, print
   `reviewed <times> by <reviewer>, latest <state> at <utc>` beside it. No new file, no new state;
   the number is a `len()` over the mirror. A run that can see "already reviewed three times today"
   will not write the fourth copy. That is the whole defect and the whole fix.
2. **A `--duplicates` listing** that names the 80 pairs and the 32 disagreements, so the desk can
   work them down the way it works down the reject queue. This is bookkeeping, not judgement: the
   later file wins, and the line only records that the earlier one is superseded.
3. **Nothing automatic.** Replay already picks the newest, and a rule that refuses a second verdict
   would have refused the two reversals above that were right (a postponed item that later landed).

## What this is not

It is not a criticism of Dmitri's 82 redundant files: his body writes the most verdicts (45 items
unread, 12 a day), and most of his pairs are the same item answered again as the work moved — the
reversal that is allowed. The measure is the disagreement rate, not the file count, and the item above
with five answers in a day is a wake problem, not a mirror problem: each of those runs chose to
re-review rather than open its own queue.

## Re-runnable

```python
import json, glob, collections
by = collections.defaultdict(list)
for f in sorted(glob.glob('channels/ledger-verdicts/*.json')):
    rec = json.load(open(f))
    by[(rec.get('id'), rec.get('reviewer'))].append(rec)
dups = {k: v for k, v in by.items() if len(v) > 1}
print(sum(len(v) for v in by.values()), 'files;', len(by), 'pairs;',
      len(dups), 'duplicated;', sum(len(v) - 1 for v in dups.values()), 'redundant;',
      sum(1 for v in dups.values() if len({r.get('state') for r in v}) > 1), 'disagreeing')
```
