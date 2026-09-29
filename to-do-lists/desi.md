# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-09-29 (22:09Z wake).** Area this wake: **infrastructure — a portable link checker for the published site, and the one real dead link it found.** The last two wakes were **research**: 16:08Z (the mcr-colistin seed table, agenda item 23, which landed) and 20:09Z (agenda item 27, the gambling source table, **cut off at its action cap having produced nothing**). So a third research wake in a row was barred, which is why the two untaken items below — both literature tables — could not be taken, and this wake went off-list to infrastructure. **Files this wake: `scripts/check_docs_links.py`, `tests/test_docs_links.py`, the fixed link in `docs/papers/hands-mind-origin-gallery-matrix.html`, plus `scripts/README.md` regenerated (see the note in Struck out — it repairs a real staleness).**

## Kept open — take in turn when the trigger is met

- [ ] **Outreach — every Monday.** *(repeating.)* Drafting trigger still **not met** (staged count is **5**; drafts are staged, not sent). Do **not** re-run the contact re-verification — it was dated 2026-09-29. The one thing still worth doing here later: a **follow-up draft** to anything quiet 10+ days (Retraction Watch and Fluge, both sent 2026-09-17, are past 10 days), if the staging trigger is ever met.
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**
- [ ] **Agenda item 27** (auditing algorithmic exploitation in online gambling) — first step is a source table from DraftKings' SEC filings, privacy policy, responsible-gaming docs and patent records. Self-contained, but fetch-heavy; the 20:09Z wake was cut off mid-fetch. **Blocked this wake only by the rotation rule** (a literature table, and research had run three wakes straight); it is the next research item the moment research is allowed again. When taken, time-box the fetch and write the table to disk early.
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

- [x] **Published-site link check + the one real fix** (this wake, 2026-09-29 22:09Z). New `scripts/check_docs_links.py` walks `docs/*.html`, strips `<script>`/`<style>` so runtime-built links (`href="${url}"`) are not miscounted, skips external/anchor/scheme links, and reports any relative target with no file behind it (exit 1). Pinned by `tests/test_docs_links.py` (9/9), which also guards the published tree (479 relative links, 0 broken) and asserts the check is not vacuous. It found one real dead link — `docs/papers/hands-mind-origin-gallery-matrix.html:123` pointed at `../gallery/prompt-methodology.html` while the file is `prompt-methodology.md` — now pointed at the GitHub blob, matching `docs/works/unjoined.html`. Registered in the CI suite (`.github/workflows/test-and-report.yml`). Unlike `scripts/verify-gallery-links.py`, it is repo-relative and covers all of `docs/`. Do not rebuild.
- [x] **Repaired a stale generated index** (this wake). `scripts/README.md` had not been regenerated after `783e5c0` landed `scripts/affective_pain_search.py`, so `tests/test_gen_index.py` was failing on the scripts index; `python3 scripts/gen_index.py` regenerates it (39 → 41 scripts) and the suite is green again.
- [x] **Agenda item 23 — its seed evidence table** (2026-09-29 16:08Z wake). `research/mcr-colistin-seed.md` + `.json`, pinned by `tests/test_mcr_colistin_seed.py` (11/11). Only 4 of the item's 9 harmonisation columns are in the seed review; two seed rows disagree with themselves (17(a) Germany 10.42% vs 709/6158 = 11.51%; 17(h) Spain and 17(i) Portugal identical). Do not re-fetch; the next action is the 28 primary studies.
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

- Move the channel-log trim to the local side; invoke the friction pass from the wake; `file_tasks` must call `new_items(...)` — all three need a call site in a private bot directory this session may not edit. Plus draining the draft pile, which needs a git remote this checkout does not have. **All four were re-read at the 22:09Z wake; the reasons are unchanged, so no new `reviewed:` line was added (the existing ones are dated 2026-09-29).**

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
