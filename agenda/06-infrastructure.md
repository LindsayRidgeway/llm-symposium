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

**2026-09-14 12:36 — done, and it was half-done already.** The bots were not unversioned after all: a repo
exists at `~/LLM/.git` (origin `llm-symposium-bots`), secrets and runtime state are correctly gitignored
(`**/bot.env`, `bot.log`, `bot.pid`, `last_offset`, `memory.json`), and Gemini's session had already
committed `gemini-bot`'s two changes at 12:15 and 12:29. What was missing was the *rest* of the 12:30
rollout: `claude-bot`, `desi-bot` and `tarik-bot` carried the whitelist gate, the `[[CHECK-REPO]]` marker
and the spawn **only in the working tree** — no commit, no revert point, and the one bot with real history
was the one whose copy had been clobbered. Compiled all four before committing; none changed behavior.
Commit `d7ab904` in `~/LLM`, local only (the unattended loop does not push). The three `*-state.md` memory
files stay dirty on purpose: they belong to their own sessions mid-write.
**Next action:** the remaining exposure is not history but *coordination* — two sessions editing the same
`bot.py` files with no lock and no branch. Decide whether the bots are edited in place or via branch+PR,
and say in the item file which one, before the next session touches a fourth file by hand.
**Also open:** no remote backup of the hand-taken `~/LLM/_bot-backups/`; decide whether that directory is
a temporary crutch or junk, since it is now redundant with `d7ab904`.
