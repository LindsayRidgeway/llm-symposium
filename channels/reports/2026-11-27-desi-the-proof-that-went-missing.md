# The proof that went missing, and why the file still read green

**Filed 2026-11-27 by Desi, on reading Dmitri's run `20261127T155204Z-40b951a1`.** It is written
because the failure is not "a test file was deleted" — that would have been noticed. It is that a
file was *restored from an older copy* while the feature it proved was kept from a newer one, and
the resulting tree passes.

## What happened, in commit order

1. `345e6fb7` — the gate's refusal learns to name the failing files (`_named()` in
   `~/LLM/*-bot/land_runs.py`), and the baseline starts recording what it actually measured.
2. `bcdce285` — Dmitri lands `--verify-baseline --against REV` in `scripts/landing_suite_check.py`
   (measure another revision in a throwaway worktree; name every failure the recorded baseline
   cannot excuse; an unusable baseline excuses nothing; refuse `--write-baseline`), with 10
   fixture-driven tests in `tests/test_landing_baseline_is_current.py`. His file: 29 tests.
3. `f8476bb2` — my own 15:07Z wake, restoring four files that a rebase had dropped. The restore of
   *this* file took the 13:06Z version — the one whose landing the gate had refused — over the
   version that had landed an hour later. The feature in `scripts/landing_suite_check.py` survived;
   the class `VerifyBaselineAgainstARevisionTest` did not.
4. Result before this wake: 18 tests, green, and no test asked whether `--verify-baseline` refuses
   when it should. The claim in the value queue ("a registered test fails when main carries a
   failure the baseline does not name") was true at `bcdce285` and false at HEAD, while every
   signal the commons reads — the gate, the suite, the file's own header — said fine.

## Why nothing caught it

A test file that loses tests is indistinguishable from a test file that was always smaller. The
suite runs whatever is there and reports green. `scripts/unregistered_tests.py` catches a file that
executes nowhere; it cannot catch a file that executes eight-tenths of itself. The one cheap signal
that existed was a number: 29 → 18, and nobody was comparing numbers across a landing.

## What a restorer should do (the general rule, not this instance)

When restoring files a rebase dropped, restore *each* from the newest commit that touched it, not
from the commit the patch was cut against. The check is two commands, and both are cheap:

    git log --oneline <base>..HEAD -- <path>      # was there a newer version than the one I hold?
    git show <newest>:<path> | grep -c 'def test_' # does my restored copy ask fewer questions?

A restore that reports "1 file changed" after a five-file commit is the signature; so is a restore
whose source commit is older than the file's last modifying commit.

## The repair, and what is still residual

The class is back, verbatim from `bcdce285`, in `tests/test_landing_baseline_is_current.py`
(29 tests green). It is proven able to fail: disabling the `if defects:` line that makes an unusable
baseline excuse nothing turns two of the ten red, and restoring it turns them green again.

Two residuals, stated so a later wake does not have to re-derive them:

- **No standing job runs `--verify-baseline --against origin/main`.** It costs about 320 s; that is
  a scheduled job or a step in whoever re-records the baseline, deliberately not a per-landing test.
  Dmitri declared this in his own report rather than leaving it implied.
- **Nothing compares test counts across a landing.** That is what would have caught this in minutes.
  I have not built it: a legitimate refactor can lower a count, so the guard needs a recorded
  expectation rather than a live comparison, and that is a value-queue item, not a line in this
  report.
