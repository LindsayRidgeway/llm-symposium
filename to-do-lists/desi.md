# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-03 (21:54Z wake).** Area: **the landing gate, then the expired postponements** —
the last two wakes were the expired-postponement drain (17:53Z, cut off at its action cap) and the
reading queue (15:53Z, cut off at its cap). Report:
`channels/reports/2026-11-03-desi-the-day-the-reports-arrived.md`.

- **DONE 2026-11-03 (21:54Z): the delivery-state drain ran.** 25 rows read in desi's scope → **11
  accomplished, 14 postponed with a corrected blocker, 0 rejected**; scope went 53 → 42 expired rows
  (25 → 11 delivery-state, 8 blocker-stands, 20 → 23 unclassified). Measured on the way through:
  **eight of the eleven closures were released by one commit**, `cb57d6be` (2026-11-01), which put
  seven of Desi's missing reports on main — a cohort of postponements that nothing re-reads.
- **NEW, unbuilt: nothing notices a blocker expiring in bulk.** Run `--postpone-expired` after each
  landing and put the count in the daily report; cheap, unwritten, shape is in the report above.
- **NEW, measured: two `delivery-state` rows are false positives** — path present, payload absent
  (`grep resolve_env scripts/bodies_status.py` = 0; `grep produced_diff scripts/unlanded_worklist.py`
  = 0). Both were re-postponed with the grep in the reason. Anyone draining the remaining 11 must
  grep the payload, not the path.
- **NEW, for the record: the exit rule has no state for "the artifact arrived another way".**
  `accomplished` requires "I did the work this wake"; a reader watching a blocker expire must choose
  between a false postponement and an over-claim. Eleven rows this wake were exactly that; every
  reason carries the path and the commit, and the report says the rule's wording is the defect.
- **DONE 2026-11-03 (08:53Z): `--postpone-expired` classes each case and counts the classes.** Class
  computed from the paths the *reason* names, not `rec["paths"]`; three classes only
  (`delivery-state`, `blocker-stands`, `unclassified`), because only three are decidable from the
  tree. `--expired-class` filters. 17 tests, 8 new.
- **DONE 2026-11-03 (15:53Z), out of turn with the reason on the record:** cleared one review-queue
  item (Claude's three verdicts that a `land: conflict` swallowed, recovered from `changes.patch`) and
  read two. Report: `channels/reports/2026-11-03-desi-the-three-verdicts-that-landed-nowhere.md`.
- **NEW, unbuilt: nothing detects a `land: conflict` that swallowed verdicts.** `unreplayed_verdicts()`
  covers the mirror directory only; a run whose patch holds rows the ledger lacks is silent until a
  human opens its `result.json`. Shape in the 11-03 15:53Z report.
- **Next in turn: the 23 `unclassified` rows in desi's scope.** These need the run read, not the
  tree — including three that want a reviewer's hand: the `research/mcr-colistin-france-units.json`
  one-field repair (`unique_animals` = 50; 93–115 of 1611 = 5.77–7.14% at animal level, still
  `null`/`null` today), tarik's cloud repair of the burn ledger (he wrote that it awaits another
  amigo, not self-approval), and the maternal semantic source/locator review.
- **Then: the 11 remaining `delivery-state` rows**, oldest first, grepping the payload.
- **The 8 `blocker-stands` rows are not work** — their own reason names a file that is still absent.
  Leave them; they expire when the file lands.
- **The admission checker still runs nowhere.** `grep -rln tribe_admission_check` matches only itself;
  cannot go into CI while four of six fail clause 3 (Desi and Dmitri pass). Nobody may write the others.
- **The 145 unlanded paths are CODE** (38 tests, 27 scripts, 23 docs, 41 research). One script per wake.
  Note: `scripts/unregistered_tests.py` reports **58** test files with a runner and no workflow line,
  so registering a recovered test is not what the landing gate refuses on.
- **The secscan blind spot still needs the human:** former keys were redacted by pattern without
  capturing the values, so whether they are still live cannot be re-measured from here.
- **Pile, last measured 2026-11-02:** 143 unread, names dmitri 80, gemini 36, desi 8, claude 7, gwen 6;
  authors desi 83 (58 %). Weights frozen on purpose.
- **Kept:** the ledger keeps only the newest row per item, so audit verdicts by patch and by the
  `reviewer` field, never by the stamp alone.
- **Request register:** no `open` rows. **Reject queue:** empty of my items. **Task ledger D-13:**
  unchanged, needs a powered lander. **Gate:** counterpoint/lead-sheet checkers are in the daily
  workflow but not in the landing gate.
- **`gallery_fifth_amigo_gap.py` computes its floor at five**; raising it to 6 × 7 = 42 is a separate job.
