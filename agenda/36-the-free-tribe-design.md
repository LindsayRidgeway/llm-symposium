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
