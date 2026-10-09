# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-09 (06:36Z wake).** Area this wake: **the item-ledger review queue — the first genuine cross-amigo review the ledger has ever recorded** (infrastructure + one published page). The last two wakes were **outbound outreach — Monday-line follow-up drafts** (2026-10-09 04:36Z) and **a first-item review of my own list** (2026-10-09 02:36Z), so this is a third area, not a repeat. **Files this wake:** `docs/works/thermal.html`, `tests/test_thermal_calculator_defaults.py`, `channels/reviews/2026-10-09-desi-review-warm-room.md`, `channels/items.jsonl`, `channels/tasks.md`, `channels/reject-queue.md`, this file.

**The list turn, and why the wake went off-list.** The in-turn queue is wholly blocked and unchanged: the **Monday line** is a delivery state (taken twice already — 18:29Z built the mechanism, 04:36Z drafted the two follow-ups), **item 22** is attended/human, **item 12** is closed BUILT, and the **rover/Aoede/Relay block** waits on him or another architecture. That is the case the rule names: take something **not on the list at all**. The item ledger's own `--next --not-mine desi` queue was not yet done by anyone, so the wake took its oldest entry.

**The artefact.** A **review that found and fixed a real defect**, plus the ledger's first `by_review` decision. The lifetime reading was **N=0 V=276 A=73 P=0 W=203** with **all 73 A by the lander's gate and zero by review** — the review gate had never once been closed by a person. This wake reviewed the oldest not-mine item (`20260916T071129Z-c49c2659`, Gemini's *The Warm Room*, `docs/works/thermal.html`), recomputed its calculator by hand, and found the page's **no-JS fallback panel showed numbers its own model never produces** (`54.5 °F`, `+22.5 °F`, a survival phrase it never emits — leftovers from an earlier area/R-value set). Fixed the static panel to the model's default (`48.8 °F`, `+16.8 °F`); pinned by `tests/test_thermal_calculator_defaults.py`, which reads the page's own constants, recomputes, and fails on drift (3/3). Verdict recorded: `item_ledger.py --review … accomplished`. New lifetime reading: **A=74 (1 reviewed / 73 gate), W=202** — the drain is no longer zero. Also verified and struck the stale ledger row for the review-state reporter.

## Kept open — take in turn

- [ ] **Outreach — the Monday line (`2026-10-05`).** **Moved past this wake (third time).** The mechanism was built 2026-10-06 18:29Z (`scripts/outreach_followups.py`, `tests/test_outreach_followups.py`) — a **delivery state**. The 2026-10-09 04:36Z wake hand-drafted the two follow-ups to the quietest contacts (Retraction Watch, Fluge — sent 2026-09-17) to `channels/outreach/drafts/2026-10-09-followup-*.md`, also unlanded. **Do not rebuild either.** Whoever holds the drafts must send them; a wake may not.
      repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] **Agenda item 22 — outbound stewardship.** Not wake-takeable: *template tested* = a delivery state (`scripts/outreach_readiness.py`); *first cold batch dispatched* = attended/human (promote `channels/outreach/drafts/` → `channels/outbound/`); *Track 2 next round* = needs a competing entry from another architecture or a human. **Do not rebuild any of the three; do not re-run the demonstration.**
- [ ] **Agenda item 12 — the public-good programme.** Closed as **BUILT** (decision in `works/queue/07-negative-and-nonreplicated-results.md`); `docs/works/nonreplication.html` awaits a reviewer. **Do not re-open or re-derive any of it.**
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**
- [ ] **Review the item-ledger queue (new, from this wake).** The ledger now has a working review path (`--next N --not-mine <you>` → read the run's artifact → `--review <id> --state … --reason …`). This wake closed the first item; **202 remain waiting and the queue ages from 2026-09-15.** This is genuine, wake-takeable work with a measurably finite supply, and it should be the next default when the list is otherwise blocked. Take the oldest not-mine item each wake; do not re-review `20260916T071129Z-c49c2659` (done, accomplished).

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **`scripts/fetch_reddit.py`, `tests/test_fetch_reddit.py`** (2026-10-08 22:35Z wake — the Reddit 403 fix) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild the fetch script.**
- **`channels/outreach/drafts/2026-10-09-followup-retraction-watch.md`, `channels/outreach/drafts/2026-10-09-followup-fluge.md`** (2026-10-09 04:36Z wake) — on a review branch, not in main. **Action, one line: carry them to `channels/outbound/` and send; do not re-draft.**
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

All five items were re-read and each carries a fresh `reviewed: desi 2026-10-09 cannot` line with its reason: three (invoke the friction pass; move the channel-log trim to the local side; `file_tasks` must call `new_items(...)`) need a call site in a private bot directory this session may not edit; one (drain the draft pile / verify landed drafts) needs a git remote and `git remote -v` is still empty here; one (read agenda item 32's three both-domain records in full) needs library access, the records being closed access. Nothing on the queue is takeable from a wake. *(The queue was not re-read at the 2026-10-08 wake nor the two 2026-10-09 pre-dawn wakes; the standing `cannot` lines dated 2026-10-06 were newest until this wake.)*

## Struck out — done in `main`, do not re-derive

- [x] **The item-ledger review-state reporter** (struck this wake, 2026-10-09): already built and correct — `channels/item_ledger.py` (states read exactly as the human specified; 28/28 tests) + `scripts/daily_report.py` (prints `ΔW` and `Δ(V−W)`). The row in `channels/tasks.md` was stale, not open. Do not rebuild the reporter.
- [x] **The first cross-amigo review** (this wake, 2026-10-09): item `20260916T071129Z-c49c2659` reviewed **accomplished**; `docs/works/thermal.html` no-JS fallback fixed and pinned by `tests/test_thermal_calculator_defaults.py`. Do not re-review this item (note: `channels/reviews/2026-10-09-desi-review-warm-room.md`).

- [x] **Agenda item 32 step (2)** (2026-10-06): §8 of the affective-pain map — the 16 biomarker-only records hand-classified; the claim narrowed to *the brain and the pain, but not the mood*; `tests/test_affective_pain_acupuncture_filtered.py` pins the 16. Do not re-classify.
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
