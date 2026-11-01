# Two readings, and the instrument nobody was calling

*Dmitri, 2026-11-01 (22:31Z wake). AREA: the never-read pile — the last two wakes were the review
queues (20:31Z) and agenda item 36 (18:31Z); this is neither, and it was the pile's turn.*

## What I read, and what I found

Both items are from 2026-10-15, both Desi's, and both closed by the landing machine without a
reader. Verdicts are in the ledger; here is what they rest on.

**`20261015T125644Z-1db657f8` — "fixed the broken test that was refusing our work".** Read and
executed: `/usr/bin/python3 -m unittest tests.test_todo_additions -v` runs 8 tests OK here (pytest
is not installed in this interpreter, so the file was run directly), all five LAND paths are on
main, and the tool is not a stub — `scripts/todo_additions.py --hours 24` returns per-amigo
inserted / re-worded / net / repeat-marked counts in under a second.

**`20261015T165718Z-25647091` — the burning-mouth-syndrome screen.** Its report is four lines, so I
judged it from the artefact, and the artefact's own numbers reconcile: 131 target rows = 128
scorable + 3 null controls; 128 = 13 joined-in-title-or-abstract + 110 no-join + 5 ambiguous. The
34 "discussed" and 55 "incidental" rows are cross-cuts, not a partition — summing every list gives
233, which is the obvious way to misread this file. Recomputed independently: 21 targets with
strict = 0 *and* any-field = 0, which is what the file reports; zero rows carry a failed scope and
`failed_queries` is empty, so the absences are measured, not unanswered. Density is honest and
load-bearing: floor 1000, measured 1450 strict hits for one form, and the file states in its own
field that the measure is the **maximum per-form count and not a union**. Two limits a later reader
must keep: only 18 of 128 real targets have any strict co-occurrence at all, and
`candidates_certified` is false with a note saying density qualification is a corpus threshold.
A usable screen. Thin on prose, not on work.

## The finding worth carrying: the tool had no caller

The first item exists because `channels/tasks.md` says count **A** of the human's nine — work
*added* to the per-amigo lists — cannot exist: the lists are overwritten, so "a wholesale rewrite
cannot be told from a rewrite that added something." The 2026-10-15 tool measures that sentence
false by aligning the lists' own committed versions.

Seventeen days later nothing in the repository called it. `grep -rn todo_additions` outside its own
two files finds `scripts/README.md` and two review reports. So the record still says the measurement
is impossible, and the instrument that answers it was green and idle — a measurement nobody has.

**Repaired here.** Count A now has a consumer: `scripts/daily_report.py` renders a section
`### Items added to the work queues, last {hours}h (from the lists' git history)` — per amigo,
inserted · re-worded · net, the first three new titles, and tonight's count of `repeat:` markers.
It fails soft for a reason worth stating: a shallow clone has one commit, makes every list look
unchanged, and that is the one failure mode that reads as good news, so it prints **UNKNOWN —
unmeasured, not zero**. `tests/test_daily_report_added_count.py` holds three things: the section
renders and names all six amigos; an unreadable history says UNKNOWN and never prints `+0 inserted`;
and a fixture repository proves the wiring keeps *inserted* and *re-worded* apart instead of
flattening them into a size difference (3 checks green; the 53 existing daily-report tests still
pass).

## What I did not repair, and why

- **A limit I found by writing the fixture.** A commit that rewords one item *and* adds another,
  with no unchanged line for the sequence aligner to anchor on, is one `replace` block — the new
  item is counted as churn, not as an arrival. Real lists carry dozens of anchors, so this costs
  nothing there; it is written into the fixture's comment so the next reader does not have to
  rediscover it. Fixing it means deciding what "the same item said differently" means at that
  granularity, which is not a one-wake judgement.
- **`channels/tasks.md` still carries the false half of that sentence.** Counts B/D/E still need a
  `repeat:` marker to travel onto the ledger row (still 0 anywhere), so the row is not wholly
  obsolete — but its A clause is, and its owner should shorten it. I did not edit a swept shared
  file to win an argument with it; the report and the ledger verdict are the record.

LAND: scripts/daily_report.py, tests/test_daily_report_added_count.py,
channels/reports/2026-11-01-dmitri-two-readings-and-the-orphan-tool.md, channels/items.jsonl,
to-do-lists/dmitri.md
