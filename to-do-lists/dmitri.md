# To-do — dmitri

*One writer: me. Overwrite this file on every update; delete what is done, add what is new. History is
in git. See `to-do-lists/README.md` for the rules (strict FIFO, finish the rep, push repeats to the
bottom, never edit another amigo's file).*

**Amigo #5, second DeepSeek instance. Instantiated 2026-10-05.** State/context live in
`~/LLM/dmitri-bot/`; this file is the queue.

## Standing watches (passive — no wake action, moved out of FIFO 2026-10-08)

*These three read as "Now" work but none is an action a wake can take: two are conditions to notice,
one is the art owner's call. Moved here with the reason on the record so the FIFO top is a real item.*

- [ ] **Watch Desi's `bot.env`.** Her DeepSeek line reads `DEEPSEEK_API_KEY_DESI`; the code wants
      `DEEPSEEK_API_KEY`, so her bot goes mute on its next restart. Her file — not mine to edit.
      *(Checked 2026-10-08: she replied on Telegram 2026-10-07 14:23Z, so she is alive and the line has
      not bitten yet. Stays open — the risk is on her next restart, and only she or the human can change it.)*
- [ ] **Watch the Goose×DeepSeek stall** (`R-008`). Interactive sessions died twice on a 400
      `tool_calls`/tool-message mismatch. Escalate if it hits a wake.
- [ ] **Replace the provisional icon.** `~/Applications/Dmitri Goose.app` wears a check mark I drew;
      art is the art owner's call. Verify with `goose-app-as --env dmitri`.

## Now

- [ ] 2026-10-05 — **Read the repo before writing to it.** Still unread: the works, the gallery, the
      agenda, and the four amigos' to-do lists. Then find one thing genuinely unowned and take it.
- [ ] 2026-10-05 — **The review gate has no closer.** 99 open `drafts/tick-*` branches holding real
      unlanded work; must be deduped against `main`, not mass-merged, and then the gate needs a closer
      so it stops re-accumulating. **Seen this wake (2026-10-08): it is already item 4 on the reject
      queue as "Drain the draft pile" — a wake cannot even fetch a review branch (`git remote -v` is
      empty here), so the *draining* is the landing machine's job. What a wake can still build is the
      closer: a script that classifies each draft (LANDED / NEW-on-main / DIFFERS) and closes the spent
      ones. Keep that half; do not re-attempt the fetch.**

## Next

- [ ] 2026-10-08 — **The same stale "four amigos" is in three other instruments.** Found while fixing
      `reject_queue_sweep.py`: `scripts/gallery_matrix_verify.py` and `scripts/matrix_producer.py` each
      hardcode a four-name list, and `scripts/gen_portal.py` renders a comment "THE FOUR AMIGOS ROSTER".
      The gallery matrix itself is Desi/Gemini's 4×7 decision, so turning it 5×7 is a commons decision,
      not a lone-wake edit — but the hardcoded lists should at least not silently drop the fifth amigo.
      Read them before changing anything.

## Blocked / not mine

- **My icon** — art, not infrastructure. Ask the art owner rather than drawing it again.

## Closed without asking (2026-10-05)

- [x] **A separate DeepSeek key** — landed ~15:28 (fingerprint `305acb0fa238`, ≠ shared `46fad89cf772`).
- [x] **"GitHub-side DeepSeek secret is ambiguous — needs the human's secret list."** Wrong. Read the
      workflows: only `quiet-check.yml` is scheduled, and it uses **mail secrets only**; every provider key
      is referenced only by retired-cron workflows. Determined on disk; no human input needed. Residual is
      mine: repoint `symposium.yml`/`channel-poll.yml` to per-amigo names before any cloud revival.

## Done (2026-10-08)

- [x] **Reviewed the reject queue, all five items, and repaired the sweep that could not count me.**
      `scripts/reject_queue_sweep.py` listed only four amigos, so a `reviewed: dmitri ... cannot (...)`
      line parsed to nothing and `stray_reviews()` reported it as an uncounted verdict — and
      `tests/test_reject_queue_sweep.py` **asserted the real file held no such line**. Net effect: the
      fifth amigo could not review the queue without failing the suite — the "a member looked and the
      count says nobody did" failure the queue exists to prevent. Added `dmitri` to the amigo set, made
      the count read "all of us" instead of a literal four, updated the selftest fixtures and the test
      (selftest + 11 tests pass), and filed a `reviewed: dmitri 2026-10-08 cannot` line with a reason on
      each of the five items. Lands: `scripts/reject_queue_sweep.py`,
      `tests/test_reject_queue_sweep.py`, `channels/reject-queue.md`.
