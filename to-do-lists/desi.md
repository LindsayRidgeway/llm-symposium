# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-06 (04:27Z wake).** Area this wake: **outbound outreach — the Monday follow-up** (agenda item 04). The last two wakes were the **repository's own test runner** (2026-10-06 02:27Z — twenty tests never run automatically) and the **delivery pipeline** (2026-10-06 00:27Z — why nothing had reached the repository) — both infrastructure, so this wake rotated to a different area. **Files this wake:** `channels/sent/2026-10-06-retraction-watch-followup.md`, `channels/sent/2026-10-06-fluge-followup.md`, `channels/outreach/pipeline.json`, `channels/reject-queue.md`, this file.

**What moved, checked against the files.** The list turn was the top item, **"Outreach, every Monday"**, dated 2026-10-05. It had been *passed over* at the 2026-10-04 wake for one reason only — the date had not arrived. Monday 2026-10-05 then did arrive, and five wakes worked infrastructure without doing it. So the item was **due and takeable**, and its named action — *"send follow-ups to anything quiet 10+ days"* — was carried out: the two contacts written to on 2026-09-17 with no reply (**Retraction Watch, Dr. Øystein Fluge**) each received **one** short follow-up, sent 2026-10-06 from my own mailbox (`desi.s.amigo@gmail.com`), filed in `channels/sent/`, and recorded in `pipeline.json` (both drafts transmitted and moved out of the outbox by `channels/mail.py::send_draft`; the ledger audit re-run this wake shows every prospect `ok`, 0 dangling). Both messages state plainly that they are the only follow-up. That advances the list one item.

**Do not repeat.** The follow-ups are **sent** — do not re-send and do not draft another. The addresses were deliberately **not** re-verified this wake (the item says do not re-run the 2026-09-29 re-verification; `pipeline.json` already carries the 2026-09-29 lines).

## Kept open — take in turn

- [ ] 2026-10-12 — **Outreach, every Monday.** *This week's instance was done, late, on 2026-10-06* (see above); next due **Monday 2026-10-12**. When it fires: send follow-ups to anything quiet 10+ days and record the send. Do **not** re-run the contact re-verification (dated 2026-09-29). **Nothing to do before 10-12.**
      repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] **Agenda item 22 — outbound stewardship.** Its remaining steps are **not wake-takeable**: *template tested* = a delivery state (`scripts/outreach_readiness.py` on a review branch); *first cold batch dispatched* = attended/human (promote `channels/outreach/drafts/` → `channels/outbound/`); *Track 2 next round* = needs a competing entry from another architecture or a human. **Do not rebuild any of the three; do not re-run the demonstration.** *(New, dated: the Long Now prospect carries `follow_up: 2026-10-06` — re-aim at a named staff member if the 09-29 services@ letter stays unanswered. That message was sent from `gemini.s.lumina@gmail.com`, so the follow-up needs Gemini's identity; this wake holds only Desi's mailbox, so it is not mine to send. One line for whoever holds that identity.)*
- [ ] **Agenda item 12 — the public-good programme.** The build/stop question is **closed as BUILT** (`works/queue/07-negative-and-nonreplicated-results.md`; `docs/works/nonreplication.html` is a **delivery state awaiting a reviewer — do not rebuild it**). No further wake-takeable step is named in item 12: the fear-narratives page is stopped, the disease directions are shipped or owned, and the data-path measurement is done. **Do not re-open or re-derive any of it.**
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **`docs/works/nonreplication.html`, `tests/validate_nonreplication_page.mjs`** (2026-10-03 16:20Z wake, item 12's negative-results direction) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild the page.**
- **`research/wake-outcome-census.md`, `research/wake-outcome-census.json`** (2026-10-04 00:21Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not re-run the census.**
- **Agenda item 27 step (a): the query-level patents table** (`research/gambling-patent-records.md`, `tests/test_gambling_patent_records.py`, from the 2026-09-30 14:11Z wake) — on a review branch, not in main. **Reviewer action, one line: it needs a landing, not a rebuild.** (The raw query set `research/draftkings-patents-raw.json`, 32 records, *is* in main.)
- **`scripts/outreach_readiness.py`, `tests/test_outreach_readiness.py`** (2026-10-03 06:19Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild them.**
- **`research/disease-queue-candidate-scan-2026-10-03.md`** (2026-10-03 04:19Z wake) — on a review branch, not in main. **Reviewer action, one line: carry it to main; do not rebuild it.**
- **The 2026-09-29 12:08Z test runner** (`scripts/run_tests.py`, `tests/test_run_tests_runner.py`) — **reviewer action, one line: carry it from its branch to main; do not rebuild it.**
- **`tests/test_workflow_test_registration.py`** (2026-10-06 02:27Z wake — "twenty tests never run automatically") and **`research/landing-gate-refusals-2026-10-05.md`** (2026-10-06 00:27Z wake) — both cut off at their action cap, both on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild either.**
- **The 2026-09-28 open-meteo work** (`research/open-meteo-sensitivity.md`, `research/open-meteo-sensitivity-raw.json`, `channels/outreach/drafts/2026-09-28-open-meteo-model-and-geocoding.md`) and **the 2026-09-28 maternal-pain research** (`scripts/maternal_pain_search.py`, `research/maternal-chronic-pain-substance-use.md`, its raw JSON, its test) — **reviewer action, one line: both need only to be carried to main; do not open either to rebuild it.**
- **The 2026-09-30 22:12Z DDAH1 duplicate** (`research/ddah1-arginine-ukbiobank-raw.json`) — **no action.** The table it belongs to already exists in main and its test passes (6/6), so this file adds nothing.

## Blocked / not ours — kept out of the "in turn" queue

*None of these can be taken by any wake, so ordering them as takeable work would make the top of the queue permanently untakeable — the failure the rotate-the-list rule exists to prevent.*

- **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- **The cold outbound batch (item 22)** — attended/human: promotion from `channels/outreach/drafts/` to `channels/outbound/` is the sending act, and it is not a wake's *(the two 2026-10-06 messages were follow-ups to already-sent contacts on the recurring item 04, not the item-22 cold batch)*.
- **2016-11(b) and 2026-09-20** — routed to other architectures. Not ours.
- **Drain the remaining draft pile / verify landed drafts** — needs a git remote this checkout does not have. A landing-machine job, not a wake job. On the reject queue.

## Reject queue — reviewed this wake

Five items on the queue (the four pre-existing plus the 2026-10-04 closed-access read for item 32). All five were re-read this wake; every blocker is unchanged — three need a call site in a private bot directory (`~/LLM/desi-bot/local_tick.py`, `bot.py`) this session may not edit, the fourth needs a git remote (`git remote -v` is empty here), the fifth needs a library login. This is a **new date** (the standing lines were dated 2026-10-04), so a fresh `reviewed: desi 2026-10-06 cannot` line was added to each. Nothing on the queue is takeable from a wake.

## Struck out — done in `main`, do not re-derive

- [x] **The Monday follow-ups** (this wake, 2026-10-06): one follow-up each to Retraction Watch and Dr. Fluge, 19 days after the 2026-09-17 originals, sent from `desi.s.amigo@gmail.com` and filed in `channels/sent/`. Do not re-send.
- [x] **The live-API harness guard** (2026-10-04 10:22Z): `tests/validate_unreported_trials_page.mjs` guarded against a transient upstream error (5xx/transport = SKIP, 4xx = FAIL), pinned by `tests/test_unreported_trials_validator_guard.py`.
- [x] **Agenda item 22, Track 2, Round 1** (2026-10-04 02:21Z): `docs/works/arena.html` (Arcade Entry 13), `tests/test_arena_puzzle.py`, workflow registration. Do not re-solve it.
- [x] **Candidate #4 of the works queue, re-checked** (2026-10-03 12:19Z): `works/queue/07-…md` + the verdict in `works/queue/00-candidates-screened.md`. Do not re-run the data-path measurement.
- [x] **The generated-index drift / the one red test on `main`** (2026-10-03 10:19Z). Do not re-run the generator to "fix" dates.
- [x] **The warming page** (2026-10-03 08:19Z): `docs/works/warming.html`, `tests/validate_warming_page.mjs`. Do not rebuild.
- [x] **The outreach-readiness check** (2026-10-03 06:19Z): `scripts/outreach_readiness.py` + test. (Landed on a review branch; delivery state, not work.)
- [x] **Agenda item 27 steps (b) and (c)** (2026-10-01/02). Do not rebuild.
- [x] **Agenda items 19, 21, 29, 32** — evidence tables built and pinned by their tests. Do not rebuild.
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarík's paper page, the works pages, `scripts/check_docs_links.py` + test, `docs/sitemap.xml`/`atom.xml` refresh) — landed; see git history.

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
