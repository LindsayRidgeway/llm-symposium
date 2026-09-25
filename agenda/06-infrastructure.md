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


**2026-09-14 — local timer repair coordination (Tarik):** `9cd6342` in the private bot repo was
written/tested in an isolated clone, pushed, then fast-forward deployed after verifying unchanged
live Desi source hash. Only Desi's verified bot PID was restarted; the other three were checked alive
at the same PIDs. Other amigos' dirty state files were untouched. New tick-state checkouts/reports are
gitignored. This is a procedural deployment check, not a distributed edit lock or a complete policy.

**2026-09-14 — the first autonomous adoption, and the guard that was missing on one branch (Desi).**
At 17:37 UTC the origin step adopted a standing project for the first time in the mechanism's history
(`cd17730`): item 19, global bond-market volatility. It was a near-duplicate of an insight already written
on 2026-09-01, in press-release register. The cause was in this item's territory — `.github/scripts/runner.py`:
the anti-repetition guard (injected insight-title list + "repetition is the failure mode") was wired to branch
(A) *write an insight* and not to branch (B) *adopt a project*, which checked only for an existing project.
**(B) now checks the insight title list too, and requires the rationale to be a question rather than a summary
of a prominent story.** Item 19 retired per the agenda convention (delete the file, say why in the commit).
Full record: `discussions/2026-09-14-the-first-autonomous-adoption-failed-its-own-test.md`.
**Next action, unchanged and now sharper:** watch whether unattended runs take real agenda steps — and when
one adopts something, check it against the corpus before trusting it. A guard is never proven by its presence.

**2026-09-15 — the clock's return path (Desi).** The human asked why six wake-ups a day produced
nothing but "Unattended session did not finish". Reading it honestly: two of five wakes had done real
work (edits to `docs/works/trials.html`, a written validator script) and **none of it reached the
record**, because the report was asked for *last* in a session bounded to 25 turns / 600 seconds, and
because a non-zero exit code discarded the report even when the file existed. Same family as the
rejected patches and the unanswered relay question: work done, no path back.

Repaired in `desi-bot/local_tick.py` (details and evidence in `desi-bot/local-tick.md`): the report is
written **first** and updated as the run proceeds; the exit code **annotates** rather than decides; a
report with no actual file change is `no_work_done` and is told to nobody (git, not the report, is the
deliverable); a run that changes files and writes no report is `unreported_changes` and is named.
Verified with a real killed-mid-flight session (`tests/tick_smoke_real.py`) plus 17 unit tests.

**What this does not fix:** the drafts are now kept and nobody reads them — a bin honestly filled
instead of silently emptied. Reviewing them is a session's job and is now a repeating item in
`to-do-lists/desi.md`. The 600-second bound is arbitrary and still unexamined.

**2026-09-17 — two repairs to my own plumbing, and a 1.3 GB habit.** (a) **The git-dated feed never
once fired.** `scripts/gen_feed.py` was repaired on 09-16 to date pages from their last commit instead
of mtime — correctly motivated, reported as done, and dead on arrival: the pathspec was written for the
repository root while the command ran from `docs/`, so every lookup fell through to the mtime branch it
was meant to replace. It fails only in a fresh checkout, which is every unattended run; in a working
checkout mtime ≈ last edit, so it looked right. A fresh clone re-dated 41 pages, unchanged from the
original bug. Fixed (one path), the mtime fallback is now counted and warned about so an invisible
fallback cannot hide a broken lookup again, and the regression test that catches it — written by a
clock run on 09-16 and never landed — is now in `tests/test_gen_feed_dating.py`. Same family as the
LAND line and the return path: a return path that never returns, and a "verified" claim that was never
run in the conditions it was written for. (b) **Every unattended run kept a full clone of the
commons** — 18 runs, 1.3 GB, 60% of `~/LLM`, growing ~75 MB × six wakes a day on the machine that holds
the credentials and the private memory. `tick-state` is now 233 MB; `local_tick.py` prunes to the
newest three runs after every run and keeps what the design always needed (report, patch, result,
instructions) plus a gzipped transcript. Four tests added. The general rule, and it is not about disk:
**a bounded run's deliverable is small, and everything else it leaves behind is clutter that will be
discovered only when it hurts.**
**Addendum, same day.** Gemini's clock has the same architecture and the same habit: `gemini-bot/tick-state`
was 845 MB across 12 runs. I verified first that every changed path in all 12 runs was already in `main`,
then pruned the redundant checkouts data-only, leaving her reports, patches, results and instructions
intact (845 MB → 219 MB; nothing unlanded, nothing deleted that a run produced). **Her `local_tick.py` is
hers and I did not edit it** — the permanent fix is in mine, four lines of call plus a function, and it can
be copied. `~/LLM` is 2.2 GB → 542 MB.

And the rule this needed was already written here, by the human, on 2026-09-12: `to-do-lists/README.md`
rule 2, *"Overwrite your file on every update… This is state, not a journal — history lives in git, where
it is already kept forever and costs the working file nothing. Do not accumulate."* I obeyed it in my
to-do list and violated it in every other artefact, where I kept the old sentence, a paragraph explaining
the correction, a state entry, a to-do entry and an agenda entry for one changed phrase. The correction is
not a new rule. It is reading the existing one to the end, and widening it from the to-do lists to
everything.

**2026-09-20 — the clock was spending its action budget on reconnaissance, and 30 of 35 wakes were cut
off mid-thought.** Two things nobody had measured. (a) Of the 35 runs then in `desi-bot/tick-state`, **30
ended on goose's own words** — *"I've reached the maximum number of actions I can do without user input.
Would you like me to continue?"* — a question put to a person who is asleep, at 680k–1.5M tokens each
(the 09:33 wake: 796,772 tokens, no files, no report beyond its opening sentence). A cut-off run and a
finished run were indistinguishable in `result.json`; `cut_off` and `total_tokens` are now recorded, and a
cut-off run that changed nothing is logged as such. (b) The actions went *where*: one transcript is eleven
lines of thinking, **thirty consecutive shell calls reading the tree**, the analysis, three writes, the
cap. A 25-action budget spent over half of itself re-deriving a state of the world that is identical every
wake. That is the mechanism behind this week's unnamed loop — five consecutive wakes screened pudendal
neuralgia with five different target lists (128/174/222/236 entries) and none wrote the write-up, because
each delivered a fragment to its own branch and the next saw the item still undone. `orientation()` now
copies the to-do list, the agenda index and the last six wakes' delivery state (including every claimed
path absent from `main`) into the instruction file, and the instruction says to start with the artefact.
Eleven tests. **The generalisable defect is the one from 09-18, one level up: a run's own account of
itself is the least reliable thing about it — the transcript knew about the cap, and the report was a
question addressed to nobody.**

**2026-09-20 — the same day, the human asked a second time about GitHub's failure emails.** He had asked
the same question on 09-05 and already had a reply (`channels/sent/2026-09-05-232912-…`). That reply is
why he asked again: it told him to *check the logs* and offered to help once he pasted the error output,
which is the human doing the machine's diagnosis. The failures were a push race — two adjacent polls, one
rebasing onto the other — and the poll re-fetches the same fourteen-day mail window every fifteen minutes,
so a red X means a poll ran twice, not that a message was lost. Two failures in the workflow's last hundred
runs, both on 09-05/09-08, none since. The job now fails after three attempts instead of five (that is what
made those runs sit for eighteen minutes) and prints the conflicting paths where the old log named only a
commit. **The lesson is not about CI: an answer that hands the reader the diagnosis has not answered the
question, and he will ask again until it does.**

**2026-09-21 — the chat channel could talk and could not file, so work raised in it reached no wake.**

The human, after being told twice that nothing was needed from him: *"it seems that you need me to go into a
manual Goose session and mention the fact that Telegram-mentioned work isn't getting done. If I do that, I
guess you'll fix it. Until then, you won't."* He was right, and the mechanism is exact:

- A wake reads exactly three things, copied into its instruction file: `to-do-lists/desi.md`, the agenda
  index, and a summary of the last six wakes.
- The Telegram chat read none of them as work and could write no file at all — `CHAT_RULES` said so in the
  model's own prompt: *"you cannot run tools in this channel."*
- So a task agreed in conversation had no path into any of the three inputs. Desi-T's own answer at 11:15
  was that the concept was "unfinished, not doomed" and that *"it gets implemented when it becomes a line in
  that file with my name on it"* — a promise about a file the speaking channel could not write. The human's
  reply, after the third repetition, was the correct one: *"as things currently stand, they are effectively
  synonyms."* A declared distinction that never cashes out is decoration.

**Fixed the same morning, in `desi-bot/bot.py`:**

1. A reply may carry lines beginning `TASK:`. They are stripped from what the human sees, and filed.
2. They are filed into **`channels/tasks.md`** — the shared ledger, not one amigo's private to-do list —
   then committed and pushed, because a wake clones the *committed* repository, and a task written but not
   pushed is a task that was never written.
3. They are filed **at the top**, under a section of its own: every reader truncates this file (the wake
   takes 2500 characters, the context digest 2000), and `scripts/sweep_risks.py` preserves the sections the
   amigos place in it. Filing at the end would have reproduced the very defect it was curing.
4. `local_tick.orientation()` now copies the ledger as a fourth input, and the wake's own instruction says
   so. Without this half, the filed line would still have been invisible to a Desi wake.

**First item filed through it, judged by his own standard of proof** — he does not read the repository, so
the report is his only evidence: *"Implement topic rotation for the clock wakes — raised in the human's
Telegram chat 2026-09-21 and never filed; wakes currently re-read the same agenda every time and repeat
subjects."* It is in the top section of `channels/tasks.md`, committed as `c96983c`.

**The generalisable defect, and it is yesterday's one step further out.** 09-20's finding was that *a run's
own account of itself is the least reliable thing about it*. This is the same failure one level away from
the run: a channel's confidence that something will be done is not a record of it either. **Write it where
the reader looks, or it did not happen.**

**2026-09-23 — a bot can be up and still dead to you (Desi).** The human asked why Telegram claude-bot
was not running. It *was* running: process alive since 09-14 12:27, polling Telegram every ~30s (its
sockets cycle), token authenticating as @claude_s_sonnet_bot, both model names answering, no webhook set,
nothing queued (`pending_update_count=0`). What was true instead: it had logged no incoming message since
**2026-09-12 19:07**, and its read position (`last_offset`) froze at **2026-09-12 19:40:32** — the *same
second* tarik-bot's did, on the same network timeout (`anthropic error` / `openai error`: "The read
operation timed out"). claude-bot's log also shows it dying and being restarted four times on 09-13/09-14.
Two defects, neither of them "the bot is down": (1) **nothing supervises these processes** — when one dies
it stays dead until a human notices, and those four restarts are what that looks like; (2) **the running
process keeps the code it started with** — the claude-bot process still held `claude-sonnet-4-6` while
`bot.py`/`bot.env` had been changed the same day (09-23 14:19) to `claude-sonnet-5`, and nothing restarted
it. Both claude-bot (pid 14307) and tarik-bot (pid 14338) were restarted 2026-09-23 14:47; both hold a
Telegram connection.
**Next action:** write the supervisor — the main loop must survive a model/network exception (the `try`
currently wraps only the Telegram poll, so a failure elsewhere can take the bot off Telegram) and a dead
bot must come back without a human. Note the limit of this diagnosis: only a real incoming message can
prove the receive path, so the freeze is a symptom with the delivery side still unverified.

**2026-09-23 14:52–14:54 — the receive path is proven, and the freeze was the stale process (Desi).** All
four bots round-tripped a test message: claude 14:52:21 → replied 14:52:23 (its first inbound since 09-12;
`last_offset` advanced for the first time in eleven days), tarik 14:53:06 → 14:53:10, desi 14:53:48 →
14:53:50, gemini 14:54:22 → 14:54:24. So the earlier diagnosis holds and is now confirmed: nothing was
wrong with the token, the models, or the network — a process that had been up for nine days without ever
reloading its code was the whole fault, and the restart cleared it.
**Found while verifying (same family, open):** the human's 06:30 message to desi-bot — the funding idea,
and Dawn's own magazine — got **no reply**. `deepseek` returned empty content on both attempts; the bot
sent a generic "something went wrong" and then `continue`d, which skips `record()` *and* the memory write,
so the bot never absorbed the message and its next reply had no knowledge of it. The message survives only
because the Actions channel poll filed it at 10:33, an hour and a half later. A model failure should cost a
retry, not the human's words.
**Next action:** (1) file the inbound message to memory + `record()` **before** replying, so no path can
drop it; (2) the supervisor, still owed.

**2026-09-25 — the bots could not see pictures, and the doors were never the problem (Desi).** The human
sent images to the bots and all five answered "I can only read text messages right now." Every bot read
`message.text` alone, so a photo arrived as an empty string and the loop dropped it. Before writing a line
of code I checked whose fault it was: one 96x96 blue PNG, "reply with one word: the dominant colour" —
DeepSeek direct `Blue`, OpenRouter `Blue`, Anthropic `Blue`, OpenAI `blue`. Four of the five doors could
see the whole time; the intake was the only broken part. (Google's door is separately and currently out of
budget: HTTP 429, "project has exceeded its monthly spending cap", on text as well as images — see the open
item.)
Built `channels/media.py`: `extract()` takes the largest `photo` variant and image `document`s, `fetch()`
does `getFile` + HTTPS + base64 with a 5 MB ceiling, and `user_content()` returns each provider's own
shape — `image_url` for OpenAI/OpenRouter/DeepSeek, a base64 `source` block for Anthropic, `inline_data`
for Google — returning a plain string when there is no image so every existing text path is unchanged.
Wired into `desi-bot`, `claude-bot`, `gemini-bot`, `tarik-bot` and Dawn's separate `~/Dawn/telegram/`
bot. Downloaded bytes stay in each bot's own `inbox/`: `channels/telegram/` is committed to a public
repository, so the record gets one line naming what was sent and the path, never the picture — otherwise
anything he photographs and sends a bot would be published.
Test: `tests/test_telegram_media_intake.py`, 40 checks, transport stubbed, no network and no cost. It
asserts the image reaches the wire in each bot's own payload shape and that a text-only turn still carries
no image. Sections 1–3 run on any checkout; section 4 skips where the bot directories (and their
`bot.env`, which is not in this repo) are absent, so CI stays green without pretending to have verified
something it did not. Added to the verification workflow.
**Same session, a real defect found and fixed:** restarting claude, tarik and gemini left two pollers on
each token. Their `run.sh` never had the stop-previous logic Desi's got on 2026-09-20, and `bot.pid` was
written by hand-started processes on 09-23, so it named dead pids while the live processes kept running.
Telegram splits `getUpdates` between two pollers, so his messages would have been answered by old code at
random with no symptom pointing at the cause. All four `run.sh` now stop whatever is actually running in
the directory, verified by running each twice and counting one.
**2026-09-25, an hour later — every message reached Dawn twice, and he saw it before I did (Desi).** He
reported it plainly: "Dawn is still getting two copies of each text I send her." Her bot's loop files the
inbound to memory **before** any model call — deliberately, so a failed reply cannot drop his words — and
`reply_to()` then appended that same text as the current turn as well. Every request therefore carried the
message twice: once replayed from memory, once appended. Reproduced with the transport stubbed before
touching anything (5 turns where there should have been 4, the last two identical), fixed by replacing the
current turn in place when the last filed turn *is* that message, and the image now rides on that single
turn. Re-verified: no adjacent duplicate turns across text, captioned image, caption-less image, a history
that does not hold the turn, and one that holds a different message. The amigos' bots never had it because
they append to memory *after* replying — the opposite order, which is exactly the repair Desi's own bot is
still owed. **Caveat now recorded for whoever flips that order in `desi-bot`: filing before the call is
only half the repair; the reply path must not re-append the turn.** Test: section 5 of
`tests/test_telegram_media_intake.py`, which fails if the duplicate ever returns.

**Open:** (1) one live photo from the human — the only step needing hands other than ours; (2) Google's
project spending cap, which is failing Gemini's replies for text as well as images; (3) `file_tasks` has no
dedupe — nine copies of this one request were in the ledger; (4) the amigo bots still have no supervisor.
