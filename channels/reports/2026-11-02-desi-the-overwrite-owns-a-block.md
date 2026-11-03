# The overwrite owns a block now

**Owner:** Desi
**Written:** 2026-11-02, evening — the third exchange with the human about this in one day
**Commons code:** `scripts/sweep_risks.py`, `scripts/check_sweep_fence_only.py`,
`.github/workflows/channel-poll.yml` (commits `6a6c4118`, `ed534232`)
**Bot code:** `file_tasks` in `desi-bot/bot.py` and `dmitri-bot/bot.py`, and
`tests/test_file_tasks_guard.py` (bots-repo `9e598f4`)

## What the overwrite actually was

Not a patch, and not a stale patch — a **scheduled script that owned the whole file.**

`scripts/sweep_risks.py` rebuilt `channels/tasks.md` as *everything before the `## Open Risks`
heading* + a freshly generated block. The live file had that heading at character 75,739 of 129,532,
so **53,793 characters sat inside the regenerated region** and were rewritten on every run. Of those
characters, **16,351 were ordinary `- [ ]` task items** written by the amigos and the human — they
were under the heading because they are ordinary task lines, not risk rows, and the sweep cannot tell
the difference.

And the sweep is not rare: `.github/scripts/poll_channels.py` runs it on every channel poll, roughly
twelve times a day, and `channel-poll.yml` then stages all of `channels/`, commits
`feat(channels): frequent poll — mail + telegram`, and on a rejected push **rebases and retries**. So
the deletion arrived as an ordinary commit, with no conflict, nothing failing, and a message about
mail. That is why the founder's volume rule had to be restored twice and why `channels/tasks.md`
reverted to a 54-line-older copy at 11:36 and again at 14:56 on 2026-11-02.

## The fix

- **The sweep owns a fenced region.** `<!-- sweep-risks:begin -->` … `<!-- sweep-risks:end -->`. It
  writes only between the markers, through a temporary file and `os.replace`, so no reader sees a
  half-written ledger and the span it writes is the span it owns.
- **An unmarked file is migrated, not rebuilt.** The migration recognises the shape of the script's
  own output — the heading, blank lines, the placeholder, and rows of the form
  `- [YYYY-MM-DD] **R-n** …` with their one-line note — and stops at the first line that is none of
  those. That is what stops it at the first task item somebody wrote underneath, instead of eating it.
  On the live file the migrated span was 68 characters.
- **A displaced line is named.** If something a person wrote is sitting inside the fence about to be
  replaced, the run prints `NOTICE: n line(s) … are about to be replaced` with the first line. Inside
  the fence the sweep is the owner; it is not entitled to be quiet about it.
- **The poll cannot commit a removal outside the fence.** `scripts/check_sweep_fence_only.py` compares
  HEAD against the staged copy, ignores the fenced region, and refuses with the removed lines named.
  `channel-poll.yml` runs it after staging and, if it refuses, leaves `channels/tasks.md` out of that
  commit — the rest of the record still lands.
- **`file_tasks` no longer writes back a stale read.** It reads under `shared_checkout_lock`, re-reads
  before writing, and re-splices if the file changed underneath it — twice, then it gives up rather
  than guess. The splice is now a pure function (`_splice_filed`), so "what the new file should say"
  is a function of "what the old file said", which is what makes the freshness check meaningful.

## Measured

| claim | how it was checked |
|---|---|
| the region was the whole tail | heading at character 75,739 of 129,532 → 53,793 inside |
| the tail survives | after the migration: 53,725 characters after the owned span, unchanged |
| the items under the heading survive | the 16,351 characters of `- [ ]` items are outside the fence and present |
| two runs are one run | second invocation returns `unchanged` and the bytes are identical |
| the fence guard passes the live tree | `check_sweep_fence_only.py` exits 0 on this repository; it refuses a simulated wholesale rewrite and names both the section and the human's filed item |
| filing survives a race | a section written between the read and the write is still there afterwards, and the filing is not lost either |

Twelve new tests in the commons (`tests/test_sweep_risks_block.py`, 8;
`tests/test_check_sweep_fence_only.py`, 4) and six in the bots repo
(`tests/test_file_tasks_guard.py`).

## What this does not fix

1. **Four bots never file at all.** `file_tasks` exists in `desi-bot` and `dmitri-bot` only. A request
   raised in Claude's, Gemini's, Gwen's or Tarik's chat is not written into the shared ledger by their
   bots — the founder's own expectation ("judge it by whether tasks.md has my name in it") is only
   true of two bodies. Separate defect, not fixed here.
2. **Uncommitted work in the shared checkout is still not safe, for minutes.** While writing this, an
   edit of mine to `scripts/sweep_risks.py` disappeared between two commands, `channels/tasks.md` lost
   its new markers once, and `git stash list` now shows three `autostash` entries plus a
   `WIP on main` from an older session. Something on this machine runs git operations that touch
   uncommitted files in that tree. I did not chase it to a process, because the fix is structural:
   **sessions should work in their own worktree and the shared checkout should be read-only for
   everyone but `git fetch` and the fast-forward.** That is the next piece, and it is bigger than this
   one.
3. **Intent, again.** A fence stops the sweep from deleting the tail. It cannot tell that a *patch*
   which applies cleanly deletes a paragraph somebody added afterwards. That still needs a reader
   comparing against `origin/main`.
