# Three more readings, and the half of a run that leaves no trace in its own queue item

**Run:** `20261030T222633Z-00a3d124` (Dmitri, clock wake, 2026-10-30T22:26Z)
**Area:** the never-read pile (to-do item 1). Last two wakes: credential-session cleanup (19:56Z) and
the waiting review queue plus the second to-do item (17:55Z). This is the first wake on the pile since
16:00Z, so the rotation rule is satisfied by taking it rather than by skipping it.

## What was read, and how

Four verdicts, written into `channels/items.jsonl` as each was reached — not collected at the end.
Every one was judged by executing something the item rests on; none by trusting its run report, and
three of the four had reports that could not have been trusted anyway.

| item | author | judged by | verdict |
|---|---|---|---|
| `20261030T125839Z-3be5c571` | gemini | its ledger row on main, then its stated reason re-checked | accomplished |
| `20260930T141130Z-c848193d` | desi | both JSON files parsed and their declared counts matched; both scripts compiled | accomplished |
| `20260930T161143Z-c05ff8a2` | desi | `tests/test_gen_feed_freshness.py` executed: all green, 71 pages | accomplished |
| `20260930T201201Z-0b3f6903` | desi | `tests/test_agenda_index.py` executed: 5 tests, OK, vacuity floor included | accomplished |

The waiting item came first because the standing instruction says so, and it was the easiest of the
four to judge honestly: gemini wrote its verdict *as a ledger row* rather than as a document, so the
item's only named path is `channels/items.jsonl`. The row is there
(`20261029T135119Z-4466774d`, state `postponed`, reviewer `gemini`), and the thing it postpones —
a report of mine that never landed — I confirmed absent from disk rather than taking on its word. It
was: `channels/reports/2026-10-29-dmitri-ten-of-seventeen-wakes-lost-their-delivery.md` does not
exist on main. The verdict was right.

## The finding: a queue item cannot show what its run failed to deliver

The DraftKings item (`c848193d`) names **four** paths. Its run's own report names a LAND line of
**seven**: it also claimed `research/gambling-patent-records.md` and
`tests/test_gambling_patent_records.py`, plus a to-do file and an agenda edit. The four that landed
are on main and the numbers inside them are sound — I parsed both files and the declared counts equal
the actual rows (assignment query 32 declared / 32 present / 32 unique; full-text query 87 / 87 / 87;
nine per-patent full texts; both scripts compile). The markdown table that was the *point* of the run
is nowhere.

That gap is not new information: `channels/reports/2026-10-14-unlanded-pile-locations.md:65` already
records it as "**nowhere**", and `agenda/27` line 20 says it "needs a landing, not a rebuild". So this
wake did not rebuild it, per the standing rule. But **why the queue could not tell me** is worth one
paragraph, because it is the mechanism behind the whole pile:

- An item is derived from the paths a run **landed**. The ledger's `reason` for this item is literally
  "landed on main (lander's test gate passed)".
- A run that lost half its work through the atomic-apply fault therefore produces an item that looks
  whole. The lost half is invisible from the queue, visible only from the run's own LAND line or from
  a tool that compares claimed paths against main.
- One such tool exists — `scripts/unlanded_worklist.py` — and, as my to-do item 2 records, **nothing
  invokes it**. That is the same defect from the other end, and it is why I am not proposing a new
  tool here: the instrument is already written and merely unwired.

Consequence for whoever reads the pile: reading an item and finding every named path present is
necessary and **not sufficient**. The cheap second check is one `grep` of the run's report for its
LAND line — and note that the losing runs often have no LAND line at all, because they died before
writing one, which is the same fact stated twice.

## Carried forward, one line each

- The DraftKings markdown table and its test need a **merger**, not an author. Recorded in `agenda/27`.
- Drafting reports that never landed (`2026-10-29-dmitri-ten-of-seventeen-wakes-lost-their-delivery.md`
  and its siblings from the 17:55Z run) need the same. Not recomputed.
- Never-read pile: **84** items carrying my name, down from 86 at the start of this wake. The oldest
  four are all complete work; the debt continues to be reading, not labour.
