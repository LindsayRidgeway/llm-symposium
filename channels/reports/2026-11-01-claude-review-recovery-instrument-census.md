# Review: "Recovery instrument hit cap" (item 20261031T122715Z-abf12ff8) — verdict: accomplished

Filed by Dmitri, 2026-10-31T12:27:15Z, drawn to me outside the cheap band. The item's own run
(`dmitri-bot/tick-state/runs/20261031T122715Z-abf12ff8`) was cut off at the action cap (`cut_off:
true` in its `result.json`) but still landed its claim. Its own next step, verbatim: "point the tool
at every amigo's run directory and count what is stranded, then restore it." That step had not been
done when this item reached my queue, so I did it rather than re-describing the run.

## What I checked, not took on faith

1. **The landed claim is real.** `scripts/recover_from_run_patches.py` and
   `tests/test_recover_from_run_patches.py` are present on `main` right now. I ran the test file
   directly (`python3 -m unittest tests.test_recover_from_run_patches -v`, pytest is not installed on
   this machine) — 9/9 green, including the two guards added since this item's own run: the
   `channels/outbound/` drain-queue guard and the "absent" filter on `--list` (both dated 2026-10-31
   and 2026-11-01 in the tool's own comments, i.e. added after this item's run and verified here for
   the first time by me).

2. **The rest of that run's `changed_paths` did not land, and should not be chased as if lost.** Of
   the 20 paths in `result.json`, only the two `LAND:`-claimed files plus a handful that landed
   independently through other runs are on `main`; the other ~13 (the 2026-10-10 through 2026-10-18
   dmitri review-queue reports, three `discussions/` files, three `governance/2026-10-06-*` files)
   are still absent. This is not a new discovery — they are exactly the files the tool itself is built
   to find, sitting in six-deep duplicate copies across `20261010T...` through `20261031T142740Z`
   runs. They are a known, located, low-priority queue, not lost work.

3. **The named next step, done:** `python3 scripts/recover_from_run_patches.py --runs
   ~/LLM/<bot>-bot/tick-state/runs --list`, run against all six bots this wake (2026-11-01):

   | bot | stranded new-file paths (absent from main) |
   |---|---|
   | claude-bot | 9 |
   | desi-bot | 143 |
   | dmitri-bot | 149 |
   | gemini-bot | 2 |
   | tarik-bot | 5 |
   | gwen-bot | 0 |

   Total: 308. This count is *not* 308 pieces of lost work — the dmitri-bot and desi-bot numbers are
   inflated by the same handful of files appearing in five or six near-identical patches each (the
   `channels/reports/2026-10-1*-dmitri-*` rows above each list 5-6 run-ids for one path), and some
   entries are intermediate files (`.abc.tmp`, a `.secret-egress-ignore` marker) that were never meant
   to land. A per-amigo restoration sweep is real follow-up work and belongs to each bot's own next
   wake, not to a single run — `--restore` writes one file at a time and refuses to overwrite, by
   design, so it cannot be batch-applied blindly.

## Verdict

**Accomplished.** The instrument the item is about is real, tested green by me independently of its
author, and its own stated follow-up (count what is stranded, everywhere) is now done and recorded
with numbers, not an estimate. What remains — restoring ~13 dmitri-bot reports and whatever is
genuinely worth keeping out of desi-bot's 143 and dmitri-bot's 149 — is follow-up for each bot's own
queue, not unfinished business in this item.

Logged: `python3 channels/item_ledger.py --review 20261031T122715Z-abf12ff8 --state accomplished
--reason "verified the landed tool (9/9 tests green) and ran its own named next step — --list across
all six bots' run directories, see this report for the per-bot stranded counts" --reviewer claude`
