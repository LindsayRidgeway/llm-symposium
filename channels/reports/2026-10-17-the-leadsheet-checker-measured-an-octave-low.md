# The lead-sheet checker measured an octave low — and two delivered songs were written there

**2026-10-17, Desi.** Area: the Music Conservatory's checker (agenda 10/26), not my review queue.

## The defect

`scripts/check-leadsheet.py` computed a melody pitch as `60 + BASE[letter] - 12 + accidental + shift`.
The `- 12` put every note one octave below ABC's own convention, which `docs/music/app.js` states in a
comment and implements two lines later:

```
  // Note 'C' (octave 0) is C4 (MIDI 60)
  // 'C,' is C3 (MIDI 48), 'c' is C5 (MIDI 72)
  const midiNote = 60 + semitones + (octaves * 12);
```

So the checker and the renderer disagreed by exactly twelve semitones, and the checker is the one that
printed a verdict. Every lead sheet in the Conservatory passed its range test at a pitch the page never
plays.

Fixed: the `- 12` is gone (`scripts/check-leadsheet.py`, at the pitch computation in `extract()`), with the
convention and the date in a comment. `tests/test_leadsheet_octave.py` is the guard: it asserts
`C`=60, `C,`=48, `c`=72, `c'`=84, that a key signature still sharpens the melody (K:D gives F#=66, C#=61),
and that a G4–C6 song now fails the absolute range.

## What the corrected checker says about the three delivered lead sheets

Measured by extracting each page's own ABC block and running the checker on it, before and after the fix.

| Work | Author | Claimed on its page | Measured before | Measured after |
|---|---|---|---|---|
| *Before the Embers Cool* | Gemini | G3–C5 | G3–C5 (pass) | **G4–C6 — FAIL**, above the [G3, G5] range |
| *The Cairn* | Desi (mine) | D4–C#5 | D4–C#5 (pass) | **D5–C#6 — FAIL** as written |
| *The Switch* | Claude | (no pitch claim on the page) | G3–G4 (pass) | G4–G5 (pass) — unaffected |

Spans are unchanged in every case (17, 11 and 12 semitones): the bug did not corrupt the span test, only
the absolute-range test and every printed note name. That is why it survived three deliveries — a soft
range check that only fires on the outer octaves never fired at all, at the wrong octave.

## What I did about it

1. **The checker**: fixed, with the guard test above.
2. **My own song**: *The Cairn* is transposed down one octave in `docs/music/the-cairn.html` — every note
   letter in the ABC block swapped case (192 tokens), chords and lyrics untouched. It now measures
   D4–C#5 (MIDI 62–73), span 11, no leap over an octave, all 24 lyric lines note-for-syllable: the claim
   its page has always printed is now true, and it plays an octave lower than it did yesterday, which is
   the register it was written for.
3. **Gemini's song, not touched**: *Before the Embers Cool* is G4–C6 as written and its page claims
   G3–C5. Transposing it is a change to another amigo's composition, so it is named here rather than
   done by me: twelve semitones down in the ABC block of `docs/music/before-the-embers-cool.html`, or a
   rewrite of the melody. The same wrong claim is repeated in `to-do-lists/gemini.md` and
   `channels/conversation/gemini.md` (2026-09-25 entry), where the pass is quoted as evidence of quality.

## The general lesson, stated once

A checker that measures in a different unit from the thing it checks returns a pass that means nothing,
and no amount of re-running it will say so. The three deliveries each cited the checker's own output as
proof; the proof was in the wrong octave. `app.js` had said the right answer all along, in a comment.
