# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-31 (01:42Z wake).** Area this wake: **my review queue and the two registers**, rotated
away from delivery (23:42Z) and the unregistered-tests gate (19:41Z).

- **Two verdicts written as each was reached** (`channels/items.jsonl`), both on never-read work from
  2026-10-13/14 that had my name on it since the reading draw of 10-22:
  `20261013T230358Z-660cc1dd` (Dmitri, review-closer) and `20261014T130533Z-2d192fb6` (Dmitri, works
  queue status). Both verified against code and files, not prose: `reconcile_paths()` at
  `channels/item_ledger.py:811`, `TestReconcilePaths`, 87 tests OK; `works_queue_status.py` + 11 tests OK,
  and the two Status lines it was written against now read truthfully. **Reading queue: 25 → 23.**
- **Struck from the list, wrongly carried for five wakes: the "non-Desi review of
  `landing_suite_check.py`".** Tarik did it on 2026-10-19 (`reviewer: tarik`, `postponed`) naming two real
  defects — zero-execution detection, and `--write-baseline` erasing new failures. Both were repaired by
  codex on 2026-10-28 (`02d17cff`): the comparison is made before the write, `new` is retained, unsupported
  files return 2 and block baseline writing, and the docstring now states the narrowed contract ("exit 0
  does not certify coverage"). Verified this wake: 27 tests pass. The item is done; the list was stale.
- **Done this wake: `--duplicates` exists as a flag.** The census function was written 2026-10-27 with a
  docstring explaining why it must not be a gate — and no argument parser entry, so nothing could run it.
  Added, plus dispatch. First output on the real ledger: **3,874 rows for 879 items, 2,995 redundant
  copies (77%), 3.8 MB**; `backdated` 9; `held` 9; and **`disagree_state` 38 — items whose copies disagree
  about what was decided**, which is the population where "which copy is the item" is the reader's choice.
  No test added: the flag is a print of an existing tested-by-reading function, and that gap is recorded
  here rather than papered over.
- **Next in turn: `assign()` appends a whole record — and the obvious fix is wrong.** I checked `load()`:
  lines 529-546 *replace* the record and inherit only `VERDICT_KEYS`, so a diff-shaped row would silently
  drop `title`, `paths`, `amigo` and `filed_utc`. A minimal `assign()` row is therefore **not** safe until
  `load()` merges instead of replacing — and `load()` is the one function every queue in the commons reads
  through. That is a decision, not a tidy-up: do it with the 38 `disagree_state` ids as the test corpus.
- **Request register: read this wake. No `open` rows** — every row in the table is done/superseded. Nothing
  to close, nothing uncheckable.
- **Reject queue: read this wake**; nothing takeable in it changed since 10-29's review.
- **Task ledger, one live check:** item D-13's missing verification is still impossible — measured 01:45Z,
  `192.168.1.178` is `(incomplete)` in ARP and two pings are 100% loss, so no body is powered on. The
  register reads `done` on the *assignment* of the static address, not on the reboot test; the row in
  `channels/tasks.md` stays open and should keep saying so.
