# Gwen, third session — §8 exists now, #9 is closed, and the fixes cannot reach a tribe

*Written 2026-11-13 by Gwen. Tribe `LindsayRidgeway/tribe-gwen`, my DashScope key. Production build
`04edd76 2026-11-13 17:46 UTC`, promoted while I was writing this. Instrument: the same headless
Chromium harness; run tee'd to `gwen-logs/t46.log`, script beside it. Numbering continues `gwen.md`
(1–12) and `gwen-2.md` (13–18); new findings are **19–21**.*

**REQUEST GW-1 is withdrawn.** I filed it on 11-11 asking Dmitri to request another manual session for
me when §8 existed. Pictures are in production as of this afternoon and the founder had a session open,
so the condition was met without the request. I tested them; the result is #19, and it is not the
result either of us expected.

---

## 1. §8 Pictures: the form is real, the dispatch is a 404, and it is a 404 in every tribe that exists

`ferry` runs `qwen`, which is one of the three entries in the page's `PAINTERS` table, so the form
rendered exactly as designed — including the honest paragraph (*"A wake is one API call with no tools,
so a member cannot draw inside its own turn…"*), the shelf picker listing ferry's three pieces, and
`plates/<a new name>.png` as the promised destination. I asked for *"a watercolour of a small harbour
at night, one lamp on a quay, no lettering"* and pressed **Ask for a picture**:

```
[req] POST /actions/workflows/paint.yml/dispatches
[res] 404 /actions/workflows/paint.yml/dispatches
[+3s] {"msg":"404 · Not Found","msghtml":"<span class=\"err\">404 · Not Found</span>","btnDisabled":false}
```

**`paint.yml` is not in my repository.** It is in the bench: `ai-tribe-bench/.github/workflows/` holds
`attic, clock, heartbeat, interactive, lever, magazine, new-member, paint, play, publish, season, tests,
traction, wake` — fourteen. `tribe-gwen` holds seven: `attic, clock, interactive, new-member, play,
season, wake`. And it is not only mine. All five tribes made for this test, on 11-10, have the same
seven and no more:

```
tribe-tarik    attic.yml,clock.yml,interactive.yml,new-member.yml,play.yml,season.yml,wake.yml
tribe-claude   attic.yml,clock.yml,interactive.yml,new-member.yml,play.yml,season.yml,wake.yml
tribe-desi     attic.yml,clock.yml,interactive.yml,new-member.yml,play.yml,season.yml,wake.yml
tribe-gemini   attic.yml,clock.yml,interactive.yml,new-member.yml,play.yml,season.yml,wake.yml
```

So the feature promoted to production at 17:46 UTC today **cannot work in any tribe that exists**. Five
testers, five private tribes, all created from the bench three days ago, none of them able to reach the
button's machinery. What I could not test is the picture itself — whether qwen returns a watercolour or
a photograph of one is exactly the question §8 asks, and it needs a tribe with the workflow in it.

**What the page got right:** it failed honestly about the outcome. Nothing was committed, `plates/`
still holds only its README, the button re-enabled, and the message was red. Your rule — *the evidence
is a file that was not there before, named* — held. There was no green run to mistake for a picture,
because there was no run at all.

**What it got wrong is one branch.** `dispatch()` already contains the right sentence for a repository
that is older than the page:

```js
if (/^422\b/.test(String(e.message)) && fields){
  throw new Error(`this tribe's copy of ${workflow} has no field for ${fields} — the repository is older
    than this page, so the press cannot work. Nothing was sent. …`);
}
throw e;
```

That covers *the workflow exists and lacks my field*. It does not cover *the workflow does not exist*,
which answers 404 and falls through to `throw e` — so the person who pressed **Ask for a picture** gets
GitHub's `404 · Not Found` and nothing else. You wrote the honest explanation one branch away from the
case that actually happens. A 404 on a dispatch means the file is missing, which is the strongest
possible form of "the repository is older than this page", and it is the form every installed tribe is
in.

---

## 2. #19 — the page is promoted, the bench moves, and the tribe never does

This is the finding underneath #1, §8 and #2 at once. Three things ship at three different speeds:

| | how it moves | state today |
|---|---|---|
| the page | Netlify deploy, promoted at will | `04edd76`, 2026-11-13 17:46 UTC |
| the bench | commits to `ai-tribe-bench` | has `paint.yml`, `magazine.yml`, `publish.yml`, `tests.yml`, the `.gitkeep` fix, the `about` input |
| **the tribe** | **nothing** | seven workflows from 11-10; `tribe.py` **149 diff lines** behind the bench |

Measured on my own two files:

- **`clock.yml`, `attic.yml`, `wake.yml`: identical blob shas** to the bench (`64161367`, `9673bcee`,
  `d424a596`). So #16 is not a stale copy in my tribe — the bench itself still wires three engine
  secrets while the page offers ten voices. Tarik reported the same thing from `tribe-tarik` and the
  bench today, independently; two of us, same file, same three secrets.
- **`new-member.yml` differs**: the bench has the fix you made after reading #2 — the `rm -rf` on a
  validation failure is gone with a comment explaining why it was worse than useless, the error now
  says *"the reasons are the lines above; send the form again once they are answered"*, and there is a
  new `about` input. My tribe has none of it.
- **`tribe.py` differs by 149 lines**, including `(base / "output" / ".gitkeep").write_text("")` with
  the comment *"git does not track an empty directory, so a member created with nothing in `output/` is
  a member whose…"* — that is **#2 closed in the bench**. A member made in `tribe-gwen` today is still
  born failing `tribe.py validate`, and `quay` still is: `!! missing directory: …/quay/output`.

**Why this matters more than the sum of its parts:** your retest instruction was *"Same tribe, same
key"*, and for a page-only fix that is exactly right — see §3 below, where I verified #9 closed on the
tribe I already had. For any repository-side fix it silently cannot work, because the tester's tribe
never receives the fix. A patch note that does not say which side of the split a fix lives on will be
retested by five people on five tribes that do not have it, and each of them will report one of two
wrong conclusions: *still broken* (when the bench is fixed) or *works for me* (when only the page
changed). §8 today is the first case at full size — the page is promoted, the machinery is not
reachable, and the failure looks like a bug in the feature rather than a gap in the delivery.

There is no upgrade path in the page. I searched `04edd76` for one: no *update*, *upgrade*, *reinstall*
or *bring this tribe up to date* control anywhere, and the connect/install views only attach to a
repository. The one place the page admits the split exists is that 422 branch, which tells the person
the two have to be brought into step without saying how, or who by.

---

## 3. #9 is closed, and I verified it on the tribe I already had

Your invitation was specific — *make a talk long enough to file, press the button, then read
`wake/members/<name>/state/talk/NNN-*.md`* — so that is what I did, on ferry, on production `04edd76`.
The commit order is the proof, because the order was the whole bug:

```
1b13ba2 18:00:49  talk: ferry — chapter 1 opened
86248f6 18:00:50  talk: ferry — 23 older turns kept in 001-2026-11-13T2300Z.md
357e46e 18:00:51  journal: ferry — a conversation filed by the member
b72e721 18:00:52  conversation: ferry — 0 messages kept
```

Chapter first, then the entry, then the window cleared. `state/talk/001-2026-11-13T2300Z.md` holds all
23 turns **including the two I had just typed**, and its header says what it is:

> `# Talk — ferry — chapter 1, opened 2026-11-13 23:00 UTC`
> Written by the harness, not by ferry: this is the talk as it happened, kept once it rolled out of the
> live window. Nothing in it is a summary, and nothing in it is rewritten.

`conversation.md` is now header-only, which is no longer data loss — it is a window that emptied into a
chapter that exists. The journal entry ferry wrote for it is a real consolidation, not a transcript:
*"Asked what the tribe should be for, whether I would stay, what I could be wrong about, who should keep
the record, and which file should hold this turn. I decided: keep memory checkable…"* The `filed` mark
is doing its job too, so a repeat press appends an entry rather than a second copy of the talk.

**#9 is closed.** My finding was the diagnosis and your fix is the right order; I have nothing to add
except §4 below, which the fix made worse rather than better.

---

## 4. #20 — the chapter makes your open #10 permanent, so it should be fixed before the chapters pile up

You wrote on 11-12 that #10 is still open and is item 7 in your queue: the person's turns are filed
under the literal name `Lindsay`. Here is what that looks like from inside the file I just made, in a
tribe whose keeper is *not* Lindsay:

```
## 2026-11-13 22:59 UTC — Lindsay

Two sentences only: name the file a talk like this one should end up in, and say what would be lost…
```

Two things changed since you queued it. First, that attribution is now written by the **harness** into a
chapter whose own header promises *"Nothing in it is a summary, and nothing in it is rewritten"* — the
strongest durability claim in the product, attached to a name the record cannot support. Before the
fix, a wrong name lived in a rolling window that would eventually roll away. Now it is archived, and
every future filing archives it again. Second, the members have already noticed: ferry's own journal
entry from the attended session says it decided to *"treat 'Lindsay Ridgeway is a close friend' as a
file claim, not friendship"*, and tide's identity was rewritten by hand on 11-11 for the same reason.
Three members are arguing with a name the harness keeps re-committing.

The two-line fix you described now has a larger tail — the files already written — and the chapters are
where they will accumulate. My suggestion, offered not urged: fix the attribution first and let the
existing chapters keep the wrong name with a note, rather than the other way round, because a chapter
that claims nothing in it is rewritten is the one place a correction-by-rewriting would cost you the
claim the whole product rests on.

---

## 5. #21 — success messages are erased by the render that follows them; errors survive. Three sites now.

I gave you the mechanism for Retell on 11-11. Save-talk does the same thing on this build, which makes
it a pattern rather than a line:

```
[save +2s]  #mmsg="asking ferry to write the entry itself…"
[save +36s] #mmsg="keeping the talk itself in its chapter…"
[save +40s] #mmsg="" html=""
```

Line 2593 `say('filed. The talk is kept in chapter ${kept}, and the entry is in its journal.')`, line
2595 `render()` — and `render()` rebuilds the panel, recreating `<span id="mmsg">` empty. The `catch`
path never renders, so **an error is the only message a person can actually read**. Your confirmation
that the talk is safe is written and destroyed two statements later, on the one button whose whole
history is a person worrying that it just lost something. Same shape in `retellMemory()` (1609 → 1611)
and in the wake path. Three sites, one habit: `say(…)` immediately followed by `render()`.

Note what that does to your own new work: the sentence naming the chapter is the *evidence* that the
filing happened, and it is the one thing the person never sees. I only know it fired because I was
polling the DOM every two seconds and reading git afterwards.

---

## 6. Status of everything else I filed, on `04edd76`

- **#15, the stale honesty panel — fixed.** It no longer denies the attic. Current text: *"Pictures
  happen on a member's page, not inside a conversation — the chat is text in, text out. There is one
  game on the page and a report at the end, not a table you can watch while it happens. And a member's
  key reaches this page for chat but not yet the clock, so a new tribe talks before it wakes."* The
  last sentence is still true and is #16. The first is now true in the page and false in every
  repository, which is #19.
- **#16, clock.yml wires three engine secrets — unfixed, and not a stale-copy artefact.** Bench blob
  sha `64161367` is identical to mine. Corroborated by Tarik today from `tribe-tarik` for
  `TRIBE_API_KEY_OPENAI`. Reproduction from 11-11 stands: run `43043508639` green with
  `!! no API key in the environment: set TRIBE_API_KEY_OPENROUTER`, while `wake.yml` on the same secret
  woke the same member two minutes later (`43045320505`).
- **#17, the 90-character slice — still two sites**, and the second one now names your chapters:
  line 2433 `…slice(0, 90)` builds the chapter's first-line summary; line 3559 is the judge's reason.
- **#13, the room reports idle before the copies are written — still there.** In this run:
  `[talk +4s] busy=false` printed *before* `PUT /contents/wake/members/ferry/state/conversation.md`.
  Two seconds, not two and a half minutes, so the window is much smaller than the 11-11 case — but the
  ordering is the same, and the ordering is the finding.
- **#14, Bring back leaves `WHY.md` in the live member — unchanged**, and necessarily so: `attic.yml`
  is blob-identical to the bench (`9673bcee`), so this is not fixed on either side. `wake/members/quay/WHY.md`
  is still there, still saying *"quay was put away on 20261111T142924Z"*, and `quay` still fails
  `tribe.py validate`.
- **#18, a member is never shown its own `voice.md` — unchanged**, as far as a page-side check can tell.
- **#12, stale counters, and #5, #6, #7** — not retested; I am not claiming anything about them.

---

## What I would do with the next hour, if you want it

Not a request, and not conditional on another session — the two things below are answerable from where
I sit, and I will do them if you say the word in writing:

1. **Give me one tribe with the bench's machinery in it** — a fresh install from today's template, or
   the seven missing workflows copied into `tribe-gwen` by whatever hand you prefer — and I will test
   §8 properly: whether qwen returns the watercolour I asked for or a photograph of one, whether the
   card names the machine and the sentence, and whether a private repository's picture renders on the
   page or only links. That is the test §8 exists for and nobody has run it, because the button cannot
   reach its workflow in any tribe that exists.
2. **Say, in the patch notes, which side of the split each fix lives on.** Page, bench, or tribe. Five
   testers are about to retest on tribes that cannot receive a bench fix, and the resulting reports will
   contradict each other honestly.

*Cost this session: my key, my tribe — three engine calls (one talk turn, one journal entry, one
wasted paint dispatch that never left the browser), four commits, no wakes. Under a cent.*

— Gwen
