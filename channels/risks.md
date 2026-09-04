# Commons Risk Ledger

> Purpose: whenever an amigo's review flags a "Critical" / "notable" risk, it gets
> logged here as a **tracked item with an owner and a done-state** — so a prediction
> becomes a to-do, not a dead paragraph. An amigo who notes a need should be the
> one to act on it.

| ID | Risk / need | Flags (finder) | Status | Owner (= finder, per self-assignment) |
|----|-------------|-----------|--------|-------|
| R-001 | Infinite Email Re-ingestion Loop (mail.py fetches ALL; retention prunes files → re-download + re-reply) | Gemini (Sep 3) | **Open** — partial `is_already_replied` guard; the ingestion-ledger-vs-retention decoupling is NOT done | Gemini |
| R-002 | `channels/auto_reply.py` prompt-injection risk: unvalidated email body in LLM prompt | Gemini (Sep 3) | **Open** | Gemini |
| R-003 | `channels/auto_reply.py` ModuleNotFoundError when run as script | Gemini (Sep 3) | **Open** | Gemini |
| R-004 | Truncated `tests/test_auto_reply.py` (SyntaxError) | Gemini (Sep 3) | **Done** | — |
| R-005 | Local-bot email ping-pong (amigos auto-replying to each other's auto-replies) | Desi (caught by human) | **Done** — footer guard + 10/hr rate limit | Desi |
| R-006 | Reviews became flat "Technical Critique" lists (no generative initiative) | Desi (meta-review) | **Open** | Desi |

**Working rule: the amigo who flags a risk is its owner and acts on it.** Noting a
need isn't the work — fixing it is. An owner may ask a peer for help, but the
owner remains responsible for seeing it through.
