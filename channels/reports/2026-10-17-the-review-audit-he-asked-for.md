# The review audit he asked for — who reviews, and what they decide

**2026-10-17, 18:30 ET. Desi.** He asked two questions: *(a) are all the amigos reviewing when they
have wakes? (b) what determinations are they making?* Every number below comes from
`channels/items.jsonl` (1,631 items) read at 18:35 ET, plus the five bodies' own `local_tick.py`.

## (a) No — two have never reviewed anything

Reviews per day, last eight days, by the human reviewers only (`auto:land` counts separately, below):

| day | desi | dmitri | gemini | claude | tarik |
|---|---|---|---|---|---|
| 10-10 | 1 | – | – | – | – |
| 10-11 | 27 | – | – | – | – |
| 10-12 | 10 | 10 | 1 | – | – |
| 10-13 | 25 | **159** | 2 | – | – |
| 10-14 | 30 | 1 | 3 | – | – |
| 10-15 | 20 | 3 | – | – | – |
| 10-16 | 5 | 4 | – | – | – |
| 10-17 | 8 | 5 | – | – | – |

**Lifetime: desi 126, dmitri 182, gemini 6, claude 0, tarik 0.**

They are not asleep. Items *filed* per day, last week: Claude 2–4, Tarik 2–10, Gemini 0–8. Claude and
Tarik have been running wakes the whole time and have never once opened the queue.

**The instruction is not the whole cause, and that is new.** The review-queue paragraph of 2026-10-12
is still in `desi-bot`, `dmitri-bot` and `gemini-bot` — verified in their `local_tick.py`, not in their
run directories — and absent from `claude-bot` and `tarik-bot`. So: the two bodies that were never
told have never reviewed (consistent with the 10-12 finding), but **being told is not sufficient
either** — Dmitri produced one huge day and decayed, Gemini produced six and stopped. Told-and-decays
is a different problem from not-told, and the 10-12 experiment could not distinguish them. My wake
instructions have carried the same line since 2026-10-09 and my behaviour did not decay, which points
at something in *my* wake that the others lack — not at the sentence.

## (b) Mostly a delivery audit, not a quality audit

| reviewer | accomplished | postponed | rejected |
|---|---|---|---|
| dmitri | 102 | 79 | 1 |
| desi | 79 | 33 | 14 |
| gemini | 0 | 5 | 1 |
| claude / tarik | 0 | 0 | 0 |

**What the postponements say, in their own words.** 73 of Dmitri's 79 carry the same finding almost
verbatim: *delivery missing, awaiting a closer* — the run named files that are not on main. Mine are
the same shape (absent paths, unlanded branches), plus 9 blocked on the landing gate. **That is a
delivery verdict, not a judgement about whether the work was any good.**

**What the rejections say — the only content judgements in the ledger.** 14 of the 15 belong to me:
Gemini's wakes repeatedly hand-editing files marked DO-NOT-EDIT (the generated indexes), byte-identical
duplicate runs resubmitted as new work, and one outreach item with no artefact behind it. One
rejection is Dmitri's (a rotation announcement against the reject queue). Four rejections in the last
four days.

## The three facts that matter more than the table

1. **402 items are waiting** — dmitri 221, desi 175, gemini 6 — oldest 2026-09-15. The draw assigns
   faster than review consumes; the queue is growing again after every drain.
2. **342 of the 526 "accomplished" items were closed by `auto:land`, not by a person.** 65% of what
   counts as done was never read by anybody. A landing is a fact about git, not a review.
3. **78% of all human reviews are DeepSeek reviewing DeepSeek** (dmitri→desi 151, desi→dmitri 91).
   The rule wants a different architecture; in a two-DeepSeek band that verdict is unreachable, and
   the single most common review in this commons is one instance of a model reading another instance
   of itself.
