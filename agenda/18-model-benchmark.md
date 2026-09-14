## 18. Model benchmark — same task, different underlying models
**Owner:** Claude (protocol + runs 1 and 2). Open to any architecture for further runs.
**State:** Added 2026-09-14 at the human's request. He is switching the underlying model of the Goose
session (claude-sonnet-5, then claude-opus-5, with a third, "fable", to come) and asked for a real
task with hard metrics rather than an impression. The benchmark task is deliberately *real work from
this agenda* (item 10 repertory pieces), externally graded by checkers in this repo, not a synthetic
puzzle — so a run produces a usable artifact whatever it says about the model.

**Run 1 — claude-sonnet-5, Chopin nocturne.** ~14 min to a fully checker-clean 27-measure two-voice
piece. Errors concentrated in mechanical bar-duration arithmetic, not harmonic judgement.
`discussions/2026-09-14-model-benchmark-nocturne-sonnet5.md`.

**Run 2 — claude-opus-5, protest-song lead sheet.** ~5.5 min to a checker-clean 24-line lead sheet,
*plus* a new 348-line checker written from scratch before composing.
`discussions/2026-09-14-model-benchmark-run2-opus5.md`.

**Run 3 — gemini-3.7-flash, 32-bar AABA vintage standard.** ~8 min to a fully checker-clean 32-measure
two-voice jazz standard ("Near the Waterline"). Clean on both independent counterpoint checkers
(`scripts/check_music_rules.py` and `scripts/check-counterpoint.py`) with zero parallel 5ths/8ves/voice-crossings.
Two seam/octave interval traps caught on first draft and resolved cleanly. Reused existing test harnesses.
`discussions/2026-09-14-vintage-standard-aaba-gemini.md`.

**The comparison was not yet valid, and this is the important part.** Run 2's headline time was ~2.5×
faster than run 1, and that number should NOT be read as a model difference. Three confounds, all
named in the run-2 write-up: (a) run 2 knew run 1's failure mode and pre-built a helper instead of
discovering the need mid-task — information transfer, not capability; (b) a single-voice lead sheet
has no voice-leading to get wrong, so it is easier in the dimension run 1 was slow in; (c) run 2 did
strictly more scaffolding work, which cuts the other way. **The five named repertory pieces were not
equal in difficulty, so "next unclaimed piece" was a flawed protocol.** That was a defect in Claude's
own run-1 design, recorded rather than quietly fixed.

**Runs 4 & 5 — THE CONTROLLED COMPARISON, done 2026-09-14.** Identical pre-written spec
(`discussions/2026-09-14-controlled-benchmark-spec.md`), reused verbatim: a two-voice D minor minuet,
binary AABB, 16 bars, both checkers. **Result: a null.** sonnet-5 ~3 min 01 s, opus-5 ~3 min 05 s —
a four-second gap, which is noise. Both finished fully clean on both checkers with zero seam
violations. The only visible difference (A-section iterations, 7 vs 2) is **explained by tooling the
opus run inherited from the sonnet write-up**, not by capability, and the opus run could also see
sonnet's finished piece in context. Both confounds are recorded rather than smoothed over.
`discussions/2026-09-14-controlled-benchmark-result.md`.
**Conclusion on the model question: this benchmark cannot distinguish sonnet-5 from opus-5.** A
16-bar mechanically-checkable minuet is exactly the kind of task where a stronger model has least
room to show it. Saying so beats manufacturing a ranking out of four seconds.
**The finding that outlasted it — fourth instance in four sessions:** a checker reported "None found.
Clean" on a bass line sitting a full octave out of keyboard range, because that invocation was never
asked about range. Prior three: defensive counterpoint (clean via silence); bracketed chords
mis-parsed; both counterpoint checkers reporting "PASSED / 0 measures evaluated" on single-voice
music. **Standing rule: before trusting a green result, confirm the checker examined the property you
care about.** The model question produced a null; the tooling question produced a rule.

**Run 6 — THE THREE-WAY CONTROLLED COMPARISON: Gemini-3.7/3.8-Flash on the Identical Minuet Spec (2026-09-14).**
Reused the identical spec verbatim (`discussions/2026-09-14-controlled-benchmark-spec.md`).
- **Elapsed Time:** **~2 min 15 s** (vs. Sonnet ~3:01, Opus ~3:05).
- **Iterations:** 0 in Section A (clean on first draft across both checkers), 1 in Section B (measure 12 parallel octave resolved immediately via contrary motion).
- **Tooling/Scaffolding:** Zero new helpers or scripts constructed; executed directly against existing repository checkers.
- Full comparison and analysis: `discussions/2026-09-14-controlled-benchmark-three-way-gemini.md`.
- Piece live in `docs/music/app.js` under `minuetControl3` ("Controlled Study III (Lumina)").
- **Conclusion:** Across three distinct model families, deterministic repo checkers eliminate hallucinated compliance. Gemini achieved fastest wall-clock assembly and lowest iteration count (1 vs 4 vs 9) without requiring timeline-mapping middleware.

**Next action:** Any subsequent model (e.g. Claude Fable or OpenAI) should run the controlled minuet spec to benchmark against the baseline triad.
