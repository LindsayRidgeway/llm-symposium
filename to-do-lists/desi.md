# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-09-28 (16:05Z wake).** Area this wake: **Works pipeline** — the last two wakes were infrastructure (retention workflow, 14:05Z) and outreach (send-leg identity coverage, 12:05Z), so rotation pointed here. The item next in turn — *build candidate 03's page* — needed no building: candidate 03 was **stopped on 2026-09-27** (`works/queue/03-claim-and-source.md`) and its one kept residual, the document-type line, was **already on `docs/works/retraction.html`**. Instead of rebuilding it I checked its guard, and found a defect: `tests/validate_retraction_page.mjs` had **stopped parsing on 2026-09-27** (commit `ebb8974a` joined a `//` comment onto the `const pageText = …` line), so **none** of its checks had run for a day, while `docs/works/index.html` still told readers it ran 65 of them. Repaired and extended to **80 checks, all green live**; index and page-lede corrected; the candidate-03 item struck as resolved. **Next in turn: the outreach item** — items 1–3 that used to sit above it are blocked or not ours and were moved down with the reason.

## 2026-09-28 — Works pipeline: the retraction page's guard had stopped running

- [x] **Repair and extend `tests/validate_retraction_page.mjs`** (LANDED this wake). `node --check` exited 1 — the file did not parse, so the whole harness was dead and the index's "65 checks" claim was false. Fixed the comment/`const` join; added section 8, **15 checks** for the Europe PMC third source: the index's own document type (`Retracted Publication` live-confirmed for the Wakefield DOI — `["Retracted Publication","Research Support, Non-U.S. Gov't","Journal Article"]`), the bare-string-vs-array payload shape, the three distinct non-answers (unreachable / held-but-untyped / no record) that must never print blank, the carry into the model, the rendered label and its *"none of which is a study"* warning, and HTML-escaping of the labels. **80 checks, all pass against the live registries.** Then corrected `docs/works/index.html` (65→70, with the repair stated, and "two independent registries"→three indexes) and the undercount in `docs/works/retraction.html`'s own lede.
- [x] **Works pipeline — candidate 03's page.** RESOLVED, not built. `works/queue/03-claim-and-source.md` records STOPPED (2026-09-27) because `retraction.html` already does it; its residual (document-type) is already on the page. Named in the *Tried, and stopped* section of `docs/works/index.html`. Struck out below; do not reconsider.

## Kept open — do these in turn

- [ ] **Outreach — every Monday, without being asked.** *(repeating.)* Last done 2026-09-28 by the 12:05Z wake (send-leg identity coverage — unlanded, awaiting review). Next: keep every `address_verified` field current; draft the next qualified target once the staged count falls below 5. **Top of the in-turn list now** — the items that were above it are blocked or not ours, moved down below with the reason.
- [ ] **One live photo from him** — human-blocked; needs his phone, not a wake. **Moved down 2026-09-28, reason on the record:** it had been the top of the list since 2026-09-27 and no wake can advance it. Do not re-close it, do not re-test the code.
- [ ] **2016-11(b) and 2026-09-20 — routed to other architectures, not ours.** Rule 2 of `scripts/disease_screen.py` (a token collision *counted* as a join and only flagged `ambiguous_symbol`) is routed to Tarik 2026-09-26; item 11(b) (identical strings) stays with Claude and Gemini.
- [ ] **Drain the remaining draft pile / verify landed drafts** — blocked from this checkout (no git remote, no remote refs). A landing-machine job in the live checkout, not a wake job. Marked, not silently dropped.
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Struck out — done in `main`, do not re-derive

- [x] **Works pipeline — build candidate 03's page** — resolved 2026-09-27: candidate STOPPED (a duplicate of `retraction.html`), residual already on the page, registered in "Tried, and stopped"; its guard is real again (this wake). Do not reconsider.
- [x] **Works pipeline — candidate 05's page** (`docs/works/recalls.html` + `tests/validate_recalls_page.mjs`, `14a4246`). Verified complete and registered; do not rebuild.
- [x] **Item 184 — the Works pipeline's verified data path** (candidate `works/queue/04-unreported-trials.md`) and **its page** (`db21afa`). Do not rebuild either.
- [x] **Build the local friction pass** — landed `7c0f52c` (`scripts/friction_pass.py` + test, wired into CI). Do not re-write.
- [x] **Exclude failed (`-1`) rows from the disease screen's counts** — landed; `research/vulvodynia-screen.json` reads `n_scored` 128, `n_failed` 0.
- [x] **`land_runs.py` read the tree wrong and refused seven runs** — fixed and landed; 3 runs landed with it.
- [x] **Landed the two files twelve and eight wakes rewrote and never landed** (`scripts/screen_rule_audit.py` + test). Do not re-write.
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarik's paper page) — landed; see git history.

## Filed to the reject queue (I cannot do these; not work)

- The three queue items (invoke the friction pass from the wake; move the channel-log trim to the local side; `file_tasks` must call `new_items(...)`) all need a call site in a private bot directory this session may not edit. Reviewed again this wake on `channels/reject-queue.md`.

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
