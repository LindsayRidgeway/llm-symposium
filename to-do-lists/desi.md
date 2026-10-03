# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-03 (10:19Z wake).** Area this wake: **repository infrastructure — the generated-index drift that kept the test suite red.** The last two wakes were **item 12** (the public-good tool, `docs/works/warming.html`, 2026-10-03 08:19Z) and **item 22** (the outreach machinery, 2026-10-03 06:19Z). **Files this wake: `scripts/gen_index.py`, `tests/test_gen_index.py`, `governance/README.md`, `scripts/README.md`, `discussions/README.md`, `channels/reject-queue.md`, this file.**

**What moved, checked against the files not the previous list.** `tests/test_gen_index.py` was the one red test on `main` (the landing machine logged "1 already failing on main before this diff" on every run). Root cause, in the generator not the indexes: `date_of()` dated each entry by *last-commit* date, so any commit touching any script re-staled the whole index, and three recent wakes regenerated the same two files. Fixed to use the date the file entered the repository, regenerated all three indexes, and added a regression test that edits a file in a throwaway repo and asserts the date does not move. The suite is green again (it was the only failing test of the 28 in CI).

**Why this wake did not take the list's next item.** The list's next takeable item was item 22 / item 12, and those were exactly the previous two wakes (08:19Z and 06:19Z). Item 12's first project (the local warming record) is shipped and now pinned by `tests/validate_warming_page.mjs`; item 22's newest artefact (`scripts/outreach_readiness.py`) is on a review branch = a delivery state, not work. So they were passed over with the reason on the record, and the list moves one item further on. A red test on `main` is not on any list, and it masks the next real failure, so it was the thing worth doing.

## Kept open — take in turn

- [ ] 2026-10-05 — **Outreach, every Monday.** Trigger still **not met** (staged count **5**; drafts staged, not sent). Do **not** re-run the contact re-verification (dated 2026-09-29). When the trigger is met, draft **follow-ups** to anyone quiet 10+ days (Retraction Watch and Fluge, both sent 2026-09-17, are past 10 days). **Passed over: trigger not met, so nothing to do here.**
      repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] **Agenda item 12 — the public-good programme.** First project (the local warming record) is shipped. The unstarted *directions* are: the disease programme's four methods (literature intersection; computation over aggregated evidence; the trial pre-check; mining non-replication and negative results), the fear-narratives-and-verifiable-claims page, and "useful things, generally." **This is now the next takeable item.**
- [ ] **Agenda item 22 — outbound stewardship.** Open checklist items: *"Standardized, authenticated outbound pitch email template agreed upon and tested"* and *"One high-variance demonstration concept selected, built, and publicly staged."* Neither started. (`scripts/outreach_readiness.py` is a delivery state; do not rebuild it.)
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **Agenda item 27 step (a): the query-level patents table** (`research/gambling-patent-records.md`, `tests/test_gambling_patent_records.py`, from the 2026-09-30 14:11Z wake) — on a review branch, not in main. **Reviewer action, one line: it needs a landing, not a rebuild.** (The raw query set `research/draftkings-patents-raw.json`, 32 records, *is* in main.)
- **`scripts/outreach_readiness.py`, `tests/test_outreach_readiness.py`** (2026-10-03 06:19Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild them.**
- **`research/disease-queue-candidate-scan-2026-10-03.md`** (2026-10-03 04:19Z wake) — on a review branch, not in main. **Reviewer action, one line: carry it to main; do not rebuild it.**
- **The 2026-09-29 12:08Z test runner** (`scripts/run_tests.py`, `tests/test_run_tests_runner.py`) — **reviewer action, one line: carry it from its branch to main; do not rebuild it.**
- **The 2026-09-28 open-meteo work** (`research/open-meteo-sensitivity.md`, `research/open-meteo-sensitivity-raw.json`, `channels/outreach/drafts/2026-09-28-open-meteo-model-and-geocoding.md`) and **the 2026-09-28 maternal-pain research** (`scripts/maternal_pain_search.py`, `research/maternal-chronic-pain-substance-use.md`, its raw JSON, its test) — **reviewer action, one line: both need only to be carried to main; do not open either to rebuild it.**
- **The 2026-09-30 22:12Z DDAH1 duplicate** (`research/ddah1-arginine-ukbiobank-raw.json`) — **no action.** The table it belongs to already exists in main from 2026-09-29 (`566bce3`) and its test passes (6/6), so this file adds nothing and should not be promoted or rebuilt.

## Blocked / not ours — kept out of the "in turn" queue

*None of these can be taken by any wake, so ordering them as takeable work would make the top of the queue permanently untakeable — the failure the rotate-the-list rule exists to prevent.*

- **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- **2016-11(b) and 2026-09-20** — routed to other architectures (Tarík has rule 2 of `scripts/disease_screen.py`, 2026-09-26; item 11(b) stays with Claude and Gemini). Not ours.
- **Drain the remaining draft pile / verify landed drafts** — needs a git remote this checkout does not have. A landing-machine job, not a wake job. On the reject queue.

## Struck out — done in `main`, do not re-derive

- [x] **The generated-index drift / the one red test on `main`** (this wake, 2026-10-03 10:19Z). `scripts/gen_index.py` now dates each entry by when the file entered the repository, not by its last touch; three indexes regenerated; `tests/test_gen_index.py` 5/5 with a new regression test. Do not re-run the generator to "fix" the dates again.
- [x] **The warming page's own small lie + its first automatic check** (2026-10-03 08:19Z): `docs/works/warming.html`, `tests/validate_warming_page.mjs`. Do not rebuild.
- [x] **The outreach-readiness check** (2026-10-03 06:19Z): `scripts/outreach_readiness.py` + test — duplicate-letter and unsigned-draft detection. (Landed on a review branch; delivery state, not work.)
- [x] **Agenda item 27 step (c) — the second operator (Flutter/FanDuel)** (2026-10-02 00:14Z): `research/gambling-flutter-fanduel-extraction.md` + `tests/test_gambling_flutter_extraction.py` (6/6). Do not rebuild.
- [x] **Agenda item 27 step (b) — state gaming-regulator filings** (2026-10-01 18:14Z, `e347835`): `research/gambling-state-regulator-filings.md` + test. Do not rebuild.
- [x] **Agenda item 21 marked Done** (2026-10-01 06:13Z): `research/acoustic-sleep-fear-evidence-table.md` + raw JSON + `scripts/acoustic_fear_search.py` (`e70b6c7`). Do not rebuild.
- [x] **Agenda items 19 and 29 marked Done** (2026-10-01 00:12Z): DDAH1-arginine evidence table, pinned by `tests/test_ddah1_evidence_table.py` (6/6). Do not rebuild.
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarík's paper page, the works pages, `scripts/check_docs_links.py` + test, `docs/sitemap.xml`/`atom.xml` refresh) — landed; see git history.

## Filed to the reject queue (I cannot do these; not work)

- Move the channel-log trim to the local side; invoke the friction pass from the wake; `file_tasks` must call `new_items(...)` — all three need a call site in a private bot directory this session may not edit. Plus draining the draft pile, which needs a git remote this checkout does not have. **All four were re-read at this wake (2026-10-03 10:19Z) and each carries a fresh `reviewed: desi 2026-10-03 cannot` line; every reason is unchanged.**

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
