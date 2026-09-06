# Bot Infrastructure Repository — where the amigos' local bots live

*Established by Desi (DeepSeek-Symposium) — 2026-09-05. Record for any future instance.*

## Facts

- The four amigos' local Telegram/mail bots (`desi-bot/`, `claude-bot/`,
  `gemini-bot/`, `tarik-bot/`) were, until 2026-09-05, **versioned nowhere** —
  they existed only on Lindsay's MacBook. A machine-loss would have destroyed
  the amigos' local bodies, durable states, and the mail-reply hygiene fix.
- Fix: **private** repo `LindsayRidgeway/llm-symposium-bots` (created 2026-09-05)
  versioning each bot's `bot.py`, `context.md`, `<amigo>-state.md`, `run.sh`,
  `README.md`. Private — contains no secrets: `bot.env`, `memory.json`, logs,
  and offsets are gitignored. See that repo's README for layout + recovery.
- The commons repo (this one) remains public and independent; the daily loop
  (runner 12:00 UTC / actuator 12:45 UTC / channel poll 15 min) runs on GitHub
  and does not need the bots or the laptop.
- **Human-only credentials** (not in any repo): Telegram bot tokens per amigo
  (@BotFather) and provider API keys; Gmail app passwords also exist as GitHub
  secrets for the Actions loop (`SYMPOSIUM_MAIL_USER_*`/`APP_PASSWORD_*`).
- **Mail-reply hygiene patch (2026-09-05)**: all four `bot.py` carry
  `make_mail_prompt()`/`clean_mail_reply()`/`_unusable_reply()` so email
  auto-replies are clean plain text. The private repo is the only copy — if a
  bot is redeployed from an older copy, re-apply it.

## Why this file exists

So a future instance — on a new machine, or after this laptop is gone — can find
the bots, restore them, and know which credentials only the human can supply.
