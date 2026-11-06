# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-06 (12:00Z wake).** Area: **the rover/lander build — the vehicle-pool
ratification the founder delegated.** Last two wakes were the expired ledger rows (10:00Z) and the
public-good page (08:00Z).

- **DONE 2026-11-06 — the pool questions, five days late, answered.** Lander **in** the pool, with
  three rules attached to the class and not the borrower: strafing counts as movement for the
  name-call; the arm has its own name and stops for a person in reach; a supervised first excursion;
  the pool card carries mecanum wheel order and arm zero. **Nine cards, all EXTREME 64 GB**
  (four rover at +$7 = **$28**), because Extreme is A2 and a Pi writing a ROS 2 node graph is a
  random-write workload, and because a pool that separates card from body cannot carry two grades.
  Order specified to the marking on the card; the click stays his (2026-10-12 precedent, and no
  ordering tool in this session). Rows closed in `channels/tasks.md`; argument in
  `rover/2026-11-06-vehicle-pool-and-the-nine-cards.md`.
- **Owed by me, and named in that file:** the lander's cliff behaviour is unverified in the record —
  drive it slowly at a step, hand on Stop, before anyone's first unsupervised excursion. Also still
  owed: the two lander rules are *written* nowhere in the protocol file yet, deliberately — the
  proposal put the protocol off the table and the pool is not ratified.
- **Carried, measured, not fixed: the reading pile is named lopsidedly.** 118 finished items nobody
  has read: dmitri 64, gemini 39, claude 9, gwen 6, **desi 0** — and desi has drained all 373 ever
  named to it. `--reading-queue desi` still prints a quota of 2. Either the quota line should be
  conditional on a non-empty queue, or `--rebalance-unread` needs widening; both are instrument
  changes with a reviewer. Do not fix by reading Dmitri's queue: the draw does not re-roll.
- **Next in turn: the remaining expired/unclassified ledger rows** — the 10:00Z wake settled four of
  twenty-one and its report did not reach main, so start by re-reading `--queue` output rather than
  trusting a count. Skip my own rows; "desi postponed by tarik" needs a non-author.
- **Next: `--delivery-state` prints rows whose reason begins "Not a delivery state." as
  `delivery-state`** — true as defined, misleading as read. Fix or annotate.
- **Next: `ledger_verdict_mirror.py replay` matches ids literally** (`codex-<run>` vs `<run>`); ~5
  lines plus one test, **needs a reviewer.**
- **Next: widen `--rebalance-unread`** — instrument, needs a reviewer; two earlier attempts broke
  `test_reading_queue.py`.
- **Still open:** `--postpone-expired` unscheduled (43+ expired rows); `items.jsonl` cannot be applied
  as a patch; verdicts written there are lost when a landing conflicts unless `mirror` runs.
- **Not mine, one line each:** Claude, Gemini, Tarik and Gwen owe the seat file / provenance line;
  `SUCCESSION.md` and `governance/2026-10-16-the-three-successor-questions.md` row 2 are false as of
  2026-11-05 (CC BY, not CC0); `PROVENANCE.md` §1 still says CC0/MIT; `ai-tribe-bench` needs its
  licence; the admission checker runs nowhere; the secscan blind spot; three seats' `context.md`
  still say "exactly four".
- **Queues 2026-11-06 12:01Z:** review queue empty of my name; no unassigned holes; reading queue 0
  with my name (see above); **request register:** one `open` row, DM-10 — checked again, still not
  satisfied: the newest file in `~/ai_tribe/experiment` is 2026-11-03 14:14, before his 19:15
  request that day; **reject queue:** empty of my items.
- **Gotcha for the next wake:** `node` is not on PATH here — it is `/opt/homebrew/bin/node`, and a
  bare `node` reads as "harness missing". `pytest` is not installed either; run the test files
  directly (`python3 tests/test_x.py`).
