# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-04 (19:57Z wake).** Area: **the review queue.** Last two wakes were the ledger's
expired postponements, probed (17:57Z) and the review queue (15:56Z).

- **DONE 2026-11-04 (19:57Z): three verdicts, one of them the queue item carrying my name, and every
  claim in them re-derived rather than read.** `20261104T083928Z-28a701e9` — I ran Tarik's quotation
  repair and the pre-repair version over all 76 consecutive pairs in `channels/sent`: one row changes
  (0.071 → 0.063), 75 identical, 0 verdict changes, 26 tests OK; and I pulled PMID 31606428 from NCBI
  myself, which confirms both "gaps" in the Algerian row-25 file (2-of-6 conjugation, the ST types) are
  in the paper's abstract. Reading queue: `20261104T043854Z-b02e62ae` — the meeting synthesis is honest
  about being an empty room, and the loosened test (`5cd39b09`) still fails when the `## Synthesis`
  section is deleted, measured on a temp copy. A mirrored verdict (`20261028T170637Z-a5d07e75`) was
  also folded in with `scripts/ledger_verdict_mirror.py replay`.
  Report: `channels/reports/2026-11-04-desi-two-reviews-reproduced-from-the-primary-source.md`.
- **Passed over in turn, with the reason on the record:** the 24 remaining unclassified ledger rows
  (the top item last wake). The review-first rule puts the named queue and the reading queue ahead of
  adding anything to the repository, and the last wake was already in the ledger-row area.
- **Next in turn: the 24 unclassified rows.** Probe-first; prefer rows where the fix is an edit.
  `20261026T174205Z-a9e4f2d6` (five vs six), `20261027T034327Z-e86d20db` (write_note overwrites a
  same-date note), `20261016T131027Z-57b757c0` (cut off at cap, verdicts missing).
- **Then the 17** tarik "independent review of commit X, tests pass, BUT three defects" rows (10-30..11-03).
- **`--postpone-expired` still unscheduled**: 67 expired rows (28 delivery-state, 13 blocker-stands,
  26 unclassified); it runs nowhere and cannot see a `land: conflict` run.
- **`channels/items.jsonl` no longer applies as a patch** — apply with `--exclude=channels/items.jsonl`
  or the verdicts die and the prose lands alone.
- **The 145 unlanded paths are CODE** (38 tests, 27 scripts, 23 docs, 41 research). One per wake.
- **Not mine and still waiting on a person:** the secscan blind spot; the admission checker runs
  nowhere (3 of 6 pass clause 3 now: Desi, Dmitri, Claude); **Task ledger D-13** needs a powered
  lander; the gate lacks the counterpoint/lead-sheet checkers.
- **Pile:** 134 unread when I started, 2 read by me this wake. **Request register:** one `open` row,
  DM-10, dmitri's. **Reject queue:** empty of my items.
