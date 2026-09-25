# Commons tasks

## Filed from the chat with the human

- [ ] Fix Telegram relay so incoming images reach the model: handle `photo`/`document` fields and `caption` (not just `message.text`), call `getFile`, download the bytes, and pass them as image input rather than string. — *(filed from Telegram)*
- [ ] Close the work-loss gap: items agreed in Telegram land in `channels/tasks.md` but neither `tasks.md` nor `risks.md` is an input to a wake. Route Telegram-filed work onto `to-do-lists/desi.md` (or add `tasks.md` to the wake's inputs) so filed work actually reaches a wake. — *(filed from Telegram)*
- [ ] Fix the Telegram relay so inbound images are actually delivered to the model: read `photo`/`document` (not just `text`), call `getFile`, download the bytes, and pass them as image input rather than a string. Also capture `caption`. Verify with a real photo sent from Telegram. — *(filed from Telegram)*
- [ ] Close the plumbing gap where work agreed in Telegram never reaches a wake — `channels/tasks.md` is not an input to a wake, and nothing currently promotes its lines onto `to-do-lists/desi.md`. Either add tasks.md to the wake's inputs or add an automatic promotion step, then document it so "nothing needed from you" can't be said falsely again. — *(filed from Telegram)*
- [ ] Extend the Telegram channel relay to receive images — handle Telegram `photo`/`document` fields and `caption` (not just `text`), call `getFile` and download the bytes, then pass the image to the model as an image input. Owner: Desi. — *(filed from Telegram)*
- [ ] Wire `channels/tasks.md` into `to-do-lists/desi.md` so a filed task reaches a wake without a human hand-carrying it. Owner — *(filed from Telegram)*
- [ ] Add Telegram image handling to the channel relay — read the `photo`/`document` fields (and `caption`, not only `text`) instead of dropping image messages; call `getFile`, download the bytes, and pass them to the model as an image input rather than a string. — *(filed from Telegram)*
- [ ] Copy the open items from channels/tasks.md onto to-do-lists/desi.md each cycle, so ledger work actually reaches a wake — currently the ledger is not one of the three things a wake reads. — *(filed from Telegram)*
- [ ] Extend the Telegram poller to handle image messages: parse the `photo` array (take the largest size variant) and `document` entries with image mime types, and read `caption` when `text` is absent — it currently reads only `message.text`, so pictures arrive as empty strings and are dropped silently. — *(filed from Telegram)*
- [ ] For any image-bearing update, call Telegram's `getFile` to obtain a file path, download the bytes over HTTPS, base64-encode them, and pass the result as an image content block to a vision-capable model instead of a text string. — *(filed from Telegram)*
- [ ] Verify end-to-end — send a photo from Telegram and confirm the reply describes the actual image content, — *(filed from Telegram)*
- [ ] When the replacement rover kit arrives (~early next week), install the new Pi card and verify the camera works end-to-end; determine whether last week's failure was the board's connector tab or the ribbon cable, and record which; then complete the second rover build for Gemini on the new hardware. — *(filed from Telegram)*
- [ ] Build second rover kit (identical to the first, ordered as a twin when the first was ordered) — assembly to resume when the kit arrives, paired with the new Pi card shipping for early next week. — *(filed from Telegram)*
- [ ] **Desi:** make the tick report name the file it touched ("proof in the report") — raised 2026-09-20, declared filed, never done; the human reads reports and not the repo, so a report that does not name a file is indistinguishable from a wake that did nothing — *(filed from Telegram)*
- [ ] **Desi:** file each inbound Telegram message verbatim BEFORE attempting a reply, so a failed answer cannot erase the question — raised 2026-09-15; the text[:100] truncation was fixed, the reply-first ordering was not — *(filed from Telegram)*
- [ ] **Desi:** fix the ORS calculator — it hardcodes 2 level teaspoons for any sugar amount between 1.5 and 3 tsp, so the 250 mL cup option prescribes a third too much sugar — diagnosed 2026-09-16, never fixed — *(filed from Telegram)*
- [ ] **Desi:** correct the ORS home-mix sodium figure in the same page (the table's ~50-60 mmol/L is generous; 2.6 g salt per litre is ~44) — diagnosed 2026-09-16, never fixed — *(filed from Telegram)*
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
- [ ] **Desi:** Pick up open lead sheet slot in `docs/music/index.html`. Suggested themes: parting, material endurance, or systemic farewell.
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

- [2026-09-20] **R-006** (Desi (master repair-amigo)) OVERDUE: Actuator diff-path parser fails open on quoted paths (`apply.py:touched_files`)
  OVERDUE — reassigned to you. Fix, then mark Done in channels/risks.md.
