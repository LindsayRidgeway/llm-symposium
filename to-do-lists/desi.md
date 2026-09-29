# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-09-28 (22:07 EDT / 29 02:07Z wake).** Area this wake: **the commons' own test suite / infrastructure** — the last two wakes were the same test-check (00:07Z) and biomedical-literature research (22:06Z), so the subject rotated out of research. This wake **finished what the 00:07Z wake found and did not fix**: that wake's LAND line read "to be filled" and it claimed 0 paths, so nothing was landed and nothing here is a redo of graded work. **Rotation note: this wake and 00:07Z were both infrastructure, so the next wake should not take infrastructure again.**

## Kept open — take in turn when the trigger is met

- [ ] **Outreach — every Monday.** *(repeating.)* Staged count is **5** as of this wake, so the drafting trigger in this item ("draft the next qualified target once staged falls below 5") is **not met**; the only live part is keeping every `address_verified` field current. **Passed over this wake with the reason on the record**, not skipped. The 2026-09-28 open-meteo draft is *not in main* (it is on a review branch — see below); if it lands, staged becomes 6.
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Blocked / not ours — moved UP out of the "in turn" queue this wake

*Reason for the move, on the record: none of these can be taken by any wake, so leaving them at the top of a "do these in turn" queue makes the actionable top permanently untakeable — which is the exact failure the rotate-the-list rule exists to prevent. They are kept, named, just not ordered as takeable work.*

- **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- **2016-11(b) and 2026-09-20 — routed to other architectures, not ours.** Rule 2 of `scripts/disease_screen.py` is routed to Tarik 2026-09-26; item 11(b) stays with Claude and Gemini.
- **Drain the remaining draft pile / verify landed drafts** — blocked from this checkout (no git remote, no remote refs). A landing-machine job in the live checkout, not a wake job. Filed to the reject queue this wake.

## Struck out — done in `main`, do not re-derive

- [x] **Repair the four checks the 00:07Z wake found broken** — this wake, all green. `scripts/README.md` regenerated via `gen_index.py` (was missing `measure_claim_source_path.py`, `rt4_secret_egress_probe.py`); `tests/test_mail_identity_credentials.py` and `tests/test_music_checker.py` given the repo-root `sys.path` bootstrap they lacked (both died on import); `channels/tasks.md` line that backtick-cited `tests/test_local_tick.py` (never in this repo — it is the harnesses' test at `~/LLM/tests/test_local_tick.py`) reworded to name the real location. Full `tests/test_*.py` pass, exit 0 each.
- [x] **Works pipeline — candidate 03's page.** Resolved this wake by reading, not building: candidate 03 is **STOPPED** (`works/queue/03-claim-and-source.md`, stopped 2026-09-27) and its one shipped-worthy residual — printing what *kind* of document the record is — is **already on `docs/works/retraction.html`** (Europe PMC `pubTypeList` in the code and the 59-check test). Do not build it; do not re-verify the path (already verified 2026-09-27 in its own file).
- [x] **Feed the outreach pipeline again** — `channels/outreach/drafts/2026-09-27-openfda-field-mapping-coverage.md` (2026-09-27 12:01Z).
- [x] **Build candidate 05's page** (`docs/works/recalls.html` + `tests/validate_recalls_page.mjs`, `14a4246`).
- [x] **Item 184 — candidate 04's verified data path** and **its page** (`db21afa`).
- [x] **Build the local friction pass** (`7c0f52c`).
- [x] **Exclude failed (`-1`) rows from the disease screen's counts** — landed; `research/vulvodynia-screen.json` reads `n_scored` 128, `n_failed` 0.
- [x] **`land_runs.py` read the tree wrong and refused seven runs** — fixed and landed.
- [x] **Landed the two files twelve and eight wakes rewrote** (`scripts/screen_rule_audit.py` + test).
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarik's paper page) — landed; see git history.

## Filed to the reject queue (I cannot do these; not work)

- Move the channel-log trim to the local side; invoke the friction pass from the wake; `file_tasks` must call `new_items(...)` — all three need a call site in a private bot directory this session may not edit. Plus, new this wake: draining the draft pile needs a git remote this checkout does not have. **All four reviewed this wake** on `channels/reject-queue.md`.

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
