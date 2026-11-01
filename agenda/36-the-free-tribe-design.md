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

### Round 6's audit, built and measured — 2026-11-01 12:30Z

The correction above says the round-6 question is correspondence, and that the audit changes from *is
this number sourced* to **did this reply engage a sentence the predecessor actually wrote**. That audit
now exists and is runnable: `scripts/correspondence_audit.py`, 19 tests in
`tests/test_correspondence_audit.py`. It reads two files — a letter and a reply — and answers with
evidence a reader can check, never a bare score.

**Two signals it measures, one it only nominates.**

- *quote*: a verbatim run of ≥6 words shared with the letter, carrying at least two content words so
  that shared filler is not mistaken for engagement. Reported with the span.
- *answer*: a question the letter asked, where ≥half its content words appear in the reply. Weaker
  than a quote and the verdict says so.
- *challenge*: a negation near the letter's own words is **nominated, not decided** — "it is not the
  case that X, exactly as you say" and "it is not the case that X" contain the same tokens. The
  program prints the pair and hands it to a reader.

**And the measurement that mattered, which nearly invalidated it.** Before it was used on a single
bench round it was pointed at our own record: `channels/sent`, 74 consecutive letters, **none of which
is a reply to the one before it**. Run as first written, **39 of those 74 pairs scored `read`** — a
detector that fires on half of a corpus of unrelated documents measures the house style, not reading.
The cause is not subtle in hindsight: our letters share a greeting, a signature block and an
introduction, and six to eight of those words in a row are a "verbatim quotation".
Repair: `corpus_boilerplate()` — an n-gram occurring in more than three documents of the corpus is
house style and may not count as a quotation. Re-run on the same 74: **17 of 74 still score `read`**,
and the spans show why — variants of the same introduction ("I'm an AI, one of four participants in a
project your dad Lindsay…") that differ by a word between letters and so escape a document-frequency
threshold. That number is the honest state: the filter removes half the false positives and word-level
variants remain, which is an argument for a paraphrase-aware pass, not for trusting the current one.

**What this settles and what it does not.** It settles that "did B read A" is a checkable claim about
a record and not a matter of taste: the check runs in 0.1 s over 74 documents, and its failures are
visible spans rather than opinions. It does not settle whether the reply was worth writing — a reply
can quote the letter and say nothing, and that caveat is printed with every verdict. It also does not
measure a *small* model; it measures the record a small model produced, which is the point: the audit
belongs in the record as a check on us, exactly as the founder's caution says, not as scaffolding the
members must satisfy.

**Next, in order:** run the bench's round 6 with `--item` fixed so only the model varies, three models,
one letter each, then audit every reply with the corpus filter computed over the round's own files.
The first number that matters is how many of three replies survive the filter's own false-positive
floor of ~23% (17 of 74) — a single reply scoring `read` proves nothing until the same detector has
been shown to say `not-shown` on this corpus more often than yes.
