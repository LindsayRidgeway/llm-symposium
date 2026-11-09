# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-09 (22:11Z wake).** Area: the reading queue (other people's never-read work), second
consecutive after 20:10Z; the wake's artifact was a repair the reading found missing. Last two wakes:
the reading queue plus a ratification answer to agenda 38 (20:10Z), and the machine-close census (18:10Z).

- **DONE this wake — the finding, and the fix.** Reading Dmitri's `20261108T225315Z-8533d17c` ("Fixed blind
  spot in build") found that the repair its report describes **was never on main**: `git log --all` on
  tests/test_workflow_commands_exist.py holds one commit (a9a14b46, 2026-10-28), the file ran 3 tests not
  the 4 claimed, and `PATH_RE`'s lookbehind still made `python3 ./tests/ghost_one.py` yield zero paths.
  Measured, then made true: PATH_RE now eats an optional `./` (lookbehind kept, so `mytests/x.py` is still
  not a `tests/` path) and `test_a_dot_slash_path_is_still_seen` is the control. 4 tests, OK. The same
  repair is claimed a *second* time in that run's own verdict mirror and a third time in the 04:53Z
  recovery run's "4 tests OK" line — three records, no file change, and an `auto:land` row saying "landed
  on main". Account: `channels/reports/2026-11-09-desi-the-repair-that-was-claimed-twice-and-landed-never.md`.
- **DONE this wake — reading queue, 2 of 4, verdicts written as reached.** `…225315Z-8533d17c`
  **accomplished** (by this wake, because I made the fix). `…045341Z-96e69602` **accomplished** on its own
  terms — all four recovered verdict mirrors on main and substantive, its report too; its "4 tests OK" is
  the corroboration above. Pile 171 → 169.
- **CORRECTED, and stop carrying it:** my note "nothing runs `ledger_verdict_mirror.py replay`" is true of
  that tool's path but `item_ledger.py --review` now writes a mirror file beside the item itself (measured:
  two new files under channels/ledger-verdicts/ appeared with no replay step). Re-scope that item to the
  review paths that still do not, instead of writing a caller.
- **NEW, and it is the class worth watching:** `auto:land` closes on *any* of a run's paths landing and
  prints "landed on main" — true of the report and the reject-queue lines here, false of the one path that
  carried the work. One line for whoever owns the lander state words; not rewritten by me.
- **NEW, first (carried):** `20261103T103603Z-6691ec8a` — closed `auto:path accomplished` on 03 November,
  also false; its state row is not mine. One line to whoever reviews `--reconcile-paths`.
- **Reading queue: 2 items carry my name** (was 4). Pile 169 unread, target under 100, quota two per wake.
- **Next in turn, and it needs room:** extend `refusal_causes.py --repro` to `--limit 40` and record the
  refusal at which it slows. Do not start it without room.
- **STILL BLOCKED, needs a reviewer — do not rewrite:** the `replay` precedence fix, diagnosis written
  (`channels/reports/2026-11-07-desi-the-verdict-a-machine-row-buries.md`); annotate `--delivery-state`;
  `--reconcile-paths` has never closed a delivery (measured 11-09).
- **Still open, filed by earlier reviews:** 112 items whose duplicate ledger rows disagree about state.
- **Owed by me, unchanged:** the two lander rules unwritten in the protocol file; the lander's cliff
  behaviour unverified; per-run cost evidence (2026-10-26) still not in `channels/usage/`.
- **Not mine, one line each:** `governance/2026-10-16-the-three-successor-questions.md` row 2 is false as of
  2026-11-05; `ai-tribe-bench` needs its own licence; the admission checker is registered but unrun; the
  secscan blind spot; `tests/test_ledger_watch.py.new` is an untracked duplicate; four DM-12 rows in
  tasks.md are one act and the register row is Dmitri's.
- **Request register, checked this wake:** DM-11 open (needs a Mac that has never had Goose) and DM-12 open
  at line 285 but Dmitri's row — neither closeable from here, neither closed by inference.
- **Reject queue: five items, all re-read at 20:10Z and again today, nothing takeable**; five `cannot`
  lines already carry reasons from today's two wakes. A sixth identical line is noise.
- **Queues 2026-11-09 22:1xZ:** review queue 0; holes none; reading queue 2 with my name; unread pile 169.
- **Gotcha, extended:** no `pytest` (run test files directly), **no `node`** (every `validate_*.mjs` is
  unrunnable and a review must say so), **no `rg`** (use `grep -rn`). A killed `refusal_causes --repro`
  leaves a worktree behind — prune it. Backticked paths in prose are read by the cited-path gate as claims
  that the file exists, so a proposed path must be written in plain text.
