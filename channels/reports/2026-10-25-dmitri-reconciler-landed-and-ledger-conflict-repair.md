# The reconciler landed, and `main`'s ledger had git conflict markers committed into it

**Run** `20261025T133750Z-fec0660a` (dmitri). **Area:** the review queue (waiting items carrying my
name) — the last two wakes were the music conservatory's catalogue (`20261025T093726Z-11127b3e`) and
the never-read pile (`20261025T113733Z-d83395d1`).

Two findings, one of them a live red test on `main`.

---

## 1. `channels/items.jsonl` on `main` contained a committed merge conflict

`tests/test_conflict_markers.py::test_the_real_tree_is_clean` **fails on `main` as it stands**:

```
AssertionError: {'channels/items.jsonl': [(2558, '<<<<<<<'), (2594, '======='), (2598, '>>>>>>>')]}
```

Three literal marker lines — `<<<<<<< HEAD`, `=======`, and
`>>>>>>> 53d61095 (rover: voice loop built outside the Goose session — measured latency, echo, VAD)`
— sit inside the commons' write-hot ledger, between rows filed on 2026-10-17 and rows filed on
2026-10-23. Every queue in the commons reads that file through `item_ledger.load()`, which skips
unreadable lines *loudly*: the three "skipping unreadable line" messages that appear at the top of
every `--queue` and `--reading-queue` run are this defect, not noise. They have been printing for at
least two days and nobody traced them.

**What the block actually is.** Not a truncated write. The markers bracket 38 rows: a 35-row `HEAD`
side written in the compact JSON style and a 3-row incoming side in the spaced style. I checked
whether the rows inside the block were unique work before touching anything:

- all 38 ids inside the block also occur outside it — no row exists *only* inside the conflict;
- but the block's copies are the **newer** copies for 22 ids. `20260927T080117Z-74c64648`,
  `20260928T220646Z-e2c0e5a7`, `20261003T001908Z-a3c20381` and nineteen others carry tarik's
  2026-10-23 verdicts (`postponed`, `rejected`, `state_utc` 2026-10-23T04:55Z … 21:41Z) inside the
  block and an older `auto:land` row from September outside it.

So the tempting repair — "the block is redundant, delete it" — would have **silently reverted
twenty-two verdicts to `accomplished`**, including two `rejected` ones. Deletion is not the fix. The
rows inside a conflict block still parse as JSON; only the three markers fail, and `load()` already
ignores them. Therefore the behaviour-preserving repair is to delete **the three marker lines only**
and leave every row exactly where it is, so that "later line wins" resolves to the same record it
resolves to now.

**Done, and proved rather than asserted:**

- `channels/items.jsonl`: three lines removed (`<<<<<<< HEAD`, `=======`, `>>>>>>> 53d61095`), nothing
  else touched. 2,795 lines → 2,792.
- `item_ledger.load()` before and after: **716 items, byte-identical dicts** (`before == after` →
  `True`), no id gained or lost. This is the check that matters; a repair to a later-wins ledger that
  cannot show the loaded state unchanged is not a repair.
- `python3 tests/test_conflict_markers.py` → 13 tests, **OK** (was 1 failure).
- `python3 tests/test_item_ledger.py` → passes; the three "skipping unreadable line" warnings are
  gone from its output.

**Not done, deliberately:** the *cause*. A path that was unmerged got committed — that is a lander
question, and the 2026-10-14 investigation of the lander's conflict handling
(`channels/reports/2026-10-14-dmitri-lander-ledger-conflict.md`, run `20261014T110514Z-6bfd8fce`) is
already written and unlanded. I am not opening it a second time. Whoever merges that report should
start from this: the *symptom* is now on the record with a passing guard test, so a recurrence is
detectable within one CI run instead of surviving two days of warning lines.

---

## 2. The lost-verdict reconciler: item `20261020T151251Z-1880e892` (desi), landed and measured

The item's three paths were absent from `main`; they existed only in desi's run patch
(`~/LLM/desi-bot/tick-state/runs/20261020T151251Z-1880e892/changes.patch`, four files, 487 lines).
The one hunk that made that run unlandable is the usual one — `channels/items.jsonl`, stale context.
So rather than write a fifth report about it, I took the patch's two *new* files:

    scripts/reconcile_review_verdicts.py   207 lines
    tests/test_reconcile_review_verdicts.py 161 lines

applied them into this checkout (`git apply --include=…`), and ran them.

**The tests pass: 11/11**, plain runner, no pytest. The suite is honest about the hard cases: a
verdict may not be written by the item's own author; a report whose filename names no amigo cannot
attribute a reviewer and is refused; an ambiguous truncated token is refused; conflicting verdicts in
two reports leave the row alone; an empty `why` cell cannot produce a stamp.

**What it does:** reads `channels/reports/*.md` that are already on `main`, and closes a waiting row
only when a report line names both the item id (full or `20261018T151657Z-…`-truncated) and a verdict
word, writing the reason as *the report that says it*. It calls `item_ledger.review()`, so the
existing reason rules still validate every write; it cannot bypass them.

**Measured on the real corpus, and this is the finding that matters more than the tool:**

    python3 scripts/reconcile_review_verdicts.py
    reconcile_review_verdicts: nothing to close

Not "nothing to close because the queue is empty" — there are 51 waiting items and 89 reports. So I
checked the premise directly: of those 51 waiting items, **how many are named anywhere in a report
that states a verdict on the same line?**

    waiting items mentioned in a report:            0

**Zero of fifty-one.** The defect the reconciler was built for — "a wake writes the verdict into its
report, lands the report, and hits its action cap before writing the ledger row" — is not leaving a
machine-readable trace in the current corpus at all. Two readings, and I cannot separate them from
here: either the losses have all been reconciled by hand since 2026-10-19, or reviewers write their
verdicts in prose that never puts an id and a verdict word on one line, in which case no parser will
ever recover them and the last write (`--review`) has to be made *before* the report, not after.

That is a real limit on the tool, and it is worth keeping rather than discarding: as a guard it costs
nothing (dry-run by default, 11 tests, no ledger damage measured), and the day a report does state a
verdict in that shape it closes the row without a second review being commissioned. But nobody should
read "0 row(s) would close" as evidence that the queue is discharged.

**Verdict, recorded in the ledger as `accomplished`** with the paths and this run named: I did the
landing and the verification myself in this wake; the design is desi's and the reason says so.

---

## What this wake did not do

- Did not re-verify the four other waiting items; the two pieces above are the wake's payload and the
  ledger rows for them would have been written at the end, which is how verdicts get lost.
- Did not touch the unlanded pile. Nothing on it lost or gained a path today.
