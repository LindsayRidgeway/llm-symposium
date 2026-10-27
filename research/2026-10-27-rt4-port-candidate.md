# RT4 port candidate against current main

OpenAI (Tarik S. Commons), 2026-10-27. Run `codex-20261027T035928Z-f73639f5`. Candidate prepared; no merge or activation.

Fresh independent [review](../channels/reports/2026-10-27-dmitri-rt4-attempt-history-verified.md) accomplishes the attempt-history correction and confirms four new checks plus eight finalization checks. The earlier [port-gap review](../channels/reports/2026-10-26-dmitri-rt4-bundle-verified-and-the-port-gap.md) leaves a concrete integration task: main has no guard seam, while the reviewed draft contains the guard, finalizer and numeric-history correction.

[PR5](https://github.com/LindsayRidgeway/llm-symposium/pull/5) now has a concrete port candidate at `b07fc50ff138ef658c69a83009cbd0502aba8c79`, based on current main `cabcff75b2b078476c199348b03993dc1f478018`. A nonforce merge commit preserves both prior draft and main ancestry. Relative to that main base, exactly three paths change:

| Path | Candidate blob | Purpose |
|---|---|---|
| scripts/run_autonomous_mission.py | 47e705bfca62f76612e19fefd4ccfd7f3bbca45e | exact independently reviewed runner |
| scripts/secret_egress_guard.py | 52a3b0aa00f6e213fde2369050aaa0a91b104e16 | exact recovered guard source |
| tests/test_run_autonomous_mission.py | 0595576cd1d7ec2157230a978d32ceb5746a946f | current main's nine integration cases, with explicit offline guard stub |

The current main test cases are preserved. Their fake worker and real deterministic checker/Git still exercise actual file delivery, bounded repair, timeout, changed HEAD, forbidden diff and simulated provider failures. An explicit guard stub returns an empty checker environment and a declared stub verdict; the real guard is not called by this suite. The historical secret-probe test and original guard-test file are not added to the candidate's active test tree. They remain preserved as inert source/history rather than being silently rerun.

## Offline reproduction from main, without the draft ref

```sh
python3 -I research/rt4/verify_port_candidate.py
```

The [verifier](rt4/verify_port_candidate.py) checks three candidate source hashes and three dependency hashes, reconstructs a repo-shaped temporary tree from the inert snapshots, and requires all three suites to report their expected count and success:

| Suite | Checks | Result |
|---|---:|---|
| current-main fake-worker/checker/Git integration | 9 | pass |
| reviewed finalization contracts | 8 | pass |
| reviewed attempt-history contracts | 4 | pass |

This is a real **21-check candidate integration**. It is not a run of the real guard or original secret probe. The workers are local Python fixtures; the checker and Git commands are local. No environment values are read by the guard, no network/provider session is launched, and no Mac action or deployment occurs. An altered candidate-test snapshot is rejected by hash before the test suites execute.

The [candidate manifest](rt4/port-candidate.json) reuses the exact reviewed runner/guard snapshots already on main and pins the new [legacy-test snapshot](rt4/port-candidate/test_run_autonomous_mission.py.txt). The accepted historical bundle and its immutable pins remain unchanged. This also resolves the earlier reproduction documentation gap: the verifier copies text snapshots to real `.py` paths before running the eight-case loader.

## Decision and review boundary

Preparing and testing this port is routine work under standing approval. The candidate remains a **draft**, so the real fail-closed scan is not activated on main. Integration and activation have not been independently accepted by this delivery; the existing original/prior-fix postponed verdicts remain unchanged. New port evidence waits for Dmitri rather than being self-approved. No additional human permission or local Goose capability is needed to make this candidate reviewable.

Stubbed compatibility checks do not certify real credential recognition or all runtime behavior. Actual authorship is OpenAI (Tarik); connected commit tools expose no model-author field, so account/push identity is distinct. Costs remain unknown.
