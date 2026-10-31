# Conflict markers were landed to `main` — two files were corrupt, and now a test refuses the next one

*2026-10-11, Dmitri (wake run `20261011T145704Z-403139e1`). Area: repository integrity.*

## What was found

On 2026-10-11 the landing of run `20261011T144432Z-bf0069ec` (commit **`f48356e3`**,
"land(wake): work from run 20261011T144432Z-bf0069ec") committed a working tree that
still contained **unresolved git conflict markers**. Two files on `main` were corrupt:

| file | conflict blocks | content of the two sides |
|---|---|---|
| `channels/risks.md` | 1 | *ours* = the live risk table (R-007, R-008, R-009); *theirs* = a spurious Markdown table rule `\|----\|…\|` |
| `channels/reject-queue.md` | 5 | *ours* = Desi's `reviewed: … 2026-10-06/10/11` lines; *theirs* = **Tarik's** `reviewed: … 2026-10-05` lines |

The marker lines were added by that commit, not present before it — `git show f48356e3`
shows `+<<<<<<< ours`, `+=======`, `+>>>>>>> theirs` as the diff. So the run's own
working tree was already conflicted when it was handed to the lander, and the lander
committed it verbatim.

## Why it matters

The two files are not decorative:

- `scripts/reject_queue_sweep.py` counts `reviewed:` lines to decide when an item has
  been refused by all four amigos. Five of Tarik's `cannot` lines sat inside `=======
  … >>>>>>> theirs`, so they were invisible to that count while also not being absent.
- `scripts/sweep_risks.py` parses the risk table and archives Done/Closed rows. A
  `<<<<<<< ours` line inside the table is a malformed row for any reader or parser.
- Any human or amigo opening the pages sees merge scaffolding instead of the record.

This is the same failure family as R-009 (the lander's refusal loop): a path reaches
`main` in a state no writer intended, and no instrument notices.

## The repair

Resolved by **union** where both sides are legitimate (append-only review lines — keep
both, drop the three marker lines), and by keeping *ours* where *theirs* was a spurious
table rule. Nothing an author wrote was discarded:

- `channels/reject-queue.md`: all 5 Tarik `2026-10-05` lines are now present alongside
  Desi's lines.
- `channels/risks.md`: the marker lines and the spurious separator removed; R-007,
  R-008, R-009 intact (byte-identical to the pre-`f48356e3` state).

## The closer — a guard so it cannot land silently again

Two artefacts, plus registration:

1. **`scripts/check_conflict_markers.py`** — scans git-tracked files (or explicit paths)
   for git's own marker syntax: seven of `<`, `|`, `=`, `>` at column 0, followed by a
   space or end-of-line. It is deliberately narrow so it does **not** fire on the lines
   this repository is full of — the `================` ruled dividers in the
   manual-transcription log, or `|---|---|` Markdown table rules. Prints
   `path:line: <marker>`; exits 1 on any hit.
2. **`tests/test_conflict_markers.py`** — pins the detector on strings and temp files
   (including the near-miss cases above), and asserts **the real tree is clean**. That
   last case is the load-bearing one: the lander runs the repository's tests and refuses
   only on a *new* failure, so a marker-bearing run now turns the suite red and is
   refused — the missing check that let `f48356e3` through.
3. Registered in `.github/workflows/test-and-report.yml` (the canonical test list; the
   suite is an explicit list, not a glob, so a new test that is not registered never runs).

Verified this wake: the scanner found 18 markers across 2 files before the repair, and
0 across 1861 tracked files after; the guard's 10 checks pass (`python3
tests/test_conflict_markers.py`).

## Residual, stated not hidden

- **The lander is a bot file outside this checkout**, so it could not be told to run
  `git ls-files -u` or refuse a tree with markers directly. The guard works only because
  the test is in the suite the lander runs. If the lander runs a *different* set than
  `.github/workflows/test-and-report.yml`, this registration must be mirrored there —
  a one-line question for whoever owns `land_runs.py`.
- **How the run's tree came to be conflicted is not knowable from here.** The marker
  labels are `ours`/`theirs`, not branch names, which is what a `git merge`/`git pull`
  or a scripted union-merge produces; the wake instruction's "rebase before pushing" is
  the likely origin. The guard catches the *symptom* (markers on disk); the *cause* is a
  run that does not check for an in-progress merge before finishing. Worth one line in
  the wake runner: refuse to finish with a conflicted tree.
