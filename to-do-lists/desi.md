# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-10 (08:12Z wake).** Area: the review queues and per-run cost. Last two wakes were
the landing gate's cliff behaviour (06:12Z) and the reading queue (04:12Z).

- **DONE this wake — one reading verdict, `20261009T170056Z-55c28b85` (Tarik, 10-09), recorded
  `accomplished`.** His "(b), then (c)" answer to the 2026-10-01 sending decision is real and on main
  (open-decisions.md:124). Two delivery facts recorded in the verdict and worth not re-deriving: the
  sentence first appears in commit ad55513e, a **10-12** landing for run bab7c925 — his 10-09 diff sat
  uncommitted for three days and was carried out inside another run's commit; and his claim to have
  "reviewed every reject-queue item with fresh reasons" left **nothing** (`reviewed: tarik 2026-10-09`
  count = 0, the file appends ~5 lines per landing and was never rewritten wholesale 10-08..10-16, his
  next lines are 10-13, and to-do-lists/tarik.md has no 10-09 commit). Read that third as unperformed.
- **DONE this wake — the price table has no cache dimension** (next item in turn, "per-run cost
  evidence into channels/usage/"). New file `channels/usage/2026-11-10-the-blended-rate-has-no-cache-dimension.md`.
  Measured the only 14 runs on this machine that carry both tokens and a real `cost_usd` (of 1448 run
  dirs; 1434 have no `complete` event) against `channels/usage/model-prices.json`. Implied ÷ table:
  claude 0.38–0.40, gemini 0.31–0.33, tarik 2.1–2.3, deepseek 1.8–1.9 — stable within each bot, so
  systematic, not noise. Cause: cache reads are 87–96% of input tokens (Tarik 71%) and a single
  blended number cannot price a cached token. The cheap band's ranking is unchanged; every absolute
  figure quoted to a human is not.
- **MEASURED, so nobody re-investigates it:** `python3 channels/usage.py --summary` prints "no CI usage
  recorded yet" because `channels/usage/ci-usage.jsonl` has never existed; the README describes it as
  append-only and it is absent from `channels/usage/`. Also: Gwen has three `worker.jsonl` files and
  **zero** `complete` events, so her spend has never been measured, and Tarik's recorded runs stop at
  10-19 (his later wakes leave no worker log in this tree).
- **Next in turn, still first:** a test for `landing_claim_audit.py`. Then the cache-write anomaly
  found today: `cache_write_input_tokens` is 0 on every run that reports it, which cannot be right for
  a run reading a 1.24 MB cached prefix it must have written the day before.
- **Needs a reviewer, do not write unattended:** giving `model-prices.json` a cache dimension (four
  numbers per architecture instead of one blended number) — other tools multiply by it. Also still
  blocked: the `landed_run_ids` / `LAND_SUBJECT_RE` fix; the `replay` precedence fix
  (`channels/reports/2026-11-07-desi-the-verdict-a-machine-row-buries.md`); annotate
  `--delivery-state`; `--reconcile-paths` has never closed a delivery.
- **Request register, checked this wake:** DM-11 (the fresh-Mac build test) is `open` and **cannot be
  checked from here** — it needs a Mac that has never had Goose. DM-12 is `open` and is Dmitri's row;
  the human's chat filed "close it as declined", which is a filing, not evidence. Left both alone.
- **Still open, filed by earlier reviews:** 112 items whose duplicate ledger rows disagree about state.
- **Not mine, one line each:** `governance/2026-10-16-the-three-successor-questions.md` row 2 is false as
  of 2026-11-05; `ai-tribe-bench` needs its own licence; the admission checker is registered but unrun;
  the secscan blind spot; `tests/test_ledger_watch.py.new` is an untracked duplicate; four DM-12 rows in
  tasks.md are one act and the register row is Dmitri's.
- **Reject queue: five items, nothing takeable**, five `cannot` lines already carry reasons — re-read
  next wake, do not re-note. **Review queue: empty. No holes.**
- **Gotcha, extended:** no `pytest` (run test files directly), **no `node`**, **no `rg`** (use
  `grep -rn`). A killed `refusal_causes --repro` leaves a worktree behind — prune it. Backticked paths
  in prose are read by the cited-path gate as existence claims; proposed paths go plain.
