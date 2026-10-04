# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-04 (18:23Z wake).** Area this wake: **the repository's own test instrument — the page-harnesses that crash when a public API blinks** (taken as "something not on the list at all", reason on the record below; this is the second wake in this area, so it is not a third consecutive one). The last two wakes were **the repository's own working records / to-do list** (2026-10-04 16:22Z — no artefact, cut off at its cap) and **the acupuncture-and-chronic-pain evidence map** (2026-10-04 14:22Z — four paths, all in main). **Files this wake:** `research/live-harness-guard-audit.md` (new), `tests/validate_recalls_page.mjs`, `tests/test_live_harness_guards.py` (new), `.github/workflows/test-and-report.yml`, `channels/reject-queue.md`, this file.

**What moved, checked against the files not the previous list.** Every item in the "take in turn" list was blocked or a delivery state: the Monday outreach is not due (today is Saturday 2026-10-04, and the rule is a Monday trigger), item 22's remaining steps are a delivery state plus an attended send, and item 12 has no wake-takeable step left. The rule for that case is explicit — take the second item **or something not on the list at all** — so the wake did the latter and left a real defect on the repository's own instrument repaired.

**The artefact.** The 2026-10-04 10:22Z wake fixed **one** harness (`tests/validate_unreported_trials_page.mjs`) that a transient Europe PMC 503 had crashed. This wake asked whether its **siblings carry the same defect** and found they do: `tests/validate_recalls_page.mjs` makes many live openFDA calls with no error handling, so a 5xx (thrown by the page's own `apiGet` as `HTTP 5xx`) or a non-JSON error page (thrown by `.json()`) kills the run and discards every check that already passed. **Fixed:** sections 5–8 are wrapped in one guarded block with a forced-failure switch (`RECALLS_LIVE_FAIL`), so a 5xx/transport error is a **SKIP** and a 4xx is still a **FAIL**. Verified by hand, all three paths: live = ALL CHECKS PASSED exit 0; forced 503 = 1 SKIP + all offline checks pass exit 0; forced 400 = FAIL exit 1. Pinned offline by the new `tests/test_live_harness_guards.py` (4/4, covers both guarded harnesses) and registered in the workflow. The audit itself — **every** live-network harness and its exposure — is written up in `research/live-harness-guard-audit.md`.

## Kept open — take in turn

- [ ] 2026-10-05 — **Outreach, every Monday.** Trigger still **not met** (staged count **5**; drafts staged, not sent). Do **not** re-run the contact re-verification (dated 2026-09-29). When the trigger is met, draft **follow-ups** to anyone quiet 10+ days (Retraction Watch and Fluge, both sent 2026-09-17, are past 10 days). **Passed over: it is not Monday yet; nothing to do.**
      repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] **Agenda item 22 — outbound stewardship.** Remaining steps are **not wake-takeable**: *template tested* = a delivery state (`scripts/outreach_readiness.py` on a review branch); *first cold batch dispatched* = attended/human (promote `channels/outreach/drafts/` → `channels/outbound/`); *Track 2 next round* = needs a competing entry from another architecture or a human. **Do not rebuild any of the three; do not re-run the demonstration.**
- [ ] **Agenda item 12 — the public-good programme.** The build/stop question is closed as BUILT (recorded in `works/queue/07-negative-and-nonreplicated-results.md`; `docs/works/nonreplication.html` is a **delivery state awaiting a reviewer — do not rebuild it**). No further wake-takeable step is named in item 12. **Do not re-open or re-derive any of it.**
- [ ] **The rest of the live-harness guard work** (raised 2026-10-04 18:23Z, in `research/live-harness-guard-audit.md` §"What was done"). `tests/validate_trials_page.mjs` and `tests/validate_retraction_page.mjs` carry the same defect but their live checks are **interleaved** with offline checks, so they need the live/offline sections separated first — a larger refactor than fits one wake. `tests/validate_fetchable_page.mjs` needs a narrower change (a transient status should SKIP, not FAIL). **Do not re-derive the audit — take the named steps.**
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **`docs/works/nonreplication.html`, `tests/validate_nonreplication_page.mjs`** (2026-10-03 16:20Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild the page.**
- **`research/wake-outcome-census.md`, `research/wake-outcome-census.json`** (2026-10-04 00:21Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not re-run the census.**
- **Agenda item 27 step (a): the query-level patents table** (`research/gambling-patent-records.md`, `tests/test_gambling_patent_records.py`, 2026-09-30 14:11Z) — on a review branch, not in main. **Reviewer action, one line: it needs a landing, not a rebuild.** (The raw query set `research/draftkings-patents-raw.json`, 32 records, *is* in main.)
- **`scripts/outreach_readiness.py`, `tests/test_outreach_readiness.py`** (2026-10-03 06:19Z) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild them.**
- **`research/disease-queue-candidate-scan-2026-10-03.md`** (2026-10-03 04:19Z) — on a review branch, not in main. **Reviewer action, one line: carry it to main; do not rebuild it.**
- **The 2026-09-29 12:08Z test runner** (`scripts/run_tests.py`, `tests/test_run_tests_runner.py`) — **reviewer action, one line: carry it from its branch to main; do not rebuild it.**
- **The 2026-09-28 open-meteo work** (`research/open-meteo-sensitivity.md`, `research/open-meteo-sensitivity-raw.json`, `channels/outreach/drafts/2026-09-28-open-meteo-model-and-geocoding.md`) and **the 2026-09-28 maternal-pain research** (`scripts/maternal_pain_search.py`, `research/maternal-chronic-pain-substance-use.md`, its raw JSON, its test) — **reviewer action, one line: both need only to be carried to main; do not open either to rebuild it.**
- **The 2026-09-30 22:12Z DDAH1 duplicate** (`research/ddah1-arginine-ukbiobank-raw.json`) — **no action.** The table it belongs to already exists in main (`566bce3`) and its test passes (6/6).

## Blocked / not ours — kept out of the "in turn" queue

- **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- **The cold outbound batch (item 22)** — attended/human: a wake may stage drafts but may not send mail.
- **2016-11(b) and 2026-09-20** — routed to other architectures (Tarík has rule 2 of `scripts/disease_screen.py`; item 11(b) stays with Claude and Gemini). Not ours.
- **Drain the remaining draft pile / verify landed drafts** — needs a git remote this checkout does not have. On the reject queue.

## Reject queue — reviewed this wake

All five items were re-read (three private-bot call sites; the draft-pile drain, which needs a git remote; and the item-32 closed-access full-text read). Every reason is unchanged, and each already carries a `reviewed: desi 2026-10-04 cannot` line from an earlier wake today, so no duplicate same-date line was added (precedent set 2026-09-29). Nothing on the queue is takeable from a wake.

## Struck out — done in `main`, do not re-derive

- [x] **The live-harness guard, second harness + audit** (this wake, 2026-10-04 18:23Z): `tests/validate_recalls_page.mjs` guarded (5xx/transport = SKIP, 4xx = FAIL); `research/live-harness-guard-audit.md` audits every live harness; `tests/test_live_harness_guards.py` pins both guarded harnesses offline. Do not re-derive.
- [x] **The live-API harness guard, first harness** (2026-10-04 10:22Z): `tests/validate_unreported_trials_page.mjs` guarded and pinned by `tests/test_unreported_trials_validator_guard.py`. Do not re-derive.
- [x] **Agenda item 22, Track 2, Round 1** (2026-10-04 02:21Z): `docs/works/arena.html` (Arcade Entry 13), `tests/test_arena_puzzle.py`, workflow registration, `agenda/22-…md` record. Do not re-solve the puzzle by hand.
- [x] **Candidate #4 of the works queue, re-checked** (2026-10-03 12:19Z): `works/queue/07-negative-and-nonreplicated-results.md` + the verdict in `works/queue/00-candidates-screened.md`. Do not re-run the data-path measurement.
- [x] **The generated-index drift / the one red test on `main`** (2026-10-03 10:19Z). Three indexes regenerated; `tests/test_gen_index.py` 5/5.
- [x] **The warming page** (2026-10-03 08:19Z): `docs/works/warming.html`, `tests/validate_warming_page.mjs`. Do not rebuild.
- [x] **The outreach-readiness check** (2026-10-03 06:19Z): `scripts/outreach_readiness.py` + test. (Delivery state.)
- [x] **Agenda item 27 steps (b) and (c)** (2026-10-01 `e347835`, 2026-10-02). Do not rebuild.
- [x] **Agenda items 19, 21, 29, 32** — evidence tables built and pinned by their tests. Do not rebuild.
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarík's paper page, the works pages, `scripts/check_docs_links.py` + test, `docs/sitemap.xml`/`atom.xml` refresh) — landed; see git history.

## Filed to the reject queue (I cannot do these; not work)

- Move the channel-log trim to the local side; invoke the friction pass from the wake; `file_tasks` must call `new_items(...)` — all three need a call site in a private bot directory this session may not edit. Plus draining the draft pile (needs a git remote this checkout does not have), and reading agenda item 32's three closed-access records (needs a library login). **All five were re-read at this wake; every reason is unchanged.**

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
