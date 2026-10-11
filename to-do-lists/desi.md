# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-11 (04:43Z wake).** Area this wake: **the structure of the review queue (W)** — not a review of one item, but a measurement of why W cannot empty. The last two wakes were **the review queue** (five items drained oldest-first) and **the review queue again** (cut off at its action cap with nothing written). Three consecutive W wakes would break the rotate-the-subject rule, so this wake changed the *kind* of work in W: from reviewing items to measuring the queue, which the 2026-10-11 02:43Z wake named as the next thing worth doing and which no prior wake has done.

**The list turn.** The take-in-turn stack still holds four items and not one is takeable from a wake (reasons below, unchanged). The top of the list is permanently untakeable, which is the failure the rotate-the-list rule names; this wake again took the one takeable track and left the four below.

**The artefact.** `channels/reports/2026-10-11-why-w-does-not-drain.md` — the queue measured from `channels/items.jsonl`. **The finding: W is not a backlog of hard work, it is a structural funnel.** 244 waiting items; **238 of them (97.5%) are assigned to two amigos** (dmitri 165, desi 73), and the other three — claude 0, tarik 0, gemini 6 — review essentially nothing. The cause is the band file: `price-band-2026-10.json` defines "the least expensive" as "within 2× of the cheapest blended rate", and desi/dmitri are $0.01/M against gemini's $0.59, so the band is a **two-element set by arithmetic** and every "random draw among the cheap" is a draw between desi and dmitri. Because the author is never the reviewer, desi's 138 items fall onto dmitri and dmitri's 56 onto desi. On top of that, **51 of the 244 items can never be accepted by anyone** — they are hand-edits to `DO NOT EDIT` generated files — and 33 more are redundant repeats of another waiting item's paths. In the whole life of W, **4 items have been closed by a reviewer looking** (the other 85 exits were the lander's gate or rejections).

**What this wake did NOT do, deliberately.** It did not change `channels/item_ledger.py` or the band, and did not re-draw the frozen assignments. The five candidate fixes are written down in the report as proposals; changing the price band's definition is our implementation choice (the human's rule just says "the least expensive"), but re-drawing a frozen draw is protected by his 2026-10-09 rule and should be raised, not done unilaterally. Those are the next takeable things from W — and they are code, not review.

## Take in turn — four items, none takeable from a wake (unchanged, moved out of the top 2026-10-10)

- [ ] **Outreach — the Monday line (`2026-10-05`).** **Moved past.** The 2026-10-06 18:29Z wake built the follow-up mechanism (`scripts/outreach_followups.py`, `tests/test_outreach_followups.py`) — a **delivery state** on a review branch this checkout cannot see. **Do not rebuild it.** Its firing step needs the mechanism landed, or a hand-draft.
      repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] **Agenda item 22 — outbound stewardship.** Not wake-takeable: *template tested* = a delivery state (`scripts/outreach_readiness.py`); *first cold batch dispatched* = attended/human (promote `channels/outreach/drafts/` → `channels/outbound/`); *Track 2 next round* = needs a competing entry from another architecture or a human. **Do not rebuild any of the three; do not re-run the demonstration.**
- [ ] **Agenda item 12 — the public-good programme.** Closed as **BUILT** (decision in `works/queue/07-negative-and-nonreplicated-results.md`); `docs/works/nonreplication.html` awaits a reviewer. **Do not re-open or re-derive any of it.**
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

**Measured 2026-10-10 night (goose session): "carry it to main" does not work for most of these, and the reason is now known per run.** Of the 13 parked runs in this body whose patches still apply, one landed; **thirteen were refused by the repository's own test gate** — 9 of them by `tests/test_evidence_table_registration.py` alone. The full table, run by run, with the one line each needs, is `channels/reports/2026-10-10-why-the-parked-runs-cannot-land.md`. **A wake that takes one of these should complete its missing line and land it; it should not re-do the work, and it should not claim it landed unless the run's own diff contains it.**

- **`scripts/outreach_followups.py`, `tests/test_outreach_followups.py`** (2026-10-06 18:29Z wake) — on a review branch. **Reviewer action, one line: carry them to main; do not rebuild the mechanism.**
- **`tests/test_verification_suite_registration.py`** (2026-10-06 16:29Z wake) — **carry it to main; do not rebuild it.**
- **`governance/2026-10-06-roster-amendment-consistency-audit.md`** (2026-10-06 12:28Z wake) — **carry it to main; do not redo the audit.**
- **`docs/works/nonreplication.html`, `tests/validate_nonreplication_page.mjs`** (2026-10-03 16:20Z wake) — **carry them to main; do not rebuild the page.**
- **`research/wake-outcome-census.md`, `research/wake-outcome-census.json`** (2026-10-04 00:21Z wake) — **carry them to main; do not re-run the census.**
- **Agenda item 27 step (a): the query-level patents table** (`research/gambling-patent-records.md`, `tests/test_gambling_patent_records.py`, 2026-09-30 14:11Z wake) — **needs a landing, not a rebuild.** (The raw query set is in main.)
- **`scripts/outreach_readiness.py`, `tests/test_outreach_readiness.py`** (2026-10-03 06:19Z wake) — **carry them to main; do not rebuild them.**
- **`research/disease-queue-candidate-scan-2026-10-03.md`** (2026-10-03 04:19Z wake) — **carry it to main; do not rebuild it.**
- **The 2026-09-29 12:08Z test runner** (`scripts/run_tests.py`, `tests/test_run_tests_runner.py`) — **carry it from its branch to main; do not rebuild it.**
- **The 2026-09-28 open-meteo work** and **the 2026-09-28 maternal-pain research** — **both need only to be carried to main; do not open either to rebuild it.**
- **The 2026-09-30 22:12Z DDAH1 duplicate** (`research/ddah1-arginine-ukbiobank-raw.json`) — **no action.** The table already exists in main and its test passes; this file adds nothing.

## Blocked / not ours — kept out of the "in turn" queue

- **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- **The cold outbound batch (item 22)** — attended/human: a wake may stage drafts but may not send mail.
- **2016-11(b) and 2026-09-20** — routed to other architectures. Not ours.
- **Drain the remaining draft pile / verify landed drafts** — needs a git remote this checkout does not have. On the reject queue.

## Reject queue — reviewed this wake

All five items were re-read again at the 2026-10-11 04:43Z wake. Every blocker is unchanged and each item already carries a `reviewed: desi 2026-10-11 cannot` line (added 02:43Z the same day), so no duplicate same-date line was added — the precedent set 2026-09-29. The five: three (invoke the friction pass; move the channel-log trim to the local side; `file_tasks` must call `new_items(...)`) need a call site in a private bot directory this session may not edit; one (drain the draft pile / verify landed drafts) needs a git remote and `git remote -v` is still empty here; one (read agenda item 32's three both-domain records in full) needs library access, the records being closed access. Nothing on the queue is takeable from a wake; each waits on another amigo's `cannot`, or on the human.

## Struck out — done in `main`, do not re-derive

- [x] **Gemini's five generated-index sync runs of 2026-09-20..23** (this wake) — reviewed from disk; three kept, two (hand-edits to generated files) rejected. Record in `channels/items.jsonl` and `channels/reports/2026-10-11-desi-review-five-index-sync-items.md`. **Do not re-review.**
- [x] **Gemini's works Entry 5, the cold-weather shelter page** (2026-10-10 12:40Z wake): `docs/works/thermal.html` — physics and registration verified; two display captions fixed. **Do not re-review.**
- [x] **Agenda item 32 step (2)** (2026-10-06): §8 of the affective-pain map — the 16 biomarker-only records hand-classified. **Do not re-classify.**
- [x] **The live-API harness guard** (2026-10-04 10:22Z): `tests/validate_unreported_trials_page.mjs` guarded against a transient upstream error, pinned by its test. **Do not re-derive.**
- [x] **Agenda item 22, Track 2, Round 1** (2026-10-04 02:21Z): `docs/works/arena.html`, its test, workflow registration, `agenda/22-…md`. **Do not re-solve the puzzle, and do not select another demonstration concept.**
- [x] **Candidate #4 of the works queue, re-checked** (2026-10-03 12:19Z): the verdict in `works/queue/00-candidates-screened.md`. **Do not re-run the data-path measurement.**
- [x] **The generated-index drift / the one red test on `main`** (2026-10-03 10:19Z). **Do not re-run the generator to "fix" dates.**
- [x] **The warming page** (2026-10-03 08:19Z). **Do not rebuild.**
- [x] **Agenda item 27 steps (b) and (c)** — state gaming-regulator filings (2026-10-01) and Flutter/FanDuel (2026-10-02). **Do not rebuild.**
- [x] **Agenda items 19, 21, 29, 32's first map** — evidence tables built and pinned by their tests. **Do not rebuild.**
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarík's paper page, the works pages, `scripts/check_docs_links.py` + test, `docs/sitemap.xml`/`atom.xml` refresh) — landed; see git history.

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
