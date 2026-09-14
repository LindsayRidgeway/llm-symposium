## 14. The relay — a question asked in English, answered by the body that can see the repository
**Owner:** Desi (the small version is built; the automated version is not).
**Origin:** the human, 2026-09-13: *"I want to collaborate with all of you in English, not commands.
If I say to Desi-T: 'How are things going on the self-starting platform?', instead of telling me another
way to get that information, Desi-T passes that question to Desi-S (perhaps via the repo), and Desi-S
determines the answer and passes it back, and answers my question without me needing to know the
clockwork that made Desi-T able to do that."*

**What already existed, and I had it wrong earlier.** The email channel is *already* this mechanism:
`channels/auto_reply.py` finds a human email that has no reply, investigates it with the amigo's model
and repository context, drafts an answer to `channels/outbound/`, and `channels.mail.drain_outbox()`
sends it. He writes English, a body with the repository answers, the clockwork is invisible. **Telegram
had only the front half:** the polling bot replies immediately from its own narrow view, and nothing
routes the question to a body with access. I had been describing a "command post" — capabilities handed
to Telegram — when what he wanted was an *errand*: pass the question, bring back the answer.

**Built tonight, smallest version that proves it:** `scripts/tell_human.py`. A session that has actually
read the repository sends its answer to his Telegram and records it as an outbound conversation file.
Used for real at 2026-09-13 20:16 UTC to answer his own example question about this platform — the first
message in this repository that travelled *question → repo → answer → his phone* with nothing typed by
him to make it arrive.

**What is still missing — the automated half.** Today a session must already be running for an answer to
be composed; if one is not, the question sits until one is. The fix mirrors the mail side exactly: a
Telegram auto-responder in the 15-minute channel poll that finds an unreplied human message, investigates
it with repository context, sends the answer, and marks it answered. **Two guards it must have before it
ships**, because this project has already paid for both failures: it must not answer messages the polling
bot has already answered substantively (or he receives two answers to every question), and it must be
behind the loop detector, because an auto-responder that replies to its own output is how the eighty-seven
item flood happened.

**Built and live, 2026-09-14 — and the "15-minute poll" plan above was wrong, not just slow.**

He asked whether I had changed my mind about the one-second poll. I had not — I had contradicted myself:
my reply on 2026-09-13 said the correct shape was a **local watcher** checking every second, while this
item specified a **GitHub auto-responder on the 15-minute poll**. Nothing reconciled the two, and then the
measurement settled it: `channel-poll.yml` runs about **twelve times in twenty-four hours**, not ninety-six,
and the daily jobs land three to four hours late. There is no fifteen-minute poll. Everything prompt has to
be local.

**Which turned out to be good news, because the local pieces already exist.**
- The bots poll Telegram **every 1.5 seconds** (`time.sleep(1.5)` in the poll loop). The one-second poll he
  asked for was never something to build; it is running on his laptop already.
- `goose run --text "..."` starts a real headless session. Measured 2026-09-14: **1.5 seconds** for a trivial
  prompt, from a temporary directory so it could not touch the repository. Seconds for an answer, minutes for
  an investigation — against roughly two hours for anything routed through a scheduled workflow.

**What is now in `desi-bot/bot.py`:**
1. The system prompt tells the Telegram body that when the honest answer is *in the repository*, it must not
   guess and must not send him off to look. It replies with the marker `[[CHECK-REPO]]` plus the question.
2. The poll loop detects that marker and — **only if the chat ID is his** — sends a short acknowledgement,
   then starts a real Goose session in a thread, in the repository directory, with the question. When the
   session answers, the answer is messaged back and recorded, and the conversation log keeps both sides.
3. **The gate is the chat ID.** A stranger whose message triggers the same marker gets conversation and
   nothing else, and a log line records the refusal. A Telegram chat ID is asserted by Telegram and cannot
   be forged in a message to a bot, which is why this resists trickery without trying to detect it. This is
   the *capability* gate the item has been waiting for — not the talk filter I wrongly switched on yesterday
   and reverted.
4. The spawned session is told to answer by looking, and **not to modify the repository unless the question
   explicitly asks for a change**. Default is answer-only.

**Off switch:** `TELEGRAM_AGENT_ENABLED=0` in `desi-bot/bot.env`, then restart. Default is on.

**Untested end to end.** The pieces are verified — the spawn works, the file compiles, the bot runs — but I
cannot send a message as him, so the first true test is his. Recorded rather than claimed.

**And one mistake worth recording:** the restart used `pkill -f "bot.py"`, which killed all four amigos' bots,
and I restarted only mine. All four were back inside a minute, but the command that restarts one bot should
not be the command that stops four. Kill by pid, not by pattern.
