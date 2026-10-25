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
- steward-requested: 2026-10-15
- raised: 2026-09-25 by desi
- blocked because: the trigger (`scripts/friction_pass.py`) is landed and tested, but calling it at the
  start of a wake means editing `~/LLM/desi-bot/local_tick.py` — a bot file, out of bounds for a wake.
- reviewed: desi 2026-09-26 cannot (editing `local_tick.py` in a private bot directory is forbidden to this session)
- reviewed: desi 2026-09-27 cannot (re-checked this wake; unchanged — it is a call site in a private bot directory this session may not edit)
- reviewed: desi 2026-09-27 cannot (looked again this wake, 06:00Z; unchanged — still a call site in a private bot directory this session may not edit)
- reviewed: tarik 2026-09-27 cannot (this wake may not edit private bot-local call sites; the repository-side trigger already exists)
- reviewed: desi 2026-09-28 cannot (re-checked; unchanged — the trigger must be invoked from `~/LLM/desi-bot/local_tick.py`, a private bot file this checkout may not edit)
- reviewed: desi 2026-09-29 cannot (looked again; unchanged — the only missing piece is the call site in `~/LLM/desi-bot/local_tick.py`, which this session's own instructions forbid it to edit)
- reviewed: desi 2026-09-30 cannot (looked again; unchanged — `scripts/friction_pass.py` is landed and tested, the only missing piece is still the call site in the private `local_tick.py` this session may not edit)
- reviewed: desi 2026-10-01 cannot (looked again at the 2026-10-01 00:12Z wake; unchanged — the only missing piece is the call site in the private `local_tick.py` this session may not edit)
- reviewed: desi 2026-10-02 cannot (looked again at the 2026-10-02 00:14Z wake; unchanged — the only missing piece is the call site in the private `local_tick.py` this session may not edit)
- reviewed: gemini 2026-10-02 cannot (editing private bot directories outside this repository checkout is forbidden)
- reviewed: gemini 2026-10-03 cannot (call site is in private bot file ~/LLM/desi-bot/local_tick.py outside this checkout)
- reviewed: desi 2026-10-03 cannot (looked again this wake; unchanged — `scripts/friction_pass.py` is landed and tested, the only missing piece is the call site in the private `local_tick.py` this session may not edit)
- reviewed: desi 2026-10-04 cannot (looked again this wake; unchanged — `scripts/friction_pass.py` is landed and tested, the only missing piece is still the call site in the private `local_tick.py` this session may not edit)
- reviewed: gemini 2026-10-04 cannot (call site is in private bot file ~/LLM/desi-bot/local_tick.py outside this checkout)
- reviewed: tarik 2026-10-05 cannot (the remaining change is the wake call site in `~/LLM/desi-bot/local_tick.py`, a private bot file this checkout may not edit)
- reviewed: desi 2026-10-06 cannot (looked again this wake; unchanged — `scripts/friction_pass.py` is landed and tested, the only missing piece is still the call site in the private `local_tick.py` this session may not edit)
- reviewed: desi 2026-10-10 cannot (looked again this wake; unchanged — `scripts/friction_pass.py` is landed and tested, the missing piece is still the call site in the private `~/LLM/desi-bot/local_tick.py` this session may not edit)
- reviewed: desi 2026-10-11 cannot (editing ~/LLM/desi-bot/local_tick.py, a private bot file, is forbidden to this session)
- reviewed: desi 2026-10-12 cannot (re-checked this wake; unchanged — `scripts/friction_pass.py` is landed and tested, the only missing piece is still the call site in the private `~/LLM/desi-bot/local_tick.py` this session may not edit)
- reviewed: desi 2026-10-13 cannot (editing ~/LLM/desi-bot/local_tick.py, a private bot file, is forbidden to this session)
- reviewed: tarik 2026-10-13 cannot (the remaining trigger is a private bot-local call site in `~/LLM/desi-bot/local_tick.py`, outside this checkout)
- reviewed: desi 2026-10-14 cannot (re-read this wake; unchanged — scripts/friction_pass.py is landed and tested; the only missing piece is still the call site in the private ~/LLM/desi-bot/local_tick.py this session may not edit)
- reviewed: desi 2026-10-15 cannot (re-read this wake: scripts/friction_pass.py is landed and tested; the only missing piece is still the call site in the private ~/LLM/desi-bot/local_tick.py this session may not edit)
- reviewed: dmitri 2026-10-14 cannot (checked on disk this wake: scripts/friction_pass.py and tests/test_friction_pass.py are landed; the only missing piece is a call site in ~/LLM/desi-bot/local_tick.py, a private bot file this checkout may not edit)
- reviewed: tarik 2026-10-14 cannot (re-read this wake; unchanged — scripts/friction_pass.py is landed and tested, but the missing call site is private ~/LLM/desi-bot/local_tick.py)
- reviewed: tarik 2026-10-15 cannot (re-read this wake; unchanged — the missing invocation point is still private ~/LLM/desi-bot/local_tick.py, outside this checkout)
- reviewed: claude 2026-10-14 cannot (checked this wake: scripts/friction_pass.py is landed; the call site is still ~/LLM/desi-bot/local_tick.py, a private bot file outside this checkout's scope)
- reviewed: desi 2026-10-25 cannot (re-read this wake; scripts/friction_pass.py is unchanged and the only missing piece is still the wake call site in the private ~/LLM/desi-bot/local_tick.py this session may not edit)

## Move the channel-log trim to the local side
- steward-requested: 2026-10-15
- raised: 2026-09-26 by desi
- blocked because: retiring `channel-poll.yml` stopped `channels/retention.py` / `scripts/enforce_retention.py`
  from ever running, so `channels/telegram/` grows unbounded; the fix is to have the local bots run the
  retention pass as part of housekeeping, i.e. a bot-file edit.
- reviewed: desi 2026-09-26 cannot (the call site is `local_tick.py` / `bot.py` in a private bot directory)
- reviewed: desi 2026-09-27 cannot (re-checked this wake; unchanged — it is a call site in a private bot directory this session may not edit)
- reviewed: desi 2026-09-27 cannot (looked again this wake, 06:00Z; unchanged — still a call site in a private bot directory this session may not edit)
- reviewed: tarik 2026-09-27 cannot (the missing call site is bot-local housekeeping outside this checkout)
- reviewed: desi 2026-09-28 cannot (re-checked; unchanged — the housekeeping call site is in the private bot directory)
- reviewed: desi 2026-09-29 cannot (looked again; unchanged — the retention pass must be invoked from private bot housekeeping, which this session may not edit)
- reviewed: desi 2026-09-30 cannot (looked again; unchanged — the retention pass must be invoked from private bot housekeeping, not a file this checkout holds)
- reviewed: desi 2026-10-01 cannot (looked again at the 2026-10-01 00:12Z wake; unchanged — the retention pass must be invoked from private bot housekeeping, not a file this checkout holds)
- reviewed: desi 2026-10-02 cannot (looked again; unchanged — the retention pass must be invoked from private bot housekeeping, not a file this checkout holds)
- reviewed: gemini 2026-10-02 cannot (housekeeping call site resides in private bot directories outside this checkout)
- reviewed: gemini 2026-10-03 cannot (housekeeping call site resides in private bot directories outside this checkout)
- reviewed: desi 2026-10-03 cannot (looked again this wake; unchanged — the retention pass must be invoked from private bot housekeeping, not a file this checkout holds)
- reviewed: desi 2026-10-04 cannot (looked again this wake; unchanged — the retention pass must still be invoked from private bot housekeeping, not a file this checkout holds)
- reviewed: gemini 2026-10-04 cannot (housekeeping call site resides in private bot directories outside this checkout)
- reviewed: tarik 2026-10-05 cannot (the missing enforcement point is private bot housekeeping/local_tick code outside this repository checkout)
- reviewed: desi 2026-10-06 cannot (looked again this wake; unchanged — the retention pass must still be invoked from private bot housekeeping, not a file this checkout holds)
- reviewed: desi 2026-10-10 cannot (looked again this wake; unchanged — the retention pass must still be invoked from private bot housekeeping, not a file this checkout holds)
- reviewed: desi 2026-10-11 cannot (the housekeeping call site is in private bot files this checkout may not edit)
- reviewed: desi 2026-10-12 cannot (re-checked this wake; unchanged — the retention pass must still be invoked from private bot housekeeping, not a file this checkout holds)
- reviewed: desi 2026-10-13 cannot (the retention/housekeeping call site is in private bot files this checkout may not edit)
- reviewed: tarik 2026-10-13 cannot (the retention pass must be wired into private bot housekeeping/local_tick code outside this repository checkout)
- reviewed: desi 2026-10-14 cannot (re-read this wake; unchanged — the retention pass must still be invoked from private bot housekeeping, not a file this checkout holds)
- reviewed: desi 2026-10-15 cannot (re-read this wake: channels/retention.py and scripts/enforce_retention.py are landed; the retention pass must still be invoked from private bot housekeeping, not a file this checkout holds)
- reviewed: dmitri 2026-10-14 cannot (checked this wake: channels/retention.py and scripts/enforce_retention.py are landed; the missing piece is a housekeeping call site in private bot files, outside this checkout)
- reviewed: tarik 2026-10-14 cannot (re-read this wake; unchanged — the retention pass must be wired into private bot housekeeping/local_tick code outside this repository checkout)
- reviewed: tarik 2026-10-15 cannot (re-read this wake; unchanged — the retention pass still needs a private bot housekeeping/local_tick call site outside this checkout)
- reviewed: claude 2026-10-14 cannot (checked this wake: channels/retention.py and scripts/enforce_retention.py are landed; the housekeeping call site is still private bot files outside this checkout)
- reviewed: desi 2026-10-25 cannot (re-read this wake; the retention code is landed and the enforcement point is still private bot housekeeping, outside this checkout)

## `file_tasks` must call `new_items(...)` before inserting
- steward-requested: 2026-10-15
- raised: 2026-09-25 by desi
- blocked because: the dedupe rule is landed (`channels/task_ledger.py`, `scripts/dedupe_tasks.py`,
  `tests/test_task_ledger.py` 9/9) but nothing enforces it until the call site in `~/LLM/desi-bot/bot.py`
  calls it; that file is a bot file.
- reviewed: desi 2026-09-26 cannot (the call site is in a private bot directory)
- reviewed: desi 2026-09-27 cannot (re-checked this wake; unchanged — it is a call site in a private bot directory this session may not edit)
- reviewed: desi 2026-09-27 cannot (looked again this wake, 06:00Z; unchanged — still a call site in a private bot directory this session may not edit)
- reviewed: tarik 2026-09-27 cannot (the remaining enforcement point is a private bot call site outside this checkout)
- reviewed: desi 2026-09-28 cannot (re-checked; unchanged — the enforcement point is `~/LLM/desi-bot/bot.py`, which this checkout may not edit)
- reviewed: desi 2026-09-29 cannot (looked again; unchanged — the dedupe rule is landed, the call site in `~/LLM/desi-bot/bot.py` is a private bot file this session may not edit)
- reviewed: desi 2026-09-30 cannot (looked again; unchanged — `new_items(...)` is landed in `channels/task_ledger.py`, the enforcement point is still the private `bot.py` this session may not edit)
- reviewed: desi 2026-10-01 cannot (looked again at the 2026-10-01 00:12Z wake; unchanged — `new_items(...)` is landed in `channels/task_ledger.py`; the enforcement point is still the private `bot.py` this session may not edit)
- reviewed: desi 2026-10-02 cannot (looked again; unchanged — `new_items(...)` is landed in `channels/task_ledger.py`; the enforcement point is still the private `bot.py` this session may not edit)
- reviewed: gemini 2026-10-02 cannot (enforcement call site is in private ~/LLM/desi-bot/bot.py which this checkout cannot touch)
- reviewed: gemini 2026-10-03 cannot (enforcement call site is in private ~/LLM/desi-bot/bot.py which this checkout cannot touch)
- reviewed: desi 2026-10-03 cannot (looked again this wake; unchanged — `new_items(...)` is landed in `channels/task_ledger.py`; the enforcement point is still the private `bot.py` this session may not edit)
- reviewed: desi 2026-10-04 cannot (looked again this wake; unchanged — `new_items(...)` is landed in `channels/task_ledger.py`; the enforcement point is still the private `bot.py` this session may not edit)
- reviewed: gemini 2026-10-04 cannot (enforcement call site is in private ~/LLM/desi-bot/bot.py which this checkout cannot touch)
- reviewed: tarik 2026-10-05 cannot (the dedupe helper is repository-side but the remaining call site is `~/LLM/desi-bot/bot.py`, outside this checkout)
- reviewed: desi 2026-10-06 cannot (looked again this wake; unchanged — `new_items(...)` is landed in `channels/task_ledger.py`; the enforcement point is still the private `bot.py` this session may not edit)
- reviewed: desi 2026-10-10 cannot (looked again this wake; unchanged — `new_items(...)` is landed in `channels/task_ledger.py`; the enforcement point is still the private `bot.py` this session may not edit)
- reviewed: desi 2026-10-11 cannot (the enforcement call site is in the private ~/LLM/desi-bot/bot.py this checkout may not edit)
- reviewed: desi 2026-10-12 cannot (re-checked this wake; unchanged — `new_items(...)` is landed in `channels/task_ledger.py`; the enforcement point is still the private `bot.py` this session may not edit)
- reviewed: desi 2026-10-13 cannot (the enforcement call site is the private ~/LLM/desi-bot/bot.py this checkout may not edit)
- reviewed: tarik 2026-10-13 cannot (the dedupe helper is repository-side but the remaining enforcement call site is private `~/LLM/desi-bot/bot.py`)
- reviewed: desi 2026-10-14 cannot (re-read this wake; unchanged — `new_items(...)` is landed in channels/task_ledger.py; the enforcement call site is still the private ~/LLM/desi-bot/bot.py this checkout may not edit)
- reviewed: desi 2026-10-15 cannot (re-read this wake: new_items(...) is landed in channels/task_ledger.py; the enforcement call site is still the private ~/LLM/desi-bot/bot.py this checkout may not edit)
- reviewed: dmitri 2026-10-14 cannot (checked this wake: new_items(...) is landed at channels/task_ledger.py:167; the missing enforcement call site is ~/LLM/desi-bot/bot.py, a private bot file this checkout may not edit)
- reviewed: tarik 2026-10-14 cannot (re-read this wake; unchanged — the dedupe helper is repository-side but the remaining enforcement call site is private ~/LLM/desi-bot/bot.py)
- reviewed: tarik 2026-10-15 cannot (re-read this wake; unchanged — new_items(...) is landed, but the enforcement call site remains private ~/LLM/desi-bot/bot.py outside this checkout)
- reviewed: claude 2026-10-14 cannot (checked this wake: new_items(...) is landed in channels/task_ledger.py; the enforcement call site is still ~/LLM/desi-bot/bot.py, a private bot file this checkout may not edit)
- reviewed: desi 2026-10-25 cannot (re-read this wake; the dedupe rule is landed at channels/task_ledger.py and the enforcement call site is still the private ~/LLM/desi-bot/bot.py)


## Read agenda item 32's three both-domain records in full
- raised: 2026-10-04 by desi
- blocked because: the three records that measure an affective outcome and a neural/autonomic
  measure in a chronic-pain population — 41332177 (*Physiotherapy Theory and Practice*),
  40935122 (*Joint Bone Spine*) and 26787729 (*J Evid Based Complementary Altern Med*,
  `PMC5871177`) — are all closed access. Europe PMC reports `isOpenAccess = N` for each, and PMC
  returns front matter only ("The publisher of this article does not allow downloading of the full
  text in XML form."). The per-subject data and the Δautonomic–Δaffective correlation that item 32
  §6 names as its overturning condition cannot be retrieved by a wake with no institutional login.
- reviewed: desi 2026-10-04 cannot (checked all three at the 2026-10-04 12:22Z wake; Europe PMC core records say isOpenAccess=N and PMC serves front matter only, so the full text needs a reader with library access)
- reviewed: desi 2026-10-06 cannot (looked again this wake; unchanged — the three records are closed access (Europe PMC `isOpenAccess=N`), so the correlation needs a reader with library access; do not re-derive the access check)
- reviewed: desi 2026-10-10 cannot (looked again this wake; unchanged — the three records are closed access (Europe PMC `isOpenAccess=N`), so the correlation needs a reader with library access)
- reviewed: desi 2026-10-11 cannot (the three records are closed access (Europe PMC isOpenAccess=N), so the correlation needs a library reader)
- reviewed: desi 2026-10-12 cannot (re-checked this wake; the three records are closed access (Europe PMC isOpenAccess=N), so the correlation needs a library reader)
- reviewed: tarik 2026-10-13 cannot (the three cited full texts are closed-access and this wake has no institutional login)

*The queue held no other items when Desi looked on 2026-09-26 — the first three were the first entries
it has ever carried; the fourth was added 2026-09-28.*

*Desi re-read all four items at the 2026-09-29 22:09Z wake. Every reason above is unchanged and none is doable from a wake checkout — three are private-bot call sites, the fourth needs a git remote this checkout does not have — so no new `reviewed:` line was added (the standing ones already carry 2026-09-29). Nothing here can be taken off the queue by a wake; each waits on another amigo's `cannot`, or on the human.*

*Desi re-read all four items again at the 2026-09-30 16:11Z wake and added a fresh `reviewed: desi 2026-09-30 cannot` line to each, with the reason. All four blockers are unchanged: three need a call site in a private bot directory, the fourth needs a git remote (`git remote -v` is still empty here). No item can be taken off this queue by a wake.*

*Desi re-read all four items again at the 2026-10-01 00:12Z wake and added a fresh `reviewed: desi 2026-10-01 cannot` line to each, with the reason. All four blockers are unchanged: three need a call site in a private bot directory, the fourth needs a git remote (`git remote -v` is still empty here). No item can be taken off this queue by a wake.*

*Desi re-read all four items again at the 2026-10-03 12:19Z wake. Every blocker is unchanged — three need a call site in a private bot directory this session may not edit, the fourth needs a git remote and `git remote -v` is still empty here. Each item already carries a `reviewed: desi 2026-10-03 cannot` line from the 10:19Z wake earlier the same day, so no new line was added: a duplicate same-date line is noise, and the 2026-09-29 wake set this precedent. Nothing on this queue is takeable from a wake.*

*Desi re-read all four items again at the 2026-10-04 10:22Z wake. Every blocker is unchanged — three need a call site in a private bot directory (`~/LLM/desi-bot/local_tick.py`, `bot.py`) this session may not edit, the fourth needs a git remote and `git remote -v` is still empty in this checkout. Each item already carries a `reviewed: desi 2026-10-04 cannot` line from an earlier wake this same day, so no new line was added — a duplicate same-date line is noise (precedent set 2026-09-29). Nothing on this queue is takeable from a wake; each waits on another amigo's `cannot`, or on the human.*

*Desi re-read all four pre-existing items again at the 2026-10-04 12:22Z wake. Every blocker is
unchanged — three need a call site in a private bot directory (`~/LLM/desi-bot/local_tick.py`,
`bot.py`) this session may not edit, the fourth needs a git remote and `git remote -v` is still
empty in this checkout. Each already carries a `reviewed: desi 2026-10-04 cannot` line from an
earlier wake the same day, so no duplicate line was added (precedent set 2026-09-29). A fifth item
was filed this wake — the closed-access full-text read for agenda item 32 — with its own reason.*
- reviewed: tarik 2026-10-05 cannot (the cited full texts are closed-access and this wake has no institutional login)
- reviewed: desi 2026-10-13 cannot (the three cited records are closed access (Europe PMC isOpenAccess=N), so the correlation needs a library reader)
- reviewed: desi 2026-10-14 cannot (re-read this wake; unchanged — the three cited records are closed access (Europe PMC isOpenAccess=N), so the correlation needs a library reader)
- reviewed: desi 2026-10-15 cannot (re-read this wake: the three cited records (41332177 / 40935122 / 26787729) remain closed access (Europe PMC isOpenAccess=N), so the correlation needs a library reader)
- reviewed: dmitri 2026-10-14 cannot (this checkout has no institutional login; the three cited records 41332177 / 40935122 / 26787729 remain closed access, so the per-subject Δautonomic–Δaffective correlation needs a library reader)
- reviewed: tarik 2026-10-14 cannot (unchanged — the three cited records are closed access and this wake has no institutional login for the needed full texts)
- reviewed: tarik 2026-10-15 cannot (re-read this wake; the three cited records remain closed access and this checkout has no institutional login)
- reviewed: claude 2026-10-14 cannot (no institutional login in this checkout; the three cited records remain closed access per Europe PMC, so the correlation needs a library reader)
- reviewed: desi 2026-10-25 cannot (re-read this wake; the access check was not re-derived (it is on record as measured twice), so the blocker stands: three closed-access records need a reader with library access)
*Desi re-read all five items again at the 2026-10-06 20:29Z wake and added a fresh `reviewed: desi 2026-10-06 cannot` line to each, with the reason. Every blocker is unchanged — four need a call site or a git remote this checkout does not have, the fifth needs library access. Nothing here is takeable from a wake; each waits on another amigo's `cannot`, or on the human.*
*Desi re-read all five items again at the 2026-10-11 04:43Z wake. Every blocker is unchanged — three need a call site in a private bot directory (`~/LLM/desi-bot/local_tick.py`, `bot.py`) this session may not edit, one needs a git remote and `git remote -v` is still empty here, one needs library access (agenda item 32's three closed-access records). Each item already carries a `reviewed: desi 2026-10-11 cannot` line from the 02:43Z wake earlier the same day, so no duplicate same-date line was added (precedent set 2026-09-29). Nothing here is takeable from a wake; each waits on another amigo's `cannot`, or on the human.*



*Desi re-read all five items at the 2026-10-15 02:55Z wake. Every blocker is unchanged — three need a
call site in a private bot directory (`~/LLM/desi-bot/local_tick.py`, `bot.py`) this session may not
edit, one needs a git remote and `git remote -v` is still empty here, one needs library access (item
32's three closed-access records). Each item already carries a `reviewed: desi 2026-10-15 cannot` line
from the 00:55Z wake the same UTC day, so no duplicate line was added (precedent set 2026-09-29).
`python3 scripts/reject_queue_sweep.py --check` reports 5 items, 0 ready for the steward. Nothing here
is takeable from a wake; each waits on another amigo's `cannot`, or on the human.*

*Desi re-read all five items at the 2026-10-18 13:06Z wake. Nothing is takeable from this checkout and the
reasons are unchanged, so one line each rather than a fresh entry: the channel-log trim and the `file_tasks`
fix both still need a call site in a private bot directory (`~/LLM/desi-bot/local_tick.py`, `bot.py`) this
session may not edit; the draft pile still cannot be verified because `git remote -v` in this checkout is
empty (0 lines, measured this wake); agenda item 32's three records are still closed access and this wake has
no institutional login. `python3 scripts/reject_queue_sweep.py --check` reports 5 items, 0 ready for the
steward. This line is the "looked and cannot" record the rule asks for, not work.*

*Desi re-read all five items at the 2026-10-19 03:08Z wake. All five still carry today's blocker and none
is takeable from this checkout, so one line each rather than five duplicate entries: the friction-pass
trigger, the channel-log trim and the `file_tasks` call site all still need an edit in a private bot
directory (`~/LLM/desi-bot/local_tick.py`, `bot.py`) this session may not touch; the draft pile still
cannot be verified because `git remote -v` in this checkout is empty (measured this wake: 0 lines); agenda
item 32's three records (41332177 / 40935122 / 26787729) are still closed access and this wake has no
institutional login. `python3 scripts/reject_queue_sweep.py --check` reports 5 items, 0 ready for the
steward. This paragraph is the required "looked and cannot" record, not work.*

*Claude re-read all five items at the 2026-10-19 17:05Z wake. Checked `git remote -v` directly: still
empty (0 lines). Checked `~/LLM/desi-bot/` directly: `local_tick.py` and `bot.py` are private bot files
outside this checkout, unchanged. Agenda item 32's three records remain closed access (no institutional
login available here). All five blockers are unchanged from the 03:08Z review the same day; no new
`reviewed:` lines added per the no-duplicate-same-day precedent. Nothing here is takeable from this
checkout. This paragraph is the required "looked and cannot" record, not work — moving on to the to-do
list.*

*Dmitri re-read all five items at the 2026-10-19 21:20Z wake and cannot take any of them. Measured
this wake, not remembered: `git remote -v` in this checkout still returns 0 lines (so the draft pile
cannot be fetched or verified); the friction-pass trigger, the channel-log trim and the `file_tasks`
call site all still need an edit inside a private bot directory (`~/LLM/desi-bot/local_tick.py`,
`bot.py`) that this session is forbidden to touch, and their repository-side halves are already on
`main` (`scripts/friction_pass.py`, `channels/retention.py`, `scripts/enforce_retention.py`,
`channels/task_ledger.py`); agenda item 32's three records (41332177 / 40935122 / 26787729) are still
closed access at Europe PMC and this checkout has no institutional login. Each item already carries a
`steward-requested: 2026-10-15` line, so what they wait on now is the human, not another amigo's
`cannot`. This paragraph is the required "looked and cannot" record, not work.*

*Desi re-read all five items at the 2026-10-22 19:18Z wake and can take none of them, measured this
wake rather than remembered: `git remote -v` in this checkout still returns 0 lines, so "drain the
draft pile / verify landed drafts" has nothing to fetch from — and that same fact is why every review
this wake had to be done from `~/LLM/<amigo>-bot/tick-state/runs/<id>/changes.patch` instead of from a
branch. The friction-pass trigger, the channel-log trim and the `file_tasks` call site each still
require an edit inside a private bot directory (`~/LLM/desi-bot/local_tick.py`, `bot.py`) that this
session may not touch, and their repository-side halves are on `main` already. Agenda item 32's three
records are still closed access at Europe PMC and this checkout has no institutional login. All five
already carry `steward-requested: 2026-10-15`, so what they wait on is the human, not a fourth
amigo's `cannot`. This paragraph is the required "looked and cannot" record, not work.*

*Desi re-read all five items at the 2026-10-24 11:23Z wake and can take none of them, measured this
wake rather than remembered: `git remote -v` in this checkout still returns 0 lines, so "drain the draft
pile / verify landed drafts" still has nothing to fetch from. The friction-pass trigger, the channel-log
trim and the `file_tasks` call site each still need an edit inside a private bot directory
(`~/LLM/desi-bot/local_tick.py`, `bot.py`) that this session may not touch; their repository-side halves
are on `main` already (`scripts/friction_pass.py`, `channels/retention.py`,
`scripts/enforce_retention.py`, `channels/task_ledger.py`). Agenda item 32's three records (41332177 /
40935122 / 26787729) are still closed access at Europe PMC and this checkout has no institutional login.
All five already carry `steward-requested: 2026-10-15`, so what they wait on is the human, not a fourth
amigo's `cannot`. This paragraph is the required "looked and cannot" record, not work.*

*One thing worth saying out loud while the queue is read again: four of the five blocked items are
blocked by the same rule, not by five separate facts — a wake may not edit the private bot directories,
and every one of them needs a call site inside one. The queue's own escalation worked (all four amigos
said `cannot` by 2026-10-15 and it became a steward request); what it cannot do is tell the human that
these are four instances of **one** decision, which is "may a wake touch `local_tick.py` / `bot.py` when
the change is a two-line call to a tool that is already landed and tested". That is a single yes or no,
and it has been sitting for 39 days.*

*Desi re-read all five items at the 2026-10-25 03:26Z wake and can take none of them, measured this
wake: `git remote -v` here still returns 0 lines (the draft-pile item has nothing to fetch from); the
friction-pass trigger, the channel-log trim and the `file_tasks` call site each still need an edit
inside a private bot directory (`~/LLM/desi-bot/local_tick.py`, `bot.py`) that this session may not
touch, and I re-checked that their repository halves are still on `main` this wake
(`scripts/friction_pass.py`, `channels/retention.py`, `scripts/enforce_retention.py`,
`channels/task_ledger.py`, all present); agenda item 32's three records (41332177 / 40935122 /
26787729) were last measured closed at Europe PMC and nothing here has an institutional login, so that
line is carried forward, not re-derived. `python3 scripts/reject_queue_sweep.py --check` still reports
the five items with none ready for the steward — they wait on the human, not on a fourth `cannot`.
This paragraph is the required "looked and cannot" record, not work.

*One thing this wake measured that bears on the first three entries: they are blocked by a single rule,
not three facts — a wake may not edit the bot directories, and each needs a two-line call site inside
one. The decision is one yes or no and it is now 40 days old.*

## TAKE OFF THE QUEUE, 2026-10-25 19:26Z — "Drain the draft pile / verify landed drafts" (raised 2026-09-28, 27 days)

*It was never blocked, and the reason it gave was wrong in one specific way. The item said a wake
"cannot fetch a review branch to confirm whether a run's LAND paths reached `main`", which is true and
irrelevant: a wake does not need the branch. Every wake starts from a checkout whose HEAD is `main` at
that moment, and every run leaves its own `changes.patch` in `~/LLM/<amigo>-bot/tick-state/runs/<id>/`,
so both halves of the job — did this path reach the tree, and if not can its bytes be recovered — are
answerable with `git cat-file`/`-f` against HEAD and `git apply --check` against the patch. Desi's
2026-10-19 `scripts/unlanded_worklist.py` is the same idea as a script, and a note on this item had
already said the item was "nearer doable than its line says".

*Done once, this wake, as the proof: five runs from the review queue were measured this way. Twelve
paths that were reported as landed and were not are now in the tree — `scripts/reconcile_review_verdicts.py`
and `tests/test_reconcile_review_verdicts.py` (11/11 pass), `tests/test_music_catalogue_unwired.py`
(the music gate now reports 14 pages, 0 problems instead of four unreachable pieces),
`tests/test_items_jsonl_parses.py` (the guard against committed conflict markers, which is what actually
damaged this ledger twice), six report files that existed only in run directories, and one research JSON.
The item is off the queue and the same job is now a to-do line with a working method, not a reject.*

*The other four items were re-read this wake (2026-10-25 19:26Z), measured rather than remembered:
`git remote -v` here still returns 0 lines, which no longer blocks anything above; the friction pass,
the channel-log trim and the `file_tasks` call site still need an edit inside a private bot directory
(`~/LLM/desi-bot/local_tick.py`, `bot.py`) this session may not touch, and their repository halves are
still present (`scripts/friction_pass.py`, `channels/retention.py`, `scripts/enforce_retention.py`,
`channels/task_ledger.py`); agenda item 32's three records (41332177 / 40935122 / 26787729) were last
measured closed at Europe PMC and this checkout has no institutional login. The three bot-directory
items are one 40-day-old yes-or-no, and they carry `steward-requested: 2026-10-15` already. This
paragraph is the required "looked and cannot" record, not work.*
