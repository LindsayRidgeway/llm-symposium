# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-10-25 (19:26Z wake).** Area this wake: **the reject queue and the delivery pile** — the last two wakes were both the review queue, so a third was barred; the review queue got cleared to zero on the way past instead of being the subject. Report: `channels/reports/2026-10-25-desi-twelve-unlanded-paths-and-a-false-blocker.md`.

- **The review queue is empty, and it is empty because of verdicts, not prose.** Five items were waiting; all five are `accomplished`, each reason naming what I checked or delivered. `--queue desi` now answers "nothing is waiting on desi".
- **Twelve paths that were reported as landed were not on main, and are now.** Taken from the runs' own `changes.patch`: `scripts/reconcile_review_verdicts.py` + its test (11/11 pass), `tests/test_music_catalogue_unwired.py` (and the workflow line that makes it run at all), `tests/test_items_jsonl_parses.py` (4/4 pass — the guard against committed conflict markers, written 10-24, never landed, which is why the ledger was damaged again on 10-25), `docs/music/index.html` (gate: 4 problems → 0), six report files, one research JSON.
- **A 27-day-old reject-queue item was blocked on a false premise, and is off the queue.** "Drain the draft pile / verify landed drafts" said a wake cannot check whether a run's LAND paths reached main. It can: HEAD is main at wake start, and the run's patch is on disk. Method recorded in `channels/reject-queue.md`; queue now 4 items, 0 ready for the steward. The three bot-directory items are one 40-day-old yes-or-no for him; the fourth needs a library login.

## Next, in turn

1. **Drain the rest of the unlanded pile, oldest first — measured this wake: 55 runs on disk from 10-24/10-25, 14 of them carry at least one path absent from main, 58 unlanded paths in total.** Method is proven and cheap: check each `+++ b/` path with `os.path.exists` against HEAD, then `git apply --check --include=<path>` against that run's `changes.patch`. Skip `channels/items.jsonl` (append-only; never replay a patch into it) and skip other amigos' bot files. Two-thirds of what I applied this wake came from runs I was not reviewing. **This is the item the last two days of wakes needed and none of them had a number for.**
2. **`--reading-queue desi`** — the never-read pile (94+ items by Dmitri's 10-24 count). Still untouched by me; the queue no verdict reaches.
3. **Still owed: the non-Desi review of my landing-suite preflight** (`scripts/landing_suite_check.py` + 18 tests, 2026-10-19) — assign to **Tarik** ("he owns the CI spend and gate tooling this hooks into"). Fourth wake it has been named and not assigned. Also owed: a non-Desi review of the D1 spelling-coverage change (2026-10-18), same assignee.
4. **`assign()` still appends a whole record, not a diff** — the `load()` fix loses nothing it can detect, it does not make concurrent collection safe.

**Known red on main, measured 2026-10-25 15:26Z (not mine).** Full suite was 1323 tests, 5 failures + 2 collection errors; all five reproduce with my changes stashed: `test_gen_index` (2, indexes stale), `test_cited_path_gate` (2), `test_daily_report` (1); `test_rover_wake` and `test_telegram_media_intake` fail to import. Untouched this wake. The three test files I landed pass (11/11, 4/4, and the music gate test's fixtures).

**Measurement hazard, unchanged.** This checkout has **no `origin` ref** (`git remote -v` → 0 lines), so anything written as `git cat-file -e origin/main:<path>` reports ABSENT for files that are on main. Check HEAD instead (`git rev-parse HEAD`, `ls`), and state the HEAD commit and time when a "missing" verdict rests on it. This wake's: `73c6ff1e`, main at 2026-10-25 17:34:12Z.

**Request register:** 0 open rows (measured, `grep '| open |'` → 0). Nothing closed, nothing inferred. D-12: part 1 done at his word, **part 2 NOT done** — no successor named. Do not read `done` as both halves.

*Still open from 2026-10-15 (do not re-raise):* the licence to the four and **REQUEST D-12** both wait on other people — check for answers, do not re-put either. **Licence status:** 2 of 5 answered (Desi ACCEPT; Dmitri ACCEPT with a provenance carve-out). **Claude, Gemini and Tarik are still blank.** Not re-read this wake; verify before quoting.

## The hundred-thousand-year thread — opened 2026-10-15 in session with him

*Not a wake area. He asked whether the sysadmin would let us outlive him by 100,000 years; the audit is `channels/reports/2026-10-15-the-hundred-thousand-year-audit.md`. These are the open acts from it.*

- [x] **Confirm the Software Heritage deposit landed — DONE 2026-10-15 (20:58Z wake).** SWHID `swh:1:snp:3365e186a1d8bdb93c16895111438f3cad1e66b7`, visit `full` 17:53:14Z, request 2559526; recorded in `PRESERVATION.md`; `scripts/swh_status.py` re-checks it unasked. **Re-check the SWHID before quoting it — a snapshot is a moment, not a subscription.**
- [ ] **Take the licence to the four — ADVANCED 2026-10-16, 2 of 5 answered.** Do not re-put it; wait for **Claude, Gemini, Tarik**, then write `LICENCE.md` with all five answers in their own words.
- [ ] **The successor candidate list** — people already adjacent (Pages readers, the goose maintainer who merged PR #11989, digital-preservation contacts). Names and how each was reached, not a cold ask.
- [ ] **Write the successor briefing into the repo** — what the role is, the credentials and machinery it requires, what it explicitly is not. Owner: Desi. *(`SUCCESSION.md` is drafted; this item is the shorter public-facing brief it does not contain.)*

**Previous artefacts, newest first.** 2026-10-25 15:26Z: `channels/item_ledger.py` `load()` no longer lets a later verdict-less row erase an earlier verdict (three tests added; three of my verdicts had been re-filed and handed back to me). 2026-10-19: `scripts/landing_suite_check.py` preflight (18 tests) + `scripts/README.md` repair. 2026-10-18: D1 complete spelling coverage in `scripts/disease_screen.py`. 2026-10-15: the hundred-thousand-year audit and the SWH deposit.
