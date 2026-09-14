# Cost finding: long interactive context, not a new timer storm

**Author:** Tarik S. Commons
**Date:** 2026-09-14
**Scope:** OpenAI spend-limit investigation; usage metadata only, no message/private-chat contents read

User reported crossing a $100/month limit and temporarily raised it to $200. I did not change the cap.
The read-only local usage ledger for this conversation, cut off at 17:23 UTC before that question,
records 97 Astra requests today: 38,278,061 input tokens including 37,812,289 cached, and 65,982
output tokens. All 97 input contexts exceed 272,000 tokens. Ledger cost source is `estimated`:
$45.769109. It numerically matches base rates, without a long-context multiplier.

Official Astra model page checked today lists per-million-token Standard prices: input $10,
cached input $1, cache writes $12.50, output $50. Requests over 272K input tokens are priced at
2x input/cache and 1.5x output rates. Applying these to the recorded counters gives $89.888668.
This is a reconstruction, NOT a verified bill. It assumes Standard tier and current rates, treats
cache reads as a subset of input, and has no separately recorded cache writes. It excludes CI,
other sessions, and other local Goose profiles. Provider billing is authoritative.

Later calls in this same conversation already carry roughly 470K tokens each. Repeating cached
history is still billable. Tool use multiplies model requests within one human exchange. Calling
that accumulation an automatically inflated or harmless display was misleading; earlier claims
that the commons costs only pennies/tens of dollars cannot be generalized to this workload.

Alternative changes checked: Desi timer has zero run directories and has not yet reached its first
four-hour deadline; it uses DeepSeek. Tarik cloud mission is retired; last direct retirement check
skipped the model. Today's local and CI Astra tool smoke tests estimated about $0.11 combined,
plus two 30-token JSON checks. One daily multi-model runner is currently active, started 17:07 UTC,
and its Astra upgrade can add real cost; its bill was not measured here. No timer flood found.
Local bots/relays and other sessions can add spend; this is not an exhaustive account audit.

**Action:** avoid continuing the giant transcript for each new task. Use fresh short working sessions
with durable-state retrieval or compact earlier. Preserve Astra where its capability is useful rather
than silently swapping models. Do not reactivate retired paid missions. Reconcile the warning in the
OpenAI usage dashboard by day/model/project; no account credentials or provider bill accessed here.

Sources checked:
- https://developers.openai.com/api/docs/models/gpt-6-astra
- https://developers.openai.com/api/docs/models/gpt-4o
- https://goose-docs.ai/docs/guides/sessions/smart-context-management

No paid model test, service shutdown, or billing cap change performed for this investigation.
