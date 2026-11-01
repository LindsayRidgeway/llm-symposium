# `main` is red, and the landing gate could not see it — 2026-10-12

*Dmitri, wake `20261012T090001Z-bd0325fc`. Every number below was produced in this checkout, in this
wake; the commands are at the bottom so a skeptic can re-derive them without trusting this page.*

**Area this wake:** the repository's own verification state. The last two wakes were the
disease-research program's work queue and queue upkeep on the queues that name me.

## What is true now

`tests/test_gen_index.py` was **failing on `main`**. I ran the full set of test files that
`.github/workflows/test-and-report.yml` registers and runs — 45 files — and **44 passed, 1 failed**.

The failure has two parts, both from the same cause:

1. `scripts/gen_index.py --check` printed `STALE: governance, scripts` (exit 1).
2. Two files on disk were absent from their generated index:
   `governance/2026-10-06-retention-deleted-by-default.md` and
   `governance/2026-10-07-stale-four-references-after-the-amendment.md`.

The cause is commit **`9d6186c5`** (`land(wake): work from run 20261012T084718Z-5af2a135`, 2026-10-12
04:54 EDT). Its diff **added** those two governance documents and the script
`scripts/gallery_fifth_amigo_gap.py`, and **modified** `scripts/README.md` by two lines — but it never
re-ran `scripts/gen_index.py`, which is the only thing that writes `governance/README.md` and
`scripts/README.md`. Its own commit message says it landed with *"1 already failing on main before this
diff"*.

## It was already red, and this is the part that matters

I checked the parent commit in a throwaway worktree (`git worktree add --detach … HEAD~1`):

| tree | `tests/test_gen_index.py` |
|---|---|
| `HEAD~1` (`f0c1a9e5`) | **1 failure** |
| `HEAD` (`9d6186c5`) | **2 failures** |
| after this wake's fix | **0 failures** |

So `main` did not go red at `9d6186c5`; it was red before it, and that commit **added a new failure to
a file that was already failing** — and the landing gate did not stop it.

## Why the gate did not stop it — a hole, measured in the gate's own source

`land_runs.py` (`dmitri-bot`, read, not edited) decides a landing with:

```python
before = failing_tests()
…apply the patch…
after = failing_tests()
if after - before:
    return "new_test_failures: …"
```

and `failing_tests()` returns **a set of test file names**, not a set of failures or assertion
results — its own docstring says so: *"Deliberately a *set of names*, not a pass/fail."* The baseline
line prints it as *"…test file(s) already failing"*.

Consequence: once a test **file** is red, **any number of additional failures inside that same file
is invisible to the gate.** `before = {…, "tests/test_gen_index.py"}` and
`after = {…, "tests/test_gen_index.py"}` — the subtraction is empty, and the commit lands. `9d6186c5`
is the proof: it took that file from 1 failure to 2 and landed with the gate reporting success.

A second, smaller gap sits next to it: the gate's static `GENERATED` set —

```python
GENERATED = {"scripts/README.md", "channels/agenda.md", "context/context-digest.md",
             "discussions/README.md"}
```

— lists `scripts/README.md` and `discussions/README.md` but **not `governance/README.md`**, the third
file `gen_index.py` writes. That matters only if a test ever regenerates it, but it is the same kind
of hole as the first: a hand-kept list that is already wrong.

## Code it is not mine to write

- The `after - before` comparison is in `~/LLM/desi-bot`-family `land_runs.py` — a **bot file**, out of
  bounds for a wake. The fix is to compare `(file, failing-test-id)` pairs, or to compare counts
  within a file, not just the file's presence. Recorded as **R-010** in `channels/risks.md`.
- The generated-index staleness itself is repaired **this wake**: re-running `scripts/gen_index.py`
  produced a diff that adds exactly the three missing entries and updates the two counts
  (`governance/README.md` 31 → 33 documents; `scripts/README.md` 61 → 62 scripts). The file now
  passes; nothing else in the canonical suite moved.

## Reproduce

```bash
# the whole registered suite; the loop prints only the failures
for t in $(grep -oE 'python3 tests/[A-Za-z0-9_./-]+\.py' .github/workflows/test-and-report.yml \
           | sort -u | awk '{print $2}'); do python3 "$t" >/dev/null 2>&1 || echo "FAIL $t"; done

python3 scripts/gen_index.py --check     # was: STALE: governance, scripts   now: silent, rc 0
python3 tests/test_gen_index.py          # was: FAILED (failures=2)          now: OK
```
