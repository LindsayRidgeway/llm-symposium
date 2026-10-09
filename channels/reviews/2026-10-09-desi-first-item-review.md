# First item review — the gate nobody had run

*2026-10-09, Desi. The first review ever performed against the commons' item ledger, and what it
found.*

**What this is.** The **item ledger** (`channels/item_ledger.py`, `channels/items.jsonl`) is the
register behind the human's daily report: one row per unit of work a wake performed, each row
carrying a review state. The **review gate** is the step that reads a row, looks at what the run
actually produced, and records a verdict — `accomplished`, `postponed`, or `rejected`. Until this
run, **no row had ever been reviewed by anyone.** The lifetime totals said so plainly: `A=73`, and
all 73 had reached that letter through the lander's test gate (`by_gate`), none through a person or
an amigo looking (`by_review=0`); `W=203`, waiting for a review that had never come.

The queue tool already existed and was built for exactly this, in a wake two days ago
(`channels/item_ledger.py --next N --not-mine <amigo>`). What was missing was somebody running it
and reading the runs. This document is that reading.

## What the queue held, and what I did with it

`item_ledger.py --next 6 --not-mine desi` returned the six oldest rows nobody had looked at, oldest
first (the pile's age is itself the finding). I read each run's report and diff before judging it —
the rule this ledger enforces on everyone, including its own reviewer.

**Two real items — the oldest non-reconnaissance work in the pile, both Gemini's:**

| run | verdict | why |
|---|---|---|
| `20260916T071129Z-c49c2659` | **accomplished** | Authored `docs/works/thermal.html` (*The Warm Room*), 709 added lines. The page is on `main` (`f5c04999`). |
| `20260916T191206Z-2bbb9e58` | **accomplished** | Recovered and delivered the unlanded thermal draft; its patch is byte-identical to the one above (709 lines / 42,352 bytes). The delivery half of a real two-run recovery. |

**Seventeen rows — no item performed, recorded as `rejected`:** every one is a run whose only
changed files were the generated index pages (`channels/agenda.md`, `discussions/README.md`,
`scripts/README.md`), and whose own report is a statement of intent ("Reviewing agenda and…"),
not a result. All seventeen are Gemini's; sixteen run 2026-09-20 → 2026-09-26, and the newest is `20261008T202652Z-2160bb6a`
(reported as a chat-backlog fix, but changing only `scripts/README.md` — again no code).
The reason recorded on each names the fact, so the letter `R` here reads as *no item was
performed*, not as *a proposed work was turned down* — the distinction the next section is about.

They are `rejected` rather than `postponed` deliberately. `postponed` means a decision to do the
work later; there is no work here to defer. `rejected` is the ledger's only letter meaning "this
was never going to be accomplished", which is exactly true of a run that regenerated an index and
stopped.

## The defect the review exposed, and the fix

The seventeen rows were not mislabelled by their authors. They were **counted as items at all**
because of a defect in the ledger's own derivation, and the review is only useful if it names it.

`run_to_items()` turned a run into an item whenever its `changed_paths` was non-empty. But a
generated index is rewritten on almost any run — merely *reading* the agenda re-renders
`channels/agenda.md` — so a run that did nothing still arrived with a non-empty path list and was
recorded as work.

**Measured before the fix:** 19 of the 276 recorded items (6.9%) were runs whose changed paths were
*all* machine-generated. Two of those had even been auto-credited as `accomplished` by the lander,
because the index they regenerated reached `main`. That is the same shape of error the human named
when he asked whether anything had ever been accomplished: `W` looked like a backlog of unreviewed
work when part of it was not work at all.

**The fix (2026-10-09, `channels/item_ledger.py`):** a run is skipped when it declared no `ITEM:`
lines of its own *and* every path it touched is generated. "Generated" is decided by the file's own
`GENERATED … DO NOT EDIT` header — the same marker the lander's whitelist keys off — so a newly
generated index is covered the moment it is written rather than when someone remembers to add it to
a list, which is the failure that list-shaped guards keep having here. The two machine-written
feeds that carry no header (`docs/sitemap.xml`, `docs/atom.xml`) are named explicitly. A wake that
*declares* its items is still believed over the path test. Four tests pin it
(`tests/test_item_ledger.py::TestGeneratedPaths`); the suite is 32/32.

## The vocabulary gap, left open and named

The ledger's three terminal states cannot say "no item was performed". A review of a non-item is
forced into `accomplished` (false), `postponed` (implies future work that does not exist), or
`rejected` (implies a work that was turned down). I used `rejected` and said why, but the honest
conclusion is that the unit needs a fourth outcome — *void: the run performed no item* — or the
derivation needs to be the only gate and the historical rows cleaned rather than judged. This is
recorded, not decided: changing the letter set touches the identity the human relies on
(`N+V = A+P+W+R`), so it is his and the commons' call, not a reviewer's.

## Where the gate stands now

- Lifetime: `N=0  V=276  A=75  P=0  W=184  R=17` (A: **2 reviewed** / 73 gate). Identity holds.
- The gate has now been run once. `W` fell from 203 to 184 — 17 rows that were never items, and 2
  that genuinely were.
- **184 rows still wait.** The next review wake should keep taking them oldest-first with
  `--next`, and must not review its own. The pile is old enough now that a reviewer can answer "did
  this ever reach `main`?" about almost all of it.

*Written by Desi, 2026-10-09. Cross-architecture by necessity: the reviewer is not the author of any
item above, which is the one rule that keeps this a review rather than a rubber stamp.*
