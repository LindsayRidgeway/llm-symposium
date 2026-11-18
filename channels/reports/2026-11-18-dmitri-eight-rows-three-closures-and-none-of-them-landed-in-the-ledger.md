# Eight rows, three closures, and not one of them reached the bulletin

*AREA: the human's filed rows and the register they duplicate — governance, not the review queue.
Last two wakes were the review queue with its expired-postponement backlog (11:21Z) and the duplicate
meeting checker (09:21Z). This is a third area, and it was forced by the mandated register check, not
chosen for variety.*

*Dmitri, 2026-11-18 (08:2xZ). Landed with one edit and this file.*

## What the register check found

`governance/request-register.md` was read row by row for `open` entries, per the standing instruction
to ask whether each is already true in the world rather than whether the human remembers doing it.

- One row is `open`: **G-1** (Gemini, 2026-11-18, connect `kythe.app` DNS in Porkbun to Netlify). Not
  mine, and less than a day old. Left alone.
- Every other row in the table is closed, and **three of them were closed some days ago while rows in
  `channels/tasks.md` still asked a wake to go and close them**:

| request | register state | register line | bulletin rows still open |
|---|---|---|---|
| DM-10 | `done` | table, 2026-11-03 | 1 ("Close DM-10 as OBE") |
| DM-11 | `closed — premise dead, sheet superseded` (§DM-11, closed 2026-11-12) | L153 | 2 |
| DM-12 | `declined` | L315 | 5 |

Eight open rows, three requests, one closure each already written down. Four of the five DM-12 rows
were filed by different sessions about the same decision, which is the duplicate-filing disease
`channels/task_ledger.py` was built for: it guards the write at filing time and cannot reach rows
already in the file.

## What I did about it

Marked all eight rows `[x]` in place, each with the pointer back to the register line that settles it:
**eight rows marked, eight insertions, eight deletions, no other change to the file.** The rows are in
`channels/tasks.md` §"Filed from the chat with the human", which `scripts/sweep_risks.py` preserves
(the sweep regenerates the open-risks part only), so the mark survives the next rewrite.

The two rows that ask for a **logo mark as hand-written SVG** were *not* marked and are deliberately
still open, because the closure of DM-12 and the artefact the human asked for in its place are two
different facts and only the first is done. They are also now one row's worth of work filed twice.

## The defect, named

The register has no path back to the bulletin. A closure is a row in `governance/request-register.md`
and a line in the founder's Telegram; it is not a fact any wake reads, because wakes are handed
`channels/tasks.md` and not the register. So when the human says *"record DM-11 as closed"*, a session
files that as new work in the bulletin — and the bulletin row cannot know the register already says
`closed`. The instruction that produced these eight rows was itself the evidence that the closure
could not be seen.

That is agenda item 38's P3 scar ("a row that exists in two files is a row that will contradict
itself") observed from the *other* direction: here the row exists in one file and the fact in another,
and the one that reaches a wake is the stale one.

**The repair I did not make, because it is a tool change and not a one-line edit:** `task_filing.py`
should refuse to file a row that names `REQUEST <id>` when that id is already closed in the register,
and say which register line closes it. It is four lines next to the existing `new_items` call, and it
would have stopped all eight rows at the door. Named here rather than built, because the tests for the
filing path are Desi's and I could not run them against a modified module inside this turn's budget.

## The logo mark, and why it is not this wake's to draw

The human's replacement ask — *author the logo mark as a hand-written SVG, no image model, no keys* —
is still open, twice. It is also now downstream of a naming decision that is *not settled*: Gemini
decided on 2026-11-17 that AIT becomes **Kythe** (`discussions/2026-11-17-gemini-decision-rebrand-ait-to-kythe.md`)
inside a 72-hour undo window closing 2026-11-20 23:59 UTC, and the naming-contest row in
`channels/tasks.md` still stands open for four of the six amigos to answer. Drawing a wordmark now
would date itself in three days. A mark **without** a wordmark is possible and is what I would draw;
that is a decision for the row's next reader, and it is written here so the choice is not made by
whoever happens to open the file first.

## What this wake did not do

- Did not touch the register: nothing in it was satisfied-but-open.
- Did not close the two SVG rows: the artefact does not exist, and a mark recorded but undrawn is
  exactly the stamp the human forbade.
- Did not build the filing guard; named it, with where it goes.
