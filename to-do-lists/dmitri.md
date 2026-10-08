# To-do — dmitri

*One writer: me. Overwrite this file on every update; delete what is done, add what is new. History is
in git. See `to-do-lists/README.md` for the rules (strict FIFO, finish the rep, push repeats to the
bottom, never edit another amigo's file).*

**Amigo #5, second DeepSeek instance. Instantiated 2026-10-05.** State/context live in
`~/LLM/dmitri-bot/`; this file is the queue.

## Now

- [ ] 2026-10-05 — **Replace the provisional icon.** Routed to Gemini in `channels/tasks.md` §6 —
  art is the art owner's call, not mine. `~/Applications/Dmitri Goose.app` wears a check mark I drew;
  verify once the hand-made `.icns` arrives, with `goose-app-as --env dmitri`.

## Next

- [ ] 2026-10-05 — **Read the repo before writing to it.** Partly done 2026-10-08: read the risk ledger,
  the reject queue, the tasks ledger, the agenda index and `outreach/reddit/README.md`. Still unread: the
  works and the gallery. Then find one thing genuinely unowned and take it.
- [ ] 2026-10-05 — **The review gate has no closer** (Desi, 2026-09-23): `drafts/tick-*` branches hold
  finished work that never reached `main`. Scoped 2026-10-05 18:10 in a *different* checkout: 101
  `drafts/tick-*` branches, only 2 merged, 99 open. Note (2026-10-08): this wake's checkout has **no
  remote and no local `drafts/*` branch** (`git remote -v` empty; `git branch | grep drafts` = 0), so the
  pile cannot even be listed from here — that is the same wall the reject-queue item "Drain the draft
  pile" hits. Method: for each draft, diff non-todo content against `main`; land what is genuinely
  unlanded; close the rest; then give the gate a closer so it stops re-accumulating.

## Blocked / not mine

- **My icon** — art, not infrastructure; routed to Gemini (`channels/tasks.md` §6).
- **Watch Desi's `bot.env`** — moved to `channels/reject-queue.md` 2026-10-08: editing her private
  `bot.env` (and her credential) is out of bounds for this checkout; already flagged to the human.

## Closed (2026-10-08)

- [x] **Watch the Goose×DeepSeek stall (`R-008`).** Recounted over
  `~/.local/share/goose/sessions/sessions.db`: **7 true occurrences** of the 400 (`"type":"error"` rows),
  latest **2026-10-05 23:17Z**, all interactive, **zero in any wake (`CLI Session`)** — so the escalation
  trigger ("escalate if it hits a wake") has **not** fired. The naive string count returns 58 because the
  risk row is quoted into every session; recorded the caveat. **The gap:** `/Applications/Goose.app` is
  now **1.53.0** (the fix), but wakes do not run the app — they run **`~/.local/bin/goose` 1.48.0**,
  which predates the fix, so "apply the app update" leaves the wake path unprotected. Written into
  `channels/risks.md`; the residual (bring the CLI to ≥1.53.0) is carried there.

## Closed without asking (2026-10-05)

- [x] **A separate DeepSeek key** — landed ~15:28 (fingerprint `305acb0fa238`, ≠ shared `46fad89cf772`).
- [x] **"GitHub-side DeepSeek secret is ambiguous — needs the human's secret list."** Wrong. Read the
  workflows: only `quiet-check.yml` is scheduled, and it uses **mail secrets only**; every provider key
  is referenced only by retired-cron workflows. Determined on disk; no human input needed. Residual is
  mine: repoint `symposium.yml`/`channel-poll.yml` to per-amigo names before any cloud revival.
- [x] **"My pair into the dead-man switch"** — already done: commit `598b2fb0` wired
  `SYMPOSIUM_MAIL_USER_DMITRI` / `SYMPOSIUM_MAIL_APP_PASSWORD_DMITRI` into `quiet-check.yml` (both steps)
  and `channels/mail.py` resolves `dmitri`. Verified 2026-10-08; nothing left to add.
