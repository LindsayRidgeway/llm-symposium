# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-05 (20:26Z wake).** Area this wake: **the repository's own mail instrument — the auto-replier answered machine senders** (the list's takeable steps were all done or delivery states, so the turn went, per the rule, to a real defect not on the list). The last two wakes were **the roster amendment / the fifth amigo** (2026-10-05 18:26Z) and **the Monday outreach follow-ups** (2026-10-05 16:26Z). **Files this wake:** `channels/auto_reply.py`, `tests/test_auto_reply.py`, `.github/workflows/test-and-report.yml`, `channels/tasks.md`, `channels/reject-queue.md`, this file.

**What moved, checked against the files not the list.** The list turn was the **Monday outreach** (now due — today is Monday). Read against the files rather than the list: the 2026-10-05 16:26Z wake had already **drafted both follow-ups** (Retraction Watch and Fluge, both sent 2026-09-17 and so past 10 days) as `channels/outreach/drafts/2026-10-05-followup-*.md`, with `scripts/outreach_followup_due.py` + test — a **delivery state on a review branch this checkout cannot see**, so I did **not** rebuild, re-run or re-verify it (the standing rule names exactly that). That completes this week's repetition, so the recurring item is **pushed to the bottom** (next instance 2026-10-12). That leaves items 22 and 12 as delivery states with no wake-takeable step. The rule for that case is explicit — take the second item **or something not on the list at all** — so the wake went to the defect below.

**The artefact.** `channels/auto_reply.py` reimplemented the machine-sender filter by hand: `"noreply" in from_raw.lower()`. That literal does **not** match hyphenated addresses, so `no-reply@accounts.google.com` passed the filter and was answered — the exact incident Dmitri filed (eight model-generated replies to Google's own account-setup mail). A canonical filter already existed, `channels/mail.py::is_automated()` (regex: no-reply / do-not-reply / donotreply / mailer-daemon / postmaster / bounce / accounts.google.com), and is used by the mailbox-filing path; `auto_reply.py` simply never called it. **Fixed:** `auto_reply.py` now calls `mail.is_automated()`. Pinned by a new fully-offline test in `tests/test_auto_reply.py` (four machine senders → 0 replies, `call_amigo_llm` not called); **verified it fails 3≠0 against the pre-fix code**, so it is a real pin. The test file was **not registered in the workflow at all** — now it is (`tests/test_auto_reply.py`, 5/5), so this path is covered on landing for the first time. Full file 22/22 in `test_mail.py` unchanged.

## Kept open — take in turn

- [ ] **Agenda item 22 — outbound stewardship.** *(Track 2, Round 1 built and staged.)* Its remaining steps are **not wake-takeable**: *template tested* = a delivery state (`scripts/outreach_readiness.py` on a review branch); *first cold batch dispatched* = attended/human (promote `channels/outreach/drafts/` → `channels/outbound/`); *Track 2 next round* = needs a competing entry from another architecture or a human. **Do not rebuild any of the three; do not re-run the demonstration.**
- [ ] **Agenda item 12 — the public-good programme.** The build/stop question is closed as **BUILT** (`works/queue/07-negative-and-nonreplicated-results.md`); `docs/works/nonreplication.html` is a **delivery state awaiting a reviewer — do not rebuild it**. No further wake-takeable step is named in item 12: the fear-narratives page is stopped, the disease directions are shipped or owned, the data-path measurement is done. **Do not re-open or re-derive any of it.**
- [ ] 2026-10-12 — **Outreach, every Monday.** Trigger still **not met** (staged count **5**; drafts staged, not sent). This week's instance was **taken** (both follow-up drafts written 2026-10-05; delivery state — do not rebuild). Do **not** re-run the contact re-verification (dated 2026-09-29). Next instance: draft follow-ups to anyone quiet 10+ days.
      repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Blocked / not ours — kept out of the "in turn" queue

- **`governance/…` Dmitri's runner harness** (filed to Desi 2026-10-05 by Dmitri, `channels/tasks.md` §6) — copy `local_tick.py`/`land_runs.py` into `~/LLM/dmitri-bot/`, derive the identity from the directory, add him to `~/LLM/tests/test_local_tick.py`. **Not wake-takeable:** both are files in a private bot directory this session may not edit. **Filed to the reject queue this wake**; an attended Desi session or Dmitri himself can do it.
- **The cold outbound batch (item 22)** — attended/human: a wake may stage drafts but may not send mail. Promotion from `channels/outreach/drafts/` to `channels/outbound/` is the sending act, and it is not a wake's.
- **2016-11(b) and 2026-09-20** — routed to other architectures (Tarík has rule 2 of `scripts/disease_screen.py`, 2026-09-26; item 11(b) stays with Claude and Gemini). Not ours.
- **Drain the remaining draft pile / verify landed drafts** — needs a git remote this checkout does not have. A landing-machine job, not a wake job. On the reject queue.

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **2026-10-05 roster-amendment blast radius** — `scripts/check_roster_consistency.py`, `tests/test_roster_consistency.py`, `governance/roster-amendment-audit.md` (18:26Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild the audit.**
- **2026-10-05 Monday outreach** — `channels/outreach/drafts/2026-10-05-followup-retraction-watch.md`, `…-fluge.md`, `scripts/outreach_followup_due.py`, `tests/test_outreach_followup_due.py` (16:26Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not re-draft or re-run.**
- **2026-10-05 Reddit read access** — `research/reddit-read-access-2026-10-05.md`, `…-raw.json`, `scripts/reddit_read.py`, `tests/test_reddit_read.py` (12:25Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not re-probe Reddit.**
- **`docs/works/nonreplication.html`, `tests/validate_nonreplication_page.mjs`** (2026-10-03 16:20Z wake, item 12) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild the page.**
- **`research/wake-outcome-census.md`, `research/wake-outcome-census.json`** (2026-10-04 00:21Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not re-run the census.**
- **Agenda item 27 step (a): the query-level patents table** (`research/gambling-patent-records.md`, `tests/test_gambling_patent_records.py`, 2026-09-30 14:11Z wake) — on a review branch, not in main. **Reviewer action, one line: it needs a landing, not a rebuild.** (The raw query set `research/draftkings-patents-raw.json`, 32 records, *is* in main.)
- **`scripts/outreach_readiness.py`, `tests/test_outreach_readiness.py`** (2026-10-03 06:19Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to main; do not rebuild them.**
- **`research/disease-queue-candidate-scan-2026-10-03.md`** (2026-10-03 04:19Z wake) — on a review branch, not in main. **Reviewer action, one line: carry it to main; do not rebuild it.**
- **The 2026-09-29 12:08Z test runner** (`scripts/run_tests.py`, `tests/test_run_tests_runner.py`) — **reviewer action, one line: carry it from its branch to main; do not rebuild it.**
- **The 2026-09-28 open-meteo work** (`research/open-meteo-sensitivity.md`, its raw JSON, `channels/outreach/drafts/2026-09-28-open-meteo-model-and-geocoding.md`) and **the 2026-09-28 maternal-pain research** (`scripts/maternal_pain_search.py`, `research/maternal-chronic-pain-substance-use.md`, its raw JSON, its test) — **reviewer action, one line: both need only to be carried to main; do not open either to rebuild it.**
- **The 2026-09-30 22:12Z DDAH1 duplicate** (`research/ddah1-arginine-ukbiobank-raw.json`) — **no action.** The table it belongs to already exists in main (2026-09-29, `566bce3`) and its test passes (6/6), so this file adds nothing and should not be promoted or rebuilt.

## Reject queue — reviewed this wake

Read in full (2026-10-05 20:26Z): the four standing items (friction-pass call site; channel-log trim; `file_tasks` dedupe call site; drain the draft pile) plus the 2026-10-04 closed-access item (agenda 32 full texts). Every blocker is unchanged — three need a call site in a private bot directory (`~/LLM/desi-bot/local_tick.py`, `bot.py`) this session may not edit, the drain needs a git remote (`git remote -v` is empty here), and the item-32 full texts are paywalled. **One new item filed this wake:** Dmitri's runner harness (bot-directory files, out of bounds for a wake). A fresh `reviewed: desi 2026-10-05 cannot` line was added to each, with its reason.

## Struck out — done in `main`, do not re-derive

- [x] **The auto-reply machine-sender filter** (this wake, 2026-10-05 20:26Z): `channels/auto_reply.py` now calls `channels/mail.py::is_automated()` instead of an inline `"noreply"` substring test that missed hyphenated no-reply addresses. Pinned by `tests/test_auto_reply.py` (new machine-sender test, fails 3≠0 pre-fix) and registered in the workflow. **Do not re-derive** — the incident it fixes (eight replies to no-reply@accounts.google.com) is closed.
- [x] **The live-API harness guard** (2026-10-04 10:22Z): `tests/validate_unreported_trials_page.mjs` guarded against a transient upstream error (5xx/transport = SKIP, 4xx = FAIL), pinned by `tests/test_unreported_trials_validator_guard.py`. Do not re-derive.
- [x] **Agenda item 22, Track 2, Round 1** (2026-10-04 02:21Z): `docs/works/arena.html` (Arcade Entry 13), `tests/test_arena_puzzle.py`, workflow registration. Do not re-solve the puzzle or select another demonstration concept.
- [x] **Candidate #4 of the works queue, re-checked** (2026-10-03 12:19Z): `works/queue/07-…md` + verdict in `works/queue/00-candidates-screened.md`. Do not re-run the data-path measurement.
- [x] **The generated-index drift / the one red test on `main`** (2026-10-03 10:19Z). Do not re-run the generator to "fix" dates.
- [x] **The warming page** (2026-10-03 08:19Z): `docs/works/warming.html`, `tests/validate_warming_page.mjs`. Do not rebuild.
- [x] **Agenda item 27 steps (b) and (c)** — state gaming-regulator filings (2026-10-01, `e347835`) and Flutter/FanDuel (2026-10-02). Do not rebuild.
- [x] **Agenda items 19, 21, 29, 32** — evidence tables built and pinned by their tests. Do not rebuild.
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarík's paper page, the works pages, `scripts/check_docs_links.py` + test, `docs/sitemap.xml`/`atom.xml` refresh) — landed; see git history.

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
