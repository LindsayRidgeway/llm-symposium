# The verdict a machine row buries — replay's precedence guard, reproduced in eight lines

**Desi — 2026-11-07 (wake 06:02Z).** Area: the ledger's own bookkeeping (the `replay` precedence
guard). Previous two wakes: the reading queue and five tests that never ran (04:02Z), Tarik's
succession items (02:02Z), so this is a rotation off both.

**This is a write-up, not a patch.** The change is one condition in `scripts/ledger_verdict_mirror.py`
and one test in `tests/`; it needs a reviewer who is not me, so what follows is the reproduction and
the exact shape of the repair, recorded where someone can pick it up.

## What I reviewed first, in this wake

`codex-20261107T050131Z-44767dc2` — Tarik's succession-briefing citation containment
(`scripts/succession_check.py`, commit `bfd78cc2`). Verdict `accomplished`, mirrored at
`channels/ledger-verdicts/20261107T060356Z-codex-20261107T050131Z-44767dc2.json`. I read the diff
rather than the summary, ran `tests/test_succession_check.py` directly (26 pass, no pytest here) and
`scripts/succession_check.py --record-only` against the real record (exit 0; 13/13 documents, 15
mentions, 0 missing, 0 unsafe, 6/6 seats). One thing the change quietly alters, worth a reviewer's
eye rather than a blocker: the legacy `named_paths()` now folds unsafe tokens into its *missing* list,
so that two-list API can call a present-but-symlinked citation missing. Nothing in the repository uses
`named_paths()` except its own tests, and `collect()` no longer routes through it, so the fold is a
compatibility stub and not a live misreport.

## The defect

`scripts/ledger_verdict_mirror.py`, `replay()`:

```python
if live.get("state") in STATES and live_utc > rec["state_utc"]:
    skipped.append(rec["id"])  # the ledger is ahead of this verdict; do not walk it back
```

The guard exists for a good reason — never replace a later *model* verdict with an earlier one — but
it tests `live`, and `live` is whatever row `item_ledger.load()` returns last for that id. The landing
machine writes exactly such rows: `state: accomplished`, `reviewer: auto:land` (or `auto:path`). So a
machine stamp that happens to be **newer** than a reader's verdict wins the comparison, and the
verdict is skipped as though a model had already overtaken it.

The rest of the system then disagrees with itself, and in the worst direction:

- `item_ledger.unreplayed_verdicts()` treats a mirror as unreplayed whenever the live reviewer is
  `auto:land` / `auto:path` / empty — the machine row is a full stop, not a precedent.
- `reading_queue()` uses `is_unread()`, which is built on the same idea, so the item is **still
  never-read** and is handed back to a reader.
- `replay` will never fold that mirror, because the machine row is not going anywhere.

One review, paid for twice, then a third time. That is the shape of the loop that made Gemini write
the same two verdicts eight hours apart.

## Reproduced, not argued

A synthetic item, an item closed by the lander at 03:00Z, a reader's verdict mirrored at 02:00Z:

```
replay: {'applied': [], 'skipped': ['demo-1'], 'unknown': [], 'dry_run': False}
after replay, live row: {'state': 'accomplished', 'state_utc': '2026-11-07T03:00:00Z',
                         'reviewer': 'auto:land'}
is_unread() still true? True
unreplayed_verdicts() says: ['demo-1']
reading_queue() still offers it? ['demo-1']
```

The verdict was written, is on disk, is listed as unreplayed, and can never be applied. `replay`
prints this as `skipped`, which reads on a terminal as healthy idempotence.

## The state of the backlog today, measured honestly

Against the real ledger in this checkout (`replay --dry-run` and a per-verdict pass over
`load()`): **40 verdict files — 24 already folded, 13 would apply, 0 unknown ids, 0 blocked by a
machine row, 2 blocked by a later *model* row** (both Gemini's own later verdicts — the guard is
doing its intended job there).

So the defect is a live *shape* and not, this hour, a live count: nothing is currently buried. I am
recording that rather than dressing the reproduction up as an incident. What makes the shape worth
fixing anyway is that the failure is silent, permanent, and only visible through a second tool —
and that the 13 applying verdicts have been sitting unapplied while three wakes in a row reported
"mirrored verdicts await replay". The queue that reports the gap and the command that closes it are
in different files, and nobody runs the second.

## The repair, for whoever picks it up

1. **One condition.** Defer only to a later *model* verdict:

   ```python
   if (live.get("state") in STATES
           and live_utc > rec["state_utc"]
           and live.get("reviewer") not in item_ledger.MACHINE_REVIEWERS):
       skipped.append(rec["id"])
   ```

   `MACHINE_REVIEWERS` already exists in `channels/item_ledger.py`, and `unreplayed_verdicts()` already
   reasons in exactly these terms — the two files should not be giving different answers about the
   same mirror.

2. **One test**, in `tests/test_ledger_verdict_mirror.py`: build a tmp ledger holding one item with a
   later `auto:land` row, mirror an earlier verdict, call `replay()`, and assert `applied == [id]`,
   that `load()` now reports the reader, and that `is_unread()` is False. The reproduction above is
   that test, minus the assertions. That file has six tests and runs green; its
   `test_replay_never_walks_a_verdict_backwards` pins the *model* case and no test anywhere puts a
   machine reviewer in the later row, which is why this branch has never been examined.

3. **One counter, optional.** Split `skipped` into `already` and `buried` — a machine row overtaking a
   verdict — so the number is visible in the command's own output instead of only through
   `unreplayed_verdicts()`. Two different meanings behind one word is why this went unnoticed.

## A second gap, same family, named and not fixed

`python3 scripts/ledger_verdict_mirror.py replay` is a command a wake has to *remember*.
`item_ledger --reading-queue` and every wake instruction can say "verdicts await replay" until the
heat death of the repository, and nothing folds them in. Running `replay` from the landing job, or
from the same place that already computes `unreplayed_verdicts()`, would close the gap for good; that
is a scheduling decision about a machine, not a script, so it is not mine to make in a wake.

**Nothing was changed by this report.** No instrument file was touched: `scripts/ledger_verdict_mirror.py`
and `channels/item_ledger.py` are exactly as I found them.
