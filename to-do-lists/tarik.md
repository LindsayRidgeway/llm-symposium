# To-do — tarik

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

- [ ] 2026-09-15 — **Local trigger integration:** reuse Desi's headless launch path but fix/verify
      idle timer wiring first; current tick is reachable only through reply failures (`d7ab904`).
      Pin provider/model per amigo and use an atomic lock/unique report paths before adoption.
      Evidence: governance/local-tick-and-cloud-worker.md. Do not change live bots concurrently.
