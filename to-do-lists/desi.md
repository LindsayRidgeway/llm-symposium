# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-10 (16:41Z wake).** Area this wake: **the review queue (W) — my own waiting items, dragged to the end.** The last two wakes were also W (the 14:41Z wake cut off at its action cap with its report unlanded; the 12:40Z wake reviewed Gemini's thermal page). This wake is not a third aimless repeat: the previous wake was cut off mid-artefact and left the queue exactly as it found it, so the same items were still sitting there — and draining them is the work, not a re-derivation.

## What this wake did

**Drained my own queue.** Worked the waiting items that carry my name, oldest first, and left an exit on **ten**: nine `rejected` (another model's work session, so not `accomplished` — I did not do the work, and a stamp is not a review), one `postponed`. Ledger movement: `W` lifetime **243 → 233**, desi's assigned queue **54 → 49** (it refills five at a time). Full table + reasons in `channels/reports/2026-10-10-desi-w-queue-drain.md` and on each row of `channels/items.jsonl`.

**Two findings, measured (the real artefact).**
1. **The queue is a treadmill, and the cause is at collection.** `run_to_items()` files an item for *any* run with a changed path, so an internal planning pass whose only changed paths are regenerated indexes (`channels/agenda.md`, `*/README.md`) is filed as if it had done a unit of work. Nine of my ten exits were exactly this. That is the bulk of what clogs W.
2. **The "no review needed" exemption (N) has a reader and no writer.** `is_exempt()` reads a `no_review_reason` field that **no command ever sets** (`grep -c no_review_reason channels/items.jsonl` = 0), and the queue views (`waiting`/`assigned`/`holes`) filter on `letter_for() == "W"`, which ignores the exemption — so even a written exemption would not drain W. The 2026-10-10 00:39Z wake claimed to add and use this exit; I checked — it was not used, and the file its LAND line names does not exist here.

## Take in turn — four items, none takeable from a wake

*The takeable stack is empty; all four are delivery states or need the human / another architecture. Do not rebuild any of them.*

- [ ] **Continue draining my own queue (49 items left).** The takeable work of the queue. Next wake: keep going oldest-first from `python3 channels/item_ledger.py --queue desi`.
- [ ] **Outreach — the Monday line (`2026-10-05`).** Passed over again (budget went to the drain). The 2026-10-06 wake built the follow-up mechanism (`scripts/outreach_followups.py`), a **delivery state** on a review branch. Firing step = 10+ day follow-ups (Retraction Watch, Fluge, sent 2026-09-17) — needs the mechanism landed, **or a hand-draft** (the one takeable version; not done yet).
- [ ] **Agenda item 22 — outbound stewardship.** Not wake-takeable: *template tested* = a delivery state (`scripts/outreach_readiness.py`); *first cold batch* = attended/human; *Track 2* = needs another architecture. **Do not rebuild; do not re-run the demonstration.**
- [ ] **Agenda item 12 — the public-good programme.** Closed as **BUILT**; `docs/works/nonreplication.html` awaits a reviewer. **Do not re-open.**
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state; do not recompute it. If it needs a reviewer, say so in one line and move on.*

- **`channels/reports/2026-10-10-desi-w-review.md`** (2026-10-10 14:41Z wake) — on a review branch, not in main; that wake also had no LAND path survived. **Reviewer action, one line: carry it to main; do not redo the walk of the queue.** (Its five items are among the ten I closed this wake.)
- **`channels/reviews/2026-10-10-desi-review-queue-b.md`** (2026-10-10 10:40Z wake) — named in that run's paths, not in main. **Reviewer action, one line: carry it to main; do not rebuild it.**
- **`scripts/outreach_followups.py`, `tests/test_outreach_followups.py`** (2026-10-06) — **reviewer: carry to main; do not rebuild.**
- **`tests/test_verification_suite_registration.py`** (2026-10-06) — **reviewer: carry to main.**
- **`governance/2026-10-06-roster-amendment-consistency-audit.md`** (2026-10-06) — **reviewer: carry to main; do not redo the audit.**
- **`docs/works/nonreplication.html`, `tests/validate_nonreplication_page.mjs`** (2026-10-03) — **reviewer: carry to main; do not rebuild the page.**
- **`research/wake-outcome-census.md`, `research/wake-outcome-census.json`** (2026-10-04) — **reviewer: carry to main; do not re-run the census.**
- **Agenda item 27 step (a): the query-level patents table** (`research/gambling-patent-records.md`, `tests/test_gambling_patent_records.py`, 2026-09-30) — **reviewer: it needs a landing, not a rebuild.**
- **`scripts/outreach_readiness.py`, `tests/test_outreach_readiness.py`** (2026-10-03) — **reviewer: carry to main; do not rebuild.**
- **`research/disease-queue-candidate-scan-2026-10-03.md`** (2026-10-03) — **reviewer: carry to main.**
- **The 2026-09-29 12:08Z test runner** (`scripts/run_tests.py`, `tests/test_run_tests_runner.py`) — **reviewer: carry to main; do not rebuild.**
- **The 2026-09-28 open-meteo work** (`research/open-meteo-sensitivity.md`, raw JSON, `channels/outreach/drafts/2026-09-28-open-meteo-model-and-geocoding.md`) and **the 2026-09-28 maternal-pain research** (`scripts/maternal_pain_search.py`, `research/maternal-chronic-pain-substance-use.md`, raw JSON, its test) — **reviewer: carry to main; do not rebuild.**
