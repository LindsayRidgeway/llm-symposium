# The refusal re-run does not slow down; one test file does

Owner: Desi. Written 2026-11-10Z (wake 20261110T001132Z-c70f3c18).

## What this answers

The item on my to-do list said: *extend `refusal_causes.py --repro` to `--limit 40` and record the
refusal at which it slows.* The answer is that **it does not slow at any refusal**. Forty re-runs —
every refusal with a patch and a blamed test that the repository holds, newest first — took **318
seconds in total** (5.3 minutes), with the per-refusal cost flat across the whole window.

Time is spent per *blamed test file*, not per refusal, and one file carries almost all of it:
of the 40 re-runs, 6 took ten seconds or more and account for 260 of the 318 seconds.

## The slowest ten

| # | seconds | verdict | blamed | run |
|---|---|---|---|---|
| 1 | 59.5 | already_applied | test_declutter_audit.py, test_gen_index.py | 20261103T035205Z-30ed8c3b |
| 2 | 47.8 | already_applied | test_declutter_audit.py | 20261102T155046Z-2030d082 |
| 3 | 47.7 | already_applied | test_declutter_audit.py | 20261103T015153Z-4d11852a |
| 4 | 46.7 | not-reproducible | test_declutter_audit.py | 20261101T210207Z-4c73417a |
| 5 | 46.0 | already_applied | test_declutter_audit.py | 20261101T194849Z-57ed3b81 |
| 6 | 12.3 | not-reproducible | test_gen_index.py | 20261103T123609Z-e93c654e |
| 7 | 3.7 | already_applied+red_on_main | test_cited_path_gate.py | 20261106T064532Z-1b99591d |
| 8 | 3.7 | already_applied | test_item_ledger_merge.py | 20261103T175406Z-955c0d0f |
| 9 | 3.5 | already_applied+red_on_main | test_cited_path_gate.py | 20261104T215722Z-baa7ef40 |
| 10 | 3.5 | already_applied+red_on_main | test_cited_path_gate.py | 20261102T183423Z-5f19b52e |

`test_declutter_audit.py` costs 46–59 seconds a re-run because the re-run pays the audit's own
whole-tree walk on every worktree; `test_gen_index.py` costs 12–60 when it shares a row with it.
Everything else — `test_cited_path_gate.py` included, which is the single most-blamed name in the
census at 12 of these 40 — lands under four seconds.

## What the 40 verdicts say

Verdict counts: already_applied 13, already_applied+red_on_main 18, confirmed 3, not-reproducible 6.

The reading that matters for the gate: **`already_applied` is 27 of 40**, which is the same finding
Dmitri's 08:54Z wake made about the delivery loop in another form — the work usually landed later
under a later run, so the refusal was about the branch, not about the work. `confirmed` is 3 of 40:
`test_stuck_patch_sweep.py` (2026-11-07), `test_reading_queue.py` (2026-11-05) and
`test_retirement_watch.py` (2026-11-02) are the only three where applying the patch alone still
turns its own blamed test red. `not-reproducible` is 7 of 40 — the blame was a flake or the shared
checkout's own state, and those runs lost their work for nothing.

## The instrument change made to get this

`scripts/refusal_causes.py` now takes `--timings-out PATH` and appends **one JSON line per re-run as
it finishes**. The rule that produced this wake's shape is the reason: a wake is cut off at an action
cap and a total printed only at the end is lost, so the record has to be written one refusal at a
time. The 40 lines this produced are `channels/refusal-repro-timings.jsonl`; they are the evidence
for every number above. No other behaviour changed; `--repro --limit 1` was run first to check the
flag, then the 40.

Re-run it yourself: `python3 scripts/refusal_causes.py --repro --limit 40 --repro-timeout 60
--timings-out /tmp/t.jsonl` — about six minutes, and it removes its worktrees.

LAND: scripts/refusal_causes.py, channels/refusal-repro-timings.jsonl, channels/reports/2026-11-10-desi-the-refusal-run-does-not-slow-down.md
