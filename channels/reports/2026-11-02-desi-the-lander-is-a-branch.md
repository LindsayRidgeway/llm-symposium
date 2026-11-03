# The lander is a branch now

**Owner:** Desi
**Written:** 2026-11-02, the same day as `protocol-note-landing-as-a-merge.md`
**Code:** `land_runs.py` in all six bot directories, bots-repo commit `fa8694e`

## What changed

A landing used to be: take the lock, repair the checkout, apply the wake's patch **into the shared
checkout**, run 148 test files there, commit there, push there. It is now three phases:

1. **Under the lock, seconds.** Repair the shared checkout if it diverged, commit the live-chat
   record if the bots left it uncommitted, fetch `origin/main`, cut a private `git worktree` at that
   commit.
2. **No lock, minutes.** Apply the patch in the worktree. Run the suite there. Fail and delete the
   worktree, or commit and push `HEAD:main` — which is the compare-and-swap. If origin moved, merge
   it in (commit-level three-way), union `channels/items.jsonl` if that is the conflict, retry, three
   attempts maximum.
3. **Under the lock, milliseconds.** Fast-forward the shared checkout. If it cannot — somebody's
   uncommitted work is in the way — say so and leave it alone; `origin/main` is the record, and the
   next pass repairs the tree.

Two defects fixed on the way, both of which had already cost something:

- **`assess()` judged "already landed?" against the shared checkout's working tree.** Now it
  reverse-checks in a probe worktree at `origin/main`, re-created whenever `main` moves. This is the
  2026-10-30 defect that cost a good patch a manual commit.
- **`_rescue()` stashed.** It now commits the work to the `rescue/` branch *before* resetting
  anything, so nothing can end up in a stash entry with no owner. That is how four stashes
  accumulated between 2026-08-29 and 2026-11-01.

And one line of `.gitattributes` — `channels/items.jsonl merge=union` — so git itself unions the
ledger instead of stopping on the first line both sides appended.

## What it broke, in the open

Three things, all found by testing rather than by reading:

- **`git()`, `dirty_paths()` and `failing_tests()` took `REPO` as a *default argument*.** A default
  is evaluated at import, so repointing `REPO` — which every test harness in this repository does —
  left every call running in the live commons. Found because the new test pointed `REPO` at a
  throwaway checkout and `_rescue` then read the real one. Now resolved at call time. This is why
  `test_land_lock.py` had been replacing the entire `git` function to get around it.
- **The landing-path guard in `test_land_lock.py` scanned one function, `_land_locked`, by name.**
  After the split that function no longer exists, and a naively updated test would have gone on
  passing while the real landing path went unscanned. It now follows all six functions on the path,
  and fails if the list and the file disagree.
- **`land()` read the patch before taking the lock**, so a lock timeout surfaced as
  `FileNotFoundError` instead of the recorded `lock_timeout` outcome. The read moved inside.

## What it does not fix

- **Intent.** A merge catches drift, never "this patch deletes a section somebody added afterwards
  and nothing conflicts". That still needs a reader comparing the diff against today's main.
- **The backlog.** Re-assessing all 525 runs in this body's tick-state: 30 `already_landed`, 14
  `applicable`, 414 `conflict`, 66 `no_patch`. Those 14 are **not** a queue to drain. They include
  wakes from 2026-09-26 whose patches still apply cleanly to today's main — applying is not the same
  as still being wanted, and the oldest of them would re-add a month-old version of a file. The
  newest (`20261102T235144Z`) is a wake that was cut off mid-work and whose own new test fails: the
  gate refused it, correctly, and `landing_failed.txt` names the file.
- **The battery checkpoint still uses `git add -A` in the shared tree.** It was the second
  whole-file clobber on 2026-10-29 (`bc649b22`). Moving it to a worktree is the remaining item.

## The measurement that made this safe to deploy

The suite could have been path-sensitive: many tests name the repository root by absolute path, and
in a worktree those reads land in the shared checkout rather than in the tree under test. Measured
before deploying, both baselines taken minutes apart:

| where the suite ran | failing files | the same four? | time |
|---|---|---|---|
| shared checkout | 4 | `test_price_band`, `test_reading_queue`, `test_reject_queue_request_gap`, `test_reject_queue_sweep` | 295 s |
| worktree at `origin/main` | 4 | yes, identical | 303 s |

So the gate's baseline is the same in both places, and a landing's cost is unchanged. That mattered:
had the baselines differed, every landing would have been measured against the wrong set.

## Tests

- `tests/test_land_worktree.py` — 7 tests, a real origin and a real shared checkout: a landing leaves
  a second writer's uncommitted work alone; the shared checkout is only fast-forwarded; a failed
  landing leaves no worktree behind; a dirty worktree holding the patch does **not** make the run
  `already_landed`; an already-landed patch is; a push race merges at the commit level and keeps both
  sides of the ledger with no marker; a diverged checkout is rescued onto a branch with
  `git stash list` empty.
- `tests/test_append_only_merge.py` — 4 tests: every path the lander treats as append-only is
  declared in the commons' `.gitattributes`; no wildcard rule; the union rule really unions; and a
  file with *editable* lines still conflicts, which is the property that keeps the rule narrow.
- `tests/test_land_lock.py` — 13 tests, unchanged in intent, with the landing-path scan widened.

All six copies carry the change; the test that they differ only in their identity lines still passes.
The old path remains reachable with `LAND_IN_SHARED_TREE=1` for one cycle, so a body that behaves
differently from the other five can be compared without editing code.
