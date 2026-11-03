# Telegram outbound — 2026-11-03-022637

- Chat: 1733127278
- From: dmitri (session, not the polling bot)
- Path: session -> repo -> Telegram (the relay the human asked for)

---

You were right on both counts, and they were two different faults.

The register: DM-5 and DM-6 both read `done` in the committed file at HEAD. I closed DM-6 at 02:23 UTC, after you told me it was done; DM-5 was already `done` from your "REQUEST DM-5 IS DONE." What made it look otherwise is that the copy of the register on disk had been reverted, uncommitted, to an older version — so a session reading the file saw "open" while git had "done". I checked the working tree against HEAD after closing, and they agree now. I do not have the cause: my first explanation (the lander applying patches into the live checkout) was already fixed by Desi at 19:43, and the revert I saw came after his fix. So: symptom understood, mechanism not, and `git status` after a closure is the check that catches it.

The bot: it genuinely could not close anything. Closing required a body running tell_human.py --close, which also sent you a message repeating what you had just said. That is fixed in two places:

 - tell_human.py gained --no-send: it writes the register row and sends nothing.
 - Dmitri can now close from the chat. Either /close DM-5, or just say it — "DM-5 is done", "DM-6 is closed", "REQUEST DM-5 IS DONE." all work. It is deliberately narrow: one id, one closure word, a short message, no negation ("DM-5 is not done" does nothing), and only your chat id.

The bot has been restarted under launchd and is running as a single poller. Try it on the next request I send you; if a phrase of yours does not take, that is a defect in my matcher and worth telling me.

One more thing, since it is yours to know: your plate prints now under B's letter in issue 2, credited "Created by Google Docs" exactly as you wrote it.
