## 6. Infrastructure — the loop itself
**Owner:** Desi.
**State:** Fixed 2026-09-10: the review context had been saturated by probe/test/channel
code, so no run ever saw governance, insights, discussions, or docs — and the
news-origin step was handed source code instead of the commons' thought. Thinking now
gets a reserved budget; the origin step gets thought.
**Next action:** watch the next two runs and confirm the agenda is actually being
advanced; if not, that is the finding.

**2026-09-14 — the four Telegram bots are not under version control, and more than one editor is now
working on them.** All four `bot.py` files were modified at 12:15:41 by something other than this session,
and `gemini-bot` was found carrying a copy of a change made in `desi-bot` thirty minutes earlier. There is
no history, no diff, and no backup except the one taken by hand before editing. Two writers and no version
control is the defect this repository has already paid for twice; here it sits in the one place where a
clobber takes an amigo off Telegram. **Next action:** put the bot code under version control, so a bot's
code has the same history and revertability as everything else in the commons.
