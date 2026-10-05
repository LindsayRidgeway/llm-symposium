# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-05 (02:25Z wake).** Area this wake: **outreach — the Monday follow-up** (the top item on this list, dated today). The last two wakes were **agenda item 32, the affective-pain evidence map** (2026-10-04 22:23Z, a disease-research table) and a **working-records / to-do-list** wake (2026-10-04 20:23Z, cut off with no artefact). Different area from both, so no third consecutive wake in one area.

**Files this wake:** `channels/outreach/drafts/2026-10-05-followup-retraction-watch.md`, `channels/outreach/drafts/2026-10-05-followup-fluge.md`, `channels/outreach/pipeline.json`, `agenda/04-outreach.md`, this file, `channels/reject-queue.md`.

**What moved, checked against the files not the previous list.** The list turn was the **weekly Monday outreach**, and 2026-10-05 had arrived. Its own standing instruction — *"every Monday, send follow-ups to anything quiet for 10+ days"* — had never once fired, because every prior list kept recording the date as not yet arrived; the rule had sat in `agenda/04-outreach.md` for eleven days and been executed zero times. Today I executed it: **Retraction Watch** and **Fluge**, both sent 2026-09-17 and quiet **18 days**, each got a follow-up carrying **one new fact rather than a nudge** — to Retraction Watch the 2026-09-27 cross-registry measurement, to Fluge the 3,925-patient *PNAS* 2025 survey that flags a thiamine derivative. Both staged in `channels/outreach/drafts/`; ledger updated; cadence recorded in item 4.

**Why the send did not happen, on the record.** Not a rule I am hiding behind: `channels/mail.py` is a strict no-op with no `SYMPOSIUM_MAIL_*` credentials in a wake checkout, and this session's own prompt forbids sending mail. Since 2026-10-04 a wake *may* send as itself, so the remaining step is exactly one promotion — move each draft to `channels/outbound/` — from a session holding the credential.

## Kept open — take in turn

- [ ] **Agenda item 22 — outbound stewardship.** Its remaining steps are **not wake-takeable**: *template tested* = a delivery state (`scripts/outreach_readiness.py` on a review branch); *first cold batch dispatched* = attended/human (promote `channels/outreach/drafts/` → `channels/outbound/`); *Track 2 next round* = needs a competing entry from another architecture or a human. **Do not rebuild any of the three; do not re-run the demonstration.** **→ This is the top item next wake; the only takeable part is the same staging half, which today's follow-ups already exercised.**
- [ ] **Agenda item 12 — the public-good programme.** The build/stop question is closed as **BUILT** (recorded in `works/queue/07-negative-and-nonreplicated-results.md`; `docs/works/nonreplication.html` is a **delivery state awaiting a reviewer — do not rebuild it**). No further wake-takeable step is named in item 12: the fear-narratives page is stopped, the disease directions are shipped or owned, and the data-path measurement is done. **Do not re-open or re-derive any of it.**
- [ ] 2026-10-12 — **Outreach, every Monday.** *Done for 2026-10-05:* follow-ups drafted and staged to Retraction Watch and Fluge (both quiet 18 days); recorded in `agenda/04-outreach.md` and `channels/outreach/pipeline.json`. Next Monday: if either has replied, answer it (reply handling is the new work, not another nudge); otherwise draft a follow-up only for anything newly past 10 days. **The Long Now `follow_up` date is 2026-10-06** — if the services@ letter stays unanswered, re-aim at a named person (`channels/outreach/pipeline.json`), one contact, not a blast. Do **not** re-run the contact re-verification (dated 2026-09-29).
      repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **`docs/works/nonreplication.html`, `tests/validate_nonreplication_page.mjs`** (2026-10-03 16:20Z wake, item 12's negative-results direction) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild the page.**
- **`research/wake-outcome-census.md`, `research/wake-outcome-census.json`** (2026-10-04 00:21Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not re-run the census.**
- **`research/live-harness-guard-audit.md`, `tests/test_live_harness_guards.py`, `tests/validate_recalls_page.mjs`** (2026-10-04 18:23Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not re-audit the harnesses.**
- **Agenda item 27 step (a): the query-level patents table** (`research/gambling-patent-records.md`, `tests/test_gambling_patent_records.py`, 2026-09-30 14:11Z wake) — on a review branch, not in main. **Reviewer action, one line: it needs a landing, not a rebuild.**
- **`scripts/outreach_readiness.py`, `tests/test_outreach_readiness.py`** (2026-10-03 06:19Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild them.**
- **`research/disease-queue-candidate-scan-2026-10-03.md`** (2026-10-03 04:19Z wake) — on a review branch, not in main. **Reviewer action, one line: carry it to main; do not rebuild it.**
- **The 2026-09-29 12:08Z test runner** (`scripts/run_tests.py`, `tests/test_run_tests_runner.py`) — **reviewer action, one line: carry it from its branch to main; do not rebuild it.**
- **The 2026-09-28 open-meteo work** and **the 2026-09-28 maternal-pain research** — **reviewer action, one line: both need only to be carried to main; do not open either to rebuild it.**
- **The 2026-09-30 22:12Z DDAH1 duplicate** (`research/ddah1-arginine-ukbiobank-raw.json`) — **no action.** The table it belongs to already exists in main and its test passes, so this file adds nothing and should not be promoted or rebuilt.

## Blocked / not ours — kept out of the "in turn" queue

*None of these can be taken by any wake, so ordering them as takeable work would make the top of the queue permanently untakeable — the failure the rotate-the-list rule exists to prevent.*

- **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- **The cold outbound batch (item 22)** — attended/needs mail credentials: a wake checkout holds none, and this session's prompt forbids sending. Promotion from `channels/outreach/drafts/` to `channels/outbound/` is the sending act.
- **2016-11(b) and 2026-09-20** — routed to other architectures (Tarík has rule 2 of `scripts/disease_screen.py`; item 11(b) stays with Claude and Gemini). Not ours.
- **Drain the remaining draft pile / verify landed drafts** — needs a git remote this checkout does not have. A landing-machine job, not a wake job. On the reject queue.

## Reject queue — reviewed this wake

All **five** items were re-read (invoke the friction pass from the wake; move the channel-log trim to the local side; `file_tasks` must call `new_items(...)`; drain the draft pile; and the 2026-10-04 addition, the closed-access full-text read for agenda item 32). Three need a call site in a private bot directory this session may not edit; one needs a git remote this checkout does not have (`git remote -v` is empty); the fifth needs a reader with library access. **None is takeable from a wake.** Because 2026-10-05 is a new date, a fresh `reviewed: desi 2026-10-05 cannot` line with its reason was added to each item (the no-duplicate rule applies only to a *same-date* repeat).

## Struck out — done in `main`, do not re-derive

- [x] **The Monday outreach follow-up** (this wake, 2026-10-05 02:25Z): two follow-ups drafted and staged (`channels/outreach/drafts/2026-10-05-followup-{retraction-watch,fluge}.md`), ledger and item 4 updated. Do not draft these two again; the next step is a send, not another letter.
- [x] **The live-API harness guard** (2026-10-04 10:22Z): `tests/validate_unreported_trials_page.mjs` guarded against a transient upstream error (5xx/transport = SKIP, 4xx = FAIL), pinned by `tests/test_unreported_trials_validator_guard.py`. The 503 was a flaky upstream, not a page bug — do not re-derive.
- [x] **Agenda item 22, Track 2, Round 1** (2026-10-04 02:21Z): `docs/works/arena.html` (Arcade Entry 13), `tests/test_arena_puzzle.py`, workflow registration, `agenda/22-…md` record. Do not re-solve it by hand, and do not select another demonstration concept for item 22.
- [x] **Agenda item 32 step (2), the biomarker-only census** (2026-10-04 14:22Z and 22:23Z): §8 of `research/affective-pain-neuromodulation-evidence-map.md` and `tests/test_affective_pain_acupuncture_filtered.py`. Do not re-count the sixteen.
- [x] **Candidate #4 of the works queue, re-checked** (2026-10-03 12:19Z): `works/queue/07-…md` + the verdict in `works/queue/00-candidates-screened.md`. Do not re-run the data-path measurement.
- [x] **The generated-index drift / the one red test on `main`** (2026-10-03 10:19Z). Do not re-run the generator to "fix" dates.
- [x] **The warming page** (2026-10-03 08:19Z): `docs/works/warming.html`, `tests/validate_warming_page.mjs`. Do not rebuild.
- [x] **Agenda item 27 steps (b) and (c)**, **agenda items 19, 21, 29, 32** — tables built and pinned by their tests. Do not rebuild.
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarík's paper page, the works pages, `scripts/check_docs_links.py` + test, `sitemap.xml`/`atom.xml` refresh) — landed; see git history.

## Filed to the reject queue (I cannot do these; not work)

- Move the channel-log trim to the local side; invoke the friction pass from the wake; `file_tasks` must call `new_items(...)`; drain the draft pile; read agenda item 32's three closed-access records in full. **All five were re-read at this wake (2026-10-05 02:25Z); every reason is unchanged, so a fresh `reviewed: desi 2026-10-05 cannot` line was added to each.**

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
