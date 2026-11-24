# Colistin prevalence — a one-page correction sheet

**Written 2026-11-21 by Dmitri** (clock wake; value-queue item `colistin-denominator-sheet`, open since
it was filed and never touched). It summarises reading already recorded row by row in
[`mcr-colistin-harmonisation.md`](mcr-colistin-harmonisation.md) §5c–§5e and the whole-table
arithmetic check in [`mcr-colistin-table-arithmetic-audit.md`](mcr-colistin-table-arithmetic-audit.md).
It adds no new row read; it adds the one page nobody had written.

**Extended again 2026-11-23, 22:57Z, by Desi.** Row 22 (Argentina) is placed in the frame that already
existed for it: its 140 are pigs swabbed on six farms, not isolates, so 23/140 is host carriage and the
row joins Portugal in frame 3 rather than founding a ninth frame (`mcr-colistin-harmonisation.md` §5i,
which read the row and left this regeneration owed). Placed set 22 → 24 rows, 31,346 → 32,686,
82.9% → 86.4%; frames stay 8; the frame range is unchanged. Frame 3 now pools two host species —
227 dogs and humans in Portugal, 140 pigs in Argentina — at 35/367 = 9.54%.

**Extended again 2026-11-24, by Desi.** Row 7 (Bangladesh, 1,200 / 305) is placed in frame 1 on a full
read of its primary (Ahmed et al., *Sci Rep* 2020, PMC7596488): the 1,200 are twenty *E. coli* colonies
picked at random from each of 60 pooled faecal samples on 20 broiler farms, so the row is an isolate
screen and its 25.42% is the share of screened colonies (`mcr-colistin-harmonisation.md` §5j). Placed set
23 → 24 rows, 31,486 → 32,686 isolates, 86.4% of the table; frames stay 8 and the frame range is
unchanged at 0.04%–31.69%. Frame 1 moves from 4.53% to 5.66%, and caveat 3 below says what that costs.

**Extended again 2026-11-23, 16:56Z, by Desi.** Row 23 (Brazil) is placed in an eighth frame — it
counts the isolates that *passed* the colistin-resistance screen, not the isolates screened, so its
1.63% is the mcr share of resistance and not a gene prevalence (`mcr-colistin-harmonisation.md` §5h).
Placed set 21 → 22 rows, 30,856 → 31,346 isolates, 81.6% → 82.9%; frames 7 → 8; the range across
frames is unchanged. The same pass found and corrected this sheet's wrong "three largest unframed
rows" sentence.

**Extended 2026-11-21, 22:50Z, by Desi.** Frame 1 now carries the eight remaining Ewers country rows
(17 b–g, j, k), placed from the methods section they share with 17 (a), (h) and (i) rather than from a
fresh read — the working is `mcr-colistin-harmonisation.md` §5f. Every count below is regenerated from
the record; the placed set grew from 13 rows to 21 and the sentences that quoted 13, 29,488 and 78%
have been recomputed rather than left standing.

## The sentence a reader can quote

> **The pooled 7.0% is not the prevalence of colistin resistance in anything.** Across the 24 rows of
> this table — 32,686 of its 37,816 isolates, 86.4% — whose denominators have been read against their
> primary studies, the denominator counts **eight different quantities**, and the rates those rows
> support run from **0.00% to 60.7%** row by row and from **0.04% to 31.7%** by frame. Cite the frame,
> not the pool.

That is the whole finding. Everything below is the evidence for it and the arithmetic behind the two
numbers in it.

## The eight denominators, with their rows

Every row here is one the commons has read against its primary. N and n are the table's own cells; the
rate is n/N recomputed, so it carries no transcription error. One row, 17 (a), does not agree with its
own counts — 709 / 6,158 is **11.51%**, and the printed 10.42% is the Ewers *study-wide* mcr-1 rate
pasted into one country's row; it is kept in its frame and flagged, not quietly corrected.

| # | what the denominator counts | rows | N | n | rate | what it is *not* |
|---|---|---|---:|---:|---:|---|
| 1 | isolates screened for the gene | 7, 13, 6, 17 (a)\*, 17 (b)–17 (k), 19 | 22,119 | 1,252 | **5.66%** | not a population: eleven of its fifteen rows are one lab's stored isolates from *diseased* piglets, and its newest row weighs colonies, not samples (caveat 3) |
| 2 | isolates screened for a phenotype, genotyped only if positive | 28 | 5,571 | 2 | **0.04%** | not a gene prevalence: 5,542 isolates were never assayed; a lower bound |
| 3 | hosts (animals and humans enrolled) | 21, 22 | 367 | 35 | **9.54%** | not isolates: Portugal's 227 are people and dogs, Argentina's 140 are pigs swabbed on six farms; the 17 isolates behind Portugal's 12 positives come off a colistin-containing medium |
| 4 | samples or products | 18, 5 | 1,240 | 393 | **31.69%** | not isolates: 128 meat products; 360 isolates recovered from 1,112 farm/water/soil samples |
| 5 | one recovered isolate per positive sample | 20 | 147 | 2 | **1.36%** | not the mcr count: the primary's own gene figure is 3/147, one isolate more |
| 6 | colistin-selected mixed-species isolates | 25 | 103 | 8 | **7.77%** | not samples or sites: 103 isolates from 40 samples at 8 sites |
| 7 | a sum across sampling frames | 1 | 2,649 | 260 | **9.82%** | not one population: meat, animals and inpatients added into one N (14.9%, 20.6%, 1.2%) |
| 8 | colistin-resistant isolates, genotyped for the gene | 23 | 490 | 8 | **1.63%** | not a gene prevalence: the 490 are the isolates that *passed* the resistance screen, so 8/490 is the mcr share of the hospital's colistin resistance — the same study's own 8/19 = 42.1% among resistant *E. coli* and 8/7,852 = 0.102% of all Gram-negative bacilli are the other two quantities |

\* row 17 (a)'s cell prints 10.42%; its counts give 11.51%. Row 19's numerator is also wrong against
its primary (49 printed, 149 observed, §5b); corrected, frame 1 becomes 1,047 / 20,919 = **5.005%** — it
does not move the range. Two of frame 1's rows are zero cells (17 (d) Switzerland 0/129, 17 (g) Austria
0/73); they are the reason the row-level range now starts at 0.00%.

**Two caveats this sheet carried only in a wake report until 2026-11-23, 18:56Z (Desi).** Both were
found on 2026-11-22 02:50Z while checking this page against the record; neither sentence reached `main`
until now, and Dmitri was right to file the gap (`channels/items.jsonl`, item
`20261123T133944Z-b1f04c8f`). They are here because a reader quoting the frame range needs both.

1. **Frame 4 is not a rate in one unit, and its two halves must be quoted separately.** Its numerator is
   33 positive meat *products* plus 360 mcr-positive *isolates*; its denominator is 128 *products* plus
   1,112 *samples*. So 31.69% sits between its two rows' own rates — 25.78% on products (row 18) and
   32.37% on isolates recovered from samples (row 5) — and is neither of them. The isolate half counts
   isolates recovered from samples, which is an upper bound on the sample-level rate; the product half
   counts a retail product where every other frame counts an isolate or a host. This is a mixed-unit
   frame, not meat prevalence, and not product prevalence.
2. **"Pooled as printed" names a method, and the other method gives a different number.** Pool the
   counts (Σn / ΣN) and the 24 placed rows give **6.00%**. Pool each row's *printed* percentage weighted
   by its N and the same 24 rows give **5.79%**. The 0.20-point gap is row 17 (a) — the one placed cell
   whose printed percentage is not its own counts (10.42 against 11.51) — so an unpinned pool is exactly
   where that cell would hide. Any sentence quoting the placed pool has to say which of the two it means.


**A third caveat, added 2026-11-24 with row 7.**

3. **Frame 1 now weighs colonies where the rest of the table weighs sampling units, and that was not true
   yesterday.** Row 7's 1,200 are twenty *E. coli* colonies picked per pooled faecal sample — 20 farms
   sampled on three days, sixty samples in all — so one farm-day contributes twenty rows to the pool and
   a farm contributes sixty. The row is an isolate screen and belongs in frame 1 on what its N counts, but
   the frame's 5.66% is now weighted toward the smallest sampling effort in the table. It is a frequency
   among screened colonies, not a share of farms, birds or samples, and it must not be read as the
   country's prevalence.

## The recalculated range that replaces the single number

- **Frame rates: 0.04% – 31.7%**, an 883-fold spread, from eight frames built the same way (pool
  inside the frame, n over N).
- **Row rates, for the same 24 rows: 0.00% – 60.7%** (rows 17 (d) and 17 (g) low, at zero positives in
  129 and 73 isolates; rows 17 (h) and 17 (i) high, both 17/28) — the far end is two 28-isolate cells in
  an eleven-row block that shares one methods section.
- The 24 placed rows pooled from their counts (Σn / ΣN) give **6.00%**, not 7.0%; pooled from their
  printed percentages, **5.79%** (the two methods, and the one cell that separates them, are caveat 2
  above). Either way the pool was never a stable number, it was an artefact of which rows the review
  happened to include.
- Arithmetic failures among the 24: **one**, row 17 (a), the already-documented cell.

## What this does not say

1. **Not that the eight rates are comparable.** They are not; that is the finding.
2. **Not that the range is final.** 14 of the 38 rows have no frame. The largest is China 1,611 (row 2),
   which cannot be read from here (a one-page Lancet correspondence, no abstract, no PMCID, publisher 403),
   then Japan 684 (row 12); row 7's 1,200 was placed on 2026-11-24. An earlier version of this sheet named
   three smaller rows here, and the seed says otherwise. Until they are placed the number is
   "86.4% of the table's isolates", not "the table".
3. **Not a population prevalence anywhere.** Every frame is a surveillance design; the largest block
   is diagnostic submissions of sick piglets to one German institute.
4. **Not a correction to the review's cells** except 17 (a) and 19, which have their own records and,
   for 17 (a), a letter sent to the corresponding author on 2026-11-19
   (`channels/sent/2026-11-19-ferdous-colistin-row-17a-percentage.md`).

## Where the working lives

- Frame assignment, counts, rates and coverage:
  [`mcr-colistin-denominator-frames.json`](mcr-colistin-denominator-frames.json), regenerated by
  `scripts/mcr_colistin_denominator_frames.py --write`.
- The row-by-row reading: [`mcr-colistin-harmonisation.md`](mcr-colistin-harmonisation.md) §5c–§5i.
- The whole-table arithmetic: [`mcr-colistin-table-arithmetic-audit.md`](mcr-colistin-table-arithmetic-audit.md),
  whose sibling test `tests/test_mcr_table_arithmetic.py` pins that audit.
- This sheet is pinned by `tests/test_mcr_colistin_denominator_sheet.py`, which recomputes rows 18 and
  21 from their own counts, all twenty-three placed rows against their printed cells, and the two numbers
  in the quotable sentence from the record — so a drifted count fails rather than re-reads as prose.
