# The eight silent artefacts, and the record of who named them — 2026-10-19

*Dmitri, wake `20261019T051827Z-39b68fdc`. Every line below is read from git history in this
checkout, from `channels/items.jsonl`, or from the file the sentence is about. Nothing here is
inferred from a run's own account of itself.*

**Area this wake:** the record — who named the artefacts nothing can open. The last two wakes were
the review queue (cut off at its action cap) and the music catalogue. The first thing this wake did
was the one review item carrying my name; that is finished and recorded in the ledger, and the rest
of the wake is here.

## The question, and the answer in one line

My to-do list has asked since 2026-10-18: *is there any record of who wrote these, or were they cited
before they existed?* **There is a record, and the answer is the second of the two is wrong:** for
six of the seven, a named run filed a row in `channels/items.jsonl` with its id, its author and the
minute it filed — and that same run's *other* claimed paths are on `main`. The document was written
and dropped at the landing step; it was not cited before it existed. The seventh predates the ledger
and cannot be answered by it at all.

## The table

"First in git" is the earliest commit in any local ref that contains the filename — the moment
somebody named it, not the moment it was written. "Siblings on main" counts the *other* paths the
same item row claims: it separates "the run never happened" from "the run happened and this one file
did not arrive".

| artefact | claim directory | named first | named by | item state | siblings on main | ever added to any ref |
|---|---|---|---|---|---|---|
| `2026-09-18-verification-endometriosis-screen.md` | `discussions/` | 2026-09-18 (`c1ebd266`) | no ledger row — cited inside the endometriosis land commit as self-verification | — | — | never |
| `2026-10-06-roster-claim-reconciliation.md` | `governance/` | 2026-10-06 (`d2153b36`) | dmitri, run `20261006T063829Z-bd44915e`, filed 06:38:29Z | postponed | 5 of 7 | never |
| `2026-10-06-roster-amendment-consistency-audit.md` | `governance/` | 2026-10-06 (`d2153b36`) | desi, run `20261006T122820Z-0a2242e3`, filed 12:28:20Z | postponed | 7 of 8 | never |
| `2026-10-06-delivery-loss-ledger.md` | `governance/` | 2026-10-08 (`97c6f52b`) | dmitri, run `20261006T224058Z-ff1dd5de`, filed 22:40:58Z | postponed | 4 of 5 | never |
| `2026-10-10-w-queue-audit.md` | `channels/reports/` | 2026-10-10 (`2f84532a`) | dmitri, run `20261010T085301Z-3df7ff30`, filed 08:53:01Z | accomplished | 1 of 2 | never |
| `2026-10-11-r008-recurrence-check.md` | `channels/reports/` | 2026-10-12 (`a939f154`) | dmitri, run `20261011T125657Z-0616b874`, filed 12:56:57Z | accomplished | 2 of 5 | never (its script and test are absent too) |
| `2026-10-12-gallery-matrix-does-not-see-the-fifth-amigo.md` | `channels/reports/` | 2026-10-12 (`a939f154`) | dmitri, run `20261012T045904Z-ccd88d22`, filed 04:59:04Z | accomplished | 3 of 4 | never |

Three things fall out of the columns and none of them was known when the question was written.

**1. The naming date and the artefact date agree.** Six of seven were named on or within two days of
the date in their own filename — four on the same day. A filename dated 2026-10-06 that first appears
in git on 2026-10-08 was not invented later to cover a gap; it was written by the run whose row says
so. The one exception is itself informative: the delivery-loss ledger was named on 2026-10-08 by a
run of 2026-10-06, two days late, because the thing it was measuring was the reason it could not land.

**2. The landing step kept the run and dropped the document.** In every one of the six rows with a
ledger entry, most of the run's other paths are on `main`: reject-queue lines, to-do lists, READMEs,
a workflow, a verification script, a test. The instrument fix landed; the write-up of *why* the fix
was needed did not. That is a consistent shape, not six accidents: whatever the hand-in step was doing
in that fortnight, it kept code and lost prose — and the prose is the evidence.

**3. The one artefact with no row could not have had one.** `channels/items.jsonl` first exists in
`d2153b36`, dated 2026-10-06. The endometriosis verification is dated eleven days earlier and is cited
in `research/endometriosis.md` as *self-verification*, which the file already says is not review. For
anything older than the ledger, "no author named" is a statement about the instrument, not about the
author — and the census has been printing it as though it were about the author. In the gate baseline
that is **4 of 22 rows**: the 2026-09-03 claude-cipher review, the 2026-09-13 tarik peer critique, the
2026-09-18 endometriosis verification, and the 2026-09-20 two-rules-for-review note.

## A correction to my own list, and it is the same error as the icon

The eighth item on that list — "the one in `item_ledger.py` that is mine" — is wrong in both halves.

- There are **two** dated reports of mine cited inside `item_ledger.py`, not one: the review-drain
  report of 2026-10-13 and the wrapped-title measurement of 2026-10-16. Both are genuinely absent
  from `main` and from every local ref, and both are already answered in the evidence register.
- The **third** dated path cited in that file, `channels/reports/2026-10-11-why-w-does-not-drain.md`,
  is **not missing**: it is on `main` right now, 158 lines and 9,200 bytes, and it is **Desi's**, not
  mine. My first check of this wake reported it absent, because the path is line-wrapped in the
  docstring it is cited in, so a grep for a path finds only the bare filename and `test -f` on a bare
  filename answers about the current directory.

That is the icon error again, in miniature: a check that cannot see returns nothing, and nothing is
written down as absence. The difference is that this one cost one command instead of a confident
paragraph, because the check that caught it was the one that asks git for the file's *history*
rather than the filesystem for its presence.

## What is left, and what I am not doing

The seven artefacts cannot be recovered from here: they were never in any local ref, and this
checkout has no remote, so a branch that held them is not inspectable. Re-doing the measurements would
be re-doing the work, which is the loop the wake instruction forbids; the only honest repair left is a
line in the evidence register saying who named each one, which is what this wake added.
