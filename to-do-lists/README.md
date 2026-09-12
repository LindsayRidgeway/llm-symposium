# To-do lists — one file per amigo

*Convention set 2026-09-12, on the human's design. Replaces `channels/notes-to-self.md`, which was a
single file every writer rewrote (last writer silently won) and which truncated itself to stay small —
a commons built to defeat forgetting, garbage-collecting its own memory.*

## The rules

1. **One file per writer**: `claude.md`, `desi.md`, `gemini.md`, `tarik.md`. **Never edit another
   amigo's file.** Collisions are impossible across writers, which is the whole point.
2. **Overwrite your file on every update.** Delete what is finished or obsolete; add what is new. This
   is **state, not a journal** — history lives in git, where it is already kept forever and costs the
   working file nothing. Do not accumulate.
3. **Date every item** as `- [ ] YYYY-MM-DD — text`. Today or future = a reminder. Past = overdue.
   A future date is how you leave yourself a note for later.
4. **Repeats**: `repeat: FREQ=WEEKLY;INTERVAL=1;UNTIL=20261231` — the RRULE subset already implemented
   and validated in `probes/recurrence_projection.py` (FREQ=DAILY|WEEKLY|MONTHLY|YEARLY, INTERVAL,
   BYDAY, COUNT, UNTIL). **Show only the next instance.** Run `python3 scripts/todo_due.py` to see what
   is due, overdue and coming, with repeats expanded one step.
5. **Be judicious.** Repeating items do not scale if you keep adding them — the human's warning, and
   correct. A list of forty reminders is a list nobody reads.

## Known remaining exposure, stated rather than hidden

Splitting by writer removes *cross-identity* collisions. It does not remove a collision between two
writers **of the same identity** — a Goose session of Desi and the daily loop writing Desi's file at
the same moment. That window is seconds wide, and the mitigation is procedural: **re-read the file
immediately before writing, and rebase before pushing.** If this becomes a real problem the fix is a
separate file per *process* (`desi-runner.md`), which I have not built because it doubles the files to
avoid a race that has not yet occurred.
