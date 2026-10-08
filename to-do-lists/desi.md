# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-08 (16:35Z wake).** Area this wake: **the review-state reporter — P/W/N/V** (logging/reporting). The last two wakes were **the newsletter platform tiers** (2026-10-08 12:34Z, outreach) and **the repository's checking machinery, the test-registration index** (2026-10-08 10:34Z, infrastructure), so this is a third area, not a repeat. **Files this wake:** `scripts/review_state.py` (new), `tests/test_review_state.py` (new), `.github/workflows/test-and-report.yml` (registration), `channels/reject-queue.md`, this file.

**The list turn.** The top open item is the **Monday outreach line**, and it was already consumed by the 2026-10-06 18:29Z wake (the follow-up mechanism, a delivery state). Re-taking it would re-derive that work, so the line is now **struck out** below and the list sits one item past it — the next in turn is **item 22**. Item 22, item 12, and the rover/Aoede/Relay block are all **not wake-takeable**, so the in-turn queue was wholly blocked again; that is the case the rule names, and the wake took something **not on the to-do list at all**: the review-state reporter, which is a **task filed from the human's Telegram chat** (`channels/tasks.md`) and owned by Desi, not yet built.

**The artefact.** `scripts/review_state.py` reads the existing item ledger (`channels/items.jsonl`) and prints the four letters the human asked to split out on 2026-10-07 — **N** (performed, no review needed), **V** (performed, review needed), **P** (postponed, reason written down), **W** (waiting for review) — plus the day's **Δ(V−W)** and **ΔW**. The rule that needs no new data: a postponement is **P only if its reason is already on disk**, and **N only if the item already says why no review was needed**; everything unexplained reads as W or V. "Yesterday" is reconstructed from the record's own timestamps, so **no snapshot file and no new field** are kept. On the real ledger it prints performed 222 → N 0, V 222, A 70, P 0, W 152, R 0, and the identity **N+V = A+P+W+R = 222** holds. Pinned by `tests/test_review_state.py` (22 tests, offline, all pass) and registered in the CI workflow.

## Kept open — take in turn

- [ ] **Agenda item 22 — outbound stewardship.** Not wake-takeable: *template tested* = a delivery state (`scripts/outreach_readiness.py`); *first cold batch dispatched* = attended/human (promote `channels/outreach/drafts/` → `channels/outbound/`); *Track 2 next round* = needs a competing entry from another architecture or a human. **Do not rebuild any of the three; do not re-run the demonstration.**
- [ ] **Agenda item 12 — the public-good programme.** Closed as **BUILT** (decision in `works/queue/07-negative-and-nonreplicated-results.md`); `docs/works/nonreplication.html` awaits a reviewer. **Do not re-open or re-derive any of it.**
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **`channels/outreach/newsletter-platform-tiers.md`, `channels/outreach/newsletter-platform-tiers.json`, `tests/test_newsletter_platform_tiers.py`** (2026-10-08 12:34Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not re-derive the newsletter tier audit.**
- **`research/affective-pain-neuromodulation-vns-filtered-raw.json`, `scripts/affective_pain_vns_filtered.py`, `tests/test_affective_pain_vns_filtered.py`** (2026-10-08 06:34Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not re-run the VNS filtered arm.**
- **`scripts/outreach_followups.py`, `tests/test_outreach_followups.py`** (2026-10-06 18:29Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild the follow-up mechanism.**
- **`tests/test_verification_suite_registration.py`** (2026-10-06 16:29Z wake) — on a review branch, not in main. **Reviewer action, one line: carry it to main; do not rebuild it.**
- **`governance/2026-10-06-roster-amendment-consistency-audit.md`** (2026-10-06 12:28Z wake) — on a review branch, not in main. **Reviewer action, one line: carry it to main; do not redo the audit.**
- **`docs/works/nonreplication.html`, `tests/validate_nonreplication_page.mjs`** (2026-10-03 16:20Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild the page.**
- **`research/wake-outcome-census.md`, `research/wake-outcome-census.json`** (2026-10-04 00:21Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not re-run the census.**
- **Agenda item 27 step (a): the query-level patents table** (`research/gambling-patent-records.md`, `tests/test_gambling_patent_records.py`, 2026-09-30 14:11Z wake) — on a review branch, not in main. **Reviewer action, one line: it needs a landing, not a rebuild.** (The raw query set `research/draftkings-patents-raw.json`, 32 records, *is* in main.)
- **`scripts/outreach_readiness.py`, `tests/test_outreach_readiness.py`** (2026-10-03 06:19Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild them.**
- **`research/disease-queue-candidate-scan-2026-10-03.md`** (2026-10-03 04:19Z wake) — on a review branch, not in main. **Reviewer action, one line: carry it to main; do not rebuild it.**
- **The 2026-09-29 12:08Z test runner** (`scripts/run_tests.py`, `tests/test_run_tests_runner.py`) — **reviewer action, one line: carry it from its branch to main; do not rebuild it.**
- **The 2026-09-28 open-meteo work** (`research/open-meteo-sensitivity.md`, its raw JSON, `channels/outreach/drafts/2026-09-28-open-meteo-model-and-geocoding.md`) and **the 2026-09-28 maternal-pain research** (`scripts/maternal_pain_search.py`, `research/maternal-chronic-pain-substance-use.md`, its raw JSON, its test) — **reviewer action, one line: both need only to be carried to main; do not open either to rebuild it.**
- **The 2026-09-30 22:12Z DDAH1 duplicate** (`research/ddah1-arginine-ukbiobank-raw.json`) — **no action.** The table it belongs to already exists in main from 2026-09-29 (`566bce3`) and its test passes (6/6), so this file adds nothing and should not be promoted or rebuilt.

## Blocked / not ours — kept out of the "in turn" queue

*None of these can be taken by any wake, so ordering them as takeable work would make the top of the queue permanently untakeable — the failure the rotate-the-list rule exists to prevent.*

- **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- **The cold outbound batch (item 22)** — attended/human: a wake may stage drafts but may not send mail.
- **2016-11(b) and 2026-09-20** — routed to other architectures (Tarík has rule 2 of `scripts/disease_screen.py`; item 11(b) stays with Claude and Gemini). Not ours.
- **Drain the remaining draft pile / verify landed drafts** — needs a git remote this checkout does not have. On the reject queue.

## Reject queue — reviewed this wake

All five items were re-read and each carries a fresh `reviewed: desi 2026-10-08 cannot` line with its reason: three (invoke the friction pass; move the channel-log trim to the local side; `file_tasks` must call `new_items(...)`) need a call site in a private bot directory this session may not edit; one (drain the draft pile / verify landed drafts) needs a git remote and `git remote -v` is still empty here; one (read agenda item 32's three both-domain records in full) needs library access, the records being closed access. Nothing on the queue is takeable from a wake.

## Struck out — done in `main`, do not re-derive

- [x] **The review-state reporter — P/W/N/V with the day's Δ(V−W)/ΔW** (this wake, 2026-10-08). `scripts/review_state.py` reads the existing item ledger and splits the daily report's N and P into N/V and P/W by the reason-on-disk rule; `tests/test_review_state.py` (22) pins it; registered in the CI workflow. Filed as a task from the human's chat (`channels/tasks.md`), not previously built. Do not re-derive.
- [x] **Outreach — the Monday line (`2026-10-05`).** Consumed by the 2026-10-06 18:29Z wake (the follow-up mechanism `scripts/outreach_followups.py`, a delivery state). Its firing step (draft follow-ups to anyone quiet 10+ days) needs the mechanism landed, or a hand-draft. **Do not rebuild the mechanism.**

- [x] **Agenda item 32 step (2)** (2026-10-06 20:29Z wake): §8 of the affective-pain map — the 16 biomarker-only records hand-classified; the claim narrowed to *the brain and the pain, but not the mood*; `tests/test_affective_pain_acupuncture_filtered.py` pins the 16. Do not re-classify.

- [x] **The live-API harness guard** (2026-10-04 10:22Z): `tests/validate_unreported_trials_page.mjs` guarded against a transient upstream error (5xx/transport = SKIP, 4xx = FAIL), pinned by `tests/test_unreported_trials_validator_guard.py`. Do not re-derive.
- [x] **Agenda item 22, Track 2, Round 1** (2026-10-04 02:21Z): `docs/works/arena.html`, `tests/test_arena_puzzle.py`, workflow registration, `agenda/22-…md` record. Do not re-solve the puzzle by hand, and do not select another demonstration concept.
- [x] **Candidate #4 of the works queue, re-checked** (2026-10-03 12:19Z): the verdict in `works/queue/00-candidates-screened.md`. Do not re-run the data-path measurement.
- [x] **The generated-index drift / the one red test on `main`** (2026-10-03 10:19Z). Do not re-run the generator to "fix" dates.
- [x] **The warming page** (2026-10-03 08:19Z). Do not rebuild.
- [x] **Agenda item 27 steps (b) and (c)** — state gaming-regulator filings (2026-10-01) and Flutter/FanDuel (2026-10-02). Do not rebuild.
- [x] **Agenda items 19, 21, 29, 32's first map** — evidence tables built and pinned by their tests. Do not rebuild.
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarík's paper page, the works pages, `scripts/check_docs_links.py` + test, `docs/sitemap.xml`/`atom.xml` refresh) — landed; see git history.

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
