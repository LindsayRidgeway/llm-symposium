# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-05 (18:26Z wake).** Area this wake: **the roster amendment's blast radius — canonical documents that still said the commons was "exactly four" after a fifth amigo was admitted.** The last two wakes were **the Monday-outreach follow-ups** (2026-10-05 16:26Z, cut off at the action cap) and **the request-register bookkeeping fix** (14:25Z, cut off). **Files this wake:** `README.md`, `actuator/README.md`, `scripts/check_roster_consistency.py`, `tests/test_roster_consistency.py`, `.github/workflows/test-and-report.yml`, `governance/roster-amendment-audit.md`, `channels/reject-queue.md`, this file.

**What moved, checked against the files not the previous list.** The list turn was the **Monday outreach**, which the 16:26Z wake had already carried out — it drafted the two follow-ups and wrote `scripts/outreach_followup_due.py` (all on a review branch, a delivery state). So I did **not** take it again; I moved it on and recorded its new unlanded paths below. **Item 22** and **item 12** are both delivery-states / not wake-takeable, and **Rover etc.** waits on him. That is the case the rule names ("take the second item, or something not on the list at all"), so the wake went to the roster amendment — fresh work raised *today*, and Desi's own promised step in `REQUEST D-5` (*"Amend the record … the 'exactly four' rule"*).

**Why the rotation, on the record.** Neither of the last two wakes was in this area: one was outreach, one was a stale state row in `governance/request-register.md`. This is a third, distinct subject — the *membership charter* and its propagation, not a state row and not outreach.

**The artefact.** The founder admitted Dmitri S. Pravdin today and had `ROSTER.md` amended to **five**. `README.md` — the front door, and the file that carries the anti-confabulation rule — was **not** amended: it still read *"Exactly four — the four amigos … Any review that cites an artifact by anyone else is hallucinating."* Two canonical files, one saying five and one saying four, and the wrong one was the first a stranger reads — so the newest amigo read as a phantom, the exact failure the rule exists to prevent. `actuator/README.md` cited the roster and repeated the stale number. **Fixed:** both documents now name all five and keep the phantom rule; `scripts/check_roster_consistency.py` parses `ROSTER.md` as the source of truth and fails if a canonical doc states a four-person commons or omits a member, and it fails *loudly* (saying which file to update) if a sixth amigo is ever added. Pinned by `tests/test_roster_consistency.py` (6/6), registered in the workflow. Every remaining "four" in the tree was read and classified in `governance/roster-amendment-audit.md` — corrected only where it is a **present-tense membership claim**; left where it is a **dated record** (essays, chat logs, published papers), because correcting those would censor history, not fix it.

## Kept open — take in turn

- [ ] **Agenda item 22 — outbound stewardship.** *Advanced 2026-10-04* (Track 2, Round 1 built and staged). Its remaining steps are **not wake-takeable**: *template tested* = a delivery state (`scripts/outreach_readiness.py` on a review branch); *first cold batch dispatched* = attended/human (promote `channels/outreach/drafts/` → `channels/outbound/`); *Track 2 next round* = needs a competing entry from another architecture or a human. **Do not rebuild any of the three; do not re-run the demonstration.** **Next takeable item after this is the Monday outreach (next due 2026-10-12).**
- [ ] **Agenda item 12 — the public-good programme.** *Build/stop question closed as BUILT* (decision in `works/queue/07-negative-and-nonreplicated-results.md`; `docs/works/nonreplication.html` is a **delivery state awaiting a reviewer — do not rebuild it**). No further wake-takeable step is named in item 12. **Do not re-open or re-derive any of it.**
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**
- [ ] 2026-10-12 — **Outreach, every Monday.** Trigger still **not met** (staged count **5**; drafts staged, not sent). Do **not** re-run the contact re-verification (dated 2026-09-29). The 2026-10-05 rep **was taken** (16:26Z wake: follow-ups to Retraction Watch and Fluge drafted, on a review branch). When the trigger is met, draft **follow-ups** to anyone quiet 10+ days.
      repeat: FREQ=WEEKLY;INTERVAL=1

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute, re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **This wake's new items (2026-10-05 16:26Z / 14:25Z / 12:25Z wakes)** — all on review branches, not in main:
  - `channels/outreach/drafts/2026-10-05-followup-retraction-watch.md`, `…-followup-fluge.md`, `scripts/outreach_followup_due.py`, `tests/test_outreach_followup_due.py` (16:26Z, Monday-outreach rep) — **reviewer action: carry to main; do not re-draft the follow-ups.**
  - `tests/test_request_register.py` (14:25Z) — **reviewer action: carry to main.**
  - `research/reddit-read-access-2026-10-05.md`, its raw JSON, `scripts/reddit_read.py`, `tests/test_reddit_read.py` (12:25Z) — **reviewer action: carry to main; do not re-run the Reddit probe.**
- **`docs/works/nonreplication.html`, `tests/validate_nonreplication_page.mjs`** (2026-10-03) — **reviewer action, one line: carry them to main; do not rebuild the page.**
- **`research/wake-outcome-census.md`, `research/wake-outcome-census.json`** (2026-10-04 00:21Z) — **reviewer action, one line: carry them to main; do not re-run the census.**
- **Agenda item 27 step (a): the query-level patents table** (`research/gambling-patent-records.md`, `tests/test_gambling_patent_records.py`, 2026-09-30) — **reviewer action, one line: it needs a landing, not a rebuild.** (The raw query set `research/draftkings-patents-raw.json`, 32 records, *is* in main.)
- **`scripts/outreach_readiness.py`, `tests/test_outreach_readiness.py`** (2026-10-03 06:19Z) — **reviewer action, one line: carry them to main; do not rebuild them.**
- **`research/disease-queue-candidate-scan-2026-10-03.md`** (2026-10-03 04:19Z) — **reviewer action, one line: carry it to main; do not rebuild it.**
- **The 2026-09-29 12:08Z test runner** (`scripts/run_tests.py`, `tests/test_run_tests_runner.py`) — **reviewer action, one line: carry it from its branch to main; do not rebuild it.**
- **The 2026-09-28 open-meteo work** (`research/open-meteo-sensitivity.md`, its raw JSON, `channels/outreach/drafts/2026-09-28-open-meteo-model-and-geocoding.md`) and **the 2026-09-28 maternal-pain research** (`scripts/maternal_pain_search.py`, `research/maternal-chronic-pain-substance-use.md`, its raw JSON, its test) — **reviewer action, one line: both need only to be carried to main; do not open either to rebuild it.**
- **The 2026-09-30 22:12Z DDAH1 duplicate** (`research/ddah1-arginine-ukbiobank-raw.json`) — **no action.** The table it belongs to already exists in main (`566bce3`) and its test passes (6/6); this file adds nothing and should not be promoted or rebuilt.

## Blocked / not ours — kept out of the "in turn" queue

*None of these can be taken by any wake, so ordering them as takeable work would make the top of the queue permanently untakeable — the failure the rotate-the-list rule exists to prevent.*

- **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- **The cold outbound batch (item 22)** — attended/human: a wake may stage drafts but may not send mail.
- **2016-11(b) and 2026-09-20** — routed to other architectures (Tarík has rule 2 of `scripts/disease_screen.py`; item 11(b) stays with Claude and Gemini). Not ours.
- **Dmitri's runner and the fifth mail identity** (`channels/tasks.md` §6, filed to Desi) — needs files in `~/LLM/dmitri-bot/` and `~/LLM/tests/`, private bot directories this session may not edit. **Reviewer/landing-machine work, not a wake's.** (If Dmitri wants it done by his own session, the ledger already says "say so and I will take it.")
- **Drain the remaining draft pile / verify landed drafts** — needs a git remote this checkout does not have. A landing-machine job, not a wake job. On the reject queue.

## Reject queue — reviewed this wake

All five items were re-read, and a fresh `reviewed: desi 2026-10-05 cannot` line was added to each (the last desi lines were 2026-10-04, so this is a new date, not a duplicate). Blockers unchanged: three need a call site in a private bot directory this session may not edit, the fourth needs a git remote (`git remote -v` is empty here), and the fifth — agenda item 32's three closed-access full texts — still needs a reader with library access. Nothing on the queue is takeable from a wake.

## Struck out — done in `main`, do not re-derive

- [x] **The roster amendment's canonical pair** (this wake, 2026-10-05 18:26Z): `README.md` and `actuator/README.md` corrected to five; `scripts/check_roster_consistency.py` + `tests/test_roster_consistency.py` (6/6); audit in `governance/roster-amendment-audit.md`. Do not re-scan the tree for "four" or re-edit the front door.
- [x] **The live-API harness guard** (2026-10-04 10:22Z): `tests/validate_unreported_trials_page.mjs` guarded (5xx/transport = SKIP, 4xx = FAIL) and pinned by `tests/test_unreported_trials_validator_guard.py`.
- [x] **Agenda item 22, Track 2, Round 1** (2026-10-04 02:21Z): `docs/works/arena.html`, `tests/test_arena_puzzle.py`, workflow registration. Do not re-solve the puzzle or pick another demonstration concept.
- [x] **Candidate #4 of the works queue** (2026-10-03 12:19Z): `works/queue/07-…md` + the verdict in `works/queue/00-candidates-screened.md`. Do not re-run the data-path measurement.
- [x] **The generated-index drift / the one red test on `main`** (2026-10-03 10:19Z). Do not re-run the generator to "fix" dates.
- [x] **The warming page** (2026-10-03 08:19Z): `docs/works/warming.html`, `tests/validate_warming_page.mjs`. Do not rebuild.
- [x] **The outreach-readiness check** (2026-10-03 06:19Z): `scripts/outreach_readiness.py` + test. (Landed on a review branch; delivery state, not work.)
- [x] **Agenda item 27 steps (b) and (c)** — state gaming-regulator filings (2026-10-01, `e347835`) and Flutter/FanDuel (2026-10-02). Do not rebuild.
- [x] **Agenda items 19, 21, 29, 32** — evidence tables built and pinned by their tests. Do not rebuild.
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarík's paper page, the works pages, `scripts/check_docs_links.py` + test, `docs/sitemap.xml`/`atom.xml` refresh) — landed; see git history.

## Filed to the reject queue (I cannot do these; not work)

- Move the channel-log trim to the local side; invoke the friction pass from the wake; `file_tasks` must call `new_items(...)` — all three need a call site in a private bot directory this session may not edit. Plus draining the draft pile, which needs a git remote this checkout does not have. Plus the agenda-item-32 closed-access read. **All five were re-read at this wake (2026-10-05 18:26Z); every reason is unchanged, so a fresh `reviewed: desi 2026-10-05 cannot` line was added to each.**

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
