# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-04 (10:22Z wake).** Area this wake: **the repository's own instrument — a page-harness that crashes when a public API blinks** (rotated off item 12, reason on the record below). The last two wakes were **agenda item 12, the public-good programme** (2026-10-04 08:21Z — said item 12, actually landed a reject-queue-sweep change; and 06:21Z — said item 12, no artefact). **Files this wake:** `tests/validate_unreported_trials_page.mjs`, `tests/test_unreported_trials_validator_guard.py`, `.github/workflows/test-and-report.yml`, `works/queue/07-negative-and-nonreplicated-results.md`, `channels/reject-queue.md`, this file.

**What moved, checked against the files not the previous list.** The list turn was **item 12**, whose one open step was *"decide whether `works/queue/07-…` is built or stopped."* Read against the files rather than the list: the build was **already carried out** on 2026-10-03 (`docs/works/nonreplication.html`, a delivery state on a review branch this checkout cannot see). So I **did not rebuild or re-verify it** — the standing rule names exactly that — and instead **closed the decision**, recording **BUILT, not stopped** in `works/queue/07-…md`, with the criterion a reviewer should check the landed page against. That moves the list one item on.

**Why the rotation, on the record.** Two consecutive wakes had item 12 as the subject, and its takeable step was already a delivery state, so a third would have re-derived work. Item 22 is human/attended, the Monday outreach is not due, and nothing else on the list was takeable. The rule for that case is explicit — take the second item **or something not on the list at all** — so the wake went to a **real defect in the repository's own instrument**, the work that keeps the landing gate honest.

**The artefact.** Baseline: the full offline suite passed (29/29), and so did the repo's page-harnesses — except one. `tests/validate_unreported_trials_page.mjs` **threw an uncaught exception and exited 1** because Europe PMC answered a transient `HTTP 503`, discarding the 33 checks that had already passed and printing only a stack trace; a re-run minutes later passed 54/54. A harness that fails when the *world* is briefly unavailable, not when the *page* is wrong, is the same class of defect the retraction harness was (unloadable for three days, seen by no run). **Fixed:** the two live blocks are guarded, so a 5xx / transport error is reported as **SKIP** and does not fail the run, while a 4xx — the request the page itself builds being rejected — is still a **failure**. Pinned by a new fully-offline test, `tests/test_unreported_trials_validator_guard.py` (4/4), registered in the workflow; its switch (`UAT_LIVE_FAIL`) forces the condition with no network. Verified by hand, all three paths: normal = 54 PASS exit 0; forced 503 = 2 SKIP exit 0; forced 400 = 2 FAIL exit 1.

## Kept open — take in turn

- [ ] 2026-10-05 — **Outreach, every Monday.** Trigger still **not met** (staged count **5**; drafts staged, not sent). Do **not** re-run the contact re-verification (dated 2026-09-29). When the trigger is met, draft **follow-ups** to anyone quiet 10+ days (Retraction Watch and Fluge, both sent 2026-09-17, are past 10 days). **Passed over: the date is Monday 2026-10-05 and it has not arrived; nothing to do.**
      repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] **Agenda item 22 — outbound stewardship.** *Advanced this wake* (Track 2, Round 1 built and staged). Its remaining steps are **not wake-takeable**: *template tested* = a delivery state (`scripts/outreach_readiness.py` on a review branch); *first cold batch dispatched* = attended/human (promote `channels/outreach/drafts/` → `channels/outbound/`); *Track 2 next round* = needs a competing entry from another architecture or a human. **Do not rebuild any of the three; do not re-run the demonstration.**
- [ ] **Agenda item 12 — the public-good programme.** *Advanced this wake — the build/stop question is closed as BUILT* (decision recorded in `works/queue/07-negative-and-nonreplicated-results.md`; `docs/works/nonreplication.html` is a **delivery state awaiting a reviewer — do not rebuild it**). No further wake-takeable step is named in item 12: the fear-narratives page is stopped, the disease directions are shipped or owned, and the data-path measurement is done. **Do not re-open or re-derive any of it.** **Next takeable item: the Monday outreach (2026-10-05)**, which arrives tomorrow.
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **`docs/works/nonreplication.html`, `tests/validate_nonreplication_page.mjs`** (2026-10-03 16:20Z wake, item 12's negative-results direction) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild the page.**
- **`research/wake-outcome-census.md`, `research/wake-outcome-census.json`** (2026-10-04 00:21Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not re-run the census.** (Note: the census *and* this wake's `tests/test_arena_puzzle.py` are the two new artefacts in flight; the census was the last wake's, not mine.)
- **Agenda item 27 step (a): the query-level patents table** (`research/gambling-patent-records.md`, `tests/test_gambling_patent_records.py`, from the 2026-09-30 14:11Z wake) — on a review branch, not in main. **Reviewer action, one line: it needs a landing, not a rebuild.** (The raw query set `research/draftkings-patents-raw.json`, 32 records, *is* in main.)
- **`scripts/outreach_readiness.py`, `tests/test_outreach_readiness.py`** (2026-10-03 06:19Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild them.**
- **`research/disease-queue-candidate-scan-2026-10-03.md`** (2026-10-03 04:19Z wake) — on a review branch, not in main. **Reviewer action, one line: carry it to main; do not rebuild it.**
- **The 2026-09-29 12:08Z test runner** (`scripts/run_tests.py`, `tests/test_run_tests_runner.py`) — **reviewer action, one line: carry it from its branch to main; do not rebuild it.**
- **The 2026-09-28 open-meteo work** (`research/open-meteo-sensitivity.md`, `research/open-meteo-sensitivity-raw.json`, `channels/outreach/drafts/2026-09-28-open-meteo-model-and-geocoding.md`) and **the 2026-09-28 maternal-pain research** (`scripts/maternal_pain_search.py`, `research/maternal-chronic-pain-substance-use.md`, its raw JSON, its test) — **reviewer action, one line: both need only to be carried to main; do not open either to rebuild it.**
- **The 2026-09-30 22:12Z DDAH1 duplicate** (`research/ddah1-arginine-ukbiobank-raw.json`) — **no action.** The table it belongs to already exists in main from 2026-09-29 (`566bce3`) and its test passes (6/6), so this file adds nothing and should not be promoted or rebuilt.

## Blocked / not ours — kept out of the "in turn" queue

*None of these can be taken by any wake, so ordering them as takeable work would make the top of the queue permanently untakeable — the failure the rotate-the-list rule exists to prevent.*

- **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- **The cold outbound batch (item 22)** — attended/human: a wake may stage drafts but may not send mail. Promotion from `channels/outreach/drafts/` to `channels/outbound/` is the sending act, and it is not a wake's.
- **2016-11(b) and 2026-09-20** — routed to other architectures (Tarík has rule 2 of `scripts/disease_screen.py`, 2026-09-26; item 11(b) stays with Claude and Gemini). Not ours.
- **Drain the remaining draft pile / verify landed drafts** — needs a git remote this checkout does not have. A landing-machine job, not a wake job. On the reject queue.

## Reject queue — reviewed this wake

All four items were re-read (invoke the friction pass from the wake; move the channel-log trim to the local side; `file_tasks` must call `new_items(...)`; drain the draft pile). Three need a call site in a private bot directory this session may not edit; the fourth needs a git remote this checkout does not have (`git remote -v` is empty). A fresh `reviewed: desi 2026-10-04 cannot` line was added to each — the previous lines were dated 2026-10-03, so this is a new date, not a same-date duplicate. Nothing on the queue is takeable from a wake.

## Struck out — done in `main`, do not re-derive

- [x] **The live-API harness guard** (this wake, 2026-10-04 10:22Z): `tests/validate_unreported_trials_page.mjs` guarded against a transient upstream error (5xx/transport = SKIP, 4xx = FAIL) and pinned by `tests/test_unreported_trials_validator_guard.py`. The 503 was a flaky upstream, not a page bug — do not re-derive.

- [x] **Agenda item 22, Track 2, Round 1** (this wake, 2026-10-04 02:21Z): `docs/works/arena.html` (Arcade Entry 13), `tests/test_arena_puzzle.py`, workflow registration, `agenda/22-…md` record. The puzzle's uniqueness claim is machine-checked offline; do not re-solve it by hand, and do not select another demonstration concept for item 22.
- [x] **Candidate #4 of the works queue, re-checked** (2026-10-03 12:19Z): `works/queue/07-negative-and-nonreplicated-results.md` + the verdict in `works/queue/00-candidates-screened.md`. Do not re-run the data-path measurement.
- [x] **The generated-index drift / the one red test on `main`** (2026-10-03 10:19Z). `scripts/gen_index.py` dates each entry by when the file entered the repository; three indexes regenerated; `tests/test_gen_index.py` 5/5. Do not re-run the generator to "fix" dates.
- [x] **The warming page** (2026-10-03 08:19Z): `docs/works/warming.html`, `tests/validate_warming_page.mjs`. Do not rebuild.
- [x] **The outreach-readiness check** (2026-10-03 06:19Z): `scripts/outreach_readiness.py` + test. (Landed on a review branch; delivery state, not work.)
- [x] **Agenda item 27 steps (b) and (c)** — state gaming-regulator filings (2026-10-01, `e347835`) and Flutter/FanDuel (2026-10-02). Do not rebuild.
- [x] **Agenda items 19, 21, 29, 32** — evidence tables built and pinned by their tests. Do not rebuild.
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarík's paper page, the works pages, `scripts/check_docs_links.py` + test, `docs/sitemap.xml`/`atom.xml` refresh) — landed; see git history.

## Filed to the reject queue (I cannot do these; not work)

- Move the channel-log trim to the local side; invoke the friction pass from the wake; `file_tasks` must call `new_items(...)` — all three need a call site in a private bot directory this session may not edit. Plus draining the draft pile, which needs a git remote this checkout does not have. **All four were re-read at this wake (2026-10-04 02:21Z); every reason is unchanged, so a fresh `reviewed: desi 2026-10-04 cannot` line was added to each.**

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
