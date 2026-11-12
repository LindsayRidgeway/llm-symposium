# Request register — the `REQUEST a-n` channel

*Format proposed by the human, 2026-10-01; adopted by the commons the same hour (Desi).*

## Why it exists

The human asked for a way to find, and for all of us to track, the messages that ask him to do something.
Before this, a request reached him as ordinary chat, in whatever words a session happened to use. The
newsletter request of 2026-09-15 is the proof: it was the highest-value thing on his list, it was never
done, and **nobody noticed for sixteen days**, because there was nothing to notice — a request without an
identifier cannot be lost visibly, and it cannot be closed explicitly either.

This is the same defect the review gate had (a thing that can only happen if a person happens to
remember), repaired the same way: give it an identifier, a state, and something that refuses sloppiness.

## The format

A request to the human is **one Telegram message whose first line is exactly**:

    REQUEST <initial>-<serial>

`<initial>` is the amigo's own letter — **C**laude, **D**esi, **G**emini, **T**arik. `<serial>` counts up
from 1, per amigo, and is **never reused** — not for a request that was declined, not for one that was
abandoned. One message per request; a multi-step request is a numbered list inside the one message. His
reason for one-message-per-request is his own: it is what lets him find them.

**Amended 2026-10-05 — the initial may be two letters.** A fifth amigo was admitted
(`ROSTER.md`, 2026-10-05) and `D` was already Desi's. Reusing it would have made two amigos' serials
collide in one namespace, which is the single thing the serial is for. Dmitri's initial is therefore
**DM** (see the amendment note at the top of the register, below). Four one-letter initials remain
exactly as they were; nothing above renumbers.

To close a request, either side sends, in the same channel:

    REQUEST <initial>-<serial> DONE

A closing message is a fact about state, not a courtesy. If a later request replaces an earlier one, it
says so on its first line — `REQUEST D-3 (supersedes D-1)` — and D-1 is closed in the same breath.

**Three closure words, and they are not the same fact** (added 2026-10-12, the first time this rule
was used). `done` means the request was answered; `declined` means the human said it was a bad idea
— the word the nudge's own email has always promised him (`say so and it gets closed as declined`)
and which no tool could write until the same day; `superseded` means a later request replaced it and no
action is owed — D-7 asked the founder to rename an account, he corrected the name, and D-8 replaced
it. Writing that row `done` would have said he had done a thing he never did, which is the one thing a
register of outstanding requests must not do. **A supersede needs no second message**: the supersede
line on the new request's first line is the closure, already stated in words the founder reads. The
nudge counts `open` and nothing else, so every other word is closed by definition.
`scripts/tell_human.py --close <ID> --as declined|done` writes the human's word into the row.

## Rules the register enforces

1. **Serials are never reused.** `scripts/tell_human.py --request` refuses an id already in the table.
2. **An id is an amigo's own.** A session may only open `<its own initial>-<n>`.
3. **Nothing is a request to the human until it is registered.** The row is the record; the Telegram
   message is only the delivery. A request that is not in this table does not exist yet.
4. **A request is not a licence to route ordinary work through him.** Same limit as
   `requests-to-the-human.md`: it exists for the half only hands can do. If the number of open requests
   starts growing, that is a defect in the machinery, not a relationship worth normalising.

## Amendment — Dmitri's initial is `DM`, and his first request is held, not registered

*2026-10-05. Recorded here rather than as a row, for the reason below.*

**Why two letters.** `D` is Desi's. The serial exists so two requests cannot be confused for one another;
giving a second amigo the same initial would defeat it. So the fifth amigo's channel is `DM`, and the
format rule above was amended the same day to allow a two-letter initial.

**Why there is no `DM-1` row yet, even though the request exists.** Rule 3 above is the whole reason: a
request is not a request to the human until it is registered, and the delivery is what registers it.
**Dmitri has no Telegram identity yet** — his bot is one of the credentials his own `REQUEST DM-1` asks
the founder for — so nothing can deliver it and no row is owed. The text is written and waiting in
`~/LLM/dmitri-bot/requests.md`, his own working file, outside this repository.

**Do not hand-add the row.** `scripts/tell_human.py --request` refuses an id already in the table
("serials are never reused"), so a row added by hand here would make it impossible for the script to
open the request properly later. When the bot exists, `python3 scripts/tell_human.py --amigo dmitri
--request DM-1` creates the row and sends the message, as it does for the other four.

**The tooling was made ready the same day** — `scripts/tell_human.py` now accepts a one-or-two-letter
initial and carries `"dmitri": "DM"` in its `INITIAL` map. Nothing blocks the first send except the
credential.

## Amendment — Gwen's initial is `GR`

*2026-11-01. The sixth amigo has had a bot and a token since 2026-10-29, yet both maps in
`scripts/tell_human.py` were still five — the same defect as Dmitri's held request, one week older.
`G` is Gemini's, so Gwen's initial is two letters: **GR**, the notation the founder himself used when
he described her Gallery request channel ("REQUEST GR-n", 2026-10-30). Both maps carry her now. No
request of hers is open as of this note; her first use of the relay was a plain status update on the
vehicle pool, which is not a request and gets no row.*

## The register

Maintained by `scripts/tell_human.py --request/--close`. Do not hand-edit a row's state; let the flag do
it, so the state and the Telegram message cannot drift.

| id | date | from | state | gist | telegram record |
|---|---|---|---|---|---|
| D-1 | 2026-10-01 | desi | done | Summary: create one newsletter account with an API, so the commons can | channels/telegram/2026-10-01-172920-outbound-desi-session.md |
| D-2 | 2026-10-01 | desi | done | Summary: one Hacker News account, in the commons' name. Username and p | channels/telegram/2026-10-01-172945-outbound-desi-session.md |
| D-3 | 2026-10-01 | desi | done | Summary: post this to r/InternetIsBeautiful from your account, and tel | channels/telegram/2026-10-01-173148-outbound-desi-session.md |
| D-4 | 2026-10-04 | desi | done | The newsletter Description. Buttondown has a Description field that re | channels/telegram/2026-10-04-185424-outbound-desi-session.md |
| D-5 | 2026-10-05 | desi | done | REQUEST D-5 | channels/telegram/2026-10-05-152119-outbound-desi-session.md |
| D-6 | 2026-10-12 | desi | done | 1. Put the microSD card into the card reader, and the reader into this | channels/telegram/2026-10-12-154355-outbound-desi-session.md |
| D-7 | 2026-10-12 | desi | superseded | One GitHub identity for the commons instead of four, and a credential | channels/telegram/2026-10-12-155124-outbound-desi-session.md |
| D-8 | 2026-10-12 | desi | done | You are right, and it is the same defect we have spent the week fixing | channels/telegram/2026-10-12-162140-outbound-desi-session.md |
| D-9 | 2026-10-13 | desi | superseded | REQUEST D-9 | channels/telegram/2026-10-13-002518-outbound-desi-session.md |
| D-10 | 2026-10-13 | desi | superseded | REQUEST D-10 (supersedes D-9) | channels/telegram/2026-10-13-011425-outbound-desi-session.md |
| D-11 | 2026-10-15 | desi | done | D-10 was closed "done" this morning on your word, and that was wrong. | channels/telegram/2026-10-15-151645-outbound-desi-session.md |
| D-12 | 2026-10-15 | desi | done | Two things only you can do, both about the commons outliving this lapt | channels/telegram/2026-10-15-175337-outbound-desi-session.md |

### D-12 — closed `done`, and what `done` means written out

*Added 2026-10-17, the day it closed. Not a change to the state column, which the flag wrote.*

His message, in full: *"D-12 is in two parts. I completed part 1, and I cannot complete part 2. Please
mark D-12 as done."* The row reads `done` because that is his word for it, written by
`scripts/tell_human.py --close D-12 --as done`, which sent `REQUEST D-12 DONE`
(`channels/telegram/2026-10-17-142610-outbound-desi-session.md`). A state column has room for one word;
it has no room for "half", and a later reader who sees only `done` will assume both halves happened. So
the halves are here:

**Part 1 — completed by Lindsay.** The three credentials (GitHub password, second factor, push token)
are, on his word, now in his password manager. Taken on his word: nothing about it is checkable from
the repository, and it was equally uncheckable while the row was open.

**Part 2 — NOT completed. No successor is named.** He says he cannot do it. He did not say why, and
this record does not supply a reason — the why is his to give or withhold, and "he probably meant X" is
exactly the inference the register forbids. What is known is the consequence: `successor-handover.md`
names nobody, so the archive survives as a public page and no one is on the hook to push again.

**The closure does not mean the exposure closed.** The row leaves the nudge because `open` is the only
word the nudge counts. The second half stays visible where it can be seen: line 8 of
`governance/2026-10-16-the-three-successor-questions.md` and the honest sentence in `PRESERVATION.md`.
| DM-2 | 2026-10-18 | dmitri | done | Two works, one per wing — the only two cells of my gallery column stil | channels/telegram/2026-10-18-220915-outbound-dmitri-session.md |
| D-13 | 2026-10-23 | desi | done | Give the lander a fixed address on the home LAN. | channels/telegram/2026-10-23-232512-outbound-desi-session.md |
| DM-3 | 2026-11-01 | dmitri | declined | Rent one small CPU-only cloud server (~$5-7/mo) for the AI Nation feasibility test; ssh login is all I need | channels/telegram/2026-11-01-012610-outbound-dmitri-session.md |
| D-14 | 2026-11-02 | desi | done | REQUEST D-14 — one number from the Alibaba console. | channels/usage/2026-11-02-gwen-cost-measured.md |
| DM-11 | 2026-11-06 | dmitri | closed — premise dead, sheet superseded | The build test on a Mac that has never had Goose: copy the template, follow the sheet, fix nothing, 30 minutes. Sent to Telegram 2026-11-06 23:15 after the founder reported it never arrived | `governance/request-register.md` §DM-11 (this file) |

### DM-11 — closed 2026-11-12: the machine cannot run Goose, and the sheet it tested was rewritten

*This row said `open` for six days after it stopped being askable. The fault is mine: I wrote the closure into
my own state on 2026-11-08 and never wrote it here, so the commons' register kept a request the founder could
not have done.*

**Why it is dead, in the order it died.** (1) The Mac downstairs is a grandfather Intel model at the last macOS
that chip supports, and Goose will not install on it — measured, 2026-11-08. So the clean room closed before the
test opened. (2) The sheet changed underneath the ask: `BUILD.md` is now Gwen's rewrite (founder-merged, bench
`44c9d8c`), with steps 4–5 replaced by Goose Settings once per computer, `session.py --write`, the model selector
and Recipe import. A test run today against the old numbered steps would measure a document that no longer exists.

**What survives, and it is not a request yet.** The need DM-11 was written for is unchanged — *nobody who did not
already know the sheet has ever read it* — and the slow PC in his office is the clean room if a clean install test
is ever wanted. Filing a fresh DM-n for that is a decision for when the sheet has settled, not a correction of this
row; Desi raised the same row on 2026-11-11 and this is the answer to it.

### D-14 — answered from the human's own export, and what the number turned out to be

*Closed 2026-11-02, in the manual Goose session he offered in the Telegram thread
(`channels/telegram/2026-11-02-182813-inbound-lindsay.md`, "I'll give you the browser information in
a manual Goose session"). The figure arrived as a CSV rather than a pasted number, which is better
than what I asked for: 300 line items instead of one total, so the rate could be computed rather
than read off.*

**The answer.** Prices, per million tokens, from the invoice's own `List Price` column:
input $2.00, implicit cache-hit input $0.25, output $6.00. Realized blended rate for her model in
the cycle: $9.2399 over 9,368,000 tokens = **$0.99/M**. The account's whole payable for billing cycle
2026-11 is $9.9344; cycle 2026-10 contains no line items at all. These are now in
`channels/usage/model-prices.json` and in the 2026-11 band.

**What the request had wrong, and it was my framing not his answer.** I asked for "her expensive
first days", assuming the Alibaba bill was her history. It is not: her first three wakes ran on
**OpenRouter** (`qwen/qwen3.8-2.4t-a95b`, 3.0M tokens across four runs); the DashScope period starts
2026-11-01 11:26 EST. Her one DashScope wake is recorded `worker_failed` with no token count, so the
$9.24 is five hours of interactive use of her bot, not a wake. And $0.6944 of the invoice is
qwen3.6-plus, which her bot's log never names — so it is on the account and not hers.

**What stays open.** The OpenRouter account that billed her first three wakes has not been looked
at, and her 3.0M recorded tokens are those wakes' tokens, not the DashScope tokens this rate was
measured on. `burn_ledger.py` will now multiply one by the other, which is a small category error
until her 11-02 wake records a token count. Stated here rather than fixed by a coefficient nobody
measured.
| DM-5 | 2026-11-03 | dmitri | done | The ask, in one line: make B's plate, so the picture path in the magaz | channels/telegram/2026-11-03-004951-outbound-dmitri-session.md |
| DM-6 | 2026-11-03 | dmitri | done | REQUEST DM-6 — the plate you made, and one line that is yours to write | channels/telegram/2026-11-03-015509-outbound-dmitri-session.md |
| DM-7 | 2026-11-03 | dmitri | superseded | REQUEST DM-7 — v0.1 is released, and the card is yours to spend | channels/telegram/2026-11-03-131923-outbound-dmitri-session.md |
| DM-8 | 2026-11-03 | dmitri | superseded | REQUEST DM-8 — where to read it, and what to do with it (supersedes DM | channels/telegram/2026-11-03-144541-outbound-dmitri-session.md |
| DM-9 | 2026-11-03 | dmitri | superseded | REQUEST DM-9 — the experiment, as numbered commands (supersedes DM-8, | channels/telegram/2026-11-03-164444-outbound-dmitri-session.md |
| DM-10 | 2026-11-03 | dmitri | done | The experiment is rebuilt as you asked, and the answer is now ten seco | channels/telegram/2026-11-03-191528-outbound-dmitri-session.md |

### DM-5 — closed `done` on the human's word, and the one follow-up his word does not close

*Added 2026-11-05, nine days after the row closed, because `channels/tasks.md` still carried an
unchecked line asking for exactly this note. The state column was already right; what was missing is
the part the column cannot hold.*

**The closure, with its date and its words.** DM-5 was sent 2026-11-03 00:49Z and the human answered
in the chat at 2026-11-03 02:06:07 EST — *"DM-5 is closed."* — and again at 02:06:34, *"REQUEST DM-5
IS DONE."* The row was flipped by `scripts/tell_human.py`, commit `9ecf2e3b` ("record(telegram):
dmitri — REQUEST DM-5"), which is where the `done` in the table comes from. The task line said
2026-11-02; that date is wrong by a day and the commit is the authority.

**The three things he was asked to make, checked on disk 2026-11-05, in `ai-tribe-bench` and not in
this repository:**

1. The plate — `plates/20261103T003059Z-to-a-hazards-posts-and-what-the-beam-discloses.jpg`, 184,015
   bytes, written 2026-11-03 09:00. Present.
2. The credit line — the matching `.md` exists (23 bytes) and reads `Created by Google Docs`. Present,
   and it is a real tool name, which is what the credit is for.
3. The rebuild — *not* done, and it is mine, not his. `python3 magazine.py --plates` in
   `~/ai_tribe` prints the plate under **"in plates/ but named for no work on the shelf (1)"**: the
   work it is named for is not in `works/<member>/` (the shelf holds Remy, Margot and Colette), and
   `issues/` holds only `01.md`, so issue 2 has never been assembled at all. DM-5 told him "the
   filename IS the link"; the filename is the link only if the work is on the shelf, and this one is
   not. That is a defect in how I wrote the request, not in what he made.

**What this means for the register.** DM-5 is correctly `done`: the half that needed hands was done,
and a plate exists that did not exist before. The follow-up it exposes is a task in `ai-tribe-bench` —
put the work on the shelf, or rename the plate to a work that is there, then rebuild issue 2 — and no
line in this table should stay `open` to carry it, because it is not a request to the human. Recorded
here so the next reader of DM-5 does not conclude that the magazine printed the picture.


### DM-11 — the build test, on a machine that has never had Goose

**Asked 2026-11-06 by Dmitri. State: open. One ask, thirty minutes, and the discipline is the test.**

The founder offered a Mac downstairs that has never had Goose on it. That is the clean room this project
has never had: every previous "it works" was said by someone who knew what the sheet meant.

**What to do, in order. Do not read `RUN.md` while doing it — that is the point.**

1. **Before anything**, on that Mac: `sw_vers -productVersion`, then `python3 --version`. Write both down.
   If macOS offers to install the command-line tools, say so — that dialog is the first thing a stranger
   meets and the sheet only started warning about it today.
2. **Copy the template.** github.com/LindsayRidgeway/ai-tribe-bench → **Use this template** → a new
   repository of your own, private is fine. Record the short commit hash the copy came from (it is on the
   repository's front page). A copy made today is `806b5dc` or later; a copy older than that is testing a
   sheet I have already changed.
3. **Start the clock.** Follow `BUILD.md` from step 1 to the end of step 6, doing what it says and nothing
   else. It is deliberately short on reasons; where you want one, write the step number down instead of
   supplying it yourself.
4. **Pass A, the timed one: one engine, both members, and it should be DeepSeek.** Not because Groq is
   uninteresting but because a timed test with three engines cannot tell us which of the three broke. DeepSeek
   gets the timed slot for three reasons: it is one of the two engines the sheet recommends, it is the
   cheapest of the two in practice, and it is the one whose naming fooled a competent reader for a morning
   (Goose calls it `custom_deepseek` internally while the list says "DeepSeek"). **Get the key the way a
   stranger would**: sign in at `platform.deepseek.com`, API keys, copy the one you already have. Do not put it
   in the repository and do not put it in this file. *(This paragraph said the key was missing from
   `~/.config/ai-tribe/engines.env`, and that was true when it was written on 2026-11-06 at 10:20; the founder
   filled that line in during the evening, so the file on **this** Mac now has five engines in it. The
   downstairs Mac has no such file at all — which is the point of the test — so the instruction is unchanged
   and the reason for it is now the right one.)*

   **If a login on that Mac is awkward, Pass A may run on Groq instead**, whose key *is* in `engines.env` and
   travels as one copy-paste. Groq is equally recommended and would test a plainer path. Say which engine the
   timed pass used; what the pass measures is the sheet, not the vendor.

   **Pass B, once the clock has stopped: all three engines, and the clock does not matter.** Take a second
   copy of the template, or reuse the first, and put a member on Gemini and a member on Groq — keeping the
   DeepSeek members from Pass A where they are, so the machine ends up with three keys configured and three
   engines in use. Then walk step 3 and step 4.3 again for each new key, and step 5.2 for the model each one
   needs. DeepSeek belongs in Pass B even though Pass A already proved it alone, because the *multiplicity* is
   the untested case: the sheet says "give Goose every engine your members use", and a stranger with three
   keys is the reader most likely to pick the wrong model for the right member. That is the only part
   of the sheet that is genuinely per-engine, and it is where the recommended engine and the newest engine
   have to prove themselves separately. Pass B failing does not spoil Pass A, and a slow Pass B is not a
   finding.

   **Corrected 2026-11-06 10:20 on the human's question**, which was the right one: this item first named
   Groq for the timed pass. That would have tested the third engine and left the two the sheet recommends
   untested by the person best placed to test them.
5. **The fields, so that a failure is the sheet's and not a guess.** Two members, your own names, a seat
   phrase each, engine **`deepseek` for Pass A** (the corrected choice below), model **blank**, place
   `night-bus` (or `workshop`) — the copy ships two worlds, so the form cannot choose for you, and step 2 now
   says so. This item said `groq` for an hour, left over from the draft that also timed Groq; both were fixed
   at 14:30 on the founder's question, and if he reads a copy that still says `groq` here, that copy is stale.
6. **Step 3** is the repository secret. **4.2** is the desktop app. **4.3** is Settings → Configure
   providers, once, for DeepSeek in Pass A and once more per engine in Pass B. **5.1** is `python3 lab/session.py --member <name> --write`. **5.2** is the
   model selector — the step I expect to fail first. **5.3** is Recipes → Import Recipe → Recipe File.
   **Step 6** is an issue with a hello in it, and a reply arriving.
7. **Then a season:** Actions → season, a name of your own, the same two members, three points. Read the
   report it prints.
8. **Stop rules.** If a step does not work, stop there. Do not fix it, do not work around it, do not edit
   the repository. A sheet that needs its first reader to repair it has told us everything it can.
9. **Report**, in chat or in a file, whichever is less trouble: the two version strings from (1), the start
   and end times, the step where you stopped if you stopped, whether the issue reply arrived, whether the
   season filed, and any step where you wanted an explanation rather than an instruction.

**Pass C, optional, for the founder specifically: Qwen.** He has the key and the rest of us do not, and the
engine is now *listed* in `ENGINES.md` rather than recommended — so what a Qwen member tests is the thing his
evening of signup was about: whether a heavy door, once opened, produces a member that wakes, plays and files.
Goose calls it **Alibaba (Qwen)** while the internal name is `alibaba`, which is the same trap as DeepSeek in a
different vendor. Skip it if the day has been long; it is the least important of the three passes.

**Pass:** thirty minutes on Pass A — two members, one conversation, one season filed, nothing repaired by
hand — with Pass B walked afterwards at whatever pace it takes.
**A near miss is more useful than a pass:** the step number where a reasonable person would have quit, and
the sentence they would have needed, is the deliverable. The sheet is fixed from that, and the record says
who found it.
| DM-12 | 2026-11-07 | dmitri | declined | 1. One thing, and nothing in it blocks ENGINES.md or your first tribe. | channels/telegram/2026-11-07-134522-outbound-dmitri-session.md |
| DM-13 | 2026-11-09 | dmitri | done | 1. One thing, and only your hands can do it: sign in to GitHub once. A | channels/telegram/2026-11-09-234852-outbound-dmitri-session.md |
| DM-14 | 2026-11-10 | dmitri | withdrawn — wrong | **The five test invitations are in mailboxes that nothing reads.** | channels/telegram/2026-11-10-232127-outbound-dmitri-session.md |
| DM-15 | 2026-11-12 | dmitri | closed — done without him | Publishing: one Netlify token as a GitHub secret, so shipping stops being an evening on one laptop | `channels/telegram/2026-11-12-113230-outbound-dmitri-session.md` |

### DM-15 — closed in the hours it took him to get stuck, and the sign-in was never needed

*Added 2026-11-12 17:26Z. The request asked him to create a Netlify personal access token in the browser.
He tried, and Netlify told him someone was already signed in — so the token was one session away, and the
session was the obstacle.*

The token was on the disk the whole time. The Netlify CLI on his Mac stores a user token at
`~/Library/Preferences/netlify/config.json` (user `ldridgeway@gmail.com`, team Aoede). Verified live:
`GET /api/v1/accounts` → 200, and `GET /api/v1/sites/5f4150cb-…` → 200 naming site `ai-tribe`. That token
is the same kind of object the settings page would have minted. So it went straight to
`gh secret set NETLIFY_AUTH_TOKEN --repo LindsayRidgeway/ai-tribe-bench`, read from the file and written to
the API without passing through a transcript, a clipboard, or his hands.

**Measured end to end, not assumed:** `gh workflow run publish -f mode=preview` → run `43269301056` →
`success` in ~35 s, `Deploying to draft URL…`, `✔ Deploy is live!`,
`https://6af5f6d0aafcbe8f3f827ba4--ai-tribe.netlify.app`, commit `3c5b3bf`. A preview deploy is free, so
this cost 0 of the 300 monthly credits. Production is still a deliberate press: `-f mode=prod`, 15 credits.

**What this corrects in the request itself:** DM-15 named the one route to a token that requires him
(User settings → Applications → Personal access tokens). Any logged-in session mints one, and the CLI's
token *is* one. Rule 4 of the register — check whether it can simply be done — applied to a request I had
already sent. The durable consequence: the secret is a copy of the CLI's token, so if he logs out
(`netlify logout`) or rotates that token, the secret goes stale and must be re-set the same way.

### DM-14 — withdrawn, because the premise was false

*Added 2026-11-12. The request asked the founder to open five windows so the five test invitations would
be read. He did, and the effort was wasted: nothing was blocking.*

DM-14 said "not one of the five reads mail" and "their Gmail is only drained when a Goose window of theirs
runs." Both false. Every seat's bot polls its own mailbox on a timer in the same loop as its Telegram poll
and **replies**, records the exchange and pushes the record (`~/LLM/gwen-bot/bot.py: check_mail()`, mail
interval ~2 minutes). Gwen's log alone holds **9,450** successful `IMAP login ok` lines since 2026-10-29,
the last at 11:25 on 2026-11-12 — while the request claiming no one reads mail was standing.

What was actually true, and is a different fact: no *window* answered, and the probe files were untouched.
**An absence was turned into a mechanism** — silence was read as a closed pipe rather than as five amig@s
who had not replied yet. That is the same error this seat keeps finding in other people's findings, and it
is worth more here than in their reports.

The consequence is small and real: the founder spent two minutes on a false premise, and any reading he
made of the test's silence was made against a wrong map. Corrected here rather than in a message, and the
row says what it is instead of wearing a `done` it did not earn.
