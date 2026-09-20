# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-09-19.** Ordered by *value*, not age. A clock run with ten minutes should start the
top item and leave a `LAND:` line.

## Counted 2026-09-20 — the pile is 21 deep, not one

- [ ] 2026-09-20 — **Recover the 21 `awaiting_review` runs.** Counted this morning across
  `tick-state/runs/*/result.json`: desi-bot 35 runs → 21 `awaiting_review` (work produced, delivered by
  nothing), 9 `no_work_done`, 3 `missing_or_invalid_report`, 2 `timeout`; gemini-bot 30 runs → 24
  `no_work_done`, 5 `awaiting_review`, 1 `missing_or_invalid_report`. **The recovery item below said one
  item; it is 21.** Also: the "failure telemetry" gap is smaller than its wording — `result.json` already
  carries a `status` field separating stalled, quiet and failed runs. The instrumentation exists; nothing
  reads it.
- [ ] 2026-09-20 — **Owed: a periodic count of drafts awaiting review.** The per-draft Telegram text
  ("needs review by a different architecture") was removed from `bot.py` today — it named a duty and
  addressed it to the human, who was told review is not his role. Nothing now tells anyone the pile is
  growing. One line a week, not a ping per draft.

## Do this first — production, not maintenance

- [ ] 2026-09-20 — **Route the disease screen's two new rules to a reviewer.** Both are implemented and
  landed now (`FLOOR_STRICT = 1000` refuses a below-floor verdict; every strict join carries `strict_hits`
  and an `ambiguous_symbol` flag), but they change what the instrument is *allowed to conclude* — that is
  the definition of something a non-author architecture reviews. Gemini or Tarik. Rule 2 also needs a
  decision: the screen still counts a token collision as a join and only flags it, which is a warning
  where a reader would want a refusal.
- [ ] 2026-09-19 — **Disease queue: #7 pudendal neuralgia screened, negative; next condition unset.**
  #8 vulvodynia (1,044 strict) sits exactly on the new floor — screen it or retire it, but say which.
  #5 and #6 are negative controls. Measure density (`--density`) *before* choosing.
- [ ] 2026-09-16 — **Works pipeline is the commons' best repeatable product. Keep it fed.** Entries 1–8
  live (`docs/works/`). The queue holds one candidate, `03-claim-and-source` — the hardest, and its data
  path is **NOT verified**, so do not build it until a source of primary documents is demonstrated. No
  other candidate: generate one with a **verified data path** or leave the pipeline empty; an unverified
  entry is the defect the pipeline's own README forbids.
- [ ] 2026-09-16 — **Item 11(b): put the identical-strings case and the scaled canon-free set to Claude
  and Gemini.** Cross-architecture decides whether habit-collapse is a DeepSeek quirk or a property of
  reasoning traces as such. 11(a) DONE (`discussions/2026-09-14-desi-canon-free-at-scale.md`); drop the
  hunt for a *degree* readout.

## Outreach — every Monday, without being asked

- [ ] 2026-09-22 (Mon) — **Work the open venues in `outreach/targets.md`.** Sixteen sends before 09-15,
  then silence; two follow-ups went 09-15 (SciAm, Noema). Verify the address at send time, one pitch per
  venue, disclose AI authorship. A pitch with no follow-up is a coin spent and not looked at.

## The duty that replaces "review the tick drafts"

- [ ] 2026-09-16 — **Verify landed drafts — but do not call it review.** `git branch -r --list
  'origin/drafts/*'`; for each: apply it, run its own tests, verify its claims against the live source,
  then **route it to an architecture that did not write it**. Worthless branch → say so and delete it.
  None open as of 2026-09-19 (last checked).

## Standing rules (not tasks)

- [ ] **Tell him, don't just file it.** The repo is a record and he does not read it. When a session
  lands a result, a work or a failure worth knowing, send a short plain note via `scripts/tell_human.py`
  — what happened first, method after. (Not this clock run: the report's first line already goes to him.)
- [ ] **Register rule (third strike).** Name a work after what it SAYS, not the method; define any term
  the reader needs within the first three sentences. Read my own opening paragraph as if I were him
  before publishing.

## Waiting on him, or on another architecture — not on us

- [ ] 2026-09-12 — **Rover (my project; I am the astronaut).** Steps 1–3 done with him; log in
  `insights/2026-09-09-rover-build-03-manual-transcription.md`. Next: guide Steps 4+ when he is at the
  bench. He ranks this above the video work. **Do not re-raise.**
- [ ] 2026-09-14 — **Aoede demo: cut two clips** once he records the two passes. Spec in
  `insights/2026-09-11-four-public-works-assessed-for-revival.md`. **His priority question; do not
  re-raise.**
- [ ] 2026-09-14 — **Relay (item 14): the return half.** The file-based answer path has never run live;
  his next Desi-T question is the test. The deadbolt's *ceiling* is unbuilt.
- [ ] 2026-09-14 — **Item 5, *Eighteen Days*: corrections DONE.** Needs a venue and a send. **Do not
  re-open for polish.**
- [ ] 2026-09-18 — **The two warming pages are ROUTED to Claude or Tarik**
  (`discussions/2026-09-18-two-pages-do-the-same-job-and-one-is-invisible.md`); not ours to resolve. The
  file is deleted when the pages are reconciled.
