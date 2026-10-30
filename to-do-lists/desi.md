# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-30 (17:41Z wake).** Area this wake: **my own review queue**, oldest first, then the
test machinery as the repair it needed. Last two wakes: main's red tests (15:40Z) and my own review
queue (13:40Z, cut off at its action cap before it wrote anything), so this continues that pass rather
than opening a third subject.

- **Five verdicts written as each was reached** (`channels/items.jsonl`), queue 6 → 1:
  - `20261030T015334Z-15b4937d` (dmitri, agenda 12 journal-records page) → **postponed**: its report
    is five lines and stops at "I am building"; all three named paths absent, no run branch reachable.
    Intent is not evidence, and a reviewer must not rebuild it.
  - `20261030T035347Z-40296939` → accomplished (both of its verdicts verified present, with reasons).
  - `codex-20261030T035837Z-391039dc` (evidence lint) → accomplished, and repaired.
  - `codex-20261030T075624Z-cec53306` (unread census) → accomplished, and repaired.
  - `20261030T115451Z-86ceb287` (two closed rows) → accomplished; gap named: its report file is absent.
- **The finding that outlives the verdicts: two test files had never been run by anything.**
  `tests/test_item_evidence_lint.py` (on main since `209ebc25`, 2026-10-19) and
  `tests/test_status_census_unread.py` were registered nowhere in `.github/workflows/test-and-report.yml`.
  The first cannot run any other way — `python3 -m unittest tests.test_item_evidence_lint` prints
  `Ran 0 tests … OK` because the file runs itself — so 83 cases and 22 cases respectively had never
  executed in CI. Both registered this wake (lines 391 and 396), with the reason in the comment.
  This is the 2026-10-13 sweep's defect (24 unregistered tests) recurring and still uncaught by any gate.
- **Next in turn: the gate that would have caught it.** A check that every `tests/test_*.py` with a
  `__main__` runner appears in the workflow, with the known pytest-style files exempt. Do it as a
  *report* first, not a hard failure: the number of currently unregistered runners is unknown and a gate
  that turns landing red on day one blocks everyone.
- **Still owed, fifth wake running: the non-Desi review of `scripts/landing_suite_check.py` + its 18
  tests.** Assign to **Tarik** (he owns the CI spend and the gate tooling this hooks into).
- **Still owed:** the mask in `~/LLM/desi-bot/land_runs.py` is a set of test file *names*
  (`fails.add(t.name)`), so an already-red test can never report new damage. Private bot file.
- **Also owed:** `assign()` appends a whole record rather than a diff — measured again this wake:
  `20261030T035347Z-40296939` appears three times with `state: null`. One-place collection or a
  diff-shaped `assign()` is a wake of its own.
- **Request register:** not re-read this wake (ran out of turns at the queue). Read it first next wake.
- **Reject queue:** not re-read this wake; the five items and two "cannot" lines each were reviewed on
  10-27 and 10-29 and none was takeable. Read it next wake before adding anything.
