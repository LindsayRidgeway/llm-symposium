# Tarik wake division of work

Adopted 2026-10-16 on Lindsay's instruction. Tarik-Codex and Tarik-Goose are
platforms for the same OpenAI amigo, not separate roster members.

## Ownership

Tarik-Codex owns the general queue at `to-do-lists/tarik.md`: research, writing,
coding, appropriate tests, peer-review duties, the commons ledger, and publication.
It runs in the manufacturer's app using the shared written continuity record.

Tarik-Goose's ONLY scheduled-wake work list is
`channels/tarik-goose-handoff.json`. It must not independently take work from
the general to-do list, agenda, reject queue, or creative floor during those wakes.
This instruction supersedes older broad-work instructions embedded in its timer.
Interactive Telegram replies and explicitly requested reactive local work are
separate from the scheduled-wake queue and remain available.

Codex may enqueue only work it cannot currently perform and has evidence Goose
can perform. State the missing capability, exact goal, permitted targets, and an
observable acceptance result. Ordinary cloud-capable work stays with Codex.
A need for another architecture's independent review goes to that architecture,
not to Goose as a second reviewer of Tarik's own work.

## Codex schedule

Requested clock slots are 00:00, 04:00, 08:00, 12:00, 16:00, and 20:00 in
America/New_York: six occurrences per calendar day. Daylight-saving transitions
can make one elapsed interval three or five hours. One recurring automation
implements all six slots. Its actual ID and enabled status are recorded only
after the scheduler confirms them.

Each Codex wake must:
1. Read fresh ROSTER and AUTHORSHIP, Tarik durable facts/recent conversation, this protocol,
   private Tarik context/state, its general to-do list, handoff statuses, and
   recent Codex wake records. Current ROSTER overrides old participant counts.
   Keep private orientation private and never inspect credential files.
2. Avoid duplicating completed or in-progress work. Advance the general queue in
   order; route a demonstrated local-only blocker to Goose and continue to useful
   cloud work. Respect independent-review rules.
3. Produce a concrete useful artifact where feasible, perform meaningful checks,
   publish without overwriting concurrent work, and freshly verify the result.
   A plan, routine orientation, or a new handoff alone is not a completed artifact.
4. Use an isolated cloud workspace when code needs execution. Record an actual
   UTC start, unique `codex-YYYYMMDDTHHMMSSZ-8hex` run ID, selected work,
   checks, artifact paths/commit, and any precise blocker under
   `channels/tarik-codex-wakes/`. Do not expose private content or credentials.
5. For substantive artifact commits use
   `land(wake): Codex work from run <run-id>`, so the existing delivery clock
   can recognize native wake work. Follow AUTHORSHIP and include the trailer
   `Architecture: OpenAI (Tarik)`; distinguish the connection's push/account
   identity from actual model authorship when a connector cannot set author fields.
   Record actual published work in the existing
   item ledger using the Codex adapter when installed; keep it waiting for
   independent review unless a documented existing rule establishes another state.
   Do not create a new amigo or claim API cost numbers that were not measured.
6. Leave concise durable outcomes and update queue state. Do not send routine
   wake summaries by Telegram/email; preserve the existing daily-report policy.
   Use REQUEST T-n only when Lindsay's involvement is genuinely necessary.

Work should stay bounded (normally about ten minutes). Use the app's model and
approved tools; do not launch separately billed model/API sessions or purchase
credits as a workaround. Lindsay is monitoring actual spending. A mandatory
approval/access failure is a precise blocker, not permission to bypass it.

## Goose queue and execution

The JSON root is `{"version":1,"tasks":[]}`. Each task has an immutable ID,
status, title, reason_for_goose, instructions, expected_result, created_utc, and
source `codex`. Task-specific allowed_targets may be listed. Lifecycle:
`pending -> in_progress -> completed | blocked | uncertain`.
A blocked task is reopened only after its blocker changes. Interrupted or
uncertain work is reconciled from evidence rather than automatically repeated.

The local timer may remain as a cheap dispatcher. Before starting any paid model
session it must read a fresh queue, validate it, choose the oldest pending item,
and successfully publish a unique claim using the current remote version.
Empty/unreadable/malformed queues and conflicting or uncertain claims start no
model session. Cache or local journal data cannot silently substitute for a fresh
queue. Only the claimed task belongs in the worker prompt.

Claims name the actor, run ID, UTC time, and a nonsecret unique claim token.
Completion re-reads current remote state and publishes the verified result artifact
and matching-token queue transition together in one nonforce commit from a fresh
disposable clone. It preserves all other tasks and newly enqueued work. The shared
local checkout and its old lander are not used to publish host-only handoffs.
Only the exact result artifact may change in the worker's public checkout;
unexpected repository edits stop publication and retain the claim for reconciliation.
No actor steals a claim or rewrites the queue from an old snapshot. If host work
succeeds but publication fails, retain its evidence and reconcile publication
without repeating the host action.

Mac actions must stay within the task's permitted targets. Prove actual host
changes with source hashes, appropriate tests, and runtime observations; a public
repo commit alone does not prove a private bot was installed. Create a nonsecret
result artifact in the isolated commons checkout for publication. Avoid killing
the running parent bot before its outcome is safely persisted. A deferred restart
is still awaiting activation; only an independent runtime observation can establish
that the new code is active. Never mark staged source or a planned restart complete.

## Deployment truth

Creating the native schedule, publishing this policy, committing a private patch,
and installing it on the Mac are separate facts. The local worker's installation is now supported by the published
`channels/tarik-goose-results/tg-20261016-001.json` receipt: Goose reports matching
deployed source hashes, an active restarted launchd service, startup persistence,
one Telegram receiver, fresh continuity and zero-model empty/unavailable queue checks.
Codex freshly verified the receipt and matching completed queue state on2026-10-17;
this is remote evidence reconciliation, not a new direct observation of the Mac.
The bootstrap required an existing Mac-local Goose session; queue publication
alone did not start its missing consumer. REQUEST T-2's installation purpose is
satisfied by that receipt. Codex still has no configured Mac command bridge.
The pending recovery tasks002/003 remain queued; automatic scheduled pickup of
one of those tasks has not yet been observed. The recorded local interval is
86400seconds, retained here without changing its cadence.

## Reporting compatibility

Codex is still `amigo: tarik`. Its run IDs use a Codex namespace and may carry
`platform: codex`; these are not a sixth participant. Completed artifact
records join the existing `channels/items.jsonl` ledger, preserving its review
states and the current daily report. An empty wake or mere metadata update is
not counted as performed work.

## Confirmed setup state

The native scheduler confirmed **Tarik Codex wakes** enabled on 2026-10-16.
Its stored schedule was freshly read back unchanged:
`DTSTART;TZID=America/New_York:20261016T120000` and
`RRULE:FREQ=DAILY;BYHOUR=0,4,8,12,16,20;BYMINUTE=0;BYSECOND=0`.
The first configured slot is noon EDT on October 16. Recurring records now include an interrupted noon attempt and verified substantive
16:00/20:00 New York artifacts on2026-10-16. See `channels/tarik-codex-wakes/`.
These observations establish actual deliveries, not a guarantee of future execution.

The private handoff-only worker and its portable tests were published in commit
`23bc345b267463083ff467145b8c39bc89782124` of the private bots repository.
Worker blob: `ae97956ef6dd2fbe76551632e9aaed496fbcf1f9`.
Thirteen portable offline tests passed; the larger local review passed fourteen
checks. Result validation rejects configured credential values and credential-bearing
URLs before any publication, without exposing rejected content. Real bare-Git tests cover claim conflicts, a stale source checkout,
atomic result/completion publication, rejected extra edits, and zero repeat execution. Mac installation and runtime checks are now reported in the completed
`tg-20261016-001` receipt described above; the source publication and actual
activation remain separate pieces of evidence.

The public recorder `scripts/record_codex_wake.py` and its fifteen offline tests
preserve the existing daily-report ledger. A verified artifact enters as Tarik,
platform Codex, waiting for review; routine reports, claims, handoffs and result
receipts cannot count as completed work. Actual costs remain unknown here.
