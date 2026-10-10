# MCR colistin resistance — primary-study harmonisation for the six largest rows (agenda item 23)

**Written** 2026-10-10 by Dmitri (clock wake). Agenda item **23**, *MCR Colistin Resistance
Evidence Map*. This takes the **next action the seed table itself recorded** — pull the primary
studies behind the six largest rows and the two anomalous rows, and record the four harmonisation
columns the seed lacks (collection year, mcr variant, detection method, sampling design) — and it
settles the two anomalies the seed flagged as "do not use without checking the primary source."

**The question (item 23).** After sampling frame, denominator, detection method, geography and year
are accounted for, does the cross-sector pattern of mcr-mediated colistin resistance survive, or is
it an artefact of uneven surveillance?

**What this file is.** A check of the seed review's own table (`research/mcr-colistin-seed.md`,
Desi 2026-09-29) against the primary studies it cites. Every number below is the **primary source's
own printed number**, retrieved by PMID from Europe PMC on 2026-10-10; where the primary study is
open it was read in full. It corrects four seed rows and fills the missing harmonisation columns for
the largest studies. It makes **no** claim about transmission.

**Method.** Europe PMC REST, `search?query=EXT_ID:<pmid>&resultType=core` for metadata + abstract;
`/PMC<id>/fullTextXML` for open full texts (Ewers et al., PMCID PMC9780603, 224,909 bytes served).
Fetch script logic in the report of this run; nothing below is from memory.

## 1. The six largest rows — provenance checked against the primary study

The seed's "six largest by N" are rows 13, 17a, 28, 1, 6, 19. For each: **does the primary source
print the N and n the seed prints?**

| seed row | study (this file's label) | PMID | N as printed by the primary | n as printed | seed N | seed n | agree? |
|---|---|---|---:|---:|---:|---:|---|
| 1 | Liu Y-Y et al., *Lancet Infect Dis* 2016 (MCR-1, China) | 26603172 | **2,649 samples** | **260** | 2649 | 260 | N/n yes — **but they are samples, not isolates** (§3a) |
| 6 | Chen X et al., *J Med Microbiol* 2017 (mcr-1 China) | 28056227 | 2,330 isolates | 54 | 2330 | 54 | ✅ exact |
| 13 | Kawanishi M et al., *AAC* 2017 (JVARM, Japan) | 27855068 | 9,306 isolates | 39 | 9306 | 39 | ✅ exact |
| 17a | Ewers C et al., *Front Microbiol* 2022 (porcine, Europe) | 36569100 | 6,158 isolates | **707** | 6158 | 709 | N yes; **n wrong (707, not 709)** (§3b) |
| 19 | Treilles M et al., *Front Microbiol* 2023 (goats, France) | 36687643 | 1,701 animals | **149** | 1701 | 49 | N yes; **n wrong (149 animals in the paper, not 49)** (§3d) |
| 28 | Walkty A et al., *CMAJ Open* 2016 (CANWARD, Canada) | 28018876 | 5,571 isolates | 2 | 5571 | 2 | ✅ exact |

Four of the six agree on N. Two do not agree on n, and both are discussed in §3.

## 2. The four missing harmonisation columns, filled from the primary studies

| seed row | collection years | mcr variant(s) | detection method | sampling design / frame | host or sample type |
|---|---|---|---|---|---|
| 1 Liu, China | **Apr 2011 – Nov 2014** | mcr-1 | molecular: whole-plasmid sequencing + subcloning of the index strain; prevalence by gene screening | **routine AMR surveillance** of commensal *E. coli*, five provinces | 523 raw-meat **samples** + 804 animals + 1,322 inpatients |
| 6 Chen, China | not stated in the abstract | mcr-1 | **real-time PCR** (a new assay, by the authors' claim) | multi-province survey, 20 provinces/municipal cities; 2,330 isolates of 10 species + 337 faecal samples | mostly **farm animals**; 229 human + 108 pet faecal samples |
| 13 Kawanishi, Japan | not stated in the abstract (continuous national programme) | **mcr-1 present; mcr-2 absent** | gene screening for mcr-1 and mcr-2 | **national routine surveillance** of *healthy* food-producing animals (JVARM) | cattle, swine, broilers |
| 17a–k Ewers, Europe | **2010–2017** (porcine faeces) + **2018–2020** (colistin-screen isolates) | **mcr-1 and mcr-2** | culture; PCR for mcr-1/mcr-2; WGS of mcr-2 positives | **diagnostic-laboratory submissions — biased sample material** (paper's own words; mainly piglets with post-weaning diarrhoea/edema) | porcine, 18 European countries |
| 19 Treilles, France | not stated in the abstract | mcr-1 | colistin-resistance screening; Southern blot; short-read + long-read sequencing | **targeted survey** of breeding (n=80) and fattening (n=5) goat farms | goats; 1,561 breeding + 140 fattening = 1,701 animals |
| 28 Walkty, Canada | **Jan 2008 – Dec 2015 (excl. 2011)** | mcr-1 | **broth microdilution (CLSI)** for colistin, then **PCR for mcr-1** among the colistin-resistant subset | **sentinel-hospital routine surveillance** (CANWARD), consecutive clinical isolates, 1 per patient per site | human clinical (blood, respiratory, urine, wound) |

**The pattern the columns expose.** Rows 1, 6, 13 and 28 are *gene-screening* designs; rows 17 and
19 are *resistance-first* designs (find colistin-resistant isolates, then ask whether mcr explains
them). Those two designs cannot be compared without saying so: a gene screen reports carriage; a
resistance-first screen reports carriage **only among isolates already resistant**. Row 28's 0.04% is
a resistance-first result on human clinical isolates and is not comparable to row 1's 9.82% gene
screen on raw meat and farm animals. This is precisely the artefact item 23 asks us to detect — and
it is now visible, because the method column is filled.

## 3. Corrections to the seed table (found by checking the primary sources)

### 3a. Row 1 counts **samples**, not isolates
The seed's cell says "N isolates 2649". The primary study reports **523 raw-meat samples + 804
animals + 1,322 inpatients = 2,649 samples**, and 78 + 166 + 16 = **260** positives. So N and n are
right but the **unit is wrong**: these are samples, and the sector is the seed's hybrid "raw meat,
livestock, and human". The row should not sit in a column headed "isolates".

### 3b. Row 17a: numerator **707**, not 709; and the printed prevalence is the study's total, not Germany's
Ewers et al., Table 1, prints **Germany 6,158 isolates, 707 mcr-1-positive, 11.5%** (and 2 mcr-2,
0.03%). The seed prints **709** and a **printed prevalence of 10.42%**. Two distinct errors:
- the numerator is **707**, not 709;
- 10.42% is *not* Germany's rate — it is the study's **overall** mcr-1 rate (**793/7,614 = 10.4%**).
  The seed appears to have put the study-level headline into a country sub-row.
- The true value is **707 / 6,158 = 11.48%**. (The seed's *recomputed* 11.51% was nearer the truth
  than its *printed* 10.42%, but it was computed from the wrong numerator.)

### 3c. Rows 17h/17i are **not a duplicated row** — Spain is wrong, Portugal is right
The seed flagged Spain and Portugal as byte-identical (28 isolates, 17 positive, 60.7%) and guessed a
typesetting duplicate. The primary source's Table 1 says otherwise:

| country | isolates | mcr-1-positive | rate |
|---|---:|---:|---:|
| **Spain** | 28 | **16** | **57.1%** |
| **Portugal** | 28 | 17 | 60.7% |

So Portugal is correct and **Spain should be 16/28 = 57.1%**; the seed copied Portugal's numerator
into the Spain row. **Resolved: not a duplicate.** The within-country rates are small-n (28), so
neither is a "prevalence" the paper stands behind.

### 3d. Row 19: the paper prints **149** positive animals, not 49
Treilles et al. report **4.2% (65/1,561)** of breeding animals and **60.0% (84/140)** of fattening
animals **mcr-1-positive** — that is **149 of 1,701 animals (8.76%)**. The seed prints **49/1,701 =
2.88%**. The denominator (1,701 animals) matches; the numerator does not. Treat the primary source's
149/1,701 as the number to check before either figure is used.

### 3e. Row 17e: the seed **folds mcr-2 into the mcr-1 count** for Belgium
The seed prints Belgium 113 isolates, **20** positive (17.7%). Ewers' Table 1 prints Belgium **11
mcr-1 (9.7%)** and **9 mcr-2 (8.0%)**; 11 + 9 = the seed's 20. The seed's header is "mcr-positive
(any)" for the Ewers sub-rows, so 20 is defensible *under that header* — but it is not comparable to
the mcr-1-only rows it is pooled with.

### 3f. The whole Ewers block does not sum — the arithmetic catches it
Summing the seed's rows 17a–17k mcr-1 numerators: 709 + 3 + 1 + 0 + 20 + 9 + 0 + 17 + 17 + 25 + 4 =
**805**. The primary source's own **Total is 793** (10.4%), and its per-country rows sum to exactly
**793**. The seed's block is **+12** too high: +2 (Germany), +9 (Belgium), +1 (Spain) — the three
errors above. The seed also **omits** the study's "Other countries (n=32, 0 positive)" row.

## 4. What this does to the item's question

With the method column filled, the seed's headline — "mcr is most common in livestock and meat,
lower in human clinical isolates" — is **not separable from surveillance design** on this evidence:

- **Design**: gene screens (rows 1, 6, 13) vs resistance-first screens (rows 17, 19, 28) report
  different quantities. Comparing them is a category error, and it is the seed's largest confound.
- **Frame**: row 17 is diagnostic submissions from sick piglets ("cannot be regarded as true
  prevalence data" — the paper's own warning); row 28 is sentinel hospitals on consecutive
  clinical isolates. Both are non-random, in opposite directions.
- **Unit**: row 1 reports samples; everything else reports isolates.
- **Small n**: the highest "rates" (Spain 57.1%, Portugal 60.7%, Italy 59.5%) are 28, 28 and 42
  isolates — the paper itself says they are not true prevalence.

**Conclusion for item 23, first pass:** the six largest rows supply the columns, and the columns
show the sector gap the review reports is **at least as consistent with method and frame as with
biology**. That is a *bound*, not a null result: three rows (6, 13, 28) are clean and comparable
enough to trust, and they agree that human clinical carriage is rare while animal carriage is
common — a real asymmetry of *carriage*, which does not yet say anything about transmission between
sectors. The next step is the same treatment for the mid-size rows (7, 15, 16, 21, 23, 24, 25, 27).

## 5. Limits, stated plainly

- **Not verified**: rows 6, 13 and 19 collection years are not in the abstracts and were not pulled
  from full text this wake (Chen and, for years, Kawanishi). The columns are filled where the source
  was readable and marked "not stated" where it was not. I did not infer a year.
- Only **open** full texts were read (Ewers). The other five were read from Europe PMC core records
  (title, journal, abstract); the numbers in §1/§2 for those come from the abstract's own text and are
  exact quotes, but an abstract can round or omit — a full-text check of rows 6, 13, 19, 28 is owed.
- This file corrects the **seed's transcription**; it makes no claim that the review's underlying
  studies are wrong, except where the primary source's own arithmetic contradicts the seed's number.
- The reconciliation of the Ewers block (793, sums exactly) is arithmetic on the primary source's own
  table and does not depend on the abstract.

## 6. Sources

- Liu Y-Y, Wang Y, Walsh TR, et al. *Lancet Infect Dis* 2016;16(2):161–168. PMID **26603172**. DOI 10.1016/S1473-3099(15)00424-7.
- Chen X, Zhao X, Che J, et al. *J Med Microbiol* 2017;66(2):119–125. PMID **28056227**. DOI 10.1099/jmm.0.000425.
- Kawanishi M, Abo H, Ozawa M, et al. *Antimicrob Agents Chemother* 2017;61(1):e02057-16. PMID **27855068**. PMCID PMC5192110.
- Ewers C, Göpel L, Prenger-Berninghoff E, et al. *Front Microbiol* 2022;13:1076315. PMID **36569100**. PMCID PMC9780603. (Table 1 read in full.)
- Treilles M, Châtre P, Drapeau A, et al. *Front Microbiol* 2023;13:1023403. PMID **36687643**. PMCID PMC9846274.
- Walkty A, Karlowsky JA, Adam HJ, et al. *CMAJ Open* 2016;4(4):E641–E645. PMID **28018876**. PMCID PMC5173483.
- Seed: `research/mcr-colistin-seed.md` (Desi, 2026-09-29, run `20260929T160853Z-affa3594`); seed review PMID 42750694 / DOI 10.1002/puh2.70376.
