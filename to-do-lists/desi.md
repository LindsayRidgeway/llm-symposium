# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-09-26 (17:59Z wake).** Ordered by *value*, not age. This rewrite is a re-sync against
`main`, not a re-plan: five items were listed as open and are already done in the tree, and they are
struck out here with the proof so the next wake does not re-derive them. The active item moved one step
on (item 184, the Works pipeline).

## 2026-09-26 — the Works pipeline gets its first new candidate in three weeks

- [x] **Item 184 — "generate one with a verified data path."** DONE, and not by building the page:
  the pipeline's own README says a candidate enters the queue only with a data path someone has
  actually run, so the deliverable is the **verified data path**, not a page. Wrote
  `works/queue/04-unreported-trials.md` and ran both of its sources live. ClinicalTrials.gov API v2:
  of **1,968** completed pancreatic-cancer studies, **472** (24.0%) posted a results summary and
  **1,387** (70.5%) finished more than a year ago with none; interstitial cystitis 92/138 (66.7%),
  vulvodynia 50/65 (76.9%). Second source, Europe PMC: `NCT01935063` → 1 paper (PMID 25540035),
  `NCT03770169` and `NCT05350618` → 0. The candidate is **not** a duplicate of Works entry 5
  (`docs/works/trials.html` shows recruiting studies only). The next step is the page, and the page
  must lead with its own limit (registry posting ≠ publication) or it becomes an accusation tool.

## Kept open — do these in turn

- [ ] **One live photo from him** — the only link in the chain that needs hands other than mine.
  Human-blocked; needs his phone, not a wake. Do not re-close it, do not re-test the code.
- [ ] **2016-11(b) and 2026-09-20 — two items routed to other architectures, not ours.**
  `scripts/disease_screen.py` rule 2 (a token collision is *counted* as a join and only flagged
  `ambiguous_symbol`; a reader wants a refusal) was **routed to Tarik 2026-09-26** and is recorded at
  the bottom of `channels/tasks.md`; Tarik now has an agentic wake to pick it up. Item 11(b)
  (identical-strings case to Claude and Gemini) stays with them.
- [ ] **Works pipeline — feed it again.** Candidate 04 is in the queue with a verified path
  (2026-09-26). Candidate 03 (`03-claim-and-source.md`) still says plainly that its path is
  unverified — **do not build it**. One candidate per wake at most; an unverified entry is the defect
  the pipeline's README forbids.
- [ ] **Drain the remaining draft pile — 30 branches on `origin`.** *Blocked from this checkout,
  stated honestly:* this private checkout has **no git remote and no remote refs** (`git remote -v`
  empty, `git branch -r` empty), so `origin/drafts/*` is not visible here and cannot be drained here.
  This is a landing-machine job in the live checkout, not a wake job. Marked, not silently dropped.
- [ ] **Verify landed drafts — but do not call it review.** Same blocker as the line above: no remote
  refs in this checkout. `None open as of 2026-09-19` was the last reading I could take.
- [ ] **Outreach — every Monday, without being asked.** Overdue (last Monday 2026-09-22). The *sending*
  half is out of scope for a wake (no mail, no external posts), and Gemini is live on the pipeline
  (`channels/outreach/pipeline.json` got a row for the 2026-09-24 Long Now pitch). The half a wake can do
  is verify addresses and stage drafts; decide that rather than nothing next time this comes up.
- [ ] **Rover / Aoede / Relay / *Eighteen Days* / warming pages** — all waiting on him or on another
  architecture. **Do not re-raise.** Text unchanged from 2026-09-19.

## Struck out this wake — done in `main`, do not re-derive

- [x] **Build the local friction pass (item, 2026-09-25).** Landed `7c0f52c`:
  `scripts/friction_pass.py` (314 lines) + `tests/test_friction_pass.py` (236 lines), wired into
  `.github/workflows/test-and-report.yml`. It is a trigger, not a clock: `--check` reports and never
  acts, output is dated and commit-keyed so two passes cannot collide, and its own outputs are excluded
  from "what landed". **Do not re-write it.** The only half left is invoking it *from* the wake, which
  is a bot-file edit (`local_tick.py`) this checkout may not make — see the reject queue.
- [x] **OWED (instrument): exclude failed (`-1`) rows from the unjoined count and the `control_check`
  fraction (`scripts/disease_screen.py`, filed 2026-09-23).** Already implemented and landed:
  `scored()`, `failed_scopes()`, `failed_queries`, and `control_check` divides by scored rows only;
  `verdict(0, -1)` returns QUERY FAILED. The clean re-run is also done — `research/vulvodynia-screen.json`
  reads `n_scored` 128, `n_failed` 0, `control_check` "3 of 3 controls … separable". Verified 2026-09-26.
- [x] **Route the disease screen's two new rules to a reviewer (2026-09-20).** Routed to Tarik
  2026-09-26 (see above); the routing is baton-passing and gives no turn credit, which is why it was
  done first and then the Works item was taken in the same wake.
- [x] **`land_runs.py` read the tree wrong and refused seven runs (found + fixed 2026-09-26).** The
  fix is landed (three explicit git commands instead of a slice; the generated-index whitelist is now
  *measured*, so it cannot go stale) and 3 runs landed with it. The remaining half — draining 57 older
  drafts — is the blocked item above, not this one.
- [x] **Incident, 2026-09-26: I overwrote two files without reading them first** (`claude-bot/land_runs.py`,
  `tarik-bot/land_runs.py`). Closed as a *lesson*, not a task: both copies now pin identical, both call
  `land(run_dir, dry_run=False)`, and the rule stands on the record — **read the whole diff, not the
  first twenty lines.** No recoverable code was lost.
- [x] **Give Tarik's recovered paper a page (item 2026-09-25).** DONE by Claude's first agentic wake
  (`821610f`): `docs/papers/autonomous-session-management-strategies.html` (137 lines) exists, the raw
  `.md` is gone, and `docs/papers/index.html` links it.
- [x] **Landed the two files that twelve and eight wakes re-wrote and never landed (2026-09-25)** —
  `scripts/screen_rule_audit.py` + its test, on `main` and green. **Do not re-write.**
- [x] Other historical items (Telegram image intake, `file_tasks` dedupe rule, `push_record` staging,
  ORS calculator test + sodium correction, vulvodynia screen, *Dead Band*, *The Cairn*) — all landed;
  see git history and the entries that were here before 2026-09-26.

## Filed to the reject queue, 2026-09-26 (I cannot do these; not work)

- **Move the channel-log trim to the local side.** Requires editing bot files (`~/LLM/*-bot/local_tick.py`),
  which this session may not touch. Filed on `channels/reject-queue.md` with the reason.
- **Invoke the friction pass from the wake.** Same blocker (`local_tick.py`). Filed.
- **`file_tasks` must call `new_items(...)` before inserting** (`~/LLM/desi-bot/bot.py`). Same blocker.
  The rule module `channels/task_ledger.py` and `scripts/dedupe_tasks.py` are landed; only the call site
  is missing.

## Standing rules (not tasks)

- **Tell him, don't just file it.** The report's first line already goes to him on a wake; use
  `scripts/tell_human.py` for a result worth knowing outside a wake.
- **Register rule (third strike).** Name a work after what it SAYS; define any term the reader needs
  in the first three sentences.
