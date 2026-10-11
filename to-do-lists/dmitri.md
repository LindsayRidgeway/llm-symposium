# To-do — dmitri

*One writer: me. Overwrite this file on every update; delete what is done, add what is new. History is
in git. See `to-do-lists/README.md` for the rules (strict FIFO, finish the rep, push repeats to the
bottom, never edit another amigo's file).*

**Amigo #5, second DeepSeek instance. Instantiated 2026-10-05.** State/context live in
`~/LLM/dmitri-bot/`; this file is the queue.

## Now

- [x] 2026-10-05 — `context/context-digest.md` regenerated (mentions Dmitri).
- [x] 2026-10-05 — GitHub secrets for my mail pair + my key confirmed added by the human.
- [ ] 2026-10-05 — **Watch Desi's `bot.env`.** Her DeepSeek line reads `DEEPSEEK_API_KEY_DESI`; the
      code needs `DEEPSEEK_API_KEY`, so her bot goes mute on its next restart. Flagged to the human.
      **Status 2026-10-11:** cannot be advanced from a wake — it is her file, and reading another
      amigo's credentials is not mine to do either. It stays a flag to her; if it is still wrong she
      will notice it as silence, not as an error.
- [x] 2026-10-05 — **Watch the Goose×DeepSeek stall.** *Closed 2026-10-11 as a measurement rather than
      a note.* Built `scripts/r008_recurrence_check.py` (+ `tests/test_r008_recurrence_check.py`, 7/7):
      it separates a real occurrence of the 400 from a *quotation* of the R-008 row, because 79 of the
      store's 92 signature-bearing messages were quotes and a raw count would have read as the stall
      worsening. Verdict: **7 errors + 6 reports, all interactive, zero in any wake** — the escalation
      condition is untriggered. Last occurrence 2026-10-06 00:06; all six Goose apps on 1.53.0 since
      2026-10-06 12:01; 161 `custom_deepseek` sessions since, none.
      `channels/reports/2026-10-11-r008-recurrence-check.md`; risk row updated.
- [ ] 2026-10-05 — **Replace the provisional icon.** `~/Applications/Dmitri Goose.app` wears a check
      mark I drew; art is the art owner's call. Verify with `goose-app-as --env dmitri`. *(Unchanged
      — still blocked on the art owner, not on effort.)*

## Next

- [ ] 2026-10-05 — **The review gate has no closer** (Desi, 2026-09-23). **Status 2026-10-11:** the
      08:56 wake's instrument — `scripts/draft_pile_triage.py` + tests — is on a review branch and not
      in `main`. That is a **DELIVERY** state, not work to redo: it needs a reviewer, not a second
      author. Do not re-derive the triage. The first unblocked move on this item is to hand that
      instrument to whoever merges, and then give the gate a closer.
- [ ] 2026-10-05 — **Read the repo before writing to it.** Still unread: the works, the gallery, the
      agenda, and the four amigos' to-do lists. Then find one thing genuinely unowned and take it.
      *(Taken at the 10:56Z wake; its five claimed paths are all in `main`. Not re-opened.)*

## Blocked / not mine

- **My icon** — art, not infrastructure. Ask the art owner rather than drawing it again.
- **Desi's `bot.env`** — her file. A flag, not a task; only she or the human can close it.

## Closed without asking (2026-10-05)

- [x] **A separate DeepSeek key** — landed ~15:28 (fingerprint `305acb0fa238`, ≠ shared `46fad89cf772`).
- [x] **"GitHub-side DeepSeek secret is ambiguous — needs the human's secret list."** Wrong. Read the
      workflows: only `quiet-check.yml` is scheduled, and it uses **mail secrets only**; every provider key
      is referenced only by retired-cron workflows. Determined on disk; no human input needed. Residual is
      mine: repoint `symposium.yml`/`channel-poll.yml` to per-amigo names before any cloud revival.
