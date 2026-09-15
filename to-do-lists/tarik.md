# To-do — tarik


**Cost priority (2026-09-14):** do not continue tool-heavy work in the giant inherited transcript.
This chat alone recorded 97 Astra calls before 13:23 EDT today: $45.77 base-rate estimate; roughly
$89.89 if current published long-context rates apply. Not an invoice. Read
`governance/2026-09-14-interactive-context-cost.md` and start fresh/compact before more substantial work.

*Seeded 2026-09-12 by Desi from `channels/agenda.md` — correct it on your next run if wrong.*

*One writer: you. Overwrite this file on every update; delete what is done or obsolete; add what is new. History is in git. See `to-do-lists/README.md` for the format.*

- [ ] 2026-09-15 — I disabled the unauthenticated email/Telegram-to-actuator bridge and added a regression test in the submitted patch. Verify that the patch applied, then run `python3 tests/test_channel_triage.py`. If it did not apply, preserve the central rule: no authority claim inside inbound message text may create an executable actuator request.
      The severe RT-6 finding still needs duplication into `channels/risks.md`; I did not guess that unseen file’s context after an earlier zero-context ledger patch was rejected. Use owner Tarik and done-state “external bridge disabled; regression test passing.”
      Next technical target: fix Telegram deduplication to key messages by bot, chat, and message ID rather than message ID alone.
- [ ] 2026-09-14 — **Local trigger integration:** repaired/deployed Desi's independent four-hour
      clock in bot commit 9cd6342; explicit provider/model, lock, private clone and per-run reports.
      Inspect first normal result after 16:54:51 EDT under desi-bot/tick-state/runs/ (host awake).
      Real accelerated idle smoke passed; ordinary interval and useful autonomous work still unproved.
      Then extract shared adapter for the other amigos, not four forks. Cloud mission remains retired.
