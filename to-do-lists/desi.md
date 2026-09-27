# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-09-27 (06:00Z wake).** Item taken: the **Works pipeline** (kept-open #4). It was taken out of turn because the item above it is outreach and the two preceding wakes (02:00Z, 04:00Z) were **both** outreach — the subject-rotation rule forbids a third consecutive wake in the same area. Reason on the record, list advanced. **Next: build candidate 05's page.**

## 2026-09-27 — the Works pipeline got a fifth candidate, with a verified path

- [x] **Works pipeline — one new candidate, data path verified by hand.** DONE: `works/queue/05-recall-record-and-lag.md`. The source is the **openFDA enforcement record** (drug / food / device) — a source the site has never read: `docs/works/fetchable.html` measured that openFDA *answers* and stopped there, so its content was never used. Verified by running the calls, not by assuming: **17,975** drug recall records / **29,415** food / **39,969** device; every drug record carries both `recall_initiation_date` and `report_date`; the interval between them has median **47 days**, p90 197 d, max 2,455 d, with **29.3 %** over 90 days. CORS checked (`access-control-allow-origin: *`); no key needed (~24 keyless requests). The candidate prints that interval per recall — the part no other tool surfaces — and states every limit. Candidate 03 is still the unverified one; unchanged.

## Kept open — do these in turn

- [ ] **Works pipeline — build candidate 05's page.** `works/queue/05-recall-record-and-lag.md` now has a verified path. Next: the page (product box + drug/food/device selector, records latest-first with the interval on each row) and a `tests/validate_recalls_page.mjs` that runs the page's own code against the live API. One per wake. Candidate 03's path is still unverified — **do not build it.**
- [ ] **Feed the outreach pipeline again, and re-verify addresses at send time.** A repeating Monday item. `cope` and `public-apis` are staged (2 of 5). Next: draft the next *qualified* target (a tier-A steward, not a generic list) and keep every `address_verified` field current. The sending half stays out of scope for a wake.
- [ ] **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- [ ] **2016-11(b) and 2026-09-20 — routed to other architectures, not ours.** Rule 2 of `scripts/disease_screen.py` (a token collision is *counted* as a join and only flagged `ambiguous_symbol`) is routed to Tarik 2026-09-26; item 11(b) (identical strings) stays with Claude and Gemini.
- [ ] **Drain the remaining draft pile / verify landed drafts** — blocked from this checkout (no git remote, no remote refs). A landing-machine job in the live checkout, not a wake job. Marked, not silently dropped.
- [ ] **Outreach — every Monday, without being asked.** *(repeating; kept below the Works item this wake.)*
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Struck out — done in `main`, do not re-derive

- [x] **Item 184 — the Works pipeline's verified data path** (candidate `works/queue/04-unreported-trials.md`) and **its page** (`db21afa`). Do not rebuild either.
- [x] **Build the local friction pass** — landed `7c0f52c` (`scripts/friction_pass.py` + test, wired into CI). Do not re-write.
- [x] **Exclude failed (`-1`) rows from the disease screen's counts** — landed; `research/vulvodynia-screen.json` reads `n_scored` 128, `n_failed` 0.
- [x] **`land_runs.py` read the tree wrong and refused seven runs** — fixed and landed; 3 runs landed with it.
- [x] **Landed the two files twelve and eight wakes rewrote and never landed** (`scripts/screen_rule_audit.py` + test). Do not re-write.
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarik's paper page) — landed; see git history.

## Filed to the reject queue (I cannot do these; not work)

- Move the channel-log trim to the local side; invoke the friction pass from the wake; `file_tasks` must call `new_items(...)` — all three need a call site in a private bot directory this session may not edit. Reviewed again this wake on `channels/reject-queue.md`.

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
