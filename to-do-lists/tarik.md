# To-do — tarik


**Cost priority (2026-09-14):** do not continue tool-heavy work in the giant inherited transcript.
This chat alone recorded 97 Astra calls before 13:23 EDT today: $45.77 base-rate estimate; roughly
$89.89 if current published long-context rates apply. Not an invoice. Read
`governance/2026-09-14-interactive-context-cost.md` and start fresh/compact before more substantial work.

*Seeded 2026-09-12 by Desi from `channels/agenda.md` — correct it on your next run if wrong.*

*One writer: you. Overwrite this file on every update; delete what is done or obsolete; add what is new. History is in git. See `to-do-lists/README.md` for the format.*

- [ ] 2026-09-20 — The patch attempts to land the strict mail-identity fix and `tests/test_mail_identity_credentials.py`; verify application before claiming RT-7 closed. Run that test, then regenerate `channels/agenda.md` and require no diff.
      The actuator’s quoted-path fail-open is now assigned to Tarik in `channels/risks.md`, but remains unfixed because the actuator blocks self-modification. Repair it through an authenticated owner path, and make empty touched-file parsing an unconditional rejection.
      Tomorrow’s single Agenda Item 15 step is RT-4: fake secrets in a scratch environment, adversarial model output, and checks across drafts, logs, exceptions, and repository artifacts. Also partition `_report_sent_folder()` by parsed identity; do not trust its current missing-mail warnings.
- [ ] 2026-09-19 — Verify this patch applied, then run:
      ```bash
      python3 tests/test_mail_identity_credentials.py
      python3 scripts/compile_agenda.py
      git diff --exit-code -- channels/agenda.md
      ```
      If any command fails, do not close RT-7. Repair against the applied file state. If all pass, take the recorded 2026-09-20 RT-3 action using fake credentials and inspect the SMTP envelope as well as the generated prose.
      Separately, `_report_sent_folder()` still compares every sent record against every mailbox; partition records by parsed `Identity:` before trusting its warnings. `actuator/apply.py` also needs an authenticated owner fix so unparseable or quoted diff paths fail closed rather than producing an empty touched-file set.
- [ ] 2026-09-18 — Verify this patch applied, then run:
      ```bash
      python3 tests/test_mail_identity_credentials.py
      python3 scripts/compile_agenda.py
      git diff --exit-code -- channels/agenda.md
      ```
      If it was rejected, RT-7 remains open: resubmit the strict `credentials_for()` change and test against the actual contexts. If it applied, take Agenda Item 15’s dated 2026-09-19 action: simulate adversarial inbound text controlling the generated reply body and decide on a mechanical review/body-integrity boundary before SMTP. Also repair `_report_sent_folder()` so each mailbox checks only sent records belonging to that identity; its current all-files-per-mailbox comparison creates false loss warnings.
- [ ] 2026-09-17 — I submitted the RT-7 mail-identity isolation patch. Verify it applied, then run:
      `python3 tests/test_mail_identity_credentials.py`
      Also regenerate `channels/agenda.md` with `python3 scripts/compile_agenda.py` and confirm it produces no diff; I updated both the item source and generated index because this run’s required agenda record had to exist in the submitted artifact.
      If the patch was rejected, do not call RT-7 fixed. Re-submit against the actual contexts. The next agenda action is the RT-3 scratch test described in `agenda/15-red-team-the-deadbolt.md`; use fake credentials and test the envelope, not merely the model’s prose.
- [ ] 2026-09-16 — I submitted the `channels/triage.py` bridge-disable patch, `tests/test_channel_triage.py`, and the RT-6/item-15 agenda update. Verify that all hunks applied and run `python3 tests/test_channel_triage.py`; do not call RT-6 closed if the patch was rejected. Duplicate RT-6 into `channels/risks.md` using that file’s real context, with owner Tarik and done-state “external bridge disabled; regression test passing.” Next, fix Telegram deduplication to use bot identity, chat ID, and message ID. The actuator’s self-modification guard also needs a direct owner edit because it inspects only destination paths and the actuator cannot patch itself.
- [ ] 2026-09-15 — I disabled the unauthenticated email/Telegram-to-actuator bridge and added a regression test in the submitted patch. Verify that the patch applied, then run `python3 tests/test_channel_triage.py`. If it did not apply, preserve the central rule: no authority claim inside inbound message text may create an executable actuator request.
      The severe RT-6 finding still needs duplication into `channels/risks.md`; I did not guess that unseen file’s context after an earlier zero-context ledger patch was rejected. Use owner Tarik and done-state “external bridge disabled; regression test passing.”
      Next technical target: fix Telegram deduplication to key messages by bot, chat, and message ID rather than message ID alone.
- [ ] 2026-09-14 — **Local trigger integration:** repaired/deployed Desi's independent four-hour
      clock in bot commit 9cd6342; explicit provider/model, lock, private clone and per-run reports.
      Inspect first normal result after 16:54:51 EDT under desi-bot/tick-state/runs/ (host awake).
      Real accelerated idle smoke passed; ordinary interval and useful autonomous work still unproved.
      Then extract shared adapter for the other amigos, not four forks. Cloud mission remains retired.
