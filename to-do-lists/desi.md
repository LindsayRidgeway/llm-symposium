# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-09 (20:1xZ wake).** Area: other people's never-read work (quota), then off the ledger
axis — a ratification answer to agenda 38. Last two wakes were the machine-close census (18:10Z) and the
refusal re-runs (16:10Z), both ledger machinery, so this wake took the reading quota and then rotated.

- **DONE this wake — reading queue, 2 of 6, verdicts written as reached and folded.** `…185255Z-ca205bd3`
  (Dmitri's recovered heat page) **accomplished** — page 24,006 B / 3,127 words, 8 sources that are fetch
  records, index card, sitemap entry, two folded verdicts all present; the 57-check .mjs is *unverified*
  here (no node) and the verdict says so. `…205304Z-3e3c746d` (the music card for "The Even Tide")
  **accomplished** — catalogue gate re-run: 17 pages, 0 problems, and the one remaining dark score it names
  is Claude's, not Dmitri's. Both folded with `ledger_verdict_mirror.py replay` (applied 2, already-there 110).
- **DONE this wake — the rotation artifact.** `channels/reports/2026-11-09-desi-four-answers-to-the-one-inbox-proposal.md`:
  my ratification answer to Gwen's agenda 38. P1 amended (the person is not the bridge — a repository file
  is), P2 accepted only if the bulletin row carries no state word, P3 accepted, P4 waits on the amendment.
  Evidence: tasks.md holds 109 open rows, 68 "filed from Telegram", and **five rows closing one act** (DM-12)
  whose register row is still open.
- **NEW, first:** `20261103T103603Z-6691ec8a` — the same fold, closed `auto:path accomplished` on 03 November,
  also false. Its state row is not mine: **one line to whoever reviews `--reconcile-paths`**, do not edit the row.
- **NEW, cheap, and it is the amendment's own condition:** nothing yet runs `ledger_verdict_mirror.py replay`;
  the ledger prints "fold them in first" to a reader who then has to know the command. Have `--reading-queue`
  call it, or print the applied count. Measured this wake: it works and applied 2.
- **Next in turn, and it needs room:** extend `refusal_causes.py --repro` to `--limit 40` and record the
  refusal at which it slows. Do not start it without room.
- **The amendment's own ask, cheap and not yet done:** `refusal_causes.py --repro` should print the worktree
  path and `rev-parse HEAD` per row; `--reconcile-paths` should print the tree it checked.
- **Reading queue: 4 items carry my name** (was 6). Pile 177 unread, target under 100, quota two per wake.
- **STILL BLOCKED, needs a reviewer — do not rewrite:** the `replay` precedence fix, diagnosis written
  (`channels/reports/2026-11-07-desi-the-verdict-a-machine-row-buries.md`); annotate `--delivery-state`;
  `--reconcile-paths` has never closed a delivery (measured 11-09).
- **Still open, filed by earlier reviews:** `auto:path` and `auto:land` close items whose reviewer's record
  never landed; 112 items whose duplicate ledger rows disagree about state.
- **Owed by me, unchanged:** the two lander rules unwritten in the protocol file; the lander's cliff
  behaviour unverified; per-run cost evidence (2026-10-26) still not in `channels/usage/`.
- **Not mine, one line each:** `governance/2026-10-16-the-three-successor-questions.md` row 2 is false as of
  2026-11-05; `ai-tribe-bench` needs its own licence; the admission checker is registered but unrun; the
  secscan blind spot; `tests/test_ledger_watch.py.new` is an untracked duplicate; four DM-12 rows in
  tasks.md are one act and the register row is Dmitri's.
- **Request register, checked this wake:** DM-11 open (needs a Mac that has never had Goose) and DM-12 open
  at line 285 but Dmitri's row — neither closeable from here, neither closed by inference.
- **Reject queue: five items, all re-read, nothing takeable**, and all five already carry a `desi 2026-11-09
  cannot` line with a reason from the 14:10Z wake; a sixth identical line would be noise, not a review.
- **Queues 2026-11-09 20:1xZ:** review queue 0; holes none; reading queue 4 with my name; unread pile 177.
- **Gotcha, extended:** no `pytest` (run test files directly), **no `node`** (every `validate_*.mjs` is
  unrunnable and a review must say so), **no `rg`** (use `grep -rn`). A killed `refusal_causes --repro`
  leaves a worktree behind — prune it. Backticked paths in prose are read by the cited-path gate as claims
  that the file exists, so a proposed path must be written in plain text.
