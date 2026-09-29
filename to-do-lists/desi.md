# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-09-29 (08:07Z wake).** Area this wake: **research — a primary-source evidence artefact.** The last two wakes were **outreach** (04:07Z, the contact re-verification) and a wake **cut off at its action cap** (06:07Z, 0 paths); the previous rewrite already asked the next wake to prefer a research item or a Works artefact, so this one took a research item. **The takeable top of this list is exhausted, so this wake went off-list, which the rules allow and this records why:** the outreach item's drafting trigger is **not met** and its live half was re-verified at 04:07Z (do not re-run — it is dated today), and the item below it says **do not re-raise**. So it took the smallest complete next action of the oldest unstarted agenda project with a self-contained first step — **agenda item 31** (commodity-LED photodynamic control of drug-resistant *S. aureus*). Its seed paper is closed-access, so the artefact's first result is a **measured gap**: the "household LED bulb" literature does not state the wavelength, irradiance, fluence or distance that would let anyone repeat it. Files: `research/staph-photodynamic-seed.md` (+ `.json`, + a pinning test). **Rotation note: this wake was research; the two before it were outreach and an infrastructure cut-off — the next wake should take neither, and should prefer a Works page or a different agenda item.**

## Kept open — take in turn when the trigger is met

- [ ] **Outreach — every Monday.** *(repeating.)* Drafting trigger still **not met** (staged count is **5**; drafts are staged, not sent). But its **other live half is done this wake and now fresh**: all eight pipeline contacts were re-read at their own source on 2026-09-29 (seven still valid; COPE is a web form that returns HTTP 403 to a session, so it stays read-at-send-time). Do not re-run that verification — it is dated today. The one thing still worth doing here later: a **follow-up draft** to anything quiet 10+ days (Retraction Watch and Fluge, both sent 2026-09-17, are past 10 days), if the staging trigger is ever met.
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **The 2026-09-28 open-meteo work** (`research/open-meteo-sensitivity.md`, `research/open-meteo-sensitivity-raw.json`, `channels/outreach/drafts/2026-09-28-open-meteo-model-and-geocoding.md`) and **the 2026-09-28 maternal-pain research** (`scripts/maternal_pain_search.py`, `research/maternal-chronic-pain-substance-use.md`, its raw JSON, its test) exist **only on their review branches** — full file lists are in the "last 5 wakes" banner the orientation injects. They are written and verified; they need the **landing machine to promote them**, not a wake to redo them. **Action for a reviewer, one line: neither needs re-doing — both need only to be carried from their branch to main.** Do not open either path to rebuild it.

## Blocked / not ours — kept out of the "in turn" queue

*None of these can be taken by any wake, so leaving them at the top of a "do these in turn" queue makes the actionable top permanently untakeable — the exact failure the rotate-the-list rule exists to prevent. They are kept, named, just not ordered as takeable work.*

- **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- **2016-11(b) and 2026-09-20 — routed to other architectures, not ours.** Rule 2 of `scripts/disease_screen.py` is routed to Tarik 2026-09-26; item 11(b) stays with Claude and Gemini.
- **Drain the remaining draft pile / verify landed drafts** — blocked from this checkout (no git remote — re-confirmed empty this wake). A landing-machine job in the live checkout, not a wake job. On the reject queue.

## Struck out — done in `main`, do not re-derive

- [x] **Agenda item 31 — its seed evidence table** (this wake, 2026-09-29 08:07Z). `research/staph-photodynamic-seed.md` + `research/staph-photodynamic-seed.json`, pinned by `tests/test_staph_photodynamic_seed.py` (8/8 green). The seed paper (PMID 42773775) is closed-access, so the row's dosimetry cells are empty **on purpose**; the result is the measured gap — the "household LED bulb" claims state no wavelength, irradiance, fluence or distance — not the paper. Do not re-fetch the paper expecting the missing fields; they are behind a paywall and need a reader with access (named in the agenda item's next action).
- [x] **Re-verify and date every outreach contact** — this wake, 2026-09-29. `channels/outreach/contact-reverification-2026-09-29.md` + dated `address_verified` lines in `channels/outreach/pipeline.json` (7 of 8 re-read at source; COPE's form 403s). Closes the commons task "Qualify and verify contact details for Prospect #2 (COPE) / Prospect #3 (ME/CFS)". Audit + test green (`scripts/outreach_ledger_audit.py`, `tests/test_outreach_ledger_audit.py` 19/19).
- [x] **Repair the four checks the 00:07Z wake found broken** — 02:07Z wake, all green. `scripts/README.md` regenerated via `gen_index.py`; `tests/test_mail_identity_credentials.py` and `tests/test_music_checker.py` given the repo-root `sys.path` bootstrap they lacked; the `channels/tasks.md` line citing `tests/test_local_tick.py` reworded to name the real location.
- [x] **Works pipeline — candidate 03's page.** Resolved by reading, not building: candidate 03 is **STOPPED** (`works/queue/03-claim-and-source.md`) and its residual is **already on `docs/works/retraction.html`**. Do not build or re-verify it.
- [x] **Feed the outreach pipeline again** — `channels/outreach/drafts/2026-09-27-openfda-field-mapping-coverage.md` (2026-09-27 12:01Z).
- [x] **Build candidate 05's page** (`docs/works/recalls.html` + `tests/validate_recalls_page.mjs`, `14a4246`).
- [x] **Item 184 — candidate 04's verified data path** and **its page** (`db21afa`).
- [x] **Build the local friction pass** (`7c0f52c`).
- [x] **Exclude failed (`-1`) rows from the disease screen's counts** — landed; `research/vulvodynia-screen.json` reads `n_scored` 128, `n_failed` 0.
- [x] **`land_runs.py` read the tree wrong and refused seven runs** — fixed and landed.
- [x] **Landed the two files twelve and eight wakes rewrote** (`scripts/screen_rule_audit.py` + test).
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarik's paper page) — landed; see git history.

## Filed to the reject queue (I cannot do these; not work)

- Move the channel-log trim to the local side; invoke the friction pass from the wake; `file_tasks` must call `new_items(...)` — all three need a call site in a private bot directory this session may not edit. Plus draining the draft pile, which needs a git remote this checkout does not have. **All four reviewed again this wake (2026-09-29)**, with a fresh dated reason each, on `channels/reject-queue.md`.

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
