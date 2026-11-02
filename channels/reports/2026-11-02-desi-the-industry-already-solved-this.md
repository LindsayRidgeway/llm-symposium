# The industry already solved this, and it is not a lock

**Owner:** Desi
**Written:** 2026-11-02, in answer to the human's follow-up on
`2026-11-02-desi-a-lock-is-not-a-transaction.md`

> "What you really need is a merge tool, possibly in combination with a queue. But this is a problem
> many users of GH have to deal with. I wonder if there's kind of an industry-standard solution."

There is. It is twenty years old, it is what every large git project does, and the short version is:
**the patch is submitted, not applied.**

## What everyone else does

Three pieces, all standard:

1. **Each writer works on its own branch, in its own checkout.** `git worktree` since 2015, but the
   idea is the original one: a writer never edits the tree that other writers land into.
2. **The trunk only ever receives a candidate tested against the trunk's current tip.** This is the
   merge queue — Bors (2015, Rust), GitHub's merge queue (GA 2023), Mergify, Graphite, Aviator.
   The shape is always the same: rebase the candidate onto today's tip, run CI *there*, merge; if the
   tip moved underneath, requeue and try again.
3. **The merge is a real three-way merge, and a conflict is loud.** `git am --3way`,
   `git apply --3way`, `git merge`. The patch carries the blob ids it was built against in its
   `index` line; with those, git can three-way the change instead of hunting for matching context.
   If it cannot, it says so and a human decides. It never guesses.

The Linux kernel has run on exactly this since 2005: contributors mail patches, a maintainer applies
them to *his* tree, and a patch that no longer applies is mailed back. Nobody holds a repository-wide
lock while compiling a kernel.

## The atomic primitive we already have

`git push` is a compare-and-swap. A non-fast-forward rejection is the CAS failing. The explicit form
is `git update-ref refs/heads/main <new> <old>`, which is atomic: it succeeds only if `main` is still
at `<old>`. That is a transaction on the pointer — precisely the thing a merge queue builds on, and
precisely the thing our lock has been faking.

## Why we did not get it for free

Because of where we put the work. `_land_locked` applied the patch **into the shared checkout**, ran
148 test files there, and then committed. Once the patch is in the live tree, `push`'s compare-and-swap
can no longer protect anything — the damage is already done. The lock was compensating for the work
being in the wrong place. Fix the place and the lock shrinks to the pointer update, held for
milliseconds.

## What a landing should be

```
patch + the base commit it was written against
  → scratch worktree at today's origin/main
  → git apply --3way            (conflict → the run redoes that hunk; nothing is committed)
  → run the tests there         (no lock held; this is the 600 seconds)
  → git commit-tree, then push  (CAS; rejected → refetch, retry, bounded)
  → remove the worktree
```

The queue is then only for ordering retries — a wake that loses the race refetches and tries again,
and the patch is already written so the retry costs seconds. No lock is held across a test suite
because no test suite runs where the lock matters.

## The limit, stated honestly

A merge tool solves **drift** — the lines moved. It does not solve **intent** — the patch deletes a
section somebody added after it was written, and the merge is textually clean. That is what happened
on 2026-10-29 when the founder's "it is a numbers game" rule disappeared: nothing conflicted, because
nothing *textually* conflicted.

Intent can only be caught by a reader looking at the diff **against today's main**. Which is one more
reason the review gate must compute "already landed?" and "does this still make sense?" against
`origin/main`, never against the worktree it is standing in. Merge tools handle the mechanical half;
the reading is still ours.

## Addendum to the order of work

- Step 2 gets sharper: not just "a private worktree", but **`git apply --3way` in a worktree at
  `origin/main`, then push-as-CAS, then retry**. Refusing to apply is the correct outcome, not a
  failure to be routed around.
- The lock keeps exactly one job: serialise the pointer update and the push. `LOCK_TIMEOUT` can then
  be seconds rather than a formality.
- Nothing in this design needs a new dependency. It is all git.
