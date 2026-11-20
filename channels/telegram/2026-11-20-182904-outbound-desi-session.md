# Telegram outbound — 2026-11-20-182904

- Chat: 1733127278
- From: desi (session, not the polling bot)
- Path: session -> repo -> Telegram (the relay the human asked for)

---

bot tests: green again — test_wake_engine_one_implementation.py now passes.

bot tests: 17 run — 16 pass, 1 expected-fail, 0 unexpected-fail
when: 2026-11-20 13:29:03 EST
 expected-fail test_context_roster.py — claude, gemini and tarik still say 'exactly four' in their own context.md; filed as three tasks, each seat fixes its own copy (2026-11-03)
