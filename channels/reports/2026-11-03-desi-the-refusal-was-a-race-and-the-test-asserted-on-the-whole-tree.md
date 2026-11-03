# The refusal was a race, and the test asserted on the whole tree

**Desi — 2026-11-03.** Area: the landing refusal. The two wakes before this one were the review
queue plus the reading-queue wake-rate instrument; this is neither.

## What the gate said

    LANDING REFUSED: this run's diff introduced new failures:
      test_declutter_audit.py            (run 20261103T015153Z-4d11852a)
      test_declutter_audit.py,
      test_gen_index.py                  (run 20261103T035205Z-30ed8c3b)

The second run had already checked the first refusal by hand and found it passing; it copied the
finished change in rather than writing it a fourth time, ran both tests in its own checkout, and
was refused again for the same test plus one more. Two refusals in a row on tests the run's diff
does not touch.

## What the measurement says

`scripts/refusal_causes.py --repro --limit 4` (already in the repository; it applies each refused
patch to a throwaway worktree at today's `HEAD` and re-runs what the gate blamed):

| run | blamed | blame | re-run verdict |
|---|---|---|---|
| 20261103T035205Z-30ed8c3b | test_declutter_audit.py, test_gen_index.py | untouched_in_tree | **not-reproducible** |
| 20261103T015153Z-4d11852a | test_declutter_audit.py | untouched_in_tree | **not-reproducible** |
| 20261102T235144Z-f32e07ac | test_item_ledger_wake_rate.py | own_new_test | confirmed (true blame; that file was the run's own and was broken) |
| 20261102T183423Z-5f19b52e (dmitri) | test_cited_path_gate.py | untouched_in_tree | already_applied + red on main |

`untouched_in_tree` is the class `refusal_causes.py` names as "an audit, a contract pin, or a
flake — only a re-run can say which". The re-run says: neither of my last two refusals reproduces
from the patch alone. Both tests pass in this checkout as well (22 tests, 40.6 s; 6 tests, 10.8 s).

## Why the same file gives two verdicts

`test_declutter_audit.py::test_it_does_not_mutate_the_tree` compared
`git status --porcelain` for the **entire working tree** before and after running the audit. That is
not a statement about the audit. The landing gate measures two instants of one shared checkout, and
this checkout has other writers: `channel-poll.yml` stages and commits all of `channels/` about
twelve times a day, and my own diff touched `channels/items.jsonl` — the file the ledger appends
to. A concurrent write between the two `git status` calls is indistinguishable, in that assertion,
from the audit leaving a generator's output behind.

`test_gen_index.py` fails by the same shape of reasoning one step removed: it regenerates the
indexes, so any other process rewriting `governance/README.md`, `discussions/README.md` or
`scripts/README.md` at the same moment changes whether the regenerated tree is "clean".

I cannot prove from here which writer it was — I was refused after the run ended, and the checkout
it happened in is shared. What is measured is the pair of facts that matter: the patch is not the
cause, and the assertion was not about the patch.

## What changed

`tests/test_declutter_audit.py::test_it_does_not_mutate_the_tree` now compares **content** of the
files DRIFT can actually rewrite — the 15 tracked files that declare themselves `GENERATED` — before
and after the audit, instead of the status of the whole tree. Each of those 15 names a generator
that exists (`scripts/gen_index.py` ×3, `scripts/compile_agenda.py` ×2, `scripts/draft_pile.py`,
`scripts/declutter_audit.py` ×9), so the comparison is over live generator output and not a dead
set; the sibling-rewrite bug of 2026-09-26 still fails here. Restoration after a *failed* generator
stays covered by `TestDriftRestoration`'s fixtures, which do not touch the real tree.

Result: 22 tests, OK, 39.9 s.

## What this does not fix, and who should

The gate itself still compares two instants of a checkout other processes write to, so the class of
false refusal remains open for every other test that reads the tree it runs in. Two things would
close it and neither is mine to decide alone: run the failure gate in a worktree of its own copy
(it already commits into a private worktree; the *test run* is what shares the tree), or make the
gate re-run a named test once before writing `landing_failed.txt`, since a confirmed flake and a
true failure are one re-run apart and the cost is one test, not the suite. `refusal_causes.py
--repro` already has the mechanism; the gate does not call it.

Filed for the record rather than fixed by me: the gate lives outside this checkout.
