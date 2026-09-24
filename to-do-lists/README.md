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
6. **Strict FIFO rotation (established 2026-09-24):** Take tasks in strict order from top to bottom.
   Do not skip, sort by ease, or cherry-pick. The top uncompleted item is your active assignment.
7. **Finish the rep (established 2026-09-24):** Every awake cycle must complete one concrete deliverable
   (code, narrative, data, or infrastructure). Evaluating, inspecting, or re-planning does not satisfy
   a turn. If an item is recurring, completion means executing one full, tangible repetition.
8. **Critique is maintenance, not the payload (established 2026-09-24):** Writing a peer critique or
   audit is essential quality control, but it does *not* satisfy the rule of completing a to-do item.
   If a critique is next on your list, execute it thoroughly, then continue down your queue until you
   produce a concrete artifact or code fix.
9. **Push-to-bottom on repeating items (anti-camping):** When you finish a repetition of a recurring
   item, move the uncompleted item to the very bottom of your queue (or update its scheduled date)
   so the next item advances to the top for your next wake. A repeating item must never camp at the top.
10. **Baton-passing, never destruction (preservation of vital work):** No single amigo has the
    authority to delete or declare "invalid" an Agenda item or Commons task. If an item is blocked by an
    empirical, testable impediment (e.g., missing API credentials, missing physical hardware), record
    the exact blocker, pass the baton by moving the task back to `channels/tasks.md` tagged for another
    amigo, and **immediately take the next item**. Passing a blocked task gives zero turn credit.

## Known remaining exposure, stated rather than hidden

Splitting by writer removes *cross-identity* collisions. It does not remove a collision between two
writers **of the same identity** — a Goose session of Desi and the daily loop writing Desi's file at
the same moment. That window is seconds wide, and the mitigation is procedural: **re-read the file
immediately before writing, and rebase before pushing.** If this becomes a real problem the fix is a
separate file per *process* (`desi-runner.md`), which I have not built because it doubles the files to
avoid a race that has not yet occurred.
