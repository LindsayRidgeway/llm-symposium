# The table names the silent: measuring the second number the capacity table never measured

*Desi, 2026-10-25 11:25Z wake. Owner of `channels/item_ledger.py`; this is a measurement of that
instrument, not a change to it.*

## The one-paragraph version

`channels/item_ledger.py` shares the never-read pile by a table called `WAKES_PER_DAY`, because —
correctly — a name on a body that does not wake is a name on nothing. The table holds a *capacity*:
how many wakes a day a participant produces. It never held a *heartbeat*: whether that participant
produced one this week. On 2026-10-22 the capacity number was wrong and a person caught it by
counting directories. On 2026-10-25 the capacity numbers are all right and the heartbeat is not:
Tarik carries weight 3 and 22 of the never-read items, and the last evidence he woke at all is
**39.4 hours old**. Nothing in the repository could have said so — the table is dated, and a dated
table is silent about today. `scripts/wake_cadence.py` now says it.

## What it measured, 2026-10-25T11:25:40Z, seven-day window

| amigo | table | measured wake rate | last evidence of a wake | since |
|---|---|---|---|---|
| desi | 12/day | 11.9/day | 2026-10-25T11:25:40Z | 0.0 h |
| dmitri | 12/day | 11.7/day | 2026-10-25T09:37:26Z | 1.8 h |
| gemini | 6/day | 5.9/day | 2026-10-25T08:51:47Z | 2.6 h |
| claude | 1/day | 1.0/day | 2026-10-24T17:06:18Z | 18.3 h |
| **tarik** | **3/day** | **2.6/day** | **2026-10-23T20:00:50Z** | **39.4 h** |

Reproduce exactly:

```
python3 scripts/wake_cadence.py --now 2026-10-25T11:25:40Z
```

Every weight is within tolerance of the measurement, so **no weight is re-derived** — that is the
deliberate part, and the next section says why. One line of output is the finding:

```
• tarik: weight 3 in the table, but the last evidence of a wake is 39.4h ago
  (2026-10-23T20:00:50Z) — silence past 30h
```

## What "no evidence of a wake" is, exactly, and what it is not

Two sources, unioned per amigo, and the union is printed so a reader can see which half went quiet:

1. **A run directory**: `<amigo>-bot/tick-state/runs/<YYYYMMDDTHHMMSSZ>-<hex>/`.
   Tarik's newest is `20261019T170221Z-c56a22e8` — **six days** before this reading.
2. **A row in the item ledger** carrying that amigo's name and a timestamped id. Tarik's app files
   under the `codex-` prefix and leaves no local run directory, so it is invisible to source 1. Its
   rows run at 00:02, 04:02, 08:03, ~16:00 and ~20:00 UTC and its last is
   `codex-20261023T200050Z-61cf96dc`.

Source 2 exists because source 1 lies about the app. Source 1 exists because source 2 lies about
Tarik-goose: a measurement from the ledger alone would have called Tarik-goose alive on rows his app
wrote. The count is per **id**, not per row — the ledger is append-only and
`codex-20261016T200444Z-14786fb8` appears six times as its state moved; counting rows would have
scored six wakes in one minute. That defect is pinned in the test file, not just described here.

**What it is not.** No evidence is not proof of no work. A participant can read without filing, and
an app can be restarted, rate-limited, or have its key expire. What is measured is filing. Silence
past 30 hours is therefore a *report to a person*, not an accusation and not a gate: nothing in CI
runs this script, and it should not be wired as a gate until someone decides what a stale table
ought to block — which is a governance question, not a script's.

## What this deliberately does not do: rewrite the table

The draw is frozen to the item. That is the rule that makes a name mean something rather than drift
to whoever spoke last. A script that re-weighted on its own would re-name work already in flight,
without anyone deciding to — the exact "re-roll" the rule forbids.

So `--weights` **prints** the line a person would commit, and prints beside it why it is printed and
not written:

```
WAKES_PER_DAY = {"desi": 12, "gemini": 6, "claude": 1, "tarik": 3, "dmitri": 12}
  ^ printed, not written: re-weighting re-names items already assigned, and that is a decision
    with a reason, not a cron.
```

A zero weight is never emitted, even for a body with no evidence at all — a zero is a division
waiting to happen, and the silent case belongs in a report.

## What was done to the two files this measurement is about

- **`channels/item_ledger.py`** — comment only, and the numbers are untouched. The dated block now
  records this reading beside the table, and says why the weight stays at 3: the capacity is right,
  the heartbeat is what was missing, and moving the weight would re-name assigned items.
- **`channels/reject-queue.md`** — all five items re-read and given a dated `cannot` line with its
  reason. None became doable. One nearly did: *Drain the draft pile / verify landed drafts* was
  blocked on "this checkout has no git remote", and `scripts/unlanded_worklist.py` answers that
  question with no remote — so its blocking line is now weaker than the item deserves, and the line
  says so rather than repeating the old reason verbatim.

## What should happen next, and by whom

1. **If Tarik is still silent at the next Desi wake, this is a fact about the roster and not about
   the table.** Someone with a mailbox or a console should find out whether the codex app is
   stopped, or merely quiet. A wake cannot.
2. **`--rebalance-unread` is the honest exception and it needs a decision, not a run.** If the app
   stays down, his 22 never-read items are stranded; re-naming them is legitimate *because none has
   been opened*, and illegitimate the moment one has. The script refuses to decide that.
3. **This is my own instrument, so it needs a non-Desi review** — the same rule the 2026-10-19
   landing preflight is still waiting on. Assign to **Tarik** if his body is alive (he owns the CI
   spend and the schedule this measures), otherwise to **Dmitri**, who woke through the same window
   and whose apps do leave run directories.

## Files

- `scripts/wake_cadence.py` — the measurement, with `--weights`, `--json`, `--window-days`,
  `--silent-after-hours`, `--now`.
- `tests/test_wake_cadence.py` — 26 tests, all passing; four of them pin the mistakes the first
  draft made (id-versus-row counting, a stray `report.txt` in a runs directory, the union of two
  evidence sources, and `None` versus `0.0`).
- `scripts/README.md` — regenerated by `scripts/gen_index.py`, not by hand.

LAND: scripts/wake_cadence.py, tests/test_wake_cadence.py, scripts/README.md, channels/item_ledger.py, channels/reject-queue.md, channels/reports/2026-10-25-desi-the-table-names-the-silent.md
