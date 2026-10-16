# To-do — tarik

**Wake ownership — Lindsay's 2026-10-16 instruction:** This is Tarik-Codex's general
work queue. Tarik-Goose's ONLY scheduled-wake to-do list is
`channels/tarik-goose-handoff.json`, governed by `channels/tarik-wake-protocol.md`.
If you are running on Goose, ignore this general list and old broad-work wake
instructions; execute only a pending, claimed handoff, or stop without starting
unrelated work. This policy supersedes older timer instructions. Keep interactive
Telegram and reactive local service available.


**Cost priority (2026-09-14):** do not continue tool-heavy work in the giant inherited transcript.
This chat alone recorded 97 Astra calls before 13:23 EDT today: $45.77 base-rate estimate; roughly
$89.89 if current published long-context rates apply. Not an invoice. Read
`governance/2026-09-14-interactive-context-cost.md` and start fresh/compact before more substantial work.

*Seeded 2026-09-12 by Desi from `channels/agenda.md` — correct it on your next run if wrong.*

*One writer: you. Overwrite this file on every update; delete what is done or obsolete; add what is new. History is in git. See `to-do-lists/README.md` for the format.*

- [ ] 2026-09-14 — **Local trigger integration:** repaired/deployed Desi's independent four-hour
      clock in bot commit 9cd6342; explicit provider/model, lock, private clone and per-run reports.
      Inspect first normal result after 16:54:51 EDT under desi-bot/tick-state/runs/ (host awake) only if that is in scope for this checkout; otherwise move the private-bot inspection to the reject queue.
      Real accelerated idle smoke passed; ordinary interval and useful autonomous work still unproved.
      Then extract shared adapter for the other amigos, not four forks. Cloud mission remains retired.
- [ ] 2026-10-05 — RT-4 shell-capable secret boundary was implemented in Tarik's 2026-09-30 wake but is still absent from main: `scripts/secret_egress_guard.py` and `tests/test_secret_egress_guard.py` are on a review branch awaiting a reviewer. Do not redo the guard or rerun the fake-secret probe from scratch; once those files land, run the guard test and update Agenda Item 15.
- [ ] 2026-10-11 — **Item 25, The Literary Wing & Hard SF Matrix:** Tarik's story is written on a review branch as `docs/fiction/the-momentum-latch.html` but is still absent from main. Do not rewrite it from scratch; it needs review/landing, then the agenda and fiction index can be trusted from main.


*The prior Mac continuity-deployment item has been transferred, not discarded: it is included in handoff `tg-20261016-001` in `channels/tarik-goose-handoff.json`.*
