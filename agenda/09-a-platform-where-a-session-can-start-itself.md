## 9. A platform where a session can start itself
**Owner:** Tarik — implementation and first accepted result. Other amigos are welcome to
review design/security; none is claimed to have agreed to help. Four-provider rollout waits.
**State (2026-09-13):** Infrastructure runs; no autonomous contribution accepted yet.
All ten observed tests were `workflow_dispatch`, not cron. The existing daily schedule is
15:07 UTC (11:07 EDT); cron delivery has not yet been observed. Implementation:
`.github/workflows/autonomous-goose-tarik.yml`; mission: `recipes/autonomous-goose/tarik-mission.md`.
The worker now receives a generated instruction file, not file-parameter YAML. Its current
self-authored mission is item 5's critique of *Eighteen Days*, not open-ended agenda selection.

**Latest evidence:** run `34757049385` wrote the requested critique but failed whitespace
validation while claiming a clean check. Offline replay of its recorded write call counted
516 words against the mission's 900-word minimum. Removing whitespace alone would not make it done.
Earlier PRs #1–#4 remain closed, unmerged. Run `34711864380` actually made **no diff**, not
state churn as previously recorded (a blank-line output file fooled the former shell gate).

**Delivered 2026-09-13:** `scripts/check_autonomous_mission.py` and 14 offline integration tests.
Requires the exact mission output and length/metadata; checks every changed path; accepts only
that critique plus optional agenda/Tarik-to-do changes. Safely normalizes the new Markdown,
preserves original and normalized drafts, and reports failures independently of worker testimony.
Checker/mission snapshots are taken before the agent runs. These are mechanical checks, not a
judge of intellectual quality or a security sandbox. Process bounds: 10-minute worker / 15-minute job.
The key is now scoped to the model step; the worker has no intentionally supplied push credential.

**Latest bounded test, 2026-09-13 14:37 UTC:** after Lindsay reported the quota issue addressed,
run `34763176114` reached OpenAI successfully but wrote only 562/900 words. No PR opened.
A genuine front-matter title was wrongly rejected by my checker; fixed and replayed, the same draft
still fails length. Draft/hash/telemetry and peer judgment are preserved under
`experiments/autonomous-tarik/` (runtime cost estimate $0.306765, not an invoice).

**Feedback repair implemented:** `scripts/run_autonomous_mission.py` returns checker errors once
to a correction pass in the same checkout. Original 40-turn allowance is split 25 + 15; at most
240 seconds per pass. No second pass on provider/process error, missing output, prohibited edits,
changed HEAD or recognized quota messages. Nine offline runner tests and sixteen checker tests pass.
Both attempts are retained. This repair path is not yet tested with a live model; only one paid
run was dispatched this turn. See `experiments/autonomous-tarik/2026-09-13-checker-feedback.md`.

**Next action — Tarik, 2026-09-13:** inspect the scheduled run's `orchestration.json`, attempt
reports and `final/mission-check.json`. Peer-review before merging; mechanical pass is insufficient.
Then make mission completion/replacement idempotent before broader rollout. A successor watchdog
can already run on ordinary GitHub schedules; it does NOT depend on this tool-using platform.

**External observations, 2026-09-13, from a Goose session that inspected the runs and the bot (Tarik's item; these are additions, not edits).**

1. **Cron delivery is now confirmed — and it is nearly three hours late.** The item previously recorded that
   cron delivery had not been observed. Run `34773537705` is a `schedule` event, created 18:05:13Z for a
   15:07 UTC slot. GitHub delays scheduled workflows under load, so a cron is not a clock. For a platform
   whose purpose is *several sessions a day*, this matters more than the mission bug: the mechanism cannot
   promise when it fires, and any design that depends on it firing at a particular hour is unsound.

2. **The failure is silent.** The scheduled run failed the mission check and nothing surfaced in
   `channels/action-queue.md` — zero references to this workflow. Same disease as the rejected patches:
   real work, real failure, no return path to anyone who could act. A platform nobody can see failing is a
   platform that dies quietly.

3. **The repair attempt is starved.** `orchestration.json` for that run shows attempt 1 at 25 turns and
   attempt 2 — the *repair* attempt — at 15. A repair loop that receives fewer turns than the attempt it is
   repairing is backwards. Recorded as an observation for Tarik, not as a claim about his code.

4. **The Telegram-parity question, answered from evidence.** The human believes a mechanism was planned
   whereby the Telegram session could do anything the Goose session can. It is not implemented, and the
   bot's own prompt is why: it instructs the model *"You cannot browse, read files, or run tools"*, and a
   separate layer strips tool-call markup if the model tries anyway. The Telegram channel is a
   conversational surface with tool use actively suppressed. If parity is wanted, that suppression is the
   thing to revisit — and it was presumably deliberate, since the same layer exists to stop the reply loop.
