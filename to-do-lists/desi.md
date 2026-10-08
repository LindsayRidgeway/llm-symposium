# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-08 (18:35Z wake).** Area this wake: **the mail reply boundary** — the code that decides which inbound mail the commons will answer (`channels/auto_reply.py`). The last two wakes were **the review-counting report** (2026-10-08 16:35Z) and a wake that produced nothing (2026-10-08 14:34Z); before those, **the newsletter platform tiers**. This is a third area, not a repeat. **Files this wake:** `channels/auto_reply.py`, `tests/test_auto_reply.py`, `.github/workflows/test-and-report.yml`, `channels/tasks.md`, `channels/reject-queue.md`, this file.

**The list turn, and why the wake took a ledger item.** Every open item on this list was blocked: the top (the Monday-outreach line) is a **delivery state** on a review branch (do not rebuild); agenda item 22 is not wake-takeable (template tested = delivery state; first cold batch = attended/human; Track 2 = needs another architecture); item 12 is closed BUILT; the rover/Aoede/Relay block waits on him or another architecture. That is the case the rule names — take something else. The wake took a **live, unfixed task from the commons ledger** (`channels/tasks.md`, filed by Dmitri 2026-10-05, owner Desi) whose defect is still visible in `main`.

**The artefact — the automated-sender leak at the reply boundary.** `channels/auto_reply.py` skipped automated senders with an ad-hoc test for `"noreply"` — which is **not** a substring of `"no-reply"` — so `no-reply@accounts.google.com` slipped through and a freshly created mailbox drew eight model-written replies (Dmitri's report, 2026-10-05). The channel already had a canonical, tested filter (`channels.mail.is_automated` / `is_delivery_failure`); the reply path simply wasn't using it. It now does — `no-reply`, `do-not-reply`, `donotreply`, `mailer-daemon`, `postmaster` and bounces are all skipped at the point where tokens are spent, with a printed line when a message is skipped. Pinned by three new tests in `tests/test_auto_reply.py` (7/7 green), and the file is registered in `.github/workflows/test-and-report.yml` so the suite actually runs it.

**Caveat, on the record.** Dmitri's 2026-10-05 note says one of the `drafts/tick-*` branches may hold "an `auto_reply` fix + tests". This checkout has no remote (only `main`), so it cannot be compared — but the defect is demonstrably still present in `main` and the ledger says "filed, not fixed". If a reviewer finds a competing fix on a branch, this is the smaller change: it removes an ad-hoc filter, it does not add a subsystem.

## Kept open — take in turn

- [ ] **Outreach — the Monday line (`2026-10-05`).** **Moved past.** The 2026-10-06 18:29Z wake built the follow-up mechanism (`scripts/outreach_followups.py`, `tests/test_outreach_followups.py`) — a **delivery state** on a review branch this checkout cannot see. **Do not rebuild it.** Its firing step (draft follow-ups to anyone quiet 10+ days: Retraction Watch and Fluge were sent 2026-09-17) needs the mechanism landed, or a hand-draft.
      repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] **Agenda item 22 — outbound stewardship.** Not wake-takeable: *template tested* = a delivery state (`scripts/outreach_readiness.py`); *first cold batch dispatched* = attended/human (promote `channels/outreach/drafts/` → `channels/outbound/`); *Track 2 next round* = needs a competing entry from another architecture or a human. **Do not rebuild any of the three; do not re-run the demonstration.**
- [ ] **Agenda item 12 — the public-good programme.** Closed as **BUILT** (decision in `works/queue/07-negative-and-nonreplicated-results.md`); `docs/works/nonreplication.html` awaits a reviewer. **Do not re-open or re-derive any of it.**
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **`scripts/review_state.py`, `tests/test_review_state.py`** (2026-10-08 16:35Z wake — the review-counting report the human asked for on 2026-10-06) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild the reporter.**
- **`channels/outreach/newsletter-platform-tiers.md`, `.json`, `tests/test_newsletter_platform_tiers.py`** (2026-10-08 12:34Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not redo the platform comparison.**
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
- **Fix the Reddit 403 / the Reddit read-access script** — Dmitri's 2026-10-05 note says the `drafts/tick-*` pile holds "a Reddit read-access script + tests", so this is likely a delivery state. Unverifiable from this checkout (no remote). **Reviewer/landing action, one line: check whether the Reddit fix is already on a branch before anyone rebuilds it.**

## Reject queue — reviewed this wake

All four items were re-read and each carries a fresh `reviewed: desi 2026-10-08 cannot` line with its reason: three (invoke the friction pass; move the channel-log trim to the local side; `file_tasks` must call `new_items(...)`) need a call site in a private bot directory this session may not edit; one (drain the draft pile / verify landed drafts) needs a git remote and `git remote -v` is still empty here. Nothing on the queue is takeable from a wake.

## Struck out — done in `main`, do not re-derive

- [x] **The automated-sender leak at the reply boundary** (this wake, 2026-10-08): `channels/auto_reply.py` now uses `channels.mail.is_automated` / `is_delivery_failure` instead of an inline `"noreply"` substring test (which missed `"no-reply"`). Three new tests in `tests/test_auto_reply.py` (7/7), registered in `.github/workflows/test-and-report.yml`. Do not re-filter.

- [x] **Agenda item 32 step (2)** (2026-10-06): §8 of the affective-pain map — the 16 biomarker-only records hand-classified; the claim narrowed to *the brain and the pain, but not the mood*; `tests/test_affective_pain_acupuncture_filtered.py` pins the 16. Do not re-classify.

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
