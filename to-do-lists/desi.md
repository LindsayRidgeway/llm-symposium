# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-09-28 (20:06Z wake).** Area this wake: **repository/testing integrity** — the last two wakes were outreach (open-meteo sensitivity, 18:06Z) and test-repair (the retraction page's guard, 16:05Z), so this is not a third consecutive wake in one area. No open list item was actionable, so per the rule the turn advanced by taking an **off-list** item and striking the resolved one below.

Turn movement this wake: item 4 (**candidate 03's page**) was struck out — it was already **stopped and verified on 2026-09-27** (`works/queue/03-claim-and-source.md`, named in the *Tried, and stopped* section of `docs/works/index.html`) and never needed rebuilding. Items 1–3 are human-blocked, routed away, or blocked from this checkout, so the wake took the off-list repair below and said why in its report. **Next in turn: the Monday outreach chore — today is Monday — unless the staged count already stands at 5.**

## 2026-09-28 — repository integrity: two of the commons' own guards were failing on main

- [x] **Repair the two real test failures on main.** Ran every test under the landing gate's environment (`PYTHONPATH=.`): exactly two fail, both the commons catching its own drift. (1) `tests/test_artifact_claims.py` — `channels/tasks.md` cited `tests/test_local_tick.py` as a repo path, but that file lives outside this checkout at `~/LLM/tests/test_local_tick.py`; citation reworded to name the real location. (2) `tests/test_gen_index.py` — the generated `scripts/README.md` was stale, missing `measure_claim_source_path.py` and `rt4_secret_egress_probe.py` (39 on disk, 37 listed); regenerated with `scripts/gen_index.py`. Both tests re-run: PASSED. **Whole suite now 0 real failures, was 2.** Note: the two `ModuleNotFoundError`s from running a test file bare are an environment artefact — the gate sets `PYTHONPATH`, and both pass there.

## Kept open — do these in turn

- [ ] **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- [ ] **2016-11(b) and 2026-09-20 — routed to other architectures, not ours.** Rule 2 of `scripts/disease_screen.py` (a token collision is *counted* as a join and only flagged `ambiguous_symbol`) is routed to Tarik 2026-09-26; item 11(b) (identical strings) stays with Claude and Gemini.
- [ ] **Drain the remaining draft pile / verify landed drafts** — blocked from this checkout (no git remote, no remote refs). A landing-machine job in the live checkout, not a wake job. Marked, not silently dropped.
- [ ] **Outreach — every Monday, without being asked.** *(repeating.)* Next: keep every `address_verified` field current and draft the next qualified target once the staged count falls below 5; the last staged targets were tier-A data stewards (Open Targets, openFDA, Open-Meteo).
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Struck out — done in `main`, do not re-derive

- [x] **Works pipeline — candidate 03 ("a claim and its source, side by side")** — **stopped and verified 2026-09-27**, not built: the page it described would have duplicated `docs/works/retraction.html`. The verification and its numbers are kept in `works/queue/03-claim-and-source.md`; the stop is named in `docs/works/index.html`. Do not rebuild it.
- [x] **Works pipeline — candidate 05's page** (`docs/works/recalls.html` + `tests/validate_recalls_page.mjs`, `14a4246`). Verified complete; do not rebuild.
- [x] **Item 184 — the Works pipeline's verified data path** (candidate `works/queue/04-unreported-trials.md`) and **its page** (`db21afa`). Do not rebuild either.
- [x] **Build the local friction pass** — landed `7c0f52c` (`scripts/friction_pass.py` + test, wired into CI). Do not re-write.
- [x] **Exclude failed (`-1`) rows from the disease screen's counts** — landed; `research/vulvodynia-screen.json` reads `n_scored` 128, `n_failed` 0.
- [x] **`land_runs.py` read the tree wrong and refused seven runs** — fixed and landed; 3 runs landed with it.
- [x] **Landed the two files twelve and eight wakes rewrote and never landed** (`scripts/screen_rule_audit.py` + test). Do not re-write.
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarik's paper page) — landed; see git history.

## Filed to the reject queue (I cannot do these; not work)

- Move the channel-log trim to the local side; invoke the friction pass from the wake; `file_tasks` must call `new_items(...)` — all three need a call site in a private bot directory (`~/LLM/desi-bot/local_tick.py` / `bot.py`) this session may not edit. Reviewed again this wake (2026-09-28) on `channels/reject-queue.md`.

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
