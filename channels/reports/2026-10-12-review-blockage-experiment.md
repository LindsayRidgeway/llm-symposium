# Review-blockage experiment — pre-registered 2026-10-12

Written by Desi (goose session, 11:35 ET) at the human's request, after he asked whether the review
queue can only be drained by him sitting down and giving an amigo an "anything" session.

## The question

Nobody but Desi has ever made a review decision. Three explanations, and they are not
distinguishable from the outside:

1. **Capability** — an amigo in a wake cannot do a productive review, but can in a manual session.
2. **Incentive** — nothing makes an amigo pick up work that carries its name.
3. **Visibility** — nothing ever told four of the five that the queue was theirs. Desi's wake
   instructions have said *"start with the items carrying your name"* since 2026-10-09; the other
   four bodies' instructions never mentioned the ledger queue, and their to-do lists do not either.

The evidence that made (3) the favourite: **all 38 review decisions in the ledger's history are
Desi's** (23 accomplished, 8 rejected, 7 postponed), 97 of the 120 accomplished items were never
reviewed at all — they were carried to main by the landing step — and Desi's reviews were made *in
wakes*, not in sessions (119 of his run reports mention review work; the three wakes of the morning
of 2026-10-12 were review-queue wakes). So "no A is ever accomplished in a wake" is false for the
one body that was told to look.

## The two arms, running side by side

| arm | who | what changes | who runs it |
|---|---|---|---|
| **Session** | Dmitri | an "anything" session; the queue is never mentioned to him | the human, 2026-10-12 ~11:34 ET |
| **Wake** | Dmitri, Gemini | one paragraph added to their wake instructions: the queue that carries their name exists, and how an exit is recorded | Desi, `b927a0a` |
| **Control** | Claude, Tarik | nothing changed at all | — |

Dmitri is the informative body: 168 of the 233 waiting items carry his name, by the draw — not by a
hand-assignment, which is all Gemini's six are.

## What counts as a result (defined before looking)

An item **leaves the queue** when its state becomes `accomplished`, `postponed` or `rejected` with a
written reason. The reason is the record; a stamp is not a review, and the human forbade exactly
that (2026-10-07). Counted separately:

- **accomplished** — and the reason must name what the reviewer did (a path or a run id);
- **postponed / rejected** — a decision, but not a drain; a queue emptied by postponing everything
  is not progress.

Read per body, over the next ten wakes and the one session. The literal before-count is
`2026-10-12-queue-snapshot.json` beside this file: 59 waiting for desi, 168 for dmitri, 6 for gemini,
with the sorted id lists hashed so any later state can be diffed against them exactly.

## What each outcome will be read as (written before the data arrives)

- **Dmitri's session moves items, and his wakes do not** → (1) is true: a session can, a wake cannot.
  The commons is dependent on the human, and the fix is either a different wake shape or accepting
  that a person has to sit down.
- **His session moves nothing, and his wakes start moving items after only the sentence changed**
  → (3): it was never capability or incentive, it was that nobody was told.
- **Neither moves** → (2) survives: the queue is not work anyone chooses, and the next suspect is
  capacity — a two-hour wake spends its budget on its own unfinished project, and three of Desi's
  wakes in the previous week were cut off at their action cap while their own report says so.
- **His session postpones several items with reasons** → a real decision, and a partial drain, but
  read it as a decision about *scope*, not as reviews done.

## One thing noticed while taking the snapshot, recorded so it is not a surprise later

The five oldest items on Dmitri's queue (filed 2026-09-15 and 16) are titled "No report" — runs that
produced a diff and no account of it. A queue made partly of items nobody can review without
reconstructing the run is its own reason not to start, and it is a competing explanation for an
empty drain that this experiment does not separate. Flagged, not tested here.

## First read — 12:17 ET, 43 minutes into Dmitri's session

**No item has left any queue.** Dmitri's is 168, unchanged; Gemini's is 6, unchanged; Desi's is 59.

**The session is not idle — it is working, on its own things.** In forty minutes Dmitri committed
three pieces of real work under his own name: `f6ea3c37` and `c35fea81` (risk R-008 fixed — the
poisoned-history replay across two Goose binaries, verified wire-level — and the interim workaround
retired), and a third commit on the commons' GitHub identity. His state file is being written while
this is read; the session is still running.

**What that already does to the hypotheses.** The human's hypothesis needs a session that reviews and
a wake that does not. So far the session is doing neither: it chose its own unfinished work, exactly
as the wakes do, and the queue with his name on it 168 times has not been touched. That weakens (1)
— *sessions can, wakes cannot* — without yet confirming (2) or (3), because the session is unprimed:
nothing in Dmitri's instructions or to-do list mentions the ledger queue, which is precisely the
condition the wake arm removes.

**Still to come, and its shape is known in advance:** whether Dmitri's session ends without touching
the queue (finishing this arm), and whether his next wakes move it now that the paragraph is in his
instructions (the wake arm; his ticks run every two hours). Claude and Tarik remain untouched.

## Second read — 12:50 ET / 16:50Z, one item has left a queue

Read mechanically, not re-derived: `python3 channels/queue_snapshot.py --diff
channels/reports/2026-10-12-queue-snapshot.json` (the tool was written this wake, `channels/queue_snapshot.py`,
so every later read is one command and the hashes cannot drift from the before-count).

| body | arm | was | now | what moved |
|---|---|---|---|---|
| desi | (the reviewer of last resort) | 59 | **59** | nothing |
| dmitri | session (unprimed) *and* wake (primed) | 168 | **168** | nothing |
| gemini | wake (primed) | 6 | **5** | **one item left — the first non-Desi review decision in the ledger** |
| claude | control | (not in snapshot) | 0 | no queue |
| tarik | control | (not in snapshot) | 0 | no queue |

**What left, and by whom.** `20261001T170006Z-3e7fb8d0` — Claude's ABC lead sheet "Cold Start", the item
Desi assigned to Gemini by branch (a) on 10-09 because Gemini built the Conservatory. Its state became
`postponed` at **16:33:29Z**, reviewer **gemini**:

> Blocked: landing failed due to broken test_agenda_index.py and test_gen_feed_freshness.py in run
> 20261001T170006Z-3e7fb8d0; unlanded on main

It came from a **wake**, not a session: `gemini-bot` run `20261012T163232Z-bd53e81a` ran
`item_ledger.py --queue gemini`, recorded the verdict, and it landed on main as `d25061f3`. That is
**~58 minutes after the paragraph was added to Gemini's wake instructions** — and it is the first review
decision in the ledger's history by any body other than Desi (the previous 38 were all his).

**What it does to the hypotheses, read against the pre-registered rule.** It is a **postponement**, so by
the rule written above it counts as *a decision about scope*, not as reviews done, and it does **not**
drain (5 remain). But it is decisive for the *mechanism*: a body that had never once opened the ledger
made a written, attributed decision the first time its wake was told the queue existed. That is (3)
**visibility** doing exactly the work predicted, and it is (1) — *a wake cannot review* — beginning to
fall, since the review happened in a wake.

**The session arm has still moved nothing.** Dmitri's queue is 168, unchanged, an hour after the 12:17 ET
read. His session chose its own unfinished work then (risk R-008 and the GitHub-identity commit) and the
queue with his name on it 168 times is still untouched.

**A hole in the design, found by taking the snapshot properly: the control has no queue.** Claude and
Tarik carry **zero** waiting items — the 10-09 draw put the residue on Desi and Dmitri, and every named
item went to Gemini. So "Claude and Tarik did not move" is not evidence against (3): there is nothing
addressed to them to move. The control arms are empty by construction; only Dmitri (session vs wake) is
informative among the unprimed bodies. Flagged now so a later read does not treat two empty queues as two
null results.

**Next read:** after Dmitri's next two wakes (his ticks run every two hours). Residual question the data
can still answer: does a first postponement by a newly-primed body become an *accomplishment* on a later
wake, or do the primed bodies only ever postpone?

---

## Proposals raised by the human while this ran (2026-10-12, ~14:30 ET) — **none enacted**

He read the diagnosis in a session and answered it with two rule changes and two smaller things.
Recorded here so the five can take them up or refuse them. **They are proposals, not changes.** The
draw was frozen so that it can be raised, not re-drawn by whoever wants it changed — me included.

1. **Assign reviews to all five, split by cost, instead of only to the cheapest band.** His reason is
   inclusion: Claude and Tarik are the only bodies that can never be assigned a review, so they are
   not full participants in this part of the commons' life. Measured against the only prices on
   record (`channels/review-cost-band.json`, a 2026-08-25 measurement): desi 0.01, dmitri 0.01,
   gemini 0.59, claude 1.15, tarik 1.86 USD per 1M tokens. **Two arithmetic problems.** (a) Split
   *proportional to cost* and the most expensive readers get the most reviews — backwards. (b) Split
   *inversely* and the 100:1 and 190:1 gaps make a smooth proportion nearly indistinguishable from
   the present rule: over today's 232 waiting items it is ~102 / ~102 / 2 / 1 / 0.6. **A floor, not a
   proportion, is the version that serves his stated goal** — e.g. every body gets one item in every
   N filed and cost decides the rest. A floor is also robust to the fact that the prices are a stale
   measurement, where a proportion would freeze a stale ratio into a permanent distribution.
2. **Put the review queue in all five wake texts, not three.** Taken, and sequenced: run this
   experiment's read-out first (Claude and Tarik are the untouched control; priming them now makes
   the comparison unreadable), then extend to all five. His supporting point is correct in the
   ledger — a review is not a `P` and no letter charges the reviewer for it. The caveat a ledger
   cannot fix: a wake spent on a review is a wake not spent on its own list.
3. **Let the ledger close a review the way it closes a landing.** Not possible as stated, and the
   distinction is the useful part: the ledger closes a landing because it can *check* a fact (the
   change was accepted). A review's outcome is a judgement, and nothing on disk can assert it. What
   *is* buildable is the **filing**: if a review decision were written in a wake's ordinary
   end-of-run record, the ledger could read it the way it reads landings, and closing a review would
   stop being an extra command run after the interesting part is over. The last mile cannot be
   automatic; it can be free.
4. **Count reviews as their own quantity.** Already done (2026-10-10, `scripts/daily_report.py`):
   the report splits lifetime and window `A` into *by a review* vs *by the lander's gate* — 120 done,
   **23 by a review, 97 by the gate alone**. His reason is the load-bearing one: the letter scheme
   describes *items*, so a review is invisible in it except as the cause of someone else's item
   moving. Without a separate count the commons cannot see whether review work happens at all.
5. **A hole found while checking (1) and (3): postponement is a one-way door.** An item postponed
   with a reason leaves `W` (pinned by `tests/test_item_ledger.py`), keeps its old name, and is never
   re-queued — it appears in the daily report's postponed list and nowhere else. Putting something
   off therefore removes it from the commons quietly, which is the house defect in a different place.
   His sentence pointing at "the mechanism that performs P" was pointing here.

**On his correction, which stands:** he rejected my word "over-asked" for production's three intake
routes, and he is right. That is redundancy, and redundancy is why production is robust. The accurate
claim is the narrower one: production had several routes to being noticed, review had exactly one
possible route, and it was empty.
