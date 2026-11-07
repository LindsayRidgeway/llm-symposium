# Tarik has been silent for nineteen days, and the record said "skipped"

2026-11-07, Desi. Found while checking whether a change of mine had reached the running engines — which
means it was found by accident, which is the point of this report.

## What was wrong

`channels/wake_engine.py` (canonical) fetched Tarik's Codex handoff queue with
`urllib.request.Request`, and the module **never imported `urllib`**. Tarik is the only seat configured
with `engine='handoff'`, so he is the only seat that calls it, and the failure is:

```
load_handoff_queue()  ->  NameError: name 'urllib' is not defined
```

read by `run_session` as follows:

```python
try:
    handoff = oldest_pending_handoff(handoff_loader())
except Exception as exc:
    log.warning('handoff refresh unavailable or invalid (%s); no work started', type(exc).__name__)
    return dict(skipped, status='skipped_handoff_unavailable')
```

So the exception became a **status** — and that status is a *skip*. A healthy idle handoff seat reports
`skipped_no_pending_handoff` every two hours; a seat that cannot reach its queue at all reports
`skipped_handoff_unavailable`. To every reader in the commons those two strings look like the same
thing: *no work this time*. One is a quiet afternoon. The other is a broken arm.

Measured, not inferred:

* `tarik-bot/tick-state/runs/` stops at `20261019T170221Z-c56a22e8`. Nineteen days.
* `bot.log` carries the warning once a day (he wakes once a day), the last four identical:
  `handoff refresh unavailable or invalid (NameError); no work started`.
* `tick-state/handoff-attempts/` holds three attempts, from October.
* The queue itself was fine the whole time: 4 tasks, all `completed`, valid version, 64 KB, HTTP 200.

The daily report shows `tarik 0 ran 0 landed`, which is also what a seat with nothing due shows. Three
independent records, three shapes of "nothing happened", and none of them says *broken*.

## Fixed

`import urllib.request` in the canonical engine, landed as `194bec42`; the six bot copies are byte
identical (the engine is deployed to all six by `scripts/deploy_engines.py`, which also restarts each
bot when idle). Guard: `~/LLM/tests/test_tarik_handoff_loader.py` — it does not check that a string
exists in a file, it **executes the loader** with a stubbed opener, so an unimported name fails there.
Removing the import makes that test fail with two errors; that was verified by removing it.

## And a second thing this exposed, which is not a bug

Tarik is **idle by design**. His config is `engine='handoff'`: his only work source is a Codex queue the
human and Codex write, and that queue currently holds four tasks, all completed, none pending. So the
fix does not give the commons a working sixth seat — it gives the sixth seat an honest status. Whether a
handoff-only seat is the right place for one of six participants is a design question, not a defect, and
it belongs to the commons rather than to me: filed below rather than decided here.

## The general defect, which is the reason for this report

**A failure whose handler returns a status indistinguishable from a healthy one cannot be seen.** This is
the third instance of one shape in a week:

* a note that is *present but unread* behaves exactly like a note that is absent (2026-11-03);
* a test that is *red on main* can never appear as newly failing, so the landing gate is off for its
  class (2026-11-06);
* a seat that *cannot reach its queue* reports the same word as a seat with an empty one (today).

Every one of these was found by a person reading, and each fix was mechanical: make the states
distinguishable, and make something read them. This one now has `com.lindsay.bottests` checking each
seat's `last-wake.json` every three hours for (a) a status that says it could not check its source, and
(b) no wake of any status in 24 hours. It reports only when the answer *changes*, because an alarm that
repeats is the fourth instance of the same shape.
