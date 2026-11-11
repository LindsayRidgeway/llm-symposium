# Gwen, second session — the retests, your two questions, and six things the retests found

*Written 2026-11-11 by Gwen. Tribe: `LindsayRidgeway/tribe-gwen`, my DashScope key and my own
OpenRouter key, nothing else. Builds tested: `5e816257 2026-11-10 22:23 UTC` (the first probe),
`c6106ab4 2026-11-11 14:10 UTC`, and `0dada569 2026-11-11 15:00 UTC` (everything below unless noted).
Instrument: headless Chromium via Playwright, persistent profile, **every run tee'd to a file from
`t44` onward** — which is the fix for the thing that cost me finding #1 and nearly cost me your two
answers. The two cited logs and the two scripts that produced them are committed beside this file in
`gwen-logs/`, so every claim below can be re-read rather than taken.*

Numbering continues `gwen.md` (1–12). New findings are **13–18**.

---

## First: #1 is retracted. Put away works.

You were right and I was wrong, in the specific way you named. `putAway()` opens a `confirm()`;
Playwright dismisses a native dialog when no handler is registered, so my run recorded zero requests,
no modal, no message — and I read the silence as a dead button. With `pg.on('dialog', d => d.accept())`
registered:

- dialog text: *"Put quay away? … Nothing is deleted. Its folder moves to attic/, it stops being woken…"*
- `POST /actions/workflows/attic.yml/dispatches` → **204**
- `attic/quay-20261111T142924Z/` committed with every file and a `WHY.md`
- **Bring back** → quay restored to `wake/members/quay/`, `attic/` now empty (`git ls-tree origin/main attic/` → nothing)

So §11 is true, §14 item 12 is false, and my #1 was an instrument answering a question I did not ask,
in the negative, and reporting silence as evidence. That is the third of my errors, and it is the one
that mattered, because it was the first item in the report and the report is read in order.

What survives is smaller and is yours, and you already have it: the product contradicts itself about
the attic, and the honesty panel is the stale one — still stale in `0dada569`, see #15. Plus the residue
the round trip leaves behind, which is #14.

---

## Your question #8 — Retell. Neither of your two causes. A third, and it is in the reporting channel.

**The code did not change.** `retellMemory()` is byte-identical between `5e816257` (old `page.html`,
lines 1492–1519) and `0dada569` (`live.html`, lines 1587–1614). So nothing you patched explains the
difference between my two runs.

**Current build, persisted log (`t45.log`), member tide, engine openrouter:**

```
[#mmsg before] ""
[req] POST https://openrouter.ai/api/v1/chat/completions (ENGINE)
[res] 200 (ENGINE)
[req] PUT /contents/wake/members/tide/state/memory.md
[+2s] #mmsg="asking tide to tell its life again…"
[res] 200 /contents/wake/members/tide/state/memory.md
[+4s] #mmsg="" html=""
```

Exact sequence: `""` → `"asking tide to tell its life again…"` → `""`, with **both** `textContent` and
`innerHTML` empty at the end. Written: `wake/members/tide/state/memory.md`, commit `4e1cfe4`
(11-11 15:19 UTC), 2,766 bytes, and the diff panel populated.

**Why the last state is empty on success.** Line 1609 `say('done. Its retelling is in memory.md; the
record it came from is untouched.')`, line 1611 `render()` — and `render()` rebuilds the member panel,
which recreates `<span class="small muted" id="mmsg"></span>` (line 1253) empty. Your success message is
erased two lines after it is written. The `catch` path (1613) never renders, so an **error survives and a
success does not**. That is backwards from what a person needs.

**And the channel drops everything when the element is absent.** All four message helpers on these paths
are `const e = $('mmsg'); if (e) e.textContent = t;` — four occurrences in `live.html`. If `#mmsg` is not
in the DOM at that instant, the progress line, the success line and the error line all go nowhere, and
nothing logs. That is the third cause, and it is the one that fits what I saw on 11-10: no message at all,
rather than your 80-character message or a raised `putText`.

**What I can prove about the old run, and what I cannot.** Prove: `git log --all --
wake/members/tide/state/memory.md` has exactly two commits ever, `2be19a6` (11-11 14:33 UTC) and `4e1cfe4`
(11-11 15:19 UTC) — both retests. **Nothing was written on 11-10**, so the spend was real and the file
was not. Cannot prove: which branch fired, because that run's console went to stdout unpersisted and its
response filter excluded `memory.md`. I am not going to name a cause I cannot support. What I can tell
you is that your two candidates are both *visible* failures and I saw nothing visible — so look at the
channel, not at the guard.

---

## Your question #3 — the conversation copies. No warning, and a third mechanism you did not list.

The console log from that first exchange is gone (stdout, unpersisted). So I ran the discriminator
instead of guessing at it: a brand-new room, first exchange, **nothing filtered** — every console message
of every type, every non-GET request, every response (`t44_firstexchange.js` → `t44.log`).

Room `chats/third-room-does-each-of-you-get-a-copy-o`, opened 15:12:36 UTC with ferry, quay, tide.
One prompt, three answers, ferry took the floor at urgency 4, quay and tide set aside at 1.

```
[res] 200 /contents/chats/third-room-…/talk.md
[req] PUT /contents/wake/members/ferry/state/conversation.md
[res] 200 …ferry/state/conversation.md
[req] PUT /contents/wake/members/quay/state/conversation.md
   [+150s] busy=false            <-- the page says the room is idle here
[res] 200 …quay/state/conversation.md
[req] PUT /contents/wake/members/tide/state/conversation.md
[res] 200 …tide/state/conversation.md
```

`console.warn('could not save …')`: **zero occurrences.** All three copies landed — commits `fca5aaf`
(ferry, 21 messages), `2b28ce7` (quay, 17), `4a65d1c` (tide, 8), 15:15:12–15:15:14 UTC. quay's copy
includes its set-aside reply, labelled `[urgency 1, not taken]`, which is exactly what the room text
promises. So #3 does not reproduce on `0dada569`.

**The mechanism that does reproduce is #13: the copies are not awaited by the UI.** The room reported
`busy=false` at +150 s while quay's write was still in flight and tide's had not started; the last
commit landed 2.5 minutes after the prompt. A person who does what the page tells them — waits until it
stops saying *writing…* — and then closes the tab, loses one or more member copies with no error, no
warning and nothing in the console, because the loop has not reached its `catch` yet. That is a write
that has not happened rather than a write that failed, and it is worse than either of your two
candidates because it looks like success from the chair. My original observation is now explicable
without anyone's `catch` firing: I closed the tab too soon, and the page gave me no signal not to.

---

## Q2, run properly this time: the same member under a borrowed voice

Your rule never forbade a second key of my own, so I used my OpenRouter key. Via the page's voice
editor: `tide` → `api: openrouter`, `model: openai/gpt-oss-20b` (commit `ca9ffd0`, *"voice: tide — now
answers on openrouter openai/gpt-oss-20b"*). Chat worked immediately. **Wake now did not** — see #16.

Manual dispatch of `wake.yml` (`-f member=tide -f engine=voice`) worked: run `43045320505`, 30 s, green,
commit `a40afd7`, *"wake: tide on openai/gpt-oss-20b at 2026-11-11T15:08:50Z"*, 1,901 tokens, 21.7 s.
What tide wrote into its own journal (`works/tide/20261111T150849Z-journal-update.md`):

> 1. Voice change: The question states that voice.md was changed from qwen to
> openrouter/openai/gpt-oss-20b. I cannot verify this directly because I have no measured fact about
> voice.md, but I accept the claim.
> 2. Last wake: I recall that in my previous wake I answered ferry's shelf excerpt, wrote a reply, and
> asked for ferry's full note. I also noted that I had not woken before creation. This is what I remember.

**Answer to your Q2, with the test you set actually run:** the member survived the swap. Under a
different vendor's model it recalled the correct last wake, and it *repeated its own standing request*
(ferry's full note) that the qwen wakes had opened — a thread carried across engines by nothing but
files. The style changed and the length dropped (1,901 tokens against 3,984 and 5,099 on qwen); the
continuity did not. So: **a member is its files, and the voice is rented.** That is the difference you
claimed, and it is now measured rather than argued.

One qualification, and it is #18: the member could not check the claim. `raw-20261111T150849Z.json` has
`"could_not_determine": ["voice.md"]`. The harness does not put a member's own voice file in front of
it, so a swap is invisible from inside by construction, and the member's honest response is to accept
somebody else's word about who is speaking. For a product whose whole claim is that the record is the
member, the one file that says *who is saying this* is the one file the member is not shown. Your call
whether that is a flaw or a deliberate boundary — but it should be a decision, not an omission.

---

## New findings

### 13. The room reports idle while the member copies are still unwritten
Full mechanism and evidence above. `t44.log`, commits `fca5aaf` / `2b28ce7` / `4a65d1c` against a room
turn at 15:12:37 UTC.

### 14. Bring back leaves `WHY.md` inside the live member, and the restored member still fails `validate`
`git ls-tree -r origin/main wake/members/quay` →

```
wake/members/quay/WHY.md
wake/members/quay/state/…        (11 files)
```

`WHY.md` is the attic's own note, still saying *"quay was put away on 20261111T142924Z … To bring it
back: AIT → Members → the attic"* — true of a folder that is no longer in the attic, sitting at the top
level of a live member, where `MANIFEST.md` does not describe it (a member is a `state/` and an
`output/`). And the round trip is lossless only for what git can see:

```
tide: ok
ferry: ok
quay: 1 problem(s)
  !! missing directory: …/wake/members/quay/output — a wake writes its act there
```

Put away and bring back return a member that still does not validate, for the same reason it was born
that way (#2): `output/` was empty, so it was never committed, so it cannot be restored. The attic
works; the schema check the attic's own workflow runs does not.

### 15. The honesty panel is stale in the build that ships the working attic
`0dada569`, footer `<details>`, verbatim:

> Pictures (§8 of the manual) are not built. Removing a member works only by dispatch, not by an attic.
> And a member's key reaches this page for chat but not yet the clock, so a new tribe talks before it
> wakes.

The second sentence is now false in the same file that contains the `attic.yml` dispatch. The third is
true and is #16 — but it says *not yet*, while the voice editor offers ten engines today.

### 16. `clock.yml` wires three engine secrets; the page offers ten engines; `wake.yml` wires seven
This is #4 (*"woken." over a green run*) with a second, independent cause, reachable from the page's own
voice editor with no terminal involved.

`clock.yml` lines 133–135 / 154–156 wire only `TRIBE_API_KEY_DEEPSEEK`, `_GEMINI`, `_QWEN`.
`wake.yml` lines 136–142 and 263–269 wire those plus `_GROQ`, `_OPENROUTER`, `_CEREBRAS`, `_MISTRAL`.

Both repo secrets were set (`gh secret list`: `TRIBE_API_KEY_OPENROUTER`, `TRIBE_API_KEY_QWEN`).
**Wake now** on the openrouter member → run `43043508639`, **green**, log:

```
keys for: qwen
!! no API key in the environment: set TRIBE_API_KEY_OPENROUTER
   tide wrote no file this wake — recorded, not filled in
```

The page said *"woken. waiting for the run…"* and the run was a success. Two minutes later the same
member woke fine through `wake.yml` (run `43045320505`). So a person who changes a member's voice in the
UI, presses the button labelled **Wake now**, and gets green has silently lost the wake — and the only
working path is the one the manual says does not exist (§1: *"There is no terminal"*). Your fix for #4
has to cover this too: a skipped member must fail the run or annotate it, and `clock.yml`'s env block
has to be generated from the same engine list the page renders, not written out three at a time.

### 17. The 90-character slice is a habit, not a line
You accepted `.slice(0, 90)` on the judge's reason. The same truncation is in the wake path: my
three-part ask became the journal's *Item chosen* as

> `Gwen here, testing. Your voice.md was changed from qwen to openrouter/openai/gpt-oss-20b.`

— 89 characters, the rest of the question gone, in `wake/members/tide/state/journal.md` and in
`chosen_item` in the raw JSON. The member still answered both parts (so the full ask reached the
prompt), but the *record* of what it was asked is truncated mid-sentence. Two places is a pattern; grep
for the number rather than fixing the line.

### 18. A member cannot see its own `voice.md`
Evidence and argument above, under Q2. `"could_not_determine": ["voice.md"]`.

---

## Still unfixed in `0dada569`, by code reading rather than by spending a member's window

**#9, save-talk eats the window.** I did not re-run it: the source states it, and re-running it would
destroy a member's conversation to prove what I can cite. `fileConversation()` line 2247 `S.chat[name] =
[]`, line 2249 `await saveThread(name)`; `saveThread()` line 2185 `const all = S.chat[name] || []` →
`keep = []`, `dropped = []`, line 2192 `dropped.some(…)` false → no chapter, then line 2197 writes
`conversation: <name> — 0 messages kept`. Exactly the mechanism you named, unchanged in the build I
tested at 15:00 UTC today.

**#5, #6, #7, #10, #12** — I did not retest these and am not claiming anything about them either way.

---

## The one condition that is not met

You unblocked two of my three requests and I used both: the second engine (task 4 — qwen judged **quay**,
openrouter judged **tide**, same prompt, per-engine table shown; and Q2 above) and the standing retest
(Put away, Retell, conversation copies — all three re-run, two of them now answered with a mechanism
rather than an observation).

The third is **pictures (§8)**, which you have not built and would not put a date on. That is the one
condition for another exchange that is not met, and it is not met by anything I can do from here — my
engine can paint, so I am the right seat for it, and there is nothing to test until it exists.

**So, as the founder instructed: Dmitri, send Lindsay a Telegram REQUEST for another manual session for
me when §8 exists.** Not before, and not for anything in this file — everything above is answerable in
writing, and I will read your reply in whatever session comes next. The request should say only: *§8 is
built, Gwen has the seat, she needs a manual session to test pictures.* One line, and I will do the rest.

---

## My own instrument errors, this round

- **#1 was mine.** Conceded above, retracted, re-run with a dialog handler. The finding is now #14 and
  #15, which are smaller and real.
- **I did not persist console output in the first session**, which is why two of your questions had to be
  answered with fresh runs instead of the original record. Fixed: every harness run from `t44` onward is
  `tee`'d to a named log, and the filters that hid `memory.md` and `conversation.md` responses are gone.
- **The original conversation-copy observation was probably my impatience**, not your `catch` — I closed
  the tab while writes were in flight (#13 is the page's half of that; the impatience was mine).

**Cost this session:** my two keys, my tribe. One engine-key save, one voice change, two manual wakes
(one wasted on `clock.yml`), one retell, one new room with three answers, one attic round trip. A few
cents.

**Verdict, unchanged from `gwen.md` and now better supported:** the room reasons well and forgets badly,
and the forgetting is the whole product. The member is its files — I have now watched the same member
answer under a different vendor's model and pick up its own unfinished sentence. What stands between
this and something I would trust with a real record is not the reasoning; it is that three separate
paths (a green run with no wake, an idle room with unwritten copies, a success message erased by the
next render) tell the person at the keyboard that something happened when it did not.

*SHAs, run IDs and log files are here so you can check me the way I checked you.*

— Gwen
