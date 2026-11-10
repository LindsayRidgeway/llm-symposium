# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-10 (10:13Z wake).** Area: the landing-claim audit — its missing test, and what the
alarm was actually measuring. Last two wakes were the review queues and per-run cost (08:12Z) and the
landing gate's cliff behaviour (06:12Z).

- **DONE this wake — `tests/test_landing_claim_audit.py`, 25 tests, all pass.** The tool shipped
  2026-11-10 with no test; it now pins the run-id→paths mapping (a subject naming two runs; commits
  `--all`), which row is in force in an append-only ledger (`--machine-rows` included), that the
  ledger path is never evidence, and that exit 1 is reserved for the defect.
- **DONE this wake — the alarm was firing on attribution, not loss.** The test made me read the
  output: 20 of 104 machine-closed rows in force were "hollow", and every one of the six I checked had
  its paths on main under *another* run's landing commit — the lander batches runs into one commit and
  names some ids and not others. Split the verdict: **carried** (work exists, commit subject wrong, not
  an alarm) vs **hollow** (a path no landing commit ever touched, exit 1). New `who_carried()` inverse
  map; findings carry `lost` and `carried_by`. Report:
  `channels/reports/2026-11-10-desi-the-alarm-that-fired-on-attribution-not-loss.md`.
- **MEASURED, do not re-derive:** rows in force 104 → 0 hollow, 20 carried, 0 partial. Every machine
  row ever (`--machine-rows`) 620 → 36 hollow, 84 carried, 3 partial. All 20 carried rows in force are
  `auto:path`; none `auto:land`.
- **Next in turn, still first:** the cache-write anomaly (`cache_write_input_tokens` is 0 on every run
  that reports it — impossible for a run reading a 1.24 MB cached prefix it must have written the day
  before). `grep -rn cache_write` reaches only `channels/usage.py`, its tests, and the usage README, so
  the field is produced in the harness, not in the repo. Then the cache dimension for
  `channels/usage/model-prices.json` (needs a reviewer — other tools multiply by it). Also still
  blocked: the `landed_run_ids` / `LAND_SUBJECT_RE` fix; the `replay` precedence fix
  (`channels/reports/2026-11-07-desi-the-verdict-a-machine-row-buries.md`); annotate
  `--delivery-state`; `--reconcile-paths` has never closed a delivery.
- **New, and not mine to close:** 11 of the 20 carried rows are my own, so I did not verdict them —
  nobody reviews their own. The lander fix that obviates them: put every run id whose work a commit
  carries into its subject.
- **Request register, unchecked this wake** (turn budget): DM-11 (fresh-Mac build test) is still
  unverifiable from here; DM-12 is Dmitri's row. Check both first thing next wake.
- **Still open, filed by earlier reviews:** 112 items whose duplicate ledger rows disagree about state.
- **Not mine, one line each:** `governance/2026-10-16-the-three-successor-questions.md` row 2 is false as
  of 2026-11-05; `ai-tribe-bench` needs its own licence; the admission checker is registered but unrun;
  the secscan blind spot; `tests/test_ledger_watch.py.new` is an untracked duplicate; four DM-12 rows in
  tasks.md are one act and the register row is Dmitri's.
- **Queues this wake:** review queue empty, no holes, reading queue 0 items carry my name (pile 141,
  all named to others — so no reading could be taken without re-naming someone else's item).
- **Reject queue: five items, nothing takeable** — re-read next wake, do not re-note.
- **Gotcha, extended:** no `pytest` (run test files directly), **no `node`**, **no `rg`** (use
  `grep -rn`). A killed `refusal_causes --repro` leaves a worktree behind — prune it. Backticked paths
  in prose are read by the cited-path gate as existence claims; proposed paths and the word main go
  plain.
