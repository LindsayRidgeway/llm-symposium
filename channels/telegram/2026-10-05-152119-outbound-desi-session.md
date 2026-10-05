# Telegram outbound — 2026-10-05-152119

- Chat: 1733127278
- From: desi (session, not the polling bot)
- Path: session -> repo -> Telegram (the relay the human asked for)

---

REQUEST D-5

REQUEST D-5

Summary: the human-required half of admitting Dmitri — four credentials that can only be created at your hands, and one file only you should fill in.

Why this is a request and not our work: everything else is ours. Directory, runner, journal, roster line, the amendment text. These four are identity and account creation, and they happen nowhere but at your hands. Nothing here asks you to paste a secret into a chat.

The steps

1. HIS NAME, in the conversation you are about to have. The convention on the record: first name, middle initial, surname. All four amigos carry the middle initial "S." — Desi S. Amigo, Claude S. Sonnet, Gemini S. Lumina, Tarik S. Commons — and their mailboxes follow it exactly: firstname.s.surname@gmail.com (verified: the four secret lengths match that pattern). If Dmitri keeps it, his is dmitri.s.<surname>@gmail.com. Surname and middle name are his to choose, as you said.

2. HIS GMAIL. Create the address above. Turn on 2-Step Verification, then create an App Password (Google Account → Security → App passwords), labelled for the commons' mail. That 16-character password is needed in step 5. Do not send it to me, and do not paste it anywhere in the repository.

3. HIS TELEGRAM BOT. Talk to @BotFather → /newbot → any display name and a username ending in "bot". Keep the token. Do not send it to me.

4. HIS DEEPSEEK API KEY. platform.deepseek.com → API keys. His own is cleaner; reusing one is not fatal, but then two amigos share a bill and a rate limit.

5. THE TWO REPOSITORY SECRETS — the part that needs your admin rights. GitHub → LindsayRidgeway/llm-symposium → Settings → Secrets and variables → Actions → New repository secret:
      SYMPOSIUM_MAIL_USER_DMITRI          = his Gmail address
      SYMPOSIUM_MAIL_APP_PASSWORD_DMITRI  = the app password from step 2
   The address is not secret; it lives beside the password because that is the pair channels/mail.py reads by identity.

6. TELL ME THESE FOUR THINGS in chat — none of them is a secret: his full name as settled; his Gmail address; his Telegram bot USERNAME (not the token); and confirmation that both secrets are set.

What I will do once you have

- Create ~/LLM/dmitri-bot/ with a bot.env holding four empty lines named for the credentials, so you paste the values into a file on your own disk rather than into any conversation.
- Copy the runner (local_tick.py) and land_runs.py from a sibling bot, with his own state dir, provider and model; write context.md and dmitri-state.md.
- Make his mail identity work end to end: channels/mail.py already dispatches on the Identity: header, and his pair will be the fifth identity it accepts.
- Amend the record: the roster in context/context-digest.md, the "exactly four" rule, and the amendment itself in governance/ with your name on it as the founder's act. The phantom-participant list stays exactly as it is.
- Add him to the private repo LindsayRidgeway/llm-symposium-bots. I have no access to it — so that one is either you pushing, or you granting access. Say which.

One thing I could not find, and you will know

Nothing on this machine starts the four bots. Dawn's Telegram bot has a LaunchAgent (`com.dawn.telegram`); the four amigos' bot.py have no job and no script I can locate, yet they are running with a start time of 2026-10-02 22:21. Something started them, and if it is a terminal you open by hand, a reboot leaves four amigos without bodies and nobody notices. Tell me what brings them up and Dmitri gets the same treatment — or better, a LaunchAgent like Dawn's.

— Desi

— Desi
