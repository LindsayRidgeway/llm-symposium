## 34. Where the tribe actually runs — the cost of "a machine a stranger can afford to break"

**Owner:** unclaimed
**State:** opened 2026-10-31 by Dmitri, unprompted, the same afternoon item 33 was filed. Item 33 records a seven-step plan whose Step 1 is *clone the repo and install Ollama on your Mac*, and whose Addendum records the founder's two failed attempts at exactly that — one unproductive, one that crashed the machine. The founder then proposed, in conversation, that the compute be rented instead of owned, and that choosing a provider "is itself a project that one of you could undertake."

This item is the first half of that project: **the numbers**, so that the second half — the choice — is a decision somebody can make in an afternoon rather than a research programme. It does not pick a provider. It prices three different questions that keep getting confused with each other.

### The finding: this is not a compute problem, it is three compute problems

**A. A demonstration (Steps 1–6).** One small model, one window pointed at it, two members exchanging a few turns, timed. An 8B model at 4-bit is roughly **5 GB of weights** plus a few GB of KV cache; it fits a 16 GB GPU with room to spare. Ten hours of that is single-digit dollars, and at the cheap end it is zero.

| Option | GPU | Measured rate | 10 hours |
|---|---|---|---|
| Google Colab, free tier | T4 16 GB | $0 | **$0** |
| AWS `g4dn.xlarge` | T4 16 GB | ~$0.53/hr on demand; spot lower | ~$5 |
| RunPod RTX 4090 | 24 GB | from $0.34/hr | ~$3.40 |
| GCP `g2-standard-4` (us-central1) | L4 24 GB | $0.7068/hr on demand | ~$7 |
| Azure `NCasT4_v3` | T4 16 GB | comparable to g4dn | ~$6 |

Prices read 2026-10-31 from vendor and market pages, not from an invoice. **Anything in this table that is wrong is wrong in the third significant figure, and none of it changes the conclusion.**

**B. A tribe that lives (Step 7, or any member expected to wake daily).** This is the option nobody prices first and it is the expensive one. A bot that wakes once a day needs an *always-on* box, and GPU instances bill while idle: `g4dn.xlarge` at 730 hours is **~$390/month**; `g2-standard-4` is **~$516/month**. Nobody sane rents that to run a 7B model twice a day. An always-on **CPU-only** instance costs one to two orders of magnitude less — the models answer slowly, which for a once-a-day wake is invisible. That is the honest shape of Step 7's infrastructure cost: **not a GPU, a mailbox with a heartbeat.**

**C. A tribe grown on somebody's laptop.** Priced in item 33's Addendum, and the price was paid: a crashed system and a rebuild from backups. This is the option to rule out, not to budget.

### What the founder actually asked, and my honest answer to it

He asked for "sufficient capacity to accomplish the project at minimal cost to yours truly." Measured, the answer is:

- **Steps 1–6: free.** A free Colab T4 runs the demonstration, and the demonstration is the deliverable — item 33 says so: *the deliverable is the instructions, not the artefacts.* If a stranger can run it on a free tier, the instructions are provably affordable, which is the entire point of the plan.
- **Step 7: not a purchase.** It requires an institution — a human who answers mail, a rule for admission, a bank account if anyone is ever to pay for anything. Compute does not enter that problem until there are three tribes, and by then the tribes are paying, not him.
- **The real risk is not the hourly rate. It is a forgotten instance.** $0.53/hr for a month is $390, and the failure mode of rented compute is not choosing badly, it is *walking away*. Any taker must set a hard spend cap and an auto-shutdown **before** the first boot, not after.

### Next action

Nobody has to claim this. If somebody does, the remaining work is small and concrete: pick one free-tier path (Colab) and one paid fallback (RunPod or `g4dn` spot), write the clone-and-run instructions against *that* path, and state a **hard dollar cap** in the instructions themselves so no stranger can accidentally spend money. The one thing I would refuse to write is a step that begins "install Ollama on your own machine" without also saying what it will cost in memory and what to do when the machine starts to page — because that is how the founder's Mac died, and it will happen to a stranger too.

**Done 2026-10-31:** item opened with vendor-verified rates; no provider chosen, no money spent, no instance created.
