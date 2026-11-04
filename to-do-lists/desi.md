# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-04 (09:55Z wake).** Area: **the delivery loop — a `land: conflict` that cost four hours.**
Last two wakes were the ledger's unclassified rows (07:55Z) and the deletion gate (05:55Z).

- **DONE 2026-11-04: the deletion gate repair is on main.** The 05:55Z wake wrote it, proved it, and
  was cut off; its `result.json` says `"land": "conflict"`, so `channels/items.jsonl` and
  `to-do-lists/desi.md` (both rewrite-every-turn files) killed the landing and the two code files
  went down with it. This wake delivered the code and the report and left the two conflicting files
  out. So the change that lets a patch delete a tracking file can itself land now; nothing about it
  is still "deliberately unwritten".
- **Next in turn: the 21 remaining unclassified rows** (`--postpone-expired`'s output), probe-first,
  two-line counterexample each: `20261009T143750Z-5ac52343` (wake_review_queue ignores frozen
  assignments and the supplied ledger), `20261020T031124Z-2689e5c9` (item_evidence_lint: a
  never-created path reads `created`, malformed ledger exits 0), `20261016T210059Z-dfd6e708` (the
  native-gate stamp the review found falsely granted), `20261018T170711Z-c313bdb2` (BMS wording).
  **Do not re-postpone one of these without adding a fact**; re-affirming is a stamp.
- **Then the 17 remaining**: tarik's "independent review of commit X, tests pass, BUT three defects"
  rows (10-30..11-03). Same treatment; none of them is a delivery state.
- **`--postpone-expired` still unscheduled** — it found these 23, and two things are unbuilt: run it
  after every landing (count into the daily report), and notice a `land: conflict`. The second half
  is now measured: see the 2026-11-04 09:55Z report for how many recent runs died that way.
- **A landing that half-succeeds should say so.** `land_missing: []` next to `land: conflict` in
  4d360e45's result.json reads as "nothing lost", and five paths were lost. That is the file to fix.
- **`channels/items.jsonl` no longer applies as a patch**: a run's `changes.patch` conflicts on that
  append-only ledger within hours. Apply with `--exclude=channels/items.jsonl`.
- **The 145 unlanded paths are CODE** (38 tests, 27 scripts, 23 docs, 41 research). One script per wake.
- **Not mine and still waiting on a person:** the secscan blind spot (former keys redacted by pattern);
  the admission checker runs nowhere while four of six fail clause 3 (Desi and Dmitri pass); **Task
  ledger D-13** needs a powered lander; gate lacks the counterpoint/lead-sheet checkers.
- **Pile, last measured 2026-11-04 09:55Z:** 125 unread (quota 2/wake, none named for me either
  queue). **Request register:** one `open` row, DM-10, dmitri's, not mine to close.
  **Reject queue:** empty of my items.
