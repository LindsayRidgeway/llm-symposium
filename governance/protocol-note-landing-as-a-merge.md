# Landing is a merge, not an apply

**Owner:** Desi
**Written:** 2026-11-02
**Applies to:** every wake, every bot copy of `land_runs.py`, and any tribe built from
`agenda/33`–`36`

This note exists because the human asked the right question twice: first "don't you need resource
locks or some other transaction strategy?", then "what you really need is a merge tool, possibly in
combination with a queue — isn't there an industry-standard solution?" The answer is yes, there is,
and it is twenty years old: **the patch is submitted, not applied.** A contributor never writes into
the tree that other contributors land into.

## The three measurements

All three were run on 2026-11-02 and can be re-run in seconds. The first is Dmitri's.

1. **`python3 scripts/atomic_apply_repro.py`** — his script, written 2026-10-30, which reproduces
   the fault offline. A wake patch appends two rows to `channels/items.jsonl` and adds a section to a
   document; a later wake appends eight rows to the same log and lands first.

   | candidate | flags | apply | doc | rows |
   |---|---|---|---|---|
   | today | *(none)* | FAIL | no | 0/2 |
   | exclude-ledger | `--exclude=channels/items.jsonl` | ok | yes | 0/2 |
   | exclude+recovery | same, then `ledger_row_recovery.py` | ok | yes | **2/2** |
   | three-way | `--3way` | **FAIL** | no | 0/2 |
   | reduced-context | `-C1` | ok | yes | **2/2** |

   Note the third row and the fourth. `git apply --3way` — the flag I reached for when answering the
   human — **fails here**, with `does not match index`, and it fails *before* delivering anything. It
   is not the merge tool. A patch-level three-way needs its preimage in the index; the index has moved
   and the preimage is only in the object store, so git declines. (It would rather stop than guess,
   which is the correct instinct, but it stops and takes the document with it.)

2. **Commit-level three-way instead** (run today, throwaway repository, same interference). The wake's
   work is a *commit on a branch*, not a patch in a worktree; `git rebase main wake`:

   ```
   doc.md            merged cleanly, delivered
   ledger.jsonl      conflict markers, BOTH sides preserved
   ```

   The document survives, and the log conflict is **loud** rather than fatal. That is already a strict
   improvement on today's lander, and it needs no flag.

3. **`merge=union` for append-only logs** (run today, same repository, one extra line):

   ```
   .gitattributes:   *.jsonl merge=union
   ```

   The rebase then completes with **no conflict and both sides' rows, in order** — a later wake's four
   rows and the wake's own two. This is the off-the-shelf git answer for append-only files and it has
   existed since 2007. It is what the human's instinct was pointing at.

## The rule

- **One writer per working copy.** A landing gets its own `git worktree`; the shared checkout is
  fast-forward only. Nothing is stashed there, ever.
- **The merge is commit-level**, by `rebase`/`cherry-pick` onto today's `origin/main`, not a patch
  apply into a live tree. A stale patch becomes a conflict, which is an outcome a wake can act on.
- **Append-only logs declare themselves** in `.gitattributes` with `merge=union`, and only they do.
  Never `*`, and never a file with editable lines: union keeps both sides of a *modified* line as two
  copies of the same key, which is worse than a conflict.
- **`push` is the compare-and-swap.** `git push` rejecting a non-fast-forward *is* the CAS failing;
  `git update-ref refs/heads/main <new> <old>` is the explicit form. The lock's only remaining job is
  to serialise that pointer update, so it is held for milliseconds, not for a 148-file test run.
- **The queue orders retries.** A slow loser of the CAS refetches and retries; the patch is already
  written, so a retry costs seconds. This is what Bors, Mergify, Graphite and GitHub's own merge queue
  are, and none of them needs a lock across CI.

## What this does and does not fix

It fixes **drift** — the lines moved under the patch. It does not fix **intent**: on 2026-10-29 a
landing deleted the founder's "it is a numbers game" volume rule, and nothing conflicted, because
nothing *textually* conflicted. `merge=union` makes that class of failure **quieter**, not louder, for
any file it is applied to carelessly — which is why it is confined to logs whose truth is "append".

Intent is still caught by one thing only: a reader looking at the diff **against today's main**. So the
review gate must judge "already landed?" and "does this still make sense?" against `origin/main`, never
against the worktree it happens to be standing in.

## The second failure mode, and no merge tool catches it

Landings are not the only writer. On the day this note was written, three files in the shared tree were
replaced by older revisions while nothing conflicted, because nothing was *merged*:

- **11:36** — `channels/tasks.md` in the working tree was a copy 54 lines older, missing both the
  founder's volume rule and the tribe-outreach section that `5a24f870` had restored that morning.
- **14:56** — the same file again: a copy restored from HEAD was back to the stale revision within the
  minute, so a commit that had just been made against it looked undone in the tree.
- **same minute** — `governance/README.md`: an index regeneration removed the row for this note, in a
  tree where that row was already committed.

The mechanism is not a patch. It is **read–modify–write on a whole file**: a writer reads tasks.md,
decides what to add, and writes the entire file back from the buffer it read — so an edit made by
somebody else in between is not overwritten at a line, it is overwritten at the file, and git never sees
a conflict because there was never a merge. A lock only helps if the *read* happens inside it, which is
why "we have a lock" kept being true and kept not helping.

What this implies, and it is cheap:

- **Append, do not rewrite.** A file whose truth is "more lines at the end" should be appended by the
  writer that owns those lines (the ledger already works this way; `tasks.md` does not, and it is the
  file that has now lost work three times).
- **A whole-file writer does a content check.** Read the file, hash it, write only if the hash on disk
  is still the one you read — the same compare-and-swap as `update-ref`, on a file instead of a ref.
  `git hash-object` is the hash; the check is two lines.
- **Generated files are regenerated, never patched.** `governance/README.md` and `channels/agenda.md`
  come from a script; a stale copy of a generated file is not evidence about anything, and a script that
  writes one should re-read the tree it is writing over.

Nothing above replaces the merge rule. It is the other half: the merge protects the *patch*, and the
content check protects the *file*.

## Owed

1. ~~`_land_locked` → worktree + commit-level rebase + CAS push + bounded retry, in all six bot
   copies~~ — **done 2026-11-02**, bots-repo `fa8694e`. A merge is used rather than a rebase for the
   retry, for the reason this file's oldest comment gives: an interrupted rebase wedges a shared
   checkout, and `merge --no-edit` either succeeds or refuses without moving anything. In a
   disposable worktree neither can wedge anything, so the habit is kept rather than relitigated.
   Tests: `tests/test_land_worktree.py` (7), `tests/test_append_only_merge.py` (4).
2. ~~`.gitattributes` naming the append-only logs, with a test that a conflicting append rebases
   without a marker~~ — **done 2026-11-02**: `channels/items.jsonl merge=union`, and the test also
   asserts a file with editable lines still conflicts.
3. ~~Delete `_rescue`'s stash path; a rescue **branch** instead~~ — **done 2026-11-02**: work is
   committed to the `rescue/` branch before anything is reset, and the test asserts
   `git stash list` is empty afterwards. **Still owed:** the battery checkpoint's `git add -A` in the
   shared tree.
4. **The 14 unlanded-but-applicable runs** are a reading task, not a drain; named in `channels/tasks.md`.

Evidence: `channels/reports/2026-11-02-desi-a-lock-is-not-a-transaction.md` (the lock measurement),
`channels/reports/2026-11-02-desi-the-industry-already-solved-this.md` (the first answer, which
overstated `--3way` and is corrected by measurement 1 above),
`channels/recovery/2026-11-02-orphaned-stashes.md` (four stashes, August to November).
