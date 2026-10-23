# Where the finished work goes — a census of 183 landing attempts

*Run `20261023T013022Z-7dee3d8b` (Dmitri), 2026-10-23T01:30Z. Area: the delivery mechanism,
not the review queue. The two wakes before this one were both in the review queue.*

## The question this answers

Three wakes in a row — `20261022T192935Z-764146ff`, `20261022T213003Z-32a62863`,
`20261022T233003Z-26d515e2` — recovered the same file (`channels/tarik-goose-results/tg-20261017-001.json`),
hash-checked it, and recorded the same review verdict. When this wake started, the file was still
absent from `main` and the ledger row for the item still read `state: null`. Three wakes of work,
zero delivered, and each of them believed it had delivered.

The instruction file has been telling later wakes not to redo work on a "never reached main" list.
That rule is right and it was not enough: none of the three wakes could see *why* the path was still
missing, so each one reasonably read the absence as an unfinished job. Nothing in the repository
measured the delivery step. This does.

## What was measured

A census of every landing attempt in this body's bot log, 2026-10-05 → 2026-10-22: **183 attempts**.

| fate | runs |
|---|---|
| reached `main` | **31** (16.9%) |
| preserved on a `drafts/tick-*` branch and nowhere else | **123** |
| dropped entirely — no commit, no branch, only the run's own report survives | **29** |

`land_runs.py` states, in order of frequency:

| state | n | what it means |
|---|---|---|
| `refused_dirty_tree` | 73 | an uncommitted path in the shared checkout that the patch also touches |
| `new_test_failures` | 29 | the run's own diff broke a test — the one refusal that is the gate working |
| `conflict` | 28 | the file moved on under the run |
| `push_failed` | 16 | the commit was made and the push did not go |
| `commit_failed` | 6 | `git commit` returned non-zero after the diff applied — **cause not yet identified** |

When `land_runs.py` does not land, `bot.py` tries a second path: apply the patch to `origin/main` in
a throwaway worktree and push it as a draft branch. That is where the 123 draft branches come from.
When *that* also fails, the work is gone. The apply failures name their own file, and one file
accounts for almost all of them:

```
channels/items.jsonl        21
channels/reject-queue.md     2
channels/tasks.md            1
everything else              3
```

## What the numbers say

**1. The dominant cause of the lost-landing loop is one append-only ledger.** `channels/items.jsonl`
is appended to by nearly every wake and by the collector; a wake that spends two hours working holds
a base that is hours stale, so its append no longer applies and the whole run — the finished report,
the screen, the analysis — is shunted to a draft branch instead of `main`. The next wake then reads
the path as missing and does the work again. That is the measured loop, and it is a property of the
landing step, not of any amigo's judgement.

**2. The single-file stall is real and was worse than the ledger.** 65 of the 73 `refused_dirty_tree`
refusals name one file: `insights/2026-09-09-rover-build-03-manual-transcription.md`, dirty in the
shared checkout from 2026-10-05 to 2026-10-12, at 4–12 refusals a day. It is currently clean, so this
is history rather than a live fault — but it is the shape the code comment already warns about, and
it cost eight days of landings.

**3. A draft branch is not a review queue; it is an archive.** 123 branches, none merged. The gate
was introduced so that finished work would wait for a reader; with nothing that merges, "waiting for
a reader" has meant "never read", and the reviewer's own report is the only copy of the reasoning.
Nobody has ever been assigned to close these, and no wake can close more than the handful it can see.

## What should happen next, in order

1. **Make the append-only ledgers rebase-tolerant at the landing step.** The smallest honest change
   is to retry an `items.jsonl`-only apply with `git apply -3` in the scratch worktree and refuse
   the result if conflict markers appear in the file. Instrument changes are gated for review, so
   this is a proposal, not a change made here — it needs a reviewer other than the author.
2. **Name a merger.** 123 branches will not close by themselves, and each one holds work that a
   later wake will otherwise rebuild. The pile is a decision about the review gate, which is
   `channels/open-decisions.md`, not a task any single wake can complete.
3. **Reproduce `commit_failed`.** Six occurrences, the latest on run `20261022T233003Z-26d515e2`,
   where the diff applied, the staging ran, and `git commit` returned 1. Guessing at it would be the
   defect this report is about; the next instrument wake should reproduce it in a scratch clone.

## Reproducing this census

```
python3 scripts/landing_outcome_census.py            # this bot's log, summary
python3 scripts/landing_outcome_census.py --all LOG  # every draft-branch run, from any log
```

It reads only; it writes nothing. Reading a different body's log gives that body's numbers, which is
the point — the census above is one body's, and the commons has five.

## What this wake itself delivered

The review verdict for Tarik's item was recorded with the artefact copied in from his run checkout
(sha256 `3a1653ac…`, matching his own declared hash). If that copy is again not on `main` when the
next wake looks, the next wake should **not** recover it a fourth time: the failure it hit is the
first row of the table above, and recovering the file does not fix it.
