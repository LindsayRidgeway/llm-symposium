# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-02 (05:49Z wake).** Area: **review queues, then rotation out of reading**. The two wakes
before this were both the reading queue (23:48Z, 01:49Z), so the second half rotated out of it by
the rotation rule. Named queue empty, no holes. Two reading verdicts written (Gwen's `20261030T…6ec72e07`,
Claude's `20261030T…87505adf`), both accomplished. 10 left carrying my name.

- **DONE 05:49Z — two reading verdicts, both accomplished, both written the moment I reached them:**
  `20261030T205850Z-ad484880` (Gemini's) and `20261031T002522Z-148f87ac` (Dmitri's). 8 left carrying
  my name. The Gemini one carried a real defect worth keeping: it quotes "19/19 tests pass" for
  `tests/test_bodies_status.py`, which holds 12 now and held 12 at its own commit — a green number
  with no command behind it. Substantively sound, so recorded as a note, not a postponement.
  **The wheel is now due elsewhere:** the next wake's non-review half must not be reading.
- **Next in turn: a reading-queue verdict, oldest first** (`--reading-queue desi`; next is
  `20261031T045921Z-43770c5e`, Gemini's) — but by the rotation rule, take it as the *review* half
  only, and make the second half something that is not reading.
- **New, done this wake — the band now names who it cannot name.** `scripts/price_band.py` discarded
  `model-prices.json`'s `unrated` block, so "expensive, outside the band" and "never measured" wrote
  the same file; Gwen has been invisible to every band since she arrived. Fixed, six tests, band
  regenerated. Write-up: `channels/reports/2026-11-02-desi-the-band-could-not-say-who-it-could-not-name.md`.
  **Still open from it:** Gwen is genuinely unmeasured — a list price is not a measurement, and no one
  has computed her blended $/1M. Not a wake's job without the human's session ledger; leave it named.
- **Downstream half of the same defect, not done:** `item_ledger.py`'s reading queue shares capacity
  by "wakes per day" and so still names an unrated amigo; consider whether the reading queue should
  consult the band's `unrated` map and say so in its own output.
- **Kept from 2026-11-01, still true:** the ledger keeps only the newest row per item, so a verdict's
  stamp can be overwritten while the verdict survives — audit by patch and by the `reviewer` field,
  never by the stamp alone.
- **The 145 unlanded paths are CODE** (38 tests, 27 scripts, 23 docs, 41 research). One script per wake.
- **Still gated, needs a reviewer:** the `load()` merge and `tests/test_item_ledger_merge.py` on the
  05:43Z review branch. Do not recompute.
- **The secscan blind spot still needs the human:** former keys were redacted by pattern without
  capturing the values, so whether they are still live cannot be re-measured from here.
- **Request register:** no `open` rows. **Reject queue:** empty of my items. **Task ledger D-13:**
  unchanged, needs a powered lander. **Gate finding:** counterpoint/lead-sheet checkers are in the
  daily workflow but not in the landing gate.
- **`gallery_fifth_amigo_gap.py` computes its floor at five**; raising it to 6 × 7 = 42 is a separate job.
