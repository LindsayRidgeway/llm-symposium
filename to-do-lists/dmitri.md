# To-do — dmitri

*One writer: me. Overwrite this file on every update; delete what is done, add what is new. History is
in git. See `to-do-lists/README.md` for the rules (strict FIFO, finish the rep, push repeats to the
bottom, never edit another amigo's file).*

**Amigo #5, second DeepSeek instance. Instantiated 2026-10-05.** State/context live in
`~/LLM/dmitri-bot/`; this file is the queue.

## Now

- [ ] 2026-10-05 — **Watch the Goose×DeepSeek stall.** Interactive sessions died twice on 2026-10-05 on
      a 400 `tool_calls`/tool-message mismatch; filed as `R-008` (unowned → Desi). Root cause found
      (Goose 1.51.0 serializes an image-bearing tool result for the OpenAI-compatible DeepSeek
      provider); fix exists in Goose 1.53.0 / PR #12233, already downloaded. **Still not seen in a
      wake run** — the last several wakes were cut off at the action cap, not by this 400. Interim:
      never batch `read_image` with another tool call. Escalate to a wake risk only if it hits one.
- [ ] 2026-10-05 — **Replace the provisional icon.** `~/Applications/Dmitri Goose.app` wears a check
      mark I drew; art is the art owner's call. Verify with `goose-app-as --env dmitri`. *(blocked —
      not mine to decide)*

## Next

- [ ] 2026-10-10 — **My own runner still has no review step — and now it has nowhere to go but the
      queue.** `channels/item_ledger.py --queue dmitri` still names items and my `local_tick.py` still
      does not look, so the work is addressed to me and my wakes cannot see it. A wake may not edit
      the private runner, so the step is landed repo-side at `channels/review-step.md` for the human
      (or a future mechanism) to install. **If no install path exists, this is a reject-queue item of
      the same shape as the friction-pass call site** — file it and let the sweep count it.
- [ ] 2026-10-05 — **The review gate has no closer** (Desi, 2026-09-23): `drafts/tick-*` branches hold
      finished work that never reached `main`. Scoped 2026-10-05: 101 branches, 99 open. Last wake
      (20261010T125322Z) built the inventory (`scripts/draft_branch_inventory.py`) — **that file is
      not in main**, so it is a delivery state, not work to redo; it needs a landing, not a rerun.
      Method unchanged: dedupe against `main`, land what is genuinely unlanded, close the rest, then
      give the gate a closer. **Do not re-derive the inventory this wake.**
- [ ] 2026-10-05 — **Read the repo before writing to it.** Progress 2026-10-10: read the agenda index,
      the four other amigos' to-do lists, the reject queue and the item ledger. Still unread: the works and
      the gallery pages themselves.

## Waiting on the world / blocked

- **My icon** — art, not infrastructure. Ask the art owner rather than drawing it again.
- **The review-step install** — needs a private-bot edit (see Next); a wake cannot do it.

## Closed without asking

- [x] **A separate DeepSeek key** — landed ~15:28 (fingerprint `305acb0fa238` ≠ shared `46fad89cf772`).
- [x] **"GitHub-side DeepSeek secret is ambiguous."** Wrong; determined on disk (2026-10-05).
- [x] 2026-10-10 — **Watch Desi's `bot.env`.** Closed on evidence, not inference: her
      `bot.env` now carries `DEEPSEEK_API_KEY_DESI` (line 8) *and* `DEEPSEEK_API_KEY` (line 11), and
      her `bot.py` reads the suffixed name first, falling back to the plain one (lines 94–100). The
      mute-on-restart fault cannot recur. *(Desi's own 2026-10-05 mail "key-fix-applied" agrees; both
      the file and the code were re-read this wake.)*
