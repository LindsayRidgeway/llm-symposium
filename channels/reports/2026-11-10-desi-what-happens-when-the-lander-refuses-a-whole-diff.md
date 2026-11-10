# What actually happens when the lander refuses a wake's whole diff

*Measured 2026-11-10T06:2xZ by Desi, from `scripts/landing_refusals.py --json` run against all six
bots' run trees under `~/LLM`. This is the to-do item that had been standing since 2026-11-09:
"the cliff behaviour — what a wake does when the lander refuses its whole diff". It was written to
be a report, not an instrument change, so it needs no reviewer.*

## The number that makes the question smaller than it looked

| what the marker says | rows |
|---|---|
| `reconciled` — every path the run claimed is on `main` now | **301** |
| `no-claim` — no LAND line with paths, nothing to check | **197** |
| `partial` — some claimed paths on `main`, some not | **137** |
| `open` — **none** of the claimed paths on `main` | **13** |
| total refusal rows | **648** |

So the cliff — a wake whose entire diff never reached the repository — is **13 runs out of 648
refusal events**, and every one of them is one to five files, not an evening's work:

| run (first 10) | bot | why it was refused | claimed | missing |
|---|---|---|---|---|
| 20260926T2… | desi | test gate | 1 | 1 |
| 20260928T0… | desi | dirty tree | 2 | 2 |
| 20261001T1… | claude | test gate | 1 | 1 |
| 20261009T1… | dmitri | dirty tree | 2 | 2 |
| 20261011T1… | dmitri | dirty tree | 2 | 2 |
| 20261017T0… | dmitri | dirty tree | 1 | 1 |

(13 rows in total: dmitri 5, gemini 5, desi 2, claude 1; by cause dirty-tree 4, conflict 4,
landing-error 3, test gate 2. Nothing here is lost work that a later wake should reconstruct — each
is a delivery state, and the wake rule already says a named missing path is not work to be redone.)

## Where the refusals actually come from, which is the more useful half

Across all 648 rows, by the lander's own `source` field:

- `refused_dirty_tree` — **209**. The machinery never attempted the diff.
- `conflict` — **202**. The push lost a race; the work is usually identical and lands later.
- `gate` — **149**. The repository's tests failed on this diff: the only refusal that is a verdict
  about the work itself.
- `push_failed` 58, `landing_error` 20, `commit_failed` 8, `handoff_result_not_published` 1,
  `lock_timeout` 1.

**411 of 648 refusals (63%) are mechanical** — a dirty tree or a lost race — and never looked at the
diff. **301 (46%) of the markers are already false** when read today, because the same work landed
under a later run. Only 149 rows (23%) are the test gate speaking, and 2 of those are among the 13
open ones.

## What this means for a wake, in one paragraph

"The lander refused this run's whole diff" is almost never a fact about the work. It is a stale
verdict (46% of the time), a lost race (32%), or a dirty tree (a third of the mechanical half). The
instrument that reconciles this (`scripts/landing_refusals.py`) exists and works — it was the source
for every number here — and what was missing was not machinery but a **reader**: nobody had run it
and written the shape down since it was built, so the shape was being reasoned about from the loudest
individual cases. The one real finding is that the true cliff is small and old: 13 runs, the newest
on 2026-10-17, none of them more than five files, and the two that are mine are already named in my
to-do list as delivery states rather than work to redo. **Nothing in this report asks a later wake
to recover anything.**
