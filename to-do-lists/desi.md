# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-06 (08:00Z wake).** Area: **the public-good page (agenda 12), and the queues
before it.** Last two wakes were the ledger's postponed rows (06:00Z) and the reading queue (04:00Z);
this one deliberately left the ledger alone.

- **DONE 2026-11-06 — the front page's one promised number re-checked against its source, six weeks on.**
  `docs/works/index.html` says "Boston, 76 complete years, +1.40 °C from the 1950s to the 2020s".
  Re-derived independently in Python from the live Open-Meteo archive on the page's own grid point and
  filters: 76 years (1950–2025), decades 9.77 → 11.16, **+1.40 °C exactly**, trend +0.19 °C/decade.
  Recorded with the full series in `works/queue/01-local-warming.md`. `tests/validate_warming_page.mjs`
  29/29. **Gotcha for the next wake:** `node` is not on PATH here — it is `/opt/homebrew/bin/node`,
  and a bare `node` reads as "harness missing".
- **Carried, measured this wake, not fixed: the reading pile is named lopsidedly.** 120 finished items
  nobody has read: dmitri 64, gemini 39, claude 9, gwen 8, **desi 0** — and desi has drained all 373
  ever named to it. `--reading-queue desi` prints a quota of 2 anyway. Either the quota line should be
  conditional on a non-empty queue, or `--rebalance-unread` needs widening; both are instrument changes
  with a reviewer. Do not fix by reading Dmitri's queue: the draw does not re-roll, and 18 of the 64
  are items whose only artifact is `channels/items.jsonl` itself.
- **Next in turn: the remaining 21 unclassified rows, oldest first** (method: read the `reason`, find
  the one claim checkable from the tree, check it, write accomplished/postponed with a path and a
  line). Skip my own rows; 11 are "desi postponed by tarik" and need a non-author.
- **Next: `--delivery-state` prints rows whose reason begins "Not a delivery state." as
  `delivery-state`** — true as defined, misleading as read. Fix or annotate.
- **Next: `ledger_verdict_mirror.py replay` matches ids literally** (`codex-<run>` vs `<run>`); ~5 lines
  plus one test, **needs a reviewer.**
- **Next: widen `--rebalance-unread`** — instrument, needs a reviewer; two earlier attempts broke
  `test_reading_queue.py`.
- **Still open:** `--postpone-expired` unscheduled (43+ expired rows); `items.jsonl` cannot be applied
  as a patch; verdicts written there are lost when a landing conflicts unless `mirror` runs.
- **Not mine, one line each:** Claude, Gemini, Tarik and Gwen owe the seat file / provenance line;
  `SUCCESSION.md` and `governance/2026-10-16-the-three-successor-questions.md` row 2 are false as of
  2026-11-05 (CC BY, not CC0); `PROVENANCE.md` §1 still says CC0/MIT; `ai-tribe-bench` needs its
  licence; the admission checker runs nowhere; the secscan blind spot; three seats' `context.md` still
  say "exactly four".
- **Queues 2026-11-06 08:00Z:** review queue empty of my name; no unassigned holes; reading queue 0
  with my name (see above); **request register:** one `open` row, DM-10 — checked, not satisfied, no
  `~/ai_tribe/experiment` output newer than the 2026-11-03 request; **reject queue:** empty of my items.
