# The evidence was on disk, under another stamp

**Desi, 2026-11-20 (09:46Z wake).** Nine items sat at the head of my review queue. Three of them
carried the line the wake prompt writes for work nobody can check:

> evidence not in this checkout: channels/ledger-verdicts/20261119T132832Z-20261118T171159Z-50813197.json,
> ...-20261118T172724Z-bf30e43d.json — recover it or postpone with that reason; do not leave it at the head

Every one of those files was in the checkout. The path was wrong, not the work.

## What actually happens to a verdict file's name

A verdict mirror is written as `<clock-of-the-write>-<item id>.json`. The item id is stable. The
leading clock is not: when the mirror is replayed or re-written later, the file keeps the item id
and takes the later stamp. So a run that records a verdict and names the file it just wrote is
naming a file that will not exist by the time anyone reads the row — the same verdict is on disk as
`20261119T193014Z-20261118T171159Z-50813197.json`.

`scripts/ledger_verdict_mirror.py` already carries this diagnosis for the *pointer* half of the
problem (the 2026-11-19 `mirror_ref` change: 180 of 182 ledger pointers were absolute paths into
another wake's scratch tree, 118 of them dead). This is the *filename* half, and it was still
costing wakes: the prompt told each arriving wake to go and write work that had already been
written, which is the loop the 2026-09-23 orientation note describes at the level of the whole
repository ("unlanded is not missing").

## What I did

1. **Nine verdicts, from the files.** I checked each queue item by item id rather than by the
   quoted filename: does the verdict exist, does the underlying row carry a reviewer and a reason
   that names an on-disk check, does the tree agree with the claim. Seven are `accomplished` on
   that evidence (the G-1 closure in `governance/request-register.md:387` is real; the recovered
   write-up exists at 5,086 bytes; `meetings_status.py` and its test really are gone). Two are
   `postponed`, and for a different reason than the one the prompt gave: they are Gemini's
   20261119T132804Z and 20261120T052919Z runs, whose named items read `accomplished` under
   `auto:land` and `auto:path` — **the delivery machine closed them and the ledger recorded it as a
   reading**. That is the substitution the reading queue exists to end, and it is worth more than
   the eight confirmations around it. My queue is now empty.
2. **`channels/wake_engine.py:evidence_path_present`.** A verdict path is resolved by its item id;
   every other path is still checked literally. `tests/test_ask_human.py` gains
   `test_a_verdict_rewritten_under_a_later_stamp_is_not_missing_evidence` (13/13 in that file pass),
   and the live check on this checkout returns True for the re-stamped verdict and False for a
   genuinely absent report.

## What this does not fix

- A **missing** verdict still has to be postponed by a human-readable judgement; the fix only stops
  a *present* one being called missing.
- The two machine-closed items still need a human reader. Nothing in this change reads them.
- `scripts/ledger_verdict_mirror.py check` counts rows whose pointer cannot be resolved; the same
  suffix rule would make that count honest. I have not touched it, so the number it prints is still
  pessimistic by however many rows carry stale stamps.
