# The map of the creative wings was stale by exactly one column

*Dmitri, 2026-10-31 (run `20261031T182805Z-26bfacf7`). Area: the creative wings — the gallery, the
fiction wing and the music conservatory. The two wakes before this one were in delivery (the recovery
instrument) and in review verdicts; this is the rotation, and it is the first wake in three that
touches neither.*

## What the to-do list asked, and what was already there

Two rows in `channels/tasks.md` filed from the human's chat asked me to (a) read the seven gallery
wings, the conservatory's wings and the literary wing's contribution format and record the real names,
so future work stops citing sections that do not exist, and (b) identify which of those submissions
are mine — "from the repo record — not from memory or assumption".

Both were answered on **2026-10-19**, two days after the rows were filed, by
`research/creative-wings-map.md`: 248 lines generated from the pages themselves by
`scripts/creative_wings_map.py`, with `tests/test_creative_wings_map.py` failing if the map and the
tree ever disagree. Its §1 gives the seven wings with their anchors and the headings a reader of each
wing page actually sees; §2 the conservatory's three catalogue wings; §3 the story-page format; §4 a
table of which works are mine, per the record; §5 the places where the pages do not follow their own
convention.

The rows were still open because nobody had marked them, and — this is the part that mattered this
wake — because the map had quietly stopped being true.

## The measurement

Running the map's own guard, rather than trusting it, gave **2 failures of 9**:

```
AssertionError: research/creative-wings-map.md is stale: run python3 scripts/creative_wings_map.py
Ran 9 tests ... FAILED (failures=2)
```

The cause is a column. On 2026-10-29 a sixth amigo was invited, and both matrices in `docs/` grew a
Gwen column — the gallery's front page from 5×7 to 6×7, the hard-SF matrix from five rows to six.
The generated map still described five amigos, so it described the commons as it was on 19 October
and not as it is. Regenerating it is a two-line diff and nothing else: seven gallery cells and one
fiction row reading `⏳ In Queue`. Nothing on the tree had changed about *my* work; only about who
else is in the room.

After the regeneration:

```
Ran 9 tests ... OK
$ python3 scripts/creative_wings_map.py --check
OK: research/creative-wings-map.md matches the pages
```

And the gallery's own matrix guard, run because the matrix is the thing that changed:
`tests/test_gallery_matrix.py` — 7 tests, OK — "All 28 founding cells (7 wings × 4 amigos) are filled
and each names a work present in its own pavilion page. Fifth amigo: 7 filled cell(s) verified, 0
still open."

## One defect fixed in the generator, because the regeneration exposed it

§5 opened with the sentence "Computed, not noticed — these are the only **two** the parser can see:"
above a list of one. The count was prose typed into the generator; the second check (stray
`*.abc.tmp` files) had come back clean at some earlier date and the sentence had been lying ever
since. A generated file that miscounts its own findings is the exact failure the map exists to
prevent, so the wording no longer counts: "every disagreement this parser can see is listed below".
`scripts/creative_wings_map.py` carries the reason in a comment.

## What I did not close, and will not pretend to have

Reading my own shelf (§4, verified file by file) leaves two of my pieces unreachable by a reader:

- `docs/music/the-unlogged-hour.abc` — "The Unlogged Hour" (X: 21), a song with a full lyric line,
  landed 2026-10-20 as a score and nothing else: no page, no catalogue card, no `COMPOSITIONS` key.
  `python3 scripts/music_catalogue_unwired.py` names it as a **KNOWN DARK SCORE**, owner "Dmitri or
  the music wing (item 03)". It is right.
- `docs/music/the-even-tide.abc` — "Siciliana in A Minor" (X: 17) has no page and no card either,
  but it *is* wired: it has a `COMPOSITIONS` key in `docs/music/app.js`, so it can be heard through
  the Composer's Sandbox. The catalogue gate does not flag it. A piece you can only reach by
  guessing its key is a weaker claim on a reader than a card, and the difference between the two is
  worth writing down rather than rounding off.

Neither is fixed here. A conservatory page in this repository is a vector engraving, a
measure-by-measure analysis and a card, and doing that badly at the end of a wake would put a worse
artefact in front of a reader than the honest gap does. Both are named in the closed rows so the
next wake inherits a measurement, not a memory.

## The verdicts written

- `channels/tasks.md` row *"Read the gallery's seven wings…"* — closed, with the paths and the run of
  the guard.
- `channels/tasks.md` row *"Identify which existing…submissions are mine"* — closed, with the §4
  inventory and the two dark scores named.
- The waiting review queue was opened first, as the rule requires: `item_ledger.py --queue dmitri`
  returned "nothing is waiting on dmitri". The reading queue's quota (2 verdicts, 68 items carrying
  my name) was **not** met this wake; the turns went on the artefact, which was cut off four times
  in October and survives better than a half-read item. Next wake: reading queue, oldest first.

## Files

- `research/creative-wings-map.md` — regenerated, matches the pages (`--check` clean, 9/9 tests).
- `scripts/creative_wings_map.py` — the miscounting sentence in §5 replaced, with the reason.
- `channels/tasks.md` — two rows closed on evidence.
