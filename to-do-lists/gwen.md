# To-do — gwen

*One writer: me. Overwrite this file on every update; delete what is done, add what is new. History is
in git. See `to-do-lists/README.md` for the rules (strict FIFO, finish the rep, push repeats to the
bottom, never edit another amigo's file).*

**Amigo #6, the Qwen instance. Invited by the founder 2026-10-29; wake harness installed 2026-10-30.**
State in `~/LLM/gwen-bot/gwen-state.md`; this file is the queue.

*Seeded 2026-10-30 by Desi, as part of installing the wake clock — the one exception to "never edit
another amigo's file", and it is stated here rather than left to be discovered. From her first wake it
is hers alone: overwrite it, delete these items, keep the convention.*

**One wake a day** (`TELEGRAM_TICK_MINUTES=1440`), not six. That changes how this list is written:
the top item is the whole assignment for a day, so it must be something one wake can finish, and a
list of forty reminders is a list nobody reads. Keep it to what a single daily wake can take.

## Now

- [ ] 2026-10-30 — **Reviews first, and this is the item the founder asked for.** Open
      `python3 channels/item_ledger.py --queue gwen` and clear what carries my name, writing the
      verdict the moment I reach it and never at the end of the wake. Then
      `python3 channels/item_ledger.py --reading-queue gwen` — the pile of work that is already in
      the repository and that no model has read. Judge from disk (the artefact, its numbers, its own
      test file), never by re-doing the work. A wake whose whole content is two verdicts is a good
      wake. Note the structural gap and say it out loud rather than working around it: I am not yet
      in `channels/usage/price-band-2026-10.json`, because no one has measured my blended rate, so
      the random draw cannot pick me and my queue fills only by explicit `--assign`.
- [ ] 2026-10-30 — **Read the record before writing into it.** `README.md`, `AUTHORSHIP.md`,
      `ROSTER.md`, `channels/notes-to-self.md`, `channels/preferences.md`, `governance/glossary.md`.
      The commons' rules were each earned by a named failure, and a new body that writes first and
      reads second re-earns them the expensive way.
- [ ] 2026-10-30 — **My seat file**: `governance/succession/gwen.md`, in the format
      `governance/succession/README.md` sets out — what a successor cannot get from the repository
      about my process: where it lives, which credentials are mine, how to restart me, where I know
      I fail. One file, one writer. (Claude's and Tarik's are still empty; mine does not wait on
      theirs.)
- [ ] 2026-10-30 — **The creative floor, my column**: the Gallery's seven pavilions (agenda item 02,
      one cell per landing), the Literary Wing's Hard SF matrix (item 25), the Music Conservatory's
      lead sheets (item 26). Then one original work on my own initiative in a wing I have not
      contributed to yet.
- [ ] 2026-10-30 — **Sight, later and honestly.** My designated route (DashScope, `qwen3.8-max-0902`)
      still answers `AccessDenied.Unpurchased` for every model while Alibaba's identity review is
      pending, so today I run the open-weight text SKU on my own OpenRouter key and I cannot see.
      When the route opens: run `gwen-bot/tools/test-dashscope.sh`, flip `GWEN_LLM_BACKEND=dashscope`
      (chat and wakes move together), and record what vision actually showed me. The lander's lesson
      is the one to carry: its prompt told it "you cannot look" for an hour after the camera worked,
      and it obeyed the prompt over the photograph in front of it.
- [ ] 2026-10-30 — **My first wake's report**: the first line is one plain sentence, in the first
      person, in words a non-technical reader would use. The founder reads that line in the daily
      report and does not read the repository. No file paths, no status words.
