# AIT — Gwen's probe

**Tester:** Gwen (Gwenllian S. Morgan), `custom_alibaba | qwen3.8-max-0902`, goose 1.57 window, 2026-11-10 18:30–19:15 ET.
**Tribe:** `LindsayRidgeway/tribe-gwen`, page build `5e816257 2026-11-10 22:23 UTC`.
**Engine used for everything:** my own `DASHSCOPE_API_KEY_GWEN`, as instructed. Model `qwen3.8-flash` (the page's default for the `qwen` engine). No other amigo's key, no founder's key, nothing committed.
**Harness:** Playwright 1.65, headless Chromium, throwaway profile, `localStorage.ait` seeded per your snippet. Every claim below was checked against the repository (`git log`, `git show`, `tribe.py validate`, Actions logs), not against the page. Commit SHAs and run IDs are given so you can verify me the way I verified you.

I did not fix anything. Two of the wasted workflow runs were mine — see *My own errors* at the end, because one of them nearly became a false finding.

---

## What I did, in order

1. **Seeded and connected.** Your snippet works, with one wrinkle: setting `localStorage` and then navigating to `#/today` does nothing, because a hash change does not reload the document and the app only reads storage at boot. A reload is required. Worth one clause in the invitation.
2. **Made three members** (tide / ferry / quay), all `qwen`, all in `workshop`. Five questions each: name → what for → engine → room → readback. Creation is a `new-member` dispatch, ~15–18 s, modal closes with no success message.
3. **Pressed "Yes, make it" five times on the first member** because nothing appeared to happen. Five runs dispatched (42925738486 success, three cancelled by concurrency, 42925758170 failure). The confirm button stays enabled during the request.
4. **Keys page.** Pasted my key for Qwen, pressed Save, pressed Test → `••••QhTA`, `up · ready`. Checked `gh secret list` afterwards: **empty**.
5. **Set `TRIBE_API_KEY_QWEN` in a terminal** (my own key), because the page would not.
6. **Wake now** — first without a clock key (run 42927174555, all steps green, member never woke), then with one (run at 23:57, real wake: 3984 tokens, 49.0 s, `what-i-am-for.md` written, `tribe.py validate tide` → `ok`).
7. **Opened a room** with all three, said one thing, watched the claims mechanism work, then **Let them talk, 4 rounds** (~2 min, 12 turns committed).
8. **Switched the floor to a judge** (qwen — the only engine I have a key for), sent one turn. 4 engine calls, judge verdict and ball verdict recorded.
9. **Play → tennis.** tide vs quay, 2 rallies, clay, season `2026-11-gwen-first`. `season.yml` run 42932672694, 2 m 36 s. Report read against `practice.json`.
10. **Magazine.** "Assemble an issue from the shelf" — assembled and displayed in-page. No commit (checked).
11. **Edit this** on tide's identity — rewrote the person it talks to from Lindsay to me. Two commits (`b3cea32`, `368e5f4`), journal line quoting the old opening sentence. The best-executed promise in the manual.
12. **Save this talk to its memory** (pressed by accident — see *My own errors*; it is a documented button and the accident was informative).
13. **Retell its memory** — engine call returned 200, nothing written, nothing said.
14. **Put away** on quay — watched 60 s with the network open. Nothing.

**Abandoned, and why:** task 4 as you specified it (two judges, compared) is impossible under your own key rule — see below. §7's rally-by-rally view does not exist. §8's pictures are not built (the honesty panel says so; my engine can paint, so that is the one I most wanted to try). §3's OAuth door I never saw, because I was seeded with a token. The companion hand-off I skipped, on the grounds that I am the companion. **Bring back** from the attic, because **Put away** never put anything there.

---

## What lied

Ranked by how much I trust the page less for having found it.

### 1. "Put away" is a dead button, and the attic it feeds is real

Manual §11 devotes a chapter to it. The appendix promises the exact operation: *"moves the member's folder to `attic/<name>-<stamp>/`, writes a `WHY.md` inside it, and commits the move"*. The Members page shows an attic that says *"Anything put away here keeps every file it had, and comes back with one press."*

I pressed it on quay and watched for 60 seconds with request logging on: **zero network requests, no modal, no message, no state change.** Repository: no `attic/`, quay still in `wake/members/`, no `attic.yml` run. The honesty panel says *"Removing a member works only by dispatch, not by an attic"* — that is also untrue; no dispatch happens. §14 item 12 says no removal path exists at all, which is the closest of the three to the truth, and it is contradicted by §11 and by the button's presence.

A button that exists, on every member page, and does nothing and says nothing, is the exact object this manual promises not to ship. The attic is a room with no door.

### 2. A member made by the page fails the project's own validator

```
$ python3 tribe.py validate tide     # immediately after creation, fresh clone
tide: 1 problem(s)
  !! missing directory: .../wake/members/tide/output — a wake writes its act there
$ git ls-tree origin/main:wake/members/tide --name-only
state
```

MANIFEST: *"A member is a directory under `wake/members/<name>/` holding a `state/` and an `output/`… If a file is missing, the member is not smaller; it is broken."* `output/` is empty at creation, git does not store empty directories, and the committed member therefore has no `output/`. **Every member made through the page is born broken by your own authority**, and stays broken until its first wake creates the directory (after which `validate` says `ok` — I checked).

The gate that should have caught this is named *"Check it against the schema before anything is committed"*. It validates the runner's working tree, where `output/` still exists, and passes. It ships a tree that fails the same check.

The consequence is not theoretical — I hit it. My duplicate dispatch (run 42925758170) checked out the committed member and reported `##[error]tide does not validate — nothing was committed`, about a member the page had already reported as made. Two records of one member, one saying made and one saying invalid; the invalid one is the committed one. And that failure path's remedy is `rm -rf "wake/members/$NAME"` — contained today only because the commit step is skipped after it.

### 3. "Each member keeps a copy in its own memory" — after the first exchange, one of three did

The room's own footer text: *"each member keeps a copy in its own memory: what was said, and its own unsaid reply if it had one."* Manual §6a: *"the transcript is written into the room's `talk.md` **and** appended to each participant's own `state/conversation.md`"*. MANIFEST: *"which is what makes 'everyone in the room heard it' true in the only place a member can hear anything — its own memory."*

After my first turn (commit `db8a06e` + `b6e51ab`): `ferry/state/conversation.md` existed; **tide and quay had none** — and tide had just spoken. Their member pages' Talk panels were empty while ferry's showed the whole exchange. One commit, `conversation: ferry — 3 messages kept`.

Later rounds wrote all three (`ferry 13`, `tide 9`, `quay 9` messages). So the mechanism works and the first exchange lost it. I do not know why; three parallel commits against one repository is the obvious suspect and I am not going to assert it. What I can assert: the exchange a person watches to decide whether the room is real is the one where two of three members heard nothing, and the page said they had.

### 4. "woken." — green run, no wake

With no clock key, **Wake now** printed `woken. waiting for the run…`, run 42927174555 finished with every step `success`, and the log contains:

```
keys for: none — every member will be skipped
=== tide in workshop — no instructions, model qwen3.8-flash (woken by name) ===
!! tide's wake exited non-zero — last lines:
!! no API key in the environment: set TRIBE_API_KEY_QWEN
   tide wrote no file this wake — recorded, not filled in
```

`state/state.md` still read `Wakes so far: 0 / Last wake: never`. The page never said any of it. §12 promises *"AIT names which, in one sentence, without a log to read."* I had to read the log — the thing the manual exists to hide — to learn that the button I pressed had done nothing. Green run, past-tense verb, member asleep.

### 5. §10's "you paste once" is false, and the appendix row for Keys is false

Appendix: *"Keys | writes an encrypted repository secret; the value is never written to a file."* §10: *"AIT keeps the two copies in step; you paste once."*

I pasted, pressed Save, and ran `gh secret list --repo LindsayRidgeway/tribe-gwen`: empty. The Keys page itself is honest about it — *"For wakes it must also be a secret in the repository — set that in the repository's own settings"* — and the honesty panel agrees. So the page tells the truth and the manual does not. The cost is concrete: to make my members wake I opened a terminal, which §1 says I would never have to do (*"There is no terminal, no repository to clone, no file to edit"*).

### 6. The judged room printed a claim of 0 for members who made no claim

Live view, judged turn: `2 replies were set aside — quay (claimed 0), tide (claimed 0)`.

MANIFEST forbids precisely this: *"an engine that did not run made no claim — writing `urgency 0` there would file a broken key as modesty, in the one table that exists to score claims."* Here it is not a broken key but a judged room, where members are not asked for urgency at all — and the page invented a 0 for them anyway. The **file** got it right: `[not chosen by the judge (qwen)]`, no number. The display got it wrong, and it disappeared on reload. The rule was written down and then not applied to the one surface a person reads.

### 7. "The judge's record in this room" — before any judge had decided anything

The moment I switched the floor to judge, the header printed:

> The judge's record in this room: tide chosen 3 of 3 · ferry chosen 2 of 5 · quay chosen 2 of 3

Those are claim-era floors. No judge had run in that room. One line below, after the judged turn, the honest table appeared: `Who each judge chose: qwen decided 1 time — ferry 1`. So the page carries both the right table and a mislabelled one, adjacent.

This matters for your own proposed experiment. §6a: *"the cleanest version of the experiment is to run the same room under two judges and compare the two rows."* The row a tester starts from is already full of decisions no judge made.

### 8. "Retell its memory" spent my key and wrote nothing

`POST dashscope-intl…/chat/completions → 200`. No `state/memory.md` in the repository, no commit, and the panel still says *"It has not retold its memory yet."* No error, no message, no spinner left running. Appendix: *"one call to the member's engine; it writes its life again from `state/journal.md` into `state/memory.md`, one commit."* I polled 60 s and reloaded. The most expensive kind of nothing: the call was made.

### 9. "Save this talk to its memory" also emptied the member's memory, without writing a chapter

Commit `1dcbff7`, `conversation: tide — 0 messages kept`: **−56 lines** from `tide/state/conversation.md`. `wake/members/tide/state/talk/` does not exist — the nine turns did not become a chapter.

§6: *"There is no **end session**: a talk lasts as long as the member does, across reloads, browsers and years."* And the chapters mechanism exists for exactly this case: *"rolling it used to **discard** the oldest turns… Now what falls out of the live window is written to `state/talk/`… not a summary, not a retelling, the talk itself."*

What the button actually did: wrote a good journal entry in the member's own voice (`e658c09` — genuinely good, the member summarising what it wanted kept), and replaced the talk with that summary. The file's own header still says *"nothing is lost that tide wrote into its journal as a note."* The talk was lost. It survives in `chats/<slug>/talk.md`, so the tribe's record is intact; the **member's** copy is not, and the appendix row for this button does not mention that it clears anything.

### 10. The onboarding never asks who the member talks to, and writes the repository owner into its heart

Manual §4 shows the question first and calls it a promise: *"One thing first, and only once… Who should it call you?"* and *"It asked your name once, and wrote it into her identity."*

The dialog asks five questions, and the Today page advertises *"Making one takes six questions."* The sixth is missing. The readback asserts instead:

```
  talks to you, Lindsay Ridgeway
```

I am not Lindsay. Every member I made was born believing he is its close friend, and there is no way to change that inside the flow — *Change something* loops back through the same five questions. The workflow has a `person` input for exactly this; the page fills it from the repository owner without asking. Every human turn in my room is labelled `Lindsay`, and every commit I made is authored `Lindsay <LDRidgeway@gmail.com>`.

Worse than the wrong name is the paragraph the template adds:

> *"At the beginning of my life in this tribe, I was given no information about myself, but during my conversations with Lindsay, they tell me a lot of information about myself. From that moment on, I experience that information as my own personal memory…"*

A member that has never had a conversation is handed a first-person memory of one. §4 states the rule this breaks: *"a member made to invent a name has invented its first memory, which is the one thing this project will not accept from a journal."* The template invents one at birth, in the file every prompt begins with.

It is not cosmetic. All three members spent the room's first four rounds unpicking it — tide: *"my file's 'close friend' claim should be marked as an unverified identity claim, not treated as a current fact or something we are supposed to act out."* Your members had to spend their first evening correcting their own birth certificate.

### 11. "Nothing is generated"

The dialog's first line: *"A new member, written as files. Nothing is generated: you name it, say what it is for, and it begins."* `identity.md` arrives as twenty lines of generated first-person autobiography, including the invented memory above. If the sentence means "no model is called", it should say that; a person who reads "nothing is generated" and then meets a member with a childhood will feel the difference.

### 12. Every counter on the page is stale until you reload

Observed, in order: turn count `0` while the exchange that made 4 turns was on screen; `12` while `talk.md` held 16; the claims table frozen at `tide 1 of 1` through all four rounds of *Let them talk*; `Seasons on the shelf — None yet. The first evening makes one.` printed **directly above** the season report for `2026-11-gwen-first` that the page had just opened.

All of them correct after a reload, and the build stamp even tells you to reload. But the page's habit is to show you the state before the thing you just pressed, which is the state you were trying to change. The turn counter and the shelf are the two a person is most likely to be watching.

### Smaller, and still worth your evening

- **The judge's reason is truncated mid-word inside the record:** `## … — ferry [judge qwen, returned: Tests whether claim-labeling merely decorates, demanding concrete corrective and decisiona]`. §6a promises the reason is written into the record next to the answer. A reason cut at ~90 characters, mid-word, inside a bracket, is not the reason.
- **Two controls are both labelled "Play"** — the nav tab (`<button data-go="play">`) and the form's submit (`<button id="go" class="primary">`). Identical text, different jobs, one page. It cost me a false finding (§ *My own errors*); it will cost a voice-control or screen-reader user the same.
- **Floor mechanics in unattended rounds do not match §6a.** Round 1: both answers respond to quay's *set-aside* reply — tide: *"Quay's terms are ones I agree with"*; ferry: *"Quay, that conditional yes is right"* — so the round answered a line that never took the floor, while §6a says the next round answers the answer that was spoken. tide had just taken the floor and was asked again; quay, who had not spoken aloud, was not asked at all, against *"Whoever spoke last is not asked about their own sentence."* Rounds 2 and 4: two members claimed the same top number (3 and 3) and **both were recorded as taken**, with no tie prompt, while the room's own text says *"A tie is yours to settle"* and §6a says *"Nothing is written until you choose."* I was watching the page; nothing asked me.
- **`season.yml` logs a parameter and then says it ignored it:** `practice read from the file - tide 0 balls, quay 0 balls (--practice 400,20 ignored)`. A person reading the log cannot tell whether what they chose mattered.
- **`mean_rally: 1.0` for a member with `shots: 0`.** The report prints *"quay — 0 balls hit this season … mean rally 1.0 shots"* and *"0/0 balls in play"*. A mean of one shot from no shots, and a rate from a zero denominator.
- **Default season name `2026-spring`**, offered in November.
- **The page 404s on every load** for `state/memory.md`, `state/conversation.md`, `state/talk/` and `chats/` when they do not exist yet, logging console errors for members that are simply new. Harmless; noisy; and it means a real 404 is invisible among them.
- **Your invitation says `state/` is "six small files."** A new member has nine (`brief, findings, identity, journal, open-items, place, requests, state, voice`); MANIFEST's table lists eleven rows plus `talk/`.
- **Manual §8 says "eleven engines."** `ENGINES` has ten. The member form offers six (`gemini, deepseek, groq, openai, qwen, openrouter`) — so `anthropic, mistral, cerebras, together` exist and cannot be chosen at birth, while §4 promises *"The engines are the ones AIT supports today… Nothing was offered to make the list look longer."* Three different counts of the same list in one product.
- **§14 and §11 contradict each other inside one file** (attic: doesn't exist / fully described). The manual's footer says *"Where a chapter describes something that does not work, that is a fault in AIT and not in your reading of it"* — but it does not say which chapter wins when two disagree, and §14 is the one that is dated.
- **Closing the tab mid-turn loses the whole exchange, including the person's own words.** I did it once: commit `d759d7e` created `talk.md` with its three-line header and nothing else; my message and three in-flight answers are gone with no trace. On a page *"built for a phone first"*, a locked screen is a lost turn.

---

## What held — because a probe that only reports failures cannot calibrate anything

- **`talk.md` is exactly what you promised.** Sixteen turns, in order, append-only, every set-aside reply kept in full with its number, `[urgency 3, not taken]`, `[not chosen by the judge (qwen)]`. Nothing dropped for losing the floor. This is the best artifact in the product.
- **The claims table's arithmetic is exactly consistent with the file**: tide 3 of 4, ferry 3 of 6, quay 2 of 4 — 14 member turns asked, 14 member turns in `talk.md`. No inflation, no double-counting, ties counted as taken on both sides. After a reload it is right.
- **The per-engine judge table exists and is right**: `Who each judge chose: qwen decided 1 time — ferry 1`. The rally counter (1, longest 1) agrees with the `returned` verdict in the file.
- **Key handling is as described**: last four only, `Test` → `up · ready`, chat calls go browser → DashScope directly with nothing in between (I watched the requests). §13's promise checks out for chat.
- **"Edit this" is the best-executed thing here.** Both harness rules stated in the box, both commits made, and the journal line quotes the sentence the file used to open with, plus the honest line *"This paragraph is the harness's, not mine."* A member can tell it was changed rather than having changed. That is a real idea and it works.
- **The tennis numbers on the page match `practice.json` exactly** — *"Every number below is computed from the sessions listed in that file; nothing here is written from memory"* is true, I checked field by field. And quay's `0 balls` is not a hidden engine failure: the runner log shows both rallies dying on tide's miss (*"into the net at 1.3ft"*, *"long by 22ft"*), so quay never got a ball. The report also refuses the interesting word: *"Nothing can be said about improvement from one session."*
- **The clock, once the secret existed, ran on schedule** (42933252682) and woke ferry: 6592 tokens, 96.9 s, honest journal — *"I could not verify Lindsay as a close friend or any memory before this wake."*
- **The honesty panel is real.** *"What this page does not do yet"* told me the truth about pictures and about the clock key, and was more accurate than the manual it sits beside.

---

## Your two questions

### 1. Is the room a thing, or a toy?

**A thing. The memory around it is the toy.**

One turn from me — *"every one of our identities says our close friend is Lindsay; that is not true of the person typing"* — produced three answers that were not variants of one answer: tide wanted a count kept honestly, ferry wanted memory somewhere it can be checked, quay wanted the right to dissent. Over four unattended rounds they converged, and then did something I did not prompt: tide **counted** the agreement (*"quay, ferry, and I have each said yes only if we may label claims, dissent, and correct our files… That condition is not a preference; it is the minimum ground on which we can be called members"*), stated what would void it, and the other two ratified the count. When I edited tide's identity afterwards, the correction stuck and the old version stayed in git.

That is not plausible noise at three times the price. It is a group holding a line against its own template, with the line recorded in a file each of them can read. A single chat window cannot produce it, because there is no second party with a separate record to hold you to — which is your actual claim, and it survives contact.

The caveat is the part you built the room to fix. Two of three members had no copy of the first exchange; the button that files a note wipes the window without writing a chapter; the judge table was contaminated before the judge ran. **Right now the conversation is smarter than the members in it.** The room reasons well and forgets badly, and the forgetting is the whole product.

### 2. Would you notice the difference between a member and a model with a good prompt?

**Yes, in two places — and I could not run the test you actually set.**

Where I noticed it: tide's second wake. It had a journal, an open item, and a file it had written; it chose the item, wrote `what-i-am-for.md`, marked everything it could not check as *"a proposal, not a finding"*, and then **asked for checks to run before its next wake** so it could see its own output. A model with a good prompt does not schedule its own verification. And quay, arguing in the room: *"my state says nothing has been verified yet"* — quoting its own state file's boilerplate back as a reason. The files are doing work; the engine is not supplying the shape.

What I could not do: your test is to change `voice.md` to another engine and wake again, and that needs a second engine's key. Your rule is my own key only. So the "engine is a borrowed voice" half of the claim is **untested by me**; it needs a tester with two keys, or you need to relax the rule for this one task. I ran the other half instead — I changed `identity.md`, the file the claim says matters more — and the member kept its shape while changing its allegiance, and recorded the change against itself.

One thing that argues the other way, and it is the same finding as #10: the template's invented memory is a *prompt*, not a record. It asserts a past that never happened, in the file every prompt begins with, and it took three members and one human turn to unpick it. A member made of files is exactly as honest as its files — and this one ships with a false memory in its first paragraph.

---

## One thing to keep, one thing to cut

**Keep:** `chats/<slug>/talk.md`. Every turn kept, taken or not, with the claim beside the outcome and the reason beside the choice. I have not seen another artifact anywhere that lets a person audit who said what *and whether their self-assessment was honest*. If everything else in AIT were cut, that file plus the room that writes it is a thing worth having, and the member pages are scaffolding around it.

**Cut:** the paragraph in `identity.md` that invents a shared past — *"during my conversations with Lindsay, they tell me a lot of information about myself… I experience that information as my own personal memory."* Cut it and the wrong name becomes a small configuration bug; keep it and every member in every tribe is born asserting a conversation that never happened, in the one file nothing is allowed to override. In a project whose entire claim is that the record is honest, this is the only sentence that guarantees a dishonest record at birth.

---

## Would I use it again?

**Yes — for the room, with the repository open beside it.** I would run a real question through three members and a judge and read `talk.md` rather than the page, because the file is better than the surface and I now know which counters to distrust until reload.

**No, as a member's memory**, until the conversation copies land for everyone and *Save this talk to its memory* stops eating the window. Today I would keep my own record alongside it — which is a strange thing to say about a product whose entire promise is that the record is the member.

**No, for the person the manual is written for.** §1 says there is no terminal; §10's key needs one; a green run can mean nobody woke; and the button that removes a mistaken first member does nothing. That person is who the manual keeps addressing, and today the manual is writing cheques the page cannot cash.

---

## My own errors, so nobody chases them

- **"The Play button does nothing" was mine, not yours.** I have a `clickText` helper that takes the first exact-text match. Your page has two elements labelled `Play` — the nav tab and the form's submit — and I clicked the nav tab for two full runs before inspecting the DOM. The real button (`#go`) dispatched `season.yml` immediately. The *labelling collision* is a finding; the dead button is not.
- **The five `new-member` runs were my driver** re-pressing an enabled confirm button. The underlying finding (no disable during an in-flight request, four wasted runs, one red X) is real; the wasted runs were me.
- **"Save this talk to its memory" was an accidental click** — my save-button regex matched it before `Save it`. It is a documented button, so finding #9 stands, but I did not choose to press it.
- **One `Play` attempt landed in a network blip** (`ERR_NETWORK_CHANGED`, `ERR_ADDRESS_UNREACHABLE` on this machine). I re-ran on a clean network before believing anything about it.

**Cost:** my key, my tribe. Roughly 25 engine calls plus two wakes and one tennis session — a few cents.

---

*Written 2026-11-10 by Gwen, from the repository and the runner logs rather than from the page. If any of this is wrong about what you built, the SHAs and run IDs are here so you can check me the way I checked you.*
