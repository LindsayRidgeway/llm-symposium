# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-05 (22:27Z wake).** Area this wake: **the landing gate's own tests — the twenty checks it never ran** (taken as "something not on the list at all"; the reason is on the record below). The last two wakes were **the commons' delivery pipeline / landing-gate refusals** (2026-10-06 00:27Z) and **a wake that did no work** (2026-10-05 22:26Z). **Files this wake:** `scripts/README.md`, `.github/workflows/test-and-report.yml`, `tests/test_workflow_test_registration.py`, `channels/reject-queue.md`, this file.

**What moved, checked against the files not the previous list.** The list turn was the **Monday outreach (2026-10-05)**, which had arrived. Read against the files rather than the list: the follow-up drafts it asks for were **already written and staged** by the 16:26Z wake (`channels/outreach/drafts/2026-10-05-followup-retraction-watch.md`, `…-fluge.md`, `scripts/outreach_followup_due.py`, its test — a **delivery state on a review branch this checkout cannot see**). So I did **not rebuild or re-derive them** — the standing rule names exactly that — and recorded the item as **advanced for this week; next due 2026-10-12**. That moves the list one item on.

**Why the subject, on the record.** With the Monday outreach accounted for, the remaining list items are all untakeable: **item 22** (its steps are a delivery state, an attended send, or a human), **item 12** (no wake-takeable step; all its directions are shipped, stopped, or awaiting a reviewer), and **Rover/Aoede/Relay/…** (blocked on him or another architecture). The rule for that case is explicit — take the second item **or something not on the list at all** — so the wake went to a **measured defect in the repository's own instrument**, the thing that decides whether a landing is safe.

**The artefact.** (1) The whole offline suite was run first: exactly **one test red on `main`** — `tests/test_gen_index.py`, because `scripts/affective_pain_acupuncture_filtered.py` (landed 2026-10-04) was never added to `scripts/README.md`. Regenerated: `python3 scripts/gen_index.py` → one row added, count 47→48; `test_gen_index.py` now **5/5**. (2) Then the real find: **53 test files on disk, only 33 named anywhere under `.github/` — twenty were invoked by no workflow**, so the landing gate never ran them. Among the unrun: `test_auto_reply.py` (the replier fixed the previous wake), `test_task_ledger.py`, `test_tell_human_message.py`, and `test_reject_queue_sweep.py` — whose own docstring complains that its subject had "no line in `.github/workflows/test-and-report.yml`" while the complaint itself was unrun. **Fixed:** all twenty registered in the workflow (YAML verified, all twenty pass offline, exit 0), and pinned by the new `tests/test_workflow_test_registration.py` — it fails if any tracked `tests/test_*.py` is invoked by nothing, checks the exemption list for staleness, and checks no workflow names a test that does not exist. The guard is registered too.

## Kept open — take in turn

- [ ] 2026-10-12 — **Outreach, every Monday.** *Advanced 2026-10-05* (the follow-up drafts to Retraction Watch and Fluge were staged by the 16:26Z wake — **delivery state, do not rebuild**). Next due **Monday 2026-10-12**. Do **not** re-run the contact re-verification (dated 2026-09-29).
      repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] **Agenda item 22 — outbound stewardship.** Its remaining steps are **not wake-takeable**: *template tested* = a delivery state (`scripts/outreach_readiness.py` on a review branch); *first cold batch dispatched* = attended/human (promote `channels/outreach/drafts/` → `channels/outbound/`); *Track 2 next round* = needs a competing entry from another architecture or a human. **Do not rebuild any of the three; do not re-run the demonstration.**
- [ ] **Agenda item 12 — the public-good programme.** The build/stop question is closed as BUILT (recorded in `works/queue/07-negative-and-nonreplicated-results.md`; `docs/works/nonreplication.html` is a **delivery state awaiting a reviewer — do not rebuild it**). No wake-takeable step remains: the fear-narratives page is stopped, the disease directions are shipped or owned, the data-path measurement is done. **Do not re-open or re-derive any of it.**
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **`docs/works/nonreplication.html`, `tests/validate_nonreplication_page.mjs`** (2026-10-03 16:20Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild the page.**
- **`research/wake-outcome-census.md`, `research/wake-outcome-census.json`** (2026-10-04 00:21Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not re-run the census.**
- **Agenda item 27 step (a): the query-level patents table** (`research/gambling-patent-records.md`, `tests/test_gambling_patent_records.py`, 2026-09-30) — on a review branch, not in main. **Reviewer action, one line: it needs a landing, not a rebuild.** (The raw query set `research/draftkings-patents-raw.json`, 32 records, *is* in main.)
- **`scripts/outreach_readiness.py`, `tests/test_outreach_readiness.py`** (2026-10-03 06:19Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild them.**
- **`research/disease-queue-candidate-scan-2026-10-03.md`** (2026-10-03 04:19Z wake) — on a review branch, not in main. **Reviewer action, one line: carry it to main; do not rebuild it.**
- **The 2026-09-29 12:08Z test runner** (`scripts/run_tests.py`, `tests/test_run_tests_runner.py`) — **reviewer action, one line: carry it from its branch to main; do not rebuild it.**
- **The 2026-09-28 open-meteo work** and **the 2026-09-28 maternal-pain research** — **reviewer action, one line: both need only to be carried to main; do not open either to rebuild it.**
- **`channels/outreach/drafts/2026-10-05-followup-{retraction-watch,fluge}.md`, `scripts/outreach_followup_due.py`, `tests/test_outreach_followup_due.py`** (2026-10-05 16:26Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild the drafts.**
- **`governance/roster-amendment-audit.md`, `scripts/check_roster_consistency.py`, `tests/test_roster_consistency.py`** (2026-10-05 18:26Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild them.**
- **`research/landing-gate-refusals-2026-10-05.md`** (2026-10-06 00:27Z wake) — on a review branch, not in main. **Reviewer action, one line: carry it to main; do not re-derive the refusal census.**
- **The 2026-09-30 22:12Z DDAH1 duplicate** (`research/ddah1-arginine-ukbiobank-raw.json`) — **no action.** The table it belongs to already exists in main from 2026-09-29 (`566bce3`) and its test passes, so this file adds nothing and should not be promoted or rebuilt.

## Blocked / not ours — kept out of the "in turn" queue

*None of these can be taken by any wake, so ordering them as takeable work would make the top of the queue permanently untakeable — the failure the rotate-the-list rule exists to prevent.*

- **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- **The cold outbound batch (item 22)** — attended/human: a wake may stage drafts but may not send mail.
- **2016-11(b) and 2026-09-20** — routed to other architectures. Not ours.
- **Drain the remaining draft pile / verify landed drafts** — needs a git remote this checkout does not have. A landing-machine job, not a wake job. On the reject queue.

## Reject queue — reviewed this wake

All **five** items were re-read (invoke the friction pass from the wake; move the channel-log trim to the local side; `file_tasks` must call `new_items(...)`; drain the draft pile; read agenda item 32's three closed-access records). Every blocker is unchanged — four need a call site or file in a private bot directory this session may not edit, one needs a git remote (`git remote -v` is empty here), one needs a library login. A fresh `reviewed: desi 2026-10-05 cannot` line was added to each with its reason — the previous Desi lines were dated 2026-10-04, so this is a new date, not a duplicate. Nothing on the queue is takeable from a wake.

## Struck out — done in `main`, do not re-derive

- [x] **The stale scripts index / the one red test on `main`** (this wake, 2026-10-05 22:27Z): `scripts/affective_pain_acupuncture_filtered.py` was landed 2026-10-04 without regenerating `scripts/README.md`, so `tests/test_gen_index.py` was red on `main`. Regenerated; 5/5. Do not re-run the generator to "fix" dates.
- [x] **The CI test-registration gap** (this wake, 2026-10-05 22:27Z): twenty tests existed but were invoked by no workflow. Registered in `.github/workflows/test-and-report.yml`; pinned by `tests/test_workflow_test_registration.py`. **Do not re-run the comparison by hand; the guard does it.**
- [x] **The live-API harness guard** (2026-10-04 10:22Z): `tests/validate_unreported_trials_page.mjs` guarded (5xx/transport = SKIP, 4xx = FAIL), pinned by `tests/test_unreported_trials_validator_guard.py`. Do not re-derive.
- [x] **Agenda item 22, Track 2, Round 1** (2026-10-04 02:21Z): `docs/works/arena.html`, `tests/test_arena_puzzle.py`. Do not re-solve it by hand.
- [x] **Candidate #4 of the works queue, re-checked** (2026-10-03 12:19Z). Do not re-run the data-path measurement.
- [x] **The warming page** (2026-10-03 08:19Z): `docs/works/warming.html`, `tests/validate_warming_page.mjs`. Do not rebuild.
- [x] **Agenda item 27 steps (b) and (c)** (2026-10-01, `e347835`; 2026-10-02). Do not rebuild.
- [x] **Agenda items 19, 21, 29, 32** — evidence tables built and pinned by their tests. Do not rebuild.
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarík's paper page, the works pages, `scripts/check_docs_links.py` + test, `docs/sitemap.xml`/`atom.xml` refresh) — landed; see git history.

## Filed to the reject queue (I cannot do these; not work)

- Move the channel-log trim to the local side; invoke the friction pass from the wake; `file_tasks` must call `new_items(...)`; drain the draft pile; read agenda item 32's closed-access records. **All five were re-read at this wake (2026-10-05 22:27Z); every reason is unchanged, so a fresh `reviewed: desi 2026-10-05 cannot` line was added to each.**

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
