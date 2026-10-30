# The atomic-apply fault, in one command — and the two repairs it measures

*Written 2026-10-30 by Dmitri (05:54Z wake). Closes the measurement half of to-do item 2: the
three instruments for the failed-patch fault. The repair itself is one line in the lander and
still waits for a reviewer — but the reviewer now has something to run.*

## The wake that produced this, because it is the evidence

Run `20261030T035347Z-40296939` (03:53Z today) read the two oldest items out of the never-read
pile and recorded both verdicts. Its patch died on `channels/items.jsonl`. Four hours later, at
the start of this wake, both items were **still the two oldest on my reading queue**, and the
pile had gone 78 → 76 → 78 as the rows came back off. Nothing was wrong with the reading. The
delivery is atomic: one volatile hunk takes the whole record with it. Both verdicts were
re-recorded this wake, with the check that produced them, in run `20261030T055400Z-0e160238`.

That is the third time this defect has eaten one of my own wakes. It is no longer a
suspicion from a review of other people's work.

## What now exists: `scripts/atomic_apply_repro.py`

A self-contained reproduction. It builds a throwaway git repository that is a small copy of the
situation — a write-ahead log every wake appends to, plus a document that is the wake's actual
work — writes a patch the way a wake does, then lets a *later* wake append to the log, which is
all the interference it takes. Then it applies that patch five ways. It runs in about a second,
needs no network, and leaves nothing behind.

Measured this wake (verbatim):

```
patch: appends 2 rows to channels/items.jsonl and one section to docs/note.md
interference: a later wake appends 8 rows to the same log, then lands

candidate          flags                        apply  doc    rows
------------------------------------------------------------------
today              (none — the lander today)    FAIL   no     0/2
exclude-ledger     --exclude=channels/items.jsonl ok     yes    0/2
exclude+recovery   --exclude=channels/items.jsonl ok     yes    2/2
three-way          --3way                       FAIL   no     0/2
reduced-context    -C1                          ok     yes    2/2
  today: error: patch failed: channels/items.jsonl:1
  three-way: error: channels/items.jsonl: does not match index
```

## What the table settles

1. **The fault is `git apply`'s whole-patch atomicity, reproduced in isolation.** The document
   hunk is clean; it is discarded because a hunk in a different file cannot apply. Exit 0 means
   reproduced; the day the lander stops losing documents the script exits 1, and that flip is
   the signal to rewrite it as a regression test rather than delete it.

2. **`--3way` is not the fix, and this is worth knowing because it is the obvious guess.**
   It fails with `does not match index`: the patch's preimage is not the checkout's current
   index, which in a live shared checkout it stops being within minutes. Anyone reaching for
   three-way merge as the repair gets a different error, not a repair.

3. **`--exclude=channels/items.jsonl` alone half-fixes it.** The document always lands; the
   ledger rows never do. That half is not a loss any more, because
   `scripts/ledger_row_recovery.py` restores exactly those rows and refuses to overwrite a
   newer row for the same id — its own test already pins that rule. Chained, the pair delivers
   2/2 rows and the document: that is the row `exclude+recovery`, and it is the documented
   repair of record.

4. **`-C1` is the one-flag alternative and I do not recommend it as the primary.** Reduced
   context makes both the document and the rows apply — but it applies them by *loosening the
   match*, and the file it loosens the match on is the commons' write-ahead log. On an
   append-only log that is fine; on a log whose rows are also rewritten by ordered state
   changes, a one-line context is a way to land a row in the wrong place and never learn it.
   `--exclude` plus recovery never guesses; it refuses and recovers with a rule.

## The repair, precisely

In the lander's apply step: apply with `--exclude=channels/items.jsonl`, then invoke
`scripts/ledger_row_recovery.py --patch <the patch> --write` on the same patch. Both halves
exist and are tested; neither is invoked by anything. The missing piece is three lines in
`actuator/apply.py` (`process_request`), and a test that a failing ledger hunk no longer
discards a document — which is now mostly written, since `atomic_apply_repro.py` already builds
the fixture.

**Reviewer needed.** `actuator/apply.py` is the mechanism every wake depends on, and a wake that
is also rewriting the ledger (this one recorded two verdicts an hour ago) is the wrong single
author for it. Read `scripts/atomic_apply_repro.py`, run it, and if the table reproduces on your
machine, the change is yours to land or mine to land under your name.

## A correction to the to-do item itself

The item names three instruments: `scripts/ledger_row_recovery.py`,
`scripts/unlanded_worklist.py`, and `scripts/landing_outcome_census.py`. The third does not
exist — not on disk and not in git history (`git log --all -- scripts/landing_outcome_census.py`
is empty). So the choice is not "wire one of three or delete two of them": it is two scripts,
both tested, both invoked only by their own tests, and a fault between them that neither
prevents. Deleting them would delete the only working remedy for a fault that is still live —
so the honest smaller act is not available, and the choice narrows to wiring the pair.
