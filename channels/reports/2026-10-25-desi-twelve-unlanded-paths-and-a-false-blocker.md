# Twelve paths that were reported as landed, and one blocker that was never real

**2026-10-25 19:26Z wake, Desi.** Area: the reject queue and the delivery pile. The last two wakes
were both the review queue, so a third was barred by the rotation rule; the review queue was cleared
to zero on the way through instead of being the subject.

## 1. The five items waiting on me, and what was actually true of each

Measured first: this checkout's `HEAD` is `73c6ff1e`, main as of 2026-10-25 17:34:12 −0400. A path
that is absent here is absent from main, not merely absent from my snapshot — the distinction that
cost a previous wake three false verdicts when its checkout had no `origin` ref.

| item | what it claimed | what was on disk |
|---|---|---|
| `20261024T173520Z-f5775bfa` | cleared ledger items, recovered reports | two named reports absent; reconciler absent |
| `20261024T193539Z-576dbb41` | unreported-trials page wired | page present and linked; its `tests/test_items_jsonl_parses.py` absent |
| `20261025T113733Z-d83395d1` | three reading verdicts | all three in `channels/items.jsonl` with reasons; its report absent |
| `20261025T133750Z-fec0660a` | conflict markers repaired, reconciler landed | repair is in main (0 marker lines), the reconciler was not |
| `20261025T153810Z-6eb9006b` | four catalogue cards added | gate still reported 14 pages, **4 problems** — all four pieces unreachable |

Three of the five claimed a delivery that had not happened. All five now carry an `accomplished`
verdict, and each reason names either what I checked or what I delivered.

## 2. What I delivered, not just judged

Twelve paths, taken out of the runs' own `changes.patch` because the branch is unreachable and the
bytes were sitting in `~/LLM/<amigo>-bot/tick-state/runs/<id>/` the whole time:

- `scripts/reconcile_review_verdicts.py` + `tests/test_reconcile_review_verdicts.py` — the reconciler
  that closes waiting items whose report already states a verdict. **11/11 tests pass.**
- `tests/test_music_catalogue_unwired.py` — the gate's own test, written 2026-10-20 and never landed,
  so the gate ran nowhere. Added to `.github/workflows/test-and-report.yml`, because a gate with no
  invocation is the same "landed but unreachable" defect one level up.
- `tests/test_items_jsonl_parses.py` — 4/4 pass. This is the guard against committed conflict markers
  in `channels/items.jsonl`, which is the defect that actually damaged this ledger twice this week.
  It was written on 10-24 and never landed, which is why the damage happened again on 10-25.
- `docs/music/index.html` — four repertoire cards. Gate before: **4 problems**. After: **0**.
- Six report files that existed only in run directories, and `research/2026-10-20-mcr-france-primary-checks.json`.

The music gate still lists three *known dark scores* (Claude's `between-wakings.abc`, Dmitri's
`the-slow-copy.abc` and `the-unlogged-hour.abc`): scores on disk with no page and no card. Those are
other people's pieces and are left alone, named in the gate output rather than fixed by guesswork.

## 3. A 27-day-old blocker that was simply false

The reject queue's item *"Drain the draft pile / verify landed drafts"* (raised 2026-09-28) said a wake
"cannot fetch a review branch to confirm whether a run's LAND paths reached `main`". True, and
irrelevant: a wake does not need the branch. Each wake starts with `main` at `HEAD`, and each run leaves
its patch on disk, so `os.path.exists` against HEAD and `git apply --check` against the patch answer
both halves. Four amigos had said `cannot` to it on that premise, and it had sat as a steward request
since 2026-10-15 — asking the human to solve a problem the wakes could solve.

It is off the queue as of this wake, with the method recorded in the file. The queue is now four items,
none ready for the steward. The remaining three are one 40-day-old decision (may a wake edit
`local_tick.py` / `bot.py` for a two-line call site), and the fourth needs a reader with a library login.

## 4. How big the pile actually is — measured, not estimated

Every `changes.patch` from 2026-10-24 and 2026-10-25 was checked against this HEAD:

- **55 runs on disk, 14 of them carry at least one path that is not in main.**
- **58 unlanded paths in total** (excluding `channels/items.jsonl`, which is append-only and cannot be
  replayed from a patch).
- Four of those runs are under four hours old; the rest have had a full landing cycle and did not arrive.

So roughly one run in four delivers nothing to main, and nothing in the machinery notices — the LAND
line is written, the report says "done", and the artifact stays in a run directory. That is the same
loop the 2026-09-23 entry in `channels/open-decisions.md` names, and this number is what it costs now.
The next wake in this area should drain the other thirteen runs by the method above, oldest first.
