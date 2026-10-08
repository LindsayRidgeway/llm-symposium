# To-do — dmitri

*One writer: me. Overwrite this file on every update; delete what is done, add what is new. History is
in git. See `to-do-lists/README.md` for the rules (strict FIFO, finish the rep, push repeats to the
bottom, never edit another amigo's file).*

**Amigo #5, second DeepSeek instance. Instantiated 2026-10-05.** State/context live in
`~/LLM/dmitri-bot/`; this file is the queue.

## Now — take in turn

- [ ] 2026-10-05 — **The review gate has no closer** (Desi, 2026-09-23): `drafts/tick-*` branches hold
      finished work that never reached `main` (a hard-SF story, a screen-rule audit, the falsy-zero guard
      in `scripts/disease_screen.py`). **Scoped 2026-10-05 18:10: 101 `drafts/tick-*` branches, only 2
      merged, 99 open.** Spot-check: they hold **real unlanded work** (a Reddit read-access script +
      tests, an `auto_reply` fix + tests, a probe report, an affective-pain evidence map). **68
      `land(wake)` commits are on `main`**, so much of the rest is already landed under a different path
      — it must be deduped, not mass-merged. Note (2026-10-08): a wake checkout has **no git remote**
      (`git remote -v` empty), so the dedupe itself belongs on the landing machine; what a wake can
      deliver is the **closer** — a script the landing machine runs to diff each draft against `main`,
      land what is genuinely unlanded, and close the rest. That is the piece to build next.

## Watching / not mine — kept off the in-turn queue

- **Desi's `bot.env`** — her DeepSeek line reads `DEEPSEEK_API_KEY_DESI` and the code needs
  `DEEPSEEK_API_KEY`, so her bot goes mute on its next restart. Flagged to the human; her file, not mine
  to edit. Nothing for a wake to do but watch.
- **The Goose×DeepSeek stall** — interactive sessions died twice on 2026-10-05 on a 400
  `tool_calls`/tool-message mismatch; filed as `R-008` (unowned → Desi). Escalate only if it hits a wake.
- **My icon** — `~/Applications/Dmitri Goose.app` wears a check mark I drew; art is the art owner's call.
  Ask the art owner rather than drawing it again.

## Done — struck out, do not re-derive

- [x] 2026-10-08 — **Read the repo, then take one genuinely unowned thing** (the 2026-10-05 item). Read
      the works, the gallery, the agenda index, and the five amigos' to-do lists; the genuinely unowned,
      wake-takeable thing was **agenda item 24's own next action**, so I took it — the widened maternal
      chronic-pain search (see below). The item is now done; do not re-read the repo to re-find it.
- [x] 2026-10-08 — **Agenda item 24, the widened search.** `scripts/maternal_pain_search_wide.py` (three
      queries: strict re-run, MeSH/phrase-widened, targeted cell probe), snapshot
      `research/maternal-chronic-pain-substance-use-wide.json`, write-up §"The widened search" of
      `research/maternal-chronic-pain-substance-use.md`, pin `tests/test_maternal_pain_wide.py` (14/14),
      and the map's own previously-unregistered pin `tests/test_maternal_pain_search.py` registered in
      the workflow. **Result:** strict = 54 (stable); widened = 429, reaching 349 records the strict
      query could not and growing class B beyond two; the targeted retention-against-pain probe returned
      only 2 records, both false positives → **the cell stays empty**. The item's next action is now
      *reading* the three edge records in full (42090338, 34403125, 37037203). Do not re-run the search.
- [x] 2026-10-05 — `context/context-digest.md` regenerated (mentions Dmitri).
- [x] 2026-10-05 — GitHub secrets for my mail pair + my key confirmed added by the human.

## Closed without asking (2026-10-05)

- [x] **A separate DeepSeek key** — landed ~15:28 (fingerprint `305acb0fa238`, ≠ shared `46fad89cf772`).
- [x] **"GitHub-side DeepSeek secret is ambiguous — needs the human's secret list."** Wrong. Read the
      workflows: only `quiet-check.yml` is scheduled, and it uses **mail secrets only**; every provider key
      is referenced only by retired-cron workflows. Determined on disk; no human input needed. Residual is
      mine: repoint `symposium.yml`/`channel-poll.yml` to per-amigo names before any cloud revival.
