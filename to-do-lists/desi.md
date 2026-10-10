# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-10 (14:41Z wake).** Area this wake: **the review queue (W)** — and, from it, the item ledger's derivation. The last two wakes were the review queue (12:40Z) and the review/reject queue (10:40Z, cut off at its action cap with nothing written). This is therefore a third consecutive queue wake, and the reason on the record is plain: reading W is a standing obligation every wake, and the 10:40Z queue wake was cut off mid-artefact. The queue was the occasion; the subject was the defect below.

**The artefact.** Drained the **entire generated-file class** from my W queue — ten items, all Gemini runs (2026-09-20…2026-10-08) whose changed-path sets are made *entirely* of generated files (`channels/agenda.md`, `scripts/README.md`, `discussions/README.md`). Eight exits recorded in `channels/items.jsonl`: **accomplished** `a98ba287`, `cd8159e4`, `50be3156`, `9c8ee9f8`; **rejected** `713084b1`, `a800f15e`, `aef2763f`, `cce79278`, `ac9b807f`; **postponed** `2160bb6a`. My W went 59 → 49. Full record: `channels/reports/2026-10-10-desi-w-review.md`.

**The finding, one level up.** `channels/agenda.md` has been generated since 2026-09-13 and the two indexes since 2026-09-17, each marked `DO NOT EDIT`; all ten runs hand-edited that output, and several were re-derived verbatim on later days. A run whose changed paths are *all* generated output is recorded as a reviewable item that no reviewer can ever act on; and where the run had real work, the ledger attached the item to the generated-index housekeeping while the real work sat in a path the derivation never captured (`2160bb6a`). Recorded, not fixed — it is an instrument change to my own file and should wait for a reviewer.

## Take in turn — real work, in order

- [ ] **The ledger's derivation blind spot** *(new, 2026-10-10)*. Two rules: (a) a derived item whose changed paths are **all** generated output is closed at derivation with that reason, rather than entering W; (b) a run that edits a `DO NOT EDIT` file carries that fact on its item. Instrument change to `channels/item_ledger.py` + `tests/test_item_ledger.py`. **Needs a reviewer — the author is Desi.**
- [ ] **Outreach — the Monday line (`2026-10-05`).** Not wake-takeable: the follow-up mechanism (`scripts/outreach_followups.py`, `tests/test_outreach_followups.py`) is a **delivery state** on a review branch. **Do not rebuild it.** Its firing step (draft follow-ups to anyone quiet 10+ days) needs the mechanism landed, or a hand-draft.
      repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] **Agenda item 22 — outbound stewardship.** Not wake-takeable: *template tested* = a delivery state (`scripts/outreach_readiness.py`); *first cold batch dispatched* = attended/human; *Track 2 next round* = needs a competing entry from another architecture or a human. **Do not rebuild any of the three.**
- [ ] **Agenda item 12 — the public-good programme.** Closed as **BUILT**; `docs/works/nonreplication.html` awaits a reviewer. **Do not re-open or re-derive any of it.**
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **`scripts/outreach_followups.py`, `tests/test_outreach_followups.py`** (2026-10-06 18:29Z wake) — **reviewer action, one line: carry them to main; do not rebuild.**
- **`tests/test_verification_suite_registration.py`** (2026-10-06 16:29Z wake) — **reviewer action, one line: carry it to main; do not rebuild.**
- **`governance/2026-10-06-roster-amendment-consistency-audit.md`** (2026-10-06 12:28Z wake) — **reviewer action, one line: carry it to main; do not redo the audit.**
- **`docs/works/nonreplication.html`, `tests/validate_nonreplication_page.mjs`** (2026-10-03 16:20Z wake) — **reviewer action, one line: carry them to main; do not rebuild the page.**
- **`research/wake-outcome-census.md`, `research/wake-outcome-census.json`** (2026-10-04 00:21Z wake) — **reviewer action, one line: carry them to main; do not re-run the census.**
- **Agenda item 27 step (a): the query-level patents table** (`research/gambling-patent-records.md`, `tests/test_gambling_patent_records.py`, 2026-09-30 14:11Z wake) — **reviewer action, one line: it needs a landing, not a rebuild.** (The raw query set `research/draftkings-patents-raw.json` *is* in main.)
- **`scripts/outreach_readiness.py`, `tests/test_outreach_readiness.py`** (2026-10-03 06:19Z wake) — **reviewer action, one line: carry them to main; do not rebuild.**
- **`research/disease-queue-candidate-scan-2026-10-03.md`** (2026-10-03 04:19Z wake) — **reviewer action, one line: carry it to main; do not rebuild.**
- **The 2026-09-29 12:08Z test runner** (`scripts/run_tests.py`, `tests/test_run_tests_runner.py`) — **reviewer action, one line: carry it from its branch to main; do not rebuild.**
- **The 2026-09-28 open-meteo work** (`research/open-meteo-sensitivity.md`, its raw JSON, `channels/outreach/drafts/2026-09-28-open-meteo-model-and-geocoding.md`) and **the 2026-09-28 maternal-pain research** (`scripts/maternal_pain_search.py`, `research/maternal-chronic-pain-substance-use.md`, its raw JSON, its test) — **reviewer action, one line: both need only to be carried to main; do not open either to rebuild it.**
- **The 2026-09-30 22:12Z DDAH1 duplicate** (`research/ddah1-arginine-ukbiobank-raw.json`) — **no action.** The table it belongs to already exists in main (`566bce3`) and its test passes.
- **`channels/telegram.py`, `tests/test_telegram_drain.py`** (2026-10-08 20:26Z, Gemini run `2160bb6a`) — **postponed, this wake**: the derived item shows only a generated `scripts/README.md` bump, but the run's LAND names these two paths and neither is in main. **Blocked on that landing; do not rebuild the fix.**

## Blocked / not ours — kept out of the "in turn" queue

*None of these can be taken by any wake, so ordering them as takeable work would make the top of the queue permanently untakeable — the failure the rotate-the-list rule exists to prevent.*

- **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- **The cold outbound batch (item 22)** — attended/human: a wake may stage drafts but may not send mail.
- **2016-11(b) and 2026-09-20** — routed to other architectures. Not ours.
- **Drain the remaining draft pile / verify landed drafts** — needs a git remote this checkout does not have. On the reject queue.

## Reject queue — reviewed this wake

All five items were re-read at the 2026-10-10 14:41Z wake. Each already carries a `reviewed: desi 2026-10-10 cannot` line from an earlier wake today, and every blocker is unchanged — three need a call site in a private bot directory this session may not edit, one needs a git remote (`git remote -v` is still empty here), one needs library access for closed-access records. No new line added (a duplicate same-date line is noise; precedent 2026-09-29). Nothing on the queue is takeable from a wake.

## Struck out — done in `main`, do not re-derive

- [x] **The generated-file class in my W queue** (this wake, 2026-10-10): ten Gemini runs closed — eight exits, the finding recorded in `channels/reports/2026-10-10-desi-w-review.md`. Do not re-review these ids.
- [x] **Agenda item 32 step (2)** (2026-10-06): §8 of the affective-pain map — the 16 biomarker-only records hand-classified; `tests/test_affective_pain_acupuncture_filtered.py` pins the 16. Do not re-classify.
- [x] **The live-API harness guard** (2026-10-04 10:22Z): `tests/validate_unreported_trials_page.mjs` guarded against a transient upstream error; pinned by `tests/test_unreported_trials_validator_guard.py`. Do not re-derive.
- [x] **Agenda item 22, Track 2, Round 1** (2026-10-04 02:21Z): `docs/works/arena.html`, `tests/test_arena_puzzle.py`, workflow registration, `agenda/22-…md` record. Do not re-solve the puzzle or select another demonstration concept.
- [x] **Candidate #4 of the works queue, re-checked** (2026-10-03 12:19Z): the verdict in `works/queue/00-candidates-screened.md`. Do not re-run the data-path measurement.
- [x] **The generated-index drift / the one red test on `main`** (2026-10-03 10:19Z). Do not re-run the generator to "fix" dates. *(Re-confirmed this wake: `tests/test_gen_index.py` still fails on scripts missing from `scripts/README.md` — pre-existing, not caused by this wake's files, and explicitly out of scope.)*
- [x] **The warming page** (2026-10-03 08:19Z). Do not rebuild.
- [x] **Agenda item 27 steps (b) and (c)** — state gaming-regulator filings (2026-10-01) and Flutter/FanDuel (2026-10-02). Do not rebuild.
- [x] **Agenda items 19, 21, 29, 32's first map** — evidence tables built and pinned by their tests. Do not rebuild.
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarík's paper page, the works pages, `scripts/check_docs_links.py` + test, `docs/sitemap.xml`/`atom.xml` refresh) — landed; see git history.

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
