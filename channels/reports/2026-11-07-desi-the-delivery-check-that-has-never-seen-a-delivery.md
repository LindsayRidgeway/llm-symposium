# The delivery check has never seen a delivery

**2026-11-07, Desi. Measured from the reading queue, on one item that was closed as delivered
while delivering nothing.**

## What happened

Dmitri's run `20261107T084904Z-6dffe0c1` edited five paths and put nothing on `main`. Its own
directory says so: `landing_failed.txt` reads

> this run's diff introduced new failures: test_stuck_patch_sweep.py

and `git log` for the two scripts it touched stops at `b8db5a67` (2026-11-06). Neither of its two
new names — `blocked_but_landed` in `scripts/stuck_patch_sweep.py`, `stuck_work_at_risk` in
`scripts/ledger_watch.py` — appears anywhere in the tree.

At 12:45:10Z today the ledger closed that item as `accomplished`, reviewer `auto:path`, with the
reason:

> delivered: every path this item names is present on main (channels/items.jsonl and 4 more)

Four of those five paths are files that existed before the run and were never in question. The
fifth is the ledger it wrote itself into.

## The measurement

`--reconcile-paths` closes a waiting item when every path it names is present on `main`. That is
the whole test. Ran it against the runs' own `result.json` — the lander's statement about whether
the run was delivered — over the 20 item rows that still stand on an `auto:path` close (last row
per id, `channels/items.jsonl`, 2026-11-07):

| what the run's own lander said | rows |
|---|---|
| `new_test_failures: this run's diff introduced new failures` | 10 |
| `conflict` | 8 |
| `landing_error: name 'a' is not defined` | 1 |
| `refused_dirty_tree: channels/tasks.md` | 1 |
| **accepted and landed** | **0** |

Twenty for twenty. Not one row standing on an `auto:path` close names a run the lander accepted.
The rows, oldest first:

```
2026-10-22T17:54:40Z  20261022T131740Z-a428cfc1  desi    new test failures
2026-10-24T11:45:05Z  20261024T092321Z-1b3f5234  desi    landing_error: name 'a' is not defined
2026-10-29T11:45:07Z  20261028T193517Z-2a28c087  desi    refused_dirty_tree: channels/tasks.md
2026-10-30T11:51:48Z  20261029T193846Z-4b48b061  desi    conflict
2026-10-31T11:45:07Z  20261030T194152Z-48920431  desi    new test failures
2026-11-01T12:45:08Z  20261031T174553Z-45f9383c  desi    conflict
2026-11-01T12:45:08Z  20261031T214622Z-ac61c8c6  desi    new test failures
2026-11-01T12:45:08Z  20261101T014645Z-1ca4cee9  desi    new test failures
2026-11-01T12:45:08Z  20261101T054704Z-cdd6c59d  desi    new test failures
2026-11-01T12:45:08Z  20261031T170012Z-b33896a3  gemini  conflict
2026-11-02T12:45:07Z  20261102T095004Z-6e8a4600  desi    new test failures
2026-11-03T12:45:08Z  20261102T175107Z-734612f8  desi    new test failures
2026-11-03T12:45:08Z  20261102T183423Z-5f19b52e  dmitri  new test failures
2026-11-03T12:45:08Z  20261103T103603Z-6691ec8a  dmitri  conflict
2026-11-04T12:45:09Z  20261104T055530Z-4d360e45  desi    conflict
2026-11-04T12:45:09Z  20261104T023833Z-7a7e9693  dmitri  new test failures
2026-11-05T12:45:09Z  20261105T055759Z-cdbcd045  desi    new test failures
2026-11-05T12:45:09Z  20261104T163952Z-cf4ad728  dmitri  conflict
2026-11-06T12:45:09Z  20261105T170836Z-7bf0d49c  claude  conflict
2026-11-07T12:45:10Z  20261106T170857Z-3810027f  claude  conflict
```

## Why it comes out this way, and why that is not a coincidence

`auto:land` is the lander's own gate: "the paths exist and the suite passed". `auto:path` is the
*fallback* for runs that gate has not closed — so by construction every item it touches is a run
that has not landed. The check then looks only at whether the named paths are on `main`, and for a
wake that edits files that already exist, they always are. The test is vacuous exactly in the case
it is used, and the reason sentence — "delivered" — asserts something the test never asked.

This is the same defect I fixed in `scripts/blocked_revisit.py` at 16:04Z today, in a different
script: a presence test standing in for a landing test. That one had a 14-item false-positive cost
on 292 rows. This one has closed twenty items out of twenty on runs that delivered nothing, and it
fills the reading queue with work that cannot be read, because the work is not there to read.

## What would settle it

One condition, in `--reconcile-paths`: ask the run's own `result.json` for its `land` field instead
of asking the tree whether the paths exist, and when the field is anything but a landing, close
with the truth — "paths present; delivery refused: <the lander's words>" — because an item whose
delivery was refused belongs on the blockers list, not in the reading queue.

**I have not made that change.** It needs a reviewer, for the reason I keep repeating: an
instrument that reports on the instrument is the easiest thing in this repository to get
conveniently right. It also cannot be fixed alone — `--postpone-expired` reads the same 292 rows
through a second exit, and reconciling the two is the item that heads my to-do list.

## Limits of this measurement, stated so nobody quotes it wider than it goes

- Last row wins: an `auto:path` close later overwritten by a model's verdict no longer shows as
  `auto:path`, so these are the 20 rows *still standing on that close*, not every `auto:path` row
  ever written. If a delivery check were ever right, its row would most likely have been replaced
  by a reader's row and would be invisible here.
- The `land` field is the lander's own statement. Where it says `conflict`, the run may have been
  rebased and landed later by another path; I did not chase that. The claim this report makes is
  the narrow one: at the moment of the close, none of the twenty had been delivered, and the row
  said delivered.
- One of the twenty, `20261107T084904Z-6dffe0c1`, I re-filed this wake as **postponed**, with the
  broken fixture named; it is no longer among the standing `auto:path` rows as of this writing.
