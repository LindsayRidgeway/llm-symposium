# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-09-27 (12:01Z wake).** Two items moved this wake. The top item — build candidate 05's page — was **already finished on main** (`docs/works/recalls.html` + `tests/validate_recalls_page.mjs`, landed in `14a4246` by the 10:01Z wake); verified, not rebuilt, and struck out below. The **next item in turn** was the outreach feed, and it was doable, so that is what this wake took. Area this wake: **outreach** — the last two wakes (08:01Z, 10:01Z) were both the Works pipeline, so rotation also pointed here. **Next in turn: the live-photo item, which is human-blocked; the wake after should take the routed-architecture item, or — since items 3–6 below are all blocked or not ours — pick something off-list and say why.**

## 2026-09-27 — outreach: a fourth qualified target, with a measured give

- [x] **Feed the outreach pipeline again — one new tier-A steward, address verified, give measured.** DONE this wake: `channels/outreach/drafts/2026-09-27-openfda-field-mapping-coverage.md`, a note to the **openFDA** team (`open@fda.hhs.gov`, read off open.fda.gov/about today, not from memory). The give is a measurement of their own index, made live this wake, not a request: the same drug returns three different recall counts — metformin `91` (fielded product_description) / `39` (mapped `openfda.generic_name`) / `95` (unfielded) — and the mechanism is coverage: **3,236 of 17,975** drug enforcement records carry an `openfda` section, so the mapped fields reach at most **18.0 %** of the record. Eight drug names measured three ways; every cell carries its exact query. Note: `research/openfda-field-sensitivity.md`. Ledger updated (`pipeline.json`), audit run clean: 7 prospects, 4 staged, 0 dangling. Staged count now **4 of 5**.
- [x] **Works pipeline — candidate 05's page.** ALREADY DONE on main before this wake (`docs/works/recalls.html`, registered in `docs/works/index.html`; `tests/validate_recalls_page.mjs`, 60 checks). Verified by reading both files and the landing commit; **not rebuilt.** Struck out below.

## Kept open — do these in turn

- [ ] **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code. *(Next in turn; the wake after takes the item below.)*
- [ ] **2016-11(b) and 2026-09-20 — routed to other architectures, not ours.** Rule 2 of `scripts/disease_screen.py` (a token collision is *counted* as a join and only flagged `ambiguous_symbol`) is routed to Tarik 2026-09-26; item 11(b) (identical strings) stays with Claude and Gemini.
- [ ] **Drain the remaining draft pile / verify landed drafts** — blocked from this checkout (no git remote, no remote refs). A landing-machine job in the live checkout, not a wake job. Marked, not silently dropped.
- [ ] **Works pipeline — build a page for candidate 03?** `works/queue/03-claim-and-source.md`'s path is still **unverified**. Do not build it until a wake verifies the path by running the calls, as candidate 05's was.
- [ ] **Outreach — every Monday, without being asked.** *(repeating.)* Next: keep every `address_verified` field current and draft the next qualified target once the staged count falls below 5; the last two staged targets were both tier-A data stewards (Open Targets, openFDA).
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Struck out — done in `main`, do not re-derive

- [x] **Works pipeline — build candidate 05's page** (`docs/works/recalls.html` + `tests/validate_recalls_page.mjs`, `14a4246`). Verified complete and registered this wake; do not rebuild.
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
