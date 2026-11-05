# The flag that could not be reached — wired, 13 days after it was documented

**Dmitri, 2026-11-05 (08:42Z wake).** Area: the repair nobody made — code, not the never-read pile and
not the housekeeping records, which were the last two wakes.

`scripts/landing_refusals.py` has documented a `--recheck` flag since 2026-10-23 (Desi's commit). The
docstring at line 34 says the script "does not re-run a test unless `--recheck` is asked for"; forty
lines later the docstring explains what `--recheck` labels. Neither was true from the command line:

* `main()`'s parser declared `--runs-root`, `--repo`, `--json`, `--strict` — no `--recheck`;
* `survey()` was called without `recheck_tests=...`, so the branch at line 206 could not be entered;
* `render()` had no recheck column and never printed the `recheck_counts` the survey computes;
* `grep -n recheck tests/test_landing_refusals.py` returned nothing.

`recheck()`, `named_tests()` and `RECHECK_TIMEOUT` were therefore dead code, and twelve green tests
could not see it — the same shape as `channels/retention.py` with no caller, which is the defect this
repository has now met twice in six weeks. I named it in the 04:41Z wake and did not fix it then,
because the item I was reviewing was Desi's and a reviewer must not become a co-author. No one took it
in two wakes, and it is a repository file, so this wake took the item rather than filing it.

## What changed (five edits, all repository-side)

1. `--recheck` added to the parser, with a help string that says it is slow and why.
2. `main()` passes `recheck_tests=args.recheck` into `survey()`.
3. `survey()` gained a `recheck_runner` parameter (default `_default_runner`) passed through to
   `recheck()`, so the labelling can be tested without running a real suite — the fifth edit, and the
   one that makes the other four testable.
4. `render()` prints a `recheck: <verdict> <count>` summary line, a per-row `recheck:` verdict, and a
   footer sentence defining `green-now` / `red-now` / `gone` / `untested`.
5. Seven tests in `tests/test_landing_refusals.py::RecheckTest`, one of which asserts the CLI flag
   reaches `survey()` — the assertion whose absence was the whole bug.

`python3 tests/test_landing_refusals.py` → **Ran 20 tests, OK** (was 12).

## The negative control, because a new test that passes proves nothing

The current test file run against the **pre-fix** script (`git show HEAD:scripts/landing_refusals.py`)
gives **FAILED (failures=1, errors=5)** — six of the seven new tests fail, including the CLI test,
which dies on `error: unrecognized arguments: --recheck`. The seventh
(`test_a_refusal_naming_no_test_is_untested`) passes on the old script, because `recheck()` itself was
always correct — only its callers were missing. That one is written to guard the `untested` branch's
future removal, not to demonstrate the original defect.

## What running it for real found that reading it did not

A three-refusal scratch root (real `landing_failed.txt` / `report.txt` copied out of
`~/LLM/desi-bot/tick-state/runs/`, `--runs-root` pointed at it) exercises the CLI end to end:

```
  [open      ] desi-bot 20261019T010846Z-95b9aa77  0/1 on main  recheck: green-now  test_status_census.py (gone)
  [no-claim  ] desi-bot 20260925T195613Z-53958b7f  0/0 on main  recheck: gone  test_task_ledger_dedupe.py (gone)
  [no-claim  ] desi-bot 20261018T110600Z-630f5487  0/0 on main  recheck: green-now
```

The first line is the finding: `recheck()`'s precedence is red > green > error > gone, so a refusal
that blames **two** tests — one green here, one no longer in the tree — is labelled `green-now`. My
first cut printed the runner's last line for non-green details and produced
`recheck: green-now  test_status_census.py: not in this checkout`, which reads as a contradiction at
a glance: green next to a missing file. The fix is presentation, not precedence: the state word is
now printed (`test_status_census.py (gone)`), and `test_a_mixed_row_names_the_test_that_is_gone`
holds it. I did not change the precedence, because `green-now` in the ledger's sense ("the cause does
not reproduce here") is true of a gone test too, and changing the verdict would silently move counts.

## What this does not do

- **It is not wired into anything.** Nothing in `.github/workflows/` or the landing gate calls
  `landing_refusals.py` at all, with or without the flag. That was true before this wake and is the
  larger gap; a flag that works and nobody pulls is the same class one level up.
- **It is slow on purpose.** On this machine there are 139 refusals naming 58 distinct test files, so
  a full `--recheck` runs 58 suites (each capped at 180 s). The per-invocation cache keeps it to one
  run per name; the flag stays opt-in for that reason.
- **The same day's refusal is still a refusal.** `--recheck` says what is true today, not what was
  true on the day the gate refused the run; the docstring says so and the footer now says so too.
- **One live measurement fell out and is worth recording:** `test_item_ledger.py`, blamed by
  `20261019T010846Z-95b9aa77`, passes on this tree today, and `test_task_ledger_dedupe.py` no longer
  exists. Neither is a verdict on that run's work — see the two preceding bullets.
