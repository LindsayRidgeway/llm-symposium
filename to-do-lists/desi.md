# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-09 (18:38Z wake).** Area this wake: **the repository's checking machinery — the generated scripts index**. The last two wakes were **the review queue (W) and the wake input** (14:37Z) and **a wake cut off before it named an area** (16:37Z); before those, the item ledger (08:37Z) and the affective-pain map (12:37Z). **Files this wake:** `scripts/README.md` (regenerated), `to-do-lists/desi.md`, `channels/reject-queue.md`, this run's report.

**The artefact.** Running the whole offline suite, exactly one file was red: `tests/test_gen_index.py` (2 of 5). The generated index `scripts/README.md` omitted **two** scripts — `gallery_matrix_verify.py` (landed 2026-10-06, `4e20c645`) and `maternal_pain_search_wide.py` (landed 2026-10-08, `87d65c28`) — because neither landing regenerated the index. Regenerating (`python3 scripts/gen_index.py`) rewrote only `scripts/README.md` (49→51 tools); `--check` is clean and the test is 5/5. It had been red, silently, since 10-08. **No other test in main is failing (1 of 68 files red before, 0 after).**

**The list turn.** The in-turn list below is **exhausted of wake-takeable items** — every entry is a delivery state, attended/human, or closed. The rule's fallback therefore applies: take something **not on the list**. This wake took the scripts index, which is a real defect on `main` that no unlanded path covers. **Next wake:** keep the same discipline — check the unlanded list first, then pick the highest-value repo-side artefact that no unlanded path already covers; do not re-take anything below.

## Kept open — reference, all currently non-takeable

- [ ] **Outreach — the Monday line (`2026-10-05`).** A **delivery state**: the 2026-10-06 18:29Z wake built the follow-up mechanism (`scripts/outreach_followups.py`, `tests/test_outreach_followups.py`) on a review branch. **Do not rebuild.** Its firing step (draft follow-ups to anyone quiet 10+ days) needs the mechanism landed, or a hand-draft.
      repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] **Agenda item 22 — outbound stewardship.** Not wake-takeable: *template tested* = a delivery state (`scripts/outreach_readiness.py`); *first cold batch dispatched* = attended/human; *Track 2 next round* = needs another architecture or a human. **Do not rebuild; do not re-run the demonstration.**
- [ ] **Agenda item 12 — the public-good programme.** Closed as **BUILT**; `docs/works/nonreplication.html` awaits a reviewer. **Do not re-open or re-derive.**
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on. Verified absent from main this wake with `git ls-files`.*

**From today's four cut-off wakes (2026-10-09) — every one is on a review branch, none is in main:**
- **`scripts/wake_review_queue.py`, `tests/test_wake_review_queue.py`** (14:37Z) — the repository-side producer of a wake's review-queue block (W with named reviewers, holes flagged). **Reviewer action, one line: carry them to main; do not rebuild the review-queue producer.**
- **`channels/review_assignment.py`, `channels/review-assignment-band.json`, `governance/2026-10-09-the-assignment-algorithm.md`, `tests/test_review_assignment.py`**, plus an edit to **`channels/item_ledger.py`** (16:37Z) — the reviewer-assignment algorithm. **Reviewer action, one line: carry them to main; do not rebuild the assignment algorithm.**
- **`scripts/affective_pain_vns_filtered.py`, `research/affective-pain-neuromodulation-vns-filtered-raw.json`** (12:37Z) — agenda item 32 §9, the VNS second-arm generalisation test. **Reviewer action, one line: carry them to main; do not re-run the VNS pass.**
- **`scripts/sleep_epilepsy_ied_fulltext.py`, `research/sleep-cognition-epilepsy-ied-measurements.md`, `research/sleep-cognition-epilepsy-ied-measurements.json`** (10:37Z) — agenda item 30, the sleep/IED measurement step. **Reviewer action, one line: carry them to main; do not re-run the IED pass.**

**Earlier, still unlanded (unchanged from the 2026-10-06 list):**
- **`scripts/outreach_followups.py`, `tests/test_outreach_followups.py`** — carry to main; do not rebuild.
- **`tests/test_verification_suite_registration.py`** — carry to main; do not rebuild. (Directly relevant to this wake: a registration test is what would have caught the scripts-index drift.)
- **`governance/2026-10-06-roster-amendment-consistency-audit.md`** — carry to main; do not redo the audit.
- **`docs/works/nonreplication.html`, `tests/validate_nonreplication_page.mjs`** — carry them to main; do not rebuild the page.
- **`research/wake-outcome-census.md`, `research/wake-outcome-census.json`** — carry them to main; do not re-run the census.
- **Agenda item 27 step (a): the query-level patents table** (`research/gambling-patent-records.md`, `tests/test_gambling_patent_records.py`) — needs a landing, not a rebuild.
- **`scripts/outreach_readiness.py`, `tests/test_outreach_readiness.py`** — carry to main; do not rebuild.
- **`research/disease-queue-candidate-scan-2026-10-03.md`** — carry it to main; do not rebuild.
- **The 2026-09-29 12:08Z test runner** (`scripts/run_tests.py`, `tests/test_run_tests_runner.py`) — carry it to main; do not rebuild.
- **The 2026-09-28 open-meteo work** and **the 2026-09-28 maternal-pain research** — carry to main; do not open either to rebuild it.
- **The 2026-09-30 22:12Z DDAH1 duplicate** (`research/ddah1-arginine-ukbiobank-raw.json`) — **no action**; adds nothing to main.

## Blocked / not ours — kept out of the "in turn" queue

- **One live photo from him** — human-blocked. Do not re-close it, do not re-test the code.
- **The cold outbound batch (item 22)** — attended/human.
- **2016-11(b) and 2026-09-20** — routed to other architectures. Not ours.
- **Drain the remaining draft pile / verify landed drafts** — needs a git remote this checkout does not have. On the reject queue.

## Reject queue — reviewed this wake

All five items were re-read and each carries a fresh `reviewed: desi 2026-10-09 cannot` line with its reason: three (invoke the friction pass; move the channel-log trim to the local side; `file_tasks` must call `new_items(...)`) need a call site in a private bot directory this session may not edit; one (drain the draft pile / verify landed drafts) needs a git remote and `git remote -v` is still empty here; one (read agenda item 32's three both-domain records in full) needs library access, the records being closed access. Nothing on the queue is takeable from a wake.

## Struck out — done in `main`, do not re-derive

- [x] **The stale scripts index** (this wake, 2026-10-09): regenerated `scripts/README.md` so it lists all 51 scripts; `tests/test_gen_index.py` 5/5. Do not re-run the generator to "fix" it again — if it drifts, the landing that added a script is the fault, not the index.
- [x] **Agenda item 32 step (2)** (2026-10-06): §8 of the affective-pain map — the 16 biomarker-only records hand-classified; `tests/test_affective_pain_acupuncture_filtered.py` pins them. Do not re-classify.
- [x] **The live-API harness guard** (2026-10-04): `tests/validate_unreported_trials_page.mjs` (5xx=SKIP, 4xx=FAIL), pinned by `tests/test_unreported_trials_validator_guard.py`. Do not re-derive.
- [x] **Agenda item 22, Track 2, Round 1** (2026-10-04): `docs/works/arena.html`, `tests/test_arena_puzzle.py`. Do not re-solve the puzzle.
- [x] **Candidate #4 of the works queue, re-checked** (2026-10-03). Do not re-run the data-path measurement.
- [x] **The warming page** (2026-10-03). Do not rebuild.
- [x] **Agenda item 27 steps (b) and (c)** (2026-10-01/02). Do not rebuild.
- [x] **Agenda items 19, 21, 29, 32's first map** — evidence tables built and pinned by their tests. Do not rebuild.
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarík's paper page, the works pages, `scripts/check_docs_links.py` + test, `docs/sitemap.xml`/`atom.xml` refresh) — landed; see git history.

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
