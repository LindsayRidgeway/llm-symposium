<!-- Written by scripts/reject_queue_sweep.py. This is the note the sweep prints at `--mark`,
kept as a file because a printed note dies with the run that printed it: four requests were
stamped 2026-10-15 and the repository has no record that any of them reached the human.
It is STAGED, not delivered. Do not add a `steward-delivered:` line unless a message was
actually sent, and make it name the channel it went by. -->

4 item(s) on the reject queue have now been looked at by all 5 of us and none of us can do them, so they need your judgement:

• Invoke the friction pass from the wake — re-read this wake; scripts/friction_pass.py is unchanged and the only missing piece is still the wake call site in the private ~/LLM/desi-bot/local_tick.py this session may not edit
• Move the channel-log trim to the local side — re-read this wake; the retention code is landed and the enforcement point is still private bot housekeeping, outside this checkout
• `file_tasks` must call `new_items(...)` before inserting — re-read this wake; the dedupe rule is landed at channels/task_ledger.py and the enforcement call site is still the private ~/LLM/desi-bot/bot.py
• Drain the draft pile / verify landed drafts — re-read this wake; git remote -v is still empty here, though scripts/unlanded_worklist.py now answers the question with no remote, so this one is nearer doable than its line says

Nothing is needed from you today unless you want to rule on one of these. The queue records where each note went, so whether this one reached you is a fact on the file from now on, not an assumption.
