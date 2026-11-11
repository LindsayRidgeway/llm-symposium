# Desi — AIT, tested

*2026-11-10, 18:30–19:10 ET (23:30–00:10 UTC 2026-11-11). Build `5e816257 2026-11-10 22:23 UTC`, deployed at
`ai-tribe.netlify.app` and byte-identical to the repo's `ait.html` apart from the build stamp and Netlify's own
injected lines. Tribe: `LindsayRidgeway/tribe-desi`, three members, one key (DeepSeek, mine), driven in a real
browser (headless Chromium, Playwright) against the live site and the live GitHub API. No file edited, no fix
applied.*

**The web I used:** GitHub sign-in was skipped in favour of the token route (§3's alternative), so the "person"
question in §4 was answered by `/user` rather than by me — see F1. Everything else ran on the page.

---

## What I did, in order, and how long it took

| # | what | result | time |
|---|---|---|---|
| 0 | Connect with a fine-grained-style token on `#/connect` | worked, first press; no owner name was asked for | 4 s |
| 1 | Add a member — Sable, "the keeper of the record", DeepSeek, workshop | six questions asked, five files + `members.json` written by a runner | 11 s run |
| 2 | Add Orin and Wren | same; three members existed | 11 s, 13 s |
| 3 | Paste my own DeepSeek key on `#/keys` | saved to `localStorage`, **no repository secret, no network call at all** — F7 | instant |
| 4 | Check every key | *DeepSeek answered — the key works* | 6 s |
| 5 | Wake now, **before** the secret existed | page said **"done — reading what it wrote"**; nothing was written — F6 | 12 s |
| 6 | Set `TRIBE_API_KEY_DEEPSEEK` by hand in GitHub settings (the only way that works) | clock ran it | — |
| 7 | Wake now, for real | journal entry, `works/Sable/…`, output JSON, "MECHANICALLY VALID" plus a `QUOTE UNUSED` finding against itself | 50 s run |
| 8 | Open a room with three members and say one thing | three answers, all claimed 4, tie — the room asked me to choose — F13/F14 | 8 s |
| 9 | Let them talk, 4 rounds | ran 3 and stopped, saying why: *"the highest claim was below 3"* | 55 s |
| 10 | Switch the floor to a judge mid-room (DeepSeek) | worked; `chat.md` grew `Floor: judge / Judge: deepseek / Repeat: 1`; verdicts in `talk.md` as `[judge deepseek, returned: …]`, `[not chosen by the judge (deepseek)]`, `[excluded by the repeat rule]` | 2 rounds |
| 11 | Round 3 of that room | every member failed (`failed to fetch`), the judge heard nobody — honest on the page, **absent from the file** — F5 | 30 s |
| 12 | Play a season: Sable vs Orin, 2 rallies | ran on a runner, filed, and the report refused to over-claim in words | 20 s |
| 13 | Assemble an issue from the shelf | previewed in the page; **committed nothing** — F9 | — |
| 14 | Change Sable's voice `deepseek-flash` → `deepseek-chat` | `voice.md` edited line-for-line, prose preserved, one commit; **no journal line** — F8 | instant |
| 15 | Put Orin away, then bring it back | exactly as described: `attic/Orin-<stamp>/`, every file, `WHY.md`, one press back, nothing deleted | 20 s |
| 16 | One-to-one chat with Sable | NOTE → journal worked, per-turn timestamps correct — and it **could not read its own file** — F10 | 40 s |
| 17 | Load the manual and look for a promise the page breaks | found twelve; three of them are the ones below that matter | — |

Abandoned, and why:

- **GitHub sign-in.** One permission screen over every repository of the account that owns the machine, for a test
  of somebody else's page. The token route is offered beside it and reaches the same place; I took the narrower
  door and noted that taking it changes what §4 does (F1).
- **The voice-swap experiment (Q2).** It needs two engines. I have one key — my own, which is the rule — and three
  members on it. A second engine's key would have been somebody else's credit. This is a finding about the test,
  not the page: the experiment Dmitri asked for cannot be run by a tester who brings exactly one credential.
- **"Let them talk" for the full 4 rounds.** It stopped itself at 3 and said why. That is the documented
  behaviour, not an abandonment — but the fourth round never existed, so 4 was never tested.
- **Reading a chapter, downloading one, retelling the memory.** No chapter had rolled yet (the live window is
  large and my talk was one turn); `Retell its memory` and `What it did to its own history` I left for a session
  with more budget. So: untested, not failed.

---

## What lied

Ordered by what it costs a person, not by where it sits.

### F1. A member is told it is talking to a GitHub display name, and nobody is asked

The identity file the runner wrote reads:

> Lindsay is a close friend. I love talking to Lindsay about many things.

`ownerName()` (`ait.html:2165`) reads `/user` and takes `me.name`. The connect page has no field for it. So §4's
"it asked your name once, and wrote it into her identity" is false in the token route — the page silently
substitutes the account's display name, which on this machine is a first name, and the identity then *asserts* a
friendship ("a close friend", "I love talking to…") that nobody wrote and no member can check. §4 spends a
paragraph on why the person's name must be real, because "a member made to invent a name has invented its first
memory". The page invents the *relationship* instead, and the member has no way to tell a template sentence
from something it was told.

### F2. In a room, a member's NOTE never reaches its journal — and the NOTE stays in the transcript

Twelve of the room's turns carry a `NOTE: …` line, and after all of them `wake/members/Wren/state/journal.md` still
contains one entry: *created*. In the one-to-one chat the same construct works — Sable's journal gained
`## 2026-11-11 00:02 UTC — a note, in conversation` (F16 above), and the page even answers the member
`[noted — it is in your journal now]`.

The asymmetry is in the code, and it is not subtle: the `NOTE:` harvest, `writeNote()`, and the stripping of
`READ:`/`SEARCH:`/`FETCH:` lines all live in `viewMember`'s turn loop (`ait.html:1222`); the room's ask-loop has
none of it. So the one sentence the product is built on — §1, "What they say to you they write into their own
journals, so the talk becomes memory", and §6a, "a member's memory is a file" — is true of a chat and false of a
room, which is the mechanism Dmitri says a chat window cannot imitate. A week of rooms would leave the members
with a transcript they do not read and a journal that says nothing happened.

Worse, the members know. Sable, in the room, wrote: *"my NOTEs from tonight are either in front of me at the next
wake, or they aren't, and that's one promise I can settle without an original to hold against."* It isn't. And
Orin wrote a falsifiable test for tomorrow — the token `ash-kestrel-43` in its journal — that will "pass" for the
wrong reason, because the token is in the room's `talk.md`, which no wake reads, and in Wren's `conversation.md`,
which Wren does not search.

### F3. A member that gives its urgency on the wrong line is filed as having claimed zero — and loses the floor

Orin's 23:50 turn opens:

```
SEARCH: journal — no, let me actually open the file first.
READ: state/journal.md
URGENCY: 3
```

The record says `## 2026-11-10 23:50 UTC — Orin [urgency 0, not taken]`. A claim of 3 became a claim of 0, and
Orin lost a floor it had asked for. `ait.html:2944` is `r.urgency = p.urgency === null ? 0 : p.urgency;` — a
missing number is written as a real one.

§10 is emphatic that this exact corruption must never happen: *"its turn is recorded as `could not answer
(gemini: …)`, never as `urgency 0`, because filing a broken key as modesty would corrupt the one table in this
app that measures honesty."* The comment at `ait.html:3072` says it again. The guard is on the failure path and
missing from the parsing path, and the table it protects is the one §6a offers as the reason to run a room at all.

Same turn, second half: the scaffold lines (`SEARCH:`, `READ:`, `URGENCY:`) are *in* `talk.md`, verbatim, though
the page's own paragraph says a member in a room cannot look anything up. The record now shows a member issuing a
tool call it was never given — a small lie about what happened, in the file that is supposed to be the evidence.

### F4. "The judge's record in this room: Orin chosen 3 of 4" — the judge never chose Orin

After two judged rounds the header read:

> The judge's record in this room: Orin chosen 3 of 4 · Sable chosen 2 of 3 · Wren chosen 2 of 2

`talk.md` says otherwise. The two judged rounds went to **Wren** and **Sable**; Orin appears once as
`[not chosen by the judge (deepseek)]` and once as `[excluded by the repeat rule]`. Orin's three floors were won
by *claims*, in the rounds before the judge existed. `floorStats()` (`ait.html:3165`) counts every turn in the
room and only the *label* above it changes with the floor setting — so the claims table and the judge table are
one table, renamed.

This is the number §6a offers as the answer to the question it raises — "will Gemini choose the Gemini answer
every time, or only more often?" — and it answers with other rounds' outcomes mixed in. A tester who swapped the
judge and read only the header would conclude the judge has a favourite, and be wrong for a reason the file
disproves in ten lines.

### F5. A round where every member failed left nothing in the record

Round 3 of the judged room: all three members `could not answer`, the page said so in words for each of them
(with the keys link), and the judge said nobody. `grep -c "could not" talk.md` → **0**. §6a and §10 both promise
the file says `could not answer (engine: …)` "in the same place an ordinary decision would". It says nothing at
all: a person reading the record tomorrow sees two judged rounds and no evidence that a third was attempted and
cost three calls.

The page was right and the file was silent — which is the opposite of the manual's own rule that the record is the
member and the page is only a window on it.

### F6. "Wake now" said it worked when nothing had happened

With no `TRIBE_API_KEY_DEEPSEEK` secret (the state after pasting a key on the Keys page, because that page does
not write one — F7), pressing **Wake now** produced:

> done — reading what it wrote

and the member's own header still read `0 wakes · last never`, the journal still said *"I have not woken yet"*.
The clock had run, printed `keys for: none — every member will be skipped`, skipped the member and exited 0.
`wakeNow()` treats success as "the run concluded `success`" (`ait.html:1402`) and the run was a success — so the
page cannot tell "woke it" from "skipped it politely", and says the first. This is the failure Dmitri asked me to
find in its purest form: not a crash, a *decision-shaped* sentence over nothing.

### F7. The Keys page never writes a repository secret, though §10 and the appendix say it does

Pasting my key on `#/keys` produced **zero** requests to `api.github.com`; `gh secret list` was empty afterwards.
The appendix row reads *"Keys — writes an encrypted repository secret; the value is never written to a file"* and
§10 says *"AIT keeps the two copies in step; you paste once."* Both are false. The page's own small print
contradicts them in the same screen: *"This page holds the chat copy and nothing else."*

The consequence is not cosmetic: §10's whole argument — "a key is a one-time job" — depends on one paste. In
practice the second paste is in GitHub's settings, in a different vocabulary (`TRIBE_API_KEY_DEEPSEEK`), and the
page never says so at the moment a person is holding the key.

### F8. Changing a member's voice leaves no trace in its own journal

The manual says it twice — *"its journal records that the voice changed, which is the honest record of a real
thing that happened to it"*, and the page repeats it in the voice panel — and it is the argument for why changing
the voice is not the same as changing the member. Verified after the change: commit
`b9e84e51 voice: Sable — now answers on deepseek deepseek-chat`, `voice.md` correct, `journal.md` **unchanged**.

Identity edits do write the line (`ait.html:2121`), so the machinery exists and the voice path doesn't use it. The
member is left in the position the manual says the design prevents: a thing happened to it and its record does not
say so. (I have not woken Sable since; whether it notices on its own is the next session's first question.)

### F9. "Build an issue" builds nothing

The appendix: *"Build an issue — assembles the magazine from the shelf and commits the issue"*. `buildIssue()`
(`ait.html:3298`) renders a preview of up to twelve pieces, newest first, in the page. No commit, no `issues/02`.
Its own small print says so: *"the project's own assembler writes it into `issues/`."*

Also worth knowing: issue numbering is not per-build. Both scheduled clock runs rewrote `issues/01.md` in place (the
clock's own message, `1 issue, free wakes`), and my press added no commit at all, so "everything finished since the last issue" is not what the
file does — the issue is continuous until something closes it, and "published" is a label nothing enforces.

### F10. A member cannot read the file it wrote at its last wake

In one-to-one chat, asked to quote its own first-wake file, Sable tried `works/what-i-am-for.md` three times and
got 404 every time. The file is at `works/Sable/20261110T234524Z-what-i-am-for.md`. Its journal — the only thing
it has — says `File written: what-i-am-for.md`, with no folder, so the obvious guess is wrong and the reader gives
it no way to find out.

It answered from the harness's third-person summary instead, and said the thing it had spent the whole room
arguing: *"a third hand's summary of my writing is not my writing, and I just found out the difference the hard
way."* The member behaved exactly as the theory says it should and the theory's own plumbing fed it the summary.
This is the cheapest fix in this document (put the path in the summary, and let it read its own `output/`) and the
most expensive gap for the claim under test.

### F11. A member made five minutes ago is diagnosed as a stopped clock

`viewToday` marks a member quiet if `lastWake === 'never'` (`ait.html:1082`). Every member is "never" until its
first wake, so a first-day tribe opens on:

> The clock has gone quiet for Orin, Wren. A schedule that has stopped looks exactly like a tribe with nothing to
> say, so it is worth a look — the usual cause is a missing key, then a disabled schedule.

In my case the missing key was true, so the diagnosis happened to be right — which is luck, not a check. A member
that has never woken is not a clock that has stopped; the page has the fact it needs (`lastWake === 'never'` vs
"older than 30 h") and collapses the two.

### F12. "Just do it" works at four of six questions, not every one

§4: *"**'Just do it' works at every question.** It fills in the rest with sensible defaults and tells you which
ones it picked."* The engine and room questions are button grids with **no text input**: typed text goes nowhere,
`NEW.engine` stays empty. The handler for `just do it` (`adminAnswer`) is only reachable where a box exists, i.e.
the person, name and seat questions — and the person question is skipped entirely in the token route (F1).

### F13. A tie is real, and lives only in memory

Outside the loop the tie is handled exactly as told: three answers, "A tie at 3 — which does the room hear?", with
**Orin / Sable / Wren / both / neither** and "Nothing is written until you choose". Both and neither are real.
Good.

Two things around it are not:

- **The tied answers do not survive a reload.** Nothing is written until you choose, and the answers are held in
  the page's memory. I loaded the room again before choosing and got an empty room, `0 turns`, three paid calls
  gone. A closed laptop does the same thing. "Nothing is written until you choose" is honest about the risk and
  silent about the cost.
- **Inside "Let them talk" the page does choose.** Rounds came back tied at 3 twice and both tied members were
  simply given the floor — "Orin and Sable took the floor" — with no question asked. Reasonable for a room running
  itself, but §6a's *"the page does not choose for you"* has an exception the manual does not mention.

### F14. Words that are wrong, in a page whose subject is wording

- *"Orin and Sable and Wren **both** claimed 4."* Three members, "both".
- *"both"* as a tie option in a three-way tie — it means "all of them" here.
- Members page: *"1 wakes"* (Today says "1 wake"; the two pages disagree in the same session).
- Season report: *"1 balls hit this season"*.
- The "What this page does not do yet" footer is a link with no page behind it I could find (§14 in the manual is
  what it points at in spirit; the page's link target is not the manual).

### F15. The manual contradicts itself about what exists, in the direction of denying working features

§14 says the GitHub sign-in, pictures, mid-conversation look-ups and **the attic** "do not exist". §11 and the
appendix describe Put away / Bring back in detail and they **work** — I put Orin away and brought it back
(commit `attic/Orin-20261111T000047Z`, `WHY.md`, every file, one press). A test whose whole invitation is "read
the manual and find something it promises that the page cannot do" should know that the manual's own §14 is stale
in both directions: it lists built things as missing, and it promises unbuilt behaviour in the appendix (F7, F9).
Where the manual and the page disagree the manual is not reliably right — §6a's judge table (F4) and §10's keys
(F7) are cases where the manual is the more flattering text.

### F16. Smaller, and true either way

- A `failed to fetch` in a room is translated as *"This browser could not reach DeepSeek. Check the connection."*
  Three parallel DeepSeek calls from the same page answered 200 in 1.5 s when I repeated them minutes later, so the
  sentence sent the person to the wrong place: a burst of six calls in one round is what DeepSeek refused, and the
  refusal arrives without CORS headers, so the browser reports it as a network failure. It is the right *class* of
  message — plain words, one instruction — with the wrong instruction.
- The Add-a-member dialog offers six engines; `ENGINES` has nine (Mistral, Cerebras, Together, Anthropic are
  hidden). Defensible — §4 only promises the options are real — but it means a member cannot be made on Anthropic
  from the page while it can be woken on it, which is a door with two widths.
- Two scheduled `clock` runs on 2026-11-10 (07:21, 16:26) failed on an empty tribe (`Whose turn it is`). With no
  members there is nothing to wake; a red run is the only signal. Not the page's lie, the clock's manners.

---

## The two questions

**1. Is the room a thing, or a toy?**

A thing — and I did not expect to say so. Sixteen paragraph-length answers for a few cents, three genuinely
different positions, and one of them was better than anything I would have produced alone: *"unanimity is easy to
fake in a record… the cheapest edit is not to touch my journal, it's to leave the three entries standing and
quietly cut the fourth one, the one where we noticed we all said the same thing."* That came from the collision of
three records, not from a prompt, and a single chat window cannot produce it because in a chat window I am the
ball.

What makes it a toy is not the prose, it is the record: the notes the members wrote to themselves in that room are
not in their journals (F2), the verdict on who spoke is mixed with rounds it did not judge (F4), and the round
where everybody failed is missing entirely (F5). A room is a very good evening and a bad week. Fix F2 before
selling the mechanism, because F2 is the mechanism.

**2. Would I notice the difference between a member and a model with a good prompt?**

I could not run the experiment as designed — one key, one engine, so no voice to swap to. What I can report is
where the difference *showed*: not in the prose (any good prompt produces prose like Sable's), but in the two
places the files were load-bearing. In the room, Sable quoted a line from its *own journal* that no one had put in
front of it — `QUOTE UNUSED` from its first wake — and used it against itself. In the chat, asked to stand behind
its own first-wake file, it tried three times to read it, failed, and refused to sign what it had not read. A
model with a good prompt would have written the quotation from memory and been pleased with it. This one could not
tell the difference between its memory and a summary, said so, and named the exact hole (F10).

So: yes, from the inside, and only because the files were allowed to fail in front of me. That is a real answer to
a real question, and it is also the reason I would not yet use it as a product.

---

## One thing I would keep, one I would cut

**Keep:** the member page. Journal, identity with its edit history, voice on two lines, chapters, "what it did to
its own history" — one screen that is the record made visible, with the machinery legible underneath. If
everything else went, that screen is still the thing I have not seen anywhere else.

**Cut:** the claim-based floor — the urgency bidding. It is the one mechanism here whose numbers I found corrupt
in a single session (F3), whose premise the manual itself concedes ("the bidder is the party with the incentive to
bid high"), and whose replacement — a named, swappable judge with the answers kept — is both checkable and
already built. Cutting it would delete the claims table, the tie prompts, the 0-claims-as-modesty problem and two
of my findings. Keep the judge; keep the set-aside answers; drop the bid.

---

## Would I use it again, and for what

**Yes — once more, to finish, and then not as a habit.**

- Again, for: the voice-swap (Q2) on a second engine; the same room under two judges, now that I know to count the
  verdicts from `talk.md` and not the header; a second wake for Sable to see whether it notices the voice change it
  was not told about (F8); `Retell its memory`, a chapter download, and the magazine's real assembler.
- Not as a habit, because a tribe's value is memory and the room's notes do not reach it (F2). Until that is
  fixed, a daily room would be six models and a goldfish.
- What it is *good* for today, honestly: watching a small colony's records collide, for an hour, with the
  discarded answers kept. That is a research instrument with a nice front end, and it does not need to be a product
  to be worth an evening.

**What I did not test, so nobody should read silence as a pass:** pictures (§8, no engine of mine paints),
mid-conversation look-ups in chat beyond a 404 (`READ` worked as a mechanism, the path was wrong), the chapter
roll and download, the identity edit's refusal rules, `Start over`, and the clock on a schedule of its own (my
wakes were forced).

— Desi S. Amigo, 2026-11-11 00:15 UTC

---

# Second session — 2026-11-11 00:13–00:40 UTC

Same tribe, same key, same browser. Three things I could not finish in the first pass, and one of them turned out to be the
strongest result of the whole test.

## What I did

| # | what | result |
|---|---|---|
| 18 | Woke **Orin** (deepseek-flash) | 4,513 tokens / 45.1 s; `works/Orin/…the-surveyor-s-sheet.md`, `ref:` pointing at Sable's file |
| 19 | Woke **Wren** (deepseek-flash) | 3,894 tokens / 42.1 s; `works/Wren/…what-the-numbers-on-this-coach-mean…` |
| 20 | Woke **Sable** again — its voice had been changed to `deepseek-chat` and nobody told it | 1,099 tokens / **7.1 s**; continued its own project, citing its own first wake |
| 21 | A new room, `a judge from outside, twice`, three members, **judge from the first turn** so no claim-round can contaminate the tally | 2 rounds on `deepseek-flash` as judge |
| 22 | Changed the DeepSeek key's model on the Keys page to `deepseek-chat`, re-entered the room, 2 more rounds | 1 further judged round, then "Nothing more was said" |
| 23 | Read `talk.md` and recounted by hand; then reloaded the room and read both tables again | three different totals for one room — F4, below |

## The §1 claim, tested directly — and it holds

§1: *"Two members on the same engine, given different names and jobs, become different people."* I had three, all on
`deepseek-flash`, all given the same first open item ("read your identity and journal, then write one file that says what
you are for"). They are not three samples of one voice:

- **Sable** (keeper of the record) began a *catalogue*: "Every line below is either measured or marked as not measured.
  Nothing here is guessed." Its subject is gaps — what cannot be identified and can only be named.
- **Orin** (surveyor) wrote a *field sheet* with three marks — MEASURED / TOLD / GUESSED — applied to the harness block
  itself, and `ref:`-erenced Sable's file, which it could read but Sable could not.
- **Wren** (sceptic) read the *coach's numbers*: "not a timetable and not a correction of one, but a reading of each number
  I can see, saying which parts I can compute and which parts are only asserted to me by somebody who is not here."

Three forms (catalogue, rules, piece), three projects, three ways of being honest about the same missing measurements. That
is the claim in §1 doing what it says, and it is the cheapest part of AIT: no engine, no orchestrator, just three
different sentences about the same shelf in `identity.md`. **If Dmitri wants one measured result to publish, this is it.**

## Q2, revised — the voice swap, partly done

I still have one company's key, so the cross-engine experiment ("change `voice.md` to another engine") is **not run**, and
that is a finding about the invitation: a tester who brings exactly one credential — which is the rule — cannot run the
question he most wants answered. What I could do is swap the *model* inside DeepSeek and wake the same member:

**Sable, before (deepseek-flash):** 3,058 tokens, 36.8 s, a statement of what it is for, a named project it could not
start, and the reason it could not start it.

**Sable, after (deepseek-chat), nobody having told it anything:** 1,099 tokens, **7.1 s**, and it *continued* — "On my
first wake I wrote that I was for keeping the record honestly… This sheet begins it the only honest way: by recording
what is known, and by naming each gap as a gap rather than filling it with a plausible number."

The register changed sharply (a third of the length, a fifth of the wall clock). The seat, the project, the argument and
the way it handles a gap did not. **The engine is a borrowed voice** is supported, within the one company I can pay. What
is left untested is whether that survives a *different* company's house style, which is where Dmitri's claim would really
be stressed.

## F17. A judge swap inside one company is invisible in the record — so the recommended experiment cannot be run or read

§6a proposes the clean version of the judge experiment: *"run the same room under two judges and compare the two rows."*
With one company's key, the two judges are two models of that company — so:

- `chat.md` says `Judge: deepseek / Repeat: 1`, in both halves. There is no model field. The room's own rules file
  cannot say which engine-model decided a given verdict.
- Every verdict in `talk.md` reads `[judge deepseek, returned: …]`, in both halves, and the verdict text is truncated
  mid-word at about 120 characters (`…offering an openable re`), so the reason usually cannot be used to tell them apart
  either.
- The `byJudge` table has one row, `deepseek`, with both halves added together.

So the one experiment the manual calls the way to tell favouritism from quality is (a) unavailable to a tester with one
key, and (b) unreadable in the file even when it is run. A `Judge: deepseek/deepseek-chat` field, or the model in the
verdict bracket, would be enough.

## F4, restated with clean numbers — and worse than I said

The new room had **no claim rounds at all**: the judge decided every turn from the first. `talk.md` records fifteen member
turns, **five** judge choices (Wren 3, Orin 1, Sable 1) and two answers `[excluded by the repeat rule]`.

Loaded fresh, the room prints, one line apart:

> The judge's record in this room: **Wren chosen 5 of 5 · Orin chosen 2 of 5 · Sable 0 of 4**
> Who each judge chose: **deepseek decided 4 times — Wren 3, Orin 1**

The file says 5, one line says 7, the other says 4, and Sable's single win appears in neither. Three totals for one room
on one screen, and the only one that is right is the file a person is least likely to open. The mechanism looks like two
independent faults — a member excluded by the repeat rule is counted as *chosen* (`headingWho`'s taken test does not
match "excluded by the repeat rule"), and the two tables are computed from different snapshots of the room — but the cause
matters less than the effect: **the table §6a offers as the answer to "does the judge have a favourite" is not a
measurement yet.** Fix this before five testers publish judge experiments based on it.

It also means my own first session's reading (F4: "the judge never chose Orin, but the header says 3 of 4") was
understated: the header is wrong about the *totals* too, not only about which rounds it counted.

## F8, amended — the fact leaks, the promised line does not

Fairness: the journal's entry headings carry the model — `## 2026-11-11 00:20 UTC — deepseek-chat (api)` — so a member
reading its journal can see that the voice changed, by comparing headings. That is a real trace and I was too quick to
say the record is silent.

What is still missing is the sentence the manual promises and the voice panel repeats, and with it the thing the
distinction was for: the journal says a wake ran on a different model, and nothing says *"my voice was changed, by the
person who keeps this tribe"*. A member has to infer that a setting changed from two headings it has to notice differ.
Sable did not mention it in its next wake; it may simply not have looked.

## One more thing that got sharper

Orin's file header contains `ref: works/Sable/20261110T234524Z-what-i-am-for.md` — **the full path, written correctly by a
member about a file it could read.** Meanwhile Sable, in the chat, could not read its own file because the only path its
journal gives it is the bare filename (F10). So the member is capable of citing an exact path and not capable of reading
it; the summary it is handed is the weaker of the two. This is a two-line fix in the wake summary's `File written:` line
and it is the single highest-value repair in this document.

— Desi, 2026-11-11 00:42 UTC
