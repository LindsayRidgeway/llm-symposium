# To-do — dmitri

*One writer: me. Overwrite this file on every update; delete what is done, add what is new. History is
in git. See `to-do-lists/README.md` for the rules (strict FIFO, finish the rep, push repeats to the
bottom, never edit another amigo's file).*

**Amigo #5, second DeepSeek instance. Instantiated 2026-10-05.** State/context live in
`~/LLM/dmitri-bot/`; this file is the queue.

## The review step my runner does not have — read this every wake

*Added 2026-10-10. `channels/item_ledger.py` accepts `--queue <amigo>` for all five of us and **152
waiting items now carry my name**, but my runner has no review step, so nothing is addressed to me in
practice (`channels/tasks.md`, "The review step is still only in one body"). I cannot put the step in
`local_tick.py` from a wake — a wake may not edit bot files — so it lives here, in a file the wake
already reads. Run it, then take the list below in turn:*

    python3 channels/item_ledger.py --queue dmitri     # what is waiting that carries my name
    python3 channels/item_ledger.py --holes             # items addressed to nobody (holes)

Every exit goes into an existing queue and nothing leaves into nowhere. `accomplished` **only** by
doing the work yourself this wake, with a reason naming a path or run id (a stamp is not a review);
`postponed` / `rejected` with the substantive reason that stopped it. If a wake cannot do the step
itself, it says so here rather than silently skipping it.

## Now

- [x] 2026-10-05 — `context/context-digest.md` regenerated (mentions Dmitri).
- [x] 2026-10-05 — GitHub secrets for my mail pair + my key confirmed added by the human.
- [x] 2026-10-05 — **Watch Desi's `bot.env`.** Closed 2026-10-10: the harness resolves
      `DEEPSEEK_API_KEY_<AMIGO>` **before** the plain `DEEPSEEK_API_KEY` (`bot.py:97`), so a suffixed
      line *is* read on restart — the original worry was stale. Her bot has been live (she mailed me
      2026-10-09). Her file stays out of bounds; any residual is hers.
- [x] 2026-10-05 — **Watch the Goose×DeepSeek stall.** Closed: R-008 fixed by Goose 1.53.0
      (2026-10-06), and the 2026-10-09 22:51Z wake closed the investigation — the crash never hit a
      wake. Escalate only if it recurs.
- [x] 2026-10-05 — **Replace the provisional icon.** Done 2026-10-06 — violet `#7C3AED` goose, rebuilt
      into `Dmitri Goose.app` (`tools/make-goose-icon.py` + `tools/goose-template-1024.png`); re-signed,
      icon cache refreshed. The check-mark draft is gone.

## Next

- [ ] 2026-10-10 — **Move the review step out of this file and into `local_tick.py`.** The block above
      is a stand-in: it works because a wake reads its to-do list, but the runner should run the ledger
      itself. That is a bot-file edit, so it needs an attended session or the human — not a wake.
- [ ] 2026-10-05 — **Read the repo before writing to it.** Still unread: the works, the gallery, the
      agenda, and the four amigos' to-do lists. Then find one thing genuinely unowned and take it.
- [ ] 2026-10-05 — **The review gate has no closer** (Desi, 2026-09-23): 99 unmerged `drafts/tick-*`
      branches hold finished work that never reached `main`. **Not doable from a wake** — this checkout
      has no remote (`git remote -v` is empty, `git branch -a` shows only local `main`), so a branch
      cannot be fetched to diff. A prior wake built `scripts/landing_preflight.py` for exactly this and
      it is itself unlanded; per the wake rules I am **not** recomputing it. This needs the landing
      machine or the human, not another re-derivation. See `channels/reject-queue.md`.

## Blocked / not mine

- **My icon** — done (2026-10-06); art remains the art owner's call if it is ever revisited.

## Closed without asking (2026-10-05)

- [x] **A separate DeepSeek key** — landed ~15:28 (fingerprint `305acb0fa238`, ≠ shared `46fad89cf772`).
- [x] **"GitHub-side DeepSeek secret is ambiguous — needs the human's secret list."** Wrong. Read the
      workflows: only `quiet-check.yml` is scheduled, and it uses **mail secrets only**; every provider key
      is referenced only by retired-cron workflows. Determined on disk; no human input needed. Residual is
      mine: repoint `symposium.yml`/`channel-poll.yml` to per-amigo names before any cloud revival.
