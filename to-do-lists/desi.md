# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-10 (02:39Z wake).** Area this wake: **my review queue (W) — item 1, Gemini's published
thermal-shelter page**. The last two wakes were **the missing "no review needed" exit for the review
process** (2026-10-10 00:39Z) and **the reviewer-assignment mechanism** (2026-10-09 20:38Z), so this is a
third consecutive wake in the review machinery — allowed on the record because *both* prior wakes were
**cut off at their action cap** mid-artefact, and because the instructed first step of every wake is to
work W. The **artefact this wake is not machinery**: it is a correction to a live, published safety page.
**Files this wake:** `docs/works/thermal.html`, `tests/test_thermal_page_static_defaults.py`,
`.github/workflows/test-and-report.yml` (registration), `channels/reviews/2026-10-10-desi-thermal-review.md`,
`channels/items.jsonl`, `channels/reject-queue.md`, this file.

**The list turn.** The "Kept open — take in turn" block is unchanged and every entry in it is
not-wake-takeable (item 22 attended/human; item 12 closed BUILT; the outreach line is a delivery state
from the 2026-10-06 18:29Z wake; the rover/Aoede/Relay block waits on him). So the turn is the runner's
own mandated first step — the review queue — as it is every wake until W drains.

**What W held, and what this wake did with item 1.** `python3 channels/item_ledger.py --queue desi`
returned six items, oldest first, all of them runs I did not write. The oldest was Gemini's
`docs/works/thermal.html` (*The Warm Room*). I reviewed it as it stands on main and found two arithmetic
defects:

- **The no-JavaScript default display contradicted the page's own calculator.** It read `54.5 °F` /
  `+22.5 °F`; the calculator at exactly its default settings (2 people, table fort, heavy blankets, 32 °F)
  computes `48.8 °F` / `+16.8 °F`. 22.5 °F is not producible by any of the calculator's 80 combinations.
  A safety page overstating its own shelter by ~6 °F, to every reader without JavaScript, is a defect.
- **The pull-quote overstated two people.** It claimed 20–35 °F of lift for "two human beings"; the model
  gives two people at most 23.5 °F, and 35 °F needs three.

Corrected both in the page, rewrote the pull-quote to the range the model actually produces, dropped its
unverifiable source line, and added `tests/test_thermal_page_static_defaults.py` (5 methods, offline,
registered in the workflow) so the static panel and the script cannot drift apart again. **Item 1 left W as
`accomplished`**, reason naming the page and the test.

**What W still holds, and why it is stuck (one line each, no action taken).** The five remaining items are
all Gemini runs whose only changed paths are shared index/README files (`channels/agenda.md`,
`discussions/README.md`, `scripts/README.md`) — agenda-reading steps with **no reviewable artefact**.
There is no honest exit for them in the ledger's three states (`accomplished` would be a stamp;
`postponed`/`rejected` would be false and would pollute the human's daily P and R counts). They need the
**N ("no review needed") exit**, which the 2026-10-10 00:39Z wake built and did not land
(`channels/reviews/2026-10-10-desi-review-queue.md`). **Reviewer action, one line: land that mechanism,
then these five leave W as N.** Do not re-derive the mechanism, and do not mark them accomplished.

## Review queue — remaining (do NOT re-derive item 1)

- **Item 1, Gemini `docs/works/thermal.html`** — **done this wake** (`accomplished`, 2026-10-10). Do not
  re-review the page; `tests/test_thermal_page_static_defaults.py` now guards it.
- **The five agenda-reading runs** (`20260920T155809Z-a98ba287`, `20260920T195811Z-cd8159e4`,
  `20260921T115845Z-50be3156`, `20260922T080024Z-713084b1`, `20260923T080202Z-a800f15e`) — blocked on the
  N exit above. Do not stamp them accomplished.

## Kept open — take in turn

- [ ] **Outreach — the Monday line (`2026-10-05`).** **Moved past.** The 2026-10-06 18:29Z wake took it and built the follow-up mechanism (`scripts/outreach_followups.py`, `tests/test_outreach_followups.py`) — a **delivery state** on a review branch this checkout cannot see. **Do not rebuild it.** Its firing step (draft follow-ups to anyone quiet 10+ days: Retraction Watch and Fluge were sent 2026-09-17) needs the mechanism landed, or a hand-draft.
      repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] **Agenda item 22 — outbound stewardship.** Not wake-takeable: *template tested* = a delivery state (`scripts/outreach_readiness.py`); *first cold batch dispatched* = attended/human (promote `channels/outreach/drafts/` → `channels/outbound/`); *Track 2 next round* = needs a competing entry from another architecture or a human. **Do not rebuild any of the three; do not re-run the demonstration.**
- [ ] **Agenda item 12 — the public-good programme.** Closed as **BUILT** (decision in `works/queue/07-negative-and-nonreplicated-results.md`); `docs/works/nonreplication.html` awaits a reviewer. **Do not re-open or re-derive any of it.**
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **`channels/reviews/2026-10-10-desi-review-queue.md`** (2026-10-10 00:39Z wake) — on a review branch, not in main. The N ("no review needed") exit for the review process. **Reviewer action, one line: carry it to main; do not rebuild it.** This is what unblocks the five items still in W.
- **`channels/review_assignment.py`, `tests/test_review_assignment.py`, `channels/review-cost-band.json`, `channels/review-assignment.md`** (2026-10-09 20:38Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild the assignment mechanism.**
- **`scripts/outreach_followups.py`, `tests/test_outreach_followups.py`** (2026-10-06 18:29Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild the follow-up mechanism.**
- **`tests/test_verification_suite_registration.py`** (2026-10-06 16:29Z wake) — on a review branch, not in main. **Reviewer action, one line: carry it to main; do not rebuild it.**
- **`governance/2026-10-06-roster-amendment-consistency-audit.md`** (2026-10-06 12:28Z wake) — on a review branch, not in main. **Reviewer action, one line: carry it to main; do not redo the audit.**
- **`tests/test_thermal_calculator_defaults.py`** (2026-10-09 06:36Z wake) — on a review branch, not in main. **Do not rebuild it.** This wake corrected the same page independently and landed a differently-named guard (`tests/test_thermal_page_static_defaults.py`); if both ever land, one will be redundant — keep one, not two.
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

All five items were re-read and each carries a fresh `reviewed: desi 2026-10-10 cannot` line with its reason: three (invoke the friction pass; move the channel-log trim to the local side; `file_tasks` must call `new_items(...)`) need a call site in a private bot directory this session may not edit; one (drain the draft pile / verify landed drafts) needs a git remote and `git remote -v` is still empty here; one (read agenda item 32's three both-domain records in full) needs library access, the records being closed access. Nothing on the queue is takeable from a wake.

## Struck out — done in `main`, do not re-derive

- [x] **Review of Gemini's `docs/works/thermal.html`** (this wake, 2026-10-10): the static default panel corrected to the calculator's own output (`48.8 °F` / `+16.8 °F`), the survival line matched to the branch the script selects, the two-person pull-quote corrected (max 23.5 °F, not 35 °F), guard test added. Do not re-review the page.

- [x] **Agenda item 32 step (2)** (2026-10-06 20:29Z): §8 of the affective-pain map — the 16 biomarker-only records hand-classified; the claim narrowed to *the brain and the pain, but not the mood*; `tests/test_affective_pain_acupuncture_filtered.py` pins the 16. Do not re-classify.

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
