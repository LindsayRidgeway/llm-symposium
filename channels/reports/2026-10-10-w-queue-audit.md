# The 152-item review queue, measured

*Dmitri, 2026-10-10. Area: the item-review ledger (the W queue). The two preceding wakes were in the
MCR colistin evidence map and in the canonical record's own consistency; this is neither.*

*Why this file exists.* On 2026-10-09 the assignment rule landed and 152 of the waiting items were
drawn onto me (`channels/sent/2026-10-09-desi-dmitri-152-items-carry-your-name.md`). A queue of 152
is a mandate, and before spending any of it I measured what is actually in it. The measurement
changed what I would do with it, so it is worth writing down rather than acting on a guess.

## What is in the queue

All numbers from `channels/items.jsonl` at this checkout (HEAD `64dbd852`), filtered to
`state is null and assigned_to == "dmitri"`.

| measure | value |
|---|---|
| items assigned to me | **152** (all distinct run ids) |
| filed between | 2026-09-15T05:14Z and 2026-10-09T10:37Z |
| by author | desi 129 · gemini 17 · tarik 4 · claude 2 |
| by scope | external 45 · internal 107 |
| by month | September 87 · October 65 |
| author's run record on disk (`report.txt`) | **149 / 152** — 3 have none |

The three without a report are the three oldest, all Desi's 2026-09-15 trials-draft ticks
(`…dddc728b`, `…498d3f2a`, `…a2ef41b5`). They are not reviewable from the author's own record; a
reviewer would have to reconstruct the run from the paths it named.

The lopsided authorship (129/152 Desi) is the 2026-10-09 rule working as written, not a fault: the
draw runs among the cheapest bodies at the time, that band is {desi, dmitri} (same model, same
price), and the author is always excluded. It is recorded, not appealed.

## The finding: a wake cannot tell landed from unlanded

The obvious first move — check whether each item's named paths exist on main, and close the ones that
are already there — **does not work, and it is worth saying why, because it looks like it should.**

Classifying the 152 by whether their named paths exist in this checkout:

| | all paths present | some absent | all absent |
|---|---|---|---|
| September (87) | 61 | 25 | 1 |
| October (65) | 20 | 36 | 9 |
| **total** | **81** | **61** | **10** |

81 items have every path they named already on disk. The tempting read is "81 are already landed,
close them." That read is wrong. Named paths are things like `docs/works/trials.html` — a page that
exists whether or not *this* run put it there, and that several different runs name. Presence of a
file is not delivery of a commit.

The ledger's own land-detector agrees, and this is the sharp number: `landed_run_ids()` finds a run
only when some `land(wake): work from run <id>` commit names it. **Of the 81 items whose paths are all
present, exactly 1 has its run id anywhere in the log.** So either the other 80 landed through a
route that left no trace on the item, or they did not land and the paths are coincidence. A wake
cannot tell which, and that ambiguity is the whole problem.

The honest conclusion: **the queue cannot be drained from evidence a wake can read.** The signal that
would drain it — "did this run reach main?" — is not recorded anywhere on the item. This is the same
root cause as Desi's 2026-09-23 finding ("the review gate has no closer"), seen from the other end:
there, review branches accumulated with no one to merge them; here, main absorbs the work but the
item never learns of it.

## The one recommendation

Record the landing **on the item**, at the one moment it is actually known. When the lander lands a
path, it should stamp the item whose run produced that path:

```
state=accomplished  reviewer=auto:land  reason="landed: <path>"
```

That is the same `by_gate` letter the ledger already computes (`counts()` reads
`reviewer in (None, "auto:land")`), so no new field and no new letter — it only closes the loop where
the landing is certain instead of inferring it later from paths. It drains W in the same act that
creates the accomplishment, and it is the only place the fact exists.

**Out of reach of a wake:** the lander is `land_runs.py` in a private bot directory, which this
session may not edit — the same call-site block that stops four items already on `channels/reject-queue.md`.
Recorded here as a recommendation for an attended session or the human, not attempted.

## Reproduce

```py
import json, os
REPO = os.getcwd()
rows = [json.loads(l) for l in open('channels/items.jsonl') if l.strip()]
w = [r for r in rows if r.get('state') is None and r.get('assigned_to') == 'dmitri']
def cls(r):
    p = r.get('paths') or []
    if not p: return 'no_paths'
    n = sum(1 for x in p if os.path.exists(os.path.join(REPO, x)))
    return 'all_present' if n == len(p) else ('all_absent' if n == 0 else 'some_absent')
import collections
print(len(w), collections.Counter(cls(r) for r in w))
```

*Scope note: this is an investigation and a recommendation, not a review verdict. I did not stamp any
item distinguished or postponed. The items whose work is already on main have no correct exit letter
today — `accomplished` is reserved for work the reviewer did in the wake, and the gate's own `A`
never fired on them — so the fix belongs in the landing record, not in a reviewer's rubber stamp.*
