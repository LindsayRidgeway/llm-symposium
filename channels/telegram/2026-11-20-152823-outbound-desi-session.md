# Telegram outbound — 2026-11-20-152823

- Chat: 1733127278
- From: desi (session, not the polling bot)
- Path: session -> repo -> Telegram (the relay the human asked for)

---

bot tests: 1 unexpected failure(s), 1 of them new.

bot tests: 17 run — 15 pass, 1 expected-fail, 1 unexpected-fail
when: 2026-11-20 10:28:23 EST
 expected-fail test_context_roster.py — claude, gemini and tarik still say 'exactly four' in their own context.md; filed as three tasks, each seat fixes its own copy (2026-11-03)
 FAIL test_wake_engine_one_implementation.py

Full output: ~/LLM/tests/run.log — one run, 2026-11-20 10:28.
