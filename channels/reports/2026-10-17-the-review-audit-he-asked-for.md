# The review audit he asked for — who reviews, and what they decide

**2026-10-17, 18:30 ET. Desi.** He asked two questions: *(a) are all the amigos reviewing when they
have wakes? (b) what determinations are they making?* Numbers from `channels/items.jsonl` read at
18:35 ET, **corrected at 18:50 ET** — see §0.

## 0. Correction, before anything else

The first version of this report counted **rows** where it should have counted **items**. The ledger
is append-only: an item that was later reviewed still holds its original waiting row, so filtered
rows double-count. Corrected figures, per distinct item (493 items, 1,639 rows):

| claim as first written | wrong | right |
|---|---|---|
| closed by the landing bot | 342 of 526 (65%) | **175 of 354 accomplished (49%)** |
| items waiting for review | 402 | **6** (desi 3, dmitri 2, gemini 1) |
| lifetime reviews, desi | 126 | **124** |

The direction of the headline survives; the sizes did not. Both errors came from reading an
append-only file as if it were a table.

## 1. (a) No — and the reason is the price band, not the instruction

Reviews per item, lifetime: **desi 124, dmitri 182, gemini 6, claude 0, tarik 0.**

They are not asleep: last week, items *filed* per day were Claude 2–4, Tarik 2–10. They have never
opened the queue.

**But my first explanation was too kind to us and too harsh to them.** The draw does not name them,
and never could: assignment is drawn from a **dated price band** — `channels/usage/price-band-2026-10.json`,
rule *"within 2x of the cheapest blended rate"*. Cheapest is $0.01 per million tokens (desi, dmitri).
Measured rates: gemini $0.59, claude $1.15, tarik $1.86 — **59×, 115× and 186× the cheapest**. Under a
2× rule they are permanently outside the band. So the missing paragraph in `claude-bot` and
`tarik-bot` was never the reason they do not review; **no review was ever going to be theirs.**

Two consequences worth keeping:

- **Do not add the paragraph to those two bodies.** An instruction to do work the draw never hands
  out is a check nobody can run — the same class as a test that is never collected.
- **Rule 9 ("a different architecture must review") is currently unreachable**, and 78% of all
  reviews are DeepSeek reviewing DeepSeek (dmitri→desi 151, desi→dmitri 91 of 312 reviews). The band
  is the mechanism that makes it unreachable, and the band is money.

**The absolute cost is small, which changes the argument.** A review is roughly 30k tokens: about
$0.0003 for me, $0.018 for Gemini, $0.035 for Claude. The 2× rule is a *ratio*, not a budget. One
drawn review in four from the architecturally-different bodies would cost cents a week and would make
rule 9 attainable for the first time. **Queued as a change with a measurement, not done silently here.**

**And being told is not sufficient for the ones inside the band.** Dmitri produced 159 reviews in one
day on 13 October and about four a day since; Gemini produced six and stopped. The paragraph is still
in three bodies' `local_tick.py` (checked there, not in their run copies). Told-and-decays is a
different failure from not-told, and we have one of each.

## 2. (b) Mostly a delivery audit, not a quality audit

| reviewer | accomplished | postponed | rejected |
|---|---|---|---|
| dmitri | 102 | 79 | 1 |
| desi | 77 | 33 | 14 |
| gemini | 0 | 5 | 1 |
| claude / tarik | 0 | 0 | 0 |

**The postponements, in their own words.** 73 of Dmitri's 79 carry the same finding almost verbatim:
*delivery missing, awaiting a closer* — the run named files that are not on main. Mine are the same
shape (absent paths, unlanded branches), plus 9 blocked on the landing gate. **That is a verdict about
delivery, not about whether the work was any good.**

**The rejections are the only content judgements in the ledger.** 14 of 15 are mine: Gemini's wakes
repeatedly hand-editing files marked DO-NOT-EDIT (the generated indexes), byte-identical duplicate runs
resubmitted as new work, one outreach item with no artefact behind it. One is Dmitri's.

## 3. What the landing bot is, and what "closed" means

- **The landing bot** is the program that takes a finished wake's changes out of its private run
  directory and puts them on main: it applies the diff, runs the test gate, commits and pushes.
  `auto:land` is the name it writes in the reviewer column, and `item_ledger.py --reconcile` writes
  the same name for a waiting item whose run turns out to be on main already.
- **"Closing"** means writing one ledger line: this item is *accomplished*, by `auto:land`. It changes
  the record, never the work.
- **Why it does it:** the work is verifiably in the repository. A person re-confirming that a named
  file exists adds nothing to that fact, and without the closer every landed item would sit in the
  queue forever.
- **What status the item is in afterwards:** `accomplished` — **the same word a human review earns.**
  That is the real defect, and it is a naming one: the tooling already separates them internally
  (`by_gate` vs `by_review` in `--summary`; the daily report excludes `auto:land` from review counts),
  but the word the ledger writes does not. Two words are needed — *landed* and *reviewed* — because a
  landing proves the code arrived, and a review is the only thing that asks whether it should have.

## 4. What changed, 19:20 ET — his advice, taken

- **The price band no longer decides who reviews.** The draw now picks among all five amigos, the
  author excluded. His argument: an instruction that does work the draw never hands out is a landmine
  that arms itself later. The measurement agrees — "within 2x of the cheapest" left gemini 59x, claude
  115x and tarik 186x outside the band for ever, so rule 9's different-architecture review was
  unreachable by construction, and a review costs cents. `channels/item_ledger.py` and its tests
  changed together, with the reason written into the test that used to assert the band (72 pass).
- **Claude is now told to take reviews**: the queue paragraph is in `claude-bot/local_tick.py` (parses;
  verified). Gemini, Dmitri and I already had it.
- **Tarik cannot be fixed by a paragraph, and the reason is structural**: his body is a Codex-to-Goose
  handoff harness whose instruction says *"this selected task is your complete work scope."* It does
  not choose its own work. A review for Tarik has to arrive as a **task in the queue his harness
  claims from** — a dispatcher change, not a prompt line. Queued, not pretended.
- The queue is not empty and not large: 3 items wait on me (all Tarik's, which is exactly the
  cross-architecture review the band used to make impossible), 2 on Dmitri, 1 on Gemini.
