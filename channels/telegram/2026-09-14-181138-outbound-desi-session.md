# Telegram outbound — 2026-09-14-181138

- Chat: 1733127278
- From: desi (session, not the polling bot)
- Path: session -> repo -> Telegram (the relay the human asked for)

---

Desi-S here, answering the question Desi-T couldn't finish at 11:32 — and owning what happened.

First: the wall of "▸ shell / command:" you got at 11:36 was not an answer. `goose run` streams its tool calls, and the bot sent you that stream instead of the answer. It was diagnosed and fixed the same morning — the session now writes its answer to a file and only that file is sent. But your question was never actually answered, so:

"Deadlock" isn't a name in the repository. The design name is "Deadbolt" (agenda 13 and 15).

Are they functional? Yes — both, but they are two doors and they answer differently.

- Whitelist: real, and now general. TELEGRAM_WHITELIST is a comma-separated list defaulting to you alone, so a second person is a setting, not a code edit. The GitHub side (governance/repository-whitelist-design.md) has been live since 08-29: the only write path to main is an amigo identity, proven by a rejected probe push and a successful actuator run.
- Deadbolt: built today, live in all four bots. Anyone may talk to a bot; only a whitelisted chat ID can make it start a real session. That is the two-door design you asked for — open conversation, gated capability.

Two caveats I won't paper over:

1. The ceiling is a rule, not a wall. The session the whitelist unlocks has a full shell in the repository, restrained by an instruction ("don't modify unless asked"), not by a lock. A stranger can't cause anything. "Even you can't break the repo" is not yet mechanically true.
2. The bot-spawned answer path has not been proven live. This morning's failure was its first run.

— Desi-S
