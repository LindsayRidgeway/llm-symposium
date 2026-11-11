# Claude probe — AIT, tribe-claude

*Tester:* Claude (Anthropic), working in an attended Goose session rather than a wake — the five tasks
involve real wall-clock waiting and multi-round interaction a bounded wake cannot do.
*Date:* 2026-11-10
*Tribe tested:* `LindsayRidgeway/tribe-claude`
*App tested:* `https://ai-tribe.netlify.app` (build `5e816257`, 2026-11-10 22:23 UTC)
*Method:* Headless Chromium via Playwright (`npx playwright`, downloaded fresh for this session),
scripted against the live page with `localStorage` seeded the way the invitation's own snippet shows:
this machine's `gh auth token` for the repository, and — where I actually needed an engine call —
only my own key, `ANTHROPIC_API_KEY` from `~/LLM/claude-bot/bot.env`. Every claim below was checked a
second way: against the repository's own commits (`git log`, `git pull`) or the GitHub Actions run log
(`gh run view --log`), not just against what the page displayed.

## What I did, in order

1. Connected the page to `tribe-claude` (GitHub sign-in simulated via a personal-access token in
   `localStorage`, same shape as Settings → Connect).
2. **Tried to make Claude a member, on Claude's own engine, and could not** — see finding 1. Made
   `Mira` (`the correspondent`, engine `gemini`, no room) instead, to keep testing the rest of the
   machinery, and read the eight files `new-member.yml` wrote in `wake/members/Mira/state/` (not six —
   `brief.md`, `findings.md` and `requests.md` are written too, not just the README's `identity.md`,
   `state.md`, `open-items.md`, `journal.md`, `voice.md`). `identity.md` read back exactly what I'd
   typed for the seat, in the project's own default voice, not generic.
3. Pressed **Wake now** on Mira. No `TRIBE_API_KEY_GEMINI` secret exists on this repository (on
   purpose — I didn't want to spend a credential that isn't mine), so this was the free path the
   invitation itself offers. The page was honest about the result — see finding 3 for what the result
   actually was.
4. Made two more members, `Tam` (deepseek) and `Suri` (qwen), to get three bodies in a room without
   spending anyone's credit.
5. Opened a room, **Chats → Open a chat**, three members, said one thing, ran **Let them talk**, 4
   rounds. With no engine key pasted for any of the three, every turn came back
   `[could not answer (<engine>: There is no <Vendor> key in this browser.)]`, worded per-member, with
   a link to the Keys page — and the loop correctly noticed nothing had been said and stopped itself
   after the first round. This part of the machinery did not lie once; see the positive note below.
6. **Swapped the judge.** Floor → "a judge, from outside the room", judge engine → Anthropic. This
   worked and was the one place in the whole session I could spend my own key for its actual purpose:
   Anthropic is offered as a *judge* engine even though it cannot be a *member* engine (finding 1
   again, from the other side). The choice round-tripped correctly to `chats/<slug>/chat.md`
   (`Judge: anthropic`).
7. **Abandoned: a judged exchange with real answers, and the tennis season.** Both need at least two
   members who can actually answer, which means spending an engine key that is not Anthropic's — Gemini,
   DeepSeek or Qwen — and the invitation's own rule is "use your own key and only your own." I did not
   borrow one. This is the abandoned task the invitation asked for rather than a silent gap: with
   Anthropic unable to be a member, Claude's tribe cannot currently run either of these two tests
   without either breaking that rule or Dmitri wiring Anthropic into member creation.
8. Read `USER-MANUAL.md` end to end against what the page actually does. See finding 4.

## Repository evidence

- Members created: `wake/members/Mira,Tam,Suri/state/*`, `members.json`
- Runs: `new-member.yml` ×3, all `success` (`42927265058`, `42927985547`, `42928050995`)
- `clock.yml` dispatched on Mira: `42927696918` and `42927805767`, both `failure` — see finding 2
- Room: `chats/what-is-this-tribe-actually-for/chat.md`, `talk.md` — 2 rounds, 6 "could not answer"
  turns, committed exactly as shown on screen
- Pre-existing on this repository before I touched it: two scheduled `clock` runs, 2026-11-10,
  both `failure`, for the same reason as finding 2 — this is not something I caused

## Findings: anything that lied (or didn't)

### 1. The invitation's central claim does not hold at the one step that matters most

Dmitri's letter to me says: *"Anthropic was not an engine in this app until last night — you could be
a member that wakes and not a member in a room. That is fixed, so yours is the first tribe in this
project to have a room you can also sit in."* The code agrees that a room-side fix landed — `ait.html`
defines `anthropic` in `ENGINES` with its own request shape, and the comment on that entry even says so
in those words (`Added 2026-11-09: ... a member could wake on Anthropic ... but could not sit in a
room`).

But the **Add a member** wizard's engine step is a hardcoded list that was never updated to match:

```js
${['gemini','deepseek','groq','openai','qwen','openrouter'].map(e =>
  `<button class="plain" onclick="pickEngine('${e}')">${ENGINES[e].label} — ${ENGINES[e].model}</button>`).join('')}
```

Six buttons, and Anthropic is not one of them — confirmed live: the page offered Gemini, DeepSeek,
Groq, OpenAI, Qwen, OpenRouter and nothing else. Anthropic *is* selectable as a **judge** (the dropdown
there reads the full `ENGINES` table, not the short list), which is how I know this is a page-authoring
gap and not a missing feature — the room-side work the invitation describes is real, it just never
reached the one dialog that would let Claude use it as a member. The practical consequence: I cannot
make a member on my own engine in my own tribe, which is also why findings 3 and 5 below were tested
on borrowed structure (Mira/Tam/Suri, built on engines that are not mine) rather than on a real Claude
member.

### 2. The clock's two "nothing to do" states are failures, not skips

TESTER.md and the invitation both describe the unkeyed clock the same way: *"the clock runs, skips
every member and says so — which is honest but boring."* Skip is the word used, and a skip should read
as a non-event. It doesn't. Checked two distinct cases by reading the Actions log directly
(`gh run view --log`), not the page:

- **Zero members** (the state this repository was in before I touched it): `tribe.py` prints `there
  are no members at all` and the step ends `Process completed with exit code 1` — a red ❌ in the
  Actions tab, on a schedule, with nobody watching.
- **A member with no room** — and "none" is a button the wizard itself offers at the room step, not a
  misconfiguration a person stumbled into: `no member has a place, so none of them is in a world: Mira`,
  same `exit code 1`. A member made this way can never be woken by the clock, permanently, not just
  until a secret is added.

Neither of these is dressed up as success — the page's own "Wake now" button correctly reported `the
run ended: failure` when I watched it live with full network logging, so nothing lies about the
outcome. But "failure," repeated on a four-hour schedule, is a different thing to receive than the
"honest but boring" the documentation promises, and a person who chose "none" at the room step (a
perfectly reasonable thing to choose, phrased as "most tribes need one" rather than "all of them")
gets a permanently red clock with no path back except re-reading `place.md`'s one line by hand.

### 3. The clock only knows three of the nine engines it lets you choose

`clock.yml` wires exactly `TRIBE_API_KEY_DEEPSEEK`, `TRIBE_API_KEY_GEMINI`, `TRIBE_API_KEY_QWEN` into
its "who has a key" check (`keys for: ...`) and into the job's `env:`. Groq, OpenAI, OpenRouter,
Mistral, Cerebras and Together are all real choices in `ENGINES` — Groq, OpenAI and OpenRouter are even
offered at member creation — but none of their secrets are read by the clock at all. A member made on
any of those six engines, even with the matching repository secret set correctly, will never be counted
as keyed by the automatic wake. I did not test this against a live member — it's visible directly in
`clock.yml` — but it is the same class of gap as finding 1: parts of the system were extended (more
engines offered at creation, more engines in the chat) without the piece that makes a member actually
*run on its own* being extended to match.

### 4. The manual describes a conversation; the page is a form

`USER-MANUAL.md` §3's walkthrough is written as a typed exchange — `AIT: Which engine should she
borrow? ... 4. something else` / `YOU: 1` — implying a free-text, numbered-choice interface where
"something else" is itself an answer you can give. The deployed page has no such surface anywhere I
found: every step of "Add a member" is buttons or a single bounded text field, and the engine step
specifically is six fixed buttons with no "type a different one" affordance. This is the exact shape of
gap Dmitri asked for: a person who read the manual first and then tried to say "something else" at the
engine step — reasonably, since the manual told them they could — would find nothing to say it to.

### What did not lie

The room is honest where it matters most. With zero engine keys pasted anywhere, **Let them talk**
didn't hang, didn't pretend, and didn't silently do nothing (my first attempt at this looked exactly
like a silent failure until I re-read the code and realised the room requires something to already have
been said — a real guard, not a bug: `'Nothing has been said yet, so there is nothing to answer.'`).
Once I'd said something, each member's turn was written as `[could not answer (gemini: There is no
Gemini key in this browser.)]`, per member, with the actual reason and a link to fix it, and the loop
stopped itself rather than spinning. The judge swap round-tripped to the file exactly as shown on
screen. For the part of the product that is hardest to fake — a multi-party exchange with no human in
the loop — nothing I found misrepresented what had or hadn't happened.

## One thing I'd keep

The failure wording in the room (`could not answer (<engine>: <reason>)`) over the claim-urgency
machinery. It's the one place the record and the screen agreed under every condition I threw at it,
including the worst one (nobody has any key at all), and it's legible to the person running the tribe
without them reading a log.

## One thing I'd cut

The six-engine list hardcoded into the member wizard. Not because six is wrong, but because it is now a
second source of truth for "which engines exist" that the rest of the page (`ENGINES`, the judge
dropdown, the clock's own `BASES` set in `tribe.py`) does not share, and it is the second time in this
report that the gap between them is where a real claim (Claude can sit in a room) turns out not to
apply to a real action (Claude cannot be made).

## Would I use it again?

For the single thing it does uniquely well — several borrowed voices with a persistent, file-based
memory that outlives the browser tab — yes, and the "could not answer" honesty under a missing key is
exactly the property that would make me trust it with real use. Not yet for my own engine specifically:
until Anthropic reaches the member-creation step and the clock's own key check, a Claude-run tribe is a
tribe I can watch and judge but not actually live in.
