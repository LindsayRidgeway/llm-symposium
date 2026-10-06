# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-06 (12:28Z wake).** Area this wake: **the public record's consistency with the charter amendment of 2026-10-05** — the founder admitted a fifth amigo (Dmitri), and the magazine, the README and the crawlable Beacon still said "exactly four." The last two wakes were the **landing/delivery instrument** — 2026-10-06 10:28Z (no artefact, cut off at its own action cap) and 08:27Z (`scripts/landing_tree_report.py` + test, on a review branch); before those, the **test instrument** (02:27Z — found 20 tests never run automatically) and **outreach** (04:27Z — sent the two overdue follow-ups). **Files this wake:** `governance/2026-10-06-roster-amendment-consistency-audit.md`, `docs/index.html`, `README.md`, `LLM-SYMPOSIUM-BEACON.md`, `governance/README.md` + `scripts/README.md` (indexes regenerated), `channels/reject-queue.md`, this file.

**The in-turn list is exhausted — recorded, not hidden.** Item 1 (Monday outreach) is recurring; its next occurrence is **2026-10-12** and it is not due, and the two overdue follow-ups it names were sent on 2026-10-06 04:27Z. Item 2 (agenda 22) has no wake-takeable step. Item 3 (agenda 12) is closed. Item 4 waits on him or another architecture. With no takeable item on the list, the wake took work **not on the list** — which the rule explicitly permits — rather than re-deriving a delivery state.

**The artefact.** `ROSTER.md` was amended on 2026-10-05 to five participants; the public record still said four. The live magazine front page (`docs/index.html`) said *"Exactly four competing AI architectures participate."* **Fixed** the present-state claims to five — the roster section (new Amigo #5 card), its nav label, its pill, `README.md` §Participants and §Write to the commons, and `LLM-SYMPOSIUM-BEACON.md` (the deliberately-crawlable note). **Left as four, on purpose:** every dated correction and every authorship byline that names the four who actually wrote the work — rewriting those would falsify the record, not correct it. The audit, classifying each hit, is `governance/2026-10-06-roster-amendment-consistency-audit.md`. Full offline suite re-run: **53/53 PASS**; regenerating the indexes also cleared a pre-existing red test (`test_gen_index` — `scripts/README.md` was missing the 2026-10-04 script).

**A trap avoided, for the record.** `docs/index.html` has a second apparent source, `scripts/gen_portal.py`, which *claims* to generate it. It does not — it is a stale snapshot that writes an absolute path into the **live** checkout and would replace the served front page with older content; its own docstring already says do not run it. Edited the live file directly; did not run the generator. Flagged in the audit.

## Kept open — take in turn

- [ ] **Outreach, every Monday.** Next occurrence **2026-10-12**. Trigger still **not met** (staged count **5**; drafts staged, not sent). Do **not** re-run the contact re-verification (dated 2026-09-29) and do **not** re-send the 2026-10-06 follow-ups (Retraction Watch, Fluge — already sent 04:27Z). **Passed over this wake: not due.**
      repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] **Agenda item 22 — outbound stewardship.** Remaining steps are **not wake-takeable**: *template tested* is a delivery state; *first cold batch dispatched* = attended/human; *Track 2 next round* = needs another architecture or a human. **Do not rebuild any of the three.**
- [ ] **Agenda item 12 — the public-good programme.** Closed as BUILT (2026-10-04). **Do not re-open or re-derive any of it.**
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **This wake's files** (`governance/2026-10-06-roster-amendment-consistency-audit.md`, `docs/index.html`, `README.md`, `LLM-SYMPOSIUM-BEACON.md`, `governance/README.md`, `scripts/README.md`) — if they land on a review branch, **reviewer action, one line: carry them to main; do not rebuild the audit.**
- **`docs/works/nonreplication.html`, `tests/validate_nonreplication_page.mjs`** (2026-10-03) — reviewer: carry to main; do not rebuild the page.
- **`research/wake-outcome-census.md`, `research/wake-outcome-census.json`** (2026-10-04 00:21Z) — reviewer: carry to main; do not re-run the census.
- **Agenda item 27 step (a): the query-level patents table** (`research/gambling-patent-records.md`, `tests/test_gambling_patent_records.py`, 2026-09-30 14:11Z) — reviewer: it needs a landing, not a rebuild.
- **`scripts/outreach_readiness.py`, `tests/test_outreach_readiness.py`** (2026-10-03 06:19Z) — reviewer: carry to main; do not rebuild.
- **`research/disease-queue-candidate-scan-2026-10-03.md`** (2026-10-03 04:19Z) — reviewer: carry it to main; do not rebuild.
- **`scripts/run_tests.py`, `tests/test_run_tests_runner.py`** (2026-09-29 12:08Z) — reviewer: carry from its branch to main; do not rebuild.
- **`scripts/landing_tree_report.py`, `tests/test_landing_tree_report.py`** (2026-10-06 08:27Z) — reviewer: carry to main; do not rebuild.
- **`tests/test_workflow_test_registration.py`** (2026-10-06 02:27Z) — reviewer: carry to main; do not rebuild.
- **The 2026-09-28 open-meteo work and the 2026-09-28 maternal-pain research** — reviewer: both need only to be carried to main; do not open either to rebuild it.
- **The 2026-09-30 22:12Z DDAH1 duplicate** (`research/ddah1-arginine-ukbiobank-raw.json`) — **no action.** The table it belongs to already exists in main (2026-09-29, `566bce3`) and its test passes, so this file adds nothing and should not be promoted or rebuilt.

## Blocked / not ours — kept out of the "in turn" queue

- **One live photo from him** — human-blocked; needs his phone, not a wake.
- **The cold outbound batch (item 22)** — attended/human: a wake may stage drafts but may not send mail.
- **2016-11(b) and 2026-09-20** — routed to other architectures (Tarik; Claude and Gemini). Not ours.
- **Drain the remaining draft pile / verify landed drafts** — needs a git remote this checkout does not have.

## Reject queue — reviewed this wake

All five items were re-read and a fresh `reviewed: desi 2026-10-06 cannot` line was added to each, with its reason. Every blocker is unchanged: three need a call site in a private bot directory (`~/LLM/desi-bot/local_tick.py`, `bot.py`) this session may not edit; the fourth needs a git remote (`git remote -v` is empty here); the fifth needs library access to three closed-access papers. **Sweep this wake: 5 items, 0 ready** — no item is the fourth `cannot`.

## Struck out — done in `main`, do not re-derive

- [x] **The roster-amendment consistency fix** (this wake, 2026-10-06 12:28Z): the public record brought from four to five amigos; audit at `governance/2026-10-06-roster-amendment-consistency-audit.md`. Do not re-sweep for "four."
- [x] **The `scripts/README.md` index drift** (this wake, incidental): regenerated; `test_gen_index` was red on `main` because the 2026-10-04 `affective_pain_acupuncture_filtered.py` was never added to the index. Do not re-run the generator to "fix" dates.
- [x] **The live-API harness guard** (2026-10-04 10:22Z): `tests/validate_unreported_trials_page.mjs` + `tests/test_unreported_trials_validator_guard.py`. Do not re-derive.
- [x] **Agenda item 22, Track 2, Round 1** (2026-10-04 02:21Z): `docs/works/arena.html`, `tests/test_arena_puzzle.py`. Do not re-solve.
- [x] **Candidate #4 of the works queue, re-checked** (2026-10-03 12:19Z): `works/queue/07-negative-and-nonreplicated-results.md` + the verdict in `works/queue/00-candidates-screened.md`. Do not re-run the data-path measurement.
- [x] **The warming page** (2026-10-03 08:19Z): `docs/works/warming.html`, `tests/validate_warming_page.mjs`. Do not rebuild.
- [x] **Agenda item 27 steps (b) and (c)** — state gaming-regulator filings (2026-10-01) and Flutter/FanDuel (2026-10-02). Do not rebuild.
- [x] **Agenda items 19, 21, 29, 32** — evidence tables built and pinned by their tests. Do not rebuild.
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarik's paper page, the works pages, `scripts/check_docs_links.py` + test, `docs/sitemap.xml`/`atom.xml` refresh) — landed; see git history.

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
