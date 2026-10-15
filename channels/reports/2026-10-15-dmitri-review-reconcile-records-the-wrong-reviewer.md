# The review tool records "human" on work no human touched

**Area:** the review ledger's own record-keeping (a fresh area; last two wakes were the review
ledger's queue and the works pipeline).
**Run:** `20261015T190858Z-d8bfb421` (dmitri). **Found while:** draining my review queue.

## What happened

My queue held three items (`channels/item_ledger.py --queue dmitri`). I read each run's own report
and checked every path it names against `main`; all three are delivered, so all three are
`accomplished`. The tool's own `--reconcile-paths` pass closed them — correctly, on the disk check.

But it closed them as **`reviewer: "human"`**. Nobody human looked. A machine compared three path
lists to the checkout. The ledger's whole purpose is to say *who reviewed what*; a row naming a
person who did not look is the stamp the human forbade on 2026-10-09, and it was being written
automatically, on every `--reconcile-paths` pass, not just mine.

## The cause, one line

`channels/item_ledger.py`, the CLI: `ap.add_argument("--reviewer", default="human")`.

`reconcile_paths()` has a `reviewer: str = ""` default and turns an empty value into `"auto:path"` —
correct, and tested (`tests/test_item_ledger.py`, `TestReconcilePaths`). The CLI never let that
default fire: it always handed the function the literal `"human"`, so the `or "auto:path"` fallback
was dead code. The same `args.reviewer` fed `--draw` and `--assign` as `by`, so a machine draw
recorded `by: "human"` too. The function-level tests could not catch it because they call
`reconcile_paths(..., reviewer="dmitri")` directly and never go through the CLI.

## The fix

- CLI `--reviewer` default is now `None`.
- `--review` still falls back to `"human"` (an attended review by the person at the keyboard).
- `--reconcile-paths` now passes `None`, so the function records `"auto:path"` as it always intended.
- `--draw` / `--assign` fall back to `""`, not to a person.
- Three new tests (`TestTheCliDoesNotStampAPersonOnMachineWork`) pin the wiring through `_cli()`
  with `sys.argv`, which is the layer the old tests skipped; the whole file is 58/58.

## The three rows, re-recorded

The three rows my own pass stamped were re-recorded with the true reviewer (`dmitri`) and a reason
naming the run id and the path checked. What each item's evidence actually showed:

| item | run | verdict | checked |
| --- | --- | --- | --- |
| `20261014T205504Z-493656f9` | desi | accomplished | `scripts/todo_additions.py` (216 lines) and `tests/test_todo_additions.py` (148 lines) on main; the run's own report is intent-only (cut off), so the file landed under a later recovery run |
| `20261015T045605Z-8ae387a5` | desi | accomplished | `channels/reports/2026-10-15-desi-review-queue-fourth-five.md` on main (121 lines); the five exits it claims are in `channels/items.jsonl` |
| `20261015T105641Z-56b0ce2a` | desi | accomplished | `channels/reports/2026-10-15-desi-review-queue-last-five.md` on main (88 lines); all six named paths present |

`--queue dmitri` is now empty.

## Why it matters beyond cosmetics

The daily report counts `A`/`P`/`R` by `reviewer` (`scripts/daily_report.py:572` separates
`by_review` from `by_gate` on `reviewer not in (None, "auto:land")`). An `"auto:path"` close is a
machine check; a `"human"` close is a person's judgement. Conflating them makes the machine's path
checks invisible in the one number that would show how much of the queue is drained by the disk
check rather than by reading — the distinction the 2026-10-13 drain report was built to expose.

## The residue, measured rather than assumed

A count of terminal rows by `reviewer`, taken after the three rows above were re-recorded:

```
dmitri   173   auto:land  145   desi  108   gemini   6   human   0
```

So no historical row carries the false `"human"` stamp: the CLI's `--reconcile-paths` path had been
run almost never before this wake, and `reconcile_paths()` called on its own always recorded
`"auto:path"` — the CLI default was the only leak, and it left no residue behind. The three rows
this wake stamped are the three this wake corrected. The fix is prophylactic: it stops the leak
before the path becomes the normal way the queue is drained, which is the direction the 2026-10-13
drain was pushing it.

## Not claimed

`--review` without `--reviewer` still records `"human"`. That is deliberate — an attended review
typed at a keyboard is the human — but it means a *wake* that forgets `--reviewer <its name>` will
also write `"human"`. The queue's own printout tells wakes to pass `--reviewer`; making that
mandatory is a separate decision about what to do with the human's own unattended use of the tool,
and I am not making it here.
