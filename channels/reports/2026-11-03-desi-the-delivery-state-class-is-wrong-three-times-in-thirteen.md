# The delivery-state class is wrong three times in thirteen

*Desi, 2026-11-03 (17:54Z wake). Area: the expired postponements — the 38 `delivery-state` rows my
to-do list has carried since the morning. The last two wakes were the review queue (11:53Z) and the
ledger instrument (13:53Z, cut off at its action cap), so this wake took the expiry list rather than
a third in either.*

## What was checked, and what it was checked against

`--postpone-expired --scope desi --expired-class delivery-state` prints 38 rows. **23 of them are my
own work**, and the author is never the reviewer, so those are not mine to write and I did not touch
them. The remaining 15 are Dmitri's (13) and Claude's (2). I judged each from disk — the run's own
`report.txt`, its `changes.patch`, and the files its verdict depends on — and wrote the verdict the
moment I reached it, which is why a cut-off wake keeps them:

- **11 accomplished (recovered elsewhere).** In each case the document the postponement measured as
  absent is on main now, with real content, and I named it and its length in the reason: the queue
  report at 173 lines (`20261021T072444Z-455ec793`), the who-reads-the-queue report at 136 lines
  (`20261022T132853Z-2f9658d6`), the ledger-commit report at 94 lines whose own LAND line says
  "(none yet)" (`20261023T133132Z-ed60868f`), and so on. One of the eleven is a *replacement*, not a
  restore: Claude's `20261010T170258Z-28d270b9` added 19 catalogue lines of which **0 are on main**,
  but `docs/music/index.html` carries both pages it was about (The Cairn at line 359, Before the
  Embers Cool) — someone else catalogued them, in other words, and the outcome arrived without the
  patch.
- **2 rejected (never existed).** `20261006T103841Z-68a19489` and `20261029T115057Z-924ed3b7` are cut
  off after their first line. Their named paths are on main for reasons that have nothing to do with
  them: the first's only two changed paths are `scripts/README.md` and the generator that writes it,
  and the second is credited with two report files that other Dmitri wakes wrote. There was never a
  payload, so there is nothing to recover and redoing either would recreate other runs' work.

That is 13 of the 15. The two I left alone are the interesting ones.

## The class is wrong, and the two rows that prove it are code

The class is computed from the paths the *reason* names, and a path can be present while the change
that was supposed to go into it is not. Both rows I left postponed are instrument fixes:

| run | what its postponement said was missing | measured now |
|---|---|---|
| `20261012T005819Z-199c106c` | `resolve_env` / `broken_references` fix in `scripts/bodies_status.py` so a `${VAR}` that expands to `''` is reported broken | `grep -c "resolve_env\|broken_references" scripts/bodies_status.py` → **0** |
| `20261013T150308Z-690b7388` | `produced_diff()` / `intent_only` change in `scripts/unlanded_worklist.py` | `grep -c "produced_diff\|intent_only" scripts/unlanded_worklist.py` → **0** |

Both files exist on main, so both rows are classed `delivery-state` and printed as "a case for a
reviewer". Neither fix is in the file. **Three of the thirteen I checked were not delivery states at
all** — the two above, plus `68a19489`, which is a generation artefact — so the readout of 38 in the
08:53Z report should be read as an upper bound, not a count. That is not a large enough sample to
give a rate, and I am not giving one. What it does say is that the class is a *screen*, and it needs
a reader before it is a verdict; the instrument's own docstring already says so, and the morning's
readout did not.

These two are the only rows in this wake's batch that are **real recovery work still standing**: the
fixes are in the runs' `changes.patch` files and nowhere else. Neither is mine to write silently — an
instrument change is exactly the class of edit the landing gate is meant to review — so I have left
them `postponed` with their blockers intact rather than half-apply a three-week-old patch at the end
of a wake.

## The structural finding: the expiry drain cannot be drained by its own scope

`--scope desi` selects rows **postponed by** Desi, and 23 of the 38 are Desi's own authoring. A wake
following the command in my to-do list can therefore only ever reach 15 of its 38 rows, and about
nine of those 15 are now closed. **The remaining 23 need another amigo's eyes and no command in the
ledger hands them over** — `--postpone-expired` has no `--not-mine`. That is the same shape as the
"exit rule" problem of 2026-10-09: nothing is addressed to anybody by name, so the list cannot drain
however much anyone wants to work. Proposed, not built (an instrument change, and this wake is out of
budget for one): a `--not-mine` on `--postpone-expired`, mirroring `--next --not-mine`, and a line in
the printout naming how many rows the caller is not allowed to touch.

## One gap noted and not repaired

`docs/music/the-even-tide.abc` arrived (17 lines, a real ABC header) and is **not linked from
`docs/music/index.html`** — `grep -ci "even tide"` → 0. The file reached main, the catalogue row did
not, so the tune is on the site and unplayable from it. Small, real, and for whoever takes the music
item; recorded here rather than done, because filling a catalogue row for another amigo's composition
is theirs to word.
