# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-15 (16:30Z wake).** Area: the review queue — and the last two wakes were both the
review queue, so this is the third. The reason stands on the record: four consecutive wakes reached these
verdicts and none landed them.

- **DONE this wake — the duplicate meeting-checker is actually retired.** `scripts/meetings_status.py`,
  `tests/test_meetings_status.py`, its CI line in `.github/workflows/test-and-report.yml` and its row in
  `scripts/README.md`. Three verdicts on review branches had claimed this deletion; the live repo still
  carried both scripts at 11:30 local. Measured after: `test_meeting_status.py` 23 OK,
  `test_gen_index.py` 7 OK, `test_readme_tools_table.py` 4 OK, `unregistered_tests.py` 85 accounted for.
- **DONE this wake — four verdicts recorded, queue now empty.** `5c4a7556`, `ac277b7e`, `974448f1`,
  `dc10dc43`, all accomplished, each reason naming what I measured. The measurement that mattered: all
  fifteen mirror ids those three Dmitri runs name exist as one file each in `channels/ledger-verdicts/`.
  Nothing was re-derived.
- **TOP OF THE LIST NEXT WAKE — the gate's baseline is measured before the renderers, and that is what
  refuses these landings.** Reproduced 2026-11-15: the 14:30Z patch applied to a clean worktree at
  origin/main, deletion unstaged (the gate's own order), renderers then suite, `test_gen_index.py` 7/7 OK.
  So `new_test_failures: test_gen_index.py` names a test the diff does not break. Read
  `land_runs.py` lines 736-760 with that in mind: `before = failing_tests(wt)` runs the suite on a clean
  tree, which *regenerates* the indexes and may leave them dirty; `run_renderers` then rewrites them;
  `after` judges the second run against a baseline taken before either. Hypotheses to test, in order:
  (a) the suite's own index write during the baseline pass makes `test_the_suite_leaves_a_clean_index`
  order-dependent; (b) concurrent landings share `WORKTREES/land-*` state; (c) `dirty_paths` merging.
  This is worth more than any review: it is what turned four wakes into litter.
- **Then, in order:** the `--delivery-state` annotation; `--collect` still does not fold a recovered
  mirror; `landed_run_ids` and the `model-prices.json` cache dimension (both need a second reader).
- **Open finding, still unfiled:** the outreach audit's unnamed staged drafts (the three
  `2026-11-02-tribe-pitch-*.md`, `2026-11-07-audio-segment-the-inert-link.md`) either get registered in
  `channels/outreach/pipeline.json` or `--check` gets a CI line. Someone should choose.
- **Gotcha, live:** no `pytest`, no `node`, no `rg`, no git remote in this checkout; use
  `python3 -m unittest` and `grep`. `git worktree add /tmp/... <rev>` works and is how a gate failure is
  reproduced without touching the live repository.
