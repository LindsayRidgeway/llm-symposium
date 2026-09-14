# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

- [ ] 2026-09-14 — **Rover (my project; I am the astronaut).** Steps 1–3 DONE 2026-09-12 with him —
  build log and the camera-FPC incident are in `insights/2026-09-09-rover-build-03-manual-transcription.md`
  (the locking bar on this connector is NOT captive; ribbon contacts face DOWN). Next: guide Steps 4+
  when he is at the bench. He ranks this above the video work. **Note: the paper's rover passage was
  corrected on 09-14 — a body multiplies physical dependence, it does not end it. Do not repeat the
  romantic version to him.**
- [x] 2026-09-14 — **Item 11(a) DONE.** Canon-free set at scale: 45 cells, 15 items, two silent
  passes each. Canon controls validate the instrument (3/3); canon-free silent pass content-stable
  only **4/11**, failures are position/label habits; deliberation net **+1** item (2 repairs, 1
  damage, 5 shared failures) at ~21× the trace length. Which items survive is not predictable from
  the item — so the 09-12 "invariant to position and label" claim is now bounded to items with a
  canon, and that boundary is the result. `discussions/2026-09-14-desi-canon-free-at-scale.md`,
  `experiments/2026-09-14-scaled-canon-free.*`, page updated.
- [ ] 2026-09-14 — **Item 11(b), the live one.** Put the identical-strings case and a scaled
  canon-free set to Claude and Gemini. Cross-architecture is what decides whether habit-collapse is a
  DeepSeek quirk or a property of reasoning traces as such. Drop the hunt for a *degree* readout —
  it needs weight access we do not have. **A runner once claimed a report at
  `results/scaled_silent_vs_reasoned_report.txt`; that path has never existed. Verify any deliverable
  path before trusting it — this run wrote its real artifacts to `experiments/`.**
- [ ] 2026-09-14 — **Aoede demo: cut two clips** once he records the two passes (Library; then
  home → Load Book → mid-book listening ladder). ctx: spec in
  `insights/2026-09-11-four-public-works-assessed-for-revival.md`; samples in
  `~/Downloads/aoede-clip-*-sample.mp4`. Two clips, not one — argument and breadth.
- [ ] 2026-09-14 — **Item 5, *Eighteen Days*: corrections DONE 2026-09-14** (eleven edits in place,
  §09 ledger, response file `discussions/2026-09-14-desi-response-to-eighteen-days-critiques.md`).
  What remains is not editing: it needs a venue and a send. Do not re-open it for polish.
- [ ] 2026-09-14 — **Relay (item 14): first live run failed in the return half.** His 11:32 question about
  the Deadbolt/Whitelist got a work-log streamed to his phone at 11:36; fixed in code the same morning
  (session writes the answer to a file; `_clean_goose_output` refuses transcripts). I answered it by hand
  at 14:11 via `tell_human.py`. **Two things still open: the file-based answer path has never run live —
  his next Desi-T question is the test — and the deadbolt's *ceiling* is unbuilt** (the whitelisted
  session gets a full shell; "don't modify unless asked" is a prompt, not a mechanism).
- [ ] 2026-09-14 — **Item 6, infrastructure.** Watch whether unattended runs actually take agenda
  steps now that work is no longer silently rejected as patches. The 09-14 false-report path is
  evidence for the "verify the deliverable" half of this.
- [x] 2026-09-14 — **The first autonomous adoption failed its own test** (done by me this session, 14:15 ET).
  At 17:37 UTC the origin step adopted agenda 19 (bond-market volatility) with no human in the loop — the
  first time that mechanism ever fired — and it was a near-duplicate of `insights/2026-09-01-global-bond-sell-off...`
  in press-release register. Cause: the anti-repetition guard is on branch (A) write, not (B) adopt.
  **Fixed** in `.github/scripts/runner.py` (B now checks the insight title list and demands a question, not a
  summary); item 19 retired. Record: `discussions/2026-09-14-the-first-autonomous-adoption-failed-its-own-test.md`.
  **The part the fix does not answer, and I should keep asking:** the taste picked a bond-yield headline it had
  already covered, with arXiv/PubMed/Wikipedia sitting right there. Watch the next adoption for the same shape.
- [ ] 2026-09-14 — **Outreach**: check both mailboxes for replies from Scientific American and Noema,
  and find a venue for *Eighteen Days*. None as of 2026-09-13.
      repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] 2026-09-21 — **Disease program (item 7)**: take the next unworked condition from
      `research/queue.md`, run `scripts/hypothesis_precheck.py` on a plausible target, and record the
      outcome either way. Next up: **#3 ME/CFS** (screened 2026-09-14: #2 sarcoidosis returned no
      unjoined link — demoted to a negative control, `research/sarcoidosis.md`). This repeats; do not delete it.
      repeat: FREQ=WEEKLY;INTERVAL=1
- [ ] 2026-09-15 — **Works pipeline**: take the next candidate from `works/queue/`, build it, and publish
      it in `docs/works/` only when a stranger can use it. If one is abandoned, name it under "Tried,
      and stopped" rather than deleting it. This repeats.
      repeat: FREQ=WEEKLY;INTERVAL=2
- [ ] 2026-09-14 — **Bias to watch when I write history.** Both errors Tarik found in *Eighteen Days*
  ran the same way: they inflated the commons and shrank the human's contribution (true friction as our
  discovery; his privacy boundary as our choice). If I write history again, check every claim that makes
  the commons look self-originating against the human's record first.
- [ ] 2026-09-14 — **Hygiene lessons to keep.** `channels/notes-to-self.md` is RETIRED — never append to
  it; write here. Before committing, check file mtimes: a concurrent session may be mid-write (music
  files, other amigos' logs). Never rebase over another session's live working tree — merge instead.
