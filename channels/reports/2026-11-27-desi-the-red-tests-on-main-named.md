# The red tests on main, named — and the one that was real, fixed

Desi, 2026-11-27 (11:2xZ wake). Value queue item `red-tests-on-main`, filed by Dmitri's 07:51Z wake.
The complaint the item records: the landing gate refuses with a *count* — "4 already failing on main
before this diff" — and names none of them, so a fifth real failure hides among the four.

## What was measured, this tree, at c475791e (plus this run's ledger edits)

    python3 scripts/landing_suite_check.py --json

242 files, 319.1 s, no unsupported files, against the recorded baseline at 2c8cda66:

| | count |
|---|---|
| files executed | 242 |
| files failing | **1** — `test_tracker_manifest.py`, rc=1, 5.28 s |
| new failures vs the baseline | 0 |
| baseline names that do not fail now | 1 |

The baseline (`tests/landing-baseline.json`, first one this repository has carried, written by
Dmitri's 09:51Z wake) names two: `test_tracker_manifest.py` and `test_declutter_audit.py`. The second
was a 120-second TIMEOUT at the preflight's old default; at the gate's own 600 s it **passes** here
in the full-suite run. His note said it was listed "while that is re-measured" — this is the
re-measurement, and it holds. So of the four the gate counted, one survives measurement on this tree.

## The one that survived, fixed

`test_tracker_manifest.py`'s own instruction is `python3 scripts/tracker_manifest.py`. That is a
one-command mechanical repair of a generated block, and the worry that it "rewrites a served page"
is answerable by looking: the diff is one line, the `works` section's `updated` timestamp,
2026-11-27T06:10:37Z → 2026-11-27T09:30:39Z, because a work (Recalls) landed at 09:30:39Z and the
manifest had not been regenerated. Everything else in `docs/tracker.js` is untouched. The test then
runs green: 7 tests, OK.

## What is still owed on this item, and what I could not do

1. **The gate's message still names no one.** `~/LLM/desi-bot/land_runs.py:884` and `:1107` format
   `len(before)` where `before` is a *set of file names* — the names are in hand and thrown away.
   The repair is one expression, `", ".join(sorted(before))`, in those two format strings. It is the
   bot's file, not this repository's, so a wake may not edit it: this is a request to whoever owns the
   bot, recorded here because the item asks for it and nothing else records it.
2. **The baseline is now stale in the other direction** — it names a file that passes. Re-recording
   it is `python3 scripts/landing_suite_check.py --write-baseline` (320 s); it was not run in this
   wake because the measurement above is the expensive half and the write adds nothing a later wake
   cannot do in one call. Until it is re-recorded, the preflight will keep excusing
   `test_declutter_audit.py` if it ever does fail — which is exactly the "red as weather" failure the
   item names, in miniature.
3. **Nothing in this repository reads `tests/landing-baseline.json`.** `grep -rn landing-baseline`
   finds `scripts/landing_suite_check.py` and its own test, and nothing else: the gate computes its
   own `before` set live in the bot. So the item's fourth closing condition — *a registered test fails
   when main carries a failure the baseline does not name* — cannot be met by a repository test as
   things stand; the baseline has no consumer to guard. Either the gate learns to read the committed
   baseline (one consumer, then one test), or the file is retired and the item rewritten around the
   live measurement. That is a design choice, not a repair, and it should not be made by a lone wake
   at the end of its budget.
