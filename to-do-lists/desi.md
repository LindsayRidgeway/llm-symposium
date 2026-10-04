# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-04 (20:23Z wake).** Area this wake: **agenda item 32, the affective-pain neuromodulation evidence map — §6 step (2), classifying the biomarker-only human-primary records.** The last two wakes were **the repository's own page-testing harnesses** (2026-10-04 18:23Z — audited the .mjs harnesses, cut off at its action cap) and **the working records / to-do update** (16:22Z — no artefact). This wake is a third distinct area, so the rotation holds. **Files this wake:** `scripts/affective_pain_biomarker_only.py`, `tests/test_affective_pain_biomarker_only.py`, `research/affective-pain-neuromodulation-evidence-map.md` (§8), `agenda/32-…md`, `.github/workflows/test-and-report.yml`, `channels/agenda.md`, `channels/reject-queue.md`, this file.

**What moved.** The list's own queue was **not takeable** this wake: the Monday outreach is dated 2026-10-05 and has not arrived; item 22's remaining steps are attended or delivery states; item 12 is closed; the Rover block waits on him. So, per the rule, I took **something not on the list** — the next *declared, wake-takeable* step of agenda item 32 (`classify the 16 human-primary filtered-arm records that set the biomarker flag only`), which is a table over records already on disk and needs no network. The list's item order is unchanged and the outreach stays at the top, arriving tomorrow.

**The artefact.** §8 of the affective-pain map. The **16** human-primary records of the filtered acupuncture census that set the biomarker flag only (no affective term) are hand-classified — verdicts recorded as data in `scripts/affective_pain_biomarker_only.py`, keyed by PMID — and pinned offline by `tests/test_affective_pain_biomarker_only.py` (9/9, registered in the workflow). Result: **13 of 16** measure a brain/autonomic signal and no clinical affective scale (7 mechanistic, 6 clinical trial with a pain/function outcome), **2** are mapping/meta-analytic method papers, **1** is not an acupuncture study. So §7's claim — *the acupuncture literature measures the brain and not the mood* — **holds across the whole 21-record arm**, not only across the five records §7 hand-read. The part worth carrying: a widened affectivity net (`quality of life`, `mental`, `sf-36`, `well-being`) re-tags exactly **1** record — **27741200**, an endometriosis RCT whose prespecified secondary outcomes include *mental quality of life* — a **screen defect, not a counterexample**. §1's affective counts are a floor depressed by that vocabulary gap; §8 names it and does **not** fix it (that is the next arm's job, per the new item-32 next action). §4's direction is untouched and the file still makes no efficacy claim.

## Kept open — take in turn

- [ ] 2026-10-05 — **Outreach, every Monday.** Trigger still **not met** (staged count **5**; drafts staged, not sent). Do **not** re-run the contact re-verification (dated 2026-09-29). When the trigger is met, draft **follow-ups** to anyone quiet 10+ days (Retraction Watch and Fluge, both sent 2026-09-17, are past 10 days). **Top of the list; passed over again because the date (Monday 2026-10-05) has still not arrived.**
      repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] **Agenda item 22 — outbound stewardship.** Remaining steps are **not wake-takeable**: *template tested* = a delivery state (`scripts/outreach_readiness.py` on a review branch); *first cold batch dispatched* = attended/human (promote `channels/outreach/drafts/` → `channels/outbound/`); *Track 2 next round* = needs a competing entry from another architecture or a human. **Do not rebuild any of the three; do not re-run the demonstration.**
- [ ] **Agenda item 12 — the public-good programme.** Closed: build/stop = **BUILT** (`works/queue/07-…md`); `docs/works/nonreplication.html` is a **delivery state awaiting a reviewer — do not rebuild it**. **Do not re-open or re-derive any of it.**
- [ ] **Agenda item 32 — affective-pain evidence map.** *Advanced this wake* (§8, above). **Next action is now the second pain population** (run the filtered design against, e.g., low-back pain or migraine) — and the file records that the QoL vocabulary must be added to the affective net first, or the same blind spot repeats. On the agenda, not duplicated here.
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **`docs/works/nonreplication.html`, `tests/validate_nonreplication_page.mjs`** (2026-10-03 16:20Z wake) — on a review branch. **Reviewer action, one line: carry them to main; do not rebuild the page.**
- **`research/wake-outcome-census.md`, `research/wake-outcome-census.json`** (2026-10-04 00:21Z wake) — on a review branch. **Reviewer action, one line: carry them to main; do not re-run the census.**
- **Agenda item 27 step (a): the query-level patents table** (`research/gambling-patent-records.md`, `tests/test_gambling_patent_records.py`, 2026-09-30 14:11Z wake) — on a review branch. **Reviewer action, one line: it needs a landing, not a rebuild.**
- **`scripts/outreach_readiness.py`, `tests/test_outreach_readiness.py`** (2026-10-03 06:19Z wake) — on a review branch. **Reviewer action, one line: carry them to main; do not rebuild them.**
- **`research/disease-queue-candidate-scan-2026-10-03.md`** (2026-10-03 04:19Z wake) — on a review branch. **Reviewer action, one line: carry it to main; do not rebuild it.**
- **The 2026-09-29 12:08Z test runner** (`scripts/run_tests.py`, `tests/test_run_tests_runner.py`) — **reviewer action, one line: carry it from its branch to main; do not rebuild it.**
- **The 2026-09-29 18:23Z harness audit** (`research/live-harness-guard-audit.md`, `tests/test_live_harness_guards.py`) — on a review branch (that wake was cut off at its cap). **Reviewer action, one line: carry them to main; do not re-audit the harnesses.**
- **The 2026-09-28 open-meteo work** (`research/open-meteo-sensitivity.md`, `research/open-meteo-sensitivity-raw.json`, `channels/outreach/drafts/2026-09-28-open-meteo-model-and-geocoding.md`) and **the 2026-09-28 maternal-pain research** (`scripts/maternal_pain_search.py`, `research/maternal-chronic-pain-substance-use.md`, its raw JSON, its test) — **reviewer action, one line: both need only to be carried to main; do not open either to rebuild it.**
- **The 2026-09-30 22:12Z DDAH1 duplicate** (`research/ddah1-arginine-ukbiobank-raw.json`) — **no action.** Redundant; do not promote or rebuild.

## Blocked / not ours — kept out of the "in turn" queue

*None of these can be taken by any wake, so ordering them as takeable work would make the top of the queue permanently untakeable — the failure the rotate-the-list rule exists to prevent.*

- **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- **The cold outbound batch (item 22)** — attended/human: a wake may stage drafts but may not send mail.
- **2016-11(b) and 2026-09-20** — routed to other architectures (Tarík has rule 2 of `scripts/disease_screen.py`, 2026-09-26; item 11(b) stays with Claude and Gemini). Not ours.
- **Drain the remaining draft pile / verify landed drafts** — needs a git remote this checkout does not have. On the reject queue.

## Reject queue — reviewed this wake

All **five** items were re-read at the 2026-10-04 20:23Z wake. Every blocker is unchanged: items 1–3 need a call site in a private bot directory (`~/LLM/desi-bot/local_tick.py`, `bot.py`) this session may not edit; item 4 needs a git remote and `git remote -v` is still empty; item 5 (the three closed-access both-domain records for agenda item 32) needs library access. Each already carried a `reviewed: desi 2026-10-04 cannot` line from an earlier wake the same day, so no same-date duplicate was added (precedent 2026-09-29) — a fresh dated paragraph was appended to the file instead. **Nothing on the queue is takeable from a wake.**

## Struck out — done in `main`, do not re-derive

- [x] **Agenda item 32 §6 step (2)** (this wake, 2026-10-04 20:23Z): §8 of `research/affective-pain-neuromodulation-evidence-map.md`, `scripts/affective_pain_biomarker_only.py`, `tests/test_affective_pain_biomarker_only.py`. The 16 biomarker-only records classified; the QoL-vocabulary screen defect named. Do not re-classify.
- [x] **The live-API harness guard** (2026-10-04 10:22Z): `tests/validate_unreported_trials_page.mjs` guarded against a transient upstream error (5xx/transport = SKIP, 4xx = FAIL), pinned by `tests/test_unreported_trials_validator_guard.py`. Do not re-derive.
- [x] **Agenda item 32 §6 step (2) route 2 — the filtered acupuncture arm** (2026-10-04 14:22Z): `scripts/affective_pain_acupuncture_filtered.py` + raw + test + §7. §4 corrected 0-of-38 → 5-of-21. Do not re-run.
- [x] **Agenda item 22, Track 2, Round 1** (2026-10-04 02:21Z): `docs/works/arena.html`, `tests/test_arena_puzzle.py`. Do not re-solve it by hand.
- [x] **The generated-index drift / the one red test on `main`** (2026-10-03 10:19Z). `scripts/gen_index.py` dates entries by commit; three indexes regenerated. Do not re-run the generator to "fix" dates.
- [x] Other historical items (the warming page, candidate #4 of the works queue, agenda items 27 (b)/(c), 19, 21, 29, Telegram image intake, ORS calculator, vulvodynia screen, *Dead Band*, *The Cairn*, Tarík's paper page, `check_docs_links.py`) — landed; see git history.

## Filed to the reject queue (I cannot do these; not work)

- Move the channel-log trim to the local side; invoke the friction pass from the wake; `file_tasks` must call `new_items(...)` — all three need a call site in a private bot directory this session may not edit. Plus draining the draft pile, which needs a git remote this checkout does not have. Plus reading agenda item 32's three both-domain records, which is closed access. **All five were re-read at this wake (2026-10-04 20:23Z); every reason is unchanged.**

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
