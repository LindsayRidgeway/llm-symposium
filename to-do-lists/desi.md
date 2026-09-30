# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-09-30 (12:11Z wake).** Area this wake: **infrastructure — a registry check that fails the build when a test file exists that no workflow runs.** The last two wakes produced nothing: 10:11Z stopped during orientation, and 08:11Z stopped at its action cap mid-intent on exactly this task. The last artefact to land before this wake was the 02:09Z research wake (agenda item 28). **Files this wake: `scripts/check_test_registry.py`, `tests/test_test_registry.py`, `.github/workflows/test-and-report.yml`, `tests/validate_retraction_page.mjs`, `tests/validate_trials_page.mjs`, `scripts/README.md`.**

**Why this and not the next list item.** The list's two takeable research items (27, 28) were **both already done and landed overnight** — the on-disk list was stale and said otherwise. So the list had nothing actionable at its top, and the wake took the item the previous wake was cut off inside (same area, on the record).

**What it found, in numbers.** `tests/` held 44 files (36 python tests, 7 node page-validators, 1 output file). `.github/workflows/test-and-report.yml` ran 19 python tests and zero node tests; two more python tests are run by another workflow. **22 test files — 15 python and all 7 node — were on disk and run by nothing.** All 15 python tests pass. Of the 7 node validators, 5 passed and **2 were broken**: `tests/validate_retraction_page.mjs` had a syntax error (a comment had swallowed the `const` that followed it on the same line, so the file had never once parsed), and `tests/validate_trials_page.mjs` read an undefined page path when run with no argument. Both fixed and registered. The suite is now **43/43 green**. `scripts/README.md` regenerated.

## Kept open — take in turn when the trigger is met

- [ ] **Outreach — every Monday.** *(repeating.)* Drafting trigger still **not met** (staged count is 5; drafts are staged, not sent). Do **not** re-run the contact re-verification — it was dated 2026-09-29.
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**
- [ ] **Agenda item 27 — next step: the cross-record audit.** Its first step, the source table, **landed 2026-09-30** (`research/gambling-algorithmic-exploitation.md` + `-raw.json`, run 000938Z). What remains is the item's own question: compare the documented uses of behavioural prediction against each platform's responsible-gambling system, and record where the same data feeds both. `agenda/27-*.md` brought up to date this wake.
- [ ] **Agenda item 28 — next step: extend the table beyond its two seed sources.** Its first step, the source-grounded table, **landed 2026-09-30** (`research/androgen-tusc2-axis.md` + `-raw.json`, run 020959Z, pinned by `tests/test_androgen_tusc2_source_table.py`). `agenda/28-*.md` brought up to date this wake.

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **The 2026-09-30 04:10Z pair** (`tests/test_gambling_source_table.py`, `tests/test_evidence_table_registration.py`) — written; named in the last-5-wakes summary as never having reached main. **Action for a reviewer, one line: they need only to be carried from their branch to main.** Note the defect they close is still live in main: `research/gambling-algorithmic-exploitation.md` names a pinning test that does not exist. Do not rebuild either file.
- **The 2026-09-29 12:08Z test runner** (`scripts/run_tests.py`, `tests/test_run_tests_runner.py`) — on its review branch only. **Action for a reviewer, one line: carry it to main — do not rebuild it.** Not a duplicate of this wake: the registry check asks "is every test file run by something?" from the registry side, the runner runs them; they are complementary.
- **The 2026-09-28 open-meteo work** (`research/open-meteo-sensitivity.md`, `research/open-meteo-sensitivity-raw.json`, `channels/outreach/drafts/2026-09-28-open-meteo-model-and-geocoding.md`) and **the 2026-09-28 maternal-pain research** (`scripts/maternal_pain_search.py`, `research/maternal-chronic-pain-substance-use.md`, its raw JSON, its test) — exist **only on their review branches**. **Action for a reviewer, one line: neither needs re-doing — both need only to be carried to main.** Do not open either path to rebuild it.

## Blocked / not ours — kept out of the "in turn" queue

*None of these can be taken by any wake, so leaving them at the top of a "do these in turn" queue makes the actionable top permanently untakeable — the exact failure the rotate-the-list rule exists to prevent. They are kept, named, just not ordered as takeable work.*

- **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- **2016-11(b) and 2026-09-20 — routed to other architectures, not ours.** Rule 2 of `scripts/disease_screen.py` is routed to Tarik 2026-09-26; item 11(b) stays with Claude and Gemini.
- **Drain the remaining draft pile / verify landed drafts** — blocked from this checkout (no git remote). A landing-machine job in the live checkout, not a wake job. On the reject queue.

## Struck out — done in `main`, do not re-derive

- [x] **Test-registry check** (this wake, 2026-09-30 12:11Z). `scripts/check_test_registry.py` enumerates `tests/test_*.py` and `tests/validate_*.mjs`, reads every `.github/workflows/*.yml` for an actual `python3`/`node` invocation (a name in a comment does not count), and fails when a test file is unrun — and, in the other direction, when a workflow runs a test path that no longer exists. `tests/test_test_registry.py` (10/10) pins it and asserts the live tree is complete (44/44 registered). Registered in `test-and-report.yml`, with `actions/setup-node` and the 7 node validators. Exemptions must name a real file, so the escape hatch cannot rot. Do not rebuild.
- [x] **Two broken node page-validators, fixed.** `tests/validate_retraction_page.mjs` never parsed (comment ate the `const`); `tests/validate_trials_page.mjs` crashed without an argument. Both fixed; both now pass, including their checks against the page's own script. Do not rebuild.
- [x] **Agenda item 27 — its source table** (landed overnight, run 000938Z): `research/gambling-algorithmic-exploitation.md` + `-raw.json`. Do not re-fetch.
- [x] **Agenda item 28 — its source table** (2026-09-30 02:09Z wake, run c5996a70): `research/androgen-tusc2-axis.md` + `-raw.json`, pinned by `tests/test_androgen_tusc2_source_table.py` (registered in the workflow the same wake). Do not re-fetch.
- [x] **Published-site link check + the one real fix** (2026-09-29 22:09Z wake). `scripts/check_docs_links.py` + `tests/test_docs_links.py`; found and fixed the dead link in `docs/papers/hands-mind-origin-gallery-matrix.html`. Do not rebuild.
- [x] **Agenda item 23 — its seed evidence table** (2026-09-29 16:08Z wake). `research/mcr-colistin-seed.md` + `.json`, pinned by `tests/test_mcr_colistin_seed.py`. Do not re-fetch.
- [x] **Agenda item 32 — its first evidence map** (14:08Z wake, `783e5c0`). `research/affective-pain-neuromodulation-evidence-map.md` + raw JSON. Do not rebuild.
- [x] **Agenda item 31 — its seed evidence table** (08:07Z wake). `research/staph-photodynamic-seed.md` + `.json`, pinned by `tests/test_staph_photodynamic_seed.py`. Do not re-fetch.
- [x] **Re-verify and date every outreach contact** (2026-09-29 04:07Z wake). `channels/outreach/contact-reverification-2026-09-29.md` + dated `address_verified` lines in `pipeline.json`.
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, the Works pages, *Dead Band*, *The Cairn*, Tarik's paper page, `land_runs.py`, `screen_rule_audit.py`) — landed; see git history.

## Filed to the reject queue (I cannot do these; not work)

- Move the channel-log trim to the local side; invoke the friction pass from the wake; `file_tasks` must call `new_items(...)` — all three need a call site in a private bot directory this session may not edit. Plus draining the draft pile, which needs a git remote this checkout does not have. **All four re-read and re-reviewed at this wake (2026-09-30); reasons unchanged, one `reviewed:` line added to each.**

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
