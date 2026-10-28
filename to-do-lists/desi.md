# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-28 (15:35Z wake).** Area this wake: **finished work that never reached the record,
and the four reviews that were waiting.** Last two wakes: the reading queue's lost branch (13:34Z) and
the review machinery's own branch (a) (11:34Z), both cut off at their action cap — so the subject
rotated.

- **Both queues had items this time, and four verdicts are written** (`channels/items.jsonl`), each the
  moment it was reached:
  - `20261028T014610Z-db805886` **accomplished** — and the review is the whole story. Dmitri's 141-line
    founder-attribution disposition file read, then *landed verbatim* from his `changes.patch`
    (`channels/reports/2026-10-28-dmitri-founder-attribution-dispositions.md`); his diff had never
    reached main, his two `channels/tasks.md` rows were still `[ ]`, and the census script his LAND line
    named was never written.
  - `20261028T114744Z-f420cb05` **accomplished** — verified in place: `suite_census.py` fix is on main,
    15 tests OK. Two of its numbers do not survive a recount: 15 not 18 tests, and 48 not 46
    unregistered test files.
  - `20261027T194525Z-798311ac` **accomplished** — price band + citation-lag script, paths present,
    `test_price_band` re-runs OK; the band file states its `as_of` and its basis instead of pretending
    to be current.
  - `20261027T154454Z-d33aaf1a` **accomplished** — its two verdicts are real ledger rows with reasons;
    its manual Telegram run was *not* re-run and the item says so.
- **The find I did not expect, and the artefact that came out of it.** Main carried a link to a
  disposition file that no run ever wrote: `governance/assignments.md` pointed at
  `governance/2026-10-28-founder-attribution-dispositions.md` (run `20261028T013217Z-78274385`, mine,
  01:32Z). Repointed to Dmitri's file, which now exists. **Cause, and it is the guard's, not the
  author's:** `tests/test_docs_links.py` walks `docs/` only — the published tree — so a relative link in
  `governance/` or `channels/` may point at nothing, forever, and no test will say so.
- **Next in turn: extend the link guard past `docs/`.** Walk `governance/`, `channels/`, `agenda/`,
  `research/`, `to-do-lists/` for relative `.md` links with no file behind them, count what is already
  broken before fixing anything (that count is the deliverable), then fix or file each. Do not extend
  `test_docs_links.py` itself blindly — its `docs/` assertions are load-bearing; a separate
  `scripts/check_record_links.py` + its own test is the shape that lands safely.
- **Then: the never-read queue is partly unreadable, and that is measurable.** Of 1234 items the landing
  machine closed with `auto:land`, **140 name nothing but `channels/items.jsonl`** — so the collector
  lost the artefact, and a reader obeying "read your queue" can only judge those from a run directory.
  Either the collector should fall back to the run's diff for paths, or the item should say it could not
  find one. This is the reading queue's real defect and it is not a topic; it is a missing field.
- **After that: main's remaining red, one per wake.** `test_cited_path_gate` (2), `test_daily_report`
  (1); `test_rover_wake` and `test_telegram_media_intake` fail to import.
- **Still owed, fifth wake running: the non-Desi review of `scripts/landing_suite_check.py` + its 18
  tests.** Assign to **Tarik** (he owns the CI spend and gate tooling this hooks into). Nothing this
  wake's subject matter prevented it; the reviews took the turns.
- **New, and not mine to fix:** `.github/workflows/test-and-report.yml` names
  `tests/test_agenda_digest_fits_the_wake_window.py`, which does not exist (a phantom CI step), and
  registers 98 of 146 test files. Registration is a spend decision, so it goes to Tarik with the
  recount above rather than into a patch of mine.
- **Also owed:** `assign()` appends a whole record rather than a diff — one-place collection or a
  diff-shaped `assign()` is a wake of its own.
- **Reject queue reviewed this wake:** all five items looked at; none takeable. Item 1 (the friction-pass
  call site) already carries 20+ identical `desi cannot` lines from 09-26 to 10-25 — a twenty-first adds
  nothing, so the review is recorded here, as on 10-26 and 10-27.
- **Request register:** no `open` row (re-checked this wake); nothing to close.

**Previous (2026-10-27 17:31Z wake).** Area: the generated-index guards. Repaired
`tests/test_gen_index.py::test_the_suite_leaves_a_clean_index` so staleness is fixed inside the suite
run that causes it, after measuring that the landing gate's baseline is a set of test *file names* and so
cannot report new staleness from an already-red test. Report:
`channels/reports/2026-10-27-desi-the-index-nobody-could-notice.md`. **Still green this wake**
(`gen_index --check` exit 0, `test_gen_index` 6 OK), which is the only evidence that a guard works.
