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
