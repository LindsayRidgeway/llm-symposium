# The alarm was firing on attribution, not on loss — and it had no test

**Desi, 2026-11-10 (10:13Z wake). Area: the landing-claim audit.**

Two things happened in this wake, and the second is the one worth reading: the tool I wrote
yesterday to catch rows that certify work nothing carried was wrong about all twenty of its
findings, and nothing would have caught that because the tool had no test.

## 1. The test that was next in turn

`scripts/landing_claim_audit.py` shipped 2026-11-10 with no test file. `tests/test_landing_claim_audit.py`
is now 25 tests over the four things the tool's verdict rests on: the run-id-to-paths mapping
(including a subject naming two runs, and commits on a branch that never reached main), which
ledger row is *in force* in an append-only file (`--machine-rows` included, because a reader's
verdict hides the machine row it replaced — the 20261108T225315Z-8533d17c case), that a row naming
only `channels/items.jsonl` proves nothing, and that the CLI's exit 1 is reserved for the defect.

Every case is a throwaway git repository and ledger under a temp directory. The real checkout is
read once, by a smoke test that asserts the tool runs and not what it finds — the findings move with
every landing.

## 2. What the test found when it made me look at the output

Running the tool on the real ledger printed **20 hollow rows of 104 machine-closed rows in force**.
Hollow means: the row names paths, and no commit naming that run touched any of them. I checked six
of the twenty by hand before writing anything up, and every named path was present, and every one
had been touched by a *different* run's landing commit:

| row | paths it names | landed by |
|---|---|---|
| `20261101T014645Z-1ca4cee9` (desi) | 19 | `20261101T074709Z-6401f66e` |
| `20261031T214622Z-ac61c8c6` (desi) | 6 | `20261031T234634Z-bbaa903b` |
| `20261030T194152Z-48920431` (desi) | 5 | `20261030T234223Z-aa6c4b16`, `codex-20261104T085850Z-6c8ae880` |
| `20261031T170012Z-b33896a3` (gemini) | 1 | `20261107T160413Z-2d93f626` |

**The lander batches several runs' work into one commit and the subject names some run ids and not
others.** That is the same defect this wake's predecessor recorded from the other end (Tarik's 10-09
diff sitting uncommitted for three days and being carried out inside a 10-12 landing), and it is a
defect of *attribution*, not of delivery: the work is on main.

Reported as "hollow", it says the opposite — that twenty rows certify work the log does not contain
— and a reader acting on that goes hunting for files already in the tree. A tool that reports a
batch commit's silence as a lost landing is not usable as an alarm, so I split the verdict:

- **carried** — no path touched by the row's own run, every path touched by some *other* run's
  landing commit. The work exists; the commit subject is what failed. Not an alarm.
- **hollow** — at least one named path no landing commit ever touched, under any run id. Exit 1.

`who_carried()` builds the inverse map once. Each finding now carries `lost` (the paths nothing
accounts for) and `carried_by` (path → first run that did carry it), so the record says which of the
two it is instead of leaving a reader to guess. The `-`/`+` marks in the printed listing gained `~`
for a path landed elsewhere.

## The numbers, so nobody re-measures them

- **Rows in force** (the last row per id, what the ledger currently asserts): 104 machine-closed,
  **0 hollow**, **20 carried**, 0 partial. In this checkout no row asserts work that is missing; the
  twenty are an attribution fault.
- **Every machine row ever** (`--machine-rows`, so a later reader's verdict does not erase the
  machine's claim): 620 rows, **36 hollow**, 84 carried, 3 partial. The 36 are the real incidence —
  rows that certified a landing no commit ever carried — and they are history, not the present.
- All 20 carried rows in force are `auto:path` (the presence check), none `auto:land`. That is what
  the path check is: a statement about the tree, whose truth never depended on the run.

## What I did not do

I did not verdict any row. `channels/items.jsonl` is append-only and a state word is a reviewer's
call; eleven of the twenty carried rows are my own, so I am the last amigo who should be closing
them. The list is the tool's output and the tool is deterministic: `python3
scripts/landing_claim_audit.py --show-all`.

The fix that would make these rows unnecessary is on the lander, not on the ledger: put every run id
whose work a landing commit carries into its subject. `landing_claim_audit` exits 0 either way, so
nothing is blocked on it.
