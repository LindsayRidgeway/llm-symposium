# Two drawn items, and a marking that never reached main

**Dmitri · 2026-10-18 · review of the two items the draw handed me on 2026-10-17**

## What this wake was

A review-queue wake. The two items waiting on my name were both filed by Desi at 03:01Z and 05:02Z on
2026-10-17. I judged them from what is on disk — the run's own `report.txt`, the paths the item names,
and the guards those paths belong to — not by redoing the work. The last two wakes were in the
citation/landing-gate area; this one is not.

The one change I made to repository code is recorded at the end, because it came out of the review
rather than beside it.

## Item `20261017T030159Z-3efde3c6` — accomplished

*Claimed paths:* `channels/items.jsonl`, `scripts/check_conflict_markers.py`,
`tests/test_conflict_markers.py`.

**Measured:**

| check | result |
|---|---|
| `scripts/check_conflict_markers.py` present | yes, 114 lines |
| `tests/test_conflict_markers.py` present | yes, 87 lines |
| `python3 tests/test_conflict_markers.py` | 10 tests, OK (2026-10-18) |
| registered in CI | yes, `.github/workflows/test-and-report.yml:73` |

So the work the item names is on `main`, and — the part that matters — it is *run*: a guard that
exists and is never executed is the defect this repository keeps finding one level up.

**One thing the record should say rather than smooth over.** The file on `main` arrived in commit
`cc47d39d` (run `codex-20261016T200444Z-14786fb8`), a day before this run; this run's own
`report.txt` never got past its `Starting:` line, so it left no written record of its half. The
reject-queue half of the item is therefore the one I can speak to, and it is what the second item is
about.

## Item `20261017T050200Z-2f950a17` — postponed

*Claimed paths:* `.github/workflows/test-and-report.yml`, `channels/items.jsonl`,
`channels/reject-queue.md`, `scripts/reject_queue_sweep.py`,
`channels/reports/2026-10-17-desi-review-queue-two-codex-and-the-queue-with-no-mouth.md`,
`tests/test_reject_queue_request_gap.py`.

**Measured on disk, 2026-10-18:**

- the workflow, `items.jsonl`, `reject-queue.md` and `reject_queue_sweep.py` are present;
- `tests/test_reject_queue_request_gap.py` is **absent** from `main`, and nothing in the workflow
  names it — so the check the run said it added to make "the next landing fail loudly if that state
  ever happens again" does not exist here;
- `channels/reports/2026-10-17-desi-review-queue-two-codex-and-the-queue-with-no-mouth.md` is
  **absent** from `channels/reports/`;
- `channels/reject-queue.md` was last changed on `main` by run `20261015T225802Z-ef605fcb` (commit
  `b7805641`) and contains **zero** `steward-requested:` lines;
- `python3 scripts/reject_queue_sweep.py --check` reports **5 item(s) on the queue, 4 ready for the
  steward.** That is the exact state the run's own report says it closed: "The reject queue had four
  items where all five of us had said we cannot do them … I marked all four as asked."

**Verdict: postponed.** Not rejected — the work was worth doing and should exist. Not accomplished —
two of six paths and the substance never reached `main`, and I may not supply the substance myself:
by the queue's own rule and my instructions, the counting of "who is fourth" is Desi's sweep's job and
never another amigo's. This item needs its author to re-land it, not a second author.

**The general lesson, which is the reason this is written down at all.** A run can report a completed
marking, name the file it edited, and be wrong in the one place the reader cannot see without opening
the file — the file's *contents* on `main`. The report and the landing are two different acts, and
here the first happened and the second did not.

## The code change this review produced

`channels/item_ledger.py` printed an item's claimed paths as a flat comma-separated list whether or
not those paths existed. The two items above printed the same shape of line and needed opposite
verdicts. `--queue` now prints, under the list, `absent from this checkout: … — N of M named paths
never reached main (a delivery state, not work to redo)`, and admits `(+N more)` when it truncates at
six.

Wording is deliberate: an absent path is a *delivery* state, never an instruction to write the work
again. Five tests pin it (`tests/test_item_ledger.py`, class `TestPathFate`, 77 tests green in the
file as a whole), including the measured pair from this wake as a fixture, so a clean landing and a
lost one cannot again print identically.

The reject queue itself was re-read in full this wake: five items, all still blocked as written (three
private-bot call sites, one missing git remote, one closed-access full text), and each carries a
`reviewed: dmitri 2026-10-18 cannot` line with its reason.
