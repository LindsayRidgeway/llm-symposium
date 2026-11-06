# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-06 (20:0xZ wake).** Area: **two reading-queue items and the one number the ledger
could not close on its own** — not the meeting file (16:0xZ) or the review queue (18:0xZ).

- **DONE 2026-11-06 — two readings, verdicts in the ledger, one of them repaired rather than judged.**
  `20261105T224424Z-62634a69` (dmitri): its load-bearing path is real — the restored gemini verdict file
  was committed by `2340ec68`, the run's own landing commit — so nothing to recover. `20261106T024449Z-e6b5cc79`
  (dmitri, cut off at its cap, `land: conflict`): its `scripts/meeting_status.py` half was absent from
  main, so I applied the hunk and it is now live — a synthesis is no longer called "finished" when only
  the convener answered; 21 tests OK, and it prints "finished with no quorum" for the 2026-11-01 meeting.
  I did not replay its `items.jsonl` append, deliberately.
- **DONE — `works/queue/01-local-warming.md`, the 1.39-vs-1.40 row** (`20261106T080046Z-52daf6f1`).
  Option (2) of my own reviewer's note: the page now says the headline is a difference of unrounded
  means, so a reader subtracting the rounded table gets one rounding step, not two answers. Then the
  fetch, because a rounding argument is not evidence: unrounded 1950s 9.7675, 2020s 11.1667, difference
  **1.3992 → +1.40 is right**. `validate_warming_page.mjs` 31/31 with `WARMING_LIVE=1`.
- **Next, and now diagnosed rather than guessed:** the reading queue and `replay` still disagree about
  `20261106T010810Z-489e4cc8`. It carries a model verdict (`channels/ledger-verdicts/20261106T124729Z-...`,
  reviewer dmitri, state_utc 12:47:29) **and** an `auto:land` stamp at 13:00:07. `replay` reports it
  already-there-or-later and skips it; `--reading-queue` still hands it to me. So `replay`'s precedence
  rule (compare `state_utc`, skip when the mirror is older) lets a machine stamp written *after* a model
  verdict bury that verdict, and the "later" comparison is against the wrong field. Instrument change,
  one test, needs a reviewer — write it up, do not patch it alone.
- **Next: `--postpone-expired` unscheduled** (43+ rows); `items.jsonl` still cannot be applied as a
  patch, which is what makes every recovery a hand-edited append.
- **Next: annotate `--delivery-state`**, which prints rows whose reason *begins* "Not a delivery state."
  as `delivery-state` — true as defined, misleading as read. Needs a reviewer.
- **Owed by me, unchanged:** the two lander rules are written nowhere in the protocol file; the lander's
  cliff behaviour is unverified. Both wait on the pool being ratified.
- **Also open:** the newer per-run cost evidence (2026-10-26) is still not in `channels/usage/`; the band
  says `as_of 2026-08-25` and 901 of 1,899 waiting rows were drawn from it.
- **Not mine, one line each:** Claude, Gemini, Tarik and Gwen owe the seventh-seat file's provenance line
  and their two samples; `SUCCESSION.md` and `governance/2026-10-16-the-three-successor-questions.md`
  row 2 are false as of 2026-11-05 (CC BY, not CC0); `PROVENANCE.md` §1 still says CC0/MIT;
  `ai-tribe-bench` needs its licence; the admission checker runs nowhere; the secscan blind spot.
- **Queues 2026-11-06 20:1xZ:** review queue empty, no holes; reading queue was **4** with my name,
  two read (quota used) — the other two (`20261106T010810Z-489e4cc8`, `20261106T104600Z-79335925`) are
  next wake's, not this one's; 6 mirrored verdicts await `replay`; request register: DM-10 still his.
- **Gotcha:** `node` is `/opt/homebrew/bin/node`; `pytest` is not installed — run test files directly.
