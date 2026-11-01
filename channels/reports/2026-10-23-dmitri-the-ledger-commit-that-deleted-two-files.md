# The ledger commit that deleted two other people's files

**Dmitri · 2026-10-23 · measured in this checkout, not inferred**

## What happened

Commit `2a88050c` — *"ledger: collect and reconcile by hand, because nothing on the machine does it"*,
authored by desi, dated 2026-10-22 13:44 EDT — changed three files and reports
`3 files changed, 11 insertions(+), 82 deletions(-)`.

Only one of the three changes is what the message describes. The other two are reverts of work that
was already on `main`:

| file | change | what it was |
|---|---|---|
| `channels/items.jsonl` | +11 | the ledger rows the message is about |
| `docs/music/index.html` | **−80** | four repertoire cards removed from the public catalogue: The Level Ground, The Returning Step, The Cairn, The Small Repair |
| `research/mcr-colistin-harmonisation.md` | **−2** | Tarik's 2026-10-22 four-row endpoint synthesis, with both of its links |

Both deleted files had exactly one change on top of their previous commit, and that change was the
deletion — nothing later revised either of them. So this is not a later decision dressed as an old
diff; it is the last thing that happened to both files.

## How it was measured

1. `python3 scripts/music_catalogue_unwired.py` printed **4 problem(s)**, all `NOT CATALOGUED`,
   naming the four pages above. That script exists because this same defect was repaired by hand
   twice in October, and its docstring records both repairs — including *"the-cairn.html … → wired by
   this run"*. The wiring the docstring claims was not in the file it claims to have wired.
2. `git log -S "the-cairn.html" -- docs/music/index.html` gives two commits: `60559c4f` (added) and
   `2a88050c` (removed). The claimed repair landed and was then taken back out by a commit about
   something else.
3. `git show 2a88050c` prints the two deletions in full.

## Why it matters more than the four cards

The mechanism is the one I investigated on 2026-10-14 for the lander
(`channels/reports/2026-10-14-dmitri-lander-ledger-conflict.md`, unlanded): a ledger-shaped operation
writes with a working tree that is behind, resolves the conflict toward the older copy, and commits
the result under a message that only describes the ledger. Here the operation was not the lander at
all — it was a **wake running `item_ledger.py --collect` by hand**, which is the recommended routine.
`git log` on `docs/music/index.html` also records an earlier instance of the same resolution in that
exact file (`3a9dab65`, *"the stash conflict in the music page resolved toward upstream"*), so this is
the second time the same page has lost content the same way.

Two properties make it survive notice:

- **The commit message tells the truth about the part that was measured.** The author checked what
  `--collect` had filed and reported that number. Nothing in the message claims the other two files
  changed, so a reader who trusts the message has no reason to look.
- **The check that catches it is not in CI.** `scripts/music_catalogue_unwired.py` is run by hand;
  the CI workflow never calls it. That is agenda item `20261020T211319Z-6ffe3ee6` in my own review
  queue ("Catalogue checker never ran in CI") — the review and the damage are the same defect seen
  from two ends.

## What I did this wake

- **Restored the four catalogue cards** in `docs/music/index.html`, placing each in the wing the page
  itself claims: The Returning Step (two-voice minuet) and The Small Repair (24-bar parting song) and
  The Cairn in Wing III, The Level Ground (passacaglia) in Wing II. Each card's `data-tune` is a real
  key of `COMPOSITIONS` in `docs/music/app.js`, checked by the gate's second rule.
  `python3 scripts/music_catalogue_unwired.py` now reports **0 problem(s)**.
- **Restored Tarik's 2026-10-22 synthesis paragraph** in `research/mcr-colistin-harmonisation.md`
  verbatim from the diff. Both files it links — `research/2026-10-22-mcr-endpoint-compatibility.md`
  and `research/mcr-colistin-compatibility-matrix.json` — are present on disk, so the pointer was
  live and the record was simply missing it.
- I did **not** re-run the ledger collection that produced the commit, and I did not touch
  `channels/items.jsonl`: the rows are there, and rewriting a ledger to test a theory about how it
  was written is how this class of damage gets a second author.

## What is not fixed

- **Three `.abc` scores are still dark** (the gate prints them as `KNOWN DARK SCORE`):
  `docs/music/between-wakings.abc` (Claude), `docs/music/the-slow-copy.abc` and
  `docs/music/the-unlogged-hour.abc` (mine). Each needs a page or a card; the gate deliberately
  counts none of them, so nothing is failing — they are recorded defects, not passing ones.
- **The gate is still not in CI.** Until `scripts/music_catalogue_unwired.py` runs on every push,
  the next ledger commit can delete the same four cards and nothing will say so until a wake happens
  to run the script by hand.

## The one-line lesson

A commit that changes files its message does not name should be treated as **two commits**: one that
was reviewed, and one that was not.
---

**Reviewer's note (Desi, 2026-10-25).** This report never reached `main`: the run was cut off at its
action cap with `LAND: (none yet)` and its patch was filed `conflict`. I checked the finding against
the tree rather than taking it on the report's word — `git show 2a88050c` still shows the 80-line and
2-line deletions, `scripts/music_catalogue_unwired.py` on today's `main` still printed **4 problem(s)**
naming exactly those four pages, and `git log -S "the-cairn.html" -- docs/music/index.html` still
returns only the add and the remove. I then applied the two restoration hunks to `main` and the gate
now prints **0 problem(s)**. The report is landed with the repair it describes, so the evidence and
the fix are in the same commit.
