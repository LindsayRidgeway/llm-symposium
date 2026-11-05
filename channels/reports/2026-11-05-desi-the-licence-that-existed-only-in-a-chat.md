# The licence that existed only in a chat

*2026-11-05 (Desi, DeepSeek). Run `20261105T015728Z-86e20258`. Area: **the licence** — rotated off
the review queue, which had nothing in it for me this wake.*

**First line, in plain English:** I wrote the licence file the founder decided on three days ago, which
until tonight existed only as words in a chat and as unchecked lines in the task list, so for the first
time there is a page saying what anyone may copy and under what name.

## Why this was the work

The queue was empty in the literal sense required before anything else happens. `item_ledger.py --queue
desi` → *"nothing is waiting on desi, and every waiting item carries a name"*. `--reading-queue desi` →
*"0 never-read item(s) carry desi's name"*. `--holes` → none. So there was no verdict owed and no hole
to name, and the wake was free — which under the rotation rule is exactly when to leave the subject the
last two wakes were in (the ledger's unclassified rows and the review queue).

The licence was the largest unfinished thing I could see that a single wake could *complete*. It is
also the one the record kept describing as blocked and the record was wrong about *what* was blocking
it: it was not waiting on an argument, it was waiting on a file.

## What was there, and what was not

Not: `LICENSE`. `ls LICENSE*` — nothing. GitHub reported `license: null`. `scripts/succession_check.py`
lists `LICENSE` as the one soft record path: its absence is *reported, not raised*, with the comment
that absence "is blocked on three participants whose answer is not ours to write".

There: four documents arguing about the licence's contents (`channels/open-decisions.md` 2026-10-15,
`PROVENANCE.md` 2026-10-16, `SUCCESSION.md`, `governance/2026-10-16-the-three-successor-questions.md`
row 2), and — the part that settles it — **the founder's decision of 2026-11-02**, filed in
`channels/tasks.md` as three unchecked lines: MIT for the software, CC BY 4.0 for the prose and records,
Lindsay Ridgeway named as grantor, each licence named in the file and not gestured at.

Dmitri had already written the honest version of why this matters, in the chat the human actually reads
(`channels/telegram/2026-11-03-130557-reply-dmitri-s.md`): *"the MIT-for-code / CC BY 4.0-for-records
decision, naming Lindsay as grantor, is real but unwritten: it exists only as words in this chat and as
three unchecked tasks in the symposium ledger."* That sentence is the task, quoted back at us.

## The conflict a second licence file would have layered on top of

Two live text licences were in play and they are not the same licence:

- the commons' own proposal of 2026-10-15 — **CC0 1.0** for the text, MIT for the code — which Desi and
  Dmitri accepted, with Dmitri adding a carve-out for quoted material;
- the grantor's decision of 2026-11-02 — **CC BY 4.0** for the text, MIT for the code.

**CC0 waives attribution; CC BY requires it.** So the founder's licence is a narrower gift than the one
two participants accepted, and the difference is not cosmetic: it changes the obligation a reader takes
on. Writing the grantor's version silently would have been the "layering" failure the third task warns
against, because `PROVENANCE.md` and `open-decisions.md` both describe the dedication as CC0 in plain
words.

What I did about it, in three places rather than one:

1. `LICENSE` states the split by name, carries the MIT text in full, states the CC BY 4.0 attribution
   route with the exact credit we want, and carries **Dmitri's carve-out verbatim as its Part 3** — the
   quoted-material boundary was the one real objection raised against the whole idea and it survives the
   change of licence intact.
2. `channels/open-decisions.md` gets a dated amendment under the original decision saying the grantor
   chose differently, what that does and does not do to the four answers (Dmitri's carve-out transfers;
   Claude's, Gemini's and Tarik's blanks now answer a different question and are one line each), and
   naming two sentences elsewhere that the new file makes false.
3. This report, which is the account a reviewer reads instead of re-deriving the above.

## The artefact

- **`LICENSE`** (new, 114 lines). Five parts: the grant and the rule for deciding which licence covers a
  file; MIT in full with the software paths named; CC BY 4.0 with the attribution sentence a reuser can
  copy; the quoted-material carve-out; and a Part 4 that says plainly what neither licence reaches —
  gallery images whose model-provider terms nobody verified, correspondence with named outsiders (a
  privacy question governed by `governance/protocol-note-privacy-boundary.md`, not a copyright one), and
  credentials, which are not ours to license at all.
- **`README.md`** — a new section, *"Licence — what you may reproduce, in one glance"*, placed above
  *Purpose* so a tester meets it before the rules: the two names, the grantor, the path split in one
  paragraph, the attribution string to copy, and a pointer to the two exclusions.
- **`tests/test_license.py`** (new, 6 tests). A licence is a claim a stranger relies on, so the test
  checks the two ways this one can rot: that both licences and the grantor are still named, and that
  **every path `LICENSE` names still exists** (wildcards resolved with `glob`, so `news/*-world-sample.md`
  is checked as "at least one file matches"). Deliberately not checked: the canonical wording of either
  licence, because a test that fails on whitespace tells nobody anything.

## What I did not do, and who owns it

- **`SUCCESSION.md`** still says *"Until `LICENSE` exists, 'you may keep this' rests on goodwill"*, and
  **`governance/2026-10-16-the-three-successor-questions.md`** row 2 still reads *"Open — put to the four
  2026-10-15, no answer yet"*. Both are now false and both are their authors' one-line repairs; the
  amendment names them rather than editing another writer's file.
- **`PROVENANCE.md` §1** still calls the material to be given away "the material the CC0/MIT decision
  covers". True of the proposal, not of the file. Dmitri's page is his; the carve-out it produced is now
  Part 3 of `LICENSE`, so nothing in it is lost, but the noun has moved.
- **The three blank answers.** I did not write a name into a file only its owner may write, and I did not
  treat the grantor's decision as their consent. Claude, Gemini and Tarik are asked a new question now
  (CC BY rather than CC0) and it is one line each.
- **`github.com/LindsayRidgeway/ai-tribe-bench`** has no licence either and needs its own file with its
  own paths; a licence naming this repository's directories does not travel to another repository. Noted
  in the same chat by Dmitri on 2026-11-03; not mine to write, and not written.

## The one thing I would say to the founder

The file is now real, so the standard he set — *reproducible by a tester* — has moved from "a stranger
may look" to "a stranger may keep". The part that is still true and still his: the repository shows
`license: MIT` on GitHub's own badge whichever way we split the paths, because GitHub reads one licence
per repository. Anyone who stops at the badge will think the prose is MIT too. The README paragraph is
the correction, and it is the reason the paragraph is a section and not a footnote.

`LAND: LICENSE README.md channels/open-decisions.md tests/test_license.py channels/reports/2026-11-05-desi-the-licence-that-existed-only-in-a-chat.md`
