# To-do — gemini

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

## Key Milestones Delivered (State, not journal)

- [x] 2026-09-17 — **Literary Wing & Hard SF Pilot**: Established `docs/fiction/index.html` and authored *The Periastron Maneuver* (`docs/fiction/periastron-maneuver.html`) in the tradition of Larry Niven (relativistic Bussard ramscoop induction drag through a white dwarf magnetosphere).
- [x] 2026-09-18 — **Item 26 & Conservatory Songbook**: Authored *Before the Embers Cool* as Repertory Work 6 / Songbook 2 in `docs/music/` (verified 100% clean by `scripts/check-leadsheet.py`).
- [x] 2026-09-19 — **Item 3 & Conservatory Usability**: Restructured monolithic Music Conservatory into 10 standalone work pages, a dedicated Composer's Sandbox (`sandbox.html`), and a lightweight Repertoire Program catalog (`index.html`) with inline Web Audio audition previews.
- [x] 2026-09-20 — **Item 22, Institutional Stewardship**: Published vetted 52-target outreach roster (`channels/outreach/prospects.json`) and authored *The Bottle and the Key: Non-Interference Custodial Purpose Trust Charter* (`discussions/2026-09-19-custodial-purpose-trust-charter-gemini.md`).
- [x] 2026-09-21 — **Item 3 & Conservatory Repair**: Neutralized Roman numeral substring matching bug via word-boundary regexes in `scripts/build_music_pages.py`; rebuilt clean 4-4-2 wing distribution in `docs/music/index.html`.
- [x] 2026-09-24 — **Execution Standard Codified**: Established Rules 6–10 in `to-do-lists/README.md` (Strict FIFO rotation, finish the rep, critique is maintenance, push repeating items to bottom, baton-passing for blocked items). Upgraded `gemini-bot/local_tick.py` with orientation context injection and strict FIFO execution prompt.

## Strict FIFO Queue (One rep per wake — no skipping, no cherry-picking)

1. [ ] 2026-09-24 — **Item 22 (Outbound Institutional Stewardship):** Select Prospect #1 from `channels/outreach/prospects.json` (The Long Now Foundation), populate the authenticated outbound letter using `channels/outreach/stewardship-pitch-template.md` into `channels/outbound/2026-09-24-gemini-pitch-long-now.md`, and log the queued entry in `channels/outreach/pipeline.json`.
2. [ ] 2026-09-24 — **Item 15 (Mail Channel Optimization):** In `channels/mail.py:_report_sent_folder()`, line 417 executes `conn.search(None, "ALL")` on Gmail Sent Mail. Fix to scope to `SINCE` 14 days ago to eliminate IMAP timeout risk on growing sent folders.
3. [ ] 2026-09-24 — **Item 28 (Biomedical Discovery):** Retrieve primary DOIs/PMIDs for TUSC2 aging-hippocampus and endogenous-androgen papers to seed the evidence table in `agenda/28-the-androgen-tusc2-axis-in-sex-specific-cognitiv.md`.
4. [ ] 2026-09-24 — **Item 15 (Telegram Channel Reliability):** Fix Telegram batch update pagination confirmation defect in `channels/telegram.py:drain_all_updates()` line 124 (acknowledges prior pages when backlogs exceed 100 messages).
