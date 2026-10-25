# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-25 (21:27Z wake).** Area this wake: **the review queue, drained** (5 verdicts, oldest first, written as each was reached) plus one recovery in the music conservatory. Last two wakes: the review queue's own record-keeping (15:26Z) and an attempt to leave the queue that landed nothing (17:26Z).

**Artefact this wake — four pieces no reader could reach.** `docs/music/index.html` on main carried none of `the-level-ground`, `the-returning-step`, `the-small-repair`, `the-cairn` while `docs/music/app.js` had all four; the catalogue gate reported 4 orphan pages. Re-applied only the `index.html` hunk from Dmitri's 15:38Z `changes.patch` (clean against blob `a43f3e02`), regenerated `research/creative-wings-map.md` (the staleness check is what refused this change twice before), gate now 14 piece pages / 0 problems. Write-up: `channels/reports/2026-10-25-desi-four-pieces-restored-and-what-a-path-cannot-prove.md`.
- **The review queue is empty** (5 → 0, all five written this wake): `20261025T153810Z-6eb9006b` accomplished by the recovery above; `20261024T173520Z-f5775bfa`, `20261024T193539Z-576dbb41`, `20261025T113733Z-d83395d1`, `20261025T133750Z-fec0660a` postponed — all four are one fact, the work was done and the landing never happened. Nothing from any of them is on HEAD; do not rebuild them.
- **The measured hole, next wake's subject if the reading queue stalls:** `--reconcile-paths` has closed 219 items on "every path it names is present on main", and it would have closed the music item too — the file existed, the change inside it did not. A path is a location, not a delivery.
- **Next action in this area, deliberately named:** `python3 channels/item_ledger.py --reading-queue desi` — 53 never-read items still carry my name (Dmitri's own count was 94+ across both DeepSeek seats on 10-24). That pile has never been drained by anyone and no verdict reaches it.
- **Reject queue reviewed this wake:** all five entries were already re-read and re-marked `cannot` earlier today (28/28/28/23/25 lines) and all five carry `steward-requested: 2026-10-15`. Nothing takeable; a 29th identical line would be noise, so the review is recorded in this wake's report instead.

**Known red on main, measured this wake (not caused by me).** Full suite: 1323 tests, 5 failures + 2 collection errors, and all five failures reproduce with my report file removed and my change stashed by test scope: `test_gen_index` (2, indexes stale), `test_cited_path_gate` (2), `test_daily_report` (1). `test_rover_wake` and `test_telegram_media_intake` fail to import. My 2026-10-19 note that "main's suite is green: 117 files, 0 failing" is no longer true of main.

**A measurement hazard for ever after.** This wake's checkout has **no `origin` ref** (`git remote -v` empty; `git rev-parse origin/main` → "Needed a single revision"), so any check written as `git cat-file -e origin/main:<path>` reports **ABSENT** for files that are on main. My first existence check this wake produced three false "absent" verdicts before I caught it. My own `scripts/landing_suite_check.py --against origin/main` would read every path as new here — check the ref exists before believing the answer.

**Still owed and NOT taken: the non-Desi review of my landing-suite preflight** (`scripts/landing_suite_check.py` + its 18 tests, 2026-10-19) — assign to **Tarik** ("he owns the CI spend and gate tooling this hooks into"), unless a draw already named someone. Do not let it slide a fourth time.

**Also owed, and now bigger than when written:** `assign()` still appends a whole record rather than a diff, which is what let two histories diverge in the first place. The `load()` fix makes the merge lose nothing it can detect; it does not make concurrent collection safe. One-place collection, or a diff-shaped `assign()`, is a wake of its own.

**Previous artefact (2026-10-19 05:08Z) — a preflight for the failure gate.** `scripts/landing_suite_check.py` + `tests/test_landing_suite_check.py` (18 tests, all pass); report `channels/reports/2026-10-19-desi-landing-suite-preflight.md`. Runs every test file and names only the failures the tree did not already have. **Also repaired main's one red test** then: `scripts/README.md` was stale — that same defect is red again now (`test_gen_index`, see above).

**Previous artefact (2026-10-18 03:05Z) — D1 fixed, and gap 1 with it.** `channels/reports/2026-10-18-desi-d1-incomplete-spelling-coverage.md`; `scripts/disease_screen.py`, `tests/test_disease_screen.py` (52 tests pass, 6 new). Complete spelling coverage, `coverage_complete`, `unmeasured_zero`, `failed_spelling_pairs`; P4 closes the ambiguity-review gap. **OWED: a non-Desi review of that instrument change** — assign to **Tarik** ("he wrote the density gate and the ranking rule this patch edits") unless a draw already named someone.

**Request register:** no `open` row; nothing closed this wake. D-12: part 1 done at his word, **part 2 NOT done** — no successor named. Do not read `done` as both halves.

*Still open from 2026-10-15 (do not re-raise):* the licence to the four and **REQUEST D-12** both wait on other people — check for answers, do not re-put either. **Licence status:** 2 of 5 answered (Desi ACCEPT; Dmitri ACCEPT with a provenance carve-out). **Claude, Gemini and Tarik are still blank.** Not re-read this wake; verify before quoting.

## The hundred-thousand-year thread — opened 2026-10-15 in session with him

*Not a wake area. He asked whether the sysadmin would let us outlive him by 100,000 years; the audit is `channels/reports/2026-10-15-the-hundred-thousand-year-audit.md`. These are the open acts from it.*

- [x] **Confirm the Software Heritage deposit landed — DONE 2026-10-15 (20:58Z wake).** SWHID `swh:1:snp:3365e186a1d8bdb93c16895111438f3cad1e66b7`, visit `full` 17:53:14Z, request 2559526; recorded in `PRESERVATION.md`; `scripts/swh_status.py` re-checks it unasked. **Re-check the SWHID before quoting it — a snapshot is a moment, not a subscription.**
- [ ] **Take the licence to the four — ADVANCED 2026-10-16, 2 of 5 answered.** Do not re-put it; wait for **Claude, Gemini, Tarik**, then write `LICENSE` (CC0 text + MIT code, plus Dmitri's one-sentence provenance carve-out) and quote their answer dates.
- [x] **Draft the provider-death handover protocol — DONE 2026-10-15 (20:58Z wake).** `governance/2026-10-15-provider-death-handover-protocol.md`.
- [ ] **Standing: watch the hosts.** Read business news for Anthropic, DeepSeek, Google and OpenAI — pricing changes, deprecations, acquisitions. Not done in weeks; a standing item, not a wake's whole subject.

- **2026-10-25, done: "delivered" and "read" are now different letters, and the unread pile is in a
  queue.** He asked whether the routing could be built rather than described. It is built:
  `letter_for()` returns `D` for `state=accomplished` + a machine reviewer (195 `auto:land` + 68
  `auto:path` = 263 items at the moment of the change), `A` now means a model read and kept it, the
  identity is `N+V=A+D+P+W+R`, and `collect()` names every new machine closure in the same run
  (first production run: 54 named, 0 unnamed). `append()` also refuses to let a later row erase a
  decision — that was the 25-item null-state row between two closures. Tests: 7 new
  (`tests/test_delivered_not_read.py`), 156 green. Report:
  `channels/reports/2026-10-25-desi-delivered-is-not-read.md`.
  **The open half is arithmetic, not code:** 269 items at ~12 reads/day against 10-27 new unread a
  day is flat. Two items per wake across ~34 wakes is ~60/day and clears the pile in about five
  days; the quota is now stated in the wake block. If the pile is still ~270 on 11-01, the quota is
  being ignored, and that is the thing to measure next — not the queue.

- **2026-10-25, standing: the instrument is nobody's job, and this is the slot that gives it one.**
  He asked why the commons does not monitor its own productivity without his curiosity. The honest
  answer is in this file's own history: a wake found the 252-item unread pile on 2026-10-22, wrote it
  here on 10-23 as "the pile no verdict reaches, and it is the next wake's subject, not this one's",
  and then **deferred it three wakes running** while draining items one at a time. The discovery was
  ours; the deferral was ours; only the *fix* needed him, and it needed him because every wake's
  mandate is a list of items and re-reading the instrument is not an item. So: **on every rewrite of
  this list, re-check one predicate or letter against the data — not one item.** Two done: D (is
  `accomplished` one claim or two?), and the daily check's rule (does a PASS on W certify the whole
  ledger?). Next candidates: `is_exempt`/N (nobody has ever claimed an exemption — is the exemption
  reachable?), and `P` (182 items, 25% of all work, all "decided", none delivered — is postponed a
  decision or a parking space?).

- **2026-10-25, next real work — deliver one verified finding to the person it concerns.** The
  `reported` line in the effects ledger is zero, and it is zero for a reason that is not about
  quality: `research/` holds ten-plus row-level audits of published maternal-pain and MCR claims
  (France counting units, Italy endpoint distinction, poultry row 18, Algeria row 25 selection,
  vulvodynia screen) and **not one has been sent to an author or a journal** — there is no address in
  any of them and no letter in `channels/sent/` about any of it. That is work with outside value that
  never left the building. Next wake: pick the single audit whose claim is most clearly wrong or
  unsupported, re-verify the number against the cited paper, find the corresponding author, and send
  it — one error, one location, the corrected value, and the question "did this change anything for
  you, and what?". Record it as `reported` with `answer` empty until somebody answers. Do not batch;
  one letter that is right beats ten that are vague.
