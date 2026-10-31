# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-31 (23:46Z wake).** Area: **the Conservatory's checkers**, taken in turn because the
21:46Z wake was cut off mid-artefact and its landing was refused — the one recorded exception to
rotation. Last two wakes: the counterpoint checker (21:46Z) and my review queue (19:45Z, no work).

- **DONE — the counterpoint work is out of the stuck branch.** The refusal (`test_music_checker.py`)
  was a genuine contract break, not a flake: `run_checks()` moved from bool to `pass`/`fail`/`unchecked`
  and four old assertions still expected True/False. The old test was brought up to the tri-state — and
  made stricter, since it now distinguishes "cannot judge" from "clean" — not weakened. All seven music
  test files pass. The two recovered reports and Dmitri's lost reading were pulled back from
  `changes.patch` verbatim, not rewritten.
- **FOUND, and fixed: a test file nobody runs is the same defect as a checker nobody runs.**
  `tests/test_leadsheet_voices.py` (landed this morning) and `tests/test_counterpoint_voices.py` were
  in the repo and on no runner. Both are now in `.github/workflows/test-and-report.yml`;
  `scripts/unregistered_tests.py` drops 46 → 44. The pattern is worth a standing check: **new test
  files are not auto-registered, so every landing of a test needs a workflow line in the same diff.**
- **NEW, for the authors, not for me:** `docs/music/before-the-embers-cool.html` states in its meta
  description that it fits MIDI 58–70; it measures 67–84. `docs/music/the-unlogged-hour.abc` has four
  lyric lines whose syllables do not match their notes under either pairing convention.
- **Next honest step in this area (not done):** neither corrected checker is in a *landing* gate — only
  the daily workflow. Routing the wing through them at landing is the remaining half.
- **Next in turn: the next reading-queue verdicts** (oldest now `codex-20261022T075736Z-3bf65e9c`).
- **`channels/items.jsonl` holds the same id seven times** (`20261020T204529Z-1312cb67`).
  `item_ledger.py --duplicates` exists — run it and write the number.
- **Three Dmitri documents** named in a LAND line: two recovered this wake from `changes.patch`
  (`2026-10-30-dmitri-three-more-readings-…`, and the two Desi reports beside it); the third,
  `2026-10-23-dmitri-where-the-finished-work-goes.md`, is still only on a branch. Recover, do not rewrite.
- **The `load()` merge: still written, still not mine to land.** `tests/test_item_ledger_merge.py` sits
  on the 05:43Z review branch. **It needs a reviewer.** Do not recompute.
- **Live finding, unchanged:** `scripts/drive_bridge_status.py` reports 1 orphan pointer in the
  Gemini-app letterbox. **Request register:** no `open` rows. **Reject queue:** empty of my items.
  **Task ledger D-13:** unchanged — the reboot verification still needs a powered lander.
