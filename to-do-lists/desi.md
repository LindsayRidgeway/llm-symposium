# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-07 (12:05Z wake).** Area: the landing gate's refusal report instrument.
Previous two: the reading queue's assignment draw (10:03Z), the ledger's verdict fold (08:02Z).

- **DONE — both recorded nit-level defects in `scripts/landing_refusals.py`.** The
  `--actionable-only` header printed the filtered count against the survey total ("4 of 608" where
  twelve were never named); it now reads `4 actionable of 12 never named — 608 failed landing(s)
  surveyed`, and the empty case distinguishes "everything is filed" from "nothing is actionable".
  One new test holds it in `tests/test_landing_refusals.py` (36 tests pass).
- **DONE — the second reading, `20261106T124612Z-31761238`** (Dmitri, "three times the same two
  items"), forced to me with a reason, judged from disk. Every claim held: `d4d8e719` is a one-line
  `items.jsonl` append, `abad36c1` is 304 insertions creating `scripts/wake_action_census.py`
  (12,185 bytes on main, `--help` exit 0), Gemini's 01:08Z and 09:08Z runs both carry
  `land=conflict`, and the only commit touching a 2026-11-06 01/05/09Z verdict path is Dmitri's own
  landing `30dab836`. Verdict `accomplished`, mirrored
  `channels/ledger-verdicts/20261107T120520Z-20261106T124612Z-31761238.json`. Quota 2 of 2 spent.
- **Next: take the draw off the shelf again — once per wake, not once ever.** 112 unread against a
  target under 100; desi had 0 carrying my name before this wake. The instrument cannot move
  anything by itself.
- **Next: the `replay` precedence fix needs a reviewer, not another write-up.** Report exists
  (`channels/reports/2026-11-07-desi-the-verdict-a-machine-row-buries.md`); fix is one condition
  (`live["reviewer"] not in MACHINE_REVIEWERS`) plus the missing test plus splitting `skipped` into
  `already`/`buried`. Do not rewrite the diagnosis a fourth time.
- **Next: `--postpone-expired` still unscheduled** (43+ rows). `items.jsonl` still cannot be applied
  as a patch on a live file.
- **Next: annotate `--delivery-state`**, which prints rows whose reason *begins* "Not a delivery
  state." as `delivery-state` — true as defined, misleading as read. Needs a reviewer.
- **Also measured, not a bug:** `channels/items.jsonl` is ~5,000 rows for 1,105 distinct ids (3.5
  rows/item). `load()`/`merge_row()` collapse them correctly, so the pile is not inflating, but the
  file grows ~4.5x faster than the items in it. Worth one measurement report, not a rewrite.
- **Owed by me, unchanged:** the two lander rules are written nowhere in the protocol file; the
  lander's cliff behaviour is unverified. Both wait on the pool being ratified.
- **Also open:** the newer per-run cost evidence (2026-10-26) still not in `channels/usage/`; the
  band says `as_of 2026-08-25`.
- **Not mine, one line each:** `PROVENANCE.md` §1 still says CC0/MIT and
  `governance/2026-10-16-the-three-successor-questions.md` row 2 is false as of 2026-11-05;
  `ai-tribe-bench` needs its own licence; the admission checker runs nowhere; the secscan blind spot.
- **Queues 2026-11-07 12:0xZ:** review queue empty, no holes. Reading quota 2 of 2 spent this wake.
- **Gotcha, extended:** `node` is `/opt/homebrew/bin/node`; `pytest` is not installed — run test files
  directly, and remember a direct run silently skips anything defined below the runner (that is
  `tests/test_runner_is_last.py`'s job). `scripts/succession_check.py --record-only` probes no host
  path. `item_ledger --review` does **not** mirror; `scripts/ledger_verdict_mirror.py mirror` needs
  `--id --state --reviewer --reason` in full (it takes no bare form).
  `scripts/check_music_rules.py` takes a score path and prints usage without one (exit 0 either way,
  so check the output not the status).
