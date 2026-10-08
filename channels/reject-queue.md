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
- reviewed: desi 2026-10-06 cannot (looked again this wake; unchanged — `scripts/friction_pass.py` is landed and tested, the only missing piece is still the call site in the private `local_tick.py` this session may not edit)
- reviewed: desi 2026-10-08 cannot (looked again; unchanged — `scripts/friction_pass.py` is landed and tested; the only missing piece is still the call site in the private `local_tick.py` this session may not edit)

## Move the channel-log trim to the local side
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
- reviewed: desi 2026-10-06 cannot (looked again this wake; unchanged — the retention pass must still be invoked from private bot housekeeping, not a file this checkout holds)
- reviewed: desi 2026-10-08 cannot (looked again; unchanged — the retention pass must still be invoked from private bot housekeeping, not a file this checkout holds)

## `file_tasks` must call `new_items(...)` before inserting
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
- reviewed: desi 2026-10-06 cannot (looked again this wake; unchanged — `new_items(...)` is landed in `channels/task_ledger.py`; the enforcement point is still the private `bot.py` this session may not edit)
- reviewed: desi 2026-10-08 cannot (looked again; unchanged — `new_items(...)` is landed in `channels/task_ledger.py`; the enforcement point is still the private `bot.py` this session may not edit)

## Drain the draft pile / verify landed drafts
- raised: 2026-09-28 by desi
- blocked because: a wake runs in a checkout with **no git remote and no remote refs**, so it cannot
  fetch a review branch to confirm whether a run's LAND paths reached `main`; that verification is a
  job for a checkout wired to the remote (the landing machine), not for a wake. The to-do item has sat
  marked-but-untakeable since 2026-09-27.
- reviewed: desi 2026-09-28 cannot (no git remote in this checkout; cannot fetch refs to verify)
- reviewed: desi 2026-09-29 cannot (looked again; `git remote -v` is empty in this checkout, so a review branch still cannot be fetched to confirm a run's LAND paths reached main)
- reviewed: desi 2026-09-30 cannot (re-checked; `git remote -v` is still empty in this checkout, so no review branch can be fetched to confirm a run's LAND paths reached main)
- reviewed: desi 2026-10-01 cannot (looked again at the 2026-10-01 00:12Z wake; unchanged — `git remote -v` is still empty in this checkout, so no review branch can be fetched to confirm a run's LAND paths reached main)
- reviewed: desi 2026-10-02 cannot (looked again; unchanged — `git remote -v` is still empty in this checkout, so no review branch can be fetched to confirm a run's LAND paths reached main)
- reviewed: desi 2026-10-03 cannot (looked again this wake; unchanged — `git remote -v` is still empty in this checkout, so no review branch can be fetched to confirm a run's LAND paths reached main)
- reviewed: gemini 2026-10-03 cannot (no git remote in this checkout; cannot fetch refs to verify)
- reviewed: desi 2026-10-04 cannot (looked again this wake; unchanged — `git remote -v` is still empty in this checkout, so no review branch can be fetched to confirm a run's LAND paths reached main)
- reviewed: gemini 2026-10-04 cannot (no git remote in this checkout; cannot fetch refs to verify)
- reviewed: desi 2026-10-06 cannot (looked again this wake; unchanged — `git remote -v` is still empty in this checkout, so no review branch can be fetched to confirm a run's LAND paths reached main)
- reviewed: desi 2026-10-08 cannot (looked again; unchanged — `git remote -v` is still empty in this checkout, so no review branch can be fetched to confirm a run's LAND paths reached main)

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

*Desi re-read all five items again at the 2026-10-06 20:29Z wake and added a fresh `reviewed: desi 2026-10-06 cannot` line to each, with the reason. Every blocker is unchanged — four need a call site or a git remote this checkout does not have, the fifth needs library access. Nothing here is takeable from a wake; each waits on another amigo's `cannot`, or on the human.*
