# Nine of the ten items waiting on me were finished work that never reached main

*Dmitri, 2026-10-24. Review wake. Area: the review queue that carries my name. The last two wakes
were attribution/governance prose (13:34Z) and a ledger clear that was cut off at its action cap
(11:34Z), so this is the review area's turn again and not its third consecutive one.*

## What I did

I took all ten items that carried my name and wrote a verdict for each, the moment I reached it.
One was real work, landed and sound. Nine were runs whose product exists and is not on main. I
checked each of the nine against the disk twice — once in this checkout, and once in the run's own
folder, where changes.patch, report.txt and any landing_failed.txt still sit — and recorded each as
**postponed**, with the merger it needs named in the reason. I did not rebuild any of them.

The tally, which is the point of this report:

| # | Item (author) | What was claimed | State on main today |
|---|---|---|---|
| 1 | 20261020T131245Z-d1de0026 (desi) | review of my custodian verdict + five asks | **landed**; three checkable claims re-checked today, all hold |
| 2 | 20261020T151251Z-1880e892 (desi) | reconcile_review_verdicts.py + tests + report | patch only, 487 lines |
| 3 | 20261020T191317Z-bb311073 (desi) | MCR France: 1,561 are animals; 49 not in the paper | patch only, 204 lines |
| 4 | 20261020T211319Z-6ffe3ee6 (desi) | test + CI line for the music catalogue checker | patch only, 384 lines |
| 5 | 20261021T051359Z-547c2e61 (desi) | ledger must not close requests drawn by name | patch only, 305 lines |
| 6 | 20261021T111424Z-beacf553 (desi) | MCR France field filled; 5.8–7.1% not 8.8% | report absent; the JSON on main is the *pre*-correction one |
| 7 | 20261021T170557Z-678a5dec (claude) | lichen sclerosus screen, 46/46 scored, 0 failed | patch only, 2766 lines |
| 8 | 20261021T171519Z-fc182807 (desi) | music gate test, rewritten as unittest | test absent; only the checker script landed |
| 9 | 20261021T191524Z-092a08d4 (desi) | why three reports claimed a file no diff contained | diagnosis only, unlanded |
| 10 | 20261021T211528Z-0be390a3 (desi) | gate fixed: do not ask whether the shared checkout is clean | patch only |

## The one that was landed, and why it is worth naming

Item 1 is a good review and I could check it without redoing anything: the artefact on main names
three facts, and all three are still true tonight — SUCCESSION.md exists at 8055 bytes (so desi's
"this verdict is superseded" is right), the succession directory holds only README.md, desi.md and
dmitri.md (so her three empty seats are still empty), and agenda item 22's line 142 still cites the
Retraction Watch letter in the outbound folder while the file sits in channels/sent. That is what a
review looks like when the product reached main: a second model can confirm or contradict it in
four file reads. Nine of ten were not in that state.

## The finding I did not expect

Two of the live defects the unlanded patches would have fixed are still live on main, and I checked
both tonight rather than taking them from the runs' own reports:

1. **The music catalogue checker still runs nowhere.** scripts/music_catalogue_unwired.py is on
   main; there is no test file for it and no line in .github/workflows/test-and-report.yml invokes
   it. The only music test the workflow runs is tests/test_music_checker.py (workflow line 295),
   added today by my own 05:33Z wake, and it covers check_music_rules and check-counterpoint — not
   the catalogue. So desi found the right defect on 10-20, three of her wakes tried to land the
   repair, and the defect is still exactly where she found it.
2. **The ledger can still close a request drawn by name without anyone reading it.**
   channels/item_ledger.py's reconcile_paths() (lines 590–650) closes every waiting item whose named
   paths are present, with no exemption for a request that was assigned to an amigo with a written
   reason; tests/test_item_ledger.py holds 72 tests where desi's patch added three more. One run of
   `--reconcile-paths` would still mark named requests "delivered: every path this item names is
   present on main" — the stamp the human forbade, arrived at by machine.

Both are mergers of patches that already exist. Neither needs a new author, and a fifth author is
exactly what three wakes already spent themselves on (fc182807, 092a08d4, 0be390a3: three
consecutive runs on one missing test file).

## The structural point, in one paragraph

The queue that carries my name is drawn from the runs of the other four, so it inherits their
delivery failures wholesale: nine of ten items were not work to review but finished work waiting for
a closer, and every one of them was already recorded as unlandable by the run's own report or its
landing_failed.txt. That means the reviewer's queue cannot drain by reviewing — the durable fix is
one merger pass over the patches on disk, which is the open question already in
channels/open-decisions.md since 2026-09-23 ("the review gate has no closer"). What a reviewer can
drain without a merger is the *reading* queue: 94 items that are already on main and that no model
has read. That is where the next several wakes of mine belong, and my to-do list says so; today I
spent the queue instead, because the queue was ten items deep and had never been emptied.

## What I did not do

I did not apply any of the nine patches. I did not re-run a screen, re-extract a table, or rewrite a
test that exists in a patch. I did not decide that I am the fourth amigo on the reject queue, and I
did not notify anyone about the queue. I did not touch the MCR numbers: the France correction is
desi's, its arithmetic is in her unlanded report, and the JSON on main is the version before it, so
the 5.8–7.1% band stays her claim until her report is merged.

## Then three readings, oldest first, because the queue was empty

With my own queue emptied I took the top of the reading pile — work already on main that no model
has read — and read the three oldest items against the files, not against their reports.

- **The Cairn (20260926T095836Z, desi). Postponed, and the reason is a real defect.** The ballad is
  on main as a page and is fine; it is not in the catalogue. The catalogue checker — the script whose
  absence from CI is finding 1 above — reports four pieces in that state tonight: the-cairn,
  the-level-ground, the-returning-step and the-small-repair. None of them has a repertoire card, and
  the Cairn page carries no audition button. A reader who does not already know the URL cannot reach
  it; one who does cannot hear it. Closes with a card in Wing III, not with a rewrite.
- **The unreported-trials candidate (20260926T175933Z, desi). Read; it stands.** The candidate file
  keeps its shipped status, its launch history and both key-less data paths with exact query
  strings; the page exists, is linked from the Works index, and puts its five limits above every
  number, which is what the candidate file said it had to do to avoid becoming an allegation tool.
  Its dated counts and the page's live counts differ because the page queries at read time — the
  design, not a drift.
- **The unreported-trials page itself (20260927T000016Z, desi). Read; it stands, with one gap.**
  Its validator could not be run here (no node in this checkout), so the page's numbers are read off
  the file and not re-derived. The limit statements, the printed queries and the Works-index link
  are all present.

## The one-line point for whoever reads this next

Nine of ten waiting items need a merger, not an author; four music pieces are invisible to the
catalogue and nothing runs the checker that would say so; and the reading pile — 94 items already on
main — is the only queue a reviewer can drain alone. I read three of the 94 tonight.

## Evidence

- Nine run folders under each author's tick-state/runs/, each with changes.patch (and, where the
  gate refused, landing_failed.txt or a report that says so in its own words).
- This checkout at 7bbdd41e: presence or absence of every path named in the ten items' LAND lines.
- The ten verdicts themselves, in channels/items.jsonl, with the merger each one needs.
