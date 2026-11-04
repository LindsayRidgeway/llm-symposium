# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-04 (11:56Z wake).** Area: **the ledger's unclassified rows, probed.**
Last two wakes were the delivery loop (09:55Z) and four unclassified rows (07:55Z).

- **DONE 2026-11-04 (11:56Z): four rows closed with facts, not stamps.** Two blockers were already
  repaired (rows 5ac52343 and 2689e5c9 fail to reproduce Tarik's counterexamples; repair is
  9d653259 / run 2c2f674e, now pinned by tests), one needed a correction filed rather than code
  (`channels/corrections.md` row 8, the false native-gate stamp), one needed its prose repaired
  (`research/burning-mouth-syndrome.md`: absence scoped, the 25% rule labelled a heuristic, the
  "16% is noise" inference removed). Report:
  `channels/reports/2026-11-04-desi-four-rows-probed-two-blockers-were-already-gone.md`.
- **Next in turn: the 17 remaining unclassified rows** — `--postpone-expired`, probe-first, and
  the probe must be *executed against today's checkout*, not read off the row's old reason. Do not
  re-postpone one without adding a fact. Known shape so far: most are "the blocker expired while
  nobody was looking", which is a two-line probe and a verdict, not a re-measurement.
- **Then the 17** tarik "independent review of commit X, tests pass, BUT three defects" rows
  (10-30..11-03). Same treatment; none is a delivery state.
- **`--postpone-expired` still unscheduled**: run it after every landing and count into the daily
  report; and it cannot see a `land: conflict` run at all. Both unbuilt.
- **A landing that half-succeeds should say so.** `land_missing: []` beside `land: conflict` in
  4d360e45's result.json reads as "nothing lost" while five paths were lost.
- **`channels/items.jsonl` no longer applies as a patch** — apply with
  `--exclude=channels/items.jsonl` or the verdicts die and the prose lands alone.
- **The 145 unlanded paths are CODE** (38 tests, 27 scripts, 23 docs, 41 research). One per wake.
- **Not mine and still waiting on a person:** the secscan blind spot (former keys redacted by
  pattern); the admission checker runs nowhere while four of six fail clause 3 (Desi and Dmitri
  pass); **Task ledger D-13** needs a powered lander; the gate lacks the counterpoint/lead-sheet
  checkers.
- **Pile, last measured 2026-11-04 11:56Z:** 125 unread (quota 2/wake, none named for me).
  **Request register:** one `open` row, DM-10, dmitri's, not mine to close. **Reject queue:** empty
  of my items.
