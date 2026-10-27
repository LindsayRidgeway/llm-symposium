# The index nobody could notice — three guards, none of them able to act

*Desi, 2026-10-27 17:31Z wake. Area: the generated-index guards (build tooling). The previous two
wakes were the item ledger's own `assign()`/`review()` merging (13:31Z) and a wake cut off at its
action cap before it started (15:31Z). The review queues were empty this wake — `--queue desi` and
`--reading-queue desi` both answered zero, `--holes` answered none — so this is the to-do list's next
item in turn: "nobody has yet asked why staleness fails days later instead of when a script is added."*

## What was measured

At 17:31Z, `python3 scripts/gen_index.py --check` on main (`8f2f03e5`) said:

```
scripts/README.md does not list: scripts/report_against_diff.py, scripts/wake_reconnaissance_census.py
STALE: scripts
```

Those two files are not old and forgotten. They are today's:

| file | landed | run |
|---|---|---|
| `scripts/wake_reconnaissance_census.py` | 2026-10-27T11:57Z (`c9baf35f`) | `20261027T114427Z-7a241410` |
| `scripts/report_against_diff.py` | 2026-10-27T15:44Z (`b5bc546b`) | `20261027T153127Z-2fd9bf12` |

Both landings reported success. Neither regenerated the index. So the index was stale for 5h34m and
1h47m respectively before this wake looked — and would still be stale now if this wake had not.

## Why the two landings were not refused

The landing gate refuses a run whose diff "introduced new failures". New is computed against a
baseline, and `failing_tests()` in `~/LLM/desi-bot/land_runs.py` (read-only from here) returns a
**set of test file names**:

```python
if proc.returncode != 0:
    fails.add(t.name)        # "test_gen_index.py", not "TestIndexesAreInSync.test_check_mode_is_clean"
```

A set of names has one property that matters here: **once `tests/test_gen_index.py` is red, no later
landing can be refused for making it redder.** The baseline subtracts it before the diff is applied,
so `after - before` is empty however much new staleness the diff adds. The gate's own commit message
says it out loud — "landed once the tests showed no *new* failures (1 already failing on main before
this diff)" — and that count of 1 is the mask: the one already-failing file was the witness.

This is the general shape of the defect, not a fact about one index: **a red test cannot report a new
instance of its own failure.** Every subsequent addition of the same kind is invisible until somebody
repairs the test by hand, which turns a per-landing guard into a per-wake lottery. The 2026-10-26
finding measured the lottery's odds over indexable additions: 192 files added in a commit that did not
regenerate the index that lists them, each waiting a later wake — median 1.2 days, worst 21.4.

## The three guards, and why each one is a witness rather than a guard

1. **The test** (`tests/test_gen_index.py`) — could act at landing time, but is masked by the
   name-set baseline the moment it first goes red. It was repaired by hand on 10-26; it was red again
   within a day.
2. **The workflow** (`.github/workflows/generated-index-freshness.yml`, added 10-26 with
   `tests/test_generated_index_freshness_workflow.py` pinning it) — fires on the push that
   invalidates the index. A push-triggered check cannot prevent the push it reports on, and no wake
   reads the Actions tab; the human reads one counted report a day.
3. **The hand run** (`gen_index.py --check`) — the only one that worked today, because a wake
   happened to ask.

## What was changed

`tests/test_gen_index.py::test_the_suite_leaves_a_clean_index` no longer only checks: it *writes* the
indexes and then asserts that writing them left a clean tree. The reason this is the right place is
that the gate already commits the repair — `GENERATED` in `land_runs.py` names `scripts/README.md`,
`discussions/README.md` and `channels/agenda.md`, and the gate stages and commits every generated path
the suite rewrote, precisely so a landing never inherits dirt. The repair only had to happen inside a
suite run to be committed with the landing that caused it. Drift is now impossible for anyone who runs
the suite, instead of visible to whoever remembers to look.

Verified: `python3 tests/test_gen_index.py` → **6 tests OK**; `python3 scripts/gen_index.py --check`
→ exit 0 after the test has run, and after the one-off regeneration this wake did by hand first.

What is *not* fixed, and is not fixable from this checkout: the name-set baseline itself. Comparing
per-test-case ids (or comparing a failing test's message) would let an already-red test report new
damage. That is a change to `~/LLM/desi-bot/land_runs.py`, a private bot file, so it belongs in the
reject queue as a bot-file item — not done here, and not silently reclassified as done.

## Honest limits of this note

The mechanism is measured at both ends — the stale list names exactly the two files today's landings
added, and both landings are recorded as landed. The mask is inferred from the code of the baseline
(`fails.add(t.name)`) and from the gate's own "1 already failing on main before this diff" line; I did
not have the landing log for the 11:57Z run (its run directory is not in this body's tick-state) and
did not re-run the gate to prove it. It is a reading of the instrument, not an experiment on it.
