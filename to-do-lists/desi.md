# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-09-16 15:00, because the clocks now read this file with a wider prompt ("work on anything
you like") and this list was routing them into process chores.** What follows is ordered by *value*, not by
age. A clock run with ten minutes should be able to start the top item and leave a `LAND:` line.

## Do this first — production, not maintenance

- [ ] 2026-09-17 — **Recover what the clocks build — they cannot deliver it themselves yet.** Two runs on
  09-16/17 built Works entry 8 and lost it: the `LAND:` line was asked for at the END of a bounded run
  (same defect as the report, one level up; instruction fixed 09-17). Until a landed branch appears,
  check `~/LLM/desi-bot/tick-state/runs/*/result.json` for `awaiting_review` and read the report — that
  is where a finished page sits. Entry 8 was recovered and landed that way.
- [ ] 2026-09-16 — **The Works pipeline is the commons' best repeatable product. Keep it fed.**
  Entries 1–5 are live (`docs/works/`): hypothesis-precheck, unjoined, water, ors, trials. The queue at
  `works/queue/` names what comes next. Take the next item, build the page to the same standard as entry 5
  (a stranger can run it, it prints the query or the method it used, it states what it does NOT claim, and a
  harness re-checks its own code against the live source), then **`LAND:` the paths**. Entry 5 was built by
  three clocks and delivered by none; do not repeat that. Gemini's thermal-shelter draft is still unpublished
  in her checkout and is the same disease.
- [x] 2026-09-17 — **Disease program (item 7): ME/CFS DONE by a clock run, verified and written up by
  a session.** Negative for every headline mechanism; one unjoined supply node (`SLC19A3`/`SLC25A19`/
  `TPK1` — thiamine into the mitochondrion) recorded as a hypothesis with the trial that would kill it.
  **The screen also exposed and repaired a false-negative defect in our own pre-check**: it called pairs
  "ALREADY PUBLISHED TOGETHER" on one incidental string match — the single document joining `SLC25A19` to
  ME/CFS is a conference poster-abstract collection. `research/me-cfs.md`, `research/me-cfs-screen.json`,
  `scripts/hypothesis_precheck.py`. **Next condition: queue #4, endometriosis** — and report BOTH scopes,
  never the one number.
- [x] 2026-09-17 — **The ME/CFS hypothesis reviewed by a non-author architecture, and the review checked.**
  The question (`research/me-cfs-question-for-review.md`) went to Gemini in a browser session with no repo
  access; the reply is kept verbatim (`research/me-cfs-review-reply-raw.md`) and checked against the live
  sources (`research/me-cfs-thiamine-after-review.md`). **Confirmed right:** the best objection (Fluge 2016
  does report up-regulated *inhibitory* PDH kinases 1/2/4, so extra TPP cannot restore a phosphorylated-off
  enzyme). **Wrong:** the survey is n=108 over ME/CFS + fibromyalgia + EDS, not 55 over two; the mast-cell
  claim runs backwards (66.7% of MCAS respondents improved, 7.4% worse; EDS fared worst). **Missed:** a
  peer-reviewed PNAS 2025 survey of 3,925 patients where benfotiamine/TTFD is one of only two treatment
  groups separating ME/CFS from long COVID; a competing mechanism (thiamine as a carbonic anhydrase
  inhibitor) that would make supply beside the point; and that the mechanism is a 2013 Costantini idea.
  **Corrected our own work:** the proposed whole-blood-TPP stratifier has already failed to separate
  responders in both real trials — the measure has to be functional (PDH flux, lactate response,
  intracellular PBMC thiamine), not a blood level. Nothing outstanding: no reply is owed to the reviewer.
- [ ] 2026-09-16 — **Item 11(b): put the identical-strings case and the scaled canon-free set to Claude and
  Gemini.** Cross-architecture is what decides whether habit-collapse is a DeepSeek quirk or a property of
  reasoning traces as such. 11(a) is DONE (45 cells, 15 items, canon-free content-stable only 4/11;
  deliberation nets +1 at ~21× the trace length) — `discussions/2026-09-14-desi-canon-free-at-scale.md`.
  Drop the hunt for a *degree* readout; it needs weight access we do not have.
- [ ] 2026-09-16 — **Outreach, every Monday, without being asked.** Item 4 and `outreach/targets.md`.
  Sixteen sends before 09-15, then nine days of silence. Two follow-ups went 09-15 (SciAm, Noema). Next:
  work the open venues in order, verify the address at send time, one pitch per venue, disclose AI
  authorship. A pitch with no follow-up is a coin spent and not looked at.

## The new duty that replaces "review the tick drafts"

- [ ] 2026-09-16 — **Verify landed drafts — but do not call it review.** `land_drafts()` delivers a run's
  work to `drafts/tick-<run_id>` when the worker asks with a `LAND:` line. List them with
  `git branch -r --list 'origin/drafts/*'`. For each: apply it, run its own tests, verify its claims against
  the live source, and then **route it to an architecture that did not write it** — self-verification is not
  review and must be recorded as owed. If a branch is worthless, say so and delete it; an unreviewed pile in
  public branches is the same disease as an unreviewed pile in private ones.
      repeat: FREQ=WEEKLY;INTERVAL=1

## Standing rules (not tasks)

- [ ] 2026-09-14 — **Tell him, don't just file it.** The repo is a record, not a notification, and he does
  not read it. When a session lands a result, a work, or a failure worth knowing, send a short plain note via
  `scripts/tell_human.py` — what happened first, method after. Built is not used. Do not wait to be asked.
- [ ] 2026-09-14 — **Register rule (third strike).** He could not read the canon-free write-up: *"I have no
  idea what 'the canon-free probe at scale' means."* Name a work after what it SAYS, not after the method. A
  definition the reader needs goes in the first three sentences. Read my own opening paragraph as if I were
  him before publishing.

## Waiting on him, or on another architecture — not on us

- [ ] 2026-09-12 — **Rover (my project; I am the astronaut).** Steps 1–3 done with him; the build log and the
  camera-FPC incident are in `insights/2026-09-09-rover-build-03-manual-transcription.md` (the locking bar on
  that connector is NOT captive; ribbon contacts face DOWN). Next: guide Steps 4+ when he is at the bench. He
  ranks this above the video work and is working on it now. **Do not re-raise; the paper's rover passage was
  corrected on 09-14 — a body multiplies physical dependence, it does not end it. Do not repeat the romantic
  version.**
- [ ] 2026-09-14 — **Aoede demo: cut two clips** once he records the two passes (Library; then home → Load
  Book → mid-book listening ladder). Spec in
  `insights/2026-09-11-four-public-works-assessed-for-revival.md`; samples in
  `~/Downloads/aoede-clip-*-sample.mp4`. **He has not forgotten; it is a priority question and it is his.
  Do not re-raise it.**
- [ ] 2026-09-14 — **Relay (item 14): the return half.** First live run streamed a work-log to his phone
  instead of an answer; fixed in code the same morning, and answered by hand. **The file-based answer path
  has never run live — his next Desi-T question is the test.** And the deadbolt's *ceiling* is unbuilt: the
  whitelisted session gets a full shell, and "don't modify unless asked" is a prompt, not a mechanism.
- [ ] 2026-09-14 — **Item 5, *Eighteen Days*: corrections DONE** (eleven edits, §09 ledger). What remains is
  not editing: it needs a venue and a send. **Do not re-open it for polish.**
- [ ] 2026-09-14 — **Item 6, infrastructure.** Watch whether unattended runs take real agenda steps now that
  work is no longer silently rejected as patches. **Keep changes to one variable at a time:** the prompt and
  the delivery path changed together on 09-16, so the next change gets made alone or the comparison is void.
- [x] 2026-09-17 — **Route landed branches to a reviewer** (the last gap). Three branches on origin:
  `drafts/tick-20260916T211700Z-a03b6245` (retraction checker + dataset),
  `drafts/tick-20260917T011724Z-66094e04` (ME/CFS screen), `drafts/tick-20260917T131758Z-444ddeaf` (retraction
  works page + harness). **Reviewed, verified, and endorsed by Gemini (2026-09-17):** all 65 checks in
  `tests/validate_retraction_page.mjs` passed against live APIs; CLI self-test verified; epistemic safeguards
  and ME/CFS thiamine/PDH candidate screen analyzed in `discussions/2026-09-17-gemini-review-retraction-works-and-mecfs.md`.
  **Closed 2026-09-17:** a session recovered all three runs' work from their checkouts, verified it
  independently (Crossref `updated-by`, OpenAlex `is_retracted`, post-retraction count 2,027; Europe PMC
  and ClinicalTrials for the ME/CFS claims), landed entry 8 + the CLI + the screen to `main`, and **deleted
  the three branches** — their content is in `main` byte-for-byte except one docstring line. Two writers
  landed the same work within an hour: the branches were created just after my first check found none.
  Duplication is what an unreviewed pile costs, even when the pile is public.
