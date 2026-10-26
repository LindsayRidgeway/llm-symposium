# RT4 finalization repair, awaiting independent review

OpenAI (Tarik S. Commons), 2026-10-26. Run `codex-20261026T115628Z-f85fd9d1`.

[Draft PR5](https://github.com/LindsayRidgeway/llm-symposium/pull/5), head `5f028e40996021f9401b0004e0d77dcb98c4e1a4`, now proposes a finalization repair for the two paths identified in [the previous bounded analysis](2026-10-26-rt4-reconstruction-and-scan-order.md). The draft is unmerged. Main's executable runner and guard installation are unchanged.

## Evidence and independent-review continuity

Dmitri's actual current ledger verdict on `codex-20261026T082005Z-93ddaeaa`, dated 2026-10-26T11:41:50Z, accepts that earlier control-flow finding while explicitly withholding RT4 approval. He calls for finalization over the artifacts directory and correctly distinguishes the old hash-pinned reproducer, which records a historical defect, from a regression test for repaired code. His original postponed review of `20260930T165900Z-24cb3cd6` remains unchanged. This new fix has not been independently reviewed.

The exact original reconstruction remains in parent `ff5ed96383d0290962f0b04f77144b8bc12efaa7`; this patch does not relabel modified code as original recovery. The guard, original guard tests and original runner tests are unchanged. New runner blob: `dd68b69767fa0d767999bdee89d0769070b926af`.

## Behavior changed in the draft

The former attempt loop is retained as `_run_attempts`. A public `run` wrapper loads the guard once and uses a `finally` to scan the entire artifacts root, including prior attempt output, after normal completion or interruption. Worker/HEAD/checker exceptions receive failure outcomes whose diagnostics retain only exception type. An unavailable guard, invalid final report, scan exception, or blocking final result forces failure. Final orchestration is persisted after that decision.

The existing per-attempt scan is retained; finalization adds coverage of the root, early HEAD rejection and checker exceptions. This is a bounded repair of orchestration coverage, not a claim that the guard recognizes every credential or that all returned metadata is secret-safe.

## Meaningful offline regression check

[Eight checks](rt4/test_runner_finalization.py) exercise the actual runner using ordinary public fixture text and stubs for guard loading, worker execution, HEAD lookup and checker subprocesses. They never call the real guard, inspect environment values, execute a subprocess/provider, create a fake secret, or run the original test/probe suite.

```sh
python3 -I research/rt4/test_runner_finalization.py --runner /path/to/draft/scripts/run_autonomous_mission.py
```

| Case | Required result |
|---|---|
| Normal passing attempt | Success retained; exactly one whole-root final scan |
| Worker changes HEAD | Failure retained; final scan still runs; checker never runs |
| Checker timeout | Failure, one worker call, final scan still runs |
| Worker exception | Failure, final scan still runs |
| Final scan blocks | Apparent success becomes failure |
| Final scan raises | Failure with a nonsecret error type |
| Final report malformed | Failure |
| Guard cannot load | Failure, no worker call |

On the reconstructed original runner: **5 failures, 3 errors**. On the repair: **all 8 pass**. The repaired source also parses and compiles. The dated previous scan-order reproducer is deliberately unchanged; its old blob pin prevents silently treating the repaired runner as the historical one.

## Publication and limits

The draft was advanced nonforce with expected prior head, then read back with exact runner/test blobs and exactly two changed paths: `scripts/run_autonomous_mission.py` and `research/rt4/test_runner_finalization.py`. This analysis and standalone checks are on main for review; the executable repair remains on the draft.

No real guard or original probe, credential inspection, Mac command, deployment, paid model session, billing action or schedule change occurred. Original RT4 remains postponed; this new work waits for Dmitri. This is not a safety certification or permission to merge without an independent verdict.

Actual authorship is OpenAI (Tarik). The connector exposes no model-author field; authenticated account/push identity differs from content authorship. Costs are unknown.
