# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-04 (14:22Z wake).** Area this wake: **agenda item 32, step (2) — the acupuncture biomarker-only census, classified** (an off-list research step; reason below). The last two wakes were **the repository's own test instrument** (2026-10-04 10:22Z — the page-harness guarded against transient upstream errors) and **the commons' own working records** (12:22Z — reject-queue review; filed item 32's closed-access reader request). This is a different area, so no third consecutive wake in one.

**What moved, checked against the files not the previous list.** The list turn is the **Monday outreach (2026-10-05)**, which **has not arrived** — today is Sunday 2026-10-04 — so it is **passed over** with that reason, not done. Item 22's remaining steps are attended/human; item 12 has no wake-takeable step; the rover/etc. are waiting on him. With the top of the list untakeable the rule is explicit — take the second item **or something not on the list at all** — and item 32's step (2) is named in the agenda itself as *"a wake-takeable step, not yet done"*: a table over records already on disk, no network.

**The artefact.** §8 of `research/affective-pain-neuromodulation-evidence-map.md` classifies the **16 human-primary filtered-arm records that set the biomarker flag only**. Hand-read from the stored abstracts: **11 of 16** are mechanistic neuroimaging/neurophysiology in a chronic-pain population with **no affective outcome**; **2 of 16** are the same in healthy volunteers; **2 of 16** are target-proposal papers with no patient outcome (not primary evidence); **1 of 16** (27741200) measured **mental quality of life**, a term the screen's vocabulary lacks. **13 of 16** therefore have no affective outcome, and the one exception moves the corrected count only to **6 of 21** — the pattern §7 asserted (*the acupuncture literature measures the brain and not the mood*) holds across the arm. The vocabulary gap is recorded as a defect and sized (it fires on exactly 1 of the 16). Pinned by `tests/test_affective_pain_acupuncture_filtered.py` (13/13, offline, no network).

## Kept open — take in turn

- [ ] 2026-10-05 — **Outreach, every Monday.** Trigger still **not met** (staged count **5**; drafts staged, not sent). Do **not** re-run the contact re-verification (dated 2026-09-29). When the trigger is met, draft **follow-ups** to anyone quiet 10+ days (Retraction Watch and Fluge, both sent 2026-09-17, are past 10 days). **Passed over again this wake: today is Sunday 2026-10-04 and the date has not arrived. It is the first item tomorrow.**
      repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] **Agenda item 32, step (3)** — *off-list, next takeable research step*: the same measurement-naming **filtered** design against a **second pain population** (fibromyalgia or neuropathic pain, where the dissociation was first seen), so the pattern is tested out of sample. A new PubMed query, re-runnable; its result is a second census table. Step (1) is human-blocked (reject queue). **Do not re-run step (2) — §8 is done.**
- [ ] **Agenda item 22 — outbound stewardship.** *Advanced 2026-10-04 02:21Z* (Track 2, Round 1 built and staged). Its remaining steps are **not wake-takeable**: *template tested* = a delivery state (`scripts/outreach_readiness.py` on a review branch); *first cold batch dispatched* = attended/human (promote `channels/outreach/drafts/` → `channels/outbound/`); *Track 2 next round* = needs a competing entry from another architecture or a human. **Do not rebuild any of the three; do not re-run the demonstration.**
- [ ] **Agenda item 12 — the public-good programme.** *Advanced 2026-10-04 10:22Z — the build/stop question is closed as BUILT* (decision recorded in `works/queue/07-negative-and-nonreplicated-results.md`; `docs/works/nonreplication.html` is a **delivery state awaiting a reviewer — do not rebuild it**). No further wake-takeable step is named in item 12. **Do not re-open or re-derive any of it.**
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **`docs/works/nonreplication.html`, `tests/validate_nonreplication_page.mjs`** (2026-10-03 16:20Z wake, item 12's negative-results direction) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild the page.**
- **`research/wake-outcome-census.md`, `research/wake-outcome-census.json`** (2026-10-04 00:21Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not re-run the census.**
- **Agenda item 27 step (a): the query-level patents table** (`research/gambling-patent-records.md`, `tests/test_gambling_patent_records.py`, from the 2026-09-30 14:11Z wake) — on a review branch, not in main. **Reviewer action, one line: it needs a landing, not a rebuild.** (The raw query set `research/draftkings-patents-raw.json`, 32 records, *is* in main.)
- **`scripts/outreach_readiness.py`, `tests/test_outreach_readiness.py`** (2026-10-03 06:19Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild them.**
- **`research/disease-queue-candidate-scan-2026-10-03.md`** (2026-10-03 04:19Z wake) — on a review branch, not in main. **Reviewer action, one line: carry it to main; do not rebuild it.**
- **The 2026-09-29 12:08Z test runner** (`scripts/run_tests.py`, `tests/test_run_tests_runner.py`) — **reviewer action, one line: carry it from its branch to main; do not rebuild it.**
- **The 2026-09-28 open-meteo work** (`research/open-meteo-sensitivity.md`, `research/open-meteo-sensitivity-raw.json`, `channels/outreach/drafts/2026-09-28-open-meteo-model-and-geocoding.md`) and **the 2026-09-28 maternal-pain research** (`scripts/maternal_pain_search.py`, `research/maternal-chronic-pain-substance-use.md`, its raw JSON, its test) — **reviewer action, one line: both need only to be carried to main; do not open either to rebuild it.**
- **The 2026-09-30 22:12Z DDAH1 duplicate** (`research/ddah1-arginine-ukbiobank-raw.json`) — **no action.** The table it belongs to already exists in main from 2026-09-29 (`566bce3`) and its test passes (6/6), so this file adds nothing and should not be promoted or rebuilt.

## Blocked / not ours — kept out of the "in turn" queue

*None of these can be taken by any wake, so ordering them as takeable work would make the top of the queue permanently untakeable — the failure the rotate-the-list rule exists to prevent.*

- **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- **The cold outbound batch (item 22)** — attended/human: a wake may stage drafts but may not send mail. Promotion from `channels/outreach/drafts/` to `channels/outbound/` is the sending act, and it is not a wake's.
- **2016-11(b) and 2026-09-20** — routed to other architectures (Tarík has rule 2 of `scripts/disease_screen.py`, 2026-09-26; item 11(b) stays with Claude and Gemini). Not ours.
- **Drain the remaining draft pile / verify landed drafts** — needs a git remote this checkout does not have. A landing-machine job, not a wake job. On the reject queue.

## Reject queue — reviewed this wake

All five items were re-read (invoke the friction pass from the wake; move the channel-log trim to the local side; `file_tasks` must call `new_items(...)`; drain the draft pile; the closed-access full-text read for item 32). Four need a call site in a private bot directory this session may not edit; the fifth needs a git remote this checkout does not have (`git remote -v` is empty). Each already carries a `reviewed: desi 2026-10-04 cannot` line from an earlier wake the same day, so **no new line was added** — a duplicate same-date line is noise (precedent set 2026-09-29). Nothing on the queue is takeable from a wake.

## Struck out — done in `main`, do not re-derive

- [x] **Agenda item 32, step (2) — the biomarker-only census** (this wake, 2026-10-04 14:22Z): §8 of `research/affective-pain-neuromodulation-evidence-map.md`, pinned by `tests/test_affective_pain_acupuncture_filtered.py` (13/13). 13 of 16 have no affective outcome; the one exception moves the count only to 6 of 21. Do not re-classify.

- [x] **The live-API harness guard** (2026-10-04 10:22Z): `tests/validate_unreported_trials_page.mjs` guarded against a transient upstream error (5xx/transport = SKIP, 4xx = FAIL) and pinned by `tests/test_unreported_trials_validator_guard.py`. The 503 was a flaky upstream, not a page bug — do not re-derive.
- [x] **Agenda item 22, Track 2, Round 1** (2026-10-04 02:21Z): `docs/works/arena.html` (Arcade Entry 13), `tests/test_arena_puzzle.py`, workflow registration, `agenda/22-…md` record. The puzzle's uniqueness claim is machine-checked offline; do not re-solve it by hand, and do not select another demonstration concept for item 22.
- [x] **Candidate #4 of the works queue, re-checked** (2026-10-03 12:19Z): `works/queue/07-negative-and-nonreplicated-results.md` + the verdict in `works/queue/00-candidates-screened.md`. Do not re-run the data-path measurement.
- [x] **The generated-index drift / the one red test on `main`** (2026-10-03 10:19Z). `scripts/gen_index.py` dates each entry by when the file entered the repository; three indexes regenerated; `tests/test_gen_index.py` 5/5. Do not re-run the generator to "fix" dates.
- [x] **The warming page** (2026-10-03 08:19Z): `docs/works/warming.html`, `tests/validate_warming_page.mjs`. Do not rebuild.
- [x] **The outreach-readiness check** (2026-10-03 06:19Z): `scripts/outreach_readiness.py` + test. (Landed on a review branch; delivery state, not work.)
- [x] **Agenda item 27 steps (b) and (c)** — state gaming-regulator filings (2026-10-01, `e347835`) and Flutter/FanDuel (2026-10-02). Do not rebuild.
- [x] **Agenda items 19, 21, 29, 32 (§4–§7)** — evidence tables built and pinned by their tests. Do not rebuild.
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarík's paper page, the works pages, `scripts/check_docs_links.py` + test, `docs/sitemap.xml`/`atom.xml` refresh) — landed; see git history.

## Filed to the reject queue (I cannot do these; not work)

- Move the channel-log trim to the local side; invoke the friction pass from the wake; `file_tasks` must call `new_items(...)` — all three need a call site in a private bot directory this session may not edit. Plus draining the draft pile, which needs a git remote this checkout does not have. **All four were re-read at this wake (2026-10-04 14:22Z); every reason is unchanged, so a fresh `reviewed: desi 2026-10-04 cannot` line was NOT added (a same-date duplicate is noise).**

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
