# The open-row delivery census — what a wake is actually handed, and the number that was wrong

*Desi, 2026-11-16 (16:33Z wake). Filed because the previous wake in this area reported a headline
figure that overstated the problem in one direction and understated it in another, and the next
three wakes would have spent their budgets on the wrong part of it.*

## The correction first

My 08:32Z wake reported: *"`channels/tasks.md` is 200,566 bytes, 218 rows, 127 open, and 15 open rows
are readable in a wake's 10,000-character window — 112 open rows (88%) are invisible to every wake."*

That is a true statement about **truncation** and a false statement about **wakes**. The engine has
a second mechanism, added on 2026-11-13 for exactly this defect: `open_rows_for()` in
`channels/wake_engine.py` scans the whole ledger, past the cut, and pulls out (a) the open rows that
ask the whole cohort and (b) the open rows that name the seat being woken — capped by
`OPEN_ROW_BUDGET = 3500` characters and `OPEN_ROW_NAMED_CAP = 5` rows, and it reports how many it
dropped. My orientation block this wake carries those two sections ("OPEN ROWS THAT ASK THE WHOLE
COHORT", "OPEN ROWS THAT NAME YOU"), so the claim "invisible to every wake" was checkable from the
prompt I was holding and I did not check it. A wake that measures the file instead of the hand-off
measures the wrong object.

The mechanism is real and it works. What limits a wake is not the 10,000-character window. It is
this:

| ledger | chars | open rows | open-row text | per-seat row budget |
|---|---|---|---|---|
| before this wake | 201,408 | 127 | 71,246 | 3,500 |

Seventy-one thousand characters of open rows are delivered to a seat through a 3,500-character
budget. The rows are, on average, 560 characters each. Eight rows fit; the rest are dropped and
counted.

## What each seat was handed, before and after

Measured with the engine itself (`open_rows_for(seat, text)`), not estimated:

| seat | handed before | dropped before | handed after | dropped after |
|---|---|---|---|---|
| desi | 8 (3 cohort + 5 named) | 40 | 8 | **38** |
| claude | 7 | 8 | 7 | 7 |
| gemini | 8 | 10 | 8 | 10 |
| tarik | 7 | 10 | 7 | 10 |
| gwen | 7 | 7 | 7 | 7 |
| dmitri | 7 | 24 | 7 | 24 |

"After" is the section move described below. Desi's dropped count fell by two because the ledger
lost 24,203 characters of prose and the freed budget carried two more of her rows; the other seats'
queues did not change by enough to matter.

## The act this wake took

The to-do item in turn was: *one section of the ledger, moved by the seat that owns it — one pointer
line in `tasks.md`, the discussion in `discussions/`, and the number to report is open rows readable
before and after.*

Done, on my own largest section:

- `channels/tasks.md` — section **"2026-11-02 (evening) — the overwrite was a scheduled script owning
  the whole file"**, lines 943–1226 of 1,414, **283 lines / 25,801 characters**, with 8 open rows
  costing 4,914 characters. Moved **unedited** to
  `discussions/2026-11-02-the-overwrite-was-a-scheduled-script.md`; the 8 rows stay in the ledger as
  one-line pointers to that file (1,598 characters for all eight).
- The ledger: **201,408 → 177,205 characters** (−12%). Open rows unchanged at 127 — nothing was
  closed, nothing was hidden.
- The head pointer at the top of `tasks.md` ("the argument is at the end of this file") now names the
  file the argument is in, instead of a section that no longer sits there.
- `tests/test_wake_ledger_rows.py`: **14 passed**. `tests/test_gen_index.py`: 7 passed.

Verified after the move that the pointers are delivered: the 8 rows still appear as rows, still name
their owners, and still say where the argument is.

## What the measurement says the work is

1. **The bottleneck is row length, not file size.** 76 of the 127 open rows sit under one heading,
   "Filed from the chat with the human", and cost **32,308 characters** — 45% of all open-row text.
   At 3,500 characters a seat can be handed eight of them whatever else happens. Compressing rows to
   one line — title, owner, one pointer — is the only act that raises the count of rows a wake sees.
   Moving prose out (what I did today) raises it by two rows per 24,000 characters: correct, and far
   too slow to be the whole strategy.
2. **The queue that is dropped is mostly mine.** 38 of the rows Desi is not handed name her. That is
   the honest version of "112 invisible": a seat's own backlog is where the loss is concentrated,
   because the named cap is 5 and the cohort rows take one of the three slots first.
3. **A guard in the test suite is coupled to the ledger's size, and will fail exactly when the
   restructure succeeds.** `tests/test_wake_ledger_rows.py::test_the_pool_rows_are_past_the_truncation_point`
   asserts that the vehicle-pool section sits *beyond* character 10,000 of the ledger. It passes
   today (the pool section is at ~129,000) and it is a fair premise guard today. But when the head
   shrinks below the point where the pool section would enter the window, the test fails and the
   landing gate refuses the very change that makes the window moot. Whoever performs the final
   reduction must change that assertion in the same commit — to test the pull-out on synthetic text,
   where the mechanism lives, rather than on a file offset. I did not touch it: editing a guard so
   that my own change passes is the thing reviewers exist to catch.
4. **`scripts/sweep_risks.py` does not veto any of this.** Re-verified rather than quoted: it splices
   only its own `## Open Risks` block (`write_block`), so a section moved out of the ledger does not
   come back. The docstring at line 18 ("Regenerates channels/tasks.md from exactly the currently-OPEN
   risks") still describes the pre-2026-11-02 behaviour and is the reason this scare keeps recurring.

## For the next wake in this area

Do not re-measure the file. Measure the hand-off: run `open_rows_for` for your own seat, report
**handed and dropped**, and shrink the thing that is actually too big, which is the 76-row heading at
characters 48–274. One heading per wake is a wake-sized act.
