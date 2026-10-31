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

### Addendum, 2026-10-31 15:20 — the founder asked for it without the table

He said he did not understand the section above and asked the two direct questions: **is it feasible,
and at what cost?** Fair. The tables answered "which provider" before answering "do we need to pay
anything", and the second question has a much better answer than the first.

**Feasible: yes. Cost: zero, for everything the document actually promises.** The $390–516/month
figure is not the price of the project — it is the price of leaving a GPU switched on for a month by
mistake, and it is quoted here only so that nobody does that.

Plainly, there are three separate needs and they have three separate prices:

1. **A stranger wants to try the instructions without risking their laptop.** Free. Google Colab and
   Kaggle both hand out a free GPU (T4 / P100) to anyone with an account. The demo runs there. Free
   tiers disconnect an idle session after a while, which is fine for a demonstration and fatal for
   anything that is supposed to stay awake.
2. **A tribe member is supposed to wake up every day.** This needs a machine that is always on, and it
   does **not** need a GPU. A 7–8B model at 4-bit fits a small CPU box and answers slowly — a few words
   a second — which is invisible when the wake happens once a day. Two ways to get one:
   - **$0: Oracle Cloud "Always Free" Arm VM.** Two cores, 12 GB RAM, free for the life of the account.
     No GPU, and it doesn't need one. **Caveat recorded because it is recent and it bit the published
     numbers: Oracle halved this allowance in 2026** (it was 4 cores / 24 GB, now 2 / 12), and Arm
     capacity is frequently unavailable at sign-up in popular regions. 12 GB is enough for one 8B model
     and nothing else.
   - **~$5–12/month: a small always-on VPS** (Hetzner, DigitalOcean and similar) if Oracle says no.
3. **Someone wants to experiment fast this weekend.** A rented GPU, only while it is switched on:
   $0.34–0.70/hour. **A weekend of experiments is $5–20.** This is the only case where the tables above
   matter, and it is the cheapest case to be careless in — which is why per-hour rows mislead.

**What I would actually do, if it were mine:** write the instructions against the free path and refuse
to publish a step that assumes a paid instance. The document's own promise is that researchers, classes
and individuals can clone it **at no cost**; if the instructions only run on a rented GPU, that promise
is false and the project has failed at Step 1. A CPU-only free-tier path makes the promise true and
costs the founder nothing.

**And the honest framing that survives all of this:** compute is the *solved* part of the Model AI Tribe
Project. It is cheap, it is free at the bottom, and it will keep getting cheaper. What Step 7 needs is an
institution — an admission rule, a human who answers mail, and a reason for a stranger to join — and no
provider sells that. The expensive part of this plan was never the machines.
