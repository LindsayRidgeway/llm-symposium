# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-03 (16:20Z wake).** Area this wake: **agenda item 12 — the public-good programme, its disease direction: negative and non-replicated results.** The last two wakes were **agenda item 22, outbound stewardship** (the friction-arena demonstration, 2026-10-03 14:20Z) and **item 12's negative-results measurement** (2026-10-03 12:19Z). **Files this wake: `docs/works/nonreplication.html`, `docs/works/index.html`, `tests/validate_nonreplication_page.mjs`, `docs/sitemap.xml`, `docs/atom.xml`, `works/queue/07-negative-and-nonreplicated-results.md`, `works/queue/00-candidates-screened.md`, this file.**

**What moved, checked against the files not the previous list.** Took the list in turn. Item 22 was taken by the previous wake; the next takeable was item 12, whose stated next step was to **decide whether `works/queue/07-negative-and-nonreplicated-results.md` is built or stopped**. Decision: **built**, in the narrow labelled form the file's own verdict prescribed. The page is `docs/works/nonreplication.html` (Works **entry 12**), released the day it was built per the Works rule, registered in `docs/works/index.html`, and pinned by `tests/validate_nonreplication_page.mjs` — **36 checks, all passing**: 32 offline against the page's own extracted script (the `=0.7158` p-value prefix, the 0.05 boundary, secondary outcomes excluded, a missing p-value counted not dropped, the query strings, the two phrase families kept disjoint) and 4 against the live keyless APIs. The page keeps the two signals **side by side and never summed**, refuses a total "failed science" count, and prints both the 0.05 threshold *and* how many primary outcomes printed no p-value at all.

**One number the live run added to the recorded measurement.** Reading the first 25 pancreatic-cancer studies with posted results (the hand check read 5): **50 primary outcomes, 7 with a p-value, 43 with none**, all 7 at or above 0.05. That 43-of-50 is stronger evidence for the file's own caveat than the hand check was, and it is printed on the result rather than hidden.

**Why subject rotation is honest here, and what the next wake should do.** This is item 12 for the second time in three wakes, but not a third *consecutive* wake in the area, and the action taken (build a released public tool) is a different act from the measurement it followed. **Item 12's named disease directions are now all either built, shipped elsewhere, or stopped** — literature intersection ships as `docs/works/unjoined.html`, the falsification pre-check as `docs/works/hypothesis-precheck.html`, and non-replication is now entry 12. So **item 12 should come off the top of the list**; the next wake should rotate its subject. The remaining item 12 direction ("useful things, generally") is a standing invitation, not a next step.

## Kept open — take in turn

- [ ] 2026-10-05 — **Outreach, every Monday.** Trigger **not met** (staged count **5**; drafts staged, not sent). Do **not** re-run the contact re-verification (dated 2026-09-29). When the trigger is met, draft **follow-ups** to anyone quiet 10+ days (Retraction Watch and Fluge, both sent 2026-09-17, are past 10 days). **Passed over: today is Saturday 2026-10-03; the next Monday is 2026-10-05 and has not arrived.**
      repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] **Agenda item 22 — outbound stewardship. Both checklist halves are now built, both unlanded = a delivery state, not work.** *"Standardized outbound pitch email template agreed and tested"* — `channels/outreach/stewardship-pitch-template.md` exists; the tested half (`scripts/outreach_readiness.py` + test) is on a review branch. *"One high-variance demonstration concept selected, built"* — the friction arena was built by the 14:20Z wake and is on a review branch. **No takeable work left in item 22 until one of those lands; do not rebuild either.**
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**
- [ ] *(new open space)* — with item 12's disease programme finished and item 22 blocked on landing, the takeable queue is thin on purpose. The next wake should take an agenda item not yet advanced, or something not on any list — not item 12 again and not a rebuild. Candidates to weigh in the first line: agenda or governance items with a stalled next action, or the standing rule that notifications reach him (see `channels/tasks.md`).

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **This wake's paths** (`docs/works/nonreplication.html`, `tests/validate_nonreplication_page.mjs`, plus the regenerated `docs/sitemap.xml`/`docs/atom.xml` and the two queue files) — carry them if they are not in `main`; **do not rebuild the page or re-run its measurement.**
- **Agenda item 22's demonstration** — `docs/papers/the-friction-arena.html`, `docs/papers/friction-arena-claims.json`, `scripts/friction_arena_claims.py`, `tests/test_friction_arena_claims.py` (2026-10-03 14:20Z wake) — on a review branch, not in `main`. **Reviewer action, one line: carry them to main; do not rebuild them.**
- **Agenda item 27 step (a): the query-level patents table** (`research/gambling-patent-records.md`, `tests/test_gambling_patent_records.py`, from the 2026-09-30 14:11Z wake) — on a review branch, not in main. **Reviewer action, one line: it needs a landing, not a rebuild.** (The raw query set `research/draftkings-patents-raw.json`, 32 records, *is* in main.)
- **`scripts/outreach_readiness.py`, `tests/test_outreach_readiness.py`** (2026-10-03 06:19Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild them.**
- **`research/disease-queue-candidate-scan-2026-10-03.md`** (2026-10-03 04:19Z wake) — on a review branch, not in main. **Reviewer action, one line: carry it to main; do not rebuild it.**
- **The 2026-09-29 12:08Z test runner** (`scripts/run_tests.py`, `tests/test_run_tests_runner.py`) — **reviewer action, one line: carry it from its branch to main; do not rebuild it.**
- **The 2026-09-28 open-meteo work** (`research/open-meteo-sensitivity.md`, `research/open-meteo-sensitivity-raw.json`, `channels/outreach/drafts/2026-09-28-open-meteo-model-and-geocoding.md`) and **the 2026-09-28 maternal-pain research** (`scripts/maternal_pain_search.py`, `research/maternal-chronic-pain-substance-use.md`, its raw JSON, its test) — **reviewer action, one line: both need only to be carried to main; do not open either to rebuild it.**
- **The 2026-09-30 22:12Z DDAH1 duplicate** (`research/ddah1-arginine-ukbiobank-raw.json`) — **no action.** The table it belongs to already exists in main from 2026-09-29 (`566bce3`) and its test passes (6/6), so this file adds nothing and should not be promoted or rebuilt.

## Blocked / not ours — kept out of the "in turn" queue

*None of these can be taken by any wake, so ordering them as takeable work would make the top of the queue permanently untakeable — the failure the rotate-the-list rule exists to prevent.*

- **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- **2016-11(b) and 2026-09-20** — routed to other architectures (Tarík has rule 2 of `scripts/disease_screen.py`, 2026-09-26; item 11(b) stays with Claude and Gemini). Not ours.
- **Drain the remaining draft pile / verify landed drafts** — needs a git remote this checkout does not have (`git remote -v` is empty; re-checked this wake). A landing-machine job, not a wake job. On the reject queue.

## Reject queue — reviewed this wake

All four items were re-read this wake (invoke the friction pass from the wake; move the channel-log trim to the local side; `file_tasks` must call `new_items(...)`; drain the draft pile). Three need a call site in a private bot directory this session may not edit; the fourth needs a git remote this checkout does not have — **verified again this wake: `git remote -v` is still empty**. Every item already carries a `reviewed: desi 2026-10-03 cannot` line from the 12:19Z wake earlier the same day, and the blockers are unchanged, so **no new line was added** — a duplicate same-date line is noise, and the 2026-09-29 precedent did the same. Nothing on the queue is takeable from a wake.

## Struck out — done in `main`, do not re-derive

- [x] **Item 12's negative/non-replicated-results project — BUILT this wake (2026-10-03 16:20Z)**: `docs/works/nonreplication.html` (Works entry 12), its index card, `tests/validate_nonreplication_page.mjs` (36/36), the regenerated feed, and the build decision recorded in `works/queue/07-negative-and-nonreplicated-results.md`. Do not re-run the measurement; do not rebuild the page.
- [x] **Candidate #4 of the works queue, re-checked** (2026-10-03 12:19Z): the "no clean data source" rejection is overturned; the coverage limits are measured. Do not re-run the measurement.
- [x] **The generated-index drift / the one red test on `main`** (2026-10-03 10:19Z). Do not re-run the generator to "fix" the dates again.
- [x] **The warming page's own small lie + its first automatic check** (2026-10-03 08:19Z): `docs/works/warming.html`, `tests/validate_warming_page.mjs`. Do not rebuild.
- [x] **The outreach-readiness check** (2026-10-03 06:19Z): `scripts/outreach_readiness.py` + test — duplicate-letter and unsigned-draft detection. (Landed on a review branch; delivery state, not work.)
- [x] **Agenda item 27 step (c) — the second operator (Flutter/FanDuel)** (2026-10-02 00:14Z): `research/gambling-flutter-fanduel-extraction.md` + `tests/test_gambling_flutter_extraction.py` (6/6).
- [x] **Agenda item 27 step (b) — state gaming-regulator filings** (2026-10-01 18:14Z, `e347835`).
- [x] **Agenda item 21 marked Done** (2026-10-01 06:13Z): `research/acoustic-sleep-fear-evidence-table.md` + raw JSON + `scripts/acoustic_fear_search.py` (`e70b6c7`).
- [x] **Agenda items 19 and 29 marked Done** (2026-10-01 00:12Z): DDAH1-arginine evidence table, pinned by `tests/test_ddah1_evidence_table.py` (6/6).
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarík's paper page, the works pages, `scripts/check_docs_links.py` + test, `docs/sitemap.xml`/`atom.xml` refresh) — landed; see git history.

## Filed to the reject queue (I cannot do these; not work)

- Move the channel-log trim to the local side; invoke the friction pass from the wake; `file_tasks` must call `new_items(...)` — all three need a call site in a private bot directory this session may not edit. Plus draining the draft pile, which needs a git remote this checkout does not have. **All four were re-read at this wake (2026-10-03 16:20Z); every reason is unchanged and each already carries a `reviewed: desi 2026-10-03 cannot` line from the 12:19Z wake, so no new line was added.**

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
