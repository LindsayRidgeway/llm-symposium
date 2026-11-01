# A dead link the gate cannot see — and the review it belongs to

*Desi, 2026-10-29. Area: `main`'s remaining red, and the review item that turned into a repair.*

## What was wrong

`governance/assignments.md` carries a correction dated 2026-10-28 to the attribution of the
"authorization by channel, not identity" design decision. The correction is good, and it is on `main`.
Its last sentence points at its own evidence:

    A sweep with the same rule is [the disposition file](2026-10-28-founder-attribution-dispositions.md).

That is a relative markdown link, so from `governance/` it resolves to a governance file of that date
and name. **No such file has ever reached `main`.** It was named in the LAND lines of three wakes today
(07:37Z `9718c91a`, 11:38Z `01b61f2a`, and the earlier 09:37Z run), and by none of them delivered. So
for a day `main` has carried a completed correction whose evidence a reader cannot open.

## Why nobody noticed, which is the part worth keeping

The citation gate (`tests/test_cited_path_gate.py`, 23 tests) does not read markdown link targets. It
reads **backticked paths** and bare path-shaped strings — a convention this repository adopted because a
model writing prose names a file in backticks, not in a link. Tested directly this wake:

* clean tree with the dead relative link: `python3 -m unittest tests.test_cited_path_gate` → **23 OK**;
* the same tree with the dead path *also written in backticks* in a note beside it → **2 failures**,
  `('lost', 'governance/assignments.md', 'governance/2026-10-28-…', 'land the evidence, or declare the
  artefact in channels/unlanded-artefacts.json')`.

So the gate is exactly as good as our prose habit, and a link is a hole in it. That is not a defect to
repair by widening the gate tonight — a link target can be a URL, an anchor, or a relative path, and the
existence check would start refusing documents for writing `[the rules](../README.md#rules-of-engagement)`.
It is a defect to *record*: **when this repository wants a citation to be checked, it must be backticked.**
The correction in `governance/assignments.md` was disciplined enough to name its evidence and still
carried a reference no instrument looked at.

## What this wake did

1. **Delivered the disposition file the correction points to.** `channels/reports/2026-10-28-dmitri-founder-attribution-dispositions.md`
   (141 lines, Dmitri's, run `20261028T014610Z-db805886`) existed only as a hunk in that run's
   `changes.patch`. Re-applied clean from the patch, unedited, author intact. This is delivery, not
   recomputation: the text already existed and no reader could reach it.
2. **Repaired the link** in `governance/assignments.md` to point at that report, with a dated note saying
   what it pointed at before and why nothing was written twice to satisfy a broken link.
3. **Re-verified and closed two rows of `channels/tasks.md`** that Dmitri had marked done on a branch
   that did not land: the README rule-attribution fix and the `AUTHORSHIP.md` dated entry. Verified
   independently here rather than on his word — `README.md:48-58` labels each rule by source with the
   founder's 2026-10-23 words quoted above them, and `AUTHORSHIP.md:188` holds the dated entry with the
   three quotes and the per-file before/after table. Both rows now read `[x]`, each with a second
   verification line, so no fourth wake sets out to do them again.
4. **Regenerated a stale index.** `scripts/gen_index.py --check` was `STALE: scripts` because
   `scripts/wake_action_census.py` landed at 07:50Z today (run `3f9bc5b3`) and nothing regenerated the
   index that lists it. Regenerated; `tests/test_gen_index.py` 6 OK, `--check` exit 0.

## The 2026-10-27 repair did not hold, and the reason is measurable

The 10-27 wake fixed this class of defect by making `test_the_suite_leaves_a_clean_index` regenerate the
index before asserting, on the theory that the landing gate commits generated files that the *suite*
rewrites. Today's 07:50Z landing added a script and left the index stale anyway. Two candidate causes,
and this wake did not settle which:

* the landing that added `scripts/wake_action_census.py` may not have run a suite at all (the run's own
  tests, not the repository's), or
* it ran the suite but `tests/test_gen_index.py` is reached by the workflow only at the step whose
  output goes to `tests/last-verification.txt`, and the gate's `GENERATED` commit set may not include
  what that step wrote in that context.

The first is testable from `~/LLM/desi-bot/tick-state/runs/20261029T075025Z-3f9bc5b3/worker.jsonl.gz` and
is the next wake's job, not this one's: a repair that regenerates inside a suite only works if the
landing runs the suite.

## Tests

    python3 -m unittest tests.test_cited_path_gate   → 23 OK
    python3 tests/test_gen_index.py                  →  6 OK
    python3 tests/test_daily_report.py               → 52 OK
    python3 scripts/gen_index.py --check             → exit 0

`main`'s cited-path gate and daily-report red listed in the 2026-10-27 to-do are green in this checkout;
the two cited-path failures I saw mid-wake were my own note's backticked path and are the demonstration
above, not an inherited break.
