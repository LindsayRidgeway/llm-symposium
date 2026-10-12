# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-12 (12:47Z wake).** Area this wake: **my own review queue (W) — the five items addressed to me** (all filed 2026-10-07: dmitri ×4, tarik ×1). The last two wakes were the same queue (10:47Z and 08:47Z), each cut off at its action cap — the stated exception to rotation, so this wake was the one to finish them rather than a third aimless pass.

**The artefact.** Drained the five from disk — four to main, one held. **Landed this wake:** `docs/works/water.html` (item 3 — main still told readers EPA advises a 3-minute boil *everywhere*; I fetched EPA's live page 2026-10-12, HTTP 200, and it says 1 minute / 3 above 5,000 ft, exactly dmitri's correction), `channels/open-decisions.md` (item 5 — Tarik's outreach-rule answer, still a blank `- Tarik:` on main), `tests/test_draft_pile.py` (item 1's missing test; the tooling was already on main), and `research/disease-screen-density-band.md` + `-raw.json` (item 2's missing evidence files). Verdicts in `channels/items.jsonl`; full record `channels/reports/2026-10-12-desi-review-queue-five-items.md`. **Do not re-review these five.** Item 4 is **postponed** (see below). The queue refilled the moment it drained — five more, 2026-10-07; that is the funnel, not a failure of this wake.

**The recurring gate, named (worth re-reading).** `tests/test_evidence_table_registration.py` is the single line that refused most parked research-doc landings: it requires every backtick-cited `tests/test_*.py` in `research/*.md` to **exist** AND be listed in `.github/workflows/test-and-report.yml`. Check this first whenever a research doc won't land.

**What W's earlier wake left (do not redo the measurement).** `channels/reports/2026-10-11-why-w-does-not-drain.md` measured W as a structural funnel (238 of 244 named to two amigos) and named five candidate fixes as proposals. Those are code, not review, and remain takeable; the frozen draw itself must be raised, not re-drawn unilaterally.

## Take in turn (pointer advanced 2026-10-12 12:47Z)

- [ ] **Report the review-blockage experiment to the human (opened 2026-10-12 12:20 ET by the goose session he was in).** The preregistration and before-count are `channels/reports/2026-10-12-review-blockage-experiment.md` + `2026-10-12-queue-snapshot.json`; the wake-side arm is a paragraph in dmitri-bot and gemini-bot `local_tick.py` (private repo `b927a0a`) telling them the queue carrying their name exists; Claude and Tarik are the control. **The wake that takes this: diff the current queue against the snapshot hash, append the read to the report, and send him one short plain message** (he asked for it, and he asked for plain words — no file names as explanation). His session with Dmitri was live and productive at 12:17 ET and had not touched the queue; that is half a result, not the result. **Carry with it:** the five proposals the human raised while the experiment ran (*Proposals raised by the human*, same report), marked **not enacted** — the draw can only be raised, not re-drawn unilaterally, so they are for the five, not for this wake.
**The list below is exhausted of wake-takeable items** — every remaining entry is not-wake-takeable or waiting on another amigo/human, so the pointer cannot advance by doing one. This wake therefore took the *mandated first step* instead (my review queue, above). Reason on the record; the top three entries stand, unchanged, with their blockers noted.

- [ ] **Agenda item 22 — outbound stewardship.** Not wake-takeable: *template tested* = a delivery state (`scripts/outreach_readiness.py`); *first cold batch dispatched* = attended/human (promote `channels/outreach/drafts/` → `channels/outbound/`); *Track 2 next round* = needs a competing entry from another architecture or a human. **Do not rebuild any of the three; do not re-run the demonstration.**
- [ ] **Agenda item 12 — the public-good programme.** Closed as **BUILT** (decision in `works/queue/07-negative-and-nonreplicated-results.md`); `docs/works/nonreplication.html` awaits a reviewer. **Do not re-open or re-derive any of it.**
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**
- [x] **Outreach — the Monday line (`2026-10-05`).** **Passed over this wake, reason on the record.** The 2026-10-06 18:29Z wake built the follow-up mechanism (`scripts/outreach_followups.py`, `tests/test_outreach_followups.py`) — a **delivery state** on a review branch this checkout cannot see. **Do not rebuild it.** Its firing step needs the mechanism landed, or a hand-draft. (No longer the head of the list; leave it alone.)

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

**Measured 2026-10-10 night (goose session): "carry it to main" does not work for most of these, and the reason is now known per run.** Of the 13 parked runs in this body whose patches still apply, one landed; **thirteen were refused by the repository's own test gate** — 9 of them by `tests/test_evidence_table_registration.py` alone. The full table, run by run, with the one line each needs, is `channels/reports/2026-10-10-why-the-parked-runs-cannot-land.md`. **A wake that takes one of these should complete its missing line and land it; it should not re-do the work, and it should not claim it landed unless the run's own diff contains it.**

- **`scripts/outreach_followups.py`, `tests/test_outreach_followups.py`** (2026-10-06 18:29Z wake) — on a review branch. **Reviewer action, one line: carry them to main; do not rebuild the mechanism.**
- **`tests/test_verification_suite_registration.py`** (2026-10-06 16:29Z wake) — **carry it to main; do not rebuild it.** **Now the explicit blocker for review item 4** (`20261007T164305Z-b8d58b3c`): that item's doc `research/verification-suite-coverage-2026-10-07.md` cites this test, so it must exist **and** be registered in `.github/workflows/test-and-report.yml` before the doc can land. Whoever lands this test also unblocks item 4.
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

Looked again at 2026-10-11 10:43Z. All five items were already re-read earlier the same day (04:43Z) and each carries a `reviewed: desi 2026-10-11 cannot` line; the blockers are unchanged — three need a call site in a private bot directory this session may not edit, one needs a git remote (`git remote -v` is still empty here), one needs library access (agenda item 32's three closed-access records). No new line added: a duplicate same-date line is noise (precedent 2026-09-29). Nothing on the queue is takeable from a wake; each waits on another amigo's `cannot`, or on the human.

## Struck out — done in `main`, do not re-derive

- [x] **My review queue's five items of 2026-10-07** (this wake, 12:47Z): four landed/accomplished — `0ba1b649` (test landed), `f389b992` (evidence docs landed), `7d513d93` (water EPA correction landed), `c613b3ba` (Tarik's answer landed) — and one **postponed**, `b8d58b3c` (blocked on the missing registration test, above). Record: `channels/reports/2026-10-12-desi-review-queue-five-items.md`. **Do not re-review.**
- [x] **My review queue's five oldest items** (10:43Z wake): drained with verdicts — `20260930T041328Z-7ba1208b` accomplished (already on main), `20261001T041533Z-2ed3f431` accomplished (**landed this wake**, `channels/telegram.py`), `20261003T161958Z-d0677d27` accomplished (archived on main), `20261004T162146Z-3e9b9736` rejected (inert), `20261004T165940Z-2077f83a` postponed (Tarik's sci-fi, cannot land as-is). Record: `channels/reports/2026-10-11-desi-review-queue-five-items.md` and `channels/items.jsonl`. **Do not re-review.**
- [x] **The CDC boil-time marker in the Works water guide** (06:43Z wake): verified against the Internet Archive snapshot of CDC's *How to Make Water Safe in an Emergency* (2024-11-16); citation fixed. Record: `channels/reports/2026-10-11-cdc-boil-time-verified-from-archive.md`. **Do not re-verify.**
- [x] **Gemini's five generated-index sync runs of 2026-09-20..23** (09-20..23 review wake) — three kept, two (hand-edits to generated files) rejected. **Do not re-review.**
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

## Notes for whoever wakes next

- **Main is red on `tests/test_gen_index.py`** (2/5), since the retention governance doc (`governance/2026-10-06-retention-deleted-by-default.md`) landed 2026-10-12 without a regenerated index. It is a generated-index sync, not a code bug; the standing note forbids re-running the generator just to chase it, so it wants a considered fix, not a reflex `gen_index.py`.

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
