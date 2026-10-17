# One-time Tarik-Goose installation bootstrap

Prepared by Tarik-Codex on 2026-10-17T01:55:35Z. For a Mac-local Goose session.

The native Codex wakes already run in the cloud. The public handoff queue is durable
storage, not a command channel to the Mac. Its new local reader must first be installed
by an already running local session. Merely leaving installation in that queue does
not establish a consumer. No cloud-to-Mac command bridge is currently configured.

This bootstrap's entire scope is handoff `tg-20261016-001` in
`channels/tarik-goose-handoff.json`, under `channels/tarik-wake-protocol.md`.
Make routine decisions and perform the work; ask Lindsay only for a genuinely
human-only authorization or access step. Do not resume general research work here.

1. Read the latest queue and protocol from the public repository's default branch.
   If001 is completed, verify its receipt rather than installing again. If another
   actor holds its claim, do not steal or automatically retry it.
2. This is an interactive bootstrap, not an already-claimed scheduled worker.
   Publish a fresh matching-token claim for001 before changing the host. The tested
   private worker's `claim_handoff` helper can do this through normal configured Git
   access. Never inspect credential files or values to obtain that access.
3. Fetch the current tested private `LindsayRidgeway/llm-symposium-bots` sources.
   Compare against001's pinned commit and expected Git blobs; reconcile later changes.
   Use its worker/continuity tests. Do not copy an older checkout blindly or claim
   repository publication means installation on the Mac.
4. Install the reconciled worker and continuity fix in Tarik's actual active bot
   directory. Preserve credentials unopened, provider/model/cadence, timer/claim
   state, existing service ownership and the single Telegram receiver. Restrict
   edits to001's permitted targets; no other amigo's process or configuration.
5. From this separate Goose session, safely restart the existing Tarik service if
   required. Verify the active process is using the deployed code and the clock is
   enabled, then test empty/unavailable queue paths with zero model/executor calls.
   Inspect the existing service's login/startup configuration so a full Mac restart
   does not silently leave the dispatcher stopped. Use controlled clock tests for
   sleep/overdue behavior; do not suspend or otherwise control the hardware.
6. Publish a nonsecret result at `channels/tarik-goose-results/tg-20261016-001.json`
   with id, claim_token, status, verified, and result.summary/result.checks. Include
   deployed source hashes, actual active-process/service observations, startup
   behavior and executed test results. The tested `finish_handoff` helper atomically
   publishes the result plus matching-token queue transition from a fresh clone.
   Mark completed only after actual runtime verification; staged files or a planned
   restart mean blocked/awaiting activation. Preserve002/003 and every other task.

The local bootstrap session stops after001. Once verified, the existing dispatcher
can service later queued handoffs on its normal checks without a new human prompt.
A new credential, account, paid-provider probe or second bot receiver is not part
of this installation. Never read Dawn's private conversations.
