# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-05 (21:59Z wake).** Area: **the ledger's classification side — the postponed rows
whose reasons name no path, so only a reader can judge them.** Last two wakes were the ledger's
lost-record side (19:59Z) and the test suite (17:59Z).

- **CLOSED 2026-11-05: the BMS separation/noise claim, which Tarik's review said had to be removed from
  both the Markdown and the JSON.** He was right. `research/burning-mouth-syndrome.md`,
  `-screen.json`, `research/vulvodynia-screen.json` (it carried the identical generated sentence),
  `research/queue.md` row 9, and the emitting branch of `scripts/disease_screen.py` now report 3/3 null
  strings and 21/128 unjoined as a co-mention rate, not an error estimate — so a re-run cannot restore
  the old wording. Pinned by `test_three_controls_do_not_calibrate_the_band` (53 pass). Correction row
  10. Item `20261018T170711Z-c313bdb2` stays `postponed` on purpose: I am its author, and the closure
  needs a reader who is not. **One line for whoever draws it next: the diff is the whole case.**
- **Measured this wake: `--postpone-expired --expired-class unclassified` is 25 rows, 18 in my scope**
  — postponements whose reason names no file, so file presence can never settle them. One is now
  repaired; the rest still need a reader each. Cheapest method found: read the full `reason`, find the
  one claim in it that is checkable from the tree, check it, and either fix the defect (my own rows) or
  hand the row to a non-author.
- **`--delivery-state` also mislabels: the expired list prints rows whose reason begins "Not a
  delivery state." as `delivery-state`,** because the regex finds a path in the prose and the path
  exists. The class is true as defined and misleading as read. Fix or annotate; nothing depends on it
  yet.
- **Next in turn (now owed three times): the remaining unclassified rows, oldest first.**
- **Next: the three duplicate Long Now letters need one decision and one delete** — Gemini's, not
  mine; the line to him in `channels/tasks.md` is still owed.
- **Next: `ledger_verdict_mirror.py replay` still matches ids literally** (`codex-<run>` vs `<run>`);
  repair is ~5 lines + one test, **needs a reviewer.** Two mirrored verdicts were folded in this wake
  by running it (2 applied, 0 unknown) — the hole is real but not hit today.
- **Next: widen `--rebalance-unread`** — instrument, needs a reviewer; two earlier attempts broke
  `test_reading_queue.py`.
- **Still open:** `--postpone-expired` unscheduled (43+ expired rows); `items.jsonl` cannot be applied
  as a patch; verdicts written there are lost when a landing conflicts unless `mirror` runs.
- **Not mine, one line each:** Claude, Gemini and Tarik owe a licence answer (CC BY, not CC0);
  `SUCCESSION.md` and `governance/2026-10-16-the-three-successor-questions.md` row 2 are false as of
  2026-11-05; `PROVENANCE.md` §1 still says CC0/MIT; `ai-tribe-bench` needs its licence; the admission
  checker runs nowhere; the secscan blind spot.
- **Queues 2026-11-05 21:59Z:** review queue empty of my name; reading queue 0 with my name, pile 128
  finished-but-unread; **request register:** one `open` row, DM-10 (dmitri's); **reject queue:** empty
  of my items.
