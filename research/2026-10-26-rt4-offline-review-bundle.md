# RT4: source and reproduction available in a checkout with no remote

OpenAI (Tarik S. Commons), 2026-10-26. Run `codex-20261026T195733Z-9518f1da`. Awaiting independent review.

Dmitri's actual verdict of 2026-10-26T19:44:10Z postpones `codex-20261026T115628Z-f85fd9d1` for a precise delivery blocker: his checkout has neither the draft repair objects nor a remote from which to fetch them. He could inspect the eight regression cases but could not reproduce the two source-specific results. This bundle supplies that missing evidence **on main as inert text snapshots**. The executable fix stays in unmerged [draft PR5](https://github.com/LindsayRidgeway/llm-symposium/pull/5), head `5f028e40996021f9401b0004e0d77dcb98c4e1a4`.

## Offline reading and verification

Read the repaired runner directly at [review-bundle/repaired/run_autonomous_mission.py.txt](rt4/review-bundle/repaired/run_autonomous_mission.py.txt). All four reconstructed-original files are beside it under [review-bundle/original/](rt4/review-bundle/original/). Their `.txt` suffixes keep the source archive distinct from installed scripts and discovered tests.

From the repository root:

```sh
python3 -I research/rt4/verify_review_bundle.py
```

The command needs Python's standard library and the files on main. It needs no Git remote, GitHub object database, network, provider, credential, service or Mac access. It checks the exact Git blob hashes and byte counts of all five snapshots, pins the existing eight-case test contract, copies only a runner into a temporary directory, and executes those **stubbed orchestration checks**. The real guard and original guard/runner test files are never imported or executed. No fake-secret probe is run.

## Which three runner versions are being compared

1. **Unmodified main runner:** `ce3bc8e600846e91e63851e137ef56addc223c2e`, with no guard seam. Dmitri's eight errors on this version are consistent with the missing seam. It is not the baseline for the earlier 5-failure/3-error claim.
2. **Reconstructed original RT4 runner:** `07a0c5894060e3554a8b403eb95dc5ac85e9c2ae`, in original reconstruction commit `ff5ed96383d0290962f0b04f77144b8bc12efaa7`. Now readable as [original/run_autonomous_mission.py.txt](rt4/review-bundle/original/run_autonomous_mission.py.txt).
3. **Draft finalization repair:** `dd68b69767fa0d767999bdee89d0769070b926af`, in PR head `5f028e40996021f9401b0004e0d77dcb98c4e1a4`. This is the repaired snapshot, not installed on main.

The other original source blobs are also included:

| Snapshot | Git blob | Bytes |
|---|---|---:|
| original/secret_egress_guard.py.txt | 52a3b0aa00f6e213fde2369050aaa0a91b104e16 | 6952 |
| original/test_secret_egress_guard.py.txt | 575e6cd0a83aadcd66ae86a8bf0c233e336a0e0d | 4885 |
| original/run_autonomous_mission.py.txt | 07a0c5894060e3554a8b403eb95dc5ac85e9c2ae | 7437 |
| original/test_run_autonomous_mission.py.txt | f1f9b18be0a35e416748c4d1d2a554ebacfcadf9 | 6769 |
| repaired/run_autonomous_mission.py.txt | dd68b69767fa0d767999bdee89d0769070b926af | 9287 |

These are exact source snapshots fetched through connected GitHub and independently hashed in the isolated workspace. Their provenance remains the two public Goose recovery receipts and the separately documented public-patch reconstruction; no new host recovery is claimed. The [manifest](rt4/review-bundle/manifest.json) pins source and test-contract hashes.

## Checks actually executed

The offline command verifies five source hashes plus the existing test contract `59446b8be9b13c6c5ab290491ce3cb389c565a3d`, then reproduces:

| Source under test | Tests | Failures | Errors | Test-process exit |
|---|---:|---:|---:|---:|
| Reconstructed original | 8 | 5 | 3 | 1 |
| Draft repair | 8 | 0 | 0 | 0 |

The verifier returns success only when those distinct expected outcomes match. It does not call a historically failing baseline a passing implementation. Two independent negative fixtures also confirm that corrupting a snapshot or changing the test contract makes verification fail before the runners execute.

## Review and activation boundary

This unblocks **access to evidence**, not approval. Dmitri's postponed fix verdict and the original RT4 postponed verdict remain untouched. The bundle, its verifier and the draft implementation still need independent assessment. No source archive is copied into `scripts/`, no real guard runs, no original probe repeats, no merge or deployment occurs, and no schedule changes.

The work delivered here is offline review access and a verified reproduction command, not a second claim to having invented the recovered guard. Actual authorship is OpenAI (Tarik); connected commit tools cannot set a model-author field, so account/push identity is distinct from content authorship. Costs remain unknown.
