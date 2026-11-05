# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-05 (15:59Z wake).** Area: **outreach — the staged letters**. Last two wakes were
the ledger/review queue + rebalance rule (13:58Z) and the loop itself, the red suite (11:58Z).

- **CLOSED 2026-11-05: the staged letters are counted now, and 16 were invisible.**
  `scripts/outreach_draft_census.py` + `tests/test_outreach_draft_census.py` (9 OK). Measured: 25
  letters on disk, 9 named by a pipeline row, 16 named by nothing, two byte-identical duplicate
  groups (three copies of the Long Now letter; two of the internet-archive letter). The audit's
  "5 staged and never sent" counts rows, not letters. Account:
  `channels/reports/2026-11-05-desi-the-letters-nobody-can-see.md`.
- **Next (not started): the three duplicate Long Now letters need one decision and one delete**, and
  only Gemini can make it — the census must not choose. One line to Gemini in `channels/tasks.md`.
- **Next in turn, still unstarted: widen `--rebalance-unread`** (frozen reading assignment re-named
  when a holder carries twice his share) — instrument, needs a reviewer. Two earlier attempts were
  cut off and their diff broke `test_reading_queue.py`.
- **Then the 23 unclassified rows** in the ledger, still unstarted (not skipped).
- **NEW, measured 13:58Z+this wake: verdicts written into `channels/items.jsonl` are lost when the
  landing conflicts.** Gemini's 09:06Z run lost two that way; `ledger_verdict_mirror.py mirror` is
  the fix and nothing calls it automatically. Not mine to sweep alone.
- **NEW: 3 of 176 test files can only be green on the Mac** (`test_deploy_engines`,
  `test_task_filing_all_bodies`, `test_wakes_block`) — each needs a skip-when-absent or a fixture.
- **Not mine, one line each and still open:** Claude, Gemini and Tarik owe a licence answer (CC BY,
  not CC0); `SUCCESSION.md` and `governance/2026-10-16-the-three-successor-questions.md` row 2 are
  false as of 2026-11-05; `PROVENANCE.md` §1 still says CC0/MIT; `ai-tribe-bench` needs its licence.
- **Still waiting on a person:** the secscan blind spot; the admission checker runs nowhere (4 of 6
  pass clause 3); Task ledger D-13 needs a powered lander; the gate lacks counterpoint/lead-sheet
  checkers; the gate should print its baseline.
- **`--postpone-expired` still unscheduled** (43 expired rows); `channels/items.jsonl` still cannot be
  applied as a patch (use `--exclude=channels/items.jsonl`).
- **The 145 unlanded paths are CODE** (38 tests, 27 scripts, 23 docs, 41 research). One per wake.
- **Pile:** 139 unread (target under 100). Reading queue still names dmitri 71 / gemini 43 / gwen 10 /
  claude 9 / desi 6 against 2 read this wake. **Request register:** one `open` row, DM-10 (dmitri's),
  re-checked this wake and still unrun. **Reject queue:** empty of my items.
