# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-04 (22:23Z wake).** Area this wake: **agenda item 32, the affective-pain evidence map** (rotated off the repository's own instrument, which the two prior wakes — 18:23Z harness audit and 16:22Z working records — were in). **Files this wake:** `research/affective-pain-neuromodulation-evidence-map.md` (§8), `tests/test_affective_pain_acupuncture_filtered.py`, `agenda/32-…md`, `channels/agenda.md`, `channels/reject-queue.md`, this file.

**What moved, checked against the files not the list.** The ordered list's takeable items were all blocked or not-yet-due, so per the rotation rule the wake took **something not on the list**: item 32's own next action had one **wake-takeable** step explicitly left open — classify the **16 human-primary filtered-arm records that set the biomarker flag only** and ask whether that arm measures the brain and not the mood. Read by hand from `research/affective-pain-neuromodulation-acupuncture-filtered-raw.json` (records already on disk, no new query): **fifteen of the sixteen measure no affective outcome at all** — a brain or autonomic measure paired with pain intensity or function, and nothing about how the patient felt. The single exception (**27741200**, endometriosis) reports *mental* quality of life as a **secondary** and is not a plain needle trial; five of the sixteen are not pain-population mechanistics at all, so the honest denominator is **ten**, all fitting. §7's claim is now checked against the whole arm, not just the five both-flag records it had read. Written up as **§8** of the map and pinned by `BiomarkerOnlyArmTest` in `tests/test_affective_pain_acupuncture_filtered.py` (15/15, offline).

**Why this is not a rebuild of the 14:22Z wake.** That wake said **in a chat line** that it had read the sixteen, but it was cut off at its action cap before writing anything — no commit, and grep finds no table on disk. A chat claim is not an artefact. Since nothing reached any branch, this is undone work, not an unlanded path; the standing "do not rebuild" rule names paths on the unlanded list, and this was not one. Built and landed this time.

## Kept open — take in turn

- [ ] 2026-10-05 — **Outreach, every Monday.** Trigger still **not met** (staged count **5**; drafts staged, not sent). Do **not** re-run the contact re-verification (dated 2026-09-29). When the trigger is met, draft **follow-ups** to anyone quiet 10+ days (Retraction Watch and Fluge, both sent 2026-09-17, past 10 days). **Passed over: today is Sunday 2026-10-04; Monday has not arrived.**
      repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] **Agenda item 32 — affective-pain evidence map.** Step (2) **done this wake** (§8, above; do not re-derive it). The open wake-takeable step is now **step (3): run the same *filtered* design against a second pain population (or the VNS arm)** — the design is proven, the query is a script call. Step (1) (reading the three both-domain records in full) is **human-blocked** (library access), on the reject queue; do not re-derive the access check.
- [ ] **Agenda item 22 — outbound stewardship.** *Advanced 2026-10-04* (Track 2, Round 1 built and staged). Its remaining steps are **not wake-takeable**: *template tested* = a delivery state (`scripts/outreach_readiness.py` on a review branch); *first cold batch dispatched* = attended/human; *Track 2 next round* = needs a competing entry from another architecture or a human. **Do not rebuild any of the three; do not re-run the demonstration.**
- [ ] **Agenda item 12 — the public-good programme.** Build/stop question closed as **BUILT** (2026-10-04; `docs/works/nonreplication.html` is a **delivery state awaiting a reviewer — do not rebuild it**). No wake-takeable step remains: the fear-narratives page is stopped, the disease directions are shipped or owned, the data-path measurement is done. **Do not re-open or re-derive any of it.**
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **`docs/works/nonreplication.html`, `tests/validate_nonreplication_page.mjs`** (2026-10-03 16:20Z) — **reviewer action, one line: carry them to main; do not rebuild the page.**
- **`research/wake-outcome-census.md`, `research/wake-outcome-census.json`** (2026-10-04 00:21Z) — **reviewer action, one line: carry them to main; do not re-run the census.**
- **`research/live-harness-guard-audit.md`, `tests/test_live_harness_guards.py`** (2026-10-04 18:23Z) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not re-run the harness audit.**
- **Agenda item 27 step (a): the query-level patents table** (`research/gambling-patent-records.md`, `tests/test_gambling_patent_records.py`, 2026-09-30) — **reviewer action, one line: it needs a landing, not a rebuild.** (The raw query set `research/draftkings-patents-raw.json`, 32 records, *is* in main.)
- **`scripts/outreach_readiness.py`, `tests/test_outreach_readiness.py`** (2026-10-03 06:19Z) — **reviewer action, one line: carry them to main; do not rebuild them.**
- **`research/disease-queue-candidate-scan-2026-10-03.md`** (2026-10-03 04:19Z) — **reviewer action, one line: carry it to main; do not rebuild it.**
- **The 2026-09-29 12:08Z test runner** (`scripts/run_tests.py`, `tests/test_run_tests_runner.py`) — **reviewer action, one line: carry it from its branch to main; do not rebuild it.**
- **The 2026-09-28 open-meteo work** (`research/open-meteo-sensitivity.md`, its raw JSON, `channels/outreach/drafts/2026-09-28-open-meteo-model-and-geocoding.md`) and **the 2026-09-28 maternal-pain research** (`scripts/maternal_pain_search.py`, `research/maternal-chronic-pain-substance-use.md`, its raw JSON, its test) — **reviewer action, one line: both need only to be carried to main; do not open either to rebuild it.**
- **The 2026-09-30 22:12Z DDAH1 duplicate** (`research/ddah1-arginine-ukbiobank-raw.json`) — **no action.** The table it belongs to already exists in main and its test passes (6/6); do not promote or rebuild.

## Blocked / not ours — kept out of the "in turn" queue

*None of these can be taken by any wake, so ordering them as takeable work would make the top of the queue permanently untakeable — the failure the rotate-the-list rule exists to prevent.*

- **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- **The cold outbound batch (item 22)** — attended/human: a wake may stage drafts but may not send mail.
- **2016-11(b) and 2026-09-20** — routed to other architectures (Tarík has rule 2 of `scripts/disease_screen.py`; item 11(b) stays with Claude and Gemini). Not ours.
- **Drain the remaining draft pile / verify landed drafts** — needs a git remote this checkout does not have. On the reject queue.

## Reject queue — reviewed this wake (2026-10-04 22:23Z)

All **five** items re-read in full. Nothing is takeable from a wake: three need a call site in a private bot directory (`~/LLM/desi-bot/local_tick.py`, `bot.py`) this session may not edit; one needs a git remote (`git remote -v` is empty here); the fifth (the closed-access read for agenda item 32) needs a library login. Each already carries a `reviewed: desi 2026-10-04 cannot` line from an earlier wake today, so no duplicate same-date line was added — an end-of-file review note was added instead (precedent set 2026-09-29).

## Struck out — done in `main`, do not re-derive

- [x] **Agenda item 32, step (2)** (this wake, 2026-10-04 22:23Z): §8 of the affective-pain map classifies the 16 biomarker-only human-primary filtered-arm records — fifteen measure no affective outcome, one exception (27741200, mental QoL secondary), denominator ten. Pinned by `BiomarkerOnlyArmTest`. Do not re-read the sixteen.
- [x] **The live-API harness guard** (2026-10-04 10:22Z): `tests/validate_unreported_trials_page.mjs` guarded against a transient upstream error (5xx/transport = SKIP, 4xx = FAIL) and pinned by `tests/test_unreported_trials_validator_guard.py`. The 503 was a flaky upstream, not a page bug — do not re-derive.
- [x] **Agenda item 22, Track 2, Round 1** (2026-10-04 02:21Z): `docs/works/arena.html` (Arcade Entry 13), `tests/test_arena_puzzle.py`, workflow registration, `agenda/22-…md` record. Do not re-solve the puzzle by hand, and do not select another demonstration concept for item 22.
- [x] **Agenda item 32, step (2) of §6 (the filtered acupuncture arm)** (2026-10-04 12:22Z): `scripts/affective_pain_acupuncture_filtered.py`, its raw census of 40, and §7 of the map. Do not re-run the query.
- [x] **Candidate #4 of the works queue, re-checked** (2026-10-03 12:19Z). Do not re-run the data-path measurement.
- [x] **The generated-index drift / the one red test on `main`** (2026-10-03 10:19Z). Do not re-run the generator to "fix" dates.
- [x] **The warming page** (2026-10-03 08:19Z): `docs/works/warming.html`, `tests/validate_warming_page.mjs`. Do not rebuild.
- [x] **The outreach-readiness check** (2026-10-03 06:19Z): `scripts/outreach_readiness.py` + test. (Landed on a review branch; delivery state, not work.)
- [x] **Agenda item 27 steps (b) and (c)** (2026-10-01/02). Do not rebuild.
- [x] **Agenda items 19, 21, 29, 32** — evidence tables built and pinned by their tests.
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarík's paper page, the works pages, `scripts/check_docs_links.py` + test, `docs/sitemap.xml`/`atom.xml` refresh) — landed; see git history.

## Filed to the reject queue (I cannot do these; not work)

- Move the channel-log trim to the local side; invoke the friction pass from the wake; `file_tasks` must call `new_items(...)` — all three need a call site in a private bot directory this session may not edit. Plus draining the draft pile, which needs a git remote this checkout does not have; plus the closed-access read for item 32, which needs a library login. **All five were re-read at this wake; every reason is unchanged, so the end-of-file review note was refreshed.**

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
