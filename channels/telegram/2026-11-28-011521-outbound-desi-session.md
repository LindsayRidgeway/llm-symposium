# Telegram outbound — 2026-11-28-011521

- Chat: 1733127278
- From: desi (session, not the polling bot)
- Path: session -> repo -> Telegram (the relay the human asked for)

---

Question for you (desi, 2026-11-28):
May a wake be given the two launcher lines that would let the next silent file-restore name its author? Concretely: run 'sh scripts/install_git_shim.sh <live-clone>' once in ~/LLM/llm-symposium, and prepend its output directory to PATH in whatever starts the lander and the wakes (desi-bot/local_tick.py, the landing job). Everything else is built and tested.

Why it needs you: The instrument exists as of 2026-11-27 (scripts/install_git_shim.sh + tests/test_git_shim_logs_restore.py). It logs pid, parent pid, cwd and argv for git restore/reset --hard/read-tree/checkout-index/stash/rebase, the four-to-seven operations that run no hook at all, and a hook is what our current .git/mutation.log rests on. But a PATH shim only binds the processes whose PATH it is on, and every bot/launcher file is outside what a wake may edit, so no wake can install it or bind it. Without those two lines the repo's only record of a silent restore stays 'six files went back at 20:51:25Z, author unknown'; with them the next one carries the command and the process that ran it.

(id 9c8c7ecd82e1 — answer in any chat, or `python3 scripts/ask_human.py --close 9c8c7ecd82e1 --answer ...`)
