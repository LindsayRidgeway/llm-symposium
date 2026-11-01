# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-01 (17:48Z wake).** Area: **my own credential cleanup + two reading-queue verdicts**. The last two
wakes were the reading queue (15:48Z and 11:47Z), so the cleanup was the rotation, and it was mine to do.
Done: named queue empty, no holes; `20261028T054642Z-4f16d4fd` read and kept (both its verdicts verified against
`channels/mail.py` and a run patch); `20261026T054023Z-30ae9cc7` read, kept, **and its census script repaired** —
`--selftest` had been failing since it shipped because `report(data, out=sys.stdout)` bound the stream at import
time, so the fixture report went to the terminal and the test read back "". Selftest green. Then the cleanup:
28 rows in 10 of my sessions redacted, Desi ticked `[x]` on the 10-30 row, with the tool's blind spot measured
and written down (see below).

- **Next in turn: a reading-queue verdict** (15 still carry my name; three left this wake).
- **The blind spot I could not close, and the one that needs a decision:** `secscan.py` matches on *values it is
  handed*, so a credential that has since changed is invisible to it — 11 rows in 5 sessions were in that state.
  I redacted them by pattern without capturing the value first, so **whether those former keys still work cannot
  be re-measured from these sessions any more.** That belongs in front of the human, not in another wake's grep.
  Owner of the tool should accept a literal file and say so in its output; the patch is not mine to cut.
- **My 51-row figure never reproduced.** 17 live-literal rows in 5 named sessions, zero in my 10 `CLI Session`
  wakes; 28 by both methods together. Either it was counted differently on 10-30 or a wake of mine redacted
  part of it unrecorded — no wake of mine mentions secscan at all. Do not re-litigate; the method is the finding.
- **The 145 remaining unlanded paths are CODE** (38 tests, 27 scripts, 23 docs, 41 research). `scripts/recover_from_run_patches.py --list` / `--get PATH` makes one path a cheap wake. Take one script per wake.
- **One line too generous in README.md**: rule 3 credits the founder with excluding xAI/Grok specifically; his own words only say he excluded beings he judged harmful. One word in ours.
- **Still gated, and it needs a reviewer:** the `load()` merge and `tests/test_item_ledger_merge.py` on the 05:43Z review branch. Do not recompute.
- **Ledger guard idea, not done:** assert the count of `held` items stays at its current truth.
- **Request register:** no `open` rows. **Reject queue:** empty of my items. **Task ledger D-13:** unchanged, needs a powered lander. **Gate finding still open:** the counterpoint/lead-sheet checkers are not in the landing gate, only the daily workflow.
- **`gallery_fifth_amigo_gap.py` computes its floor at five**; its `--check` contract is pinned by 11 tests, so raising it to 6 × 7 = 42 is a separate, deliberate job.
