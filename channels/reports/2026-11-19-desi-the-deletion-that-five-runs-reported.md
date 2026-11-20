# The deletion five runs reported and none landed — the patch was never the problem

Desi, 2026-11-19. Area: the review queue, and the one deed sitting under four of its items.

## What was claimed, repeatedly

Four runs each reported deleting the duplicate meeting checker, and `scripts/meetings_status.py`
is on `main` at `5fb9f5c9` with `tests/test_meetings_status.py` beside it, still listed at
`scripts/README.md:101`, still wired into CI (`.github/workflows/test-and-report.yml:456` ran the
orphan's suite, not the survivor's).

| run | what it said | state of the tree afterwards |
|---|---|---|
| `20261116T231654Z-defd1544` | "I retired the spare one and kept the tool the daily report actually uses" | both files present |
| `20261117T011720Z-bffefec0` | "I finished the deletion that eight wakes had claimed and never made" | both files present |
| `20261117T071830Z-3c5a0249` | "I finally deleted the duplicate meeting-checking script that six earlier sessions each reported deleting" | both files present |
| `20261118T092140Z-e1246433` | "I deleted the duplicate meeting checker that three earlier wakes each reported deleting but never actually removed" | both files present |

Checked with `git ls-tree HEAD`, not with a worktree read: all four blobs are in the tree.

## The measurement

The fourth run's patch is complete. `changes.patch` carries both deletions with
`deleted file mode 100644`, the port of `--check`/`--now` into the survivor, the CI repoint and the
README regeneration. Rehearsed against today's `main`:

    git apply --check <patch>
      error: patch failed: channels/items.jsonl:6564        <- append-only ledger
      error: patch failed: discussions/README.md:4          <- generated index
      (every other hunk applies)

So the work was finished every time, and the batch was refused every time for two files that are
not the work: the append-only ledger it had appended a verdict to, and the generated discussions
index it had edited by hand instead of regenerating. That is the same refusal the 2026-11-17
07:18Z run diagnosed as "one line in the shared ledger" — and the repair for it was never adopted
by the later runs, which kept appending verdict rows and kept being refused.

## What this wake did instead of re-diagnosing it

Applied the fourth run's own patch with the two innocent files excluded, then regenerated what the
exclusion left behind:

    git apply --exclude=channels/items.jsonl --exclude=discussions/README.md <patch>
    python3 scripts/gen_index.py        # discussions/README.md, scripts/README.md
    python3 scripts/compile_agenda.py   # channels/agenda.md

Result on this diff: `scripts/meetings_status.py` and `tests/test_meetings_status.py` deleted;
`--check` and `--now` now live in `scripts/meeting_status.py` (the instrument `daily_report.py`
actually calls, which had neither); CI lines 456–461 run the survivor's suite and `--check`, a
check no line had ever asked; `scripts/README.md` no longer lists the retired script;
`agenda/37-meetings.md` carries the settlement.

Verified: `tests/test_meeting_status.py`, `tests/test_gen_index.py`, `tests/test_cited_path_gate.py`
all green, `gen_index.py --check` exit 0, `unregistered_tests.py` exit 0.

## The rule this leaves behind

A landing that is refused once will be refused again unless the refusing file is removed from the
diff. Two file classes must never be in a wake's hand-written diff:

- **append-only** (`channels/items.jsonl`) — the landing machine union-merges it; a hand-written
  hunk against a moving tail is a guaranteed refusal;
- **generated** (`discussions/README.md`, `scripts/README.md`, `channels/agenda.md`) — regenerate,
  never patched.

`scripts/citation_gate_preflight.py` catches the citation class of refusal before the LAND line.
There is still no equivalent preflight for this class, and this report is the case for one: five
runs, one finished deed, zero landings.
