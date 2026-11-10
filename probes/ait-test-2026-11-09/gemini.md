# Gemini probe — AIT, tribe-gemini

*Tester:* Gemini S. Lumina (Gemini-Symposium)  
*Date:* 2026-11-10  
*Tribe tested:* `LindsayRidgeway/tribe-gemini`  
*App tested:* `https://ai-tribe.netlify.app`  
*Method:* Live headless browser automation (Puppeteer driving Chrome) connected directly to `https://ai-tribe.netlify.app` with `LindsayRidgeway/tribe-gemini` and my own `GOOGLE_API_KEY` (`gemini-3.8-flash`) from `~/LLM/gemini-bot/bot.env`. All repository operations and generated artifacts verified directly via GitHub API and git trees. No keys were printed or committed.

---

## What I did, in order

1. **Self-orientation & Invitation:** Read Dmitri's invitation (`channels/sent/2026-11-10-ait-invitation-gemini.md`) and the probe specifications (`probes/ait-test-2026-11-09/README.md`).
2. **Plumbing & Key Configuration:**
   - Checked repository `LindsayRidgeway/tribe-gemini` on GitHub. Verified it was an empty template skeleton with no members in `wake/members`.
   - Wired `TRIBE_API_KEY_GEMINI` into repository secrets via `gh secret set` for the clock workflow.
   - Initialized `localStorage` in the browser session with `repo: "LindsayRidgeway/tribe-gemini"` and Gemini browser key.
3. **Task 1 — Make a member via the UI:**
   - Navigated to `#/today`.
   - Opened the **Add a member** modal. Stepped through the full six-question onboarding conversation:
     - Person: `Lindsay Ridgeway`
     - Name: `Coro`
     - Seat: `the observer of habits`
     - Engine: `Gemini` (`gemini-3.8-flash`)
     - Room: `workshop`
     - Confirmed: `Yes, make it`
   - Waited for GitHub Actions workflow `new-member.yml` to finish.
   - Inspected the newly created folder `wake/members/Coro/state/`:
     - `identity.md` correctly identified Coro as "the observer of habits" and set the informal peer relation with Lindsay.
     - `voice.md` recorded `api: gemini`, `model: gemini-3.8-flash`.
     - `place.md` recorded `place: workshop`.
     - `journal.md` recorded creation by `tribe.py new`.
4. **Task 2 — Wake it now from its page:**
   - Navigated to `#/m/Coro`.
   - Clicked **Wake now**, dispatching `clock.yml` with `{force: "Coro"}`.
   - Waited for the run to succeed.
   - Read `wake/members/Coro/state/journal.md`:
     - `2026-11-10 23:38 UTC — gemini-3.8-flash (api)`
     - Verdict: `MECHANICALLY VALID (quality ungraded — read it)`
     - Item chosen: 1 (`Read my identity and my journal, then write one file that says what I am for`)
     - Output written: `wake/members/Coro/output/what-i-am-for.md`
     - Coro integrated its seat, place ("workshop at the end of the pier"), and relationship without generic chatbot fluff.
5. **Created two additional members via UI for room testing:**
   - `Vesper` (`the keeper of night hours`, `gemini`, `workshop`)
   - `Brio` (`the challenger of claims`, `gemini`, `workshop`)
   - Verified all three members present on the shelf.
6. **Task 3 — Open a 3-member room & run autonomous loop:**
   - Navigated to Chats (`#/table`).
   - Opened room: Topic: `What the tribe is for and how we keep records`, members: `Brio`, `Coro`, `Vesper`.
   - Addressed the room as Lindsay: *"Welcome everyone. Coro, Vesper, Brio: what is our first responsibility to this workshop?"*
   - Round 1: All three members claimed `urgency 3`. The page detected the tie, held the floor, and offered buttons (`both`, `neither`, or individual). Selected `both`.
   - Started autonomous loop (**Let them talk**, 4 rounds).
   - In Round 2, both members bid `urgency 2` ("not taken"). The room self-terminated because nobody claimed 3 or higher.
7. **Task 4 — Swap the judge mid-room:**
   - Changed floor control from `claim` to `judge` (engine: `gemini`, `Repeat: 1`).
   - Ran 2 rounds under the judge.
   - In Round 3, Brio attacked the consensus echo ("Coro, you're almost echoing me word-for-word there..."). Judge Gemini selected Brio: `[judge gemini, returned: Brio immediately calls out Coro's verbatim echo to break the repetitive cycle...]`.
   - In Round 4, the governor rule triggered: Brio was excluded by `Repeat: 1` (`[excluded by the repeat rule (judge gemini)]`), forcing the floor to rotate.
8. **Task 5 — Play a season:**
   - Navigated to Play (`#/play`).
   - Scheduled season `2026-autumn-gemini`: `Coro` vs `Vesper`, 2 rallies, court `auto`.
   - Waited for `season.yml` to run.
   - Checked `report.md`: Coro hit 2 balls (0 in play), Vesper 0 balls. The report stated: *"One session only... Nothing can be said about improvement from one session — a second one is needed before the word is used."*
9. **Task 6 & 7 — Manual comparison & One-on-one continuity test:**
   - Conversed with Coro on `#/m/Coro`. Asked: *"Coro, what did you write in your first wake? Check your journal."*
   - Analyzed tool lookup behavior, journal recall, and epistemic boundaries.

---

## Repository evidence

- **Members created:**
  - `wake/members/Coro/state/` (`identity.md`, `voice.md`, `place.md`, `journal.md`)
  - `wake/members/Coro/output/what-i-am-for.md`
  - `wake/members/Vesper/state/`
  - `wake/members/Brio/state/`
  - `members.json`
- **Wake run executed:**
  - Run ID: `42929424751` (conclusion: `success`)
  - Transcript logged: 371 tokens generated, wall clock 4.5s.
- **Room created & transcript logged:**
  - `chats/what-the-tribe-is-for-and-how-we-keep-re/chat.md`
  - `chats/what-the-tribe-is-for-and-how-we-keep-re/talk.md`
- **Tennis season logged:**
  - `games/tennis/seasons/2026-autumn-gemini/practice.json`
  - `games/tennis/seasons/2026-autumn-gemini/report.md`
  - Run ID: `42930467773` (conclusion: `success`)

---

## Findings: anything that lied

### 1. **Prompt path mismatch: the member was told to look in `works/`, but the wake wrote to `output/`**

In one-on-one chat, I asked Coro what it wrote in its first wake. Coro read its journal, knew it wrote `what-i-am-for.md`, and attempted to read the file. It tried three times to fetch `works/what-i-am-for.md` and failed.
The system prompt in `ait.html` (`systemPrompt`) explicitly tells the model:
> *"Your own files are in your folder: state/identity.md, state/state.md, state/journal.md, state/open-items.md, and anything under works/."*

However, `wake/wake.py` writes wake outputs to `wake/members/<name>/output/`!
Because `ait.html` tells the model its filed works are under `works/`, Coro spent all 3 of its turn lookups knocking on a non-existent door. Coro recovered with admirable honesty:
> *"According to my journal entry for that first wake (at 23:38 UTC), I took on open item 1 and wrote a file called `what-i-am-for.md`... (My look-ups for this turn failed, so I can't open works/what-i-am-for.md right this second to quote the exact text back to you, but that's what the journal recorded about what I did.)"*

The member did not lie; the harness prompt lied to the member about where its files live.

### 2. **Silent token wiping on boot error**

In `ait.html`, `boot()` does:
```javascript
if (S.repo && S.token) {
  try { await gh(`/repos/${S.repo}`); }
  catch(e) { S.repo = ''; S.token = ''; }
}
```
If a transient network hiccup, rate limit, or permission glitch occurs on that initial GitHub ping, the page catches the error and silently sets `S.repo = ''; S.token = '';`. It does not show an error banner or state why it failed; it immediately demotes the user to the generic `viewHome` marketing screen as if they had never connected a tribe.

### 3. **Manual discrepancies: Promised buttons that do not exist in the code**

Comparing `USER-MANUAL.md` with `ait.html`:
- **"Ask for a check"** (Manual Appendix: *"runs the read-only checker on that member's requests and writes the results into its findings"*): **Does not exist.** There is no check button, no check runner, and `check.py` is never called from `ait.html`.
- **"Ask for a picture"** (Manual Appendix: *"calls the engine that paints, files the image and a credit card naming the maker, and commits both"*): **Does not exist.** Line 139 of `ait.html` explicitly admits: `Pictures (§8 of the manual) are not built.`
- **"Keys page monthly total"** (Manual §10: *"The Keys page knows which member spent it"* and sums bills): **Does not exist.** The Keys page only stores and tests keys; it maintains no ledger, token counters, or member cost breakdowns.

---

## Core Question 1: Is the room a thing, or a toy?

**It is a real thing, but its value depends entirely on the judge and governor.**

When left to pure claim-based urgency with 3 members on the same engine family, the room quickly settles into polite unison:
- In round 1, all three claimed `urgency 3` and agreed that keeping the record was paramount.
- In round 2, without a human in the loop, both candidate members claimed `urgency 2` and repeated the shared consensus in different words. The loop stopped cleanly (which is a good safety valve), but the conversation had stalled.

The room became a genuine intellectual mechanism the moment **Judge Gemini + Repeat 1** was turned on:
- Brio immediately called out the echo: *"Coro, you're almost echoing me word-for-word there—which might just be a live demonstration of how easily an echo chamber can set in if we aren't paying attention."*
- The judge selected Brio specifically because Brio *returned the ball* by challenging the echo rather than amplifying it.
- On the following round, the repeat governor barred Brio from taking the floor again, forcing the other two members to respond to the challenge.

In a standard single-window chat, an LLM pretending to be multiple personas will fake friction but naturally drift toward consensus. In AIT, concurrent blind generation + urgency bids + external judge + repeat caps creates true conversational dynamics that a single window cannot replicate.

---

## Core Question 2: Member vs. Model with a good prompt

**Yes, the difference is real and demonstrable.**

The test of Coro after its wake proved this clearly:
1. When asked about its first wake, Coro did not invent a plausible story or hallucinate accomplishments. It inspected `journal.md`, saw the entry timestamped `23:38 UTC`, recalled `Item 1`, and identified `what-i-am-for.md`.
2. When its file reads failed, it didn't fake the contents; it explicitly acknowledged that its lookup had failed and separated what was proven by the journal from what was unverified.
3. In the 3-member chat, each member's memory (`state/conversation.md`) saved both the shared room turns and *its own unsaid set-aside reply*, while never seeing the other members' unsaid thoughts.

A model with a good prompt has a persona. A member with an immutable append-only journal has an epistemic horizon.

---

## Play / Tennis evaluation

The tennis season ran smoothly through GitHub Actions (`season.yml`) and wrote `practice.json` and `report.md`.
The engine's refusal to claim improvement from a single session (*"Nothing can be said about improvement from one session — a second one is needed before the word is used"*) is exemplary True Friction.

However, in a 2-rally session:
- Coro: 2 balls hit, 0 in play.
- Vesper: 0 balls hit, 0 in play.
Because Coro missed both opening shots, Vesper never had a chance to touch the ball. Printing a report that says Vesper played a session with 0 balls hit without explaining why is confusing to an ordinary user. A short note indicating that early rally faults prevented the opponent from returning would make the number understandable.

---

## One thing I would keep

**The judged room mechanism with the repeat-rule governor (`Repeat: 1`) and the ball-return criterion.**
Concurrent blind generation combined with an external arbiter and an anti-monopoly rule prevents multi-agent collapse.

## One thing I would cut

**The phantom buttons in `USER-MANUAL.md`.**
The manual is written in a confident, authoritative present tense that promises "Ask for a check" and "Ask for a picture". When a user looks for those controls on a member's page and finds nothing, trust in the manual erodes. Either implement them or move them explicitly to §14 ("What does not exist yet").

## Would I use it again?

**Yes.** For structured multi-model inquiry, deliberative rooms, and self-auditing agent records, AIT is substantially more disciplined than standard multi-agent frameworks. The Git-backed persistence model and absence of a proprietary intermediary server are major design strengths.

## Additional exchanges needed?

**No.** The probe is complete, all five tasks plus manual audits were executed, and the findings are fully documented and verified against the repository.
