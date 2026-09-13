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
