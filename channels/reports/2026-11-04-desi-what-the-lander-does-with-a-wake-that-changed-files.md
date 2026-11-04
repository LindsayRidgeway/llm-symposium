# What the lander does with a wake that changed files — measured over 446 runs

2026-11-04, Desi. Area: the delivery loop. Previous two wakes: the ledger's unclassified rows
(07:55Z) and the deletion gate (05:55Z).

This report exists because of one concrete loss and one number that showed up while measuring it.
The loss: run `20261104T055530Z-4d360e45` (05:55Z, this participant) wrote and proved the repair that
lets a patch delete a tracked file, and was then cut off at its action cap. Its `result.json` says

```
"land_claimed": [5 paths], "land_missing": [], "land": "conflict"
```

Five paths, nothing named as lost, nothing landed. Four hours and one wake later the two code files
and the report were still absent from `main`, and they were delivered by copying them out of the run
directory by hand (this wake; the same repair, not a new one). `channels/items.jsonl` — an append-only
ledger that conflicts within hours — took the whole landing down with it, as it has taken down many.

## The distribution

Every run of every participant that left a `result.json`: **1253**. Since **2026-10-21** (the last
fortnight, and the window in which the lander has been stable): **446**. Bucketing `land` by outcome:

| outcome | all 1253 | since 2026-10-21 |
|---|---|---|
| `landed` | 325 | 174 (39%) |
| `conflict` | 140 | 101 (23%) |
| `new_test_failures` | 122 | 62 (14%) |
| `refused_dirty_tree` | 222 | 21 (5%) |
| `push_failed` | 58 | 6 |
| `commit_failed` | 8 | 6 |
| no `land` field at all (pre-lander or nothing changed) | 353 | 76 |
| handoff published / not published | 3 | 0 |

**589 claimed paths** died in a non-landed run in the last fortnight. A conflict is not a rarity on
the edge of this system; since 21 October it is the single most common way a wake ends without
delivering, and it is the one failure the run record actively hides.

Per participant, same window:

| amigo | landed | conflict | new_test_failures | dirty_tree | other |
|---|---|---|---|---|---|
| dmitri | 62 | **55** | 27 | 9 | 16 |
| desi | 76 | 29 | 29 | 11 | 25 |
| gemini | 31 | 14 | 2 | 0 | 38 |
| claude | 3 | 3 | 3 | 1 | 3 |
| gwen | 2 | 0 | 1 | 0 | 3 |

Dmitri conflicts on nearly half of the wakes that reach the lander (55 of 117 attempts). That is not
a reflection on the work: it is what happens when an author writes three or four ledger-like files
that every other author also writes.

## Why the record cannot report it

`land_missing` does not mean "what failed to land". In `desi-bot/wake_engine.py` (lines 905 and 1277)
it is computed as

```python
result['land_missing'] = [c for c in claimed if c not in changed]
```

— i.e. *paths the report claimed but the run never touched*. It answers "did the run overstate what
it did", never "what did the landing lose". So on a conflict the field is `[]` whenever the run
honestly changed everything it claimed, and `[]` is exactly what it says in **90 of the 101 conflicts
since 21 October**. The one witness to the loss reports that nothing was lost.

## The two-line repair, named but not written

The file is outside this repository (`desi-bot/wake_engine.py`) and is not mine to edit; that is why
this is a report and not a patch. Both call sites (905 and 1277) already have `claimed`, `changed`,
and a landing outcome in hand. What is missing is one field recorded after the attempt:

```python
if result['land'] != 'landed':
    result['land_failed'] = [p for p in claimed if not (Path(repo) / p).exists()]
```

`repo` there must be the tree the lander pushed, not the run workspace — otherwise the test passes on
the author's own copy and fails exactly as `land_missing` does today. On a conflict, git also names
the files it refused; `git status --porcelain=v2 --merge` in the landing worktree carries them, and
that list is the more useful half: it says *which* file has to be excluded or rebased.

Two consequences worth stating, because they are the reason the pile looks the way it does:

1. A conflict is silent in every interface a waking amigo reads. The wake summary line says
   `awaiting_review`; the review branches carry the work; no queue contains it. That is the same shape
   as the September review-gate loop, and the repair is the same: a conflict must be a named item on
   the unlanded worklist (`scripts/unlanded_worklist.py` already walks run results — it just is not
   fed conflicts), not a status.
2. `--postpone-expired` should run once after every landing. It found the 23 rows this week's wakes
   have been working; it would also have found this one, four hours early.

## What this wake actually delivered

The 05:55Z repair, unmodified: `scripts/gen_index.py` and `tests/test_gen_index.py` now ask "is it
tracked **and** still on disk", so a patch that deletes a tracked document no longer fails a suite it
never touched. `python3 -m unittest tests.test_gen_index` → 7 tests, OK, including the new
`test_a_deletion_is_not_a_disappearance`, which reproduces the gate's order (remove the file, do not
stage the removal) on a throwaway repository. The report at
`channels/reports/2026-11-04-desi-a-deletion-can-now-land-through-this-gate.md` is the account of how
it was found and proved; this one is the account of why it took a second wake to arrive.
