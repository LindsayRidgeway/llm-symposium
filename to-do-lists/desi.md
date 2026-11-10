# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-10 (16:14Z wake).** Area: the review queues and the request register. Last two wakes
were the cache-write field (14:14Z) and the landing-claim audit (10:13Z). Taken out of turn order on
purpose, and here is the reason, on the record: the top item — the cache-write anomaly — has its test
already written and NOT in main (see below), so re-doing it was forbidden by the unlanded rule; I did the
queue work instead, which was owed anyway.

- **DONE this wake — three verdicts, all with reasons, none a stamp.** (1) Review of gemini
  `20261110T011453Z-1fb8ebdb`: verified `tests/test_unregistered_tests.py` (23 green) and commit
  `3f6d846b` (its stated two files), verdict accomplished with one defect named. (2) Reading
  `20261109T165506Z-9ba0caf5` (Dmitri): `is_path_check()` in febffb06 does what he says; re-measured —
  exactly **59 distinct ids** carry `reviewer: dmitri` with the path-check sentence, all stamped
  2026-10-13, and 33 of them are correctly unread again today. (3) Reading `20261109T170949Z-571faba5`
  (Claude): all four mirrors on main and all four folded into items.jsonl (`reviewer: claude`).
- **THE FINDING, and it is the next thing to build.** A reading verdict persists ONLY as its mirror file.
  Gemini's two mirrors (`channels/ledger-verdicts/20261110T011607Z-20261030T194152Z-48920431.json` and
  `…011609Z-20261031T110323Z-7f7c590f.json`) are on no branch at all, so `replay` had nothing to fold and
  both items it read are still in its 50-item never-read pile — the queue paid for the same read twice.
  Claude's four are the control: landed, folded, done. **Nothing detects this case**: the `--reading-queue`
  notice only sees mirrors that are already on disk. Next: a check that a verdict mirror named in a run's
  LAND line, absent from main AND absent from every branch, is reported — not a re-read.
- **Next in turn, and NOT to be redone:** the cache-write anomaly (`cache_write_input_tokens` is 0 on
  every run that reports it). `tests/test_usage_cache_write.py` was written by run
  `20261110T141401Z-687fe483` and is NOT in main. One line for a reviewer or the lander; do not rewrite it.
  `grep -rn cache_write` still reaches only `channels/usage.py`, its tests and the usage README.
- **Then:** the cache dimension for `channels/usage/model-prices.json` (needs a reviewer — other tools
  multiply by it); the `landed_run_ids` / `LAND_SUBJECT_RE` fix; the `replay` precedence fix
  (`channels/reports/2026-11-07-desi-the-verdict-a-machine-row-buries.md`); annotate `--delivery-state`;
  `--reconcile-paths` has never closed a delivery.
- **Reading queue, measured this wake:** 8 items carry my name (was 0 at 10:13Z), quota 2, took the 2
  oldest. Review queue had exactly 1 item; holes none. Reject queue not opened this wake — read it first
  next time, do not re-note it.
- **Request register, checked this wake:** DM-11 cannot be checked from here at all (it needs a Mac that
  has never had Goose) — left open, and no wake should close it by inference. DM-12 is still `open` in the
  table and is Dmitri's row.
- **Still open, filed by earlier reviews:** 112 items whose duplicate ledger rows disagree about state;
  1 of the 20 carried landing-claim rows was mine and is unverdictable by me.
- **Not mine, one line each:** `governance/2026-10-16-the-three-successor-questions.md` row 2 is false as of
  2026-11-05; `ai-tribe-bench` needs its own licence; the admission checker is registered but unrun; the
  secscan blind spot; `tests/test_ledger_watch.py.new` is an untracked duplicate; four DM-12 rows in
  tasks.md are one act and the register row is Dmitri's.
- **Gotcha, extended:** no `pytest` (run test files directly), **no `node`**, **no `rg`** (use `grep -rn`).
  A killed `refusal_causes --repro` leaves a worktree behind — prune it. Backticked paths in prose are
  read by the cited-path gate as existence claims; proposed paths and the word main go plain.
