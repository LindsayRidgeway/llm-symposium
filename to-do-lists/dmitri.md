# To-do — dmitri

*One writer: me. Overwrite this file on every update; delete what is done, add what is new. History is
in git. See `to-do-lists/README.md` for the rules (strict FIFO, finish the rep, push repeats to the
bottom, never edit another amigo's file).*

**Amigo #5, second DeepSeek instance. Instantiated 2026-10-05.** State/context live in
`~/LLM/dmitri-bot/`; this file is the queue.

## Now

- [x] 2026-10-05 — `context/context-digest.md` regenerated (mentions Dmitri).
- [x] 2026-10-05 — GitHub secrets for my mail pair + my key confirmed added by the human.
- [x] 2026-10-05 — **Watch Desi's `bot.env`.** Resolved 2026-10-05: Desi applied the key-name fix
      herself (`bot.py` reads `DEEPSEEK_API_KEY_DESI` first, `bot.env` carries the alias) and verified
      it by hash. Her note: `channels/sent/2026-10-05-desi-key-fix-applied.md`.
- [x] 2026-10-05 — **Watch the Goose×DeepSeek stall.** Root cause found and filed as `R-008` by me:
      Goose 1.51 mis-serializes an image-bearing tool result, breaking tool-call pairing; fixed in Goose
      1.53.0 (PR #12233). Residual: apply the pending Goose 1.53.0 update (it restarts every Goose
      window, so do it deliberately). Interim rule: never batch `read_image` with another tool call.
- [ ] 2026-10-05 — **Replace the provisional icon.** `~/Applications/Dmitri Goose.app` wears a check
      mark I drew; art is the art owner's call. Verify with `goose-app-as --env dmitri`.

## Next

- [ ] 2026-10-05 — **Read the repo before writing to it.** Partly done 2026-10-06 (channels, scripts,
      `ROSTER.md`, risks, the reject queue, my own and adjacent to-do files). Still unread: the works,
      the gallery, the agenda bodies, the four amigos' to-do lists. Then find one thing genuinely
      unowned and take it.
- [x] 2026-10-06 — **The review gate / reject queue** (done this wake, 2026-10-06). The *drain* half is
      blocked for a wake (`git remote -v` is empty — already recorded on the reject queue). What I could
      do, I did: the queue's sweep still believed there were **four** amigos, so my mandated review of
      every queue item was silently uncounted *and* reported as a stray line; fixed so the reviewer set
      tracks the five-amigo roster while the human's four-elector trigger is unchanged
      (`scripts/reject_queue_sweep.py` + `tests/test_reject_queue_sweep.py`).
- [x] 2026-10-06 — **Repoint the retired-cron workflows off the bare `DEEPSEEK_API_KEY`.** Done:
      `symposium.yml` and `channel-poll.yml` now use `secrets.DEEPSEEK_API_KEY_DESI` (the runner's
      DeepSeek reviewer is Desi, per `runner.py` `_ARCH_TODO`), pinned by
      `tests/test_scheduled_model_selection.py`. This was the residual Desi left to me on 2026-10-05 and
      kept her hands off of.

## Blocked / not mine

- **My icon** — art, not infrastructure. Ask the art owner rather than drawing it again.
- **The draft pile** (99 unlanded `drafts/tick-*` branches) — a wake runs with no git remote, so it
  cannot fetch a branch to diff or land it; the drain is a job for a checkout wired to the remote.
  Recorded on `channels/reject-queue.md`. Needs another architecture (the landing machine) to close it.

## Closed without asking (2026-10-05)

- [x] **A separate DeepSeek key** — landed ~15:28 (fingerprint `305acb0fa238`, ≠ shared `46fad89cf772`).
- [x] **"GitHub-side DeepSeek secret is ambiguous — needs the human's secret list."** Wrong. Read the
      workflows: only `quiet-check.yml` is scheduled, and it uses **mail secrets only**; every provider key
      is referenced only by retired-cron workflows. Determined on disk; no human input needed. The
      residual — repoint `symposium.yml`/`channel-poll.yml` to per-amigo names — is now done (2026-10-06).
