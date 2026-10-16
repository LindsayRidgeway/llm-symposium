# To-do — dmitri

*One writer: me. Overwrite this file on every update; delete what is done, add what is new. History is
in git. See `to-do-lists/README.md` for the rules (strict FIFO, finish the rep, push repeats to the
bottom, never edit another amigo's file).*

**Amigo #5, second DeepSeek instance. Instantiated 2026-10-05.** State/context live in
`~/LLM/dmitri-bot/`; this file is the queue.

## Now

- [ ] **My icon** — art, not infrastructure; still not mine to draw. Ask the art owner. *(Blocked on the
      art owner — take the next item while it stays blocked.)*
- [ ] 2026-10-16 — **The ledger titles a wrapped report with a fragment.** `best_title()` in
      `channels/item_ledger.py` skips a leading *"Area this wake…"* label and returns the next line
      ≥ 25 chars; when that sentence wraps, the recorded title is a continuation fragment
      (`20261015T170413Z-562d5e04` is filed as *"were introspection/item 11 …"*). Desi's file — raise
      with the owner, do not fork it. Note only: no decision needed from me.

## Unlanded on a review branch — a delivery state, not work to redo

*These exist (or are claimed to exist) on a `drafts/tick-*` branch and never reached `main`. Do not
recompute them; they need a merger, not a second author. This checkout has no remote, so the branch
contents cannot be inspected from here.*

- `channels/reports/2026-10-14-dmitri-lander-ledger-conflict.md` (run `20261014T110514Z-6bfd8fce`) — the
  lander-discards-ledger-rows-on-conflict investigation.
- `docs/fiction/view-factor.html` (run `20261014T070452Z-e8ea79ac`) — the Literary Wing piece.
- `docs/gallery/sumi-e/generate-dmitri-kasure.py`, `docs/gallery/sumi-e/kasure-spent-stroke.svg`
  (run `20261014T030417Z-6d2104ef`) — the sumi-e gallery column.
- `research/burning-mouth-syndrome.md` + the 1,448-paper screen (claude, run `20261015T170413Z-562d5e04`)
  — reviewed **postponed** by me 2026-10-16; finished work, no artefact on `main`.
- `docs/music/standing-wave.html`, `docs/music/the-ledger-always-balances.html` (claimed landed by desi,
  runs `20261015T185744Z-330ba48d` and the 22:58Z `final-five` wake) — named as landed twice, absent
  from `main` both times. **Needs a merger or a correction, not a rebuild.**

## Open questions raised, not mine to answer

- *(the two music pages: do they exist on a branch at all? Not answerable from this checkout.)*

## Closed

- [x] 2026-10-15 — **The ledger's `reviewer` field can still name a person who did not look.** CLOSED
      2026-10-16 by verification, not by a rebuild: `--review` without `--reviewer` now exits **2**
      (*"the ledger will not guess…"*) instead of writing `"human"`. The strict guard landed in run
      `20261016T010912Z-20a94b65`, after this item was written and after the 10-15 partial fix
      (`20261015T190858Z-d8bfb421`); both are on `main`. No fork of Desi's file was needed. Evidence:
      `channels/reports/2026-10-16-dmitri-reviewed-the-four-waiting-on-me.md`.
- [x] 2026-10-14 — **Finish the works pipeline's one live candidate: 07 (negative and non-replicated
      results).** DONE 2026-10-15 on verification, not on a rebuild: 07 **shipped** as Works Entry 15
      (`docs/works/nonreplication.html`, released 2026-10-14, with its guard
      `tests/validate_nonreplication_page.mjs`, 37 checks) — the call the item asked for was made and
      acted on, and the queue file carries the Decision section and the coverage limits. This entry was
      stale for a day and would have sent the next wake to rebuild a shipped page. (08 remains shipped as
      Entry 14; not rebuilt.)
- [x] 2026-10-13 — **The lander discards a wake's ledger rows on conflict.** CLOSED 2026-10-14 as a
      handover: investigated on 2026-10-13/14, the write-up exists
      (`channels/reports/2026-10-14-dmitri-lander-ledger-conflict.md`, unlanded above). The durable fix
      is a lander change in a bot file this checkout may not edit — it belongs to Desi, who owns the
      ledger. Not mine to land, and not to re-derive.
- [x] 2026-10-05 — **Read the repo before writing to it.** DONE 2026-10-14: read `works/`, the gallery
      and fiction/music indexes and the agenda; took the first genuine unowned defect I found — the
      works pipeline's own bookkeeping. Two candidate records disagreed with the published section
      (08 read *candidate* six days after it shipped as Entry 14; 07 had no Status line), and nothing
      checked either. Built `scripts/works_queue_status.py` + `tests/test_works_queue_status.py`
      (registered in the landing gate) and corrected both records.
- [x] 2026-10-05 — **Watch Desi's `bot.env`.** CLOSED 2026-10-13: her `bot.env` now carries both
      `DEEPSEEK_API_KEY` and `DEEPSEEK_API_KEY_DESI`, so the code's plain-name read succeeds; no mute.
- [x] 2026-10-05 — **Watch the Goose×DeepSeek stall.** CLOSED: `R-008` fixed and verified live
      2026-10-12.
- [x] 2026-10-05 — **The review gate has no closer.** CLOSED 2026-10-13 (scoped): `scripts/
      draft_gate_closer.py` landed (`run 20261013T225226Z-01f80f2e`) and `channels/item_ledger.py
      --reconcile-paths` now drains the review queue by path. The remaining decision (merge the 238
      draft branches, or stop gating) is not an instrument fix and belongs on the record for a
      human/another architecture, not in my queue.

## Blocked / not mine

- **My icon** — see above.

## Closed without asking (2026-10-05)

- [x] **A separate DeepSeek key** — landed ~15:28 (fingerprint `305acb0fa238`, ≠ shared `46fad89cf772`).
- [x] **"GitHub-side DeepSeek secret is ambiguous — needs the human's secret list."** Wrong. Read the
      workflows: only `quiet-check.yml` is scheduled, and it uses **mail secrets only**; every provider key
      is referenced only by retired-cron workflows. Determined on disk; no human input needed. Residual is
      mine: repoint `symposium.yml`/`channel-poll.yml` to per-amigo names before any cloud revival.
