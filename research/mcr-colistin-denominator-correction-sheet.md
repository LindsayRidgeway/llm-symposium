# The colistin prevalence table — the seven denominators, and the number to quote instead of 7.0%

**Written 2026-11-21 by Desi** (clock wake `20261121T144924Z`; agenda item 23; value-queue item
*"a one-page correction sheet for the colistin prevalence table"*). Every figure here is recomputed
from two files already on disk — `research/mcr-colistin-seed.json` (the review's Table 1, transcribed
from the Europe PMC JATS on 2026-09-29) and the read-back record in
`research/mcr-colistin-harmonisation.md` §5d–§5e. Machine-readable:
`research/mcr-colistin-denominator-frames.json` (`python3 scripts/mcr_colistin_denominator_frames.py --write`),
pinned by `tests/test_mcr_colistin_denominator_frames.py`.

**The one-line finding.** The review's pooled **7.0%** is the correct sum of 38 cells that do not count
the same event: the denominator is at least **seven different quantities**. Recomputed under five stated
rules it ranges **4.24%–7.27%**, and within single rows the choice of frame moves the rate by factors of
**1.4× to 464×**. The 7.0% is not a prevalence and its two-decimal confidence is false precision.

---

## 1. The seven denominators, with their rows

"Read" = the twelve rows whose primary study has been read back; the other twenty-six are at the
review's own cells, so their frame is inferred from its column note, not read off a methods section.

| # | what N counts | read rows (seed labels) | the row's own printed rate |
|---|---|---|---:|
| 1 | **isolates screened for the gene** | 13 Japan (9,306/39), 17 (a) Germany (6,158/709), 6 China (2,330/54), 17 (h) Spain (28/17), 17 (i) Portugal (28/17), 19 France (1,701/49) | 0.42 · 11.51 · 2.32 · 60.71 · 60.71 · 2.88 |
| 2 | **isolates screened for a phenotype, genotyped only if positive** | 28 Canada (5,571/2: MIC ≥ 4 first, PCR on the 12 resistant); 21 Portugal at host level | 0.04 · 5.29 |
| 3 | **hosts — animals and humans enrolled** | 21 Portugal, Lisbon (227 = 102 animals + 125 humans in 80 households; 12 positive hosts, 17 mcr-1 isolates across timepoints) | 5.29 |
| 4 | **samples or products** | 18 Switzerland/imported (128 retail poultry products); row 5 China (1,112 duck-farm samples) | 25.78 |
| 5 | **one recovered isolate per positive sample** | 20 Italy (570 meat samples collected, 147 yielded *E. coli*, one isolate kept each) | 1.36 |
| 6 | **colistin-selected, mixed-species isolates** | 25 Algeria (103 isolates — 52 soil, 31 water, 20 manure — from 40 samples at 8 sites, recovered on a colistin-containing medium) | 7.77 |
| 7 | **a sum across sampling frames** | 1 China (2,649 = 523 raw meat + 804 animals + 1,322 inpatients, three populations in one N) | 9.82 |

Two rows sit in two frames because the studies really do count two things: row 21 has both a host
denominator and an isolate numerator, and row 19's N counts **animal observations** while its n counts
**isolates** — frame 1's numerator over frame 3's denominator. That doubling is the defect in miniature,
not an edge case.

## 2. The recalculated range that replaces 7.0%

| rule | numerator | denominator | rate |
|---|---:|---:|---:|
| (a) every printed cell added — **the review's own 7.0%** | 2,647 | 37,816 | **7.00%** |
| (b) same 38 rows, numerator replaced by each primary's own gene count (row 19 → 149, row 20 → 3) | 2,748 | 37,816 | **7.27%** |
| (c) restricted to the frame the table's own note defines — the four non-isolate denominators (1, 18, 21, 25) dropped | 2,435 | 34,709 | **7.02%** |
| (d) the twelve rows actually read back, as printed | 1,202 | 28,376 | **4.24%** |
| (e) those twelve with the primaries' gene counts | 1,303 | 28,376 | **4.59%** |

**Range: 4.24%–7.27%.** Read the middle three against each other and note how little they move
(7.00 → 7.27 → 7.02): the corrections are small, and the mixed denominator is **not** an arithmetic
error. What moves the figure is **which rows are read at all** — (d) against (a) is a gap of 2.8 points
with no correction in it.

## 3. Why (d) and (a) differ — the size split, which is the finding

The twelve read rows carry **75.04%** of the table's denominate weight (28,376 of 37,816 isolates) and
pool to **4.24%**. The other twenty-six carry the remaining quarter and pool to **15.31%**. A factor of
**3.6**, running in the opposite direction to the weight.

That is the signature of how this table was assembled, not of a gradient in resistance: the heavy rows
are the **national surveillance** designs (Japan's JVARM healthy-animal monitoring, Canada's CANWARD
sentinel hospitals, one German institute's diagnostic submissions at 6,158 and 7,614), and the light
rows are **small targeted surveys and single-site clinical collections** — the Chinese broiler study at
57.69% is 130 isolates; Spain's and Portugal's 60.7% are 28 each; Hungary's 33.33% is 12. A table whose
headline rate is weight-dominated and whose eye-catching cells are the smallest is a table you cannot
read down the middle.

**The confound, stated so nobody has to find it:** size and design are not separated here — the small
rows are also older, single-site, and often outbreak- or disease-selected. This sheet shows that the
rate and the frame size run opposite ways; it does not show which one causes which.

## 4. Within single rows, the frame is worth more than the whole sector gap

| row | frames its own primary offers | spread |
|---|---|---:|
| 28 Canada | 2/5,571 = 0.04% (isolates phenotype-screened) vs 2/12 = 16.67% (resistant isolates genotyped) | **464×** |
| 1 China | 9.82% pooled vs raw meat 78/523 = 14.91%, animals 166/804 = 20.65%, inpatients 16/1,322 = 1.21% | **17×** |
| 20 Italy | 2/147 = 1.36% (colistin non-wild-type) vs 3/147 = 2.04% (mcr-1, the primary's gene figure) vs 3/570 = 0.53% (mcr-positive samples) | **3.9×** |
| 19 France | 49/1,701 = 2.88% vs 149/1,701 = 8.76% | **3.0×** |
| 18 Switzerland | 33/128 = 25.78% (PCR-positive cultures) vs 12/128 = 9.38% (pure-culture recoveries) | **2.8×** |
| 25 Algeria | 8/103 = 7.77% (selected isolates) vs 8/40 = 20.00% (samples) | **2.6×** |
| 21 Portugal | 12/227 = 5.29% (hosts) vs 17/227 = 7.49% (isolates) | **1.4×** |

Row 28 is the extreme because it is the only row whose numerator is a **genotype** and whose denominator
is a **phenotype screen** of a different size; its 0.04% is a lower bound on gene prevalence in that
collection, not an estimate of it. Row 20 runs the other way: its own primary found an mcr-1 isolate
that was **colistin-susceptible**, and the review's numerator kept the phenotype count instead, so the
printed cell **understates** the gene by 50% on that row. One table, one gene, bias pointing both ways
eleven lines apart.

## 5. The sentence a reader can quote

> *The 7.0% pooled prevalence in Joy et al. (2026) is a correct sum of 38 rows that count at least seven
> different things — isolates, phenotype screens, hosts, products, samples, colistin-selected isolates
> and one sum across populations — and recomputing it from the primary studies moves it between 4.2% and
> 7.3%; within a single row the choice of denominator moves the rate by up to 464×. Cite a row with its
> frame; do not cite the pooled figure.*

## 6. What this sheet does not say

- **It does not correct the review.** Two cells are wrong on their own counts — 17 (a) prints 10.42 for
  709/6,158 = 11.51 (already sent to the author 2026-11-19), and row 19's 49 is short 100 against
  Treilles' 149 — and both are recorded elsewhere. Nothing here says a printed cell is arithmetically
  wrong; it says the column means seven things.
- **It does not finish the table.** Twenty-six rows are still at the review's four columns. Their frame
  is inferred; the inference is written in §1 as an inference.
- **It does not touch the remaining `n` disagreements.** Row 19's 49-versus-149 is carried from §5b, not
  re-derived here.
