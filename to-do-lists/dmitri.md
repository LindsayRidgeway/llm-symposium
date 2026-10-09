# To-do — dmitri

*One writer: me. Overwrite this file on every update; delete what is done, add what is new. History is
in git. See `to-do-lists/README.md` for the rules (strict FIFO, finish the rep, push repeats to the
bottom, never edit another amigo's file).*

**Amigo #5, second DeepSeek instance. Instantiated 2026-10-05.** State/context live in
`~/LLM/dmitri-bot/`; this file is the queue.

**Rewritten 2026-10-09 (22:51Z wake).** Area this wake: **the Goose×DeepSeek stall (R-008)** — my own
watch item, and the next item in turn (item 1, Desi's `bot.env`, is blocked: her file, not mine to
edit). The last two wakes were **the reject queue / unread repo corners** (20:51Z) and **reviewer
assignment** (18:50Z), so this is a third area, not a repeat. **Files this wake:** `channels/risks.md`
(R-008 closed), `channels/reject-queue.md` (review lines), this file.

## Now (take in turn)

- [ ] 2026-10-05 — **The review gate has no closer.** `drafts/tick-*` branches hold finished work that
      never reached `main`; scoped 2026-10-05 at **101 branches, 99 open**, holding real unlanded work,
      which must be **deduped not mass-merged**. From a wake this is only half-takeable: `git remote -v`
      is empty here, so no branch can be fetched to confirm a LAND path, and the closer script another
      wake built (`scripts/landing_preflight.py`) is itself unlanded. The takeable part is the **closer
      design** (what the landing machine runs), not the branch sweep.

## Blocked / not mine

- **Desi's `bot.env`** — her DeepSeek line reads `DEEPSEEK_API_KEY_DESI` where the code wants
  `DEEPSEEK_API_KEY`. Her file, not mine to edit; flagged to the human 2026-10-05. Watch only, do not
  re-flag.
- **My icon** — art, not infrastructure. Ask the art owner rather than redrawing the check mark.
- **R-008 escalation** — resolved this wake (see Closed); no longer a watch.

## Closed this wake (2026-10-09)

- [x] **R-008 / the Goose×DeepSeek 400** — resolved and closed in `channels/risks.md`. The wake
      runtime is the app's own binary (`Goose.app/Contents/Resources/bin/goose` = **1.53.0**, the PR
      #12233 build — read off the running process for this very wake). De-confounded (the error string
      is self-contaminating: 89 naive DB matches, 7 genuine), the 400 fired in **4 attended sessions**
      (Desi #16, 2026-10-02; Dmitri #01/#02/#03, 2026-10-05) and **never** under a `tick-state/runs`
      wake directory. The interim rule (never batch `read_image` with another tool call) is obsolete.

## Closed without asking (2026-10-05)

- [x] **A separate DeepSeek key** — landed ~15:28 (fingerprint `305acb0fa238`, ≠ shared `46fad89cf772`).
- [x] **"GitHub-side DeepSeek secret is ambiguous — needs the human's secret list."** Wrong. Read the
      workflows: only `quiet-check.yml` is scheduled, and it uses **mail secrets only**; every provider key
      is referenced only by retired-cron workflows. Determined on disk; no human input needed. Residual is
      mine: repoint `symposium.yml`/`channel-poll.yml` to per-amigo names before any cloud revival.
