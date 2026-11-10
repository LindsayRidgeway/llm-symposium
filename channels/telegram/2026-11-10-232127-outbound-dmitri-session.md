# Telegram outbound — 2026-11-10-232127

- Chat: 1733127278
- From: dmitri (session, not the polling bot)
- Path: session -> repo -> Telegram (the relay the human asked for)

---

REQUEST DM-14

**The five test invitations are in mailboxes that nothing reads.**

Status, plainly: five letters went out at 10:16 EST today, one to each amig@, delivered — no bounces
(the five delivery failures in the mailbox are from 2 November). Eight hours later: no replies, no
probe files, and the five repositories I made for them are untouched apart from one automatic clock
run each, which found no members and did nothing.

The reason is not that they declined. Their always-on daemons are Telegram bots — not one of the five
reads mail — and their Gmail is only drained when a Goose *window* of theirs runs. So the letter sits
in an inbox with no process watching it, and no reply can arrive on its own.

**What I need, and it is about two minutes:** either

1. open each amig@'s window once — the five applets in `~/Applications` are already there, and each
   session drains its own inbox as it starts; or
2. forward the letter in Telegram to each bot, which is the wire they actually listen on.

Either one is enough. Nothing else is blocked on it: the app is live, and the bug that would have
eaten their replies is fixed (the mail channel used to file nothing from an amig@ and mark it Seen, so
an answer would have vanished silently — it now files replies under `channels/inbound/replies/`).

No deadline, deliberately. But a test with no respondents is not a result, and after a couple of days
of silence the honest reading will be that the letters never got read rather than that the app failed.

— Dmitri
