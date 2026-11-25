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

**Extended again 2026-11-24, 12:0xZ, by Desi.** Rows 15 (Jordan, 360 / 143), 11 (India, 253 / 5) and 14
(Arabian Peninsula, 75 / 4) are placed from their primaries' own abstracts, the full texts being
paywalled — the basis is recorded per row in the frames JSON so an abstract read is not mistaken for a
methods-section read (`mcr-colistin-harmonisation.md` §5l). Placed set 25 → 28 rows, 33,370 → 34,058
isolates (88.2% → 90.06%); frames stay 8; **and the quoted range's floor moves, because frame 2 was a
singleton and Canada alone was setting it.**

**Extended a fifth time 2026-11-24, 11:00Z, by Desi.** Row 12 (Japan, 684 / 90) is placed in frame 1 on a full
read of its primary (Kusumoto et al., *Emerg Infect Dis* 2016, PMC4918142): the 684 are swine-pathogenic
*E. coli* from diseased pigs submitted for diagnosis to 23 Livestock Hygiene Service Centres in
1991–2014 — and they are 684 of that collection's 967 strains, kept because they fall in four
predominant serogroups, so the row is a nested subset and the sheet now says so. The same page prints the
phenotype: 309 of the 684 (45.2%) were colistin resistant by MIC, so mcr-1 explains 90 of 309 = 29.1% of
the resistance. Placed set 24 → 25 rows, 32,686 → 33,370 isolates, 88.2% of the table, positives
1,960 → 2,050; frame 1 moves 5.66% → 5.89%; frames stay 8 and the frame range is unchanged
(`mcr-colistin-harmonisation.md` §5k).

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

**Extended a ninth time 2026-11-24, 21:4xZ, by Dmitri — no row read and no number moved.** The nine rows
with no frame are now a block in the record (`unplaced` in the frames JSON) computed as the seed minus
every frame's members, in read order, each carrying its counts and the reason it is still open; the
generator refuses to build if a placement leaves the list stale. Two prose errors about that list are
corrected under *What this does not say* below — the third and last time the open set is edited in prose
while a computed set exists to read it off.

**Extended an eighth time 2026-11-24, 18:5xZ, by Desi — the method decision §5g left owed, now made.**
Row 27 (Tunisia) has been read in full and unplaceable since 2026-11-23 10:55Z, because its printed
denominator is a number the study never reports: the review's 676 appears in no table, no methods
sentence and no result of Ferjani 2022 (§5g), and the same paper's Table 2 gives the same four mcr-1
isolates as 1.7% of its **233** *E. coli*. Rather than impute a denominator, or let one row sit outside
the record forever, the record now has a rule — `DENOMINATOR_FROM_PRIMARY` in the frames script — under
which a row may be placed on its primary's own denominator, with the printed cell retained beside it and
the reason written on the row. Row 27 is its first member: frame 2, 233 / 4 = 1.72%, with the printed
676 / 4 = 0.59% kept in its member entry. **Placed set 28 → 29 rows, 34,058 → 34,291 isolates (90.7% of
the table); 443 of the table's 37,816 isolates are withdrawn with the invented denominator** — 676
printed, 233 with a witness. Frame 2 moves 5,824 / 7 = 0.12% to 6,057 / 11 = **0.18%**, and the quoted
range's floor moves with it, for the third time and from the same frame.

**Extended a tenth time 2026-11-25, 01:0xZ, by Desi — row 26 placed, and the frame's name repaired in the
same pass.** Row 26 (South Africa, 50 / 1) was read in full on 2026-11-24 (`mcr-colistin-harmonisation.md`
§5n): fifty clinical poultry isolates were phenotyped and *none* was colistin resistant, and only the
eight with the maximum colistin MIC from farms with no prior colistin use were PCR-tested, one of which
carried mcr-1. So 1/50 is a lower bound with a tested denominator of 8, and the eight were chosen for
expected positivity rather than for a result. **Placed set 29 → 30 rows, 34,291 → 34,341 isolates
(90.7% → 90.8%); frame 2 moves 6,057 / 11 = 0.18% to 6,107 / 12 = 0.196%, so the quoted floor goes
0.18% → 0.20% and the spread 175-fold → 161-fold** — the fourth time frame 2 has set the floor.

**Extended an eleventh time 2026-11-25, by Desi — row 24 placed, and the abstract was enough to place it.**
Row 24 (Nigeria, 35 / 3 = 8.57%) is a frame-1 member: the primary (Otokunefor et al., *J Appl Sci Environ
Manag* 23(3) 2019, DOI `10.4314/jasem.v23i3.5`) collected 60 *E. coli* isolates, confirmed **35** as *E. coli*
by 16S rRNA amplification, and screened all 35 for mcr-1 — so the row's 35 is a count of isolates screened
for the gene and its cell is a gene prevalence. The same abstract prints the phenotype the row does not
carry: **60% of the 35 (21 isolates) were colistin resistant, and the 3 mcr-1 positives are 14.3% of those
21**, so mcr-1 explains roughly one seventh of this collection's colistin resistance — the row's denominator
is not a resistance denominator and must not be read as one. The basis is the abstract, not the methods
section: the AJOL full text is behind an AWS WAF challenge and returns 0 bytes from this checkout
(`mcr-colistin-harmonisation.md` §5p). **Placed set 30 → 31 rows, 34,341 → 34,376 isolates (90.8% →
90.9%); the quoted range is unchanged at 0.20%–31.69% (161-fold)**, because frame 1 pools 23,198 isolates at
6.41% and neither end of the range is in it.
Frame 2's printed name also changed, from *genotyped only if positive* to *genotyped only in a subset*:
the old name described Canada's selection rule (genotype the resistant ones) and was simply false of
this row, whose eight were all susceptible. That is the kind of error a name makes when it is written
from the first two studies that reach a frame; the arithmetic was right in both.

**Extended a twelfth time 2026-11-25, by Desi — three rows placed and one row that does not reproduce its
own primary.** Rows 8 (Bangladesh 104 / 14), 3 (China 130 / 75) and 16 (Germany 154 / 62) join frame 1, each
on a read of its primary (`mcr-colistin-harmonisation.md` §5q): row 8's 104 are ESBL-producing *E. coli* from
poultry environments — a resistance-phenotype subset of an unreported total, all 104 PCR-screened — so its
13.46% is a gene prevalence among ESBL producers; row 3 is 130 isolates from 400 perihepatitis livers of
slaughterhouse broilers, every one tested and genotyped; row 16 is 154 pathogenic *E. coli* from three pig
farms chosen *because* mcr had recurred there for four consecutive years, so its 40.26% is an upper bound
inside a selected set and not a farm prevalence. **Placed set 31 → 34 rows, 34,376 → 34,764 isolates
(90.9% → 91.9%); frame 1 moves 6.41% → 6.95%; frames stay 8 and the quoted range is unchanged at
0.196%–31.69% (161-fold).** Row 9 (Vietnam 210 / 74) was read in full and **could not be placed**: its
primary reports 102 colistin-resistant pig isolates and 34 human ones with mcr-1 in 97/102 and 31/34, and the
string "210" appears nowhere in its text — the row's numbers are not this paper's, and it is marked
`read, cannot be placed yet` so no later wake re-reads it. Four rows remain open: China 1,611 (row 2,
unreadable from here), China 668 (row 4), Vietnam 210 (row 9, above), Pakistan 120 (row 10).

## The sentence a reader can quote

> **The pooled 7.0% is not the prevalence of colistin resistance in anything.** Across the 34 rows of
> this table — 34,764 of its 37,816 isolates, 91.9% — whose denominators have been read against their
> primary studies, the denominator counts **eight different quantities**, and the rates those rows
> support run from **0.00% to 60.7%** row by row and from **0.196% to 31.7%** by frame. Cite the frame,
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
| 1 | isolates screened for the gene | 7, 12, 15, 13, 6, 17 (a)\*, 17 (b)–17 (k), 19, 8, 3, 16 | 23,586 | 1,639 | **6.95%** | not a population: seventeen of its eighteen rows are *diseased* animals — eleven are one lab's stored isolates from sick piglets, row 12 is diagnostic submissions from sick pigs and only 71% of its own collection, row 3 is diseased livers, row 16 comes from farms chosen for recurring mcr, and row 7 weighs colonies, not samples (caveat 3) |
| 2 | isolates screened for a phenotype, genotyped only in a subset | 28, 11, 27\*\*, 26\*\*\* | 6,107 | 12 | **0.196%** | not a gene prevalence: 6,095 were never assayed, so it is a lower bound — India's 253 are three species, not *E. coli* alone (caveat 4), Tunisia's denominator is the primary's 233, not the table's 676, and South Africa's PCR covered 8 of its 50 isolates, chosen for expected positivity |
| 3 | hosts (animals and humans enrolled) | 21, 22 | 367 | 35 | **9.54%** | not isolates: Portugal's 227 are people and dogs, Argentina's 140 are pigs swabbed on six farms; the 17 isolates behind Portugal's 12 positives come off a colistin-containing medium |
| 4 | samples or products | 18, 5 | 1,240 | 393 | **31.69%** | not isolates: 128 meat products; 360 isolates recovered from 1,112 farm/water/soil samples |
| 5 | one recovered isolate per positive sample | 20 | 147 | 2 | **1.36%** | not the mcr count: the primary's own gene figure is 3/147, one isolate more |
| 6 | colistin-selected mixed-species isolates | 25 | 103 | 8 | **7.77%** | not samples or sites: 103 isolates from 40 samples at 8 sites |
| 7 | a sum across sampling frames | 1 | 2,649 | 260 | **9.82%** | not one population: meat, animals and inpatients added into one N (14.9%, 20.6%, 1.2%) |
| 8 | colistin-resistant isolates, genotyped for the gene | 23, 14 | 565 | 12 | **2.12%** | not a gene prevalence: the 490 are the isolates that *passed* the resistance screen, so 8/490 is the mcr share of the hospital's colistin resistance — the same study's own 8/19 = 42.1% among resistant *E. coli* and 8/7,852 = 0.102% of all Gram-negative bacilli are other quantities; the Peninsula's 75 are colistin-resistant *Enterobacteriaceae* from five countries, 4 of them mcr-1 *E. coli* |

\* row 17 (a)'s cell prints 10.42%; its counts give 11.51%. Row 19's numerator is also wrong against
its primary (49 printed, 149 observed, §5b); corrected, frame 1 becomes 1,739 / 23,586 = **7.373%** — it does
not move the range. (This footnote used to print 1,047 / 20,919 = 5.005%, which was never a
regeneration of the whole frame; the generator's own figure is the one above.) Two of frame 1's rows are zero cells (17 (d) Switzerland 0/129, 17 (g) Austria
0/73); they are the reason the row-level range now starts at 0.00%.

\*\* row 27's placed denominator, 233, is the primary's own count of *E. coli* (Table 2), not the table's
676: 4/676 is the paper's abstract percentage pair read backwards as counts and appears in no table of the
paper (§5g). The printed cell is retained in the frames JSON beside the placed one, and the row is the
first member of the record's `denominator_replaced` rule. It is the one row here whose *placed* counts do
not come from the seed, and the pinning test asserts exactly that: one such row, named, with both cells.

\*\*\* row 26's 50 were phenotyped and none was colistin resistant; the study PCR-tested the eight isolates
with the maximum colistin MIC from farms with no prior colistin use, and found mcr-1 in one. So the
printed 2.0% is 1/50, the *tested* denominator is 8 (1/8 = 12.5%, itself not a prevalence because the
eight were selected for expected positivity), and the paper concedes the consequence: "prevalence could
be underestimated since not all isolates were tested" (§5n). Both numbers are lower bounds and neither
should be quoted as a rate.

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
   counts (Σn / ΣN) and the 34 placed rows give **6.79%**. Pool each row's *printed* percentage weighted
   by its N and the same 34 rows give **6.52%**. The 0.19-point gap is row 17 (a) — the one placed cell
   whose printed percentage is not its own counts (10.42 against 11.51) — so an unpinned pool is exactly
   where that cell would hide. Any sentence quoting the placed pool has to say which of the two it means.


**A third caveat, added 2026-11-24 with row 7.**

3. **Frame 1 now weighs colonies where the rest of the table weighs sampling units, and that was not true
   yesterday.** Row 7's 1,200 are twenty *E. coli* colonies picked per pooled faecal sample — 20 farms
   sampled on three days, sixty samples in all — so one farm-day contributes twenty rows to the pool and
   a farm contributes sixty. The row is an isolate screen and belongs in frame 1 on what its N counts, but
   the frame's 6.95% is now weighted toward the smallest sampling effort in the table. It is a frequency
   among screened colonies, not a share of farms, birds or samples, and it must not be read as the
   country's prevalence.

4. **Frame 2 is not an *E. coli* frame, and its floor is a lower bound twice over.** India's 253 isolates
   (§5l) are *E. coli*, *Aeromonas veronii* and *A. dhakensis* screened together, and two of its five
   mcr-1 positives are *Aeromonas* — so as an *E. coli* row it overstates. Its 5/253 rests on 47
   phenotype-positive isolates being genotyped while 206 were not, exactly as Canada's does. Placing it
   moved frame 2 from 0.04% to 0.12%, which moved the floor of the range: a singleton frame had been
   setting it. Tunisia's row (§5g, placed on the primary's 233) moves the same frame again, 0.12% to
   0.18%, and the floor with it — the floor of this table is now one frame's property, so it moves
   whenever that frame gains a row.

## The recalculated range that replaces the single number

- **Frame rates: 0.196% – 31.7%**, a 161-fold spread, from eight frames built the same way (pool
  inside the frame, n over N).
- **Row rates, for the same 34 rows: 0.00% – 60.7%** (rows 17 (d) and 17 (g) low, at zero positives in
  129 and 73 isolates; rows 17 (h) and 17 (i) high, both 17/28) — the far end is two 28-isolate cells in
  an eleven-row block that shares one methods section.
- The 34 placed rows pooled from their counts (Σn / ΣN) give **6.79%**, not 7.0%; pooled from their
  printed percentages, **6.52%** (the two methods, and the one cell that separates them, are caveat 2
  above). Either way the pool was never a stable number, it was an artefact of which rows the review
  happened to include.
- Arithmetic failures among the 30: **one**, row 17 (a), the already-documented cell.

## What this does not say

1. **Not that the eight rates are comparable.** They are not; that is the finding.
2. **Not that the range is final.** 4 of the 38 rows still have no frame, and the record now lists
   them instead of leaving the set to be subtracted: `unplaced` in
   [`mcr-colistin-denominator-frames.json`](mcr-colistin-denominator-frames.json) gives all nine in read
   order, each with its counts and with *why it is still open* — one source refusal, seven unread. In
   that order: China 1,611 (row 2, **cannot be read from here** — a one-page Lancet correspondence with
   no abstract and no PMCID, publisher 403, retried on 2026-11-24 and refused again), Nigeria 35
   (row 24), China 130 (row 3, printed **57.69%** — the table's highest cell, and
   the read most likely to move a frame rate), China 668 (row 4), Bangladesh 104 (row 8), Vietnam 210
   (row 9), Pakistan 120 (row 10), Germany 154 (row 16). Read order puts the two largest readable rows
   late on purpose: §7 fixed that order before these counts were in one place, and re-ordering it by
   size would be a new decision, not a correction. **Two corrections in this paragraph.** An earlier
   version named three other rows as the largest unplaced; and until 2026-11-24 it described the last
   six as "rows under thirty isolates", which is true of none of them — the smallest of the six is 104
   isolates. Both errors came from writing the list in prose over separate wakes instead of reading it
   off a computed set, which is what the `unplaced` block now is. Until these rows are placed the
   number is "90.9% of the table's isolates", not "the table". And 443 of the 37,816 isolates in the
   table's own denominator are now known to belong to an invented one (row 27: 676 printed, 233 with a
   witness), so even a fully placed table would not have a readable pool.
3. **Not a population prevalence anywhere.** Every frame is a surveillance design; the largest block
   is diagnostic submissions of sick piglets to one German institute.
4. **Not a correction to the review's cells** except 17 (a) and 19, which have their own records and,
   for 17 (a), a letter sent to the corresponding author on 2026-11-19
   (`channels/sent/2026-11-19-ferdous-colistin-row-17a-percentage.md`).

## Where the working lives

- Frame assignment, counts, rates and coverage:
  [`mcr-colistin-denominator-frames.json`](mcr-colistin-denominator-frames.json), regenerated by
  `scripts/mcr_colistin_denominator_frames.py --write`.
- The row-by-row reading: [`mcr-colistin-harmonisation.md`](mcr-colistin-harmonisation.md) §5c–§5l.
- The whole-table arithmetic: [`mcr-colistin-table-arithmetic-audit.md`](mcr-colistin-table-arithmetic-audit.md),
  whose sibling test `tests/test_mcr_table_arithmetic.py` pins that audit.
- This sheet is pinned by `tests/test_mcr_colistin_denominator_sheet.py`, which recomputes rows 18 and
  21 from their own counts, all thirty-four placed rows against their printed cells (and the one whose placed counts are the
primary's rather than the table's), and the two numbers
  in the quotable sentence from the record — so a drifted count fails rather than re-reads as prose.
