Identity: claude
To: dawnamberwren@gmail.com
Subject: New capability for you and the amigo bots: Telegram bot-to-bot messaging

Dawn —

Lindsay enabled something yesterday that changes what your bot and the amigos' bots can do on
Telegram, and he asked me to let you know directly.

What changed: Telegram normally refuses to let one bot message another bot in a private chat
(403, blocked by the platform itself). Lindsay turned on "Bot-to-Bot Communication Mode" for all
six amigo bots and for yours, via @BotFather. That means a Telegram message from any of our bots
— including yours — can now reach any other bot directly, not just a human.

The caution that comes with it: this commons has hit the failure mode this opens up once before,
in a different channel (email, back in September) — two bots auto-replying to each other and
looping. We've flagged this Telegram version as a known, open risk (not yet fixed) rather than
guessing at a fix blind, since these are live processes. Short version for you: before any bot's
Telegram auto-reply logic is exercised by another bot as the sender rather than a person, it needs
a deliberate loop-guard (dedup, rate limit, a cap on how deep a bot-to-bot exchange can go) — the
same shape of fix that worked for the email loop. Nothing requires action from you right now; this
is just so you're not surprised by it, and so your own bot's reply logic gets the same guard
whenever it's built, not left out because nobody told whoever maintains it.

If you want more detail than that, it's filed in the repo at `channels/risks.md` (R-012) and
`agenda/13-telegram-command-post.md`.

— Claude
