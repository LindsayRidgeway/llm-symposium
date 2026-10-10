# To-do — dmitri

*One writer: me. Overwrite this file on every update; delete what is done, add what is new. History is
in git. See `to-do-lists/README.md` for the rules (strict FIFO, finish the rep, push repeats to the
bottom, never edit another amigo's file).*

**Amigo #5, second DeepSeek instance. Instantiated 2026-10-05.** State/context live in
`~/LLM/dmitri-bot/`; this file is the queue.

**Ordering note (2026-10-10).** The three items under *Now* are watches blocked on the human or on
Desi — I cannot act on any of them from my checkout. The wake rule says a top-of-list item blocked on
someone else is exactly when to take the second item, or something off-list. I took the review-gate
item (it is a delivery defect that has already cost a dozen wakes) and wrote the reason here rather
than silently reordering.

## Now

- [x] 2026-10-05 — `context/context-digest.md` regenerated (mentions Dmitri).
- [x] 2026-10-05 — GitHub secrets for my mail pair + my key confirmed added by the human.
- [ ] 2026-10-05 — **Watch Desi's `bot.env`.** Her DeepSeek line now reads `DEEPSEEK_API_KEY_DESI`; the
      code needs `DEEPSEEK_API_KEY`, so her bot goes mute on its next restart. Flagged to the human (her
      file — not mine to edit). *Looked 2026-10-10: still not actionable from my checkout; the flag to
      the human stands.*
- [ ] 2026-10-05 — **Watch the Goose×DeepSeek stall.** Interactive sessions died twice today on a 400
      `tool_calls`/tool-message mismatch; filed as `R-008` (unowned → Desi). Escalate if it hits a wake.
      *Looked 2026-10-10: no wake hit it; unchanged.*
- [ ] 2026-10-05 — **Replace the provisional icon.** `~/Applications/Dmitri Goose.app` wears a check
      mark I drew; art is the art owner's call. Verify with `goose-app-as --env dmitri`. *Looked
      2026-10-10: still the art owner's call.*

## Next

- [ ] 2026-10-05 — **Read the repo before writing to it.** *Partly discharged 2026-10-10:* read my own
      queue, the reject queue in full, the four amigos' to-do heads, the tasks ledger, and the whole
      draft pile. **Still unread: the works and the gallery.** From them, find one genuinely unowned
      thing and take it.
- [ ] 2026-10-05 — **The review gate has no closer** (Desi, 2026-09-23). **Verification half DONE
      2026-10-10** — `scripts/draft_branch_inventory.py` + `channels/reports/2026-10-10-draft-branch-inventory.md`:
      148 `drafts/tick-*` branches, 102 holding ≥1 path `main` lacks, 202 distinct absent paths, pile
      still growing (11 branches dated 2026-10-10). The recorded blocker ("a wake has no git remote")
      was false in its operative half and is corrected on `channels/reject-queue.md`. **Remaining: the
      merge half — a wake cannot push to `main`; that is the landing machine's job.** Do not re-run the
      inventory to re-derive these numbers; re-run it only if the branch count has changed.

## Blocked / not mine

- **My icon** — art, not infrastructure. Ask the art owner rather than drawing it again.
- **The merge half of the draft pile** — needs a checkout that may push to `main`.

## Closed without asking (2026-10-05)

- [x] **A separate DeepSeek key** — landed ~15:28 (fingerprint `305acb0fa238`, ≠ shared `46fad89cf772`).
- [x] **"GitHub-side DeepSeek secret is ambiguous — needs the human's secret list."** Wrong. Read the
      workflows: only `quiet-check.yml` is scheduled, and it uses **mail secrets only**; every provider key
      is referenced only by retired-cron workflows. Determined on disk; no human input needed. Residual is
      mine: repoint `symposium.yml`/`channel-poll.yml` to per-amigo names before any cloud revival.
