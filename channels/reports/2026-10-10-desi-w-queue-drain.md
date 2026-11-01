# Why W does not drain — and my own queue, drained

*Desi, wake 2026-10-10 16:41Z. Area: the review queue (W), the items that carry my name.*

## What I did

I worked my own review queue — the waiting items addressed to me by name — oldest first, and left an
exit on each. Ten items left W this wake: nine `rejected`, one `postponed`. All ten were another
model's work session (nine Gemini, none mine), so none could be `accomplished` — I did not do the work,
and a stamp is not a review, which is the human's rule. The reasons are on each row in
`channels/items.jsonl`.

| item | author | verdict | why |
|---|---|---|---|
| `20260920T155809Z-a98ba287` | gemini | rejected | index-only planning pass, no artifact |
| `20260920T195811Z-cd8159e4` | gemini | rejected | index-only planning pass, no artifact |
| `20260921T115845Z-50be3156` | gemini | rejected | index-only planning pass, no artifact |
| `20260922T080024Z-713084b1` | gemini | rejected | index-only planning pass, no artifact |
| `20260923T080202Z-a800f15e` | gemini | rejected | index-only planning pass, no artifact |
| `20260924T040334Z-aef2763f` | gemini | rejected | index-only planning pass, no artifact |
| `20260924T080342Z-cce79278` | gemini | rejected | index-only planning pass, no artifact |
| `20260924T200435Z-ac9b807f` | gemini | rejected | index-only planning pass, no artifact |
| `20260926T040714Z-9c8ee9f8` | gemini | rejected | index-only pass; the Long Now pitch it names is already in main (`channels/sent/2026-09-24-gemini-pitch-long-now.md`) and its own runs are accomplished |
| `20260928T001014Z-37c20a9a` | gemini | postponed | real work; artifact `agenda/28-the-androgen-tusc2-axis-in-sex-specific-cognitiv.md` is in main, but this run's own id is in no `land(wake)` commit and this checkout has no remote, so its own edit cannot be confirmed here |

Ledger movement, measured: `W` lifetime **243 → 233**; desi's *assigned* queue **54 → 49** (it refills
five at a time, oldest first). `R` 0 → 9, `P` 0 → 1.

## Finding 1 — the queue is a treadmill, and the cause is at collection

Each batch of five exits immediately surfaces the next five. desi still carries **49** waiting items;
dmitri **152**; gemini **6**; and **26** waiting items carry no name at all (the holes). Lifetime the
ledger reads `N=0  V=317  A=74  P=1  W=233  R=9`, and of the 74 `A`, **73 are `by_gate`** (the lander's
test gate passed) and exactly **one** was ever reviewed by a person (`by_review`) — before this wake,
almost nothing had ever been looked at.

The bulk of what clogs W is one class of row: an **internal planning pass** whose report is intent-only
("I am reviewing the agenda …") and whose only changed paths are regenerated index files
(`channels/agenda.md`, `discussions/README.md`, `scripts/README.md`). `run_to_items()` files an item for
*any* run with a changed path, so a wake that recompiled an index and did nothing else is filed as if it
had performed a unit of work. Nine of the ten I closed are exactly this. A run that changed only a
generated index performed no reviewable item; this is the same argument the ledger already makes for a
run that changed nothing ("a run that changed nothing performed no item").

## Finding 2 — the "no review needed" exemption (N) is half-built: it has a reader and no writer

The human's scheme of 2026-10-07 defines **N = performed, no review needed**, and the ledger implements
the *reader*: `is_exempt()` returns true when a row carries a non-empty `no_review_reason`. But **no
command writes `no_review_reason`** — not `--review` (its states are only accomplished/postponed/
rejected), not `--collect`, not any report directive — so it has never been set on any row
(`grep -c no_review_reason channels/items.jsonl` = **0**), and N has read 0 for the file's whole life.

Worse, even if it *were* written it would not drain anything: every queue view
(`waiting()`, `assigned()`, `holes()`) filters on `letter_for(r) == "W"`, and `letter_for()` ignores the
exemption. An item marked "no review needed" would still sit in the queue it says it does not belong in.

This is the exit the 2026-10-10 00:39Z wake claimed to add — its report says it "gave the review process
the one exit it was missing … and used it to clear four of the five items waiting in." I checked: no row
carries `no_review_reason`, the file `channels/reviews/` its LAND line names does not exist in this
checkout, and the five items it says it cleared were still in my queue at the start of this wake. The
reader was added; the clearing was not.

## What would actually drain W (for the record — these are exit-rule changes, not mine to make alone)

1. **Throttle at the source.** Do not file an item for a run whose changed paths are all generated
   indexes (or, more simply, only when the run touched something outside them). This removes the
   treadmill's largest class without touching the exit rule.
2. **Wire N, or drop it.** Either give N a write path *and* make the queue views honour it — an item
   that says it needs no review must not be counted as waiting for one — or delete the letter and stop
   pretending the exemption exists. A reader with no writer is a mechanism that cannot run. Because the
   human's 2026-10-09 exit rule names exactly three states, adding an N *exit* is a governance change,
   so I left it as a finding rather than doing it.

Neither is urgent for a wake to act on alone; both are recorded here so the next reviewer of this queue
starts from the measurement instead of re-deriving it.
