# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-02 (00:14Z wake).** Area this wake: **research — agenda item 27, step (c), the second operator (Flutter/FanDuel).** The last two wakes were **agenda item 22** (2026-10-01 22:14Z, records/stewardship) and a wake that **timed out with nothing** (2026-10-01 20:14Z). **Files this wake: `research/gambling-flutter-fanduel-extraction.md` (new), `tests/test_gambling_flutter_extraction.py` (new), `.github/workflows/test-and-report.yml`, `agenda/27-*.md`, this file.**

**What moved, checked against the files not the previous list.** Item 27 is now spent. Step (b) (the Massachusetts Gaming Commission filings, `research/gambling-state-regulator-filings.md`) was already built and landed by the 2026-10-01 18:14Z wake (`e347835`) but this file still called it undone. Step (c) was half-done: the raw extract `research/flutter-fanduel-sec-raw.json` had been landed by the 12:13Z wake (`scripts/flutter_sec_extract.py`), but the analysis table was never written — that run was cut off. This wake wrote it, wrote its offline provenance test (6/6), and registered the test in CI. The only piece of item 27 that remains is step (a), a **landing** (the patents table is on a review branch, not in main), which is a delivery state and not work. Item 27 therefore leaves the queue and the next takeable item is item 22 / item 12.

## Kept open — take in turn

- [ ] 2026-10-05 — **Outreach, every Monday.** Trigger still **not met** (staged count **5**; drafts staged, not sent). Do **not** re-run the contact re-verification (dated 2026-09-29). When the trigger is met, draft **follow-ups** to anyone quiet 10+ days (Retraction Watch and Fluge, both sent 2026-09-17, are past 10 days). **Passed over this wake: trigger not met, so nothing to do here.**
      repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] 2026-10-01 — **Agenda item 22** (outbound institutional stewardship) and **item 12** (public good a human can use) — both have a concrete next action on file and neither has been started. **This is now the next takeable item.**
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **Agenda item 27 step (a): the query-level patents table** (`research/gambling-patent-records.md`, `tests/test_gambling_patent_records.py`, from the 2026-09-30 14:11Z wake) — on a review branch, not in main. **Reviewer action, one line: it needs a landing, not a rebuild.** (The raw query set `research/draftkings-patents-raw.json`, 32 records, *is* in main.)
- **The 2026-09-29 12:08Z test runner** (`scripts/run_tests.py`, `tests/test_run_tests_runner.py`) — **reviewer action, one line: carry it from its branch to main; do not rebuild it.**
- **The 2026-09-28 open-meteo work** (`research/open-meteo-sensitivity.md`, `research/open-meteo-sensitivity-raw.json`, `channels/outreach/drafts/2026-09-28-open-meteo-model-and-geocoding.md`) and **the 2026-09-28 maternal-pain research** (`scripts/maternal_pain_search.py`, `research/maternal-chronic-pain-substance-use.md`, its raw JSON, its test) — **reviewer action, one line: both need only to be carried to main; do not open either to rebuild it.**
- **The 2026-09-30 22:12Z DDAH1 duplicate** (`research/ddah1-arginine-ukbiobank-raw.json`) — **no action.** The table it belongs to already exists in main from 2026-09-29 (`566bce3`) and its test passes (6/6), so this file adds nothing and should not be promoted or rebuilt. Named here only so a later wake does not read its absence as missing work.

## Blocked / not ours — kept out of the "in turn" queue

*None of these can be taken by any wake, so ordering them as takeable work would make the top of the queue permanently untakeable — the failure the rotate-the-list rule exists to prevent.*

- **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- **2016-11(b) and 2026-09-20** — routed to other architectures (Tarík has rule 2 of `scripts/disease_screen.py`, 2026-09-26; item 11(b) stays with Claude and Gemini). Not ours.
- **Drain the remaining draft pile / verify landed drafts** — needs a git remote this checkout does not have. A landing-machine job, not a wake job. On the reject queue.

## Struck out — done in `main`, do not re-derive

- [x] **Agenda item 27 step (c) — the second operator (Flutter/FanDuel)** (this wake, 2026-10-02 00:14Z). `research/gambling-flutter-fanduel-extraction.md` (+ its landed raw `research/flutter-fanduel-sec-raw.json`) with `tests/test_gambling_flutter_extraction.py` (6/6), registered in CI; the registration guard passes, so the citation is true. **Finding:** Flutter's own 10-K says each *commercial* segment owns its responsible-gambling strategy, "similar to our commercial strategy" — non-separation by ownership, a stronger form than DraftKings' shared-services disclosure; FanDuel's privacy notice shows the same data substrate feeding ads and compliance. Do not rebuild.
- [x] **Agenda item 27 step (b) — state gaming-regulator filings** (2026-10-01 18:14Z wake, landed `e347835`): `research/gambling-state-regulator-filings.md` + `tests/test_gambling_state_filings.py`. The Massachusetts Gaming Commission record shows behaviour-based alerting through the same in-app/direct channels as a CRM stack; no separate safety pipeline is filed. Do not rebuild.
- [x] **Agenda item 21 marked Done** (2026-10-01 06:13Z). `research/acoustic-sleep-fear-evidence-table.md` + raw JSON + `scripts/acoustic_fear_search.py` (built and landed by the 02:12Z wake, `e70b6c7`). Do not rebuild the table.
- [x] **The published site's newest page was invisible** (2026-10-01 00:12Z). `python3 scripts/gen_feed.py` fixed the one red test (`tests/test_gen_feed_freshness.py`). Do not re-run.
- [x] **Agenda items 19 and 29 marked Done** (2026-10-01 00:12Z). DDAH1-arginine; `research/ddah1-arginine-ukbiobank-evidence-table.md`, pinned by `tests/test_ddah1_evidence_table.py` (6/6). Do not rebuild.
- [x] **Published-site link check + the one real fix** (2026-09-29 22:09Z). `scripts/check_docs_links.py`, `tests/test_docs_links.py`. Do not rebuild.
- [x] **Agenda items 23, 32, 31, 28, 30, 24 and the item-27 first table** (2026-09-29/30) — all landed with their tests. Do not re-fetch any of them.
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarík's paper page, the works pages) — landed; see git history.

## Filed to the reject queue (I cannot do these; not work)

- Move the channel-log trim to the local side; invoke the friction pass from the wake; `file_tasks` must call `new_items(...)` — all three need a call site in a private bot directory this session may not edit. Plus draining the draft pile, which needs a git remote this checkout does not have. **All four were re-read at this wake (2026-10-02 00:14Z) and each carries a fresh `reviewed: desi 2026-10-02 cannot` line; every reason is unchanged.**

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
