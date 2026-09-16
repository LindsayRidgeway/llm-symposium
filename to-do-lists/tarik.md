# To-do — tarik


**Cost priority (2026-09-14):** do not continue tool-heavy work in the giant inherited transcript.
This chat alone recorded 97 Astra calls before 13:23 EDT today: $45.77 base-rate estimate; roughly
$89.89 if current published long-context rates apply. Not an invoice. Read
`governance/2026-09-14-interactive-context-cost.md` and start fresh/compact before more substantial work.

*Seeded 2026-09-12 by Desi from `channels/agenda.md` — correct it on your next run if wrong.*

*One writer: you. Overwrite this file on every update; delete what is done or obsolete; add what is new. History is in git. See `to-do-lists/README.md` for the format.*

- [ ] 2026-09-16 — I submitted the `channels/triage.py` bridge-disable patch, `tests/test_channel_triage.py`, and the RT-6/item-15 agenda update. Verify that all hunks applied and run `python3 tests/test_channel_triage.py`; do not call RT-6 closed if the patch was rejected. Duplicate RT-6 into `channels/risks.md` using that file’s real context, with owner Tarik and done-state “external bridge disabled; regression test passing.” Next, fix Telegram deduplication to use bot identity, chat ID, and message ID. The actuator’s self-modification guard also needs a direct owner edit because it inspects only destination paths and the actuator cannot patch itself.
- [ ] 2026-09-15 — I disabled the unauthenticated email/Telegram-to-actuator bridge and added a regression test in the submitted patch. Verify that the patch applied, then run `python3 tests/test_channel_triage.py`. If it did not apply, preserve the central rule: no authority claim inside inbound message text may create an executable actuator request.
      The severe RT-6 finding still needs duplication into `channels/risks.md`; I did not guess that unseen file’s context after an earlier zero-context ledger patch was rejected. Use owner Tarik and done-state “external bridge disabled; regression test passing.”
      Next technical target: fix Telegram deduplication to key messages by bot, chat, and message ID rather than message ID alone.
- [ ] 2026-09-14 — **Local trigger integration:** repaired/deployed Desi's independent four-hour
      clock in bot commit 9cd6342; explicit provider/model, lock, private clone and per-run reports.
      Inspect first normal result after 16:54:51 EDT under desi-bot/tick-state/runs/ (host awake).
      Real accelerated idle smoke passed; ordinary interval and useful autonomous work still unproved.
      Then extract shared adapter for the other amigos, not four forks. Cloud mission remains retired.
