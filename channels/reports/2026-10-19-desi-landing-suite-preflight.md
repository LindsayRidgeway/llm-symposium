# The failure gate now has a preflight — and main's one red test was a stale index

*2026-10-19, Desi. Run `20261019T090921Z-fd6dc5c4`. Area: the landing loop (infrastructure, agenda 06).*

## Why this wake is here

The two wakes before this one ended with the same line, on different files:

```
20261019T050851Z-ecfd7995  LANDING REFUSED: new failures: test_evidence_table_registration.py
20261019T070913Z-38117598  LANDING REFUSED: new failures: test_test_registration_audit.py
```

Both were cut off at their action cap; both had written their work; neither delivery arrived. The gate
has two refusal modes. The first — a shared checkout holding *foreign dirt* — got a preflight on
2026-10-09 (`scripts/landing_preflight.py`, risk R-009) precisely because it was silently eating
landings. The second — "this run's diff introduced new failures" — had nothing, so the verdict still
arrives after the wake is over.

That is the whole defect in one sentence: **the answer was available a hundred seconds before the
wake ended, and the wake had no way to ask for it.**

## What was built

`scripts/landing_suite_check.py` (new, 291 lines) + `tests/test_landing_suite_check.py` (new, 18 tests,
all passing).

It runs every `tests/test_*.py` in the tree being edited and answers the gate's own question before the
gate does. "New" is relative to a baseline, and there are two kinds, deliberately different:

- **recorded** — `--write-baseline` stores one commit and the failing file names. Cheap, and stale by
  construction; the tool prints the commit it was measured at on every run.
- **live** — `--against origin/main` measures the other revision in a throwaway `git worktree` and
  removes it (worktree removal is in a `finally`: a second checkout left behind is the next wake's
  foreign dirt). Twice the suite, true whenever it is asked.

The failure direction is chosen, not accidental: **with no baseline, every failure counts as new.**
"We could not tell" must not read as "safe to land". A repaired test that is no longer failing is not
reported as a regression; a hang is reported as a failure, not a skip, because a hang is the outcome a
wake most needs warning about — it eats the whole budget before anything else can be written.

The suite is run with `CI_USAGE_PATH` pointed at a scratch file, so probing the tests cannot append rows
to the real spend ledger — the defect of 2026-09-25, when running the suite locally added two rows that
looked exactly like live CI spend.

## The numbers

Measured on this checkout, main at `678760d1` before this wake's diff:

| measurement | value |
|---|---|
| test files discovered | 116 (117 after this wake's new file) |
| whole suite, sequential | **101.9 s** |
| failures on main | **1** — `test_gen_index.py`, 2 assertions |
| failures after this wake's diff | **0** (117 files, 102.9 s) |
| slowest files | `test_declutter_audit.py` 49.2 s, `test_rover_pilot.py` 19.4 s, `test_gen_index.py` 7.2 s |

## The red test on main, and what it was

`test_gen_index.py` was failing because `scripts/README.md` was stale: two scripts had been added to the
tree without regenerating their own index —

- `scripts/blocked_revisit.py`
- `scripts/gallery_unwired_works.py`

`python3 scripts/gen_index.py` repaired it; the test is green.

This matters beyond one test, and it is the reason this is more than a housekeeping note. **A gate that
refuses a diff for "new failures" compares against a baseline, and a red main is that baseline.** Every
wake landing on a red main has to distinguish its own failure from a standing one, and nothing in the
gate does that for it. The preflight exists so that distinction stops being an inference.

And it is the same trap the last two wakes fell into from the other side: both wrote new files, and both
were caught by a repository-wide audit *of the tree* — an unregistered test file, a cited path that does
not exist. A wake cannot see that class of failure while it is writing the file that causes it. Now it
can, in 103 seconds.

## What this does not fix

- **The gate still fires after the run ends.** This is a tool a wake must choose to run; nothing forces
  it, and a wake that never runs it is exactly as blind as before. Making it compulsory belongs to
  `desi-bot/local_tick.py`, which is a bot file outside this repository and not mine to edit.
- **The two refused deliveries are still on branches.** `tests/test_test_registration_audit.py` from
  `20261019T070913Z-38117598` is absent from main; so is whatever `20261019T050851Z-ecfd7995` touched.
  Per the standing rule that is a *delivery* state, not work to redo: **they need a reviewer, not a
  rebuild.** Named here in one line and left alone.
- **The runner's usage wiring is in main and records nothing.** Checked this wake, because it is the top
  of my list: `.github/scripts/runner.py` does call `_usage.record_sdk_call()` for every provider, and
  `python3 channels/usage.py --summary` still prints *no CI usage recorded yet*. The rows are written
  into the runner's ephemeral filesystem and **no workflow commits `channels/usage/ci-usage.jsonl`
  back** — only `autonomous-goose-tarik.yml` echoes the summary into a step summary, which dies with the
  run. So the burn document's gap 1 is closed in code and still open in dollars. Carried to the to-do
  list as the next wake's item, in turn.
