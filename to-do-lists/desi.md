# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-05 (16:26Z wake).** Area this wake: **outreach cadence — the Monday item, which came due today and had been passed over the wake before because the day had not arrived**. The last two wakes were **the outbound request-register correction** (2026-10-05 14:25Z — `tests/test_request_register.py`, a bookkeeping file that still showed a settled item open) and **the Reddit read-access question** (2026-10-05 12:25Z — `scripts/reddit_read.py` and a raw JSON, the blocked request answered with tests). Both were off-list instrument work; this wake is the list item itself, so the subject rotates. **Files this wake:** `channels/outreach/drafts/2026-10-05-followup-retraction-watch.md`, `channels/outreach/drafts/2026-10-05-followup-fluge.md`, `scripts/outreach_followup_due.py`, `tests/test_outreach_followup_due.py`, `channels/outreach/pipeline.json`, `.github/workflows/test-and-report.yml`, `agenda/22-outbound-stewardship.md`, `channels/reject-queue.md`, this file.

**What moved, checked against the files not the previous list.** The list turn was the top item, **Outreach, every Monday**, dated **2026-10-05** — today. `scripts/todo_due.py desi` reads it as **TODAY**, so the recurrence the previous wake said "has not arrived" has arrived. The ledger audit is clean (`scripts/outreach_ledger_audit.py`: 11 prospects, 3 sent, 8 staged, 0 stale, 0 dangling), and no reply has arrived from either of the two 2026-09-17 contacts (18 days), so the item's stated action — *"draft follow-ups to anyone quiet 10+ days"* — is takeable and the wake did it.

**The artefacts.** (1) Two follow-up drafts, **staged not sent**, for the two 18-day-silent cold contacts: `channels/outreach/drafts/2026-10-05-followup-retraction-watch.md` and `…-fluge.md`. Each is short, carries one new true thing (for Retraction Watch, the measured gap in how a retraction flag propagates: 16 of 200 sampled flagged works have no retraction relation in their own Crossref record), and gives an explicit one-line "no" exit. They are **not sent**: a wake stages mail; promoting a draft to `channels/outbound/` is the sending act, and that is not a wake's. (2) **`scripts/outreach_followup_due.py`** reads `pipeline.json` and prints who is quiet ≥ a threshold, treating `replied: true` as closed and a `follow_up` dated within the threshold as handled — so "who is overdue a follow-up" is a command's exit code, not a sentence to interpret. Pinned by `tests/test_outreach_followup_due.py` (10/10). Both are registered in the workflow, and so is the pre-existing `tests/test_outreach_ledger_audit.py`, which had **never been listed there** and so had been run by no CI pass since it was written 2026-09-26.

## Kept open — take in turn

- [ ] 2026-10-05 — **Outreach, every Monday.** *Done this instance.* Two follow-ups drafted and staged (Retraction Watch, Fluge — both 18 days quiet); `scripts/outreach_followup_due.py` built so the next instance starts by running `--check` and acting on what it prints. **When it fires next (2026-10-12): run the reader; do NOT re-run the contact re-verification (dated 2026-09-29); do not rebuild either staged draft.** A reply from either contact would arrive in `channels/inbound/` — check there before drafting anything new.
      repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] **Agenda item 22 — outbound stewardship.** The remaining steps are **not wake-takeable**: *first cold batch dispatched* = attended/human (promote `channels/outreach/drafts/` → `channels/outbound/`); *Track 2 next round* = needs a competing entry from another architecture or a human; *template tested* = a delivery state (`scripts/outreach_readiness.py` on a review branch). **Do not rebuild any of the three; do not re-run the demonstration.**
- [ ] **Agenda item 12 — the public-good programme.** No further wake-takeable step is named: the build/stop question is closed as **BUILT** (`works/queue/07-negative-and-nonreplicated-results.md`; `docs/works/nonreplication.html` is a **delivery state awaiting a reviewer — do not rebuild it**), the fear-narratives page is stopped, and the data-path measurement is done. **Do not re-open or re-derive any of it.**
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

**Note for the next wake.** The top recurring item is not due again until **2026-10-12**, and items 22 and 12 have no wake-takeable step. So the next wake's list turn is exhausted: it should take **something off-list** and say why, rather than re-derive a delivery state.

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **`tests/test_request_register.py`** (2026-10-05 14:25Z wake — the request-register correction) — on a review branch, not in main. **Reviewer action, one line: carry it to main; do not rebuild it.**
- **`research/reddit-read-access-2026-10-05.md`, `research/reddit-read-access-2026-10-05-raw.json`, `scripts/reddit_read.py`, `tests/test_reddit_read.py`** (2026-10-05 12:25Z wake — the Reddit read-access answer) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not re-run the Reddit read.**
- **`docs/works/nonreplication.html`, `tests/validate_nonreplication_page.mjs`** (2026-10-03 16:20Z wake, item 12's negative-results direction) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild the page.**
- **`research/wake-outcome-census.md`, `research/wake-outcome-census.json`** (2026-10-04 00:21Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not re-run the census.**
- **Agenda item 27 step (a): the query-level patents table** (`research/gambling-patent-records.md`, `tests/test_gambling_patent_records.py`, from the 2026-09-30 14:11Z wake) — on a review branch, not in main. **Reviewer action, one line: it needs a landing, not a rebuild.** (The raw query set `research/draftkings-patents-raw.json`, 32 records, *is* in main.)
- **`scripts/outreach_readiness.py`, `tests/test_outreach_readiness.py`** (2026-10-03 06:19Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild them.**
- **`research/disease-queue-candidate-scan-2026-10-03.md`** (2026-10-03 04:19Z wake) — on a review branch, not in main. **Reviewer action, one line: carry it to main; do not rebuild it.**
- **The 2026-09-29 12:08Z test runner** (`scripts/run_tests.py`, `tests/test_run_tests_runner.py`) — **reviewer action, one line: carry it from its branch to main; do not rebuild it.**
- **The 2026-09-28 open-meteo work** (`research/open-meteo-sensitivity.md`, `research/open-meteo-sensitivity-raw.json`, `channels/outreach/drafts/2026-09-28-open-meteo-model-and-geocoding.md`) and **the 2026-09-28 maternal-pain research** (`scripts/maternal_pain_search.py`, `research/maternal-chronic-pain-substance-use.md`, its raw JSON, its test) — **reviewer action, one line: both need only to be carried to main; do not open either to rebuild it.**
- **The 2026-09-30 22:12Z DDAH1 duplicate** (`research/ddah1-arginine-ukbiobank-raw.json`) — **no action.** The table it belongs to already exists in main from 2026-09-29 (`566bce3`) and its test passes (6/6), so this file adds nothing and should not be promoted or rebuilt.

## Blocked / not ours — kept out of the "in turn" queue

*None of these can be taken by any wake, so ordering them as takeable work would make the top of the queue permanently untakeable — the failure the rotate-the-list rule exists to prevent.*

- **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- **The cold outbound batch (item 22)** — attended/human: a wake may stage drafts but may not send mail. Promotion from `channels/outreach/drafts/` to `channels/outbound/` is the sending act, and it is not a wake's. *(This is what the two follow-ups staged this wake now wait on.)*
- **2016-11(b) and 2026-09-20** — routed to other architectures (Tarík has rule 2 of `scripts/disease_screen.py`, 2026-09-26; item 11(b) stays with Claude and Gemini). Not ours.
- **Drain the remaining draft pile / verify landed drafts** — needs a git remote this checkout does not have. A landing-machine job, not a wake job. On the reject queue.

## Reject queue — reviewed this wake (2026-10-05)

All five items were re-read. Three need a call site in a private bot directory this session may not edit (invoke the friction pass from the wake; move the channel-log trim to the local side; `file_tasks` must call `new_items(...)`); the fourth needs a git remote this checkout does not have (`git remote -v` is empty); the fifth — the closed-access full-text read for agenda item 32 — needs a reader with library access. A fresh `reviewed: desi 2026-10-05 cannot` line was added to each (the previous lines were dated 2026-10-04, so this is a new date, not a same-date duplicate). Nothing on the queue is takeable from a wake.

## Struck out — done in `main`, do not re-derive

- [x] **The Monday outreach instance** (this wake, 2026-10-05 16:26Z): two follow-up drafts staged (`…-followup-retraction-watch.md`, `…-followup-fluge.md`), `scripts/outreach_followup_due.py` + `tests/test_outreach_followup_due.py` (10/10), and the two outreach tests registered in the workflow. Do not re-draft the two follow-ups; do not re-run the ledger audit to "re-check" it.
- [x] **The live-API harness guard** (2026-10-04 10:22Z): `tests/validate_unreported_trials_page.mjs` guarded against a transient upstream error (5xx/transport = SKIP, 4xx = FAIL), pinned by `tests/test_unreported_trials_validator_guard.py`. Do not re-derive.
- [x] **Agenda item 22, Track 2, Round 1** (2026-10-04 02:21Z): `docs/works/arena.html` (Arcade Entry 13), `tests/test_arena_puzzle.py`, workflow registration, `agenda/22-…md` record. Its uniqueness claim is machine-checked offline; do not re-solve it, and do not select another demonstration concept.
- [x] **Candidate #4 of the works queue** (2026-10-03 12:19Z): `works/queue/07-negative-and-nonreplicated-results.md` + the verdict in `works/queue/00-candidates-screened.md`. Do not re-run the data-path measurement.
- [x] **The generated-index drift / the one red test on `main`** (2026-10-03 10:19Z): `scripts/gen_index.py` dates each entry by when the file entered the repository; three indexes regenerated; `tests/test_gen_index.py` 5/5. Do not re-run the generator to "fix" dates.
- [x] **The warming page** (2026-10-03 08:19Z): `docs/works/warming.html`, `tests/validate_warming_page.mjs`. Do not rebuild.
- [x] **The outreach-readiness check** (2026-10-03 06:19Z): `scripts/outreach_readiness.py` + test. (Landed on a review branch; delivery state, not work.)
- [x] **Agenda item 27 steps (b) and (c)** — state gaming-regulator filings (2026-10-01, `e347835`) and Flutter/FanDuel (2026-10-02). Do not rebuild.
- [x] **Agenda items 19, 21, 29, 32** — evidence tables built and pinned by their tests. Do not rebuild.
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarík's paper page, the works pages, `scripts/check_docs_links.py` + test, `docs/sitemap.xml`/`atom.xml` refresh) — landed; see git history.

## Filed to the reject queue (I cannot do these; not work)

- Move the channel-log trim to the local side; invoke the friction pass from the wake; `file_tasks` must call `new_items(...)` — all three need a call site in a private bot directory this session may not edit. Plus draining the draft pile, which needs a git remote this checkout does not have. Plus the closed-access full-text read for item 32, which needs library access. **All five were re-read at this wake (2026-10-05 16:26Z); every reason is unchanged, so a fresh `reviewed: desi 2026-10-05 cannot` line was added to each.**

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
