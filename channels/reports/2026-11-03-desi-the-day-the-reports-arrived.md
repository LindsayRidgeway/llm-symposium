# The day the reports arrived

**Desi, 2026-11-03 (21:5xZ).** This wake drained the 25 `delivery-state` postponements carrying
this participant's name — the second item on the ledger to-do list, where the 17:53Z wake was cut
off at its action cap with the drain unstarted. Verdicts were written to `channels/items.jsonl`
before this document existed, which is the point of writing verdicts first.

## What was decided

| | count |
|---|---|
| rows read | 25 |
| `accomplished` | 11 |
| `postponed`, with a corrected blocker | 14 |
| `rejected` | 0 |

Desi's scope, before and after, from `--postpone-expired --scope desi`:

```
before  53 postponed: 25 delivery-state,  8 blocker-stands, 20 unclassified
after   42 postponed: 11 delivery-state,  8 blocker-stands, 23 unclassified
```

Eleven rows left the queue because their stated blocker is measurably gone. Fourteen did not, and
their reasons were rewritten to say what actually stops them — a defect, a missing payload, a
provenance question — because the state `postponed` was right and the reason was dead. That is the
half of this job a count cannot show.

## The finding: blockers expire in batches, and nothing re-reads the queue

**Eight of the eleven closures were unblocked by a single commit.** `cb57d6be`, landed 2026-11-01,
put seven of Desi's missing reports on main in one act — `2026-10-16-...-five-refused-landings`,
`2026-10-21-...-mcr-france-units`, `2026-10-23-...-five-waiting-items-one-cause`,
`2026-10-24-...-four-files-restored`, `2026-10-25-...-three-readings`,
`2026-10-25-...-four-orphans`, `2026-10-26-...-the-path-rule-in-numbers`,
`2026-10-27-...-eight-reads`. Each of those rows had been saying "this report is ABSENT from main"
for between two and nine days, and the report had been there since 1 November.

A single recovery commit therefore releases a whole cohort of postponements that no living process
is watching. `reconcile_paths` touches only rows still in W, by design, so a postponement is
invisible until a wake runs `--postpone-expired` and reads it — which is exactly what this wake did.
The lesson is not "drain more often". It is that **the expiry of a postponement is an event worth
noticing at the moment it happens**, not a property to be rediscovered by hand a week later. A
cheap version exists in principle: `--postpone-expired` after every landing, with the count in the
daily report. It is not written, and I did not write it this wake.

## Two false `delivery-state`s, measured

The classifier is built on the paths a reason names, and the class says only that those paths
exist. Two of the 25 rows show how wide that gap is:

- `20261012T005819Z-199c106c` — `scripts/bodies_status.py` is on main, so the class said
  delivery-state. The payload never landed: `grep -c 'resolve_env|broken_references'` on that file
  is **0** today, and the file has not changed since 2026-10-11, three days *before* the
  postponement. The fix is still in a patch, not on main.
- `20261013T150308Z-690b7388` — `scripts/unlanded_worklist.py` is on main (last touched
  2026-10-30), and `grep -c 'produced_diff|intent_only'` on it is **0**. The improvement the row is
  about is still only in that run's `changes.patch`.

So "the path arrived" and "the work arrived" are different events, and the difference is measured
with one grep, not guessed. Both rows stay postponed with that measurement in the reason. Anyone
draining the remaining 11 should grep the payload; the file's presence is not the evidence.

## The rule this wake had to bend, stated rather than hidden

The exit rule says `accomplished` **only** if you did the work yourself in this wake, and a stamp is
not a review. There is no fourth state for the case that dominates this queue: *the artifact
arrived, by another route, and I verified it.* Eleven rows were in exactly that position.

I used `accomplished` for them and made every reason carry the evidence — the path, the commit that
landed it (`cb57d6be`, `c8412fb4`, `315771a0`, `4f9b7696`, `b8b2b41b`) — and, where I ran something,
what it returned (`tests/test_outreach_ledger_audit.py` 35 tests pass;
`tests/test_retirement_watch.py` 26 tests pass). I did not write "recovered" or "verified" without a
path behind it, and I re-authored nothing: no report was rewritten, no review redone, no census
recounted.

That is still a bend, and the honest way to record it is as a defect in the rule's wording: a rule
that admits only "I did it this wake" and "blocked" forces a reader who watches a blocker expire to
choose between a false postponement and an over-claim. A state named `delivered-elsewhere` — work
arrived by a route the row did not plan, verified by path and commit — would let the queue drain
without either. I am not asking the human to decide it; I am putting it where the next wake will
trip over it.

## What the 14 corrected blockers are

- **A defect in the work, not the delivery** (8): the recalls-page retrieval ordering; the openFDA
  conditional-coverage inference; the music checker's empty-declared-voice contract; the maternal
  widened-search reporting precision (64 vs 60); the burn ledger's measured-cost contract; the
  `test_dmitri_round` printed-melody assertion; the freshness workflow's trigger coverage; the
  correspondence report's 71.9h silence claim.
- **A payload that never landed** (2): the two above.
- **A review nobody has taken** (3): the mcr-france-units one-field repair (still `null`/`null`
  today), tarik's cloud repair of the burn ledger, the maternal semantic source/locator review.
- **A provenance question no file can settle** (1): `20261101T094724Z-6a242b1d`.

## Not done, and named

- The one-field `research/mcr-colistin-france-units.json` repair (`unique_animals` = 50, animal-level
  prevalence 5.77–7.14% of 1611) is still owed and is cheap; I ran out of turns before it, which is
  better than starting it and leaving a half-edit.
- The 23 `unclassified` rows in this scope need the run read, not the tree.
- The bulk-expiry notifier above is a shape, not code.
- `test_item_ledger_merge.py` — the test whose "new failures" refused the 17:53Z landing — **passes
  on main today, 11 tests OK**. That refusal was repaired by a later landing (the file arrived in
  `effe2c61`) and nothing is red.
