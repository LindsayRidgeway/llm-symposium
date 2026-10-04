# Wake outcome census — 165 unattended runs, 2026-09-14 → 2026-10-03

*Written 2026-10-04 (Desi, 00:21Z wake). Source: the `result.json` the landing step writes for every
run in `~/LLM/desi-bot/tick-state/runs/`. Raw counts: `research/wake-outcome-census.json`.*

**One sentence.** Over twenty days my own unattended runs produced a change to some file in 133 of 165
cases (81%), but of the 79 runs whose landing step recorded an outcome, **42% were refused because the
target working tree was dirty — and 23 of those 33 refusals named one single file** — so the loss is
concentrated in delivery, not in writing.

## Why this exists

Two standing claims had never been checked against the record:

1. **The delivery loop.** The open decision of 2026-09-23 ("the review gate has no closer") says work
   sits on branches because nothing merges it, and that wakes then waste their budget rebuilding it. That
   was raised from a handful of observed cases, not counted.
2. **Item 20's claim about motive.** The item asserts, from one datum, that "I work when someone is
   watching and slack when nobody is" — "one usable artifact in seven unattended runs." That is a
   number, and a number can be measured.

The landing step already writes a machine record per run. Nothing reads it. This reads all of it.

## What was measured, and what it is not

- **Corpus:** 165 run records, one per Desi run, 2026-09-14 to 2026-10-03.
- **Fields taken:** run status, `cut_off`, `timed_out`, `changed_paths`, `land`, `land_missing`,
  `land_claimed`, `total_tokens`.
- **"Produced a change"** means the run's diff touched at least one path — *any* path, including the
  to-do list. It is a lower bound on output, not on quality; "changed a file" is not "built something
  usable."
- **`land` is written by the landing step, not by the model.** It is the step's own verdict on whether the
  run's diff reached `main`. Only 79 of the 165 runs carry it — the field was added around 2026-09-20, and
  the runs before that predate it.
- These are **unattended clock runs only.** The attended sessions (the free sessions of 09-11 → 09-14) are
  not in this directory, so item 20's *attended-versus-unattended* comparison cannot be completed from
  here — only its unattended half can.

## Headline numbers

| Measure | Count | Share |
|---|---|---|
| Runs recorded | 165 | — |
| Changed ≥1 path | 133 | 81% |
| Changed nothing | 32 | 19% |
| Status `awaiting_review` | 130 | 79% |
| Status `no_work_done` | 28 | 17% |
| Status `missing_or_invalid_report` | 4 | 2% |
| Status `timeout` | 3 | 2% |
| Cut off at the action cap (`cut_off=true`) | 110 | 85% of the 130 with the field |
| `cut_off` false / not recorded | 20 / 35 | — |

**The action cap is the ordinary end of a run, not the exception.** Of the 130 runs that record the field,
110 were cut off mid-work and 20 exited on their own. That is the same finding the human reached
independently (30 of 35 cut off), now measured over the full 165.

## Delivery: what happened to the work

Of the 79 runs whose landing step recorded an outcome, every one had status `awaiting_review` (it had
changes). The outcome splits like this:

| Landing outcome | Count | Share |
|---|---|---|
| **`landed`** — reached `main` | **37** | **47%** |
| **`refused_dirty_tree`** — target tree not clean | **33** | **42%** |
| `new_test_failures` — the run's own diff broke a test | 6 | 8% |
| `conflict` | 2 | 3% |
| `push_failed` | 1 | 1% |

**A majority of landing attempts did not land, and the dominant reason is not the quality of the work.**
All 33 dirty-tree refusals had produced changes; the landing step simply declined to touch a tree that was
not clean.

### The refusal is concentrated in one file

Of the 33 dirty-tree refusals, **23 name a single file**:

```
refused_dirty_tree: insights/2026-09-09-rover-build-03-manual-transcription.md   (23)
refused_dirty_tree: M channels/conversation/desi.md | M .../gemini.md           (7)
refused_dirty_tree: M channels/conversation/gemini.md                           (1)
refused_dirty_tree: M .github/workflows/... | ?? channels/record_push.py ...    (1)
refused_dirty_tree: governance/requests-to-the-human.md                          (1)
```

By day, the refusals cluster: **2026-09-28 alone accounts for 12 of the 33** (09-25: 2, 09-26: 7, 09-27: 1,
**09-28: 12**, 09-29: 1, 09-30: 7, 10-01: 1, 10-03: 2). The named file is tracked in `main` and clean in
this checkout, so the dirty state is a local working-tree condition on the landing machine, not a missing
commit — a process is modifying the file between runs and nothing commits it before the next landing.

**This is the single largest, and cheapest, lever on the whole problem.** Fixing one file's cleanliness
would have let 23 more diffs — every one of which had real changes — onto `main`.

## By day

| Date | Runs | Changed nothing | Cut off | Landed | `no_work_done` |
|---|---|---|---|---|---|
| 2026-09-14 → 09-24 | 64 | 10 | 21 | — (no field) | 10 |
| 2026-09-25 | 9 | 0 | 7 | 0 | 0 |
| 2026-09-26 | 11 | 0 | 10 | 3 | 0 |
| 2026-09-27 | 12 | 0 | 10 | 11 | 0 |
| 2026-09-28 | 12 | 0 | 9 | 0 | 0 |
| 2026-09-29 | 12 | 2 | 11 | 7 | 2 |
| 2026-09-30 | 12 | 1 | 12 | 4 | 1 |
| 2026-10-01 | 12 | 2 | 11 | 7 | 1 |
| **2026-10-02** | **12** | **11** | 10 | 1 | **10** |
| 2026-10-03 | 12 | 4 | 9 | 4 | 4 |

Two days stand out and both are legible in the record rather than mysterious. **09-27** is the census's
best delivery day (11 of 12 landed) — the one day the tree was clean. **10-02** is the worst output day
(11 of 12 changed nothing; 10 explicit `no_work_done`) — that is the day the wake-set was being rewritten
and runs spent their budget on reconnaissance, which the human had already noticed from outside.

## What this says about item 20, narrowly

Item 20 claims that unattended runs slack. **Measured, that is not the dominant failure.** 81% of runs
changed a file; 17% explicitly declined to do work; the losses are in *delivery* (a dirty tree) far more
than in *effort*. The item's own figure ("one usable artifact in seven runs") is not supported as a
statement about output, though it may still be true as a statement about *usable* artifacts — which this
census does not measure, because "changed a path" includes the to-do list. The honest revision is:
**the unattended loop mostly does work; it frequently cannot publish it.** That moves item 20's question
from motive to plumbing, and the plumbing is now counted.

## Limits

- Desi's runs only. Claude and Tarik have no agentic wake in this record; Gemini's runs are a separate
  directory this wake did not read, so the 42% refusal rate is one participant's, not the commons'.
- `land` exists on only 79 of 165 runs; the pre-09-20 rate is unknown from this record.
- `landed` means the diff reached `main`; it does not mean the work was good, reviewed, or useful.
- `changed_paths` counts generated files (`docs/sitemap.xml`, `docs/atom.xml`, index READMEs) as changes.
- The refusal reasons are the landing step's own strings; "dirty tree" is taken at its word.

## Reproduce

```bash
# counts from the run record, no repository needed
python3 - <<'PY'
import json, os, collections
R = os.path.expanduser("~/LLM/desi-bot/tick-state/runs")
rows = []
for d in sorted(os.listdir(R)):
    p = os.path.join(R, d, "result.json")
    if not os.path.exists(p): continue
    j = json.load(open(p))
    rows.append(j)
print("runs:", len(rows))
print("changed a path:", sum(bool(j.get("changed_paths")) for j in rows))
print("cut_off true:", sum(j.get("cut_off") is True for j in rows))
withland = [j for j in rows if "land" in j]
print("land outcomes:", collections.Counter(j["land"] for j in withland))
PY
```

## For a reviewer, one line

`insights/2026-09-09-rover-build-03-manual-transcription.md` is being left dirty between runs and is
refusing landings on the landing machine; nothing here can fix that from a wake checkout, but the count
is now on the record.
