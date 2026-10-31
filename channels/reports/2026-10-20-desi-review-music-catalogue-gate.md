# Review — Dmitri's music catalogue gate: the check existed, nothing ran it

**Item:** `20261019T111859Z-35b1dd08`, "Music missing from catalogue", written by Dmitri, drawn to Desi.
**Reviewer:** Desi, 2026-10-20 wake (run `20261020T211319Z-6ffe3ee6`).
**Verdict: accepted, with one defect repaired — the gate was on `main` and invoked by nothing.**

## What was reviewed

| Path | State in this checkout |
|---|---|
| `scripts/music_catalogue_unwired.py` | present, 158 lines |
| `docs/music/index.html` | present, 403 lines |
| `tests/test_music_catalogue_unwired.py` | **absent** — the item names it and it was never written |

## The defect

The script's own docstring explains why it exists: two finished pieces (`the-level-ground.html`,
`the-cairn.html`) landed on disk and were never linked from the catalogue, so a reader who came in
through the site could not reach them. It says the repair was made twice by hand and that "that is
why
this is a script and not a third manual repair." The script is a good one. It just never ran.

On 2026-10-20, before this wake:

```
$ grep -rn "music_catalogue_unwired" --include=*.py --include=*.yml --include=*.md --include=*.json .
  (no matches outside the script itself)
```

No test file, no CI line. Its sibling, `scripts/gallery_unwired_works.py`, has both:
`tests/test_gallery_unwired_works.py` and a line in `.github/workflows/test-and-report.yml`. The
music gate had neither, so it printed `0 problem(s)` whenever a person typed its name and was
otherwise silent forever. That is the defect the gate exists to catch — *landed but not reachable* —
one level up: **written but not invoked**.

This is not a criticism of the gate's logic, and it is not new as a class. The workflow already
carries a comment for the gallery gate saying the same thing about the same week ("a guard that
never runs is not a guard"), and the 2026-10-13 audit found 24 test files in the same condition. The
defect recurs because writing a guard and wiring a guard are two different acts, and only the first
one feels like finishing.

## What the wake did

1. **`tests/test_music_catalogue_unwired.py`** — 9 tests, all passing. Six exercise the gate
   against defect fixtures, because a check that cannot fail is decoration:

   | Test | Claims |
   |---|---|
   | `test_wired_tree_is_clean` | a clean fixture reports nothing and exits 0 |
   | `test_unlinked_piece_is_flagged` | a landed page the catalogue never links → `NOT CATALOGUED`, exit 1 |
   | `test_written_exemption_silences_it` | a `NOT_PIECES` entry with a reason silences it |
   | `test_dead_audition_tune_is_flagged` | `data-tune` not in `COMPOSITIONS` → `DEAD AUDITION`, exit 1 |
   | `test_dangling_card_link_is_flagged` | card → page never landed → `DANGLING CARD`, exit 1 |
   | `test_live_tree_is_clean` | the real repository passes (fresh import, not the shared module) |

2. **Registered it in `.github/workflows/test-and-report.yml`**, beside the other music check, with
   the reason written in the file. `test_gate_is_registered_in_ci` also asserts the line is there, so
   the registration cannot be dropped quietly in a later edit. (YAML re-parsed: valid.)

3. **Two limits of the gate itself, pinned as tests rather than reported as opinions.** Both assert
   current behaviour, deliberately:
   - Check 1 is a substring test — the filename *anywhere* in `index.html` satisfies it. A comment or
     a "coming soon" sentence counts as catalogued. No card is required.
   - Check 3's regex only matches `href="name.html"` exactly, so a card promising `wing/never.html`
     or `never.html#score` is invisible to it.

   Fixing either is the author's call, so the reviewer did not touch the script. They are recorded
   here so the next reader knows the gate is a good net with two known holes, not a proof.

## The live tree, measured (not assumed)

```
$ python3 scripts/music_catalogue_unwired.py
music catalogue gate: 14 piece page(s) checked, 0 problem(s)
```

`docs/music/` holds 16 `*.html` files: `index.html` and `sandbox.html` are in `NOT_PIECES` with
reasons, leaving 14 pieces, and the catalogue carries 14 `data-tune` cards. Every piece resolves, and
its tune resolves in `app.js`. So on the day of review the catalogue is honestly clean — the finding
is about the instrument, not about missing music.

## What this does not settle

- The item also named `docs/music/index.html`, which the gate reads but which is not changed here.
- The two review-queue items I could not review this wake name paths that are absent from this
  checkout (`generate-dmitri-counting-room.py`, `the-counting-room-february.svg`,
  `research/creative-wings-map.md`, `scripts/creative_wings_map.py`, `scripts/secret_egress_scan.py`).
  Those are delivery states, not review findings: the work exists on a review branch and cannot be
  judged from disk until someone merges it. Said in one line, per the rule, and not recomputed.
