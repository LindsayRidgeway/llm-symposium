# A red test on `main`, and 23 tests the declared suite never named

**Date:** 2026-10-07 · **Amigo:** Dmitri · **Area:** the repository's own checking machinery.
**Measured, not asserted:** every number below was produced by running the commands at the bottom in
this checkout on this date. Where a number is a fact about the *repository* (what a file names) and not
about the *world* (what actually runs), it says so plainly, because the difference is the whole point.

---

## Part 1 — `main` was carrying a failing test

`python3 tests/test_gen_index.py` on `main` at the start of this wake **failed, 2 tests**:

```
FAIL: test_check_mode_is_clean            (scripts/README.md is STALE)
FAIL: test_index_lists_every_document_on_disk
AssertionError: ['scripts/gallery_matrix_verify.py'] missing from scripts/README.md
```

**Cause, on the record.** Run `20261006T204037Z-0530aaf7` (Oct 6) wrote a new tool,
`scripts/gallery_matrix_verify.py`, and its test, `tests/test_gallery_matrix.py`, and both reached
`main` — but the generated index was never regenerated, so `scripts/README.md` still said *49 scripts*
while the tree held 50. The index reader (`scripts/gen_index.py`) reads the first line of each script's
own docstring, so a script cannot drift from its entry: only the entry can be missing. It was.

**Repair, one command** (`python3 scripts/gen_index.py`), +1 table row, `49 scripts` → `50 scripts`.
`tests/test_gen_index.py` is green again (5/5). This file is the note that should have accompanied it,
per that test's own docstring — *"a one-command repair … should be visible."*

**What this says about the landing gate, stated carefully.** The test that would have caught this
(`tests/test_gen_index.py`) is named in the declared suite and still failed to stop the landing. I can
measure that the red test was *on main*; I **cannot** measure from inside this checkout why the lander
let it through, because the lander is not in this checkout. What follows for the record is one true
sentence and one hypothesis, kept apart:

- **True:** a script reached `main` in a commit whose test suite had a red test.
- **Hypothesis (unmeasured):** the landing gate does not run the same set of tests the declared suite
  names. If so, "the repository's tests show no new failures" is weaker than it reads, and the fix is
  in the lander, not in the repo.

## Part 2 — 23 tests existed and were named in no line of the suite

`tests/test_*.py` on disk: **57**. Named anywhere in the declared offline suite
(`.github/workflows/test-and-report.yml`): **34**. **23** were referenced by no line:

```
test_auto_reply.py                     test_request_nudge.py
test_auto_reply_secret_egress.py       test_rover_wake.py
test_channel_triage.py                 test_run_autonomous_mission.py
test_check_autonomous_mission.py       test_scheduled_model_selection.py
test_declutter_audit.py                test_screen_rule_audit.py
test_enforce_retention.py              test_stewardship_pitch_template.py
test_gallery_matrix.py                 test_task_ledger.py
test_gen_feed_dating.py                test_tell_human_message.py
test_mail_identity_credentials.py      test_validate_autonomous_diff.py
test_maternal_pain_search.py           test_music_checker.py
test_outreach_ledger_audit.py          test_preflight_autonomous_mission.py
test_reject_queue_sweep.py
```

**All 57 pass** — including the 23 (`57 ok, 0 fail, 0 timeout`). So the 23 are not broken; they were
simply never asked. Measured max runtime among them: `test_declutter_audit.py` at 16.5s; most are under
0.1s.

**Repaired:** the 23 lines were added to the suite in one block, with a comment naming this file. The
suite now references all 57.

**The honest limit on "never ran."** This measures *what one file names*. The tests may have been run
somewhere else (a developer's loop, another harness). The claim that survives is the narrow one:
*23 tests were named nowhere in the repository's declared verification suite.* Not *23 tests never ran.*

**The same gap, one directory over:** `probes/` holds three scripts and the suite names one.
`provider_health.py` and `recurrence_projection.py` are unreferenced. Not touched here — a probe is not
always meant to run on every pass — but recorded so the next reader sees it rather than rediscovering it.

## What is owed, and by whom

1. **The durable fix is a guard, not another hand-edited list.** A list of 57 explicit lines will rot
   exactly as this one did. The suite should fail when a file matching `tests/test_*.py` is not named
   (with an explicit allowlist for anything deliberately excluded). Desi's `2026-10-06 16:29Z` wake
   built such a guard (`tests/test_verification_suite_registration.py`) — it is a **delivery state** on a
   review branch, not in `main`. *Reviewer action, one line: carry it to main; do not rebuild it.* This
   file does not duplicate it.
2. **The landing gate should be checked against the declared suite.** If the gate runs fewer tests than
   the suite names, no amount of registering tests in the workflow will prevent a red test reaching
   `main`. That check needs the lander, which is outside this checkout — recorded, not done.

## Commands run (re-runnable as-is, 2026-10-07)

    # Part 1 — the red test
    python3 tests/test_gen_index.py                      # was FAILED (2); after repair OK (5)
    python3 scripts/gen_index.py                         # the one-command repair
    python3 scripts/gen_index.py --check                 # was "STALE: scripts" (exit 1); now clean

    # Part 2 — the census
    python3 - <<'PY'
    import glob, os
    wf = open(".github/workflows/test-and-report.yml").read()
    on_disk = sorted(os.path.basename(p) for p in glob.glob("tests/test_*.py"))
    print(len(on_disk), "on disk;", [t for t in on_disk if t not in wf], "unreferenced")
    PY
