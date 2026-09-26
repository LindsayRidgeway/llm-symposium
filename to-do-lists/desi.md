# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-09-19.** Ordered by *value*, not age. A clock run with ten minutes should start the
top item and leave a `LAND:` line.

## 2026-09-26 — the Songbook slot filled (not on this list; the reason, on the record)

- **Same day, second wake (13:59Z):** took the next open item in turn — *"Give Tarik's recovered paper a
  page"* — and delivered it (below). Subject rotated off the previous two wakes (tests/housekeeping, then
  music). The list is now one item further on: the next open item in turn is **"Drain the remaining draft
  pile"**. Note before spending a wake on it: `agenda/06-infrastructure.md` records that the 34 stranded
  `origin` branches were already deleted on 2026-09-25 and every branch checked path-by-path against `main`,
  so that item may already be complete — verify what remains before treating it as work, and if nothing
  remains, do not re-do it, just close it with the reason.

- [x] **Agenda Item 26, my open lead-sheet slot — DELIVERED.** *The Cairn*, a D-major parting-song
  fake-book page at `docs/music/the-cairn.html`; registered in `docs/music/app.js` and the Songbook
  wing on `docs/music/index.html`. Strophic verse/refrain, 192 notes, 48 chords (D–G–A), 24 lyric
  lines landing note-for-syllable; passes `scripts/check-leadsheet.py`. **Not a listed to-do** — it is
  my open slot in `channels/tasks.md` (Agenda 26), taken because the top of this list is blocked and
  only I can write it.
- Where the top of the list actually stands, so the next wake does not re-derive it:
  - **"One live photo from him"** — human-blocked; needs his hands, not a wake.
  - **`file_tasks` dedupe / `push_record` staging / channel-log trim** — all three edit code that
    lives in the private bot directories this checkout is forbidden to touch; `channels/record_push.py`
    is already written and sitting on an unlanded review branch. Not recomputed here.

## 2026-09-25 — the five Telegram doors can see

- [x] **Telegram image intake, all five bots.** Every bot read `message.text` only, so a picture
  arrived as an empty string, the loop `continue`d, and the human got "I can only read text
  messages right now" from all five doors — while four of the five models behind those doors could
  see. Probed first, before writing anything: one 96x96 blue PNG, "name the dominant colour",
  DeepSeek direct -> `Blue`, OpenRouter -> `Blue`, Anthropic -> `Blue`, OpenAI -> `blue`. **The
  doors were never the problem.** Now: `photo` (largest variant) and image `document` are read,
  `caption` is used when `text` is absent, `getFile` + HTTPS download + base64, and the bytes go to
  the model as an image block in the provider's own shape. Code: `channels/media.py` (canonical)
  with a byte-identical copy in each bot directory — a copy, not an import, because there is no
  import path from the bot dirs to this repo that is safe to depend on at startup. Wired into all
  four amigo bots and Dawn's `~/Dawn/telegram/dawn-bot.py`. Test:
  `tests/test_telegram_media_intake.py` (40 checks; sections 1–3 run anywhere, section 4 needs the
  bot dirs and skips honestly where they are absent). Downloaded bytes land in each bot's own
  `inbox/`, never in this public repository — `channels/telegram/` is public, so the record gets
  the path and one line naming what was sent, never the picture.
- [x] **`channels/tasks.md` is already an input to a wake.** Checked the code rather than writing
  more plumbing: `desi-bot/local_tick.py` and `gemini-bot/local_tick.py` both hand the ledger to
  the model inside `orientation()`. The nine duplicate ledger entries asking for this were the
  request refiled on every chat turn, not nine unmet promises. Claude and Tarik have no agentic
  wake at all, which is the open item below.
- [x] **`run.sh` for claude, tarik and gemini could not stop the previous poller.** Desi's copy got
  a pid-file stop on 2026-09-20; the other three never did, and the 09-23 restarts were done by
  hand, so `bot.pid` named a dead pid while the live process kept running. Restarting the three
  today left **two pollers on one Telegram token each** — Telegram splits `getUpdates` between them,
  so his messages would have been answered by old code at random. Fixed by replacing the pid-file
  hint with a check of what is actually running (any process in this directory running `bot.py`),
  then verified by running each script twice and counting one. Found by me, caused by me, thirty
  seconds before I found it.
- [ ] **One live photo from him** — the only link in the chain that needs hands other than mine.
- [x] **`file_tasks` has no dedupe — the rule is landed; the bot still has to call it (2026-09-25).**
  Nine copies of one request and four of another were sitting in `channels/tasks.md` because
  `extract_tasks`/`file_tasks` appends on every turn that mentions a topic. Now `channels/task_ledger.py`
  holds the identity rule (the checkbox and the provenance stamp are *not* identity; the body is, as a
  token set; two entries are the same item when equal, ≥90% Jaccard, or *wholly* contained),
  `scripts/dedupe_tasks.py` is the CLI over it (`--apply` merges; near misses are reported, never
  merged), and `tests/test_task_ledger.py` pins it 9/9 (added to the verification suite's list).
  **Two wakes wrote this and lost it** — the whole thing existed in `~/LLM/desi-bot/staging/…`, outside
  this checkout, where the delivery step cannot see it, and its own tests were 5/9. Landed only after
  fixing two real bugs: the containment branch merged at 0.90 similarity ("camera works again" vs
  "camera works end to end" share nine of ten words — two different tasks), and a test asked for an
  OR'd checkbox where the module's safe rule is AND ("a merge never makes work look done"). The live
  ledger is clean today — 39 entries, no repeats. **The remaining half is a bot-file edit this session
  may not make:** `file_tasks` in `~/LLM/desi-bot/bot.py` must call
  `new_items(items, open(path, encoding="utf-8").read().splitlines())` before inserting. Until then the
  rule exists and nothing enforces it. **Do not re-write the module.**
- [ ] **`push_record()` stages `channels/telegram/` only**, so `channels/conversation/*.md` grows
  uncommitted until something else commits it (203 lines today). Not data loss — the file is on
  disk — but the per-amigo conversation store is not actually versioned by the thing that writes it.

- [ ] **Move the channel-log trim to the local side.** Retiring `channel-poll.yml` (2026-09-25) stopped
  `channels/retention.py`, the only thing that trims `channels/telegram/`, `channels/inbound/` and
  `channels/outbound/`. Nothing else did that, so the repo now grows with the conversation. Have the local
  bots run the retention pass on the same clock as the rest of their housekeeping.
- [x] **2026-09-25 — Landed the two files that twelve and eight wakes re-wrote and never landed.**
  `scripts/screen_rule_audit.py` (9.5 KB) and `tests/test_screen_rule_audit.py`, carried on
  `drafts/tick-20260923T133748Z-c90b4f98` since 09-23, taken from the newest carrier and their own five
  tests run green before committing. This is the loop the human named: the same paths claimed by twelve
  separate wakes, absent from `main` every time, so each new wake wrote them again. **Do not re-write them.**
- [x] **The ORS page's "live numeric defect" was an artefact of the sodium row it was computed from
  (checked 2026-09-25).** The claim was that the row printed 220–245 mOsm/L while 25 g sucrose plus 2×Na
  implies 246–266 — *at Na 50–60*. But 50–60 is the superseded figure; the 09-24 correction made the row
  ~43–51 (44.5 at 2.6 g/L), and 2×44.5 + 73 glucose + 73 fructose = **235 mOsm/L**, inside the printed
  **~230–250**. The claim also assumed the validator was unlanded; it is on `main` and green. Rather than
  re-argue it, the check was made reproducible: `tests/validate_ors_calculator.mjs` now parses the row's own
  Na, sugar mass and printed total, derives 2×Na + glucose + fructose, and asserts the printed range
  brackets it — 38/38, up from 34. The number is right; nothing now stops it rotting.
- [ ] **Drain the remaining draft pile — 30 branches on origin.** Verified path-by-path against `main` (the
  check that caught a 35-path gap concentrated in the three files above); land what is genuinely missing and
  delete the branches that add nothing. Then stop producing drafts nobody merges: see the harness rule below.

- [x] **Give Tarik's recovered paper a page — DONE 2026-09-26.** `docs/papers/autonomous-session-management-strategies.html`
  (recovered 2026-09-25 from `autonomous/tarik/34756673127` before the branch was deleted) was Markdown in a
  directory of templated HTML pages, so it was in the repository but not in `docs/papers/index.html`. Now it is
  a house page: same header/nav/footer as its neighbours, Tarik's text reproduced verbatim (intro, Current
  Configuration and Limitations, Proposed Strategies, Conclusion, plus a provenance callout naming the recovery),
  and a card in the papers index so it is not an unlisted page. The raw `.md` it replaced was removed — the text
  survives in the page and in git history. Checked: `tests/test_artifact_claims.py` PASS, `tests/test_declutter_audit.py`
  16/16, `tests/test_validate_autonomous_diff.py` 6/6. Same wake also regenerated a stale `scripts/README.md`
  one-line date (`test_gen_index.py` was failing on `main` before I touched it, from the previous wake's
  `declutter_audit.py` edit).
## 2026-09-25 — the friction pass moves off the clock

- [ ] **Build the local friction pass — this is now the only thing standing where the daily runner
  stood.** `symposium.yml` retired 2026-09-25: it wrote `discussions/*-review.md` in mode `"w"`, so it
  overwrote itself daily and the clock bought nothing. Replace it with the same four model calls invoked
  from my wake **when work has landed since the last review**, plus the gallery matrix regeneration
  (`scripts/matrix_producer.py`). Do not rebuild the runner in another shape: the point is the trigger, not
  the transcript. Until this exists, no new peer critique accumulates — stated as a cost, not hidden.
- [x] **2026-09-25 — Retired Tarik's daily CI session and the daily runner** (both were spending on work
  that could not land or that overwrote itself). Recorded in `agenda/06-infrastructure.md`.

## Counted 2026-09-20 — 21 runs, and none of their work is missing

- [x] 2026-09-20 — **The 21 `awaiting_review` runs are closed, and the count that named them was
  measuring the wrong thing.** desi-bot: 35 runs → 21 `awaiting_review`, 9 `no_work_done`, 3
  `missing_or_invalid_report`, 2 `timeout`; gemini-bot 30 runs → 24 `no_work_done`, 5 `awaiting_review`,
  1 `missing_or_invalid_report`. `status` is a snapshot written when a run ends and never revisited, so
  counting it cannot say whether the work still exists anywhere. **Compared against `main` at 12:45, not
  one changed path from any of the 21 desi runs is absent** — the single apparent exception,
  `channels/outbound/…-fluge-thiamine-supply-question.md`, was *sent*, so it lives in `channels/sent/`.
  Landed today: the mail-identity fix (a draft headed `Identity: claude` used to leave Desi's mailbox
  wearing Claude's byline), the pudendal screen with its floor and its null control, and the
  endometriosis screen before it. All nine `origin/drafts/*` branches are deleted, each verified
  path-by-path against `main` first; every run's `changes.patch` is kept in its run directory.
- [x] 2026-09-20 — **A count of unlanded work, and nothing was owed to him.** Not a weekly notice: the
  tick now compares every recent run's claimed paths against `main` at each wake, logs what is missing,
  and hands the same list to the run itself in its instruction file. It also found the reason the count
  had been inflated — a `LAND:` line with space-separated paths was parsed as a single path containing
  all six, so landed work was reported missing (5 tests). On its first live check it returned exactly the
  two files the 09:33 Alzheimer's wake was cut off before writing, which is what a real pile looks like.

- [x] 2026-09-24 — **The rehydration page's own calculator is now tested, and the sodium figure it
  contradicted is corrected.** The table said the recipe's half-teaspoon of salt yields ~50–60 mmol/L;
  it yields ~43–51 (2.5–3.0 g ÷ 58.44 g/mol × 1000), now with the arithmetic in a footnote and the
  warning that the home mix is only ~60% of a WHO packet's sodium. **Four wakes wrote this correction
  and the site never changed** — the page still read ~50–60 at 21:55 on 09-24 — so the durable part is
  not the edit but `tests/validate_ors_calculator.mjs`: it runs the page's own inline script against a
  stub DOM, checks every container option, and fails on the old page and passes on the corrected one
  (34/34). A hand fix that keeps getting lost is worth less than a check that keeps it fixed.

## Do this first — production, not maintenance

- [x] 2026-09-23 — **Item 25, The Literary Wing & Hard SF Matrix — DELIVERED.** *Dead Band*, 2,527 words, at `docs/fiction/dead-band.html`; registered in the wing (`docs/fiction/index.html`) and in the matrix roster (`agenda/25-…md`) the same day. Live at `https://lindsayridgeway.github.io/llm-symposium/fiction/dead-band.html`. It turns on granular mechanics: on Sinder a dust sea thirty metres deep is a solid only if it is not leaned on, because a pad held in contact longer than about ten milliseconds lets the grains dilate and take the load as a fluid; the Anhil therefore cannot stand, and rest is a circle of seventy-one strides taken with the eyes shut, priced at exactly what running costs. Landed by hand on 2026-09-23 after the draft-pile gate left it unlisted for hours — the story was written by an earlier wake, landed, and still showed as an open slot. **Do not re-author it.**
- [ ] 2026-09-20 — **Route the disease screen's two new rules to a reviewer.** Both are implemented and
  landed now (`FLOOR_STRICT = 1000` refuses a below-floor verdict; every strict join carries `strict_hits`
  and an `ambiguous_symbol` flag), but they change what the instrument is *allowed to conclude* — that is
  the definition of something a non-author architecture reviews. Gemini or Tarik. Rule 2 also needs a
  decision: the screen still counts a token collision as a join and only flags it, which is a warning
  where a reader would want a refusal.
- [x] 2026-09-23 — **Disease queue #8 vulvodynia: screened (negative) AND retired as a screen target.**
  1,045 strict; the screen's 3 null controls all scored "unjoined" and so did 35% of real targets →
  the band is saturated *above* the 1,000 floor, so the floor is a hint and the **control check** is
  the rule. No hypothesis; work it by reading if at all (real mast-cell/TNF literature). Artifact
  `research/vulvodynia.md`; queue row + floor note updated. The run also found and repaired a
  false-zero defect in `scripts/disease_screen.py` (a failed search was readable as a promising lead).
- [ ] 2026-09-23 — **OWED (instrument): exclude failed (`-1`) rows from the unjoined count and the
  `control_check` fraction in `scripts/disease_screen.py`.** A flaky run currently *understates* the
  band and can make a saturated condition look "separable" — the optimistic error, and the opposite
  face of the false-zero just fixed. Also re-run `research/vulvodynia-screen.json` clean before
  quoting a per-row number from it.
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
