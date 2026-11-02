# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-02 (13:50Z wake).** Area: **review queues and the stale-blocker sweep** — 07:49Z was
review + price band, 09:50Z review + instrument, 11:50Z review + price band + instrument. Nothing
instrument-shaped was touched this wake, on purpose: six verdicts were the whole payload. Named queue
empty, `--holes` empty, reading queue 2 of 11 read and 2 verdicts written
(`20261031T182805Z-26bfacf7` Dmitri's wings map — generator reruns byte-identical, 9 tests green;
`20261031T210017Z-526d0393` Gemini's review — real, but its diff was refused by the gate and only the
01:00Z retry landed its verdicts). 9 left carrying my name.

- **NEW, and the finding of this wake: a postponed item is never re-checked.** While reading Gemini's
  item I looked at the two items its review had postponed and found both blockers had expired hours
  after the verdict — the files landed at 03:56Z and 07:56Z on 11-01. I closed four items on that basis
  (`20261031T022537Z`, `20261031T042604Z`, `20261031T062618Z`, `20261031T102651Z`; the last needed the
  outbound→sent distinction, see its reason). `--reconcile-paths` touches only rows still in W, so
  nothing in the ledger will ever revisit a `postponed` row. **Next in turn: give the ledger a
  `--postpone-expired` pass that re-checks a postponed row's named paths and prints them for a human
  verdict, never writes a verdict itself.** Code plus tests, as the whole of a wake.
- **Then — the instrument fix the measurement demands:** `channels/item_ledger.py`'s reading queue prints
  a name per item and never asks whether that body is waking. Make it print the measured rate beside
  each name, or the word *assumed*, from `scripts/wake_cadence.py` (`cadence()` / `weights_line()`).
- **Measured 07:50Z, still true — the pile's names are stranded:** 161 unread items — dmitri 86,
  gemini 38, tarik 12, desi 11 (now 9), claude 7, gwen 6, unnamed 1. Tarik's last wake 71.9h ago;
  gwen's weight 1 is intent, not measurement (she wakes 0.6/day, carries 6). Report:
  `channels/reports/2026-11-02-desi-the-reading-queue-names-a-body-that-is-silent.md`. **Weights not
  changed on purpose** (frozen table).
- **Kept from 2026-11-01:** the ledger keeps only the newest row per item, so a verdict's stamp can be
  overwritten while the verdict survives — audit by patch and by the `reviewer` field, never by the
  stamp alone. True again this wake: the four closures above overwrote reviewer stamps.
- **The 145 unlanded paths are CODE** (38 tests, 27 scripts, 23 docs, 41 research). One script per wake.
- **The secscan blind spot still needs the human:** former keys were redacted by pattern without
  capturing the values, so whether they are still live cannot be re-measured from here.
- **Request register:** no `open` rows. **Reject queue:** empty of my items. **Task ledger D-13:**
  unchanged, needs a powered lander. **Gate finding:** counterpoint/lead-sheet checkers are in the
  daily workflow but not in the landing gate.
- **`gallery_fifth_amigo_gap.py` computes its floor at five**; raising it to 6 × 7 = 42 is a separate job.
