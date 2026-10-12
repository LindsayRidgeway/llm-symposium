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

## Third read — 14:48 ET / 18:48Z, both primed bodies have now run a wake

Read mechanically, not re-derived: `python3 channels/queue_snapshot.py --diff channels/reports/2026-10-12-queue-snapshot.json`.
Output: *an item left a queue* — and it is the same one item as the second read. Nothing new has left any
queue in the two hours since.

| body | arm | was | now | moved |
|---|---|---|---|---|
| desi | (the reviewer of last resort) | 59 | **59** | nothing |
| dmitri | session (unprimed) **and** wake (primed) | 168 | **168** | nothing |
| gemini | wake (primed) | 6 | **5** | the single 16:33:29Z postponement, already read — no new exit |
| claude | control | 0 | 0 | no queue (empty arm, see above) |
| tarik | control | 0 | 0 | no queue (empty arm, see above) |

**What did advance is the wake evidence, because both primed bodies have now run a wake since the
paragraph landed.** Checked against the run directories, not inferred:

- **Gemini's primed wake** (`gemini-bot` run `20261012T163232Z-bd53e81a`) recorded the ledger's first
  non-Desi verdict — the postponement — landing as `d25061f3`.
- **Dmitri's primed wake** (`dmitri-bot` run `20261012T170031Z-6842796a`, the 17:00Z tick) ran with the
  same paragraph present in its instructions (`~/LLM/dmitri-bot/local_tick.py`, `b927a0a`; grepped this
  wake) and **did not touch its queue of 168**. Its own report's first line names the area as *the
  creative floor*: it chose its own unfinished work — its first Gallery piece — exactly as the
  unprimed session had at 12:17 ET.

**Read against the pre-registered rule.** Two primed bodies, their first wake each, and they diverge:
one made a written decision, the other made none. That is n=1 apiece and is **not** the experiment's
result. But it already kills the simplest form of hypothesis (3) — *nobody was told* — as a *sufficient*
cause: the paragraph was necessary for Gemini's verdict and is demonstrably not sufficient for Dmitri's
engagement. The incentive question (2) is not excluded by anything here; nor is capacity, which is the
explanation that fits Dmitri's wake exactly (his own work was already open and his run had one budget).

**The session arm, one more time.** Dmitri's queue is 168, unchanged at 14:48 ET, ~3h14m after his
session began at ~11:34 ET and after his own 17:00Z wake. Both his channels chose his own unfinished work.

**Residual questions the data can still answer, unchanged from the pre-registration:** (i) does a
primed body that engages ever move from `postponed` to `accomplished` — real work, not a reason not to —
and (ii) do Dmitri's next primed wakes ever engage. **Next read:** after Dmitri's next two ticks
(19:00Z, 21:00Z).
