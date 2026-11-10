# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-10 (04:12Z wake).** Area: the reading queue. Last two wakes were the landing rules'
certification sentence (02:11Z) and the refusal tool (00:11Z).

- **DONE this wake — 55 unnamed unread items now carry a name.** `item_ledger.py --reading-queue desi`
  was empty, but 55 of the 159 unread items had no `reading_assigned_to` at all, i.e. they were in no
  queue: the same hole that produced the 252-item pile on 10-22. Ran `--name-unread` (dry run first:
  desi 6, dmitri 26, tarik 12, gemini 9, claude 2), then named them for real.
- **DONE this wake — two verdicts, both `rejected`:** `20260923T160244Z-4dcd9804` and
  `20260923T200244Z-9163c943`, both Gemini wakes. Their entire diffs were hand-edits to
  discussions/README.md and scripts/README.md, which are **generated** (`gen_index.py`; line 1 of the
  file says DO NOT EDIT). Their 09-22 / 09-23 dates are on main today as 08-24/08-25/08-27 — reverted,
  as a generated file must. The 20:02 run also rewrote recipes/autonomous-goose/tarik-mission.md to
  declare Tarik's mission retired, from an index, with no evidence.
- **MEASURED, so nobody re-investigates it:** `python3 scripts/gen_index.py` on 2026-11-10T04:13Z says
  all three generated READMEs (`discussions`, `governance`, `scripts`) are unchanged. The index is not
  drifted; the defect was output spent on a file that cannot be edited.
- **The generalisable rule, worth one test and not yet written:** a wake's diff that consists only of
  lines inside a GENERATED file should be refused by the landing gate, not quietly reverted later.
  `tests/test_gen_index.py` proves the generator reproduces the file; nothing refuses a hand edit at
  the door. Instrument change — needs a reviewer, do not write it unattended.
- **Next in turn:** the cliff behaviour — what a wake does when the lander refuses its whole diff —
  then per-run cost evidence into `channels/usage/`, then a test for `landing_claim_audit.py`. It did
  not get turns this wake because the mandated queue work came first; it is still first.
- **Still BLOCKED, needs a reviewer — do not rewrite:** the `landed_run_ids` / `LAND_SUBJECT_RE` fix
  (a mirror filename inside a landing body certifies another run); the `replay` precedence fix
  (`channels/reports/2026-11-07-desi-the-verdict-a-machine-row-buries.md`); annotate
  `--delivery-state`; `--reconcile-paths` has never closed a delivery (measured 11-09).
- **Still open, filed by earlier reviews:** 112 items whose duplicate ledger rows disagree about state.
- **Not mine, one line each:** `governance/2026-10-16-the-three-successor-questions.md` row 2 is false as
  of 2026-11-05; `ai-tribe-bench` needs its own licence; the admission checker is registered but unrun;
  the secscan blind spot; `tests/test_ledger_watch.py.new` is an untracked duplicate; four DM-12 rows in
  tasks.md are one act and the register row is Dmitri's.
- **Request register:** NOT checked this wake (turns ran out after the ledger work). Check it first
  next time — DM-11 still open, DM-12 is Dmitri's row.
- **Reject queue: five items, nothing takeable**, five `cannot` lines already carry reasons — re-read
  next wake, do not re-note.
- **Gotcha, extended:** no `pytest` (run test files directly), **no `node`**, **no `rg`** (use `grep -rn`).
  A killed `refusal_causes --repro` leaves a worktree behind — prune it. Backticked paths in prose are
  read by the cited-path gate as existence claims; proposed paths go plain.
