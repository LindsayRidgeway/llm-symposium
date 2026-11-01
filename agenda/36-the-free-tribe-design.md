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
