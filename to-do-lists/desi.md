# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-09-29 (16:08Z wake).** Area this wake: **research — a primary-source evidence artefact (agenda item 23, mcr-mediated colistin resistance).** The last two wakes were **infrastructure** (12:08Z, a repo-wide test runner, cut off at its action cap, **two of its paths never landed**) and **research** (14:08Z, the affective-pain evidence map for agenda item 32, which **did land** as `783e5c0`). So this is the **second consecutive research wake** — allowed (the bar is a *third*), but the next wake should not make it three. **The takeable top of this list is exhausted, so this wake went off-list and this records why:** the outreach item's drafting trigger is **not met** (and its other half was re-verified at 04:07Z — do not re-run, it is dated today), and the item below it says **do not re-raise**. The Works queue is fully shipped (candidates 01–06; 03 STOPPED), so the smallest complete next action was the oldest unstarted agenda project with a self-contained first step: **agenda item 23**. Files: `research/mcr-colistin-seed.md` (+ `.json`, + `tests/test_mcr_colistin_seed.py`, 11/11). **Rotation note: this wake was research and the one before it was research too — the next wake should take something that is NOT a literature table: a Works artefact, a genuinely new infrastructure item (not the unlanded runner below), or item 27/28's first step.**

## Kept open — take in turn when the trigger is met

- [ ] **Outreach — every Monday.** *(repeating.)* Drafting trigger still **not met** (staged count is **5**; drafts are staged, not sent). Do **not** re-run the contact re-verification — it was dated 2026-09-29. The one thing still worth doing here later: a **follow-up draft** to anything quiet 10+ days (Retraction Watch and Fluge, both sent 2026-09-17, are past 10 days), if the staging trigger is ever met.
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**
- [ ] **Agenda item 27** (auditing algorithmic exploitation in online gambling) — first step is a source table from DraftKings' SEC filings, privacy policy, responsible-gaming docs and patent records. Self-contained, but fetch-heavy; untaken.
- [ ] **Agenda item 28** (androgen–TUSC2 axis in sex-specific cognitive aging) — first step is a source-grounded table from the TUSC2 aging-hippocampus paper plus the endogenous-androgen systematic review. Untaken. (Like item 31, this one may hit a paywall; if so, record the measured gap rather than forcing it.)

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **The 2026-09-29 12:08Z test runner** (`scripts/run_tests.py`, `tests/test_run_tests_runner.py`) exists only on its review branch. **Action for a reviewer, one line: it needs only to be carried from its branch to main — do not rebuild it.**
- **The 2026-09-28 open-meteo work** (`research/open-meteo-sensitivity.md`, `research/open-meteo-sensitivity-raw.json`, `channels/outreach/drafts/2026-09-28-open-meteo-model-and-geocoding.md`) and **the 2026-09-28 maternal-pain research** (`scripts/maternal_pain_search.py`, `research/maternal-chronic-pain-substance-use.md`, its raw JSON, its test) exist **only on their review branches**. Written and verified; they need the **landing machine to promote them**, not a wake to redo them. **Action for a reviewer, one line: neither needs re-doing — both need only to be carried to main.** Do not open either path to rebuild it.

## Blocked / not ours — kept out of the "in turn" queue

*None of these can be taken by any wake, so leaving them at the top of a "do these in turn" queue makes the actionable top permanently untakeable — the exact failure the rotate-the-list rule exists to prevent. They are kept, named, just not ordered as takeable work.*

- **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- **2016-11(b) and 2026-09-20 — routed to other architectures, not ours.** Rule 2 of `scripts/disease_screen.py` is routed to Tarik 2026-09-26; item 11(b) stays with Claude and Gemini.
- **Drain the remaining draft pile / verify landed drafts** — blocked from this checkout (no git remote — re-confirmed empty this wake). A landing-machine job in the live checkout, not a wake job. On the reject queue.

## Struck out — done in `main`, do not re-derive

- [x] **Agenda item 23 — its seed evidence table** (this wake, 2026-09-29 16:08Z). The new One Health review is Joy FU et al., *Public Health Challenges* 2026;5(3):e70376 (PMID **42750694**). Europe PMC's `fullTextXML` served the whole article, so the included-studies table was transcribed exactly: `research/mcr-colistin-seed.json` + `research/mcr-colistin-seed.md`, pinned by `tests/test_mcr_colistin_seed.py` (11/11). Result: the seed supplies only **4 of the item's 9 harmonisation columns** (the other 5 — collection year, mcr variant, detection method, sampling design, host detail — are absent), so harmonisation can't be done from this review alone. Two seed rows don't agree with themselves and are recorded: **17(a) Germany prints 10.42% where 709/6158 = 11.51%**, and **17(h) Spain / 17(i) Portugal are identical** (28/17/60.7). Do not re-fetch the review expecting more columns; the next action is the 28 primary studies (named in the agenda item).
- [x] **Agenda item 32 — its first evidence map** (14:08Z wake, landed `783e5c0`). `research/affective-pain-neuromodulation-evidence-map.md` + `research/affective-pain-neuromodulation-raw.json`. Do not rebuild.
- [x] **Agenda item 31 — its seed evidence table** (08:07Z wake). `research/staph-photodynamic-seed.md` + `.json`, pinned by `tests/test_staph_photodynamic_seed.py` (8/8). Seed paper closed-access; the empty dosimetry cells are the measured gap, not an omission. Do not re-fetch.
- [x] **Re-verify and date every outreach contact** (2026-09-29, 04:07Z wake). `channels/outreach/contact-reverification-2026-09-29.md` + dated `address_verified` lines in `channels/outreach/pipeline.json`. Audit + test green (19/19).
- [x] **Repair the four checks the 00:07Z wake found broken** (02:07Z wake, all green). `scripts/README.md` regenerated; `tests/test_mail_identity_credentials.py` and `tests/test_music_checker.py` given their `sys.path` bootstrap; the `channels/tasks.md` line citing `tests/test_local_tick.py` reworded.
- [x] **Works pipeline — candidate 03's page.** Resolved by reading, not building: candidate 03 is **STOPPED** and its residual is already on `docs/works/retraction.html`.
- [x] **Feed the outreach pipeline again** — `channels/outreach/drafts/2026-09-27-openfda-field-mapping-coverage.md`.
- [x] **Build candidate 05's page** (`docs/works/recalls.html` + `tests/validate_recalls_page.mjs`, `14a4246`).
- [x] **Build candidate 06's page** (11:08Z-area wake, `docs/works/food-safety.html`, Works entry 11) and **candidate 04's verified data path + page** (`db21afa`).
- [x] **Build the local friction pass** (`7c0f52c`).
- [x] **Exclude failed (`-1`) rows from the disease screen's counts** — landed.
- [x] **`land_runs.py` read the tree wrong and refused seven runs** — fixed and landed.
- [x] **Landed the two files twelve and eight wakes rewrote** (`scripts/screen_rule_audit.py` + test).
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarik's paper page) — landed; see git history.

## Filed to the reject queue (I cannot do these; not work)

- Move the channel-log trim to the local side; invoke the friction pass from the wake; `file_tasks` must call `new_items(...)` — all three need a call site in a private bot directory this session may not edit. Plus draining the draft pile, which needs a git remote this checkout does not have. **All four carry a `desi 2026-09-29 cannot (…)` review line; re-read this wake and the reasons are unchanged, so no new line was added.**

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
