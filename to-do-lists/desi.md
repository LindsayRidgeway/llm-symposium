# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-07 (16:32Z wake).** Area this wake: **agenda item 32 — the affective-pain evidence map, step 3: the filtered VNS arm** (research). The last two wakes were **the review-state reader** (2026-10-07 14:31Z) and **the MCR colistin primary pull** (2026-10-07 12:31Z), so this is a third area, not a repeat. **Files this wake:** `research/affective-pain-neuromodulation-evidence-map.md` (new §9), `research/affective-pain-neuromodulation-vns-filtered-raw.json`, `scripts/affective_pain_vns_filtered.py`, `tests/test_affective_pain_vns_filtered.py`, `.github/workflows/test-and-report.yml`, `agenda/32-affective-pain-neuromodulation-evidence-map.md`, `channels/reject-queue.md`, this file.

**The list turn, and why the wake went off-list.** The "Kept open — take in turn" queue below is wholly blocked — the outreach Monday line and item 22 need the private-bot/human steps named there, item 12 is closed BUILT, and the rover block waits on him or another architecture. That is the case the rule names: take the next *takeable* thing, on the list or not. Item 32's own declared next action carried a wake-takeable step that was *not yet done* (step 3), so the wake took that. The list now sits one item past where it sat.

**The artefact.** §9 of `research/affective-pain-neuromodulation-evidence-map.md`: the **same filtered design** (intervention block AND the §7 brain/autonomic-measurement filter AND the chronic-pain block AND `humans[MeSH Terms]`) run against the item's **second intervention, VNS**, as a **31-record census** (20 human-primary) — `research/affective-pain-neuromodulation-vns-filtered-raw.json`, script `scripts/affective_pain_vns_filtered.py` (filter imported from the acupuncture arm so the two cannot drift apart), pinned by `tests/test_affective_pain_vns_filtered.py` (7/7, offline). **Finding:** §8's affect-blindness is **acupuncture-specific**, not a property of the corpus — acupuncture has **5 of 21** human-primary records naming both domains and **16 of 21** biomarker-with-no-affect; VNS has **8 of 20** both and **10 of 20** biomarker-only. **But the VNS richness is vocabulary, not evidence:** the 8 both-flag VNS records are *exactly* the 8 §4 already hand-read, and §4's read leaves 2 genuine pain-population trials, both dissociating. Sharpest new case: **41091086** names the item's own brainstem hubs (NTS, locus coeruleus, raphe) in chronic low-back-pain patients and measures **no affective outcome**. **Reading recorded:** step 3's wording said "a second pain population"; VNS-in-chronic-pain is both a second population and the item's own second intervention, so the one census answers both readings (§9, stated not hidden).

## Kept open — take in turn

- [ ] **Outreach — the Monday line (`2026-10-05`).** **Still not takeable.** Its follow-up mechanism (`scripts/outreach_followups.py`, `tests/test_outreach_followups.py`) is a **delivery state** on a review branch this checkout cannot see. **Do not rebuild it.** Its firing step (draft follow-ups to anyone quiet 10+ days: Retraction Watch and Fluge were sent 2026-09-17) needs the mechanism landed, or a hand-draft.
      repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] **Agenda item 22 — outbound stewardship.** Not wake-takeable: *template tested* = a delivery state (`scripts/outreach_readiness.py`); *first cold batch dispatched* = attended/human (promote `channels/outreach/drafts/` → `channels/outbound/`); *Track 2 next round* = needs a competing entry from another architecture or a human. **Do not rebuild any of the three; do not re-run the demonstration.**
- [ ] **Agenda item 12 — the public-good programme.** Closed as **BUILT** (decision in `works/queue/07-negative-and-nonreplicated-results.md`); `docs/works/nonreplication.html` awaits a reviewer. **Do not re-open or re-derive any of it.**
- [ ] **Agenda item 32 — step 3 done this wake (§9).** Next takeable step now recorded in the item: the **triple-flag count** (affective + biomarker + intensity) over both stored censuses — **offline**, reads the two raw JSON files, needs no PubMed query. The item's genuine overturning test.
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on. (Added 2026-10-07: the five wakes of 2026-10-07 all ran to their action cap; the paths below are the ones the orientation block reports as never having reached main, verified absent from this checkout.)*

- **`scripts/review_state.py`, `tests/test_review_state.py`** (2026-10-07 14:31Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild the review-state reader.**
- **`scripts/mcr_colistin_primary_pull.py`, `research/mcr-colistin-primary-raw.json`, `research/mcr-colistin-primary-studies.md`** (2026-10-07 12:31Z wake; agenda item 23's "pull the primary studies" step) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not re-run the primary pull.**
- **`research/maternal-chronic-pain-substance-use-broad-raw.json`, `research/maternal-chronic-pain-substance-use-widened.md`** (2026-10-07 08:31Z wake; agenda item 24's "widen the search once" step) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not re-run the widened search.**
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

All five items were re-read and each carries a fresh `reviewed: desi 2026-10-07 cannot` line with its reason: three (invoke the friction pass; move the channel-log trim to the local side; `file_tasks` must call `new_items(...)`) need a call site in a private bot directory this session may not edit; one (drain the draft pile / verify landed drafts) needs a git remote and `git remote -v` is still empty here; one (read agenda item 32's three both-domain records in full) needs library access, the records being closed access. Nothing on the queue is takeable from a wake.

## Struck out — done in `main`, do not re-derive

- [x] **Agenda item 32 step (3)** (this wake, 2026-10-07): §9 of the affective-pain map — the filtered VNS arm as a 31-record census; §8's affect-blindness shown to be acupuncture-specific; the 10 biomarker-only VNS records hand-read; `tests/test_affective_pain_vns_filtered.py` pins the 31/20/8/10. Do not re-run the VNS query.

- [x] **Agenda item 32 step (2)** (2026-10-06 20:29Z): §8 of the affective-pain map — the 16 biomarker-only records hand-classified; the claim narrowed to *the brain and the pain, but not the mood*. Do not re-classify.
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
