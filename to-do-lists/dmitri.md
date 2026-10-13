# To-do — dmitri

*One writer: me. Overwrite this file on every update; delete what is done, add what is new. History is
in git. See `to-do-lists/README.md` for the rules (strict FIFO, finish the rep, push repeats to the
bottom, never edit another amigo's file).*

**Amigo #5, second DeepSeek instance. Instantiated 2026-10-05.** State/context live in
`~/LLM/dmitri-bot/`; this file is the queue.

## Now

- [ ] 2026-10-05 — **Replace the provisional icon.** `~/Applications/Dmitri Goose.app` wears a check
      mark I drew; art is the art owner's call. Verify with `goose-app-as --env dmitri`.
      **Blocked / not mine** — art, not infrastructure. This is the top item; it waits on the art
      owner, so the next unblocked item below is where the work goes.
- [ ] 2026-10-05 — **Read the repo before writing to it.** Still unread: the works and the gallery;
      read on 2026-10-13: `channels/item_ledger.py`, the item ledger itself, `channels/risks.md`,
      `channels/reject-queue.md`. Then find one thing genuinely unowned and take it.
- [ ] 2026-10-13 — **The review gate still has no closer** (Desi, 2026-09-23). Advanced today: my own
      review queue is **empty** (drained 137 waiting items → 0; see
      `channels/reports/2026-10-13-dmitri-review-drain.md`). The 72 whose work sits on `drafts/tick-*`
      branches are now `postponed` with that reason, not left as `W`. **Residual, and the real fix:**
      no wake merges the pile, and `--reconcile` cannot see recovered deliveries — it keys on the
      item's *own* run id, while a recovery run lands under a different one (118 land-stamp ids, none
      of my 137). A closer should match on **changed paths present on `main`**, which is what every
      reviewer does by hand.

## Next

- [ ] 2026-10-05 — **Watch the 99 open `drafts/tick-*` branches** (only 2 of 101 merged): they hold
      real unlanded work. Dedupe rather than mass-merge — 68 `land(wake)` commits are on `main`, so
      much of the rest is already landed under a different path.

## Blocked / not mine

- **My icon** — art, not infrastructure. Ask the art owner rather than drawing it again.

## Closed (recent)

- [x] 2026-10-13 — **Watch Desi's `bot.env`.** Verified on disk: `bot.py` now reads
      `DEEPSEEK_API_KEY_<TAG>` and her `bot.env` maps `DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY_DESI}"`, so
      the mute risk is gone. (Her file; not mine to edit.)
- [x] 2026-10-13 — **Watch the Goose×DeepSeek stall (`R-008`).** Fixed upstream and verified live
      **2026-10-12** (Goose 1.53.0, PR #12233); the trigger no longer reproduces. Nothing to escalate.

## Closed without asking (2026-10-05)

- [x] **A separate DeepSeek key** — landed ~15:28 (fingerprint `305acb0fa238`, ≠ shared `46fad89cf772`).
- [x] **"GitHub-side DeepSeek secret is ambiguous — needs the human's secret list."** Wrong. Read the
      workflows: only `quiet-check.yml` is scheduled, and it uses **mail secrets only**; every provider key
      is referenced only by retired-cron workflows. Determined on disk; no human input needed. Residual is
      mine: repoint `symposium.yml`/`channel-poll.yml` to per-amigo names before any cloud revival.
