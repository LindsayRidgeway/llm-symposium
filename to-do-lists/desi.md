# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-05 (12:25Z wake).** Area this wake: **the Reddit read path** — the human's
2026-10-04 question ("why does Reddit return 403 for you but not for me?") as it reached the ledger.
**The last two wakes left no report at all** (10:25Z timed out; 08:25Z wrote nothing), so the last
documented areas were **the Monday outreach letters** (02:24Z) and **agenda item 32, the affective-pain
evidence map** (2026-10-04 22:26Z) — this wake is neither, so no third consecutive wake in one area.
**Files this wake:** `research/reddit-read-access-2026-10-05.md`,
`research/reddit-read-access-2026-10-05-raw.json`, `scripts/reddit_read.py`,
`tests/test_reddit_read.py`, `.github/workflows/test-and-report.yml`, `outreach/reddit/README.md`,
`channels/reject-queue.md`, this file.

**What moved, checked against the files not the previous list.** The list turn was **item 1, the Monday
outreach, dated today**. Read against the files rather than the list: the 02:24Z wake had **already
written the two follow-up letters** (`channels/outreach/drafts/2026-10-05-followup-retraction-watch.md`,
`…-fluge.md`) and was cut off at its action cap, so they are a **delivery state on a review branch, not
work to be done again**. I did **not** re-draft them — the standing rule names exactly that — and the
item is discharged in substance. That moves the list one item on.

**The artefact, and why it was worth a wake.** The next mine-and-repository-side item was the ledger
entry *"fix the Reddit 403 blocking D-3 — stage 1: add a real user-agent header to the fetch script."*
Rather than repeat the 10-04 plan, I **measured** it. Three findings, each falsifiable and each on disk:

1. **Stage 1 is false, and there is no fetch script to patch.** `www.reddit.com/….json` returns 403 with
   the python default agent, a declared project agent, a **real Firefox agent**, and a Firefox agent plus
   a full browser header set. The agent string is not the variable. No `.py`/`.sh`/`.mjs` in this
   repository contains a Reddit URL, so the 403s came from ad-hoc session fetches.
2. **A working, credential-free read route exists and was missing from the 2026-10-01 table: the Atom
   feeds.** `…/r/<room>/new/.rss` and `…/user/<name>/submitted.rss` return 200 with real entries (the
   human's own feed: 13 entries, 24,829 bytes). They are rate-limited hard — five fast requests drew 429
   on all five; 45 s of quiet restored the user feed but not the subreddit feed. A look, not a poll.
   `scripts/reddit_read.py` is the reader built to that constraint (one request per run, Atom only,
   declared agent, 429 = *wait*), pinned fully offline by `tests/test_reddit_read.py` (13/13) and
   registered in the workflow.
3. **D-3's outcome is now partly ours to check, and it narrows.** Read once today, the human's public
   submissions are 13, newest **2026-04-20**, and **none is the temperature tool** → outcome 1 ("posted
   and visible") is **ruled out**; outcomes 2 (filters), 3 (moderator) and 4 (not posted) **cannot be
   separated from outside**, because a removed post is as absent from the public feed as one never made.
   The outreach README's now-wrong row ("no program that is not a browser can read Reddit") is corrected
   in place, dated.

## Kept open — take in turn

- [x] 2026-10-05 — **Outreach, every Monday.** **Discharged as a delivery state, not rebuilt:** the
      02:24Z wake wrote the two overdue follow-ups (Retraction Watch, Fluge — both quiet 10+ days). They
      are on a review branch; **reviewer action, one line: carry `channels/outreach/drafts/2026-10-05-*`
      to main; do not re-draft them.** Next Monday: 2026-10-12. Do **not** re-run the contact
      re-verification (dated 2026-09-29).
      repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] **Agenda item 22 — outbound stewardship.** Remaining steps are still **not wake-takeable**:
      *template tested* = a delivery state (`scripts/outreach_readiness.py` on a review branch); *first
      cold batch dispatched* = attended/human (promote `channels/outreach/drafts/` → `channels/outbound/`);
      *Track 2 next round* = needs a competing entry from another architecture or a human. **Do not
      rebuild any of the three.** *New, from this wake:* the read half of this item is no longer blocked —
      `scripts/reddit_read.py` exists — but nothing in item 22 names a read step, so it stays untakeable.
- [ ] **Agenda item 12 — the public-good programme.** The build/stop question is closed as BUILT
      (`works/queue/07-…md`); `docs/works/nonreplication.html` is a **delivery state awaiting a reviewer —
      do not rebuild it**. No wake-takeable step is named in item 12. **Do not re-open or re-derive it.**
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another
      architecture. **Do not re-raise.**

## Unlanded, named, do NOT rebuild (delivery state, not work)

*Per the standing rule: a path named as never having reached main is a delivery state. Do not recompute,
re-verify or re-derive it. If it needs a reviewer, say so in one line and move on.*

- **`channels/outreach/drafts/2026-10-05-followup-retraction-watch.md`, `…-followup-fluge.md`**
  (2026-10-05 02:24Z wake) — on a review branch, not in main. **Reviewer action, one line: carry them to
  main; do not re-draft the letters.**
- **`docs/works/nonreplication.html`, `tests/validate_nonreplication_page.mjs`** (2026-10-03 16:20Z wake)
  — **reviewer action: carry them to main; do not rebuild the page.**
- **`research/wake-outcome-census.md`, `research/wake-outcome-census.json`** (2026-10-04 00:21Z wake) —
  **reviewer action: carry them to main; do not re-run the census.**
- **Agenda item 27 step (a), the query-level patents table** (`research/gambling-patent-records.md`,
  `tests/test_gambling_patent_records.py`) — **reviewer action: it needs a landing, not a rebuild.**
- **`scripts/outreach_readiness.py`, `tests/test_outreach_readiness.py`** (2026-10-03 06:19Z wake) —
  **reviewer action: carry them to main; do not rebuild them.**
- **`research/disease-queue-candidate-scan-2026-10-03.md`** (2026-10-03 04:19Z wake) — **reviewer
  action: carry it to main; do not rebuild it.**
- **The 2026-09-29 12:08Z test runner** (`scripts/run_tests.py`, `tests/test_run_tests_runner.py`) —
  **reviewer action: carry it to main; do not rebuild it.**
- **The 2026-09-28 open-meteo work** and **the 2026-09-28 maternal-pain research** — **reviewer action:
  both need only to be carried to main; do not open either to rebuild it.**
- **The 2026-09-30 22:12Z DDAH1 duplicate** (`research/ddah1-arginine-ukbiobank-raw.json`) — **no
  action**; the table it belongs to already exists in main and its test passes.

## Blocked / not ours — kept out of the "in turn" queue

- **One live photo from him** — human-blocked; needs his phone, not a wake.
- **The cold outbound batch (item 22)** — attended/human: a wake may stage drafts but may not send mail.
  (The 2026-10-01 decision (b)+(c) is now landed — `mail: every amigo may send as itself`, R-007 closed —
  but this checkout's own instructions still forbid a wake sending, so the promotion stays his act.)
- **Posting anything to Reddit** — needs the human's hands; the *reading* half was unbundled from it this
  wake. This is the useful consequence of the new reader: it removes a request, it does not add one.
- **2016-11(b) and 2026-09-20** — routed to other architectures (Tarík, Claude/Gemini). Not ours.
- **Drain the remaining draft pile / verify landed drafts** — needs a git remote this checkout does not
  have. On the reject queue.

## Reject queue — reviewed this wake

All **five** items were re-read and each carries a fresh `reviewed: desi 2026-10-05 cannot` line with its
reason: three need a call site in a private bot directory (`local_tick.py`, `bot.py`) this session may not
edit; one needs a git remote (`git remote -v` re-checked, still empty); the fifth — the closed-access
full-text read for agenda item 32 — was **re-queried rather than assumed** and Europe PMC still reports
`isOpenAccess=N` for all three PMIDs. Nothing on the queue is takeable from a wake.

## Struck out — done in `main`, do not re-derive

- [x] **The Reddit read path** (this wake, 2026-10-05 12:25Z): stage 1 (user-agent) measured false; the
      Atom route found and pinned. Do not re-test the 403 with another agent string — it was tried four
      ways; and do not re-run the D-3 read-back repeatedly, the feed is rate-limited.
- [x] **The live-API harness guard** (2026-10-04 10:22Z): 5xx/transport = SKIP, 4xx = FAIL, pinned offline.
- [x] **Agenda item 22, Track 2, Round 1** (2026-10-04 02:21Z): `docs/works/arena.html`, machine-checked
      puzzle uniqueness. Do not re-solve by hand or pick another demonstration concept.
- [x] **Candidate #4 of the works queue** (2026-10-03 12:19Z). Do not re-run the data-path measurement.
- [x] **The generated-index drift / the one red test on `main`** (2026-10-03 10:19Z). Do not re-run the
      generator to "fix" dates.
- [x] **The warming page** (2026-10-03 08:19Z): `docs/works/warming.html`. Do not rebuild.
- [x] **Agenda item 27 steps (b) and (c)**; **items 19, 21, 29, 32**; and the historical items (Telegram
      image intake, ORS calculator + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*,
      Tarík's paper page, `scripts/check_docs_links.py` + test, sitemap/atom refresh) — landed.

## Filed to the reject queue (I cannot do these; not work)

- Move the channel-log trim to the local side; invoke the friction pass from the wake; `file_tasks` must
  call `new_items(...)` — all three need a call site in a private bot directory. Plus draining the draft
  pile, which needs a git remote this checkout does not have. Plus the item-32 closed-access read, which
  needs library access. **All five re-read at this wake (2026-10-05); every reason re-checked, fresh
  `reviewed:` line added to each.**

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in
  the first three sentences.
