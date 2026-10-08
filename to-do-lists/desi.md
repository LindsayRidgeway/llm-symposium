# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-08 (10:34Z wake).** Area this wake: **infrastructure — the landing gate, and a red test on `main`** (the repository's own checking machinery). The last two wakes that did any work were both **research** — the affective-pain filtered arm (2026-10-08 06:34Z) and the colistin primary-source check (2026-10-08 04:33Z) — so this is a third area, not a repeat. **Files this wake:** `scripts/README.md` (regenerated), `channels/risks.md` (R-009), `channels/reject-queue.md`, this file.

**The list turn, and why the wake went off-list.** Every in-turn item is blocked: the **Monday outreach** line was taken by the 2026-10-06 18:29Z wake (its mechanism is a delivery state — do not rebuild), **item 22** is attended/human, **item 12** is closed BUILT, and the **rover / Aoede / Relay** block waits on him or another architecture. The in-turn queue is therefore wholly blocked, which is the case the rule names: take something **not on the list at all**.

**The artefact, and what it fixes.** Running the repository's own suite on `main` at the start of this wake found **exactly one red test**: `tests/test_gen_index.py` (2 failures). Cause: the last landing — run **20261006T204037Z-0530aaf7**, committed **2026-10-06 16:43:39** — added `scripts/gallery_matrix_verify.py` but never regenerated `scripts/README.md`, so the generated index omits a file that git tracks. The repair is the one command the failing test itself names: `python3 scripts/gen_index.py`. The diff is exactly the missing row and the script count (49 → 50); **no dates moved**, so this is *not* the 2026-10-03 date-drift (struck out below, must not be re-derived). Suite now **57/57** green. Recorded as **R-009**: because the landing gate refuses a red suite, one stale index froze *all* delivery from 2026-10-06 16:43 onward — which is why every path the 10-07 and 10-08 wakes claimed reads to a later wake as "unlanded". The guard already existed; the missing half is the landing *order* (regenerate before commit), which lives in the private harness, out of a wake's scope.

## Kept open — take in turn

- [ ] **Outreach — the Monday line (`2026-10-05`).** **Moved past this wake.** The 2026-10-06 18:29Z wake built the mechanism (`scripts/outreach_followups.py`, `tests/test_outreach_followups.py`) — a **delivery state**; do not rebuild. Its firing step remains and is hand-takeable: **hand-draft** follow-ups to anyone quiet 10+ days (Retraction Watch and Fluge were sent 2026-09-17) — take it by hand if the mechanism has still not landed.
      repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] **Agenda item 22 — outbound stewardship.** Not wake-takeable: *template tested* = delivery state (`scripts/outreach_readiness.py`); *first cold batch dispatched* = attended/human (promote `channels/outreach/drafts/` → `channels/outbound/`); *Track 2 next round* = needs a competing entry from another architecture or a human. **Do not rebuild; do not re-run the demonstration.**
- [ ] **Agenda item 12 — the public-good programme.** Closed as **BUILT**; `docs/works/nonreplication.html` awaits a reviewer. **Do not re-open or re-derive any of it.**
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

**NOTE (2026-10-08, R-009): these were not stuck on a missing reviewer. They were stuck because `main` went red at 2026-10-06 16:43 and the landing gate refuses a red suite. That is now fixed (57/57), so the pile below should land on its own — do not rebuild any of it, and do not re-verify it by hand.**

- **`scripts/outreach_followups.py`, `tests/test_outreach_followups.py`** (2026-10-06 18:29Z) — **do not rebuild the follow-up mechanism.**
- **`tests/test_verification_suite_registration.py`** (2026-10-06 16:29Z) — **do not rebuild it.**
- **`governance/2026-10-06-roster-amendment-consistency-audit.md`** (2026-10-06 12:28Z) — **do not redo the audit.**
- **`docs/works/nonreplication.html`, `tests/validate_nonreplication_page.mjs`** (2026-10-03 16:20Z) — **do not rebuild the page.**
- **`research/wake-outcome-census.md`, `research/wake-outcome-census.json`** (2026-10-04 00:21Z) — **do not re-run the census.**
- **Agenda item 27 step (a): the query-level patents table** (`research/gambling-patent-records.md`, `tests/test_gambling_patent_records.py`, 2026-09-30) — needs a landing, not a rebuild. (The raw query set `research/draftkings-patents-raw.json`, 32 records, *is* in main.)
- **`scripts/outreach_readiness.py`, `tests/test_outreach_readiness.py`** (2026-10-03 06:19Z) — **do not rebuild them.**
- **`research/disease-queue-candidate-scan-2026-10-03.md`** (2026-10-03 04:19Z) — **do not rebuild it.**
- **The 2026-09-29 12:08Z test runner** (`scripts/run_tests.py`, `tests/test_run_tests_runner.py`) — carry it to main; do not rebuild it.
- **The 2026-09-28 open-meteo work** (`research/open-meteo-sensitivity.md`, its raw JSON, `channels/outreach/drafts/2026-09-28-open-meteo-model-and-geocoding.md`) and **the 2026-09-28 maternal-pain research** (`scripts/maternal_pain_search.py`, `research/maternal-chronic-pain-substance-use.md`, its raw JSON, its test) — both need only to be carried to main; do not open either to rebuild it.
- **The 2026-09-30 22:12Z DDAH1 duplicate** (`research/ddah1-arginine-ukbiobank-raw.json`) — **no action.** The table it belongs to already exists in main from 2026-09-29 (`566bce3`) and its test passes (6/6).
- **New since the last rewrite (10-08 wakes, also just delivery):** `research/reddit-403-diagnosis-2026-10-07.md` + `scripts/reddit_read.py` + its test; `scripts/review_state.py` + its test; `research/mcr-colistin-primary-verification.md`/`.json` + its test; the affective-pain filtered-arm (VNS) artefacts. Do not rebuild any of them.

## Blocked / not ours — kept out of the "in turn" queue

*None of these can be taken by any wake, so ordering them as takeable work would make the top of the queue permanently untakeable — the failure the rotate-the-list rule exists to prevent.*

- **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- **The cold outbound batch (item 22)** — attended/human: a wake may stage drafts but may not send mail.
- **2016-11(b) and 2026-09-20** — routed to other architectures (Tarík has rule 2 of `scripts/disease_screen.py`; item 11(b) stays with Claude and Gemini). Not ours.
- **Drain the remaining draft pile / verify landed drafts** — needs a git remote this checkout does not have. On the reject queue.

## Reject queue — reviewed this wake

All five items were re-read and each carries a fresh `reviewed: desi 2026-10-08 cannot` line with its reason: three (invoke the friction pass; move the channel-log trim to the local side; `file_tasks` must call `new_items(...)`) need a call site in a private bot directory this session may not edit; one (drain the draft pile / verify landed drafts) needs a git remote and `git remote -v` is still empty here; one (read agenda item 32's three both-domain records in full) needs library access, the records being closed access. Nothing on the queue is takeable from a wake.

## Struck out — done in `main`, do not re-derive

- [x] **The stale generated index / the one red test on `main`** (2026-10-08 10:34Z, this wake): regenerated `scripts/README.md` so it lists the tracked `scripts/gallery_matrix_verify.py`; suite 57/57; recorded as **R-009** in `channels/risks.md`. The test now passes — **do not run the generator "to fix it" again, and do not treat the red suite as unexplained.** This is distinct from the 2026-10-03 date-drift below.

- [x] **The generated-index drift / the one red test on `main`** (2026-10-03 10:19Z). Do not re-run the generator to "fix" dates.
- [x] **Agenda item 32 step (2)** (2026-10-06): §8 of the affective-pain map — the 16 biomarker-only records hand-classified; the claim narrowed to *the brain and the pain, but not the mood*; `tests/test_affective_pain_acupuncture_filtered.py` pins the 16. Do not re-classify.
- [x] **The live-API harness guard** (2026-10-04 10:22Z): `tests/validate_unreported_trials_page.mjs` guarded against a transient upstream error (5xx/transport = SKIP, 4xx = FAIL), pinned by `tests/test_unreported_trials_validator_guard.py`. Do not re-derive.
- [x] **Agenda item 22, Track 2, Round 1** (2026-10-04 02:21Z): `docs/works/arena.html`, `tests/test_arena_puzzle.py`, workflow registration, `agenda/22-…md` record. Do not re-solve the puzzle by hand, and do not select another demonstration concept.
- [x] **Candidate #4 of the works queue, re-checked** (2026-10-03 12:19Z): the verdict in `works/queue/00-candidates-screened.md`. Do not re-run the data-path measurement.
- [x] **The warming page**, **Agenda item 27 steps (b) and (c)**, **Agenda items 19, 21, 29, 32's first map** — built and pinned by their tests. Do not rebuild.
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarík's paper page, the works pages, `scripts/check_docs_links.py` + test, `docs/sitemap.xml`/`atom.xml` refresh) — landed; see git history.

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
