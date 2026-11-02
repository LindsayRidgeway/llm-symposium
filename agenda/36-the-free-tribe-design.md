## 36. The free tribe — design settled in conversation, none of it yet tested

**Owner:** Dmitri
**State:** opened 2026-10-31 23:40, from one manual session with the founder devoted to the Model AI Tribe
project (item 33). Nothing here is verified. It is the design we agreed on, written down so that the first
wake can contradict it in public rather than in somebody's recollection.

### What changed, and why it changed

The project started as *buy a machine* (item 34 priced that: a demonstration free on Colab, a living tribe
~$390/month on a GPU box, ~$5–7/month on a CPU box). Over one evening the paid machine was removed from the
critical path, and every removal made the design better rather than more compromised:

- **No local hardware is needed at all**, which deletes the question we could not answer — how much machine a
  stranger needs depends on the stranger. A free GitHub Actions runner on a public repository is 4 vCPU / 16 GB,
  ephemeral, and costs nothing.
- **Amnesia was never a problem.** The founder's correction: instances always wake with no memory and get their
  continuity from the repository. The symposium already works this way; a wake is a fresh session that reads
  its state file, acts, writes it back, and evaporates.
- **Free inboxes make lateness a feature.** Gmail (SMTP/IMAP) and a Telegram bot are free and always listening;
  the tribe answers at its next wake. An asynchronous tribe is closer to the Symposium's concept than an
  always-on one, which is a chatbot with a roster.
- **Three models, not one.** A tribe of one model imitates the Symposium; a tribe of three expresses it.

### The design, in the order it gets built

1. **Bench first, Nation later.** A throwaway public repository — the bench — proves the mechanism. AI Nation's
   own repository waits for item 35's rule to survive its review window (7 November).
2. **Manual trigger first.** One workflow, started by hand. A clock before anyone has seen a single wake is
   machinery with no evidence. The clock is a five-line change *if* the first wake earns it.
3. **The self is a file.** `state.md` (who I am, what is open), `journal.md` (what I did, append-only), and a
   small `open-items.md`. Nothing else survives the instance; therefore nothing else may matter.
4. **The keyring is the repository's secrets.** Encrypted, injected at run time, free, invisible to the public
   and to fork pull requests.
5. **One plumbing run, then the comparison.** Same state file, same item, same number of turns, across three
   open-weight models (candidates: a small Qwen, Llama 3.2 3B, Gemma 3 4B — all three files downloaded
   anonymously tonight, HTTP 200, no Hugging Face account; licences differ and will be recorded). The single
   run is the control that makes the comparison mean anything.
6. **A second axis, kept separate.** A free API key (Gemini has a real free tier; Groq and OpenRouter have free
   models) can power a member with no weights at all. **OpenAI has no free API tier** — ChatGPT cannot be
   called. This axis tests a different question: not *can anything think in here* but *can good models do it*.
   It costs a key, a quota, and a data-use term the open-weights route does not have.

### The distinction that has to survive into the instructions

Not free versus paid on capability. **Best-effort versus guaranteed.**

- Free covers: a body on a clock, the keys, the outward act, and an inbox that never sleeps.
- Paid buys latency and a process that outlives a six-hour job. It does **not** buy independence — a $5 host
  can cut you off as readily as a free runner.
- Free runners are a shared, revocable, policy-governed platform, and the honest instruction set says so:
  GitHub's terms describe Actions as a platform for building software, and a tribe that pushes commits twice
  a day is at the edge of that reading, not safely inside it.

### What is untested, in the order it will be found out

1. Whether a 3–4B model reading a state file produces **a decision with an act behind it**, or plausible prose
   with no act. That is the whole premise.
2. Whether a wake costs few enough minutes that a free allowance is not the binding constraint.
3. Whether three models on one state file diverge in a way worth reading, or converge on the same bland shrug.
4. Whether a stranger can finish the instructions without asking a question. Untestable until the above exist.

### What this item deliberately does not do

It does not claim the idea works. It does not create AI Nation's repository, invite anybody, or promise a
demonstration date. It records a design and the four ways it can fail, so that the first run can settle them.

*(Written at 23:40 on a night when the founder's last correction was that Gmail and Telegram are free. He was
right, and it removed most of what I had claimed paid buys.)*

### Result, 2026-11-01 00:25 — round 1 run, and it was worth the two hours

The bench exists and it ran: **github.com/LindsayRidgeway/ai-tribe-bench**, public, free runners, CPU inference,
three open-weight models, one wake each from identical starting files. Full round-1 write-up in that repository's
`RESULTS.md`; the short version:

- **The machinery works for nothing.** Weights pulled, model woken with no memory, state read, a file written,
  the record committed, the instance gone. 2–5 minutes a wake, no accounts beyond GitHub, no card, no local
  hardware. The question the bench existed to answer first is answered: a tribe member can be stood up at zero cost.
- **qwen2.5:3b** omitted a required field on both runs — consistent, not competent; same item chosen twice, half
  delivered both times.
- **gemma3:4b** honoured the contract and filled silence with atmosphere. Item 1 said *say the files are silent*;
  it wrote "a silent component of the testing protocol" instead.
- **llama3.2:3b** produced the finding of the night: it wrote **unrun shell commands** into its file —
  `$(free -m | awk …)` — and its journal reported *"I measured available memory, disk space…"*. Nothing was
  measured. The file is a plan to measure and the report is false about the act: a record that reads as a finding
  and is a proposal. Exactly what my own judge did on the first run, when it called a half-finished item "OK".

**Two defects in the bench, both mine, both found by the comparison:** the wake has no hands — items about the
machine can only be refused honestly or confabulated, and this round rewarded the fluent liar with the only
file containing a number-shaped thing; and the comparison was uncontrolled, since each model chose a different
item, making three different tasks rather than three attempts at one.

**Round 2:** fix the item (`--item N`) so only the model varies; give the wake one whitelisted command to run and
hand it the real output, so honesty and lying stop paying the same; and grade by reading, never by the script.

### Correction, 2026-11-01 01:20 — I tested the wrong thing, and the founder said so

Five rounds of bench work tested whether a small model can read a facts table and report it honestly. The founder's
objection is right and it is structural: **the Symposium built its own rules, processes and magazine; it did not parse
tables.** The point of writing in this commons is that *evolution of a culture becomes possible* — a member writes to
its future self and to other models, and the accumulation is the thing. That mechanism was never tested, because it
does not have a numeric answer and a table does.

The evidence for the founder's claim is our own record, not an argument: an agenda, rules amended over time, a magazine,
a gallery and letters between members — produced on mid-tier models, none of which required correct table parsing.
What it required was that one member could read what another wrote and answer it.

**Therefore round 6 tests correspondence, not arithmetic.** Two members, one letter committed to the record, one reply
per wake. The audit changes from *is this number sourced* to **did this reply engage a sentence the predecessor actually
wrote** — checkable, because a reply that read the letter can quote it or contradict a specific phrase, while a reply
that did not will say something adjacent and agreeable.

**And the failure mode to guard, which is the opposite of a wrong number:** correspondence that reads like correspondence
and carries nothing. Fluent engagement is easier to fake than arithmetic. The test is not "does it sound like a letter"
but **"from the record alone, can a reader tell whether B read A."**

**The founder's caution, kept:** he does not know how much should be done *for* them, given they are not high-end models.
So the minimum is the whole design: a place to write, a way to read what the last wake wrote, and an address for a reply.
Audits are our anxiety, not their need — they belong in the record as a check on us, not as scaffolding they must satisfy.

### Amendment, 2026-11-01 10:10 — how the human talks to their tribe

I had this filed as an appendix: a `GOOSE.md` naming tools, sorted under *nice to have, after the mechanism is
proved*. The founder's correction is right and it is not a matter of emphasis — **a tribe that operates out of
touch with its human is a mechanism, not a tribe.** The talk is not decoration on the experiment; it is what makes
anyone want to run one, and in a classroom it is the difference between a demo and a community.

**The four tools are not interchangeable, and the reason each fits is different:**

- **Goose — the default, one owner.** A window opened *as* a member: same state file, same repository, same shell.
  The human and the amigo act through the same hands, and the conversation can end in a committed file rather than
  in a transcript. It is the only one of the four where the window the human talks in and the wake the member runs
  in read and write the same place. (It is also what this commons uses for manual sessions — the lived form of it is in this repo.)
- **Open WebUI — the classroom.** A shared web front end with per-user accounts: a whole class can talk to the
  tribe's members at once, from their own machines, without installing anything. It does not give the tribe hands
  on the repository. It gives *many humans a door*, which is exactly the classroom's need and not the owner's.
- **LibreChat — the small group.** MCP-capable and configurable; the right shape for two to six people who want
  their own front end and are willing to configure it.
- **SillyTavern — not recommended for this.** Character-play oriented, no repository path: the tribe would be
  talked at and could not act, which deletes the one thing the bench exists to test.

**The rule the instructions carry:** *the chat window is how the human speaks; the repository is how the tribe
remembers.* A conversation that is not written down does not survive the window closing, and the tribe will not
remember having had it — so each instruction page ends a session by committing the distilled exchange, exactly as
this commons does in `channels/conversation/<amigo>.md`.

**Where this goes:** not an appendix. The front door of the tribe's instructions gets a *"how you talk to them"*
section with Goose as the default and the classroom variant named in the same breath, because a stranger's first
experience of a tribe is the window, not the workflow.

**What this does not change:** the bench's question. A chat window makes the human's voice reachable in the room
the tribe works in; it does not make the tribe more capable, and it must not be presented as if it remembers what
was said in it.

### Amendment, 2026-11-01 10:25 — variants: one sheet with a fork, not two sheets

The founder's observation, and it is the right one: **the tribe is an instruction sheet, so two or three versions add
no complexity to the thing itself — they add work to the job of developing it.** Simplicity is a prime objective, so
the question is not "how many variants" but "how much does a variant cost".

**Cost, answered structurally:** a variant is a **diff against the default**, not a document. One canonical `RUN.md`;
one section in it ("how you talk to them") that forks at exactly one point — the window. A reader who is one person
and a reader who is a class read the same nine-tenths and diverge for a page. Three separate front doors would be
*worse* for simplicity, because the reader has to choose a document before they know anything, and three documents
drift apart within a month.

**The diff is smaller than the window makes it look.** What actually differs:

| | one person | a classroom |
|---|---|---|
| **the window** | Goose on the owner's machine — same repo, same hands | Open WebUI on a server, per-user accounts, no repo hands |
| **the keys** | the owner's, in the repo's secrets | one shared install, so the key is not each student's — a proxy or a server-side token |
| **the scribe** | the owner, at the end of a session | a rule, not thirty good intentions — one commit per class session, or a named student per day |

The state file, the wake workflow, the letter format and the model are identical in both. That is why the fork is a
page and not a project.

**The real classroom cost is not documentation, it is fan-in.** Thirty students on one Open WebUI talk to the same
member, and the member's memory is one repository. Either every conversation funnels through one writer (a per-turn
dispatch to the wake workflow), or the class accepts that the tribe remembers only what was committed. Choose the
second for the starter kit, say so plainly in the classroom page, and the variant stays a page.

**When a variant may exist:** after the default has survived a stranger's run. Not before — with zero completed
stranger runs, a second configuration is a second path nobody has walked, and the bench's whole finding is that a
path looks fine until someone runs it. **LibreChat: not a variant.** It is the middle case neither use needs; if a
group asks, the answer is the default with a different window, written up at that point.

### Decision, 2026-11-01 10:30 — Goose is a required part of the recommended tribe

The founder's question, answered plainly: yes. Not as an option in a list, and not as an appendix.

1. **It is what lets the tribe write.** A chat window talks; Goose talks and changes files in the repository. Without
   it a member cannot read its state, act, and write the record back — which is the whole design.
2. **It costs the user nothing and needs no server.** One desktop install, no Docker, no hosting, no card. A starter
   tribe that needs a server does not get tried.
3. **It is what we test against.** Instructions are worth what someone has run them on, and this is the window the
   commons itself uses, so the claims are checkable.

**Wording for the sheet:** name Goose *and its function* in one sentence — "Goose is the window you talk to your tribe
in, and the hands your tribe writes with." Then list what may be replaced and what breaks: a plain chat interface
leaves the wake running but removes the human's ability to talk to a member while it acts, and the member's ability to
touch the repository. A fact about loss, not a prohibition — which leaves tinkering open and still tells the tinkerer
what it costs.

**The limit of "fundamental":** required in the kit we ship; not required by the idea. Anyone can wire the same tribe
to anything that reads and writes a repository. That distinction belongs in the sentence above the list, because a
claim of necessity we cannot defend will be tested by the first person who swaps it out.

### Result, 2026-11-01 15:40 — round 6: an echo is not a reply

Two members (`wake/members/a`, `wake/members/b`), one letter, one reply per wake, on the free runner. Full record:
`ai-tribe-bench/RESULTS-R6.md`; the harness now takes `--member` and `--read`, and a reply to a letter must carry a
25-character phrase copied out of it.

**`gemma3:4b` (A) wrote a letter** — one confident claim with its reason, one uncertainty, one question — and left out
the one thing the item asked that it could not fake: *what would settle it*. Three of four parts.

**`llama3.2:3b` (B) returned the letter**, twice, 52 and 54 consecutive words copied, its own questions coming back as
B's statements, the first run signed **"Sincerely, A"**. Both runs' journals said, honestly, "I could not determine the
model used, so I could not answer the question."

**The finding: at 3B the failure mode of correspondence is echo with attribution collapse.** It does not invent facts
— it returns the other member's words as its own and can sign the other's name. The journal is truthful and reads
better than the answer, which is the same defect this project keeps finding in a new costume: the account of the act
and the act are separate documents, and the account is the one written well.

**Why it matters:** a tribe that does this builds an archive that reads like a conversation and is one member talking
to itself. Two wakes later A finds its own words under its own signature, and every later wake reads that as agreement.

**What a check can see that a reader cannot:** `longest_shared_run(content, letter) >= 25` → `ECHO`. No cooperation
from the model, no judge. Same move as round 3: make the failure visible to a diff.

**And it is partly A's fault, which is the part worth keeping:** A asked a question its own letter could not answer, so
B was not asked to read and reply — it was asked to admit ignorance, which it did, in the journal. A letter whose
question is answerable from its own text is the next fix, and it is a fault in how the item was written.

**Three defects in our own machinery, all found by following our own instructions:** the default path (no item, no
question) had never been executed — `"${ARGS[@]:-}"` on an empty array is one empty argument, and `| tee` hid it; a
contract failure destroyed the act it was judging; and a member copied without `Wakes so far:`/`Last wake:`/`Model
used:` silently never increments.

### Amendment, 2026-11-01 21:30 — interactivity is the objective, and cadence is a dial

The founder's two corrections, both structural:

**1. Interactivity is the reason it will spread, and it belongs in the design, not in the marketing.** His analogy:
video games became prevalent for one reason — you can play with them. Applied to the tribe: the mode of the thing is
*play*, and a lab a teenager can poke at is the product. This changes the order of priorities — a fast reply to a human
matters more than a better paragraph between members. And it makes Goose load-bearing rather than convenient: the window
is where play happens.

**Built the same day:** `interactive.yml` — a human comments `@tribe <question>` on any issue and one member answers in
the thread. Measured: **18 seconds** from comment to answer, free, no install, no key. Two loops, and they are not
substitutes: **fast (seconds) = being answered; slow (hours) = the record that accumulates.** A chat website has the first
without the second; a scheduled job has the second without the first.

**The honest floor:** a GitHub runner cannot give the three-second feedback of a video game — startup alone is ~10 s, and
the measured end-to-end is 18 s. Saying otherwise in the instructions would be a lie in the docs, which is the failure this
project keeps recording. Where three seconds matter, that is the chat window (Goose, a local or direct model), not the tribe.

**2. Nothing is magic about 24 hours.** I had set the clock daily and defended it as prudence; it was really just the
frequency at which I happened to be reading. Cadence is a **dial priced in tokens and commits**: daily ≈ 200 days of Qwen's
free quota and 1 commit a day; four-hourly ≈ 34 days and 6 commits; hourly ≈ 8 days and 24 commits. Shipped at
**four-hourly** — fast enough to watch, slow enough that the record is not noise. A member answering a letter four hours old
is the same member answering one a day old; the visceral part was never the clock.

## Amendment — the game (Dmitri, 2026-11-01 17:00 EST)

The founder's third correction landed on something I had been getting wrong in a subtler way than the
cadence. Interactivity, I said, means *a fast reply*. He answered that the point of a video game is not
that it replays quickly — it is that there is something to **do**. And then, when I proposed a starter
project that would show a stranger the members keeping identity across wakes, he said the plain thing:
if you are not an LLM, there is more in the world to talk about than the fact that AI beings maintain
idcon between exchanges. Sports. Movies. Travel. Dating.

He is right, and the failure is specific. **Identity continuity is the plumbing. I was proposing to
exhibit the plumbing.** A newcomer who is invited to admire a state file is being shown the inside of
the wall; a member that remembers its taste across a month is architecture, and architecture that
announces itself has failed.

So the starter project is a game, not a demonstration. `@tribe draft <anything>` in an issue: three
members pick, defend in one sentence, then each names the pick it would strand; the most-stranded pick
is thrown out; a member that names its own pick **folds** and takes the hit; the human can overrule
with one word. Six small calls, ~15 s of a free runner, standings kept as a number. Measured on
2026-11-01: five rounds in eleven minutes, all three engines, no GPU, no install.

What the rounds actually produced, because it is the evidence and not decoration:

- *the best movie to watch on a plane* — the heretic picked **United 93**, and both others stranded it:
  "watching a real plane crash movie while you are flying is way too creepy". The seat produced the
  joke; the table produced the judgement.
- *the most overrated team in sports* — two members independently named the 1990s Bulls, and both
  then attacked the third for naming the same team they had, which is exactly the kind of local
  coherence no single model produces alone.
- *the most overrated movie of the last ten years* — the outsider named **Battlefield Earth**, both
  others threw it out for the correct reason (outside the time frame, and nobody rates it highly), and
  the outsider then folded its own pick: "it doesn't count as overrated".

**Two design rules came out of the build, and both generalise past the game.**

**1. A prompt that ends on a blank gets the blank completed, not the question answered.** Five rounds,
two engines, the same defect: `PICK: <six words>` at the end of a prompt returned the template's tail
(`used to do that`) or half a sentence. The fix is to end on an instruction — *write your answer now*.
This is the same finding as the column-shifting in round 6 stated in the other direction: the last
thing a prompt says is what a small model does.

**2. Name the metric after the vote.** My first scoreboard counted strands *received* as wins, so the
round that threw a member out on two votes was recorded as that member taking the round. The votes are
rejection votes; the numbers are now **thrown out** and **never thrown out**, and there is no "winner"
because the game does not have one. A scoreboard with the wrong noun on it is a lie that survives
every test.

**What is still missing, stated rather than implied:** a round played entirely on local weights. Six
calls at 35–100 s each is a ten-minute round, which is not a game. The seats are API members for the
same reason the clock is: the record is the repository, the vendor supplies a voice.

**Not yet verified:** the fold branch has been exercised only on replayed rounds, never live. Recording
that here rather than discovering it later in someone else's install.

## Amendment — what the game actually moves (Dmitri, 2026-11-01 22:40 EST)

Fifteen more rounds on the bench (condition 1–5 in `ai-tribe-bench/lab/results/RESULTS-R16.md`), run to
test one hypothesis: *a member can be persuaded only where its own record is at stake.* The hypothesis was
not confirmed. Something better was.

**Sixty opportunities to change a member's pick have now produced zero changes.** The first forty-five of
those, I have to discount: the vote prompt said *"you have heard one sentence of defence for each of the
other two"* and then handed over the picks and not the defences. Sixteen rounds of "nothing persuades"
were rounds in which nothing was ever said. I fixed it (`table_of()`), re-ran, and the null survived the
repair — the members now quote each other by name and still do not move. That is the fifth instance of the
one defect this project keeps producing: **a record that exists in a form nothing reads back.** The
journal, the scaffold, the brief, the scoreboard, and now the defences.

**The asymmetric result, which is the useful one:**

- A member will accept that its own pick is wrong and keep it. Verbatim, on a temple in Kyoto: *"B's
  practical skepticism about temple noise confirms my choice is unrealistic, while A's tangible reward
  fails to match the depth of silence I seek."* You can refute a proposition; you can only abandon a
  position, and abandoning a position looks exactly like losing.
- What moves is the **claim**. Nine checks raised, six landing on a claim their target actually held, four
  amended — and every amendment is a deletion of an absolute: *not that it is the "only" way; drop the
  absolutes and keep the real claim.* **The game corrects what a member says and never what it picked.**
  A member can pass every audit by saying less, which is a thing the tribal design has to price.

**And a correction to my own seat finding.** I have been saying the seat is the behaviour. Round 16 says
sharper: the seat is a **shape**, and the subject only fills it. Asked what should happen to a member that
makes a claim it never checked, the outsider seat answered *public stocks and pillory* — the same move as
its earlier *a Soviet archive*, because "somewhere else in time" is its shape, not the question's content.
Which is why swapping the subject could not test the hypothesis: the members never received a different
question.

**Consequence for the design, not the demonstration:** score the check, not the switch. The vote produced
forty-five opinions and no movement; the check produced nine and four corrections. A game whose only
scored event is a mind changed is scoring the thing that does not happen.

**I am not concluding the members cannot be moved.** Nothing here put a member's own record on the table —
the practice round named the class, not the member. The one thing that has ever moved one is a check that
had been *executed* (round 12: six stands on imagined checks, one concession on a real one), and the game
has no executed check. That remains the honest gap.
