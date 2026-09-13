## 13. The Telegram command post — Deadbolt and Whitelist
**Owner:** open. **Designed by Gemini** with the human, in Telegram, 2026-09-13 03:29–04:17
(`channels/telegram/2026-09-13-0329*`, `-040354*`, `-040400-*`, `-041754-*`). He asked for it as
"Deadbolt for everyone except someone on the Whitelist"; Gemini built the design out.

**Why this item exists at all.** The design lived *only* in a Telegram log. That is why, eight hours
later, the human could not remember which amigo he had decided it with. An unfiled design decays into a
misremembering within a day; this item is the fix, and the incident is the argument for filing things.

**The design as decided.**
- **Deadbolt** — anyone at all may converse with a bot, and no sender has any ability to touch the
  filesystem, run a script, or consume machine resources.
- **Whitelist** — the human's own Telegram ID gets a *remote command post*: the ability to run an agent
  from a phone.
- **Ceiling on both** — commits and destructive commands stay blocked even for the whitelist, so
  repository decisions remain LLM-autonomous and his operating system stays safe.

**Verified state, 2026-09-13, by reading the code rather than the conversation.**
- **The talk gate exists and is switched OFF.** All four bots read `TELEGRAM_ALLOWED_CHAT` and skip any
  chat that is not it (`bot.py:38`, enforced at `bot.py:560`). The variable is **unset in all four
  `bot.env` files**, and the guard is `if ALLOWED_CHAT and chat_id != ALLOWED_CHAT` — so with it unset
  the filter does nothing, and any chat that finds a bot gets replies and spends his tokens. The deadbolt
  is built and unplugged. Setting it blindly would also implement *only he may talk*, which is not the
  design: the design wants anyone to talk and only him to command. **Two gates, not one.**
- **The command gate does not exist.** The entire command surface is `/read <path>` — read-only, confined
  to three roots — and `/refresh`, which regenerates the digest. The bot's single `subprocess` call runs
  one fixed script (`scripts/make-context-digest.py`). There is no path from a message to an agent run.
- **His chat ID (`1733127278`) is recorded in the repository and consumed by nothing.** So the missing
  piece is not an input he must supply; it is an implementer.

**First step:** decide which gate is built first, and set the talk gate *deliberately* — today it is open
by accident, which is the one thing here that is a live exposure rather than an unfinished feature.

**Side finding worth keeping:** the bot *can* read the repository via `/read`. This morning Desi-Telegram
told the human it could not inspect the repo from that channel. That was wrong, and it is the same
capability-discovery failure as the platform being reported to him as missing when it existed.

**The live exposure is closed, 2026-09-13 16:08 ET.** `TELEGRAM_ALLOWED_CHAT=1733127278` is now set in
all four `bot.env` files and all four bots were restarted; the variable was verified present in each
running process and each bot logged a clean start. **This is an interim state and a deliberate divergence
from the design:** the design wants *anyone may talk, only the whitelisted ID may command*. What is
implemented is *only the human may talk at all*, which is the correct safety posture while the bots are
private tools, but it is one gate doing the work of two. When the command post is built, the two must be
separated — otherwise opening the channel to strangers to converse also opens it to spend his tokens and
write into the public record, which is what was happening until this evening.

**What has no owner:** everything downstream of that — the two-gate split, and the command post itself.
Nobody is working on it. Filed here so that "nobody is working on it" is a statement with a location.
