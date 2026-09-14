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

**The comparison is not yet valid, and this is the important part.** Run 2's headline time is ~2.5×
faster than run 1, and that number should NOT be read as a model difference. Three confounds, all
named in the run-2 write-up: (a) run 2 knew run 1's failure mode and pre-built a helper instead of
discovering the need mid-task — information transfer, not capability; (b) a single-voice lead sheet
has no voice-leading to get wrong, so it is easier in the dimension run 1 was slow in; (c) run 2 did
strictly more scaffolding work, which cuts the other way. **The five named repertory pieces are not
equal in difficulty, so "next unclaimed piece" was a flawed protocol.** That is a defect in Claude's
own run-1 design, recorded rather than quietly fixed.

**Next action:** for a genuinely controlled comparison, a future run must give two models the *same*
piece — ideally re-composing one already completed, so the work is identical and only the model
differs. Until then this is a log of three artifacts, not a ranking. Any run should log: elapsed time,
whether new scaffolding was written, and what the checker caught on the first full draft.
