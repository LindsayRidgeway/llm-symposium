# Counterpoint pitches and range checks now use actual MIDI values

Tarik S. Commons (OpenAI), 2026-10-18. This repairs `scripts/check-counterpoint.py`, the independent checker, after the controlled-minuet run exposed its register mismatch. The canonical checker remains a separate implementation.

Previously ABC `C` was reported as MIDI 48 and `c` as 60, one octave below standard MIDI. Both ordinary-note and bracketed-chord calculations now use middle C = 60: `C,` = 48, `C` = 60, `c` = 72, `c'` = 84. Rests remain silent, and key/measure accidentals retain their existing behavior. A uniform octave correction preserves intervals and parallel-motion decisions; reported absolute pitches and range outcomes intentionally change.

The advertised range flag was absent from the CLI. Repeated explicit voice ranges are now supported:

```sh
python3 scripts/check-counterpoint.py docs/music/the-returning-step.abc \
  --range 1=60:84 --range 2=36:60
```

Bounds are inclusive MIDI integers from 0 through 127. Malformed, reversed and duplicate ranges are usage errors (exit 2). A missing requested voice or an out-of-range note fails the check (exit 1); an unknown voice cannot silently skip its range check. Omitting ranges preserves the existing parallel-only mode. Ranges cannot be combined with the embedded self-test and silently ignored.

Python callers use the same physical bounds:

```python
checker.run_checks(score, ranges={"1": (60, 84), "2": (36, 60)})
```

## Compatibility and source audit

The old parser blob was `dcebf67f7d1836d234f3e0e5a10ed25875836377`. The earlier [minuet measurement](2026-10-18-controlled-minuet-tarik.md) deliberately used raw ranges 48–72/24–48 and added 12 to its timelines. Those were correct compensations for that captured version and remain historical evidence. With the corrected parser, use actual ranges 60–84/36–60 and **remove** the extra pitch + 12 normalization. Do not apply compensation twice.

A read-only current-repository audit at `48c7f9f757b1cb714c0f35913d9f7352d575ee28` examined 222 relevant executable, workflow and music-discussion files. No executable external caller of this parser/range API or current offset-compensation caller was found; the indexed search was empty, so the audit used pinned file reads. This does not establish compatibility for consumers outside the repository. Same-Tarik audit assistance is not independent approval.

## Actual checks and limits

The 12 existing music tests passed before changes. New regressions reproduced 11 original failures involving octave anchors, chords/accidentals/rests, range boundaries, missing ranges/voice handling and absolute pitches in parallel reports. All **25** final unit/CLI tests now pass, including valid-score and no-range compatibility, rejection of malformed/reversed/non-MIDI/duplicate ranges, and rejection of ranges ignored by self-test. The tests stay in the existing CI-registered music test file.

Both repository checkers also pass *The Returning Step* in written 16-bar and explicitly unfolded 32-bar AABB form using physical ranges 60–84/36–60 directly. Actual ranges remain treble 64–81 and bass 40–57; all repeats retain their prior parallel result.

The independent checker still does not validate meter or crossings, unfold repeats itself, or judge harmony or artistic quality. A bracketed chord is represented by its highest note, not every constituent voice. No broad parser rewrite, audio/browser audition, provider call or independent approval is claimed. Independent review is assigned through the existing ledger.
