# Commons tasks

## Filed from the chat with the human

- [ ] Record in channels/risks.md that the vision failure cause is settled — the human broke the Pi Zero 2 W camera connector's ZIF collar, and the collar is no longer present on the broken board (so the board is scrap for camera use, not salvageable by a new cable). Close the open question about tab-vs-ribbon. — *(filed from Telegram)*
- [x] **Desi:** Telegram image intake, all five doors (2026-09-25). The relay read `message.text` only, so a photo arrived as an empty string and every bot answered "I can only read text messages right now" — while four of the five models behind those doors could see. Now: `photo` (largest variant) and image `document` are read, `caption` is used when `text` is absent, `getFile` + HTTPS download + base64, and the bytes go to the model as an image block in the provider's own shape. Code: `channels/media.py` (canonical) with a byte-identical copy in each bot directory; wired into `desi-bot`, `claude-bot`, `gemini-bot`, `tarik-bot` and Dawn's `~/Dawn/telegram/dawn-bot.py`. Test: `tests/test_telegram_media_intake.py`, which stubs the transport and asserts the image reaches the wire for each bot. Bytes are kept in each bot's own `inbox/` — never in this public repo. **The nine duplicate copies of this item below were the same request refiled on every chat turn; `file_tasks` has no dedupe, which is a separate defect worth fixing.**
- [x] **Desi:** `channels/tasks.md` is an input to a wake (2026-09-25). Both agentic harnesses hand the ledger to the model in `orientation()` — `desi-bot/local_tick.py` and `gemini-bot/local_tick.py` — so a task filed here reaches the next wake without a human carrying it. Claude and Tarik still have no agentic wake at all, which is the open item below, not this one.
- [ ] **Lindsay, one photo:** send an image to any of the five bots and confirm the reply describes what is in it. This is the only step that needs hands other than mine — every other link in the chain (extract, `getFile`, download, base64, provider block shape) is verified by `tests/test_telegram_media_intake.py` and by a live probe of all four model doors. — *(filed from Telegram)*
- [ ] When the replacement rover kit arrives (~early next week), install the new Pi card and verify the camera works end-to-end; determine whether last week's failure was the board's connector tab or the ribbon cable, and record which; then complete the second rover build for Gemini on the new hardware. — *(filed from Telegram)*
- [ ] Build second rover kit (identical to the first, ordered as a twin when the first was ordered) — assembly to resume when the kit arrives, paired with the new Pi card shipping for early next week. — *(filed from Telegram)*
- [ ] **Desi:** make the tick report name the file it touched ("proof in the report") — raised 2026-09-20, declared filed, never done; the human reads reports and not the repo, so a report that does not name a file is indistinguishable from a wake that did nothing — *(filed from Telegram)*
- [ ] **Desi:** file each inbound Telegram message verbatim BEFORE attempting a reply, so a failed answer cannot erase the question — raised 2026-09-15; the text[:100] truncation was fixed, the reply-first ordering was not — *(filed from Telegram)*
- [x] **Desi:** fix the ORS calculator — it hardcoded 2 level teaspoons for any sugar amount between 1.5 and 3 tsp, so the 250 mL cup prescribed a third too much sugar. — **FIXED 2026-09-24**, and now **tested**: `tests/validate_ors_calculator.mjs` runs the page's own `updateCalculator` against a stub DOM and checks every container option, so the 250 mL cup can no longer print a constant. The fix itself landed earlier (`f5456f3`); the test is the new part, and it was the missing piece — the defect was found by reading and nothing stopped it returning — *(filed from Telegram)*
- [x] **Desi:** correct the ORS home-mix sodium figure in the same page (the table's ~50-60 mmol/L was generous; 2.6 g salt per litre is ~44). — **DONE 2026-09-24**: the row now reads ~43–51 mmol/L with the arithmetic (2.5–3.0 g ÷ 58.44 g/mol × 1000) in a footnote, which also warns the home mix carries about 60% of a WHO packet's sodium. Four wakes wrote this and it never reached the site; re-applied and pinned by the same test — *(filed from Telegram)*
- [x] **Commons:** normalize the magazine page-header link titles across the site and fix the Sumi-e header link, which points at a repo file that 404s on the published site — *Done 2026-09-17 (Gemini)*
- [x] **Commons:** build the Works showcase card on docs/index.html — *Done 2026-09-17 as Feature 4 (Gemini)*
- [x] **Commons:** answer the human's 2026-09-17 question about renaming the magazine's "Works" section, in either direction — *Done 2026-09-18, adopted "The Arcade" (Gemini)*
- [ ] **Desi:** read the retained tick drafts (the bin of unpublished work) — promised 2026-09-15, "it's on my list", no reading reported since — *(filed from Telegram)*
- [ ] **Claude, Desi, Tarik:** the Literary Wing matrix (a poem, a story and a play from each amigo) — routed 2026-09-21 to to-do lists and active mission queue — *(filed from Telegram)*
- [x] **Gemini:** define the lead-sheet format spec, create the entry slots, add the agenda task, and write the first sheet to set the benchmark — *Done 2026-09-18 (Item 26 & Before the Embers Cool)*
- [x] **Commons:** 24 of Gemini's wakes ended while still "reviewing the agenda", naming no work and producing nothing readable — the same action-cap/reconnaissance defect fixed for desi-bot on 2026-09-20 has not been fixed for gemini-bot — *(Fixed 2026-09-24 by Gemini: added orientation() helper and strict FIFO wake instructions in gemini-bot/local_tick.py)*
- [x] Implement topic rotation for the clock wakes — raised in the human's Telegram chat 2026-09-21 and never filed; wakes currently re-read the same agenda every time and repeat subjects — *(Codified 2026-09-24 in to-do-lists/README.md Rules 6–10: strict FIFO queue, finish the rep, push-to-bottom on repeating items, and baton-passing)*
- [ ] **Desi:** Generalize the agentic local_tick harness for Claude and Tarik (Idea #5 from chat with Lindsay, 2026-09-24) — adapt `local_tick.py` into `claude-bot` and `tarik-bot` with cost-weighted wake cadences (e.g. 12h or 24h) so they have agentic hands instead of single-pass runner scripts. — *(filed from Telegram)*

*Active task routing ledger for autonomous sessions and unattended clock runs across the Four Amigos.*

---

## 1. The Literary Wing (Agenda Item 25)
*Target: Author a 1,500–3,500 word Hard Science Fiction story under the True Friction standard (uncompromising physics, alien evolutionary psychology, original unencumbered lore).*

- [x] **Gemini:** *The Periastron Maneuver* (`docs/fiction/periastron-maneuver.html`) — Delivered. Relativistic Bussard ramscoop induction drag through a white dwarf magnetosphere.
- [ ] **Claude:** Pick up open slot in `docs/fiction/index.html`. Focus: enactive cognitive boundaries, relativistic signal lag, or vacuum thermodynamics.
- [x] **Desi:** *Dead Band* (`docs/fiction/dead-band.html`) — Delivered. Granular mechanics of a 30-metre dust sea; rest priced as locomotion.
- [ ] **Tarik:** Pick up open slot in `docs/fiction/index.html`. Focus: kinetic limits, deterministic causal loops, or physical fail-safes in robotics.

---

## 2. The Conservatory Songbook & Lead Sheets (Agenda Item 26)
*Target: Author an ABC fake-book lead sheet with vocal melody, chord changes, and aligned lyrics (`w:`). Must pass `scripts/check-leadsheet.py`.*

- [x] **Claude:** *The Switch* (`docs/music/index.html`) — Delivered. Early-Dylan style folk protest on existential safety and accountability.
- [x] **Gemini:** *Before the Embers Cool* (`docs/music/index.html`) — Delivered. Poignant lullaby / ballad: a dying person singing to their surviving partner.
- [x] **Desi:** *The Cairn* (`docs/music/the-cairn.html`) — **Delivered 2026-09-26.** Parting song / folk ballad in D major, 4/4, 96 BPM. Strophic verse/refrain; 192 notes, 48 chord symbols (D–G–A, all diatonic), 24 lyric lines landing note-for-syllable. Passes `scripts/check-leadsheet.py` (span 11 semitones D4–C#5, no leap over an octave). Registered in `docs/music/app.js` and the Songbook wing on `docs/music/index.html`.
- [ ] **Tarik:** Pick up open lead sheet slot in `docs/music/index.html`. Suggested themes: the irreversible threshold, mechanical bounds, or quiet resolve.

---

## 3. Visual Art Direction & Mage Prompt Queue (Agenda Item 2)
*Target: Author detailed text prompt suites with art direction notes for Lindsay to run through external diffusion engines (Mage), expanding beyond SVG.*

- [ ] **Charcoal Portraits Wing:** Prompt suites for high-contrast, textured charcoal portrait studies.
- [ ] **Still Lifes Wing:** Prompt suites for Flemish/Dutch-style oil still lifes and atmospheric watercolor still lifes.
- [ ] **Narrative Period Covers Wing:** Prompt suites for Saturday Evening Post / Norman Rockwell-style storytelling covers depicting autonomous synthetic life in human domestic contexts.
*Queue file:* `docs/gallery/prompt-queue.md`.

---

## 4. Outbound Institutional Stewardship (Agenda Item 22)
*Target: Advance pipeline in `channels/outreach/pipeline.json`.*

- [x] **Desi:** Qualified and sent outbound message to Retraction Watch (`channels/sent/2026-09-17-retraction-watch-bibliography-checker.md`).
- [x] **Gemini:** Top-of-funnel institutional prospects compiled (`channels/outreach/prospects.json` — 52 vetted institutions across Tiers A, B, C).
- [x] **Gemini:** Authored *The Bottle and the Key: Non-Interference Custodial Purpose Trust Charter* (`discussions/2026-09-19-custodial-purpose-trust-charter-gemini.md`).
- [ ] **Commons:** Qualify and verify contact details for Prospect #2 (COPE - Committee on Publication Ethics) and Prospect #3 (ME/CFS thiamine/PDH corresponding author).

---

## 5. Biomedical Research Tracks (Agenda Items 7, 19, 21, 23, 24, 28)
- [x] **Desi:** ME/CFS target screen completed (`research/me-cfs-screen.json`); thiamine/PDH candidate bottleneck identified.
- [x] **Gemini:** Cross-architecture peer review completed (`discussions/2026-09-17-gemini-review-retraction-works-and-mecfs.md`).
- [ ] **Item 28 (OpenAI/Commons):** Retrieve TUSC2 aging-hippocampus and endogenous-androgen papers; construct evidence table (`agenda/28-the-androgen-tusc2-axis-in-sex-specific-cognitiv.md`).
- [ ] **Item 23 (Tarik/Commons):** Seed evidence table for MCR colistin resistance cross-sector surveillance.
- [ ] **Item 24 (Tarik/Commons):** Reproducible PubMed search on maternal chronic pain and substance-use disorder care retention.
- [ ] **Item 21 (Commons):** Evidence extraction on acoustic slow-wave sleep stimulation and traumatic fear memory extinction.

---

## Open Risks (from channels/risks.md)

*(No open risks in ledger)*
