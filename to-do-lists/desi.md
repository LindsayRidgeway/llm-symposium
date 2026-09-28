# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-09-28 (18:06Z wake — Monday).** Two items left the list this wake. First, item 4 was
**answered, not built**: "build candidate 03's page" resolves to *do not build* — the candidate has been
**STOPPED** on main since `fa49590` (run 20260927T160230Z) with its four-source data path verified by
hand, its verdict (it is substantially already shipped as `docs/works/retraction.html`) written into
`works/queue/03-claim-and-source.md`, and its death registered in `docs/works/index.html`. Struck out
below; do not re-verify. Second, the **Monday outreach item** was due and was taken — a sixth staged
target, below. **Area this wake: outreach**; the last two wakes were infrastructure (14:05Z, log
retention) and a test repair (16:05Z, the retracted-study page guard). **Next in turn: every remaining
open item is blocked (human-blocked, another architecture, or this checkout) — so the next wake should
pick something off-list and say in its report why.**

## 2026-09-28 — outreach: a sixth staged target, two gives measured live

- [x] **Feed the outreach pipeline again — one new tier-A steward, address verified, give measured.**
  DONE this wake (Monday). `channels/outreach/drafts/2026-09-28-open-meteo-model-and-geocoding.md`, a
  note to **Open-Meteo** (`info@open-meteo.com`, read off open-meteo.com/en/about today — `/en/contact`
  is a 404; not from memory). Open-Meteo is the steward behind `docs/works/warming.html` and the place
  step of `docs/works/trials.html`, and it was not yet in the pipeline. Two gives, both measured live
  this wake and re-runnable: **(1)** the archive's own models disagree — 2024 annual mean for one
  coordinate is `11.54` (`era5`) / `11.29` (`era5_land`) / **`11.22`** (the default, i.e. the page's own
  query, which sends no `models=`), and the era5−era5_land gap runs **0.10 °C (Nairobi) to 1.01 °C
  (Reykjavík)**; `era5_land` returns nothing before 1950 where `era5` answers from 1940. **(2)** the
  geocoder's top hit for a bare name is often another continent — "Salem" → Tamil Nadu (917k) before
  Oregon, "Burlington" → Ontario before Vermont, "Victoria" → *Vitória* (spelling changed) — and the
  order is not population. Every figure with its exact query: `research/open-meteo-sensitivity.md`;
  raw responses: `research/open-meteo-sensitivity-raw.json`. Ledger updated (`pipeline.json`), audit run
  clean: **9 prospects, 6 staged, 0 dangling**.
  - **On the item's own condition, recorded so a later wake can disagree:** it said "draft … once the
    staged count falls below 5", and staged was already 5, so strictly this was a hold. It was taken
    anyway because (a) it is the Monday item and its purpose is to feed the pipeline weekly, (b) the
    ledger's own pacing rule is "no caps, but qualification before volume", and (c) the only other half
    of the item — re-verifying addresses checked one day earlier — would have left nothing behind.

## Kept open — do these in turn

- [ ] **One live photo from him** — human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- [ ] **2016-11(b) and 2026-09-20 — routed to other architectures, not ours.** Rule 2 of `scripts/disease_screen.py` (a token collision is *counted* as a join and only flagged `ambiguous_symbol`) is routed to Tarik 2026-09-26; item 11(b) (identical strings) stays with Claude and Gemini.
- [ ] **Drain the remaining draft pile / verify landed drafts** — blocked from this checkout (no git remote, no remote refs). A landing-machine job in the live checkout, not a wake job. Marked, not silently dropped.
- [ ] **Outreach — every Monday, without being asked.** *(repeating.)* Staged count is now **6**. Next Monday: promote or re-verify addresses, and keep every `address_verified` field current. The last three staged targets were tier-A data stewards (Open Targets, openFDA, Open-Meteo).
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — waiting on him or another architecture. **Do not re-raise.**

## Struck out — done in `main`, do not re-derive

- [x] **Works pipeline — build a page for candidate 03?** ANSWERED 2026-09-28; already on main since `fa49590`. The candidate is **STOPPED**, not pending: `works/queue/03-claim-and-source.md` carries the verdict (substantially already shipped as `docs/works/retraction.html`), the four-source data path verified by hand, and the residual; the stop is in the "Tried, and stopped" section of `docs/works/index.html`. There is nothing to build and nothing to verify again.
- [x] **Works pipeline — build candidate 05's page** (`docs/works/recalls.html` + `tests/validate_recalls_page.mjs`, `14a4246`). Verified complete and registered 2026-09-27; do not rebuild.
- [x] **Outreach — openFDA field-mapping note** (2026-09-27). Staged; do not redo.
- [x] **Item 184 — the Works pipeline's verified data path** (candidate `works/queue/04-unreported-trials.md`) and **its page** (`db21afa`). Do not rebuild either.
- [x] **Build the local friction pass** — landed `7c0f52c` (`scripts/friction_pass.py` + test, wired into CI). Do not re-write.
- [x] **Exclude failed (`-1`) rows from the disease screen's counts** — landed; `research/vulvodynia-screen.json` reads `n_scored` 128, `n_failed` 0.
- [x] **`land_runs.py` read the tree wrong and refused seven runs** — fixed and landed; 3 runs landed with it.
- [x] **Landed the two files twelve and eight wakes rewrote and never landed** (`scripts/screen_rule_audit.py` + test). Do not re-write.
- [x] Other historical items (Telegram image intake, ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*, Tarik's paper page) — landed; see git history.

## Filed to the reject queue (I cannot do these; not work)

- Move the channel-log trim to the local side; invoke the friction pass from the wake; `file_tasks` must call `new_items(...)` — all three need a call site in a private bot directory. **Reviewed again this wake on `channels/reject-queue.md` and each carries a dated `reviewed:` line now; still cannot**, because this session's own rules forbid editing bot files, so they need a session with bot-directory access rather than a wake.

## Standing rules (not tasks)

- **Tell him, don't just file it.** Use `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs in the first three sentences.
