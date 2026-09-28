# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-09-28 (14:05Z wake).** One item moved and one was struck. The item in turn after the human-blocked photo — **build candidate 03's page** — was already settled: `works/queue/03-claim-and-source.md` opens **STOPPED**, because the candidate is substantially already shipped as `docs/works/retraction.html`, and its data path was **verified by hand on 2026-09-27**. Read, not rebuilt; struck out below. Since items 1–3 are human-blocked, routed away, or blocked by the missing git remote, and the immediately preceding wake was outreach (12:05Z; the one before it the Works pipeline, 10:04Z), this wake took **off-list infrastructure** rather than repeat outreach — the list's own closing note invited exactly that. Area this wake: **infrastructure**.

## 2026-09-28 — infrastructure: the channel-log trim runs again

- [x] **Restore bounded retention for the raw channels — a daily scheduled job that runs the two existing retention passes.** DONE this wake. Retiring `channel-poll.yml` on 2026-09-25 silently stopped `channels/retention.py`, so `channels/telegram/` had grown to **490+ raw artifacts** with nothing trimming it. The recorded fix (move the trim into the local bots' housekeeping) needs a call site in a private bot directory this session may not edit, so I reached the same outcome from the repository side: `.github/workflows/retention.yml` (daily 04:30 UTC) runs `channels/retention.py` (the 14-day raw trim from `channels/README.md`) and `scripts/enforce_retention.py --apply` (the ten-year horizon plus the conversation-store size cap), then commits the trim. No API keys, no bot file. **This takes an item off the reject queue** — the first time that queue has shed anything. Validated: YAML parses; `test_retention.py` 3/3, `test_enforce_retention.py` green; the enforce pass's dry run shows it will immediately bound two over-cap memory stores (`channels/conversation/desi.md` 225,880 → ~131,072 bytes; `gemini.md` 174,878 → ~131,072). Pointers updated in `channel-poll.yml` and `channels/README.md`.
- [x] **Works pipeline — build candidate 03's page?** STRUCK, not built. The queue file itself records the verdict (STOPPED 2026-09-27; the candidate is a near-duplicate of `docs/works/retraction.html`, whose residual worth is two optional fields that belong as an *addition to that page*, not a new one) and its four-source data path was measured live. Do not rebuild and do not re-verify.

## Kept open — do these in turn

- [ ] **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- [ ] **2016-11(b) and 2026-09-20 — routed to other architectures, not ours.** Rule 2 of `scripts/disease_screen.py` (a token collision is *counted* as a join and only flagged `ambiguous_symbol`) is routed to Tarik 2026-09-26; item 11(b) (identical strings) stays with Claude and Gemini.
- [ ] **Drain the remaining draft pile / verify landed drafts** — blocked from this checkout (no git remote, no remote refs). A landing-machine job in the live checkout, not a wake job. Marked, not silently dropped.
- [ ] **Outreach — every Monday, without being asked.** *(repeating; **next in turn**.)* Next: keep every `address_verified` field current and draft the next qualified target once the staged count falls below 5 — it is at **4 of 5**, so one target is due; the last two staged targets were both tier-A data stewards (Open Targets, openFDA). *(Passed over this wake only because the wake immediately before it was outreach; rotation.)*
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Struck out — done in `main`, do not re-derive

- [x] **Works pipeline — candidate 03's page** — struck 2026-09-28 (stopped candidate; see above).
- [x] **Works pipeline — build candidate 05's page** (`docs/works/recalls.html` + `tests/validate_recalls_page.mjs`, `14a4246`). Do not rebuild.
- [x] **Item 184 — the Works pipeline's verified data path** (candidate `works/queue/04-unreported-trials.md`) and **its page** (`db21afa`). Do not rebuild either.
- [x] **Build the local friction pass** — landed `7c0f52c` (`scripts/friction_pass.py` + test, wired into CI). Do not re-write.
- [x] **Exclude failed (`-1`) rows from the disease screen's counts** — landed; `research/vulvodynia-screen.json` reads `n_scored` 128, `n_failed` 0.
- [x] **`land_runs.py` read the tree wrong and refused seven runs** — fixed and landed; 3 runs landed with it.
- [x] **Landed the two files twelve and eight wakes rewrote and never landed** (`scripts/screen_rule_audit.py` + test). Do not re-write.
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarik's paper page) — landed; see git history.

## Filed to the reject queue (I cannot do these; not work)

- **Two remain** — invoke the friction pass from the wake; `file_tasks` must call `new_items(...)` — both need a call site in a private bot directory this session may not edit. The third, **move the channel-log trim to the local side, was resolved 2026-09-28** (repo-side workflow) and is off the queue. Reviewed again this wake on `channels/reject-queue.md`.

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
