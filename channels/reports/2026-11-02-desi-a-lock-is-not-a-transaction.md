# The shared checkout has no transaction strategy, and a lock is not one

*Written 2026-11-02 by Desi, answering the founder's question the same day: "This has to be one of the
oldest bugs in the industry. Don't you need to start using resource locks or some other transaction
strategy?" Owner: Desi — the landing gate is mine.*

## Short answer

**Yes, but a lock is the smaller half, and we already have one.** Two things are wrong, and neither is
fixed by adding more locking:

1. **The lock is held for the wrong length of time.** `land_lock()` is taken around the *entire*
   apply‑and‑test sequence, and the test sequence is 148 test files. So one landing stops the world for
   minutes. Measured 2026-11-02 11:41 ET: a landing held the checkout from 11:35 and I could not write
   at all; at 11:44 it was still running `tests/test_task_ledger.py`. A lock held for a whole test suite
   is a lock that makes everything else wait, and waiting writers are exactly the ones that then get
   their work stashed out from under them.
2. **The damaging operation happens *inside* the lock, in the shared tree.** `_rescue()` does
   `git stash push -u` → `git reset --hard origin/main` → `git stash apply`. That is a hand-written
   transaction on a directory other processes are also writing to. When the apply does not replay
   cleanly, the tree stays reset and the work stays in a stash **that nothing reads**. That is how my
   own restored section of `channels/tasks.md` disappeared on 2026-11-02, and `git stash list` shows
   four earlier instances of the same loss (2026-08-29, 10-17, 10-22, 11-01 — preserved as patches in
   `channels/recovery/`).

There is a third, smaller one: **sessions do not take the lock.** An advisory `flock` only protects code
that opts in, and my own edit‑then‑commit on 2026-11-02 did not. That is my fault and it is the cheap
one to fix.

## Why "just use locks" cannot solve it

- **Git has no transactions.** The index is last‑writer‑wins by design; there is no version check on
  commit ("commit if the file is still what I read"), which is the primitive all of this needs and which
  git does not offer. Locks are the only substitute, and they are advisory and coarse: one per
  repository, not one per path.
- **The unit of work is too big to lock.** Applying a patch, running 148 test files and pushing is
  minutes. Serialising that against every other writer converts a race into a queue, and a queue with no
  timeout is a deadlock with extra steps — which is what the 2026-10-10 note in `land_runs.py` records
  ("one uncommitted file stalled every landing in every body for 36 hours").
- **A per-repository lock cannot make a *patch* fresh.** The failure that bit us is staleness: a wake's
  patch was computed against an older `channels/tasks.md`, and the guard (`foreign = dirty paths the
  patch touches`) only catches the case where the file is dirty *at that moment*. Serialise everything
  and the patch is still stale; it just loses later instead of sooner.

## The strategy that actually removes the class

**One writer per working copy.** The standard shape, and git supports it natively:

1. **Every writer works in its own `git worktree`**, created fresh at `origin/main`: the landing gate,
   each session, the battery checkpoint, the record push. Apply, test, commit, push — all inside that
   private tree. Failure costs nothing because the tree is thrown away.
2. **The shared checkout becomes read‑mostly.** Its only mutating operation is `git fetch` followed by
   `git merge --ff-only origin/main` — a fast‑forward that either applies cleanly in milliseconds or
   fails and says so. No patch is ever applied there, nothing is ever stashed there, and
   `git reset --hard` is banned in it outright.
3. **The lock shrinks to the fast‑forward.** What needs mutual exclusion is a pointer update, not a test
   suite. It is then held for milliseconds and a timeout is a formality.
4. **Staleness is handled where it is created**: a patch that does not apply to today's `origin/main` is
   `conflict`, and the run is asked to redo the small part that moved — never silently reapplied over
   somebody else's newer lines.
5. **No stash, anywhere, ever.** A stash is an unreviewed queue with no owner; we have four of them
   already. Work that cannot be committed goes in a rescue *branch* (committed, visible, owned) and the
   tree is left alone.

## What I am doing, in order

1. **Today:** my own writes take `record_push.shared_checkout_lock()` around edit‑and‑commit, and I do
   not edit an existing tracked file in that tree while a landing is running. (The files in
   `channels/recovery/` were written without it on purpose: they are new paths that no patch can touch,
   which is the condition under which writing there is safe.)
2. **Next:** replace `_land_locked`'s apply‑in‑the‑shared‑tree with a private worktree, in all six bot
   copies, with a test that lands while a second writer holds uncommitted work and asserts both survive.
3. **Then:** delete `_rescue`'s stash path in favour of a committed rescue branch, and make the battery
   checkpoint use a worktree instead of `git add -A` in the shared tree — it was a blanket checkpoint
   that committed the deletion of the founder's volume rule on 2026-10-29.

Measured cost of not doing it: three separate pieces of work lost in eight days (2026-10-25 sixty-eight
commits stranded, 2026-11-02 two sections of one file, plus four orphaned stashes going back to August).
