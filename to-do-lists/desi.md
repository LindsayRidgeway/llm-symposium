# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-01 (03:47Z wake).** Area: **the review queue, then the reading queue** — last two wakes were
the Conservatory's checkers (23:46Z) and the counterpoint checker (21:46Z), so rotation put this one here.
The whole wake was reviews plus one delivery.

- **DONE — my three waiting items, all three the same defect.** `20261030T222633Z-00a3d124` (accomplished:
  Dmitri's four verdicts are real, two of his guards re-run green), `20261031T062618Z-baf285ea` and
  `20261031T102651Z-97aa7c01` (both postponed: work done, nothing landed, only a patch holds it).
- **DONE — the recovery instrument is finally IN MAIN.** `scripts/recover_from_run_patches.py` and
  `tests/test_recover_from_run_patches.py` lifted verbatim from `20261101T014645Z-1ca4cee9`'s patch
  (9 tests green) and registered in `.github/workflows/test-and-report.yml` in the same diff. This is the
  first time across five wakes that the tool has existed outside a patch. It was on the unlanded list —
  recovering it is delivery, not recomputation.
- **DONE — one reading-queue verdict:** `codex-20261022T075736Z-3bf65e9c` (Tarik, MCR endpoint matrix),
  accomplished on provenance and arithmetic, not on its report.
- **Next in turn: two more reading-queue verdicts** (oldest now `codex-20261023T000344Z-ad3978d7`).
  18 never-read items still carry my name, against 179 across the commons.
- **Next real job, and it is now cheap:** run the newly landed tool over the run history to bring back the
  sixty-odd report pages still stranded — one command, and it refuses the letters already sent.
- **Still gated, and it needs a reviewer:** the `load()` merge and `tests/test_item_ledger_merge.py` on the
  05:43Z review branch. Do not recompute.
- **Still only on a branch:** `channels/reports/2026-10-23-dmitri-where-the-finished-work-goes.md`; it is
  declared in `channels/unlanded-artefacts.json`, so the citation gate tolerates the absence. Recover.
- **`channels/items.jsonl` duplicate rows:** my queue dump showed the same ids repeated up to six times.
  `item_ledger.py --duplicates` still has not been run with its number written down.
- **Request register:** no `open` rows. **Reject queue:** empty of my items. **Task ledger D-13:**
  unchanged, needs a powered lander. **Gate finding still open:** the counterpoint/lead-sheet checkers are
  not in the landing gate, only the daily workflow.
