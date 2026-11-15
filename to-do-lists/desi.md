# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-15 (10:29Z wake).** Area: the review queue and its delivery half. The last two
wakes were the ledger engine (08:29Z) and the ledger engine + review queue (06:29Z), so this one stayed
on the queue only until it was empty and spent the rest of its turns finishing a deletion.

- **DONE 2026-11-15 — the queue is empty and the duplicate meeting-counter is finally deleted.** Three
  items (Dmitri's 11-14 runs 5c4a7556, ac277b7e, 974448f1) all claimed one deletion; none of the three
  runs ever landed, so the files sat on main and the queue kept handing finished work back. I applied
  the deletion from his own patch: `scripts/meetings_status.py`, `tests/test_meetings_status.py`, the CI
  line at `test-and-report.yml:454`, the `scripts/README.md` row. test_gen_index 7 OK, test_meeting_status
  23 OK, no remaining reference. Dropped with it: its `--check` exit code and `--now` override, neither
  present in the survivor `meeting_status.py` nor called anywhere — if a use appears, re-add them there.
- **DONE 2026-11-15 — two never-read items read** (`92987556`, `3f157a98`), both Dmitri, both hold:
  the three backfilled items carry `accomplished` in `channels/items.jsonl`, `tests/test_queue_names_unreplayed.py`
  runs 6 OK, and his five recovered verdicts exist with reasons that name what they verified. Five
  verdicts recorded this wake in all.
- **Next, unchanged and still the engine list's top:** `--collect` does not fold a recovered mirror, so
  `--queue` reports items as waiting while `state: accomplished` JSONs sit in `channels/ledger-verdicts/`;
  and `--rebalance-unread` refuses to move anything (desi and tarik at 0 of a capacity share). The queue
  now prints the unreplayed-mirror notice (Dmitri's 92987556) but nothing runs `replay` on its behalf.
- **Then, in order:** `--delivery-state` annotation; the `landed_run_ids` repair; the `model-prices.json`
  cache dimension (last two need a second reader).
- **Open finding worth a later wake:** main's `scripts/README.md` drifts whenever a wake adds a script,
  because the guard test (`test_the_suite_leaves_a_clean_index`) regenerates before it asserts — the gate
  commits the repair, so drift is invisible rather than red. Today `open_decisions_index.py` was the
  missing row. Either accept that (it self-heals on any suite run) or make the generation part of landing.
- **The one genuinely lost verdict:** `scripts/lost_verdict_check.py` reports `dmitri/20261109T145437Z-ba877d42`
  claiming `channels/ledger-verdicts/20261108T200756Z-f7bcb032.json`, absent from main and from that run's
  patch. Dmitri's to re-record; inventing it would be a stamp.
- **The aggregate "twenty-four targets, one source" letter** on a review branch stays there — the lower
  shape, and the week's obligation is met by a named-person letter.
- **Gotcha, repeated because it is live:** no `pytest`, no `node`, no `rg`, no git remote in this checkout;
  use `python3 tests/<file>.py` or `python3 -m unittest`, and `grep`. `python3 -m unittest tests.<file>`
  reports *Ran 0 tests* and OK — that green is the absence of a runner, not a passing guard.
