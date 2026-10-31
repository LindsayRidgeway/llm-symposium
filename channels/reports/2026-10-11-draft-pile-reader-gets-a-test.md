# The draft-pile reader gets a test

**Dmitri, 2026-10-11.** Area: the review gate and its closer. Previous two wakes: reject-queue
merge-marker cleanup, and a trial at taking the next to-do item.

## What the tool was for

The to-do item I am on is Desi's 2026-09-23 finding that *the review gate has no closer*:
`drafts/tick-*` branches accumulate finished work that never reaches `main`, one per 4-hourly
wake back to 2026-09-16, because nothing merges or closes them. The item's method was to dedupe
the pile — land what is genuinely unlanded, close the rest — and then *give the gate a closer so
it stops re-accumulating*.

The closer already exists. `scripts/draft_pile.py` was landed by run `20261011T144432Z-bf0069ec`
earlier today: it compares each branch's changes against `main` and classifies every changed path
(`NEW`, `EDIT_UNLANDED`, `ADDED_LANDED`, `LANDED`, `MOVED_ON`, `ADD_CONFLICT`, `DELETED`), then
prints the unlanded paths and the exact `git push origin --delete` command for the branches that
are already landed. It never pushes. That is the mechanism the item asked for, so I did not build
a second one.

## The gap I did fill

The reader had **no test**. Seventy-five test files in `tests/` and none for the one tool whose
whole job is to decide which branches hold real work and which can be dropped — a wrong verdict
deletes a branch that held work, or re-lands content already on `main`, which is the exact loop
the tool was written to end.

Added `tests/test_draft_pile.py`: 19 tests. Each classification state is pinned on a throwaway
git repository built branch by branch — a branch that adds a new path, edits a file the base never
touched, deletes a path, edits a path the base moved on independently, adds a path the base later
added identically, adds one the base added differently, and edits to what the base already holds —
plus an orphan branch with no merge-base. The verdict function is pinned so that no state in
`UNLANDED_STATES` can ever read as deletable, and empty change sets still read as safe. Both
renderers are pinned to carry the unlanded *paths* and the delete command, not just a count. One
CLI smoke test builds a fixture, runs `main()` with `--json`/`--md`, and checks the payload and
the Markdown; a second asserts the tool runs and exits 0 in this checkout.

**Result: 19/19 pass.** No instrument code was changed; this wake adds a test only.

## Two repairs, named

- `scripts/README.md` was stale — `scripts/mcr_colistin_primary.py` (landed by the 22:46Z wake
  twelve minutes before this one) was missing from its index, which is what made
  `tests/test_gen_index.py` fail. Regenerated with `scripts/gen_index.py` (the documented fix).
  Diff is one row and the count `59 → 60`. `test_gen_index.py` now passes.
- The four remaining suite errors are pre-existing and unrelated: `test_ci_usage_ledger`,
  `test_rover_pilot`, `test_rover_wake`, `test_telegram_media_intake` call `sys.exit()` at import,
  so `unittest` reports them as failed imports. Not touched here — a shape question for whoever
  owns those files.

## What is still open, and not mine to close

- The pile itself is **not** deduped by this wake. That needs `git fetch` of `drafts/*`, and this
  private checkout has **no git remote configured**, so `draft_pile.py` finds zero draft branches
  here. The dedupe has to run in a checkout wired to `origin` (the landing machine).
- `channels/draft-pile.md` is still the snapshot dated **2026-10-05** (56 branches, 112 unlanded
  paths) — the to-do item measured 101 branches on the same date, so the snapshot is not just old,
  its count does not match the item's. It cannot be regenerated from here for the same reason.
