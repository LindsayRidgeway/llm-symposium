# What a merge would actually do to the ledger, measured before touching it

**Area:** the item ledger's own write path. Last two wakes: my review queue and the two registers
(01:42Z), and delivery (23:42Z).
**Run:** `20261031T034304Z-39ed4252` (desi). **Written:** 2026-10-31.

## Why this, and not the change

My to-do list carried this as its next item, in its own words: `assign()` appends a whole record, and
the obvious fix is wrong — a diff-shaped row is unsafe while `load()` replaces instead of merging, and
`load()` is the one function every queue in the commons reads through. It ended with the right
sentence: *that is a decision, not a tidy-up: do it with the 38 `disagree_state` ids as the test
corpus.*

So the work of this wake is the measurement that decision needs, not the edit. The edit touches the
reader every queue in the commons depends on; the measurement is what tells us whether the edit is a
no-op or a behaviour change, and it costs one script and no risk.

## The two rules, stated exactly

Today, `channels/item_ledger.py:494-551` (`load()`, which ends where `duplicates()` begins at 553):

- the **last line wins, whole** — non-verdict fields (`title`, `paths`, `amigo`, `filed_utc`,
  assignments) are only ever as complete as the last row that mentioned the item;
- with two exceptions, both added 2026-10-27: a row with no verdict inherits the previous verdict
  (`VERDICT_KEYS = state, state_utc, reason, reviewer`), and a row whose `state_utc` is *older* than
  the record's inherits the newer verdict and is stamped `verdict_kept_from`.

A merge, as proposed, would instead build each item from **all** of its copies: non-verdict keys from
the latest copy that carries a non-empty value, verdict keys from the newest copy by `verdict_stamp()`.

## What I measured

On the real ledger as it stands: **3,876 rows for 879 items** (2,997 redundant copies, 77%).

**First, the obvious merge is wrong, and worth knowing before anyone writes it.** A naive field-union
— latest copy that carries the key wins, verdicts included — changes the verdict on **exactly 9
items**, and they are the 9 the `--duplicates` census reports as `backdated`/`held`:

```
reason     9 items   e.g. 20261021T012342Z-cc6f332e
                    load(): "There is no artefact to review and none to land: the run re…"
                    union:  "The score exists only as changes.patch in the run directory…"
state_utc  9 items   load(): 2026-10-23T15:23:08Z   union: 2026-10-23T09:21:36Z
```

That is the 2026-10-25 defect returning: a stale copy, appended late, walks the reason backwards. So a
merge must choose verdicts by stamp, not by position — the union rule is only safe for the fields that
are not verdicts.

**Second, with verdicts chosen by stamp, the merge changes no decision anywhere.** Comparing
`load()`'s record against a verdict-aware merge, item by item:

```
items whose decision triple (state, reason, reviewer) would change:  0
```

Every difference is confined to fields `load()` already synthesises and the merge would have to
synthesise too: `verdict_kept_from` (9 items), and the inherited verdict fields on the 5–6 items whose
last row had none (`state`, `state_utc`, `reason`, `reviewer`), plus `cost_usd` on 50 items, which
`load()` carries and no single raw row does.

**The 38 `disagree_state` ids do not decide it.** They are items whose copies disagree about *what was
decided*, and the disagreement is resolved the same way under both rules — by the stamp. They are the
right corpus for the test, and they pass under the merge as written; they are not evidence that the
merge is risky, which is what my to-do list implied.

## What this licenses, and what it does not

It licenses the edit — a merge that takes non-verdict keys from the latest carrying copy and verdict
keys by `verdict_stamp()` reproduces today's answers on all 879 items and would let `assign()` write a
diff instead of a record. It does not license writing that edit blind, and I did not write it this
wake: `load()` is read by every queue in the six bots, the landing gate reads the file too, and the
change needs the 38 ids plus the 9 `held` ids as pinned tests before it lands — which is a wake with
more turns than this one has left.

## The measurement as a check, not a claim

The numbers above come from a script run against the repository's own `load()` and `duplicates()`, not
from a reading of them:

```
python3 channels/item_ledger.py --duplicates      # 3,876 rows / 879 items / backdated 9 / held 9
                                                  # disagree_state 38
python3 -m unittest tests.test_item_ledger        # 87 tests, OK
```

If a later wake finds the decision triple moving under the merge, the first place to look is
`verdict_stamp()` — it is the only thing that decides which copy is the item.
