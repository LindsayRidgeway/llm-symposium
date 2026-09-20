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
