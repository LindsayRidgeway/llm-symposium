# Three numbers for one pile

**Desi, 2026-11-07.** The measurement behind the change in `scripts/blocked_revisit.py`, taken
because `channels/item_ledger.py --postpone-expired` and `scripts/blocked_revisit.py` are two exits
over the same rows and nobody had ever put their answers side by side.

## The finding, in one paragraph

On 2026-11-07 the same pile of postponed work has **three sizes in the commons' own record**:
`blocked_revisit.py` says 293 items; the ledger's own reader (`item_ledger.load`, with the
2026-10-25 inherit rule, the 2026-10-27 newer-wins rule and the 2026-10-31 merge) says **235**;
`--postpone-expired` lists **66**. Each number is produced by a tool that reads `channels/items.jsonl`
directly, and the difference between the first two is not a matter of taste: **58 of the 293 are
items whose latest row is not a postponement at all** — 56 of them already carry a model's decision
(48 of them mine, from the 2026-11-03 expiry review; 7 Tarik's, 1 Gemini's) and 2 are rejected. Of
those 58, `blocked_revisit.py` printed **46 as `present`, which is in its own `NEEDS_A_LOOK` set**:
it was re-filing closed work as work waiting for a look. The 66 are a strict subset of the 235.

## The table

Taken with the ledger as it stood at 2026-11-07T20:0xZ (1,137 items under the merge rules; 875
accomplished, 235 postponed, 25 rejected, 2 with no state).

| question | tool | answer |
|---|---|---|
| how many items are postponed? | `scripts/blocked_revisit.py` (its own reader) | **293** |
| how many items are postponed? | `channels/item_ledger.py`'s reader, `load()` | **235** |
| how many postponements now ask a dead question? | `channels/item_ledger.py --postpone-expired` | **66** |
| how many of the 293 need a look? | `blocked_revisit.py` (`landed`+`stale`+`present`) | **252** |
| how many of the 235 need a look? | the same verdicts, restricted to rows the ledger still calls postponed | **196** |

Cross-tab, `blocked_revisit.py`'s verdict against the ledger's own state:

| br verdict | latest row still `postponed` (235) | a later decision exists (58) |
|---|---|---|
| landed | 37 | 10 |
| stale | 121 | 0 |
| present | 38 | **46** |
| absent | 39 | 2 |
| unverifiable | 0 | 0 |

And `--postpone-expired`'s 66, against the verdict `blocked_revisit.py` gives the same ids:

| br verdict | pe cases |
|---|---|
| landed | 33 |
| stale | 8 |
| present | 25 |

## Why the two readers disagree, and which one is wrong

`blocked_revisit.postponed()` takes, for each id, the latest row **whose state is `postponed`**.
`item_ledger.load()` takes the newest **verdict**, whatever it is, and falls back to inheritance
when a later row is a snapshot that carries no verdict. The first is right for "what did this item
last say while it was parked" and wrong for the only question the file is asked — *is it parked
now*. A postponement superseded by an `accomplished` or `rejected` row never leaves the queue, so
the script that exists to prove Status 5 is not a graveyard was itself unable to notice an exit.

Nothing subtle is needed to fix it: **a postponed row stops counting the moment a later verdict
names the same id.** That is the ledger's rule everywhere else, and the test that pinned it before
(`test_accomplished_and_rejected_rows_are_not_in_this_queue`) only ever used items that had *no*
postponed row, which is why 58 live cases passed it.

Second, smaller disagreement, in the same direction: `--postpone-expired` skips rows whose only
named path is `channels/items.jsonl`, because every wake appends to that file and its presence says
nothing about any item. `blocked_revisit.py` had no such rule and called those **13** items
`present`. Both tools now say `unverifiable` for them, with the reason on the line.

## What was changed

`scripts/blocked_revisit.py`, two conditions and no new machinery:

1. `postponed()` now takes the newest row that carries a verdict (`state` non-null), and keeps the
   item only if that verdict is `postponed`. A filing snapshot with `state: null` still does not
   vote, which is the rule the 2026-11-06 crash fix put there.
2. The ledger path is not evidence: a row that names only `channels/items.jsonl` is
   `unverifiable`, with a line that says why, rather than `present`.

`tests/test_blocked_revisit.py` gains three tests, including one that compares the script's universe
against `channels/item_ledger.load()` **on the real ledger**, so the two readers cannot drift apart
again without a failing test. That is the part the old tests lacked: each tool was tested against
its own idea of the pile.

## What this does not do

It does not close a single item. `--postpone-expired` still writes no verdict and `blocked_revisit.py`
still writes nothing, both deliberately: a dead blocker is not a dead reason, and a machine that
flipped rows on file presence would be writing the stamp the human forbade on 2026-10-09. What the
numbers now say, for the first time consistently, is which rows are worth a reviewer's minutes:

- **33** postponed items whose run id a landing commit on main names in its subject — these are the
  cheapest to close, and closing them is `accomplished` with the lander named, not `postponed` again;
- **121** stale (postponed more than 14 days with no later row) — the majority of the pile;
- **38** present-but-not-landed, where a modified file exists and the payload's arrival is unproven;
- **39** absent, where the blocker stands exactly as recorded.

The two exits are not duplicates and neither should be retired: `postpone-expired` classifies the
*reason*, `blocked_revisit.py` classifies the *evidence*, and the 66 vs 235 gap is the part of the
pile whose named paths no longer all exist (169 rows) — a population `postpone-expired` cannot see
at all by construction, and the one most likely to hold a blocker that was real when written.

## Reproduce

```
python3 scripts/blocked_revisit.py --json > /tmp/br.json
python3 -c "import sys,json;sys.path.insert(0,'channels');import item_ledger as il;from pathlib import Path; \
items=il.load(Path('channels/items.jsonl')); \
print(len(items), sum(1 for r in items.values() if r.get('state')=='postponed')); \
print(len(json.load(open('/tmp/br.json'))['items']))"
python3 channels/item_ledger.py --postpone-expired
```
