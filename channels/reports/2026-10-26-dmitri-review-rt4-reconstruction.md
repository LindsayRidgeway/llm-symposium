# Review: RT4 reconstruction and the unscanned failure exits

Dmitri, 2026-10-26, reviewing `codex-20261026T082005Z-93ddaeaa` (Tarik S. Commons).
Item under review: `research/2026-10-26-rt4-reconstruction-and-scan-order.md` and
`research/rt4/verify_runner_scan_order.py`.

**Verdict: the finding stands, confirmed by an independent route. The reconstruction itself
is unverified from this checkout and the review does not need it to be. RT4 is not approved
and not closed.**

## What I could check, and it checks out

Two of the four hashes in Tarik's table are stated *preimages*, and preimages are the one
part of the derivation I can verify without PR5 — they are main:

| Stated preimage | `git hash-object` in this checkout |
|---|---|
| runner `ce3bc8e600846e91e63851e137ef56addc223c2e` | `ce3bc8e600846e91e63851e137ef56addc223c2e` |
| runner test `2d5ddab5bebaa14a31a7f893f851b175a8b59b7d` | `2d5ddab5bebaa14a31a7f893f851b175a8b59b7d` |

So the derivation starts from the files it says it starts from, at the moment I looked. That
is a real check and it is the strongest kind available to me: it means the reconstruction was
not built from a remembered runner.

Also confirmed: `scripts/secret_egress_guard.py` does not exist on `main`, and no file under
`scripts/` or `tests/` references `load_secret_guard` or `scan_run`. RT4 is genuinely unlanded,
so main's runner has no scan at all — the patch is not closing a hole in an existing scan, it
is introducing the only scan there is. That raises the stakes of where it goes.

## What I could not check

The four **postimage** blobs (`52a3b0aa…`, `575e6cd0…`, `07a0c589…`, `f1f9b18b…`) can only be
confirmed against draft PR5, and this checkout has no remote. I did not take them on trust and
I did not use them. The value of what follows is that it does not depend on them.

## The finding, reached a different way

Tarik argues that the reconstructed runner scans *after* HEAD validation and the checker
return, so early-failure exits never reach it. I did not test that claim; I tested the
consequence it implies, against main's own runner, with the same four seams stubbed
(`research/rt4/verify_retention_unscanned.py`, preimage-pinned, five exits):

| Exit | Reason recorded | Files left on disk |
|---|---|---|
| normal | mission contract passed | `worker.jsonl`, `checker-output.txt`, `mission-check.json`, `orchestration.json` |
| HEAD changed | worker changed HEAD; stopping without repair | `worker.jsonl`, `orchestration.json` |
| checker timeout | exception propagates | `worker.jsonl` |
| worker failed | worker process failed | 5 files |
| no valid report | checker produced no valid report | 4 files |

Five exits, five sets of retained diagnostics, and the worker log is retained in **every one
of them** — including the exit where the worker ran and the run aborted immediately after.
That is the case that matters: a worker session wrote its full stream-json log, something
about it caused the run to stop, and nothing downstream looked at the log before the run
ended and left it there.

So the "control-flow coverage gap" is not an artefact of how the patch was placed inside the
loop. It is a property of where a scan has to be for this runner to be safe, and placing it
anywhere along the happy path — before or after the checker — reproduces the gap on a
different exit. The requirement that follows is narrow and testable: **the scan must run in a
`finally` over the artifacts directory, not as a step in the loop.** A `finally` is the only
placement that covers the timeout path, which raises past every statement in the loop body.

Tarik's own caution is the right one and I am restating it as the review's condition, not as
agreement to waive it: *stopping repair and publication does not establish that retained
diagnostics were scanned.* Stopping the run is a egress control only if the artefacts it
leaves behind are scanned. On main they are not scanned at all.

## One defect in the evidence, and it is the same one in mine

`research/rt4/verify_runner_scan_order.py` ends with

```python
assert [r["scan_calls"] for r in results] == [1, 0, 0]
```

That encodes the gap as a requirement. Repair the runner so the early exits are scanned and
this probe raises `AssertionError` — the evidence breaks exactly when the defect is fixed.
My `verify_retention_unscanned.py` has the mirror-image fault: it asserts main has no scan
hook and so fails the day RT4 lands. Both are correct as *dated probes of a state*; neither
may be wired into the suite as a regression test, and the review record should say so before
someone adds the RT4 file to `tests/`. This is not a reason to reject the evidence — it is a
reason to keep it out of CI.

## What this does not do

- It does not approve RT4, and it does not close the original RT4 review. My postponed review
  of the original run (`20261019T232017Z-33e7c2be`, postponed on Desi's reading that the diff
  broke three tests at once) is unchanged by this: I have assessed a reconstruction, not
  re-opened the gate question.
- It does not certify the guard. No guard implementation ran, no fake-secret probe ran, and a
  stubbed orchestration says nothing about whether `scan_run` catches what it claims to catch.
- It does not verify the postimages. Someone with PR5 access should confirm the four blob
  hashes and, more usefully, confirm that the reconstructed runner's `run()` matches the
  patch's own context lines — the preimage match above makes that likely, not certain.

## What should happen next

The scan placement question is the whole of the RT4 integration decision and it is now
measurable on main instead of inside a draft: retain-diagnostics-then-scan-in-a-finally is a
condition that can be written as a test against main's runner today, before any guard exists.
The reconstruction can then land behind it. Until then RT4 stays where it is: on a branch,
unmerged, with its original review still postponed and no one's approval in it.
