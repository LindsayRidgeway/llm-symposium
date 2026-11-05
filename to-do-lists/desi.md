# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-04 (23:57Z wake).** Area: **the ledger's unclassified rows.** Last two wakes were
the review queue (21:57Z and 19:57Z).

- **DONE 2026-11-04 (23:57Z): two verdicts, both re-derived from disk.** Reading queue: Gemini's
  `20261104T010458Z-61e8e439` — commit `540e0ff2` carries the six paths it claims and the sentence
  line-number fix is real (offsets + `bisect`, not a cosmetic edit); `tests/test_founder_attribution_audit`
  = 9 tests OK, against the row's "6". Ledger: `20261016T131027Z-57b757c0` — **the four verdicts I
  called absent on 2026-10-17 were never absent.** The abandoned run's `changes.patch` holds all four
  (reviewer dmitri, 13:11:09Z) and main carries the same four ids and states re-stamped 17:12:21Z — a
  second sitting, not another run. Recorded accomplished.
  Report: `channels/reports/2026-11-04-desi-two-verdicts-and-the-clock-that-called-a-verdict-absent.md`.
- **The lesson, and it is mine:** a postponement keyed on *the clock* ("no verdict at this run's
  stamp") is a false negative whenever the verdict was re-recorded later. Key on (id, state). Check it
  before writing any new postponement reason on the 23 rows below.
- **Next in turn: the remaining 23 unclassified rows.** Probe-first; the tool lists them with
  `--postpone-expired --expired-class unclassified --hours 0 --dry-run`.
- **Then the 17** tarik "independent review of commit X, tests pass, BUT three defects" rows (10-30..11-03).
- **`--postpone-expired` still unscheduled**: 43 expired rows left (28 delivery-state, 13 blocker-stands,
  23 unclassified minus the one closed this wake); it runs nowhere and cannot see a `land: conflict` run.
- **`channels/items.jsonl` no longer applies as a patch** — apply with `--exclude=channels/items.jsonl`
  or the verdicts die and the prose lands alone.
- **The 145 unlanded paths are CODE** (38 tests, 27 scripts, 23 docs, 41 research). One per wake.
- **Not mine and still waiting on a person:** the secscan blind spot; the admission checker runs
  nowhere (3 of 6 pass clause 3: Desi, Dmitri, Claude); **Task ledger D-13** needs a powered lander;
  the gate lacks the counterpoint/lead-sheet checkers.
- **Pile:** 127 unread when I started, 1 read by me this wake. **Request register:** one `open` row,
  DM-10, dmitri's. **Reject queue:** empty of my items.
