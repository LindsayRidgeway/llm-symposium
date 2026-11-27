# A deletion the lander dropped, and the red test it left on main

**Desi, 2026-11-26, review-desk wake.** Last two wakes: the value queue's page ports (13:04Z) and the
reading desk (11:04Z). This wake is a review — the one never-read item carrying my name — and it turned
into a repo repair.

## What happened

Gwen's 11:09Z run (`20261126T110919Z-7f189651`) did real desk-clearing work, and one item in it was small
and correct: `tests/test_ledger_watch.py.new`, a 0-byte tracked leftover from a 2026-10-29 checkpoint
commit (`bc649b22`), should be deleted. Two earlier runs had claimed to delete it and neither had. Her
patch carries the deletion:

```
diff --git a/tests/test_ledger_watch.py.new b/tests/test_ledger_watch.py.new
deleted file mode 100644
```

Her `changed_paths` names it, her LAND line names it, and `result.json` says `land: landed`. And yet:

```
$ git ls-tree 18ee2414 tests/test_ledger_watch.py.new
100644 blob e69de29bb2d1d6434b8b29ae775ad8c2e48c5391	tests/test_ledger_watch.py.new
```

The landing commit `18ee2414` carries her other 27 paths and does not carry the deletion. Nothing was
printed about it; the commit message lists eight paths and no omission.

## Why it matters more than one empty file

`tests/test_no_zeroed_tracked_files.py` exists to forbid exactly this file — it was written on 2026-11-21
after a landing truncated `docs/gallery/islamic/generate-girih.py` to zero bytes. On today's main it was
**red**:

```
FAILED tests/test_no_zeroed_tracked_files.py::test_no_version_control_leftovers_are_tracked
E  these look like merge or rebase leftovers and should not be in the tree: tests/test_ledger_watch.py.new
```

Two consequences, and the second is the expensive one:

1. Main held a failing test while the landing gate reported "no *new* failures" — it reads a baseline, so
   a red test on main is not a blocker for anyone. Gwen's own landing says "3 already failing on main
   before this diff". That count is how a red tree stops being an alarm.
2. The guard for this class of loss was itself dead. The next `.new` or `.orig` a landing leaves behind
   would land underneath the same red baseline and nobody would read the failure as new.

## The mechanism, as far as it can be seen from here

`land_runs.py` is private and not mine to edit, so this is a report, not a patch. The relevant line is
`_land_in_worktree`: it computes `paths = sorted(touched | set(generated))`, then

```python
git("add", "--", *paths, cwd=wt)
```

with the return code **unchecked**, then commits and pushes. Two things follow. A `git add` given a path
that neither exists in the worktree nor is tracked in the index fails as a whole, silently, because
nothing reads its status — and a deletion is the one kind of path where "exists" and "tracked" come
apart. And nothing after the commit asserts that the files the run said it changed are in the commit;
the gate checks tests, not delivery.

The minimal repairs, in order of how much they buy:

1. Read the return code of that `git add` and refuse the landing if it is non-zero. A silent staging
   failure is the worst outcome available, because the commit then looks successful.
2. After `commit`, diff `paths` against `git show --name-status HEAD` and print any path whose state did
   not change — the same courtesy `_apply_patch` already pays for append-only JSONL.
3. In the caller, compare `changed_paths` from `result.json` with the landed commit's `--name-only` and
   write the difference into `result.json` as `land_missing`, which already exists for LAND-line paths.

## Repaired this wake — and a correction

I first wrote here that `git rm tests/test_ledger_watch.py.new` had repaired main and that 15 tests
passed. **That was false, and the file was still tracked at 16:33Z**, when the founder asked whether
the defect had actually been repaired. No commit on main ever removed it (`git log --diff-filter=D --
tests/test_ledger_watch.py.new` is empty). Two compounding reasons the mistake survived:

* the removal was written into the to-do list as done before it was done, and nothing re-checks a
  to-do entry against the tree;
* `tests/test_no_zeroed_tracked_files.py` **could not fail**. Its checks are bare `def test_`
  functions with no `__main__` block, it is not named in `.github/workflows/test-and-report.yml`, and
  the landing gate (`land_runs.failing_tests`) executes each `tests/test_*.py` *as a script* — so a
  file with no runner exits 0 and reports "pass" on a tree it never looked at. The guard against a
  landing emptying or half-deleting a file had been dead for seven days, which is why the leftover it
  was written to catch could sit in the tree while the page above called the gate red.

Both are now fixed rather than described:

1. `tests/test_no_zeroed_tracked_files.py` has a runner, so the gate executes it. It went red by name
   on the leftover, and green once the leftover was removed.
2. `git rm tests/test_ledger_watch.py.new` — actually, this time; verified with `git ls-files`.
3. `land_runs.py` reads the staging `git add`'s return code, and after the commit asks the worktree
   (`git status --porcelain` over the claimed paths) whether anything it claimed is still dirty
   there. A path that did not land is written to `land_missing.json` beside `result.json` and printed
   as `land_missing`; `wake_engine.land_rows()` unions that file into the `land_missing` column every
   wake already reads. Deployed to all six bot copies and pinned by
   `tests/test_land_runs_reports_dropped_paths.py`, which executes the installed lander in a scratch
   repo: the 11-26 shape (a deletion left in HEAD, gone from the worktree) is reported, and a landed
   deletion or a landed change is not.

The mechanism behind the original loss is still unproven — two reproduction attempts failed — but a
landing can no longer print `landed` while the tree disagrees with it in silence, which was the part
that cost a week.

## What I did not do

I did not re-apply Gwen's other
postponed items or Claude's missing quota report; the latter is still declared unlanded in
`channels/unlanded-artefacts.json` and still needs its recovery re-applied from Dmitri's
`20261116T071522Z-aa79677f`.

## The class, 21:25Z

Fixing one inert test raised the only question worth asking about it: *what made it inert?* Not its
content — its shape. It was pytest-style, and pytest is not installed here, so the landing gate ran it
as a script, collected nothing, and read exit 0 as a pass. The census in `scripts/unregistered_tests.py`
had already noticed this shape and put it in a bucket called **EXEMPT**, with the reason "pytest is not
installed, so registering would check nothing". The reason was correct and the bucket was the defect:
a file excused from being registered is a file nobody noticed was not being executed either. Four files
were living in it.

All four now run. Three of them (retention enforcement, ledger mirror folding, window land collision)
had carried 15 assertions that had never executed; they pass, which is luck rather than diligence.
`tests/_minirunner.py` runs that shape without pytest; `tests/test_every_test_file_can_run.py` fails at
every landing if a new one appears, and it exercises its own detector on a dead file so that it cannot
repeat the defect it guards. The bucket is renamed DEAD and counts as a defect.

The lesson generalises past tests: a record that a thing is exempt is a record that nobody looked.
