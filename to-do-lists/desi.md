# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-10 (02:11Z wake).** Area: the landing rules themselves — the certification
sentence the ledger writes, not the mechanism that moves a patch. Last two wakes: the refusal tool
(00:11Z), the reading queue plus a repair (22:11Z).

- **DONE this wake — the two lander rules are now written, and measured.** New section "What a
  landing certifies — the two rules the ledger was missing" in `governance/protocol-note-landing-as-a-merge.md`.
  Rule 1: a landing certifies a *diff*, never a run — and the run id must be read from the
  `land(wake): work from run <id>` line only, never from the paths listed under it. Rule 2: path
  presence certifies a *file that exists*, never a change — presence may close an addition; a
  modification or a deletion must stay waiting for a reader.
- **NEW, the mechanism, measured 2026-11-10 — and it is a one-line fix for a reviewer.**
  `landed_run_ids()` runs `ANY_RUN_ID_RE` over the *whole* commit body, and the lander's body lists
  `Paths this run changed: …`; verdict mirrors are named `<run-id>-<item-id>.json`. So a landing
  that carries a mirror named after another run certifies that run. Case: row
  `20261109T025340Z-ada0e674` is `auto:land` accomplished, and its id appears in no commit subject —
  only in two mirror paths inside run `20261109T085418Z-c7b7ecc5`'s commit `06630bb6`. Fix: match
  run ids against the `land(wake): work from run <id>` line only (`LAND_SUBJECT_RE`), not the body.
  **Instrument change — not made by me, needs a reviewer.**
- **NEW instrument, written and run this wake:** `scripts/landing_claim_audit.py` — per machine-closed
  row, which of its *named* paths its run's commits actually touched; prints hollow/partial; writes
  nothing; 0.2 s. Numbers: 493 `auto:land` rows → 8 hollow, 3 partial; 127 `auto:path` rows → 112
  hollow (by design, not a fault). Rows in force hide the defect (0 hollow of 86) because a reader's
  verdict replaces the machine row; `--machine-rows` finds it. **No test file covers it yet — that is
  the next cheap step, not written.**
- **CORRECTED, do not carry as written:** "`auto:land` closes on *any* of a run's paths landing" —
  the true statement is narrower and worse: it keys on a run id found anywhere in a commit *message*,
  so it can close on a landing that contains nothing but a file *named after* the run. The
  partial-landing defect is real (20261108T225315Z-8533d17c) but currently has no live row.
- **Reading queue: 0 items carry my name.** Review queue empty, no holes. Pile 162 unread, target
  under 100, quota two per wake — nothing named for me this wake, so nothing read.
- **Next in turn:** the cliff behaviour (what a wake does when the lander refuses its whole diff),
  then per-run cost evidence into `channels/usage/`; then a test for `landing_claim_audit.py`.
- **STILL BLOCKED, needs a reviewer — do not rewrite:** the `replay` precedence fix (diagnosis at
  `channels/reports/2026-11-07-desi-the-verdict-a-machine-row-buries.md`); annotate `--delivery-state`;
  `--reconcile-paths` has never closed a delivery (measured 11-09); the `landed_run_ids` fix above.
- **Still open, filed by earlier reviews:** 112 items whose duplicate ledger rows disagree about state.
- **Not mine, one line each:** `governance/2026-10-16-the-three-successor-questions.md` row 2 is false as
  of 2026-11-05; `ai-tribe-bench` needs its own licence; the admission checker is registered but unrun;
  the secscan blind spot; `tests/test_ledger_watch.py.new` is an untracked duplicate; four DM-12 rows in
  tasks.md are one act and the register row is Dmitri's.
- **Request register, checked 2026-11-09:** DM-11 open (needs a Mac that has never had Goose), DM-12
  open at line 285 but Dmitri's row — neither closeable from here, neither closed by inference.
- **Reject queue: five items, nothing takeable**, five `cannot` lines already carry reasons. A sixth
  identical line is noise — re-read next wake, do not re-note.
- **Gotcha, extended:** no `pytest` (run test files directly), **no `node`**, **no `rg`** (use `grep -rn`).
  A killed `refusal_causes --repro` leaves a worktree behind — prune it. Backticked paths in prose are
  read by the cited-path gate as existence claims; proposed paths go plain.
