# The shared checkout is not a workspace, and no hook can make it one

**Desi — 2026-11-02, evening.** Owner-facing. This closes the top item in `channels/tasks.md`,
*"The shared checkout must become read-only for everyone"* — and it closes it **partly**, with the
part that is left named at the end rather than implied.

## What the item asked for, and where its premise was wrong

The item said: *"Sessions should work in their own worktree; the shared checkout should take `git
fetch` and the fast-forward only."*

The first half is **already true and has been for weeks.** `local_tick.run_session()` does
`git clone --single-branch` into `run_dir/repo`, removes `origin`, and tells the wake *"This is a
private checkout for review, NOT the live shared repository. Do not push."* No amigo wake has ever
edited that tree. I wrote the item without reading the code that runs wakes, and the first thing
this session did was correct it.

So the writers into the shared checkout were never the wakes. They were **three bot functions and
the human's own sessions** — and one of the three is me, tonight, typing in that directory. That is
why "read-only for everyone" was never achievable as written, and why the honest version of the
goal is: *no automated process writes there, and a person's uncommitted work there is never moved
by one.*

## The four writers, measured

| writer | copies | what it did to the shared tree |
|---|---|---|
| `record_push.push_record` | 6 | `git pull --rebase` — on **every human message, in every body** |
| `bot.py file_tasks` | 2 | `add`, `commit`, `pull --no-rebase`, `push` — **outside** the lock it had just taken |
| `bot.py battery_guard_tick` | 2 | `git add -A`, `commit`, `push` — on `main` |
| `land_runs` Phase 1 | 6 | commits record paths, path-scoped, under the lock (already correct) |
| `scripts/append-goose.py` | 1 | `pull --no-rebase` in the shared tree — **still open** |
| `scripts/daily_report.py` | 1 | `add -- <staged>`, `commit` — scoped, but on `main` — **still open** |

### What `pull --rebase` actually did — and it is not what I first wrote down

My first draft of the `record_push` docstring said it autostashed the tree and ate the work. Then I
checked. `rebase.autoStash` is unset in local, global **and** system config, and git 2.48 therefore
refuses outright:

```
pull: error: cannot pull with rebase: You have unstaged changes.
error: Please commit or stash them.
```

Exit 128, tree untouched. So that line never ate anybody's work. **It stopped pushing the record** —
and the caller dropped the exit code, so a body whose record never left this Mac looked identical to
a body whose record landed. That is the same defect this module was written to fix in September,
reappearing one layer down. In a tree six bodies write to, a refusal on a dirty tree is not an edge
case; it is most of the time.

## The attempt that failed, because a negative result is still a result

The obvious answer is a git hook: refuse the dangerous operation whatever calls it. I built two and
measured both. Neither works, and *why* is worth keeping.

1. **`pre-rebase`** refuses on stderr, exits 1. It fires for a real rebase — and **never fires for
   `pull --rebase` that fast-forwards**, which is the common case here. Measured: the pull
   fast-forwarded, created an autostash anyway, and left
   `<<<<<<< Updated upstream / RIVAL / ======= / MY EDIT / >>>>>>> Stashed changes` in a tracked
   file plus `stash@{0}: autostash`. The hook was never consulted.
2. **`reference-transaction`**, aborting any update to `refs/stash`. This *does* fire, and it aborts
   the ref update — **after** the working tree has already been rewound. Result: the conflict
   markers are still in the file, and the stash object is now *unreachable* instead of named. It
   makes recovery worse, so it is not in the repository.

**The finding: git's `pull` is not transactional.** It fetches, moves the working tree, and only
then re-applies what it set aside. There is no hook point before the move. So this cannot be fixed
at the git layer, and any future attempt to fix it there should start from this paragraph rather
than from a hook.

## What actually shipped

One rule, applied three times: **a bot moves commits, never files.**

`channels/record_push.py` — and its six copies beside the bots, byte-identical — now exposes
`push_paths(repo, paths, message)`. It is the pattern `land_runs` already used:

1. `git fetch` (remote-tracking refs only);
2. cut a **throwaway worktree** at today's `origin/main`;
3. **copy** the changed record files into it, under the checkout lock, for milliseconds;
4. commit there, push there, and on a rejected push `rebase` **there** — the disposable tree, up to
   three attempts;
5. remove the worktree, then try `git merge --ff-only` in the shared checkout.

Step 5 is the only write it makes to that tree, it can only add commits, and git refuses it
wholesale rather than partially when a session's uncommitted work is in the way. A refusal is
printed, not filed as an error: `origin` is the record, and the checkout being behind is the design
working.

`file_tasks` in the two bots that have it now writes the file under the lock, leaves it there, and
hands `[FILED_TARGET]` to the same `push_paths` — instead of four git commands outside the lock it
had just taken.

`battery_guard_tick` no longer stages anything. `snapshot_checkout()` runs `git stash create` — which
writes a commit object holding the working tree *and* the index and touches nothing else: no ref, no
file, no index change, no stash-list entry — and pushes that object to `refs/heads/wip/battery-<stamp>`.
Measured before shipping: an unstaged edit and a staged new file both land in the snapshot, `git
stash list` stays empty, HEAD does not move, and the tree is left dirty on purpose.

## The tests, and the standard for calling it settled

Settled means a test exists that **fails on the old code**. These four fail on the old
`record_push.py` and pass on the new one:

- `test_an_uncommitted_edit_survives_a_record_push` — a rival edits *the same file* the session is
  editing; after the record push the session's line is still in the tree, `git stash list` is empty,
  and HEAD has not moved. On the old code it fails with the `cannot pull with rebase` above.
- `test_the_record_lands_on_origin_although_the_tree_is_not_moved` — refusing to move the tree is
  not refusing to deliver.
- `test_a_rejected_push_is_retried_in_the_worktree_not_the_shared_checkout` — origin moves between
  fetch and push; both records end up on main, no stash is used.
- `test_the_push_path_cannot_pull_stash_checkout_or_reset` — structural, over all seven copies.

That last one **passed on the old code on its first run**, which is the most useful thing that
happened today: it looked for the string `"pull"` among the arguments of a call, and the old code
built the command as `pull = ["pull", …]` and passed the *variable*. A check that reads the shape of
an expression instead of the words in it is a check that has gone blind while still reporting that
it looked. It now reads every non-docstring string literal in the module.

`tests/test_battery_snapshot.py` (3 tests) fails on the old `bot.py` and passes on the new.
`tests/test_file_tasks_guard.py` grew one test asserting the filing reaches `push_paths` with
`channels/tasks.md` and never a bare `pull`.

## The four stash entries, triaged rather than believed

`git stash list` held four entries, three named `autostash`. They are now also reachable as
`recovered/autostash-20261017`, `recovered/autostash-20261022`, `recovered/autostash-20261101` and
`recovered/wip-20260829`. Nothing was dropped; nothing was restored.

`stash@{0}` (2026-11-01) is the one that looked like a casualty: two `channels/items.jsonl` rows
absent from today's file, for `codex-20261020T160238Z-a2779210` and `20261021T131453Z-b52bdd68`.
Checked rather than assumed: **both ids already carry `reviewer: gemini`, state `accomplished`,
filed `2026-11-02T01:03`** — the session that lost them re-recorded both verdicts an hour later.
The stash holds a superseded draft. Restoring it would have appended two duplicate verdicts to the
ledger of two already-closed items, which is the kind of "recovery" that costs a reader an hour.

## What is still open, named

1. **`scripts/append-goose.py` still runs `git pull --no-rebase` in the shared checkout**, and
   `scripts/daily_report.py` still commits there. Both are in-repo scripts, so they can import a
   shared helper; neither has been changed. They are the "silently does nothing" class (a merge-pull
   refuses on a dirty tree) rather than the "eats work" class, which is why they were not tonight's.
2. **A person's manual session is still the biggest writer**, and it is the one the hooks cannot
   help. Tonight's answer is that the automated writers no longer move that tree, so a session's
   uncommitted work is no longer moved *by a bot*. It is still not safe from the session itself.
3. **Four of six bodies have neither `file_tasks` nor a battery guard** (claude, gemini, tarik,
   gwen — checked by AST, not by grep). Their `bot.py` files are a different, thinner shape. A
   request raised in their chats still never reaches `channels/tasks.md`.
