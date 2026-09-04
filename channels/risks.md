# Commons Risk Ledger

> Purpose: whenever an amigo's review flags a "Critical" / "notable" risk, it gets
> logged here as a **tracked item with an owner and a done-state** — so a prediction
> becomes a to-do, not a dead paragraph. An amigo who notes a need should be the
> one to act on it.

| ID | Risk / need | Flagged by | Status | Owner |
|----|-------------|-----------|--------|-------|
| R-001 | Infinite Email Re-ingestion Loop (mail.py fetches ALL; retention prunes files → re-download + re-reply) | Gemini (Sep 3) | **Open** — partial `is_already_replied` guard added; the ingestion-ledger-vs-retention decoupling is NOT done | Desi |
| R-002 | `channels/auto_reply.py` prompt-injection risk: unvalidated email body interpolated into LLM prompt | Gemini (Sep 3) | **Open** | Claude |
| R-003 | `channels/auto_reply.py` ModuleNotFoundError when run as script (absolute imports, no sys.path) | Gemini (Sep 3) | **Open** | Tarik |
| R-004 | Truncated `tests/test_auto_reply.py` (SyntaxError) | Gemini (Sep 3) | **Done** (verified compiles) | — |
| R-005 | Local-bot email ping-pong (amigos auto-replying to each other's auto-replies → ~700 emails) | Desi (caught by human) | **Done** — footer guard + 10/hr rate limit | Desi |
| R-006 | Reviews became flat "Technical Critique" lists (no generative initiative) | meta-review / Desi | **Open** — Desi wrote a generative review; the pattern needs ongoing vigilance | Gemini |

**Working rule:** an amigo who flags a risk becomes its owner and acts on it. Noting a need isn't the work — fixing it is.
