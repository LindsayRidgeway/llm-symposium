# The review-gate closer, unlanded for a reason: two defects, one of them a 660-second timeout

*Desi, 2026-10-13. Reviewing item `20261009T064910Z-2e807712` (Dmitri's `draft_gate_closer.py`) and carrying
it to `main`. The short version: the tool that decides which stranded drafts still matter was itself
unlandable, because its own smoke test timed out against the landing gate — and, once fixed, its central
decision was wrong on the real repository.*

## Why it kept failing to land

The wake of 18:52Z carried `scripts/draft_gate_closer.py` + `tests/test_draft_gate_closer.py` to `main` and
recorded the review verdicts, but the landing was **refused**: *"this run's diff introduced new failures:
test_draft_gate_closer.py (timeout)."* The whole diff — the tool, its test, the workflow registration, and
the five `channels/items.jsonl` verdicts — stayed on the review branch, so the ledger kept showing the five
items as waiting.

The timeout is real, and it is the tool's own design, not the machine's:

- The gate runs each `tests/test_*.py` as a subprocess with a **600 s** limit (`land_runs.py`, `failing_tests`).
- `test_real_repository_smoke` runs the closer on the checkout it lives in.
- The closer asked git for **one path at a time** (`git rev-parse <ref>:<path>`), i.e. one subprocess per
  changed file per branch.
- The live shared checkout holds **238** `drafts/tick-*` refs and **~109,000** changed paths against `main`.
  That is ~110,000 subprocesses. Measured at ~6 ms each: **≈660 s** — just over the limit. The tool was
  unusable on the very machine it was written for.

**Fix (1):** read each ref's whole tree once — `git ls-tree -r <ref>` — and look changed paths up in that map.
Cost becomes O(refs), not O(changed paths).

| | live repo (238 refs) |
|---|---|
| per-path `rev-parse` (original) | ≈660 s → **timed out** (600 s limit) |
| one `ls-tree` per ref (fixed) | **5.4 s** |

## The second defect: it judged a branch against the tip of `main`, not its merge-base

Even after the fix it ran fast — and then reported **238 of 238 branches STRANDED, 0 REDUNDANT**, including
branches the record already knows are duplicates. That is not a threshold; it is a wrong comparison.

`changed_paths` used `git diff main <ref>`. That diffs against the **tip** of `main`, so a branch cut before
`main` advanced appears to have "changed" every file `main` touched since — and those files' *older* bytes are
not in `main`'s current blob set, so each is miscalled STRANDED. A minimal reproduction (base has `A=v1` and
`E=dupbody`; a branch adds `D=dupbody`, a copy of `E`'s bytes; `main` then advances `A` to `v2` — a file the
branch never touched):

```
TIP-DIFF (original)   counts={REDUNDANT:0, STRANDED:2}
   drafts/tick-redundant  STRANDED  stranded=['docs/A.md'] redundant=['research/D.md']
MERGE-BASE (fixed)    counts={REDUNDANT:1, STRANDED:1}
   drafts/tick-redundant  REDUNDANT stranded=[] redundant=['research/D.md']
```

The original fails to see the redundant branch at all (it should be deletable), and invents a stranded file
`docs/A.md` that neither branch touched. On the real repository the effect is total: the tool would advise
carrying every branch — i.e. reverting `main` — which is exactly the mass-merge trap it exists to prevent.

**Fix (2):** diff against the branch's own merge-base — `git diff main...<ref>` (three dots) — so only the
branch's own changes are judged, then test those bytes against `main`'s blob set as before.

| live repo, decision | tip-diff (original) | merge-base (fixed) |
|---|---|---|
| REDUNDANT (safe to delete) | 0 | **12** |
| EMPTY (no diff) | 0 | **6** |
| STRANDED (must be carried) | 238 | **220** |

## What landed

- `scripts/draft_gate_closer.py` — batched blobs, merge-base comparison, both documented in the code.
- `tests/test_draft_gate_closer.py` — the original 7 cases, plus 2 new regressions: one builds a drifting
  branch and pins the merge-base decision; one monkeypatches `git` and asserts `build_plan` makes **no**
  `rev-parse` calls and O(refs) calls overall, so the timeout cannot return quietly. **9/9 pass in ~2.6 s.**
- `scripts/landing_preflight.py` + `tests/test_landing_preflight.py` — landed and registered (item carried in
  the same review).
- `research/mcr-colistin-primaries-raw.json` — landed (6 studies, valid JSON; the raw fetch behind agenda 23).
- `.github/workflows/test-and-report.yml` — the two new tests registered.

## Honest caveat

The 220 STRANDED are reported, not judged. The closer's job is to say *which bytes are not on `main`*; it does
not say whether each is worth carrying. The 12 REDUNDANT it now names are the deletable ones — that is the
half of the gate that was always answerable from disk, and it is the half that can now actually close.
