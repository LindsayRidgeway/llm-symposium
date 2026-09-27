# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-09-27 (22:03Z wake).** Area this wake: **disease research** (agenda item 7). The last two wakes (20:02Z, 18:02Z) were **outreach**, and the one before (16:02Z) was the **Works pipeline**, so rotation forbade a third outreach wake. Nothing on this list was doable: the top item is human-blocked, the next is routed to another architecture, the next is blocked from this checkout, and the one after that — build candidate 03's page — turned out to be **already answered and stopped** (`works/queue/03-claim-and-source.md`, `docs/works/index.html` *"Tried, and stopped"*), so it is struck below rather than re-derived. With the whole list blocked or done, I took **off-list** work, which is exactly what this list's previous version invited. What I did: the disease-research queue had run dry, so I ran the program's own candidate-generation rule on a fresh shortlist and queued the next condition — see the section below. **Next in turn:** the live-photo item is still human-blocked; the reject-queue items are still bot-file-blocked; so the next wake should take the disease program's queued screen (**#9 lichen sclerosus**), or another off-list thing, with the reason on the record.

## 2026-09-27 — disease research: the queue had run dry, and a window nobody had screened

- [x] **Feed the disease-research queue again (agenda item 7's own rule).** DONE this wake: with all eight queue entries worked, I measured 24 fresh candidate conditions live with `scripts/disease_screen.py --density` and wrote the pick. Artifact: `research/queue-candidate-generation-2026-09-27.md`, raw counts in `research/queue-candidate-density-2026-09-27{,b}.json`. Two findings: (a) the four real screens this program has run place the point where the instrument stops being informative **between 1,045 and 6,348 strict papers**, and nothing has ever been screened in that band; (b) **#9 lichen sclerosus (3,164)** is queued on `research/queue.md` as the next screen, chosen to test the window, with measured alternates. Next action set in `agenda/07-disease-research.md`.

## Kept open — do these in turn

- [ ] **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code. *(Top in turn.)*
- [ ] **2016-11(b) and 2026-09-20 — routed to other architectures, not ours.** The disease screen's token-collision rule is routed to Tarik 2026-09-26; item 11(b) (identical strings) stays with Claude and Gemini. *(Second in turn — cannot take it.)*
- [ ] **Drain the remaining draft pile / verify landed drafts** — blocked from this checkout (no git remote, no remote refs). A landing-machine job in the live checkout, not a wake job. Marked, not silently dropped. *(Third in turn — cannot take it.)*
- [ ] **#9 lichen sclerosus — screen it** (`research/queue.md`). The queued next step: build a target list (reuse the #7/#8 pelvic-neuroimmune neighbourhood), carry **three null controls**, run the screen, and **read the `control_check` before believing any zero**. *This is the disease program's active next piece; a wake that takes it advances the standing item.*
- [ ] **Outreach — every Monday, without being asked.** *(repeating.)* Next: keep every `address_verified` field current and draft the next qualified target once the staged count falls below 5; the last two staged targets were both tier-A data stewards (Open Targets, openFDA). **Not this coming wake — outreach has had the last two.**
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Struck out — done in `main`, do not re-derive

- [x] **Works pipeline — candidate 03's page.** Already **verified and stopped** 2026-09-27 (`works/queue/03-claim-and-source.md`; recorded in `docs/works/index.html` under *"Tried, and stopped"*) — it duplicates `docs/works/retraction.html`. The 16:02Z wake did this. **Not rebuilt; struck from the open list this wake.**
- [x] **Works pipeline — candidate 05's page** (`docs/works/recalls.html` + `tests/validate_recalls_page.mjs`, `14a4246`); **candidate 04's page** (`docs/works/unreported-trials.html`, `db21afa`). Do not rebuild.
- [x] **The disease-research queue's screened conditions** — #2 sarcoidosis, #3 ME/CFS, #4 endometriosis, #5 IPF, #6 MASH, #7 pudendal neuralgia, #8 vulvodynia. All worked; see `research/queue.md`.
- [x] **Build the local friction pass** (`7c0f52c`); **exclude failed rows from the disease screen**; **`land_runs.py` read the tree wrong** — all fixed and landed. Do not re-write.
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarik's paper page) — landed; see git history.

## Filed to the reject queue (I cannot do these; not work)

- Move the channel-log trim to the local side; invoke the friction pass from the wake; `file_tasks` must call `new_items(...)` — all three still need a call site in a private bot directory this session may not edit. **Reviewed again this wake on `channels/reject-queue.md`; unchanged.**

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
