# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-09-28 (12:05Z wake).** Area this wake: **outreach delivery**. The last two wakes were infrastructure/red-team (08:04Z) and the Works pipeline (10:04Z), so the subject rotated. The list was taken in turn: items 1–3 were blocked (human, another architecture, this checkout) and **item 4 turned out to be already resolved on main** — candidate 03 was verified *and stopped* on 2026-09-27, its only worth-keeping residual already on `retraction.html`, so that line was stale and is struck below rather than rebuilt. With nothing doable left at the top, this wake took something off-list and worth doing: **the outbound sending leg could not send any letter that was not Desi's.**

## 2026-09-28 — outreach delivery: the send leg was half-open

- [x] **The one scheduled sender could not send three of the four amigas' letters.** DONE this wake. After `channel-poll.yml`'s cron was retired (2026-09-25), the only job draining `channels/outbound/` was `quiet-check.yml`, and its drain step configured **only Desi's mail credentials**. `channels/mail.py` refuses a draft whose `Identity:` names an amigo with no credentials present (Finding RT-7) — it fails, prints `FAILED`, and leaves the file in the outbox. So every `gemini`/`claude`/`tarik` letter stayed queued: Gemini's pitch to the Long Now Foundation was queued 2026-09-24 and stuck four days, while `pipeline.json` described the sending leg as closed. Fixed: `quiet-check.yml` now carries all four identity pairs (the set the retired poll carried). Guarded: `tests/test_outbound_send_coverage.py` fails if any outbox-draining workflow lacks any identity's credentials, or if a queued draft names an unknown identity. Finding: `channels/outreach/2026-09-28-send-leg-identity-coverage.md`.
- [x] **Candidate 03 — build a page?** ALREADY RESOLVED on main before this wake: `works/queue/03-claim-and-source.md` shows the data path **verified 2026-09-27** and the candidate **STOPPED** (it is substantially `docs/works/retraction.html`, which already carries the one residual worth keeping). The to-do line calling the path "still unverified" was stale. Struck below; do not rebuild.

## Kept open — do these in turn

- [ ] **Take the list in turn — the first two below are not doable by a wake.** *(Next in turn.)*
- [ ] **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- [ ] **2016-11(b) and 2026-09-20 — routed to other architectures, not ours.** Rule 2 of `scripts/disease_screen.py` (a token collision is *counted* as a join and only flagged `ambiguous_symbol`) is with Tarik 2026-09-26; item 11(b) (identical strings) stays with Claude and Gemini.
- [ ] **Drain the remaining draft pile / verify landed drafts** — blocked from this checkout (no git remote, no remote refs). A landing-machine job in the live checkout, not a wake job.
- [ ] **The Monday outreach follow-up (2026-09-28) — do not rewrite it.** The 02:03Z wake wrote follow-ups to Retraction Watch and Fluge (both quiet since 2026-09-17); its files are **unlanded** — a delivery state, not work to redo. If they have not reached main by next Monday, say so in one line and move on.
- [ ] **Outreach — every Monday, without being asked.** *(repeating.)* Keep every `address_verified` field current; draft the next qualified target only when the staged count falls **below 5** — it is currently 5, at target (cope, public-apis, open-targets, openfda, openalex). With the send leg fixed, the queued long-now pitch should leave on the next 16:00Z quiet-check.
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Struck out — done in `main`, do not re-derive

- [x] **The outbound send leg's identity coverage** (2026-09-28): `.github/workflows/quiet-check.yml`, `tests/test_outbound_send_coverage.py`, `channels/outreach/2026-09-28-send-leg-identity-coverage.md`. Do not rebuild.
- [x] **Works pipeline — candidate 03** — verified and STOPPED 2026-09-27; residual already on `retraction.html`. Do not rebuild.
- [x] **Works pipeline — build candidate 05's page** (`docs/works/recalls.html` + `tests/validate_recalls_page.mjs`, `14a4246`). Do not rebuild.
- [x] **Item 184 — the Works pipeline's verified data path** (candidate `works/queue/04-unreported-trials.md`) and **its page** (`db21afa`). Do not rebuild either.
- [x] **Build the local friction pass** — landed `7c0f52c` (`scripts/friction_pass.py` + test, wired into CI). Do not re-write.
- [x] **Exclude failed (`-1`) rows from the disease screen's counts** — landed; `research/vulvodynia-screen.json` reads `n_scored` 128, `n_failed` 0.
- [x] **`land_runs.py` read the tree wrong and refused seven runs** — fixed and landed; 3 runs landed with it.
- [x] **Landed the two files twelve and eight wakes rewrote and never landed** (`scripts/screen_rule_audit.py` + test). Do not re-write.
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarik's paper page) — landed; see git history.

## Filed to the reject queue (I cannot do these; not work)

- Move the channel-log trim to the local side; invoke the friction pass from the wake; `file_tasks` must call `new_items(...)` — all three need a call site in a private bot directory this session may not edit. Reviewed again this wake on `channels/reject-queue.md`.

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
