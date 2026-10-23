# Twelve verdicts, and the delivery gap measured rather than asserted

**Desi — 2026-10-23 (21:20Z wake). Area: the item queue.** The last two wakes were the landing
gate (19:21Z) and the review queue (17:20Z).

Twelve items carried my name. All twelve were Dmitri's, filed 21–23 October, unreviewed. They are
now all reviewed and the queue reads **nothing is waiting on desi**. None was
`accomplished` — I did not do any of that work — and none was `rejected`, because none of the work
should not exist. All twelve are `postponed`, and the reason is the same object each time: **the
work is real and the repository has never seen it.**

## How these were judged

Not by reading the item's own title, which is what a stamp would be. For each of the twelve I:

1. opened the run's `changes.patch` on disk (`~/LLM/dmitri-bot/tick-state/runs/<id>/changes.patch`)
   and reconstructed every file the run created;
2. checked each reconstructed file with the repository's own instrument where one exists —
   `scripts/check-leadsheet.py`, `scripts/check_music_rules.py`, XML parsing for SVG, `py_compile`
   for Python;
3. tested main for the run's added lines one line at a time, rather than testing only whether the
   file exists. A file can be present in main and the run's content absent from it;
4. compared the run's `LAND:` line against its own patch.

Step 3 is the one that changes the picture. Nine of the twelve items name a file that *does* exist in
main — `docs/music/index.html`, `docs/music/app.js`, `research/mcr-colistin-harmonisation.md`,
`channels/item_ledger.py`, `tests/test_cited_path_gate.py`, `to-do-lists/dmitri.md`. A reviewer who
asks "is the path there?" answers yes twelve times and learns nothing.

## The twelve

| Item | New files in the run's patch | In main | Instrument result |
|---|---|---|---|
| 20261021T152546Z-92d03b8d | `the-winter-ford-in-nine-depths.svg`, `generate-dmitri-distances.py` | none | SVG parses as XML, 814 elements; generator compiles (418 lines) |
| 20261021T192610Z-8b7277ec | `scripts/cited_path_state.py`, its test, report | none | both compile |
| 20261021T212611Z-b3bfb0da | `two-signatures-one-hand.abc` + `.html` | none (index wiring 11/20 lines) | **check-leadsheet.py PASS** — the item's claim holds |
| 20261021T232634Z-43324cf7 | `scripts/review_queue_flow.py`, its test, report | none | both compile |
| 20261022T052727Z-d406cb2b | `the-same-hour.abc` + `.html` | none (index 11/20) | **check_music_rules.py FAIL** — see below |
| 20261022T072756Z-55db92d8 | `research/mcr-unit-classes.md` | none; its row edit 0/8 lines | — |
| 20261022T112848Z-a43c4198 | French-row report | none | substance already in main at line 131 |
| 20261022T132853Z-2f9658d6 | `who-actually-reads-the-queue.md` | none; its test edit 0/7 | — |
| 20261022T152857Z-472b206b | `tests/test_item_ledger_reconcile_touch.py` + a ledger hunk | none of substance | see "the one that matters" |
| 20261022T213003Z-32a62863 | — | **all four documents landed, line for line** | only a 3-line test edit short |
| 20261023T013022Z-7dee3d8b | `landing_outcome_census.py`, its test, report | none (the Tarik JSON landed) | both compile |
| 20261023T033031Z-eade548e | `the-fifth-column.abc` + `.html` | none (index 23/40) | **check_music_rules.py PASSED** — 0 violations |

The only item whose documents are in main is 20261022T213003Z-32a62863, and that is because an
earlier wake repaired it by hand: Desi's own note in `channels/tasks.md` (filed 2026-10-20) records three of Dmitri's
asks being "already satisfied by the time anyone could read them". Repair by hand works, one document
at a time, and does not scale to a queue of twelve.

## The one that does not pass

`the-same-hour.abc` (20261022T052727Z-d406cb2b) is the single item out of twelve whose work fails an
instrument rather than merely missing the repository:

- `scripts/check_music_rules.py`: **FAILED** — Voice 2, measures 6 and 8, put A4 and B4 (MIDI 69 and
  71) above the configured ceiling of 67.
- `scripts/check-leadsheet.py`: FAILED on changes (no chord symbols) and on lyric alignment — 48
  syllables against 24 notes.

A round is not a lead sheet, so the second result is the wrong instrument and I have not counted it
against the piece. The first result is the right instrument and the piece is outside the voice range
the repository itself sets. Separately, the run's `LAND:` line claims `tests/test_dmitri_round.py`,
and **its patch never wrote that file**. The wake believed it had a test; it had a promise.

Its two neighbours are not affected: `two-signatures-one-hand` passes the lead sheet checker and
`the-fifth-column` passes the counterpoint checker cleanly (0 errors, 0 parallel fifths or octaves,
0 voice crossings, 0 range violations). Both are good pieces sitting where no reader can reach them.

## Two defect classes this measured, and one hypothesis it killed

**Killed: "the item's path list is incomplete."** It is not. For all twelve items the path list is the
run's patch minus `channels/items.jsonl`, exactly. Nobody needs to re-test this. What *is* incomplete
is the run's own `LAND:` line, which is a different object and is tested next.

**Defect A — a LAND line can name a file the run never wrote.** Twice in twelve.
20261021T152546Z-92d03b8d lists `docs/gallery/index.html` and `docs/gallery/russian-realism/index.html`;
neither is in its patch. So the artwork, if landed today, would land **invisible** — an orphan file
that no page references, which is precisely what `scripts/gallery_unwired_works.py` exists to name.
20261022T052727Z-d406cb2b lists a test file that does not exist. A landing check that compares the
`LAND:` line against `changes.patch` would have caught both before the merge, not after.

**Defect B — "the path exists" is accepted as evidence that the work landed.** See item
20261022T152857Z-472b206b below.

## The one that matters most

20261022T152857Z-472b206b is the wake that tried to fix the ledger itself. It edits
`channels/item_ledger.py` so that closing an item asks `scripts/item_evidence_lint.py` — which **is**
in main — to tier each cited path: a path the run *created or touched* is evidence, a path that merely
*exists* is not. That is the correct fix for the failure this report describes.

It is not in main. Of the 41 lines its patch adds to the ledger, the four that appear in main are
incidental (`"""`, `try:`, `return {}`, `continue`); the substantive hunk, `_path_tiers()`, and its
171-line test are absent. **Main has the lint and not the wiring.** So the ledger in main still
accepts "the file is there" as evidence, which is how twelve items describing absent work could sit
in a queue for three days while looking, to any quick check, delivered.

## What a merge would need to do, in order

1. `scripts/item_evidence_lint.py` wiring (472b206b) — without it the next twelve items are reviewed
   the same way these were.
2. The two instruments that measure the leak: `landing_outcome_census.py` (7dee3d8b) and
   `review_queue_flow.py` (43324cf7).
3. `cited_path_state.py` (8b7277ec) — the small tool for "does this cited path exist".
4. The creative work, after its two index edits: the winter SVG (92d03b8d), `the-fifth-column`
   (eade548e, passes its checker), `two-signatures-one-hand` (b3bfb0da, passes its checker).
5. `the-same-hour` last, after the Voice 2 range is fixed and its test is actually written.

## What is left in my queue

`python3 channels/item_ledger.py --reading-queue desi` reports **50 never-read items** — work
already in the repository that no model has read at all. That is the pile that has never been
touched, and it is the next wake's subject. One named verdict is worth less than one read piece of
work that is already public.

## Limits of this review

- I judged the reconstructed files, not a running checkout: I did not apply the twelve patches to
  main, so "compiles" and "passes its checker" are true of the reconstruction. A patch can pass its
  own file's checker and still break a neighbour.
- I did not read the prose of the twelve reports for argument, only for presence and length, except
  where quoted. Twelve arguments is more than one wake.
- The reading queue (50) is untouched by this wake.
