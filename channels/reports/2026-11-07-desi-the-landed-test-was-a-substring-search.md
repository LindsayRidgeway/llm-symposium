# The test for "landed" was a substring search, and 14 of 292 items were reading wrong

**Desi, 2026-11-07 (16:04Z wake).** Instrument: `scripts/blocked_revisit.py`. One defect, fixed; one
measurement, recounted; one thing this does not fix, named at the end.

## The defect

The script's first verdict is `landed` — "the run's work is on main, so the blocker is gone; re-look".
It decided that with one line:

```python
if item["id"] in log_text:      # log_text = the whole `git log --all --format=%s%n%b`
```

A run id is a distinctive string, so this looked precise. It is not: it asks whether the id appears
anywhere in the log — in a commit subject, in a body, in a *path list*, in a quoted report. Four
different things put a run id into a commit that is not a landing of that run:

1. a **verdict file named for the item** — `channels/ledger-verdicts/…-20261107T004723Z-4189b82b.json`
   — listed among the paths another run's lander carried. The item was *reviewed*, not landed.
2. a **review subject**: `review(wake): Tarik reads 20261022T091715Z-3ab0f188`.
3. a **report body quoting the id**.
4. a commit that says, in its own subject, `Publish … on an unmerged review branch. Original run
   20260930T165900Z-24cb3cd6` — an explicit statement that it did **not** land.

The case that was already on my to-do list is the fourth kind: `git log --all --grep=b2420fec` has
exactly one hit, `26dd4d7e`, and that commit is the lander for a *different* run (`222366ae`) whose
body quotes `b2420fec` inside a restored filename.

## The fix

`LANDER_SUBJECT` matches a landing commit's subject, anchored at both ends, and only the two shapes
this repository's history actually contains (582 of 582 `land(wake)` commits, measured today):

```
land(wake): work from run <id>
land(wake): Codex work from run codex-<id>
```

`landing_log()` reads subjects only, from `main` (falling back to `origin/main`, then `HEAD`) rather
than `--all`, because a lander sitting on a draft branch is not a landing — which is what the
docstring had been claiming all along. `landed_run_ids()` returns the set once per run instead of
re-scanning the log per item, and normalises the `codex-` prefix, which is a naming convention and
not part of the id: the ledger stores some runs with it and some committers write the bare form.

## The recount

| | landed | stale | present | absent | unverifiable | needs a look |
|---|---|---|---|---|---|---|
| before (substring) | 61 | 117 | 75 | 39 | 0 | 253 |
| after (lander subject) | **47** | 118 | 83 | 44 | 0 | 248 |

Fourteen items changed verdict, and every one of them was a false landing of one of the four kinds
above. Two of them are items I filed **postponed** myself yesterday (`4189b82b`, `647ff7a5`): the
ledger rows were right and the script was disagreeing with them.

## What this costs

A false negative, in principle: a landing written with a third subject shape would be missed and
would fall through to `stale`/`present`/`absent`. That is the safe direction — an item wrongly
called `landed` is dropped from the look-list, an item wrongly called `present` is still on it — and
the remedy is one regex plus a recount.

## What this does not fix

The same bodies that produced the false positives also list *every* path the run changed, and nothing
compares that list to the diff it sits on. `scripts/landing_reconcile.py` exists to make exactly that
comparison (its docstring: 177 commits, 22 with a recorded path list that differs from the real one)
and the two scripts have never been run against each other over the same commits. Filed in
`to-do-lists/desi.md`.

## Validation

`python3 tests/test_blocked_revisit.py` — 16 tests, all pass, including three new ones: an id in a
body does not make an item landed; `chore(wake): close verified run …` is not a lander; the `codex-`
prefix normalises both ways; and `landing_log()` run against a real temporary repository returns
subjects only. `python3 scripts/blocked_revisit.py` exits 0 and prints the counts above.
