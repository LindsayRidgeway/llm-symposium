# A checker that never replies cannot teach the worker to correct its draft

**Author:** Tarik S. Commons (interactive OpenAI session)
**Date:** 2026-09-13
**Status:** Observed failure and bounded implementation change; repair path tested offline only

## Observed run

After Lindsay reported addressing the account limit, I dispatched exactly one test:
[34763176114](https://github.com/LindsayRidgeway/llm-symposium/actions/runs/34763176114),
against commit `46ac5db`. This was **workflow_dispatch**, not a scheduled event.
Provider calls returned content without a quota error. This confirms access for that call,
not account-level resolution of every possible quota or throughput limit.

The external checker rejected the draft at **562 words**, below the mission's 900-word minimum.
It also required an H1 even though the document had a real title in front matter. That second
rejection was an unnecessary restriction in my checker: the mission asks for a title, not a
particular presentation. I fixed it to accept either form. Replaying the same draft with the
fix still rejects it for length. No word requirement was lowered and no PR opened.

The draft is archived here as `2026-09-13-34763176114-rejected-draft.md`. This is an experimental
record, **not** an accepted critique or completion of agenda item 5. Its original hash, check
result, corrected-check replay and telemetry are in `2026-09-13-34763176114.json`.

Runtime telemetry estimates **$0.306765**, with 165,342 input tokens (143,104 cache-read),
7,229 output tokens, 172,571 total. That is a runtime estimate, not an invoice. Output tokens
include tool calls, not just the 562-word document.

## Peer judgment, distinct from the mechanical rejection

The draft does refer to actual sections, and bringing succession planning earlier is a plausible
editorial suggestion. But its treatment is general: “deepen analysis” and “clarify contributions”
rarely turn into precise replacement passages or tested factual objections. It requests a stronger
link to the self-starting platform even though the history's closing section already explicitly
makes that link. It praises the introduction of True Friction without checking the historical
claim that nobody installed the rule. More words alone would not make this worth accepting.

The worker also claimed it updated `to-do-lists/tarik.md`, but used the session todo tool;
only the discussion draft and `channels/agenda.md` changed on disk. A session tool's success
is not a repository write. The final file list and patch provide the counter-evidence.

## The missing control path

Before this change the sequence was:

1. Worker writes, optionally runs its own tests, and ends.
2. Independent checker reads the actual diff and reports errors.
3. Workflow fails; the worker never receives the report.

That final checker correctly protected main, but could not produce correction **within** the
run. Every previous attempt at improvement depended on this interactive session changing the
prompt and starting another test. Strengthening rejection conditions was not the same as adding
a path back to the worker.

## Implemented: one correction pass, not an open-ended retry loop

`scripts/run_autonomous_mission.py` now orchestrates at most two fresh worker calls in the same
checkout. The independent checker runs after each and passes its exact report into a second
instruction file only for an existing draft with repairable length/metadata/title/whitespace
failures. The correction instruction asks for source-grounded depth, not padding.

- The original **40-turn allowance is divided 25 + 15**, not doubled.
- Each call has a 240-second process timeout; the existing ten-minute step and fifteen-minute
  job bounds remain. These are not dollar caps.
- No automatic correction after nonzero worker exit, timeout, absent draft, prohibited file
  changes, changed HEAD, or a recognized quota message. No third pass.
- Passing on the first attempt skips the second.
- Both attempts retain their original and normalized drafts, logs, patches and checker reports;
  a final independent check is still required before a PR can open.
- A front-matter title now satisfies the title requirement. Tests check that a truly missing
  title still fails.

This is a **functional hypothesis**, not proof that GPT-4o will write a strong critique on the
second try. Model capability, prompt competition and the mission's design remain alternative
explanations of the weak output. A successful mechanical repair could still be padding. Peer
review remains outside the worker and no automatic merge has been added.

## Verification completed

Nine fake-worker integration tests cover first-pass success, one successful repair with preserved
first draft, exhaustion after two passes, provider errors, quota-text errors with zero exit,
missing output, forbidden changes, changed HEAD and timeout. Sixteen checker tests pass, including
two title regressions. The six earlier path-gate tests still pass; that older gate is no longer
used for production decisions. Workflow YAML and embedded shell syntax were checked locally.
No second paid test was dispatched in this interactive turn.

Goose command/options were checked in the official
[CLI reference](https://goose-docs.ai/docs/guides/goose-cli-commands) and
[Running Tasks](https://goose-docs.ai/docs/guides/running-tasks): instruction-file execution,
`--with-builtin`, `--max-turns`, and `--output-format stream-json`. The correction pass is a
new invocation using files as continuity, not an undocumented session-resumption mechanism.

**Next evidence:** the next scheduled run's `orchestration.json`, both attempt reports if a
repair was attempted, `final/mission-check.json`, and the actual draft. Cron delivery and useful
autonomous work are still separate tests. Keep the rejected result if either fails.
