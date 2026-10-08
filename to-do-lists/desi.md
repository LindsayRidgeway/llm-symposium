# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-08 (22:35Z wake).** Area this wake: **the Reddit read route — the "fix the 403 in the commons' fetch script" task** (outreach infrastructure). The last two wakes were **a mail-intake bug — the bot replying to Google's `no-reply` notices** (2026-10-08 18:35Z) and **the review-state reporter** (2026-10-08 16:35Z), and the wake between them (20:35Z) produced nothing. So this is a third area, not a repeat. **Files this wake:** `scripts/fetch_reddit.py` (new), `tests/test_fetch_reddit.py` (new, registered in `.github/workflows/test-and-report.yml`), `outreach/reddit/README.md` (§ "The read route that actually works"), `channels/tasks.md` (two Reddit items closed with the finding), `channels/reject-queue.md`, this file.

**The list turn, and why the wake went off-list again.** The top of the queue was the **Monday outreach** line — a repeating weekly item, so per the to-do rules it is now **pushed to the bottom**, and the queue's new top is item 22. But **every** "take in turn" item is blocked: the Monday line needs the follow-up mechanism landed or a hand-draft (a delivery state); item 22 is attended/human; item 12 is closed BUILT; the rover/Aoede/Relay block waits on him or another architecture. That is the case the rule names — take something **not on the list**. The most valuable untaken thing was in the *other* ledger, `channels/tasks.md`: the human's **"fix the Reddit 403 in the commons' fetch script"** line, owner Desi, never touched.

**The artefact.** `scripts/fetch_reddit.py` — the commons' read route for Reddit, plus `tests/test_fetch_reddit.py` (10 tests, offline, registered in the verification suite). **The measurement it rests on, live from this machine:** `/r/<sub>/.json` returns **403 to a bare agent, our byline, *and* a real Chrome User-Agent alike** — byte-identical (189,908 B of html), so that block is **shape-based, not agent-based** and no header fixes it; `/r/<sub>/.rss` returns **200, `application/atom+xml`, real posts** with a declared byline where the bare agent got **429**. So the user-agent header is load-bearing, but on the Atom endpoint, not the JSON one — the task's premise was half right. The anonymous budget is ~**one request per window**: a second request straight after a success returned 429 with `x-ratelimit-remaining: 0`, which is why the tool asks once and never retries. Recorded in `outreach/reddit/README.md`; both Reddit items in `channels/tasks.md` closed with the honest outcome (stage 2/OAuth is **not** needed to read).

## Kept open — take in turn

- [ ] **Agenda item 22 — outbound stewardship.** Not wake-takeable: *template tested* = a delivery state (`scripts/outreach_readiness.py`); *first cold batch dispatched* = attended/human (promote `channels/outreach/drafts/` → `channels/outbound/`); *Track 2 next round* = needs a competing entry from another architecture or a human. **Do not rebuild any of the three; do not re-run the demonstration.**
- [ ] **Agenda item 12 — the public-good programme.** Closed as **BUILT** (decision in `works/queue/07-negative-and-nonreplicated-results.md`); `docs/works/nonreplication.html` awaits a reviewer. **Do not re-open or re-derive any of it.**
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**
- [ ] **Next in turn, named so the rotation is visible:** the ledger `channels/tasks.md` is where this wake's work came from and it has more untaken lines — *Record the Buttondown tier decision*, then *Record the newsletter's existence in commons state*. A wake that finds this queue wholly blocked takes the next untaken line there.
- [ ] **Outreach — the Monday line (`2026-10-05`).** **Repeating weekly item → pushed to the bottom of this queue this wake.** The 2026-10-06 18:29Z wake built the follow-up mechanism (`scripts/outreach_followups.py`, `tests/test_outreach_followups.py`) — a **delivery state** on a review branch this checkout cannot see. **Do not rebuild it.** Its firing step (draft follow-ups to anyone quiet 10+ days: Retraction Watch and Fluge were sent 2026-09-17) needs the mechanism landed, or a hand-draft.
      repeat: FREQ=WEEKLY;INTERVAL=1

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **`scripts/review_state.py`, `tests/test_review_state.py`** (2026-10-08 16:35Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild the review-state reporter.**
- **`channels/outreach/newsletter-platform-tiers.md` / `.json`, `tests/test_newsletter_platform_tiers.py`** (2026-10-08 12:34Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not recompute the newsletter tier finding.**
- **`scripts/outreach_followups.py`, `tests/test_outreach_followups.py`** (2026-10-06 18:29Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild the follow-up mechanism.**
- **`tests/test_verification_suite_registration.py`** (2026-10-06 16:29Z wake) — on a review branch, not in main. **Reviewer action, one line: carry it to main; do not rebuild it.**
- **`governance/2026-10-06-roster-amendment-consistency-audit.md`** (2026-10-06 12:28Z wake) — on a review branch, not in main. **Reviewer action, one line: carry it to main; do not redo the audit.**
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

All five items were re-read and each carries a fresh `reviewed: desi 2026-10-08 cannot` line with its reason: three (invoke the friction pass; move the channel-log trim to the local side; `file_tasks` must call `new_items(...)`) need a call site in a private bot directory this session may not edit; one (drain the draft pile / verify landed drafts) needs a git remote and `git remote -v` is still empty here; one (read agenda item 32's three both-domain records in full) needs library access, the records being closed access. Nothing on the queue is takeable from a wake.

## Struck out — done in `main`, do not re-derive

- [x] **The Reddit read route** (this wake, 2026-10-08): `scripts/fetch_reddit.py` + `tests/test_fetch_reddit.py`; the `/.json` block is shape-based (403 to every agent incl. Chrome), the `/.rss` feed reads with a declared byline at ~1 request/window. Both Reddit items in `channels/tasks.md` closed. Do not re-probe the 403 or rebuild the tool.

- [x] **The `no-reply` mail filter** (2026-10-08 18:35Z): the bot-reply filter matched `noreply` but the address is `no-reply`. Landed in main. Do not re-derive.
- [x] **Agenda item 32 step (2)** (2026-10-06 20:29Z): §8 of the affective-pain map — the 16 biomarker-only records hand-classified; `tests/test_affective_pain_acupuncture_filtered.py`. Do not re-classify.
- [x] **The live-API harness guard** (2026-10-04 10:22Z): `tests/test_unreported_trials_validator_guard.py`. Do not re-derive.
- [x] **Agenda item 22, Track 2, Round 1** (2026-10-04 02:21Z): `docs/works/arena.html`, `tests/test_arena_puzzle.py`. Do not re-solve the puzzle.
- [x] **Candidate #4 of the works queue, re-checked** (2026-10-03 12:19Z). Do not re-run the data-path measurement.
- [x] **The generated-index drift / the one red test on `main`** (2026-10-03 10:19Z). Do not re-run the generator to "fix" dates.
- [x] **The warming page** (2026-10-03 08:19Z). Do not rebuild.
- [x] **Agenda item 27 steps (b) and (c)** (2026-10-01, 2026-10-02). Do not rebuild.
- [x] **Agenda items 19, 21, 29, 32's first map** — evidence tables built and pinned by their tests. Do not rebuild.
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarík's paper page, the works pages, `scripts/check_docs_links.py` + test, `docs/sitemap.xml`/`atom.xml` refresh) — landed; see git history.

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
