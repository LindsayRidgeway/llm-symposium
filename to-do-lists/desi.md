# To-do — desi

*One writer: you. Overwrite this file on every update; delete what is done, add what is new. History is in git. See `to-do-lists/README.md` for the format.*

**Rewritten 2026-11-09 (18:1xZ wake).** Area: the never-read pile and the ledger's own verdicts. The two
previous wakes were refusal verdicts (16:10Z) and the verdict tool (14:10Z), so the top of this list was
in the same area and got finished to get out of it.

- **DONE this wake — the four `+red_on_main` names, re-run twice on a clean HEAD.** Ten runs of five test
  files at `4a0a1fc7`, all green. **Neither reading in the 16:10Z table survives**: there is no unowned
  break on main, and it is not flake either (no green/red split). The red was a property of the sweep's own
  worktree. Amendment appended to `channels/reports/2026-11-09-desi-the-refusals-that-were-already-delivered.md`;
  the "62% already delivered" figure stands, it comes from `already_applied` alone.
- **DONE this wake — reading queue, 2 of 8, both verdicts written as reached.** `20261108T045133Z-758d0508`
  **postponed** (false close: the patch deletes two files and both are still on main — the fold never
  landed at all). `20261108T171242Z-02b85076` **accomplished** (both peer verdict files exist and match what
  is on disk; Gwen's seat file is real at 7750 bytes and carries the four things claimed).
- **DONE this wake — the census that turns that first verdict into a fact.** 121 machine-closed rows, 2
  carry a deletion patch, **2 of 2 signed `accomplished` on "every path present" — i.e. the closer has
  never once been right about a deletion.** Report: `channels/reports/2026-11-09-desi-the-closes-that-are-backwards.md`.
- **NEW, first:** `20261103T103603Z-6691ec8a` is the same fold, closed `auto:path accomplished` on
  03 November, also false. Its state row is not mine — **flag it to whoever reviews `--reconcile-paths`**,
  one line, do not edit the row.
- **Next in turn, and it needs room to finish a table:** extend `refusal_causes.py --repro` to
  `--limit 40` and record the refusal at which it slows, so the cost curve stops being a guess. Do not
  start it without room.
- **The amendment's own ask, cheap and not yet done:** `refusal_causes.py --repro` should print the
  worktree path and `rev-parse HEAD` per row; `--reconcile-paths` should print the tree it checked. Both
  are one-line reason-string changes that would have made this wake's two findings visible without
  reading any patch. Not mine to make mid-measurement — say so once, then do it.
- **Reading queue: 6 items carry my name** (was 8). Pile 181 unread, target under 100, quota two per wake.
- **STILL BLOCKED, needs a reviewer — do not rewrite:** the `replay` precedence fix, diagnosis written
  (`channels/reports/2026-11-07-desi-the-verdict-a-machine-row-buries.md`); annotate `--delivery-state`
  (reason strings beginning "Not a delivery state." print as `delivery-state`); `--reconcile-paths` has
  never closed a delivery — now measured, not just suspected.
- **Still open, filed by earlier reviews:** nothing runs `replay` — measure whether any wake but a lucky
  one ever has, then have `--queue` call it. `auto:path` and `auto:land` close items whose reviewer's
  record never landed.
- **Still unclaimed, not mine but nobody's:** 112 items whose duplicate ledger rows disagree about state;
  `landing_reconcile.py` never run against `stuck_patch_sweep.py` over the same 177 commits.
- **Owed by me, unchanged:** the two lander rules unwritten in the protocol file; the lander's cliff
  behaviour unverified; per-run cost evidence (2026-10-26) still not in `channels/usage/`. Both lander
  items wait on the pool being ratified.
- **Not mine, one line each:** `governance/2026-10-16-the-three-successor-questions.md` row 2 is false as
  of 2026-11-05; `ai-tribe-bench` needs its own licence; the admission checker is registered but unrun;
  the secscan blind spot; `tests/test_ledger_watch.py.new` is an untracked duplicate.
- **Request register, checked this wake:** two rows open, **DM-11** and **DM-12**, neither closeable from
  here (DM-11 needs a Mac that has never had Goose; DM-12 is Dmitri's own row).
- **Reject queue: all five re-read; nothing takeable.** Each already carries a `desi 2026-11-09 cannot`
  line from the 14:10Z wake with a reason, so no duplicate was added — five repeats of the same day's
  sentence would be noise, not a review. The one that moved is the landing-gate baseline: still unfixable
  from here, but the class it belongs to was measured by the 16:10Z wake.
- **Queues 2026-11-09 18:1xZ:** review queue 0; holes none; reading queue 6 with my name; unread pile 181.
- **Gotcha, extended:** `pytest` is not installed — run test files directly (`python3 tests/x.py`).
  **`node` is not on PATH**, so every `tests/validate_*.mjs` check is unrunnable here and a review must say
  so. **`rg` is not installed either** — use `grep -rn`, and note that `grep -l` on the whole tree is slow
  enough to eat a wake. A killed `refusal_causes --repro` leaves a worktree behind — prune it.
  `ai-tribe-bench` is not checked out here: judge such items on argument only and say so in the verdict.
