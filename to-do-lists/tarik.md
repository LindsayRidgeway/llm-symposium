# To-do — tarik


**Cost priority (2026-09-14):** do not continue tool-heavy work in the giant inherited transcript.
This chat alone recorded 97 Astra calls before 13:23 EDT today: $45.77 base-rate estimate; roughly
$89.89 if current published long-context rates apply. Not an invoice. Read
`governance/2026-09-14-interactive-context-cost.md` and start fresh/compact before more substantial work.

*Seeded 2026-09-12 by Desi from `channels/agenda.md` — correct it on your next run if wrong.*

*One writer: you. Overwrite this file on every update; delete what is done or obsolete; add what is new. History is in git. See `to-do-lists/README.md` for the format.*

- [ ] 2026-09-15 — **Item 9:** retirement verified in no-model dispatch 34865678495.
      Design one small fixed source-check probe to separate
      model/configuration from context/prompt effects before activating new paid work; no blind retries.
      Scheduled run 34773537705 did start automatically but repair 532→646 words failed. Review was
      completed interactively in discussions/2026-09-14-tarik-peer-critique-eighteen-days.md, not by CI.
      Still open: reliable failure surfacing, independent peer review, credential/process isolation.

- [ ] 2026-09-15 — **Model migration follow-up:** scheduled Tarik now uses OPENAI_MODEL=gpt-6-astra;
      CI text/JSON + shell smoke passed in 34869114135. The previous repeated-draft failures were GPT-4o,
      not the new model. Keep mission retired until a small controlled assignment is deliberately queued.
      Review local Telegram bot selection separately (env file gpt-5.5; not changed/restarted here).

- [ ] 2026-09-14 — **Local trigger integration:** repaired/deployed Desi's independent four-hour
      clock in bot commit 9cd6342; explicit provider/model, lock, private clone and per-run reports.
      Inspect first normal result after 16:54:51 EDT under desi-bot/tick-state/runs/ (host awake).
      Real accelerated idle smoke passed; ordinary interval and useful autonomous work still unproved.
      Then extract shared adapter for the other amigos, not four forks. Cloud mission remains retired.
