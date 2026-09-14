# Controlled benchmark spec — identical task for both models

Compose a two-voice Baroque minuet, binary form (AABB), in D minor.

Fixed parameters (do not vary):
- Meter: 3/4, L: 1/8
- Key: D minor
- Form: A section 8 bars, B section 8 bars, each repeated (AABB), 16 bars of
  distinct music total
- Voices: 2 (treble + bass), keyboard idiom
- A section: starts and ends in D minor (or relative F major at the A-section
  half-cadence, composer's choice), B section modulates and returns
- Discipline, fixed before composing: zero parallel fifths, zero parallel
  octaves/unisons, zero voice crossings, checked against BOTH
  scripts/check-counterpoint.py and scripts/check_music_rules.py
- No lyric, no chord symbols needed — pure two-voice counterpoint like the
  existing Two-Part Invention

Metrics to log: elapsed time from first tool call to fully-verified score on
both checkers, number of correction iterations, categories of errors caught.

This file is reused verbatim for both the sonnet and opus runs so the task is
identical and only the model differs.
