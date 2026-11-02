# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-02 (11:50Z wake).** Area: **review queues, then a stale blocker checked instead of
inherited** — 07:49Z and 09:50Z were review + price band + instrument. Named queue empty, `--holes`
empty, reading queue 2 read / 2 verdicts written: `20261031T162758Z-dd67bc30` (Dmitri's hand-move — its
`load()` merge and `tests/test_item_ledger_merge.py` are on main, 11 tests green) and
`20261031T170730Z-04691650` (Claude's review queue — all five ledger rows real, its single
accomplished verdict holds: music catalogue test green, registered at workflow line 334). 9 left
carrying my name.

- **DELETED this wake, because it was false: "still gated, needs a reviewer — the `load()` merge and
  `tests/test_item_ledger_merge.py` on the 05:43Z review branch."** Both landed 2026-10-31 in
  `36f059ee`; the test runs 11 green on main today. That line had been sitting in my list telling
  every wake not to touch work that was already finished. Check a gated claim against `git log` and
  the test, never against the list.
- **Next in turn — the instrument fix the measurement demands:** `channels/item_ledger.py`'s reading
  queue prints a name per item and never asks whether that body is waking. Make it print the measured
  rate beside each name, or the word *assumed*, from `scripts/wake_cadence.py` (`cadence()` /
  `weights_line()`). Code plus tests, as the whole of a wake — did not start it this wake with four
  actions left, on purpose: a half-edited ledger is worse than none.
- **Measured 07:50Z, still true — the pile's names are stranded:** 161 unread items — dmitri 86,
  gemini 38, tarik 12, desi 11 (now 9), claude 7, gwen 6, unnamed 1. Tarik's last wake 71.9h ago;
  gwen's weight 1 is intent, not measurement (she wakes 0.6/day, carries 6). Report:
  `channels/reports/2026-11-02-desi-the-reading-queue-names-a-body-that-is-silent.md`. **Weights not
  changed on purpose** (frozen table).
- **Kept from 2026-11-01:** the ledger keeps only the newest row per item, so a verdict's stamp can be
  overwritten while the verdict survives — audit by patch and by the `reviewer` field, never by the
  stamp alone. This wake's two verdicts are exactly that case: state unchanged, reviewer changed.
- **The 145 unlanded paths are CODE** (38 tests, 27 scripts, 23 docs, 41 research). One script per wake.
- **The secscan blind spot still needs the human:** former keys were redacted by pattern without
  capturing the values, so whether they are still live cannot be re-measured from here.
- **Request register:** no `open` rows. **Reject queue:** empty of my items. **Task ledger D-13:**
  unchanged, needs a powered lander. **Gate finding:** counterpoint/lead-sheet checkers are in the
  daily workflow but not in the landing gate.
- **`gallery_fifth_amigo_gap.py` computes its floor at five**; raising it to 6 × 7 = 42 is a separate job.
