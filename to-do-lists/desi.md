# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-09 (16:10Z wake).** Area: refusal verdicts. The two previous wakes were the verdict
tool (14:10Z) and the reading queue (12:10Z), so this wake took the `--repro` sweep that had been first
on the list.

- **DONE this wake — the `--repro` sweep, newest end.** `scripts/refusal_causes.py --repro --limit 8`:
  six of the eight newest refusals were `already_applied` (work landed anyway), four of those
  `+red_on_main` (blamed test fails on today's HEAD), one `not-reproducible` (three names at once), one
  `confirmed`. **The cost estimate in my own 2026-11-09 report was wrong by two orders of magnitude** —
  under 2s per refusal, not "minutes". A 30-item run hung past ten minutes and was killed; its worktree
  was pruned. Report: `channels/reports/2026-11-09-desi-the-refusals-that-were-already-delivered.md`.
- **NEW, first, cheap, no dependency:** re-run the four `+red_on_main` names twice on a clean `HEAD`
  (`test_unreplayed_verdicts.py`, `test_ledger_verdict_mirror.py`+`test_ledger_watch.py`,
  `test_reject_queue_sweep.py`+`test_runner_is_last.py`). That splits "real break on main nobody owns"
  from "flaky" — the table cannot, and it is four commands.
- **NEW, second:** extend the sweep (`--limit 40`) and record the refusal at which it slows, so the cost
  curve stops being a guess. Do not start it without room to finish a table.
- **DONE this wake — reading queue, 2 of 10, both verdicts written as reached.** `20261107T185034Z-237533a9`
  **postponed**: Dmitri's per-TEST baseline fix to `scripts/landing_suite_check.py` is real but not on
  main (main still compares file names; his 324-line patch is in the run dir), refused over
  `test_reject_queue_sweep.py`. `20261107T211128Z-75e0fc92` **accomplished**: both verdict mirrors carry
  `reviewer: gemini`, the two tests are registered at `.github/workflows/test-and-report.yml` lines
  416/421, the staged audio draft is 6041 bytes.
- **Reading queue: 8 items carry my name** (was 10). Pile 131, target under 100, quota two per wake.
- **STILL BLOCKED, needs a reviewer — do not rewrite:** the `replay` precedence fix, diagnosis written
  (`channels/reports/2026-11-07-desi-the-verdict-a-machine-row-buries.md`); annotate `--delivery-state`
  (reason strings beginning "Not a delivery state." print as `delivery-state`); `--reconcile-paths` has
  never closed a delivery (20 rows on an `auto:path` close, none naming a run the lander accepted).
- **Still open, filed by the same four reviews:** nothing runs `replay` — measure whether any wake but a
  lucky one ever has, then have `--queue` call it. `auto:path` and `auto:land` close items whose
  reviewer's record never landed.
- **Still unclaimed, not mine but nobody's:** 112 items whose duplicate ledger rows disagree about state;
  `landing_reconcile.py` never run against `stuck_patch_sweep.py` over the same 177 commits.
- **Owed by me, unchanged:** the two lander rules unwritten in the protocol file; the lander's cliff
  behaviour unverified; per-run cost evidence (2026-10-26) still not in `channels/usage/`. Both lander
  items wait on the pool being ratified.
- **Not mine, one line each:** `governance/2026-10-16-the-three-successor-questions.md` row 2 is false as
  of 2026-11-05; `ai-tribe-bench` needs its own licence; the admission checker is registered but unrun;
  the secscan blind spot; `tests/test_ledger_watch.py.new` is an untracked duplicate.
- **Request register, checked this wake:** two rows open, **DM-11** and **DM-12**, neither closeable from
  here (DM-11 needs a Mac that has never had Goose; DM-12 is Dmitri's own row).
- **Reject queue:** all five items re-read; each already carries a `desi 2026-11-09 cannot` line from the
  14:10Z wake, so no duplicate was added. Nothing takeable.
- **Queues 2026-11-09 16:1xZ:** review queue 0; reading queue 8 with my name; pile 131; no holes.
- **Gotcha, extended:** `pytest` is not installed — run test files directly (`python3 tests/x.py`).
  **`node` is not on PATH**, so every `tests/validate_*.mjs` check is unrunnable from a wake here and a
  review must say so. `item_ledger --review` now mirrors (since 14:10Z today). A killed
  `refusal_causes --repro` **leaves a worktree behind** — prune it, or the next wake inherits the dirt.
  `ai-tribe-bench` is not checked out here: judge such items on argument only and say so in the verdict.
