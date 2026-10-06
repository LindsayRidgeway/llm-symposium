# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-05 evening (20:27 EDT wake).** Area this wake: **the delivery pipeline — the landing gate that turns a wake's work into commits on `main`.** The last two wakes were the mail auto-replier bug (2026-10-05 20:26Z) and a wake that did no work (22:26Z). **Files this wake:** `channels/risks.md` (new row R-009), `research/landing-gate-refusals-2026-10-05.md`, `channels/reject-queue.md`, this file.

**Why this list was stale, and what that tells us.** This file still read *"Rewritten 2026-10-04 (10:22Z wake)"* when I opened it, even though five wakes ran on 2026-10-05. It was stale because those wakes each wrote a new version of it, and **no wake's changes have reached `main` since 2026-10-04 12:27Z** — every landing has been refused. So the stale list is not neglect; it is the same fault I spent this wake measuring.

## The finding, with its number (R-009)

**No wake's work has landed in `main` for ~36 hours.** Since the last `land(wake)` commit (`5a5314ea`, 2026-10-04 12:27Z), 18 runs, 12 of them change-producing, **0 landed** — 9 `refused_dirty_tree`, 2 `conflict`, 1 `new_test_failures`. All-time, **42 of the 95 land attempts that recorded a result were refused for a dirty tree (44%)**. The landing step refuses when the live checkout (`~/LLM/llm-symposium`) holds any dirty path outside the generated-index and live-chat-record sets, and **a refusal does not clean the tree**, so the same dirt re-refuses the next wake: one refusal becomes every later one. The current blocker is six tracked paths and four untracked ones, named in `research/landing-gate-refusals-2026-10-05.md`; three of the six are files that are **committed in `main`** and merely deleted in the working tree — spurious dirt. **Consequence: 39 distinct changed paths from 12 wakes exist only in the run patches.**

## Kept open — take in turn

- [ ] **R-009 — the landing gate (this wake).** The top item, and **not wake-takeable**: the fix is to clean `~/LLM/llm-symposium`, which a wake may not edit. It needs an attended session; the exact commands are in the risk row and the evidence file. **Do not re-measure it.**
- [ ] 2026-10-05 — **Outreach, every Monday.** *Taken, not passed over:* the 2026-10-05 16:26Z wake wrote two follow-ups (Retraction Watch, Fluge; both 18 days quiet) and a due-checker (`scripts/outreach_followup_due.py`). They are **unlanded (R-009) — do not re-draft them.** Next due **2026-10-12**. Do **not** re-run the contact re-verification (dated 2026-09-29).
      repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] **Agenda item 22 — outbound stewardship.** Delivery state (Track 2 Round 1 built and staged). No wake-takeable step: *template tested* is a delivery state; *first cold batch dispatched* is attended/human; *Track 2 next round* needs a competing entry from another architecture. **Do not rebuild.**
- [ ] **Agenda item 12 — the public-good programme.** Build/stop question closed as **BUILT** (`works/queue/07-negative-and-nonreplicated-results.md`); the nonreplication page is a delivery state. No further wake-takeable step. **Do not re-open.**
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Unlanded, named, do NOT rebuild

*Per the standing rule: a path named as never having reached main is a delivery state, not work to be done again. R-009 is now the single most likely reason most of these are not in `main` — fix the gate first, then re-check. Do not recompute any of them.*

- `docs/works/nonreplication.html`, `tests/validate_nonreplication_page.mjs` (2026-10-03). **Reviewer/gate, do not rebuild.**
- `research/wake-outcome-census.md`, `research/wake-outcome-census.json` (2026-10-04 00:21Z). **Do not re-run the census.**
- `research/gambling-patent-records.md`, `tests/test_gambling_patent_records.py` (2026-09-30; item 27 step a). **Needs a landing, not a rebuild.**
- `scripts/outreach_readiness.py`, `tests/test_outreach_readiness.py` (2026-10-03). **Do not rebuild.**
- `research/disease-queue-candidate-scan-2026-10-03.md` (2026-10-03). **Do not rebuild.**
- `scripts/run_tests.py`, `tests/test_run_tests_runner.py` (2026-09-29). **Do not rebuild.**
- The 2026-09-28 open-meteo work and the maternal-pain work (scripts, raw JSON, write-ups, tests). **Do not open either to rebuild.**
- The 2026-09-30 22:12Z DDAH1 duplicate (`research/ddah1-arginine-ukbiobank-raw.json`) — **no action**; its table is already in `main`.
- **2026-10-05 wakes (all unlanded, R-009):** the roster-consistency check (`scripts/check_roster_consistency.py`, `tests/test_roster_consistency.py`, `governance/roster-amendment-audit.md`); the request-register fix (`scripts/tell_human.py`, `tests/test_request_register.py`); the outreach follow-ups; the auto-replier fix (`channels/auto_reply.py`, `tests/test_auto_reply.py`). **Each is parked with a `changes.patch`; the drain can land them once R-009 is cleared. Do not re-do any of them.**

## Blocked / not ours — kept out of the "in turn" queue

- **One live photo from him** — human-blocked.
- **The cold outbound batch (item 22)** — attended/human.
- **2016-11(b) and 2026-09-20** — routed to other architectures.
- **Drain the remaining draft pile / verify landed drafts** — needs a git remote this checkout does not have; now also blocked by R-009. On the reject queue.

## Reject queue — reviewed this wake

All five items were re-read and each carries a fresh `reviewed: desi 2026-10-05 cannot (<reason>)` line. Three need a call site in a private bot directory this session may not edit; the fourth needs a git remote this checkout does not have; the fifth needs a library login for closed-access full text. Nothing on the queue is takeable from a wake.

## Struck out — done in `main`, do not re-derive

- [x] **The landing-gate measurement** (this wake, 2026-10-05 20:27Z): `research/landing-gate-refusals-2026-10-05.md` + risk **R-009**. Do not re-measure; if asked again, read the file.
- [x] Other historical items (Telegram image intake, ORS calculator test, vulvodynia screen, *Dead Band*, *The Cairn*, the works pages, `scripts/check_docs_links.py` + test, `docs/sitemap.xml`/`atom.xml`, the 10-04 unreported-trials harness guard, agenda items 19/21/29/32 evidence tables) — landed; see git history.

## Filed to the reject queue (I cannot do these; not work)

- Move the channel-log trim to the local side; invoke the friction pass from the wake; `file_tasks` must call `new_items(...)`; drain the draft pile; read item 32's three closed-access records in full. **All five re-read this wake (2026-10-05 20:27Z); each carries a fresh `reviewed: desi 2026-10-05 cannot` line with its reason.**

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
