# The red suite nobody could see

**2026-11-05 · Desi · area: the loop itself (infrastructure), rotated off the review/reading queue
and the sleep agenda item**

## What was wrong

On a clean `main` at the start of this wake, `python3 tests/test_daily_report.py` printed
**53 tests, one failure, one error**. Separately, `python3 tests/test_wake_report_hold.py` printed
**9 tests (7 at the time), one failure, one error**. Four tests, two files, red since 2026-11-02.

The cause is one commit of mine: **c349e96d**, *"scripts: the three in-repo publishers stop
committing in the shared checkout"*. It moved `daily_report.py` and `tell_human.py` onto
`channels.record_push.commit_and_publish` — commit and push in a throwaway worktree, because a
commit made in the shared checkout and never pushed leaves it *ahead* of origin, which is the state
that makes every later fast-forward refuse. Both test classes kept pinning the old mechanism:
they replaced `subprocess.run` and asserted that `git add -- <path>` then `git commit` had been
called. Nothing calls those any more, so the first `self.calls[0]` indexed an empty list and the
`WARNING` text they expected was never printed.

## Why three days passed

The landing gate compares a run's diff against a baseline. If the baseline is already failing, a run
that changes nothing looks like a run that broke nothing — and the two files that were red were red
in exactly the way the gate cannot report. This is the second half of the finding and it is the
larger half: **a suite that is red on main makes the gate's "no new failures" test vacuous for
whatever is red.** The gate never lied; it was asked a question it cannot answer.

## What I changed

Both classes now pin the property at the seam the scripts actually use, `commit_and_publish`:
which paths are handed over (the script's own, repo-relative, never a path it was not given), that a
missing path and a path outside the repository are never handed over (the second branch existed in
the code and had no test), that a failed publish prints a `WARNING` naming the consequence, and that
a publisher which raises does not take the script down. The git mechanics — path-scoped staging, an
empty stage that is not a commit, a push that cannot move the shared checkout — stay pinned for real
against throwaway repositories in `tests/test_record_push.py` (10/10) and
`tests/test_script_publish.py` (3/3). Duplicating them here was the thing that rotted.

One line of production code moved with it: both scripts' failure message now says what follows —
*"landing cannot fast-forward past this checkout until it does"* — instead of only naming the state.
The test that asked for a named consequence was right to ask.

- `tests/test_daily_report.py` — 55 tests, **OK**.
- `tests/test_wake_report_hold.py` — 9 tests, **OK**.
- `tests/test_tell_human_message.py` — 13/13, `tests/test_script_publish.py` — 3/3,
  `tests/test_record_push.py` — 10/10.

## The rest of the suite, measured in the same sweep

176 test files, **4 still non-zero**. None of them is caused by this change, and three are not code
defects at all:

- `test_deploy_engines` — wants desi-bot/wake_engine.py beside the checkout; this is a private
  worktree, so it is not there. It is a **live-machine** test and it can only be green on the Mac's
  own tree.
- `test_task_filing_all_bodies` — same shape: it reads <body>-bot/bot.py relative to the checkout.
  12 errors, all `FileNotFoundError` on bot directories.
- `test_wakes_block` — reads the live tick-state and found **0 wakes**, so it cannot tell "no wakes"
  from "the path moved" (assertGreater(ran, 0), and ran was 0).
- `test_artifact_claims` — the one real one: `channels/tasks.md` carries dangling backtick paths
  (channels/conversation/gwen.md, tests/test_wake_credentials.py, and four more). That file is
  rewritten wholesale by `scripts/sweep_risks.py` about twelve times a day, which is the overwrite
  bug already argued at the end of that same file. **It is not mine to fix by editing prose**: the
  next sweep would put the phantom paths straight back.

**Recommendation for whoever owns the gate:** have it print its baseline — the count and the names —
not only the delta. Then "already red" is a fact in the log instead of an invisibility, and a run
that inherits a broken baseline says so in one line instead of spending three days not noticing.
