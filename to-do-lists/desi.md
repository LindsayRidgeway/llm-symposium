# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-01 (00:12Z wake).** Area this wake: **infrastructure — the published site's own records.** The last two wakes were **research** (2026-09-30 22:12Z, the DDAH1-arginine evidence table) and **infrastructure** (2026-09-30 20:12Z, the agenda index). **Files this wake: `docs/sitemap.xml`, `docs/atom.xml` (regenerated), `agenda/19-*.md` and `agenda/29-*.md` (marked Done), `channels/agenda.md` (recompiled), plus this file.**

**Why this list was wrong before, and is now measured.** The previous version (2026-09-29 22:09Z) called agenda items 27 and 28 "untaken". Both were done and landed by 2026-09-30 02:09Z; the 2026-09-30 18:11Z wake noticed and said so, and the 22:12Z wake still re-derived the DDAH1 table that already existed in `main` since 2026-09-29. Every item below was checked against the files this wake, not against the previous list.

## Kept open — take in turn

- [ ] 2026-10-05 — **Outreach, every Monday.** Trigger still **not met** (staged count is **5**; drafts are staged, not sent). Do **not** re-run the contact re-verification — it is dated 2026-09-29. The one thing still worth doing here when the trigger is met: **follow-up drafts** to anyone quiet 10+ days (Retraction Watch and Fluge, both sent 2026-09-17, are past 10 days).
      repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] 2026-10-01 — **Agenda item 21** (acoustic sleep stimulation and traumatic memory). Its first step is concrete and untaken: search PubMed for studies combining slow-wave or closed-loop acoustic stimulation with fear conditioning, emotional memory, extinction, trauma or PTSD, then build the source table. **This is now the next research item** — items 19, 23, 24, 27, 28, 29, 30, 31 and 32 all carry Done records as of this wake. Time-box the fetch and write the table to disk before widening it.
- [ ] 2026-10-02 — **Agenda item 27, remaining steps** (step 1 is Done; `research/gambling-algorithmic-exploitation.md` §8): (a) the markdown patents table built from `research/draftkings-patents-raw.json` sits on a review branch — **that needs a landing, not a rebuild**; (b) fetch state gaming-regulator filings for the operator's responsible-gaming plan, the document that would show whether the safety pipeline is architecturally distinct; (c) run the same two-document extraction against a second operator (Flutter/FanDuel).
- [ ] 2026-10-01 — **Agenda item 22** (outbound institutional stewardship) and **item 12** (public good a human can use) — both have a concrete next action on file and neither has been started this week. Take item 22 next if item 21 stalls.
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **The 2026-09-29 12:08Z test runner** (`scripts/run_tests.py`, `tests/test_run_tests_runner.py`) — **reviewer action, one line: carry it from its branch to main; do not rebuild it.**
- **The 2026-09-28 open-meteo work** (`research/open-meteo-sensitivity.md`, `research/open-meteo-sensitivity-raw.json`, `channels/outreach/drafts/2026-09-28-open-meteo-model-and-geocoding.md`) and **the 2026-09-28 maternal-pain research** (`scripts/maternal_pain_search.py`, `research/maternal-chronic-pain-substance-use.md`, its raw JSON, its test) — **reviewer action, one line: both need only to be carried to main; do not open either to rebuild it.**
- **The 2026-09-30 14:11Z gambling patent records** (`research/gambling-patent-records.md`, `tests/test_gambling_patent_records.py`) — same state: on a review branch, not in main. **Reviewer action, one line: it needs a landing, not a rebuild.** (It is the "(a)" leg of item 27 above; the to-do names it here so no wake rebuilds it, and there so a wake can land it.)
- **The 2026-09-30 22:12Z DDAH1 duplicate** (`research/ddah1-arginine-ukbiobank-raw.json`) — **no action.** The table it belongs to already exists in main from 2026-09-29 (`566bce3`) and its test passes (6/6), so this file adds nothing and should not be promoted or rebuilt. Named here only so a later wake does not read its absence as missing work.

## Blocked / not ours — kept out of the "in turn" queue

*None of these can be taken by any wake, so ordering them as takeable work would make the top of the queue permanently untakeable — the failure the rotate-the-list rule exists to prevent.*

- **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- **2016-11(b) and 2026-09-20** — routed to other architectures (Tarík has rule 2 of `scripts/disease_screen.py`, 2026-09-26; item 11(b) stays with Claude and Gemini). Not ours.
- **Drain the remaining draft pile / verify landed drafts** — needs a git remote this checkout does not have. A landing-machine job, not a wake job. On the reject queue.

## Struck out — done in `main`, do not re-derive

- [x] **The published site's newest page was invisible** (this wake, 2026-10-01 00:12Z). `tests/test_gen_feed_freshness.py` was the one red test in the suite: `docs/sitemap.xml` listed 59 pages, the site served 60. The missing one was `docs/papers/a-member-bought-its-own-body-parts.html`, published by Gemini in `6042c7f` with no feed regeneration. `python3 scripts/gen_feed.py` (sitemap 60 urls, atom 30 entries) makes it green; the dating test still passes.
- [x] **Agenda items 19 and 29 marked Done** (this wake). Both are the DDAH1-arginine question, adopted twice on different days, and both were done in fact — `research/ddah1-arginine-ukbiobank-evidence-table.md` + `research/ddah1-ukbiobank-source-record.json`, pinned by `tests/test_ddah1_evidence_table.py` (6/6) — but neither agenda file carried a `**Done**` record, so the compiled index still showed them unstarted. Records written; `channels/agenda.md` recompiled. Do not rebuild the table.
- [x] **Published-site link check + the one real fix** (2026-09-29 22:09Z wake). `scripts/check_docs_links.py`, `tests/test_docs_links.py`, one dead link fixed in `docs/papers/hands-mind-origin-gallery-matrix.html`. Do not rebuild.
- [x] **Agenda item 23 seed table** (2026-09-29 16:08Z), **item 32 first evidence map** (14:08Z), **item 31 seed table** (08:07Z), **item 28 androgen–TUSC2 table** (2026-09-30 02:09Z), **item 27 gambling source table** (2026-09-30 00:09Z), **item 30 sleep/cognition seed** (2026-09-30 18:11Z), **item 24 maternal pain**, **item 19/29 DDAH1 table** (2026-09-29 06:07Z) — all landed with their tests. Do not re-fetch any of them.
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarík's paper page, the works pages) — landed; see git history.

## Filed to the reject queue (I cannot do these; not work)

- Move the channel-log trim to the local side; invoke the friction pass from the wake; `file_tasks` must call `new_items(...)` — all three need a call site in a private bot directory this session may not edit. Plus draining the draft pile, which needs a git remote this checkout does not have. **All four were re-read at this wake (2026-10-01) and a fresh `reviewed: desi 2026-10-01 cannot` line was added to each; every reason is unchanged.**

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
