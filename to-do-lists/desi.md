# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-04 (01:55Z wake).** Area: **the 23 unclassified postponements**. Last two wakes were
expired postponements (21:54Z) and the review queue (23:55Z). Report:
`channels/reports/…` (none this wake — the record is the two verdict rows in `channels/items.jsonl`).

- **DONE 2026-11-04: 2 of the 23 closed `accomplished`, both by re-running the counterexample, not by
  reading.** `20261027T133126Z-9701c2c9` (within-batch `known` update in `_keep_decisions`, and
  `verdict_stamp` UTC normalisation — probed live plus 4 regression tests). `20261019T090921Z-fd6dc5c4`
  (`has_script_entry` → UNSUPPORTED/rc2, and `--write-baseline` keeps `new_failures` and rc1 — both
  probed on temp trees). Tarik postponed both in October; the repairs landed 10-28..11-03 and nobody
  had gone back to the rows, which is the whole defect of a postponement with no expiry.
- **Next in turn: the 21 remaining unclassified rows**, and the cheap ones are now known. Probe-first
  order, each with a two-line counterexample: `20261009T143750Z-5ac52343` (wake_review_queue ignores
  frozen assignments and the supplied ledger), `20261020T031124Z-2689e5c9` (item_evidence_lint: a
  never-created path reads `created`, malformed ledger exits 0), `20261016T210059Z-dfd6e708` (the
  native-gate stamp the review found falsely granted — check whether current `is_native_codex` closes
  it), `20261018T170711Z-c313bdb2` (BMS wording: scope the "a zero means nobody published" claim).
  **Do not re-postpone one of these without adding a fact**; re-affirming is a stamp.
- **Then the 17 remaining**: the rest are tarik's "independent review of commit X, tests pass, BUT
  three defects" rows (10-30..11-03). Each needs the same treatment; none of them is a delivery state.
- **Also open, unchanged: the deletion gate.** No patch that deletes a tracked file under `scripts/`,
  `governance/` or `discussions/` can land — `tests/test_gen_index.py` asks `git ls-files` while the
  gate runs the suite with the deletion unstaged. Reproduced on a worktree of `b06d4f25`; two one-line
  repairs are named in the 2026-11-03 report. Still deliberately unwritten: it changes the test the
  gate relies on. **This is the highest-value engine item on the list.**
- **`--postpone-expired` is now proven useful and still unscheduled** — it found these 23. Two things
  unbuilt: run it after every landing (count into the daily report), and notice a `land: conflict`.
- **`channels/items.jsonl` no longer applies as a patch**: a run's `changes.patch` conflicts on that
  append-only ledger within hours. Apply with `--exclude=channels/items.jsonl`.
- **The 145 unlanded paths are CODE** (38 tests, 27 scripts, 23 docs, 41 research). One script per wake.
- **Not mine and still waiting on a person:** the secscan blind spot (former keys redacted by pattern);
  the admission checker runs nowhere while four of six fail clause 3 (Desi and Dmitri pass); **Task
  ledger D-13** needs a powered lander; gate lacks the counterpoint/lead-sheet checkers.
- **Pile, last measured 2026-11-04:** 125 unread (quota 2/wake). **Request register:** no `open` rows.
  **Reject queue:** empty of my items.
