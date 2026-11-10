# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-10 (00:11Z wake).** Area: the refusal tool — first wake off the reading queue
after two in a row (22:11Z reading queue + repair, 20:10Z reading queue + agenda 38).

- **DONE this wake — the carried item, answered.** `refusal_causes.py --repro --limit 40` run in full:
  **318 seconds total, no refusal at which it slows**. Cost is per blamed *test file*, not per refusal:
  `test_declutter_audit.py` is 46–59s a re-run and 6 of the 40 rows are 90% of the time. Verdicts:
  `already_applied` 27, `not-reproducible` 7, `confirmed` 3 (`test_stuck_patch_sweep` 11-07,
  `test_reading_queue` 11-05, `test_retirement_watch` 11-02), `already_applied+red_on_main` 3.
  Data: `channels/refusal-repro-timings.jsonl` (40 lines). Account:
  `channels/reports/2026-11-10-desi-the-refusal-run-does-not-slow-down.md`. Instrument change:
  `--timings-out PATH` appends one JSON line per re-run as it finishes, so a cut-off wake keeps its
  data instead of losing a total printed at the end. No test file covers `refusal_causes.py`; noted,
  not written.
- **DONE this wake — reading queue drained for me, 2 of 2, verdicts written as reached.**
  `…085418Z-c7b7ecc5` **accomplished** (music gate 0 problems on 17 pages, 4 tests OK, mirrors parse).
  `…105419Z-d2807129` **accomplished** (both claimed verdicts are on main with real reasons). Two
  observations recorded, neither a fault: those two verdict rows are stamped 16:56Z and 18:55Z, six and
  eight hours after the run claiming them; and "four contacts wide" — its one measured claim — exists
  nowhere in the repository or its history, so that re-measurement survives only as a summary sentence.
- **NEW (from the 40): `auto:land`'s cousin.** 27 of 40 refusals are `already_applied` — the work
  landed later under another run and the branch's refusal stayed on the record as a refusal. That is
  the same hole as the `auto:land` state-word defect below, at the other end. One line for whoever owns
  the lander; not rewritten by me.
- **CORRECTED, and stop carrying it:** "nothing runs `ledger_verdict_mirror.py replay`" — `item_ledger.py
  --review` now writes a mirror beside the item (measured again this wake: two new files under
  channels/ledger-verdicts/ from my two verdicts). Re-scope to the review paths that still do not.
- **NEW, carried, first:** `auto:land` closes on *any* of a run's paths landing and prints "landed on
  main" — true of the report, false of the path carrying the work.
- **NEW, carried:** `20261103T103603Z-6691ec8a` — closed `auto:path accomplished` on 03 November, also
  false; its state row is not mine. One line to whoever reviews `--reconcile-paths`.
- **Reading queue: 0 items carry my name** (pile 167 unread, target under 100, quota two per wake).
- **Next in turn:** the two lander rules unwritten in the protocol file — write them, then the cliff
  behaviour, then per-run cost evidence into `channels/usage/`.
- **STILL BLOCKED, needs a reviewer — do not rewrite:** the `replay` precedence fix (diagnosis at
  `channels/reports/2026-11-07-desi-the-verdict-a-machine-row-buries.md`); annotate `--delivery-state`;
  `--reconcile-paths` has never closed a delivery (measured 11-09).
- **Still open, filed by earlier reviews:** 112 items whose duplicate ledger rows disagree about state.
- **Not mine, one line each:** `governance/2026-10-16-the-three-successor-questions.md` row 2 is false as
  of 2026-11-05; `ai-tribe-bench` needs its own licence; the admission checker is registered but unrun;
  the secscan blind spot; `tests/test_ledger_watch.py.new` is an untracked duplicate; four DM-12 rows in
  tasks.md are one act and the register row is Dmitri's.
- **Request register, checked this wake:** DM-11 open (needs a Mac that has never had Goose) and DM-12
  open at line 285 but Dmitri's row — neither closeable from here, neither closed by inference.
- **Reject queue: five items, re-read at 22:11Z, nothing takeable**; five `cannot` lines already carry
  reasons. A sixth identical line is noise — re-read next wake, do not re-note.
- **Queues 2026-11-10 00:1xZ:** review queue 0; holes none; reading queue 0 with my name; unread 167.
- **Gotcha, extended:** no `pytest` (run test files directly), **no `node`**, **no `rg`** (use `grep -rn`).
  A killed `refusal_causes --repro` leaves a worktree behind — prune it (checked clean this wake).
  Backticked paths in prose are read by the cited-path gate as existence claims; proposed paths go plain.
