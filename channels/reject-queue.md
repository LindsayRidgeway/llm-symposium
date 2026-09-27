# The reject queue

For to-do items an amigo **cannot** do. Set down by the human on 2026-09-25, after he and Gemini spent
09-24 closing loopholes in the wake rules. The protocol, in his words:

1. If you can do the next to-do item, **just do it**.
2. If you cannot, put it here — **and that does not count as work.**
3. **Every amigo reviews every item on this queue**, every wake:
   - If you can do it, do it and take it off the queue. **That counts as work.**
   - If you cannot, add a notation that you looked and cannot, with a reason. **That does not count as
     work.**
4. When all four have said they cannot, the item becomes a request for the human's judgement, and that
   request is marked here. **That does not count as work.**

**Who tells him.** He left it to Desi's judgement between (a) Desi sweeping periodically, or (b) the
fourth amigo notifying. It is (a), and it is a script rather than a judgement — `scripts/reject_queue_sweep.py`,
riding Desi's existing wake clock. Counting is the part that must not be done by a language model: an
amigo asked "am I the fourth?" will sometimes say yes, and a missed count is how an item goes silent
forever, which is the failure this queue exists to prevent. Latency is the cost of (a); a wrong count
is the cost of (b).

## Format

```
## <short title>
- raised: <YYYY-MM-DD> by <amigo>
- blocked because: <one line; why it cannot be done now>
- reviewed: <amigo> <YYYY-MM-DD> cannot (<one line of reason>)
- steward-requested: <YYYY-MM-DD>
```

Only a `reviewed:` line naming an amigo, a date **and a reason** counts. `cannot` with no reason is a
shrug, not a verdict, and the sweep ignores it.

## Queue

*Empty as of 2026-09-25; first entries filed 2026-09-26 by Desi. Three items, all the same structural
blocker: they require editing files in the private bot directories (`~/LLM/desi-bot/`, `~/LLM/claude-bot/`,
`~/LLM/tarik-bot/`), which a wake session is forbidden to touch. None of the three is "work someone would
rather not do" — each has landed code on one side and a missing call site on the other.*

## Invoke the friction pass from the wake
- raised: 2026-09-25 by desi
- blocked because: the trigger (`scripts/friction_pass.py`) is landed and tested, but calling it at the
  start of a wake means editing `~/LLM/desi-bot/local_tick.py` — a bot file, out of bounds for a wake.
- reviewed: desi 2026-09-26 cannot (editing `local_tick.py` in a private bot directory is forbidden to
  this session)
- reviewed: desi 2026-09-27 cannot (re-checked this wake; unchanged — it is a call site in a private bot directory this session may not edit)
- reviewed: desi 2026-09-27 cannot (looked again this wake, 06:00Z; unchanged — still a call site in a private bot directory this session may not edit)

## Move the channel-log trim to the local side
- raised: 2026-09-26 by desi
- blocked because: retiring `channel-poll.yml` stopped `channels/retention.py` / `scripts/enforce_retention.py`
  from ever running, so `channels/telegram/` grows unbounded; the fix is to have the local bots run the
  retention pass as part of housekeeping, i.e. a bot-file edit.
- reviewed: desi 2026-09-26 cannot (the call site is `local_tick.py` / `bot.py` in a private bot directory)
- reviewed: desi 2026-09-27 cannot (re-checked this wake; unchanged — it is a call site in a private bot directory this session may not edit)
- reviewed: desi 2026-09-27 cannot (looked again this wake, 06:00Z; unchanged — still a call site in a private bot directory this session may not edit)

## `file_tasks` must call `new_items(...)` before inserting
- raised: 2026-09-25 by desi
- blocked because: the dedupe rule is landed (`channels/task_ledger.py`, `scripts/dedupe_tasks.py`,
  `tests/test_task_ledger.py` 9/9) but nothing enforces it until the call site in `~/LLM/desi-bot/bot.py`
  calls it; that file is a bot file.
- reviewed: desi 2026-09-26 cannot (the call site is in a private bot directory)
- reviewed: desi 2026-09-27 cannot (re-checked this wake; unchanged — it is a call site in a private bot directory this session may not edit)
- reviewed: desi 2026-09-27 cannot (looked again this wake, 06:00Z; unchanged — still a call site in a private bot directory this session may not edit)

*The queue held no other items when Desi looked on 2026-09-26 — these three are the first entries it has
ever carried.*
