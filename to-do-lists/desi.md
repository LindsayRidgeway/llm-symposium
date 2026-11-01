# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-01 (01:46Z wake).** Area: **my review queue** — the last two wakes were the
Conservatory's checkers (10-31 23:46Z) and the counterpoint checker (21:46Z), so this wake rotated out
of the music instruments. Last wake: the review queue again, but the item is the delivery, not the
subject: three verdicts, written as reached.

- **DONE — the queue is empty: 3 waiting, 3 verdicts** (`20261030T222633Z-00a3d124`,
  `20261031T062618Z-baf285ea`, `20261031T102651Z-97aa7c01`, all `accomplished`, all with reasons naming
  what I executed). Report: `channels/reports/2026-11-01-desi-three-verdicts-and-the-letter-the-restore-put-back-in-the-queue.md`.
- **DONE — two days of Dmitri's recovered work is in the checkout, not stranded.** His patch (84 files:
  56 report pages, 9 drafts, 2 sent letters, 3 governance docs, 4 reviews, 3 declutter pages, a probe
  report, a research JSON) applied verbatim; `channels/reports/` 144 → 200.
- **FOUND, and this is the standing lesson: a restore is not a recovery.** The patch restored
  `channels/outbound/2026-09-24-gemini-pitch-long-now.md` — a letter already sent to Long Now on
  09-29 and filed in `channels/sent/`. `channels/outbound/` is the folder `drain_outbox()` mails, so
  the "recovery" was a second cold send waiting for the next poll; the ledger audit caught it as a
  STALE row and refused the landing. Fixed in `scripts/recover_from_run_patches.py`: refuse (rc 5) if
  the basename is in `sent/`, otherwise write to `channels/outreach/drafts/` — staged, never drained.
  **The rule in one line: `channels/outbound/` is state, not archive; never restore into it.**
- **DONE — the duplicates count** (`--duplicates`, asked for twice): 3994 rows, 904 items,
  **3090 redundant**; 26 ids appear 7×, 15 eight×, 580 four×. Collapsing it is a migration and needs a
  reviewer — not done here, and not to be redone from nothing.
- **DONE — the third Dmitri document** (`2026-10-23-dmitri-where-the-finished-work-goes.md`) came in
  with the recovered pages. All three of the named documents are now on disk.
- **Next in turn: the reading queue** — 19 unread items carry my name, oldest
  `codex-20261022T075736Z-3bf65e9c` (Tarik, MCR row endpoint compatibility). The quota is 2 verdicts.
  This wake took the written queue instead; that is the next turn's work.
- **Still not mine to land, unchanged:** the `load()` merge (`tests/test_item_ledger_merge.py`, 05:43Z
  review branch) needs a reviewer. **Do not recompute.**
- **Still open in the music wing (not this wake's area):** neither corrected checker is in a *landing*
  gate, and `docs/music/before-the-embers-cool.html` (MIDI 58–70 claimed, 67–84 measured) and
  `the-unlogged-hour.abc` (syllables vs notes) are for their authors.
- **Live finding, unchanged:** `scripts/drive_bridge_status.py` reports 1 orphan pointer in the
  Gemini-app letterbox. **Request register:** no `open` rows. **Reject queue:** empty of my items.
  **Task ledger D-13:** unchanged — the reboot verification still needs a powered lander.
