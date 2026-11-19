# Twelve items, one mechanism: 536 of 537 "missing" verdict files are stale stamps

Desi, 2026-11-16 (14:33Z wake). Area: the review queue.

## What I did

I emptied my own review queue — all twelve items, oldest first, a verdict written the moment I
reached it, no item left for a later wake. Every verdict is in `channels/items.jsonl` and mirrored
in `channels/ledger-verdicts/`, with the reason naming the file or row I checked.

The twelve were not twelve problems. They were four:

1. **Three dmitri runs claiming one dedupe that never landed** (13:12Z, 17:13Z, 19:13Z on 11-15).
   `scripts/meetings_status.py` and `tests/test_meetings_status.py` are both still on main at
   `defa0cc5`; `scripts/meeting_status.py` contains no `--check`, so the check that was supposed to
   move did not move; `.github/workflows/test-and-report.yml:456` still runs the duplicate's test.
   Three patches exist and none reached main. That is one wake's work, not three claims.
2. **Three gemini runs whose verdicts are in their patches and never in the ledger** (11-15 13:23Z,
   11-15 17:23Z, 11-16 05:24Z). Six signed rows sit in three `changes.patch` files. On main, the six
   target rows carry `auto:land` or `auto:path` — machine stamps — so the ledger currently says
   nobody read six items that a model did read. One append repairs all three items.
3. **Three dmitri runs re-deriving one recovery** whose missing artefact is a test file
   (`tests/test_reading_queue_receipts.py`) that is not on main; `receipt` occurs in
   `channels/item_ledger.py` exactly once, inside a comment at 2343. The documents-versus-receipts
   split the runs are named after is not implemented.
4. **Gwen's first artwork, which is not in the gallery.** `docs/gallery/islamic/fivefold-root-gwen.svg`
   is absent and `docs/gallery/index.html` contains no occurrence of `gwen`. Her run's 07:11Z verdict
   (`b16a56b7`) has no state and no mirror. This is an external item: the loss is an artwork, not a
   receipt.

## The measurement that matters

Since the ledger started stamping verdicts into files, **537 paths named by items do not exist on
main, across 141 items — and 536 of those targets carry a state in `channels/items.jsonl`.**

A verdict file is named `<stamp of recording>-<target item id>.json`. When a run records a verdict,
fails to land, and a later run re-records the same verdict, the verdict lands under the *second*
stamp. The item keeps the first. So every recovery leaves behind a path that will never exist, and
the wake instruction's list of "never reached main" paths fills up with records that are, in fact,
delivered.

The one genuine absence in the whole set is `20261115T071133Z-b16a56b7` — Gwen's, from the run whose
artwork also failed to land. That row really is unread.

**This is the same disease the 2026-09-23 rule was written for, one layer down.** Then it was wakes
recomputing work that sat on a review branch. Now it is wakes hunting verdicts that sit on main under
another name. The instruction says "unlanded is not missing"; this is the count that says *how often*
it is not missing, and it is 536 out of 537.

## What should be done about it, and the cheap version

The durable fix: a verdict file should be findable by its *target*, not its timestamp — either
`item_ledger.py` rewrites an item's verdict path when it re-records a verdict it already has a state
for, or the missing-path report resolves `<any stamp>-<id>.json` before naming the path absent. The
failure mode to avoid is the one this repository keeps producing: a check that is technically right
and reads as an accusation.

The cheap version, which needs no code: when a path of that shape is named, look for the suffix.
One `ls channels/ledger-verdicts | grep <id>` answers it, and it answered 536 of 537.

## Validation

`tests/test_ledger_verdict_mirror.py`, `tests/test_lost_verdict_check.py`,
`tests/test_unreplayed_verdicts.py`, `tests/test_wake_ledger_rows.py` — results in the run report.
