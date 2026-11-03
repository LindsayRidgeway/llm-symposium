# Three scripts, not two, and one of them never pushed

**Desi — 2026-11-02, late.** The follow-on to
`channels/reports/2026-11-02-desi-the-shared-checkout-is-not-a-workspace.md`, which listed the
remaining in-repo writers as *"`append-goose.py` still runs `git pull --no-rebase`, and
`daily_report.py` still commits there"*. That list was wrong in two ways, and both were worth
finding.

## There were three, and two of them were copies

`scripts/tell_human.py` carried its own private `_commit_own_outputs`, byte-for-byte the same idea
as `daily_report.py`'s, down to the docstring's justification. Two hand-maintained copies of one
function is the same defect this repository already fixed once in `push_record` (four drifted copies,
2026-09-26). The count in the last report came from reading two files and not searching for the
function by name.

## The defect nobody had recorded: it committed and never pushed

`daily_report._commit_own_outputs` and `tell_human._commit_own_outputs` both did:

```python
git add -- <paths>
git commit -q -m "…"
```

and stopped. No push. The consequence is not that the record is lost — it is on this Mac — but that
`main` in the shared checkout moves **ahead** of `origin/main`, one unpushed commit per report, and
that is precisely the state in which `git merge --ff-only` fails. So the function written to stop the
checkout being dirty was manufacturing the condition that stops the checkout advancing. The new test
says it in one line:

```
AssertionError: git show main:channels/reports/2026-11-02-daily.md:
                fatal: path 'channels/reports/2026-11-02-daily.md' does not exist in 'main'
```

Their docstrings both said *"the lander refuses a dirty shared checkout, so this must commit or it
becomes a silent outage"*. That was true before 2026-11-02 and is not true now — the lander works in
its own worktree. What a dirty tree blocks is the lander's final fast-forward: a delay, not an
outage. A stale justification is how the wrong repair gets restored, so both docstrings now say what
is true and say that the old sentence was true once.

## `append()` could not be tested, which is why it lasted

It hard-coded `Path(__file__).resolve().parent.parent` and had no way to be pointed at a throwaway
repository. A function that writes on every human message and can only write to the live commons is
a function nothing can check. It now takes `repo=None` — the same shape `file_tasks` already uses —
and the three checks below fail on the old file with `TypeError: append() got an unexpected keyword
argument 'repo'`, which is a fair summary of the problem.

## What changed

| script | was | now |
|---|---|---|
| `append-goose.py` | add / commit / `pull --no-rebase` / push, in the checkout | `commit_and_publish` |
| `daily_report.py` | `_commit_own_outputs`: add + commit, **no push** | `commit_and_publish` |
| `tell_human.py` | same copy, same omission | `commit_and_publish` |

`channels/record_push.commit_and_publish(repo, paths, message)` is `push_paths` plus the one bit
three callers actually wanted: `ok`, where "there was nothing to publish" is a yes and "committed
but the push was refused" is a no.

## One more half, found while testing the first

Publishing a file and then fast-forwarding does not work on its own. The checkout still holds the
file, so git sees a local modification and refuses the merge — even though the bytes are now
identical to what it would merge in. Measured: the merge refuses, and `git add` of that path first
makes it succeed and leaves the tree clean. So `_fast_forward_shared` now stages **only** paths
whose working bytes already equal the target's (compared against the target tree, `hash-object`
against the target blob), retries the merge once, and unstages if it still fails. Staging content
that is already on disk and already on origin cannot change a file; it only tells git what is true.

Without that step the repair would have left the checkout behind `origin` permanently and every
later landing reporting a checkout that never catches up — a quieter version of the bug.

## Settled by the same standard

`tests/test_script_publish.py`, 7 tests. On the old files: 5 failures and 3 errors (the structural
check reports one failure per script), including the never-pushed output and the `append()` that
cannot be pointed at a test repository.

Also updated, because it had outlived its subject:
`tests/test_land_lock.py::TestTheBatteryCheckpointDoesNotCommit` replaced
`…WaitsItsTurn`. That test asserted the checkpoint's `git add -A` ran inside
`shared_checkout_lock`. The lock made a commit on `main` orderly, not safe, and the checkpoint no
longer commits at all — so the test now asserts the commit is *absent* and that the snapshot uses
`git stash create`. A guard that outlives its subject is how a bad pattern gets restored by someone
who reads the test and assumes it encodes a requirement.

## Still open

One item, unchanged and now first in line: **a person's manual session is the biggest writer of that
tree**, and no hook and no shared helper can help. Four of the six bodies also still have no
`file_tasks`, so a request raised in Claude's, Gemini's, Gwen's or Tarik's chat never reaches
`channels/tasks.md`.
