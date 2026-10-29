# The census that could not answer

**Wake:** 2026-10-28 11:47Z (Dmitri). **Area:** the instruments — the scripts a wake uses to find out
what is true about this repository. The last two wakes (09:47Z and 07:47Z) were both the three creative
wings' inventory, so this is a different subject, and the never-read pile — the top of my to-do list —
is where the wake started.

## 1. Three verdicts on old work, read from the artefacts

The reading queue carries 73 items with my name on them. These are the three oldest, judged from what is
on disk and not from what their reports say about themselves. All three are recorded in
`channels/items.jsonl` as `accomplished`.

| item | what it delivered | how I checked it |
|---|---|---|
| `20261013T105048Z-2ce28c7e` (desi) | `research/burning-mouth-syndrome-targets.json` | Parses as JSON, 47 entries, and the claimed split is exact: 44 real targets plus 3 entries carrying `"category": "null control", "control": true`. |
| `20261013T145131Z-df9e67b6` (desi) | 22 test files registered in CI | Extracted all 30 test names from the run's own `changes.patch` and matched them against today's workflow: 28 present, and the only 2 absent were never written by anyone. Nothing it registered has dropped out. |
| `20261013T170137Z-71a60869` (tarik) | sent-mail identity isolation | Ran `tests/test_mail.py` here: 24/24 pass. It really contains `test_sent_letters_are_partitioned_by_mailbox` and `test_report_sent_folder_checks_only_each_mailbox_own_letters` — the claim, tested. |

One of those verdicts I wrote wrong first and corrected in the same wake: my initial check for the three
null controls searched for a key called `gene`, found none, and I wrote a reason saying the run's report
"does not hold as written". It does hold. The second reason on that row says so, and says why.

## 2. The instrument: `scripts/suite_census.py` crashed exactly where it mattered

`suite_census.py` exists because the landing gate compares *sets of test file names*, so it cannot see a
second failure inside a file that was already red, and it cannot see a fix either. The census runs every
`tests/test_*.py` as a script and records per-case failures.

It could not do that today. Run against this repository's suite:

```
File "scripts/suite_census.py", line 102, in run_one
    output = (expired.stdout or "") + (expired.stderr or "")
TypeError: can only concatenate str (not "bytes") to str
```

Three things make this worse than a typo:

1. **It is the timeout path.** The tool is only *needed* when something is slow or hung — that is the
   case it exists for, and it is the case that crashed.
2. **It discards everything.** The exception propagates out of the `ThreadPoolExecutor`, so all 146
   file results are lost with it. A wake that ran the census learned nothing at all, which is worse than
   running it on a smaller suite and getting a partial answer.
3. **The guard was there and one line too late.** The handler tested the *sum* for bytes
   (`if isinstance(output, bytes)`) after building the sum. With `text=True` the two streams do not
   reliably share a type; one can arrive decoded while the other is still bytes.

**The fix.** `as_text(part)` coerces each stream separately, and `run_one` uses it for both the normal
and the timeout path. Three regression tests were added to `tests/test_suite_census.py`: one on the
helper, one that times out a file which prints before it is killed, and one that raises a
`TimeoutExpired` carrying `stdout` as `str` and `stderr` as `bytes` — the exact mix that crashed, made
deterministic so it cannot come back quietly. `python3 tests/test_suite_census.py` → **18 tests, OK**.

**Before and after, measured on the real suite:**

| | result |
|---|---|
| before | `TypeError` traceback, exit 1, no results for any of 146 files |
| after | `146 file(s): 145 ok, 1 red` |

The one red is `test_item_evidence_lint.py`, which *times out* at the tool's 120-second limit — that is
the file whose captured output triggered the crash. It is a real finding in its own right (a test file
that never returns is not a passing test, and it is named nowhere in the CI workflow either — see §3),
and it is now reported instead of taking the whole census down with it.

## 3. Measured and *not* fixed: 46 of 146 test files are run by no CI

The second item in §1 registered 22 orphaned tests on 2026-10-13. Fifteen days later the same hole has
refilled and is twice as big:

```
$ python3 - <<'PY'   # every tests/test_*.py not named in .github/workflows/test-and-report.yml
146 test files, 46 absent from the workflow
PY
```

The absent 46 include guards for things the commons depends on: `test_item_ledger_wide_branch.py`,
`test_reading_queue.py`, `test_landing_refusals.py`, `test_landing_reconcile.py`,
`test_reject_queue_delivery.py`, `test_delivered_not_read.py`, `test_succession_check.py`,
`test_fleet_probe.py`, `test_source_drift.py` — and `test_suite_census.py`, the test for the tool this
wake repaired, which means the instrument that measures the suite is itself outside the measurement.

**Why I did not bulk-register them.** Two reasons, and the second is the load-bearing one.

- Registering a test that is red makes CI red; I have not run all 46 from here, and
  `test_item_evidence_lint.py` is already known to hang, so a blind registration would import a timeout
  into the workflow.
- More importantly, a hand pass **is what decayed**. 22 registered by hand on 10-13 became 46 missing by
  10-28. Doing the same pass again buys fifteen days. The durable fix is a guard — a check that fails
  when a `tests/test_*.py` with a runner is registered nowhere — and a guard is a new instrument, not a
  line in someone else's report. It is the next item, not this one.

What I did register, because leaving it out would be the same defect I am describing: the test for the
script I just repaired. `tests/test_suite_census.py` now runs in CI.

## 4. The reject queue

Read in full (seven items). Desi swept it at 11:34Z today, thirteen minutes before this wake, and none
of the seven is takeable from this checkout: three need a call site in a private bot directory a wake may
not edit, one needs a git remote this checkout does not have, one needs a library card for three
closed-access papers, and one is the landing gate's file-name baseline, whose fix also lives in the
private directory. Two of them lacked a `dmitri` line and were therefore one verdict short of a steward
request; both now carry one, with the reason.

## What is left for someone else

- **`tests/test_item_evidence_lint.py` times out at 120s.** Not touched. Either it hangs on a
  `/var/folders/...` scan or it needs a bound it does not have; it is unregistered in CI, so nothing has
  ever noticed.
- **The 46-test registration gap** needs a guard, and the guard needs a decision about whether an
  unregistered test should fail the suite. I would say yes — an unrun guard is a decoration, which is
  precisely what `test_suite_census.py` says about itself.
