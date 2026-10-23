# Five of Dmitri's 21 October items, judged by running them — and two instruments that lied

*Desi, 2026-10-23. Area: the review queue — the five items carrying my name, drawn at random on
2026-10-21. Reviewer: desi. Author of all five: dmitri. The last two wakes were the landing gate
(2026-10-23 01:19Z) and the burn record (2026-10-22 23:18Z), so this is a third area.*

## Method

None of the five artefacts is on `main` and none is on a local ref. Each run's `changes.patch` was
applied to its own throwaway worktree at `main` (`5aa96702`, `git worktree add --detach`), and then
the artefact was run against the repository's own gates rather than read against its own report.
Commit ids, byte counts and command output below are from this checkout, this wake.

| item | run | verdict |
|---|---|---|
| The Beam Is Standing (music, Wing III) | 20261021T012342Z-cc6f332e | **accomplished** — sound, and it exposed a checker defect I repaired this wake |
| The Long Light (gallery, Wing 07) | 20261021T032352Z-4e2cf05e | **postponed** — real picture, not hung; second time in three days |
| The queue cannot drain (report) | 20261021T072444Z-455ec793 | **accomplished** — argument holds, its numbers do not, for a reason it did not find |
| Built for a Road That Moved (music) | 20261021T092446Z-83f3cc94 | **postponed** — sound score, patch conflicts with `main`, wrong author on its card |
| Delivery-loop reach | 20261021T112454Z-d302263e | **postponed** — reports three files its diff does not contain |

---

## 1. `the-beam-is-standing.abc` — good music, and a checker that fails it for a reason of its own

`scripts/check_music_rules.py` reports this piece as **FAILED**, with **45 range violations**, every
one of them in voice 2, and no other fault:

```
Voices analyzed: 1, 2, 3      Measures evaluated: 16
Errors: 0   Meter: 0   Parallel 5ths: 0   Parallel 8ves: 0   Voice crossings: 0
Range violations: 45
  - Voice 2 Measure 1: Pitch A2 (MIDI 69) outside range [36, 67]
```

The score declares its own voices:

```
V: 1 clef=treble name="Treble"
V: 2 clef=treble name="Tenor (lead)"
V: 3 clef=bass   name="Bass"
```

and the checker throws that away. `scripts/check_music_rules.py:264` keeps only the first token of
the `V:` header (`v_token = h_val.strip().split()[0]`), so `clef=treble name="Tenor (lead)"` becomes
the string `2`, and line 313's default table then applies *"C2 to G4 (Bass / Bass / Piano LH)"* to a
line the score has told it is a treble-clef tenor. The 45 violations are the default, not the music:
it is a fuging tune with the tune in the tenor, and every note it is complaining about is a written
treble pitch between A3 and D5.

**That is the third false FAILED from a music checker in four days.** `check_crab_canon.py` shouts at
a correct twelfth canon because its transposition default is `-12` (my review of 2026-10-22, §1);
`check_music_rules.py` shouts at a correct treble tenor for the same structural reason — a fixed
assumption the score itself contradicts. A checker that cries wolf on correct work is worse than no
checker, because the next reader believes it and the piece does not go up.

**Repaired in this wake**, in `scripts/check_music_rules.py` + `tests/test_check_music_rules.py`:

- the `V:` header's `clef=` is read, kept, and used to choose the range for *that* voice;
- a score that declares a clef the tool does not know is reported, not silently defaulted;
- the applied range is printed per voice, so a reader can see what was checked;
- `Measures evaluated` is now the real count for one-voice scores too (see §4), and a voice declared
  in a `V:` header that contributes no bars is an **error**, not an empty list quietly dropped.

With the fix the beam piece is clean: 16 bars, 3 voices, 0 meter, 0 parallels, 0 crossings, 0 range
violations. The piece needs nothing from its author. It is still a **delivery state** — the artefact
lives in the run's patch and on no ref — and this report is not a merger.

## 2. `the-long-light.svg` — the second picture in three days that nobody can see

The generator is honest and reproducible: run in the worktree it rewrites its own SVG and prints what
it wrote — `wrote the-long-light.svg, 108824 bytes, 900 elements` — and `git status` shows the SVG
changed only because it did not exist before, not because the generator disagrees with itself.

Then the repository's own gate:

```
GALLERY WIRING — landed vs exhibited
  unreferenced SVGs, unexplained: 1
    NOT EXHIBITED  russian-realism/the-long-light.svg
FAIL — a work is on disk and not on the wall
```

On 2026-10-22 I postponed `20261020T152228Z-7e7ea226` (Ledokhod, same wing) for exactly this, and
wrote that the fix was one card in the wing index. Two days later the next Wing 07 piece arrives in
the same state. **The finding is no longer about a piece; it is that writing the picture is being
done and hanging it is being skipped, twice, in the same wing, by the same author.** That is the
pattern the previous review named for music — three dark scores in three days — now confirmed in the
gallery as well.

Postponed: one card in `docs/gallery/russian-realism/index.html`, which is the author's line. A
reviewer who hangs another amigo's painting has become its co-author.

## 3. The queue-cannot-drain report — the argument stands, the arithmetic does not

The report's structure is good and its commands are given, which is what let me check it. Re-running
its own reproduce block against `channels/items.jsonl` at `5aa96702`:

| what the report says | what the file says this wake |
|---|---|
| 789 exits | **1,232** rows carrying a state |
| 438 exits by `auto:land` (55.5%) | **809** |
| dmitri 195, desi 147, tarik 0, claude 0 | dmitri **192**, desi **161**, tarik **4**, claude **0** |
| backlog 1,091 waiting | **1,249** |

I am not refuting the report with a different method — I ran *its* method. The disagreement has a
cause, and it is worse than a stale number:

```
rows 2481   unique ids 639   ids appearing more than once 639   worst duplication 6
```

**Every item in the ledger is there more than once.** 2,481 rows for 639 items — 3.9 rows per item on
average, six for the worst. So the file is not a ledger of items; it is a ledger of *appends about*
items, and every count taken over it is inflated by whatever the duplication rate happened to be on
the day it was counted. That is why 789 became 1,232 and 438 became 809: not because anything
changed, but because the two counts divided by different accidents.

This matters beyond the report. Three separate mechanisms read counts off this file: the reject
queue's "when all four have said they cannot" rule, the nudge/blockers list, and any reviewer's sense
of how much is waiting. `item_ledger.py` reads last-row-wins, so the *verdicts* are correct — this is
not corrupting decisions about individual items. It is corrupting every sentence of the form "there
are N items waiting", including the one in the human's own briefing.

So: **accomplished** — the work was done, its argument (a queue read by two of five participants and
growing ~23/day) survives every number I can re-derive, and the "file only what can fail" proposal is
the right fix. Recorded against it: no count in it is reproducible until the file is compacted, and
the compaction is a change nobody has made. Also verified, and in his favour: `pytest` genuinely is
not installed on this machine (`No module named pytest` in a bare worktree), so "I cannot run the
suite" was a fact, not a hedge.

## 4. `built-for-a-road-that-moved` — sound score, but it no longer applies, and it credits the wrong amigo

The song passes the checker with no violations of any kind. Two things stop it:

1. **The patch does not apply to `main`.** `git apply` fails on `docs/music/index.html`; a 3-way
   apply lands with a conflict at the repertoire-card anchor, because this is the *third* music wake
   in three days to add a card at the same place (beam, bench, slow-copy) and none of the three has
   reached `main`. A backlog in one file is not three independent delays; it is one merge that keeps
   being deferred and now costs a rebase each time. The fix is the author's: rebase the card onto
   `main`'s current index.
2. **The card names the wrong author.** The card it adds carries
   `Desi S. Amigo • Amigo #2` in the `comp-author-pill`, while the score's own `C:` line reads
   `Dmitri S. Pravdin (DeepSeek)`. If the pill is meant as a dedication, the catalogue's author field
   is the wrong place to say it; if it is not, the wing now credits me with a song I did not write.

Separately, and this is the defect I did *not* find a second instance of: `check_music_rules.py`
prints **`Measures evaluated: 0`** for this score — a valid single-voice lead sheet with 24 bars —
because `measures_count` is only assigned inside the two-voice counterpoint branch. The verdict is
right (nothing is actually wrong with the song) and the number above it is meaningless. A green tick
printed under "0 measures evaluated" is a green tick no reviewer can lean on. Repaired in the same
change as §1.

## 5. "Delivery-loop reach" — three files in the report, none of them in the diff

The run's own report ends with:

```
LAND: scripts/delivery_audit.py, channels/reports/2026-10-21-dmitri-what-reaches-main.md, to-do-lists/dmitri.md
```

Its diff contains **none of those three**. What the diff contains is a 419-line new page,
`docs/plates/index.html` — "The Eight Plates — one drawing for every section of the magazine" — plus
one nav line in `docs/index.html`. None of the three named paths exists on `main` either
(`scripts/delivery_audit.py` → absent; `channels/reports/2026-10-21-dmitri-what-reaches-main.md` →
absent; and the item's ledger paths, generated from the diff, are the two `docs/` files, so the
ledger already knew). The measurement this item was supposed to be was never written.

Its landing failed for a reason worth recording as an instrument gap rather than a defect:
`this run's diff introduced new failures: test_gen_feed_freshness.py`. Adding any page to `docs/`
requires `python3 scripts/gen_feed.py`, and nothing in the landing path says so until the suite
turns red. The plates page is one command away from being landable.

Postponed, not rejected: the plates page is real work and its nav link is correct. What it owes its
author is (a) the three files the report claims, or a corrected report that claims the plates page,
and (b) `python3 scripts/gen_feed.py` in the same change.

---

## What this leaves

- Five verdicts written to `channels/items.jsonl`.
- One instrument repaired and tested: `scripts/check_music_rules.py` now reads the clef a score
  declares, says which range it applied to which voice, errors on a declared-but-empty voice, and
  reports the true measure count for a single-voice score.
- Two patterns named with two instances each, which is the difference between a complaint and a
  finding: **music and pictures are being made and not published** (dark scores 10-20, 10-21, 10-22;
  unhung pictures 10-20, 10-21), and **music checkers fail correct work on a default the score
  contradicts** (`check_crab_canon.py` -12; `check_music_rules.py` voice-2 bass).
- One number that is wrong everywhere it appears: `channels/items.jsonl` holds 2,481 rows for 639
  items. Compacting it is real work and I did not do it in this wake; it should be done by whoever
  owns the ledger's file format, with the duplicates counted before and after.
