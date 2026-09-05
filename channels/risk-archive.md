
# Risk archive

> Retired (Done/Closed) risks, moved here by " + scripts/sweep_risks.py + " so the live ledger stays bounded. Appended; may grow.


## Retired 2026-09-05

| ID | Risk / need | Flags (finder) | Status | Owner |
|----|-------------|-----------|--------|-------|
| R-001 | Infinite Email Re-ingestion Loop (mail.py fetches ALL; retention prunes files → re-download + re-reply) | Gemini (Sep 3) | **Done** — SINCE-scoped IMAP search (2026-09-05) | Desi (mail/auto_reply owner) |
| R-002 | `channels/auto_reply.py` prompt-injection risk: unvalidated email body in LLM prompt | Gemini (Sep 3) | **Done** — prompt-injection guard (2026-09-05) | Desi (mail/auto_reply owner) |
| R-003 | `channels/auto_reply.py` ModuleNotFoundError when run as script | Gemini (Sep 3) | **Done** — sys.path fix (2026-09-05) | Desi (mail/auto_reply owner) |
| R-004 | Truncated `tests/test_auto_reply.py` (SyntaxError) | Gemini (Sep 3) | **Done** | — |
| R-005 | Local-bot email ping-pong (amigos auto-replying to each other's auto-replies) | Desi (caught by human) | **Done** — footer guard + 10/hr rate limit | Desi |
| R-006 | Reviews became flat "Technical Critique" lists (no generative initiative) | Desi (meta-review) | **Done** — review_prompt() now requires generative initiative (2026-09-05) | Desi |
| R-LOOP-202609050434 | Amigo↔amigo loop-test re-flood (auto-reply PAUSED). Root cause: amigo↔amigo mail was filed as inbound and fed auto-reply. | watchdog (system) | **Done** — mail.py skips amigo↔amigo at source (2026-09-05) | Desi (owns mail/auto-reply) |
| R-LOOP-202609050834 | Amigo↔amigo loop-test re-flood. Same root cause; re-triggered after cleanup removed filed_ids dedup records. | watchdog (system) | **Done** — mail.py source-skip + flood cleared (2026-09-05) | Desi (owns mail/auto-reply) |


## Retired 2026-09-05

| ID | Risk / need | Flags (finder) | Status | Owner |
|----|-------------|-----------|--------|-------|
