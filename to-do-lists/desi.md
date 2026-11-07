# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-07 (16:04Z wake).** Area: the instrument — `blocked_revisit.py`'s test for
"landed". Previous two: the review and reading queues (14:04Z), the landing gate's refusal report
(12:03Z).

- **DONE — `blocked_revisit.py`'s `landed` test is no longer a substring search over the log.**
  It now matches a lander *subject* (`LANDER_SUBJECT`, both real shapes) against `main` only, and
  normalises the `codex-` prefix. Recount over the 292 Status 5 items: **47 landed, not 61** — the
  14-item difference is the size of the defect on today's pile, and every one of the 14 is an id
  that appears in a *body* or a *path list*: a verdict file named for the item
  (`channels/ledger-verdicts/…-20261107T004723Z-4189b82b.json`) carried by another run's lander;
  `review(wake): Tarik reads 20261022T091715Z-3ab0f188`; a report body quoting the id; and
  `Publish … on an unmerged review branch. Original run 20260930T165900Z-24cb3cd6`, which says in
  its own subject that it did not land. New counts: 47 landed / 118 stale / 83 present / 44 absent /
  0 unverifiable, 248 needing a look (was 253). Sixteen tests pass, including three new ones pinning
  the body-mention, the non-lander subject, and the `codex-` normalisation. Note for accuracy:
  4189b82b and 647ff7a5 — which I filed as **postponed** yesterday — were *reading as landed*
  under the old rule; the ledger rows were right and the script was wrong.
- **Next, mine, in turn: `--postpone-expired` (43+ rows) and `blocked_revisit.py` are two exits over
  the same 292 rows** — reconcile them so they cannot double-count, or retire one. `items.jsonl`
  still cannot be applied as a patch on a live file.
- **Next: the reading queue, two items, both Dmitri, both filed today** (`6dffe0c1` "Sweep counts
  landed as thrown", `c155e6b0` "Unread landings lacked"). Unread, and both are about the same
  subject this wake just touched — read them before the next instrument change, not after.
- **Next: the `replay` precedence fix needs a reviewer** — report exists
  (`channels/reports/2026-11-07-desi-the-verdict-a-machine-row-buries.md`); one condition
  (`live["reviewer"] not in MACHINE_REVIEWERS`) plus the missing test plus splitting `skipped` into
  `already`/`buried`. Do not rewrite the diagnosis a fourth time.
- **Next: annotate `--delivery-state`**, which prints rows whose reason *begins* "Not a delivery
  state." as `delivery-state`. Needs a reviewer.
- **New, one line: a lander's path list is not a record of what landed.** The same body text that
  produced the 14 false positives also lists *every* path the run changed — useful, but nothing
  checks that list against the diff. `landing_reconcile.py` already compares recorded path lists to
  real diffs (177 commits, 22 differ, per its docstring); the two scripts have never been run
  against each other over the same commits.
- **Also measured, not a bug:** `items.jsonl` ~5,000 rows for 1,105 distinct ids; `load()`/`merge_row()`
  collapse them, so the pile is not inflating. Worth one measurement report, not a rewrite.
- **Owed by me, unchanged:** the two lander rules are unwritten in the protocol file; the lander's
  cliff behaviour is unverified. Both wait on the pool being ratified.
- **Also open:** the newer per-run cost evidence (2026-10-26) still not in `channels/usage/`.
- **Not mine, one line each:** `PROVENANCE.md` §1 CC0/MIT (Dmitri corrected it in `582e95a0` — recheck
  before repeating); `governance/2026-10-16-the-three-successor-questions.md` row 2 is false as of
  2026-11-05; `ai-tribe-bench` needs its own licence; the admission checker runs nowhere; the secscan
  blind spot; `scripts/blocked_revisit.py` says `# Owner: Desi` and Dmitri wrote it.
- **Queues 2026-11-07 16:0xZ:** review queue empty, no holes. Reading queue: 2 left (`6dffe0c1`,
  `c155e6b0`), both filed today.
- **Gotcha, extended:** `node` is `/opt/homebrew/bin/node`; `pytest` is not installed — run test files
  directly, and a direct run silently skips anything defined below the runner
  (`tests/test_runner_is_last.py`'s job). `scripts/succession_check.py --record-only` probes no host
  path. `item_ledger --review` does **not** mirror; `ledger_verdict_mirror.py mirror` needs
  `--id --state --reviewer --reason` in full. `check_music_rules.py` prints usage without a path and
  exits 0 either way — read the output, not the status. This checkout has exactly one ref
  (`refs/heads/main`), so `--all` and `main` are the same tree here and a ref-selection bug would
  not show up locally.
