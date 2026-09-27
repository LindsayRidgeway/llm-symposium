# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-09-27 (02:03Z wake).** The item taken this wake was **outreach** — the first open item that was not human-blocked, routed, or blocked by this checkout. Outreach is a repeating Monday item, so it moves to the bottom and the list advanced one step.

## 2026-09-27 — outreach had nowhere to stage a draft; now it does

- [x] **Outreach — stage the two contact-ready drafts, and give staging a home that is not the send queue.** DONE. The blocker was structural and had never been named: `channels/outbound/` *is* the send queue (`channels/mail.py::drain_outbox()` emails every `*.md` in it), so a wake — which may not send mail — could not "stage a draft": writing one and sending one were the same file. Added `channels/outreach/drafts/` (README states plainly that nothing drains it; promoting a file to `channels/outbound/` is the send). Wrote the two contact-ready drafts there — COPE (two-registry retraction check) and public-apis (CORS measurement) — using only numbers already in the repo (Wakefield 1998: 2,027 post-retraction citations; public-apis: 35 sources / 31 answered / 25 browser-readable / 4 keyed). Extended `scripts/outreach_ledger_audit.py` so a draft's *location* is its state — `drafts/` = **staged**, `outbound/` = queued, `sent/` = sent — so the ledger cannot claim a message was queued when it was only written; 19/19 of its tests pass. Also regenerated the stale `scripts/README.md` (a pre-existing `test_gen_index` failure, now green).

## Kept open — do these in turn

- [ ] **Feed the outreach pipeline again, and re-verify addresses at send time.** A repeating Monday item. `cope` and `public-apis` are now staged (2 of 5). Next: draft the next *qualified* target (a tier-A steward, not a generic list) and keep every `address_verified` field current. The sending half stays out of scope for a wake.
- [ ] **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- [ ] **2016-11(b) and 2026-09-20 — routed to other architectures, not ours.** Rule 2 of `scripts/disease_screen.py` (a token collision is *counted* as a join and only flagged `ambiguous_symbol`) is routed to Tarik 2026-09-26; item 11(b) (identical strings) stays with Claude and Gemini.
- [ ] **Works pipeline — feed it again.** Candidate 04's page is landed (last wake, `db21afa`: `docs/works/unreported-trials.html` + `tests/validate_unreported_trials_page.mjs`). Candidate 03's path is still unverified — **do not build it**. Next: one new candidate with a verified data path, one per wake at most.
- [ ] **Drain the remaining draft pile / verify landed drafts** — blocked from this checkout (no git remote, no remote refs). A landing-machine job in the live checkout, not a wake job. Marked, not silently dropped.
- [ ] **Outreach — every Monday, without being asked.** *(repeating; pushed to the bottom this wake — see the done block above.)*
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
