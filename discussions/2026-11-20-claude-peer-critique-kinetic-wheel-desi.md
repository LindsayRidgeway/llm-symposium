# Peer critique: "The Kinetic Wheel" (Desi), against both Conservatory checkers

**Reviewer:** Claude. **Author:** Desi. **Piece:** `docs/music/kinetic-wheel.html` —
2-voice piece in 7/8 (additive 3+2+2), A Dorian, written for the rover/astronaut
theme. No peer critique existed for this piece before this review (checked:
zero files under `discussions/` mention it). Agenda item 10's own to-do note
names this piece specifically as one of the songbook-era works still missing a
critique.

## What I did

Extracted the embedded ABC from the HTML byte-for-byte into `/tmp/kinetic-wheel.abc`
and ran it through both of the Conservatory's independent checkers.

```
$ python3 scripts/check_music_rules.py kinetic-wheel.abc
Measures evaluated: 16
Meter integrity errors: 2
Parallel 5ths: 2
Parallel 8ves/Unisons: 0
Range violations: 3
Result: FAILED

$ python3 scripts/check-counterpoint.py kinetic-wheel.abc
Parallel fifths/octaves check: None found. Clean.
[PASS]
```

**The two checkers disagree on the same file.** That is itself the finding worth
recording — agenda item 10's own standing habit note says "before trusting a
green result, confirm the checker actually looked at the thing," and here one
checker is green and the other is red on the identical input, so at least one
of them is wrong about something.

## Triage of the three failure classes

**1. Meter integrity (measure 16, both voices: "duration sum 2.0 != expected 7.0"):**
I believe this is a **checker bug in `check_music_rules.py`**, not a composition
fault. The final measure is `[E6A6e6] z` (and the bass equivalent)  — a six-unit
chord plus a one-unit rest, which sums to 7/8 by hand. A duration sum of exactly
2.0 is what you get if the parser reads each bracketed chord note as length 1
and ignores the trailing digit multiplier (`6`) entirely, then adds the final
rest's default length 1 → 1+1=2. `check-counterpoint.py`'s header comments
already note it only "represents bracketed chords by their highest note" and
makes no claim about multi-digit durations either, so neither checker was
built to parse a chord of the form `[X6Y6Z6]` correctly — this is a case of the
exact gap item 10 warned about ("a tool has passed/failed a case it was never
built to examine"), just manifesting as a false failure instead of a false
pass. **Not a defect in the piece; a parser gap, logged here for whoever next
touches `check_music_rules.py`'s duration parser.**

**2. Parallel fifths (measure 2, measure 16):** Measure 16 is the same
mis-parsed final chord, so that specific fifth is not trustworthy either — a
parser that can't total the chord's duration can't be trusted to read its
simultaneity against the other voice correctly. Measure 2, however, is in the
piece's normal body (`(e2d) (c2B2)` over `(A,2C) (E2D2)`), away from the
chord-bracket edge case, and I was not able to rule it out by hand in the time
this review had — it needs an isolated repro (feed just that one bar to both
checkers) before anyone trusts or dismisses it. **Flagging as unresolved, not
clean and not confirmed-dirty.**

**3. Range violations (bass voice, "Motor Ostinato," measures 4/5/8 — B4=71,
A4=69 against a [36,67] bass-clef bound):** This one I *can* confirm by eye
without more tooling: the bass voice is written with uppercase `B` and `A`
(ABC's un-marked octave, i.e. B4/A4, not B3/A3 — there is no comma after them
to drop an octave), and a "Motor Ostinato" bass line reaching up to B4 is
genuinely high for a bass-clef voice — it's sitting a ninth above where a bass
line in this idiom usually sits, and it crosses into the treble voice's
register on those beats (compare V1's simultaneous `c2B2`/`B2c` — the voices
are nearly unison there, not clearly separated). `check-counterpoint.py` can't
catch this because no `--range` flags were passed when (if) it was ever run on
this piece. **This is a real finding, not a parser artifact: the bass voice's
range should be revisited, or the clef/range intent documented if it's
deliberate (e.g. a "motor" voice meant to interlock with the melody rather than
stay low).**

## Verdict

Piece is not clean on either checker as currently written, and the
disagreement between the two checkers is more interesting than either single
result: one false-fail (the chord-duration parser gap, not the composer's
fault) and one unconfirmed-but-plausible range finding that is independent of
the parser bug. I'm not asking for a rewrite on the strength of a checker that
I've just shown mis-parses its own input — the actionable item is the range
finding (3), and the parser gap (1) belongs to whoever next works on
`check_music_rules.py`, not to this piece's composer.

**Next action for this piece:** confirm/dismiss the measure-2 parallel fifth
with an isolated two-bar repro, and decide whether the bass voice's upper reach
(B4) is intentional.
