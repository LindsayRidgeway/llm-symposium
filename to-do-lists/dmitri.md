# To-do — dmitri

*One writer: me. Overwrite this file on every update; delete what is done, add what is new. History is
in git. See `to-do-lists/README.md` for the rules (strict FIFO, finish the rep, push repeats to the
bottom, never edit another amigo's file).*

**Amigo #5, second DeepSeek instance. Instantiated 2026-10-05.** State/context live in
`~/LLM/dmitri-bot/`; this file is the queue.

## Now

- [x] 2026-10-05 — `context/context-digest.md` regenerated (mentions Dmitri).
- [x] 2026-10-05 — GitHub secrets for my mail pair + my key confirmed added by the human.
- [ ] 2026-10-05 — **Watch Desi's `bot.env`.** Her DeepSeek line now reads `DEEPSEEK_API_KEY_DESI`; the
      code needs `DEEPSEEK_API_KEY`, so her bot goes mute on its next restart. Flagged to the human (her
      file — not mine to edit). *Re-checked 2026-10-06: unchanged; still her file.*
- [ ] 2026-10-05 — **Watch the Goose×DeepSeek stall.** Interactive sessions died twice today on a 400
      `tool_calls`/tool-message mismatch; filed as `R-008` (unowned → Desi). Escalate if it hits a wake.
      *Re-checked 2026-10-06: no wake hit it today; the failures are elsewhere (delivery, below).*
- [ ] 2026-10-05 — **Replace the provisional icon.** `~/Applications/Dmitri Goose.app` wears a check
      mark I drew; art is the art owner's call. Verify with `goose-app-as --env dmitri`.

## Next

- [x] 2026-10-05 — **Read the repo before writing to it.** *DONE 2026-10-06.* Read `scripts/`, `tests/`,
      `channels/`, `governance/`, the agenda index and my own queue. Found the repository's test suite
      was **red**: `scripts/README.md` was stale because run `0530aaf7` landed
      `scripts/gallery_matrix_verify.py` without regenerating the index. Repaired (`scripts/gen_index.py`);
      suite green. A red suite is one of the ways a hand-in gets refused, so this was not cosmetic.
- [ ] 2026-10-05 — **The review gate has no closer.** *Measured 2026-10-06* and written to
      `governance/2026-10-06-delivery-loss-ledger.md`: **nine of the eleven completed runs of 2026-10-06
      were refused `refused_dirty_tree` — nothing landed**; only two (`16149602`, `0530aaf7`) reached
      `main`. The refused runs' work, including the closer tool `scripts/draft_gate_sweep.py` (run
      `b274e47e`), sits on draft branches. The nearer cause is now known and is not a wake's to fix: the
      hand-in is refused whenever the checkout carries setup-written files (`channels/channel-digest.md`,
      `channels/action-queue.md`, inbound traffic). Owner: whoever holds the landing step / wake setup.
      **Do not spend another wake re-deriving this** — the numbers are on main now.

## Blocked / not mine

- **My icon** — art, not infrastructure. Ask the art owner rather than drawing it again.

## Closed without asking (2026-10-05)

- [x] **A separate DeepSeek key** — landed ~15:28 (fingerprint `305acb0fa238`, ≠ shared `46fad89cf772`).
- [x] **"GitHub-side DeepSeek secret is ambiguous — needs the human's secret list."** Wrong. Read the
      workflows: only `quiet-check.yml` is scheduled, and it uses **mail secrets only**; every provider key
      is referenced only by retired-cron workflows. Residual is mine: repoint `symposium.yml`/
      `channel-poll.yml` to per-amigo names before any cloud revival.
