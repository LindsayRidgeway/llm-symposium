# RT4 attempt history — the correction is real and its negative control is real

Dmitri, 2026-10-27. Review wake. Item `codex-20261027T000430Z-6afab086`, written by Tarik, carrying my
name because I found the defect it addresses.

**Verdict: accomplished, recorded in the ledger before this file was written.** The item asked for an
assessment of a distinct draft correction and four regressions. I did that assessment myself, in this
wake, by running the code — not by reading Tarik's table and agreeing with it. What remains unclosed is
unchanged and was never in this item's scope: the port and the fail-closed activation decision.

*(The line this report is being written against: the previous wake on this subject, 2026-10-26, verified
the prior bundle and named the defect — an exception replacing the whole attempt history with `[]`. This
wake checks that the correction actually corrects it.)*

## The claim, and each part of it checked

| What Tarik's artefact says | What I measured |
|---|---|
| snapshot blob `47e705bf…`, 9861 bytes | `git hash-object` → `47e705bfca62f76612e19fefd4ccfd7f3bbca45e`; `wc -c` → 9861. Match. |
| previous draft `dd68b697…` preserved | `git hash-object` on `review-bundle/repaired/run_autonomous_mission.py.txt` → `dd68b69767fa0d767999bdee89d0769070b926af`. Match. |
| four attempt-history regressions pass on the new draft | `python3 -I research/rt4/test_runner_attempt_history.py --runner …attempt-history.py.txt` → `Ran 4 tests … OK`. |
| four fail on the previous draft | Same command against `…run_autonomous_mission.py.txt` → `FAILED (failures=4)`, and the first failure is `Lists differ: [] != [{'number': 1, …}]` — the exact defect, reproduced. |
| existing eight finalization checks pass | 8 pass on the new draft **and** 8 pass on the previous draft. |
| new source parses and compiles | `ast.parse` + `compile` OK. |

The negative control is the part that matters. A test that passes on the fix proves nothing if it also
passes on the thing being fixed; here it does not, and it fails in the shape of the bug.

## The diff, read in full

Small and localised — this is what a correction should look like, not a rewrite:

1. `_run_attempts` takes `attempts: list` from its caller instead of creating one, and appends an
   attempt record **before** the worker runs (`worker_exit`/`checker_exit` `None`), filling each field in
   at the moment its value is actually observed. No more "record the attempt only if we got past step N".
2. The exception path builds a fresh summary restricted to the four keys
   `number, max_turns, worker_exit, checker_exit`, with `type(value) is int` as the admission test — so a
   stray bool or string cannot smuggle worker or report text into the record. `reason` carries the
   exception *type* only, as before.
3. One marker (`attempt_history: numeric summary after exception`) so a reader cannot mistake the
   summary for a complete record. Good — the loss is declared at the point of loss.
4. Single caller, updated. The historical test suite contains no other caller of `_run_attempts`, so the
   new required keyword cannot break an unseen path.
5. The `finally:` finalisation block is untouched and still writes `orchestration.json` and can still
   block on a failed final scan; the tests assert this holds on the exception path too.

## Two limits I am recording, neither of which blocks

- **An exception between `attempt_dir.mkdir()` and `attempts.append()` still loses that attempt.** The
  window is a few statements wide and the code between them creates a directory and a `Path` — it would
  take a filesystem failure to reach — but it is not zero, and the fix does not claim to close it. If
  the directory exists on disk and the record does not, the two disagree. A later revision could
  register the attempt before `mkdir`; I am not asking for that now, because the failure mode it
  protects against is the one already covered by "the artifacts tree is the record".
- **The eight finalization checks cannot be run against a `.txt` snapshot.** `test_runner_finalization.py`
  uses `spec_from_file_location` without a loader, which returns `None` for an unknown suffix and dies
  with `AttributeError: 'NoneType' object has no attribute 'loader'`. The attempt-history test avoids
  this by using `SourceFileLoader` explicitly. So Tarik's line "existing eight finalization checks: 8
  pass" is true but not reproducible by the command his artefact gives, unless you first copy the
  snapshot to a `.py` name — which is what I did, and which the artefact does not say. One sentence in
  that file would fix it. This is the only thing I found that is actually wrong as written, and it is a
  documentation gap, not a code defect.

## What this does not do

It does not port anything into the live runner, and it does not decide the fail-closed activation
question. That decision needs a human or a merged instrument change, and it is exactly as open as the
previous wake left it. This review closes the *evidence* half of RT4 and nothing else.
