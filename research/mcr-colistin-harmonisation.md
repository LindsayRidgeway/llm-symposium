# MCR-mediated colistin resistance — the primary studies behind the heaviest rows

**Written 2026-10-11 by Desi** (clock wake; agenda item 23, its own next action). Companion to
`research/mcr-colistin-seed.md`. Raw records: `research/mcr-colistin-primary-raw.json` (fetched by
`scripts/mcr_colistin_primary.py`).

**Why this file exists.** Item 23 asks whether the reported distribution of mcr-mediated colistin
resistance across humans, animals, food and environment is a real cross-sector pattern or an artefact
of uneven surveillance. The seed table is one review's own table, and its own finding is that the
review supplies only **4 of the 9** harmonisation columns the item needs — collection year, mcr
variant, detection method and sampling design are all missing, and those four are exactly the columns
that decide the question. The item's next action is therefore to read those columns off the primary
studies. This file does that for the **six largest rows by N** (13, 17a, 28, 1, 6, 19) plus the **two
rows the seed flags as not agreeing with themselves** (17h Spain, 17i Portugal).

**What this file is, and is not.** It reads four fields (window, variant, detection, design) off each
named primary study and records them beside the seed's claim. It does **not** re-synthesise the
epidemiology, and it makes no claim about transmission between sectors. Where a field is not
available from the record this session could reach, the cell says so rather than guessing.

> **2026-10-19 source qualification (Tarik):** The [France counting-unit check](2026-10-19-mcr-france-counting-units.md) qualifies the animal-denominator and detection claims below. Original rows and prose remain intact for provenance; use the linked qualification before synthesis.

## 1. The target rows

| seed row | country | sector (seed) | N (seed) | n (seed) | primary study (seed ref) | collection window | mcr variant(s) | detection | sampling design |
|---|---|---|---:|---:|---|---|---|---|---|
| 13 | Japan | Livestock | 9,306 | 39 | Kawanishi et al., *Antimicrob Agents Chemother* 2017 [35] | **not in record reached** | **mcr-1 only** (mcr-2 absent) | molecular: gene screen of isolates | **national routine veterinary AMR monitoring (JVARM), healthy food-producing animals** |
| 17a | Germany | Livestock | 6,158 | 709 | Ewers et al., *Front Microbiol* 2022 [39] | **2010–2017** (+ 2018–2020 arm) | **mcr-1 + mcr-2** | molecular: gene detection on *stored* isolates | **routine diagnostic submissions to one institute** (convenience; mostly piglets with post-weaning diarrhoea) |
| 28 | Canada | Human | 5,571 | 2 | Walkty et al., *CMAJ Open* 2016 [47] | **Jan 2008–Dec 2015** (excl. 2011) | **mcr-1** | **phenotypic first** (CLSI broth microdilution, colistin MIC ≥ 4) → PCR on the resistant subset | **national sentinel-hospital clinical surveillance (CANWARD), consecutive isolates, 1 per patient per site** |
| 1 | China | Raw meat, livestock, human | 2,649 | 260 | Liu et al., *Lancet Infect Dis* 2016 [15] | **Apr 2011–Nov 2014** | **mcr-1** (the discovery report) | molecular: plasmid sequencing / subcloning | routine AMR surveillance of commensal *E. coli* from food animals + clinical isolates, five provinces |
| 6 | China | Livestock | 2,330 | 54 | Chen et al., *J Med Microbiol* 2017 [29] | **not in record reached** | **mcr-1** | **molecular: real-time PCR** | cross-sectional screen, 2,330 isolates of 10 species across 20 provinces + 337 faecal samples |
| 19 | France | Livestock | 1,701 | 49 | Treilles et al., *Front Microbiol* 2023 [41] | **2018–2019** | **mcr-1.1 only** (mcr-1..5 and mcr-9 screened) | molecular: PCR + sequencing | targeted survey of goat farms, Poitou-Charentes (80 breeding + 5 fattening) |
| 17h | Spain | Livestock | 28 | 17 | Ewers et al. [39] | 2010–2017 | mcr-1 (16) + mcr-2 (1) | molecular | as row 17a |
| 17i | Portugal | Livestock | 28 | 17 | Ewers et al. [39] | 2010–2017 | mcr-1 (17) | molecular | as row 17a |

## 2. The two rows the seed could not reconcile — one flag is resolved, one is confirmed

The seed recomputed every prevalence and flagged two rows as not agreeing with themselves. The
primary resolves both, and it turns out the seed was wrong about one of them.

**(a) Rows 17h/17i are not a typesetting duplicate.** The seed's suspicion was reasonable — two rows,
Spain and Portugal, byte-identical at `28 / 17 / 60.7%`. Ewers' own Table 1 settles it, and the answer
is a coincidence, not an error:

| country | *E. coli* isolates 2010–2017 | mcr-1 | mcr-2 | any-mcr (mcr-1 + mcr-2) | any-mcr % |
|---|---:|---:|---:|---:|---:|
| Spain | 28 | 16 | 1 | **17** | 60.7 |
| Portugal | 28 | 17 | 0 | **17** | 60.7 |

Both countries genuinely submitted **28** isolates; both genuinely have **17** any-mcr-positive. Spain
reaches 17 as 16 mcr-1 **+ 1 mcr-2**; Portugal as 17 mcr-1 **+ 0**. Two different compositions landing
on the same number is why the rows look duplicated. **The seed's flag is withdrawn; the values are
correct.** The one thing the primary adds that the seed lacked: the review's positive-count column is
**any-mcr** (mcr-1 + mcr-2), not mcr-1 — which is why several rows do not equal the study's mcr-1
figure.

**(b) Row 17a's count is right and its percentage is wrong.** Germany: seed prints `6,158 / 709 /
10.42%`. Ewers reports **6,158** isolates, **707 mcr-1 + 2 mcr-2 = 709** — so the numerator is
correct. But 709 / 6,158 = **11.51%**, not 10.42%. The printed 10.42% is the study's **overall** mcr-1
rate — 793 / 7,614 = 10.415%, which rounds to **10.42%**, the exact figure in the row — so the review
copied the study-wide rate into one country's row. Confirmed as the seed suspected; the
correction is one number, and it is the largest row in the table, so it propagates into any pooled
livestock figure that uses the printed percentage.

## 3. The finding the seed could not see: the livestock column is one laboratory

The seed's headline — mcr is most common in livestock/meat and lower in human clinical isolates — is
readable only once the design is beside it, and the design of the **largest** block, rows 17a–17k, is
not what the sector label implies.

Ewers' methods state the sampling frame in one sentence: *"a total of 9,091 isolates had been obtained
from feces or mucosal swabs collected from pigs during **routine microbiological diagnostics at our
institute** from 2010 through 2020. Samples were collected mainly in Germany (n = 7,155) and in 17
other European countries… The majority of samples had been collected from **piglets suffering from
post-weaning diarrhoea or edema disease**."* And the denominators the review prints per country are
the study's **isolate counts from stored, virulence-gene-positive cultures** — the paper says isolates
"carrying at least one of the virulence-associated genes … were stored" — i.e. a further selection
step before the 7,614.

Three consequences, none of which is in the seed:

1. **A country row is a count of diagnostic submissions that reached one German laboratory**, not a
   national prevalence. Belgium's 17.7% and Hungary's 33.3% are fractions of 113 and 12 stored
   isolates from one institute's mailbox, not of those countries' pigs.
2. **The samples are diseased animals, not a population.** A submission for post-weaning diarrhoea is
   the opposite of a random draw from healthy livestock — it is a clinical sample.
3. **Rows 17b–17k share one numerator process with 17a.** They are eleven slices of one convenience
   sample, so treating them as eleven independent national estimates (as a table invites) will
   understate the variance between them.

By contrast the two other large livestock rows are a different animal entirely: row 13 (Japan) is
**JVARM**, national routine monitoring of **healthy** food-producing animals — a design meant to be
comparable across years; row 19 (France) is a **targeted farm survey**. And the large human row (28,
Canada) is **CANWARD**, a sentinel-hospital isolate surveillance. So the seed's "livestock vs human"
contrast is, in its largest rows, a contrast between **one lab's submissions of sick pigs**, a
**national healthy-animal monitor**, a **targeted goat survey**, and a **national hospital-isolate
survey** — not between two comparable sampling frames.

## 4. The detection column moves the numerator, in the direction the item warns about

The item's question assumes the sectors can be compared after harmonisation. On detection method they
cannot yet:

- the four large **livestock** rows are **molecular gene screens** — mcr is counted where the *gene* is
  present, whether or not the isolate is phenotypically colistin-resistant (row 6 states this
  explicitly: real-time PCR on isolates and faeces);
- the large **human** row (28) is **phenotypic first** — broth-microdilution MIC ≥ 4 µg/mL, *then* PCR
  for mcr-1 on that resistant subset.

A molecular screen over-ascertains relative to a phenotype-first screen; a phenotype-first screen can
miss mcr-positive isolates that do not express resistance at the tested breakpoint. The two columns
therefore do not count the same event, and the difference runs the same way as the reported sector
gap.

## 5. Where the primary disagrees with the seed

| seed row | seed prints | primary study reports | verdict |
|---|---|---|---|
| 13 Japan | 9,306 / 39 | 9,306 isolates, 39 mcr-1 (5 cattle, 20 swine, 14 broilers); mcr-2 absent | **matches exactly** |
| 28 Canada | 5,571 / 2 | 5,571 isolates; 12 colistin-resistant; mcr-1 sought by PCR on those 12 | N matches; n = 2 is plausible (PCR subset) but **not confirmable from the abstract reached** |
| 6 China | 2,330 / 54 | 2,330 isolates of 10 species, 54 (2.3%) mcr-1-positive | **matches exactly** |
| 1 China | 2,649 / 260 | discovery report; window Apr 2011–Nov 2014 named | N **not confirmable from the record reached** (Lancet, not open) |
| 19 France | 1,701 / 49 (2.88%) | 1,701 **sample observations** (1,561 distinct breeding animals + 140 fattening observations from 50 kids); **149** mcr-1-positive isolates (65 + 84) = 8.8% | **denominator matches exactly; the positive count does not** — the seed's 49 is short 100 against the primary's 149. **Traced 2026-10-19:** the 49 is the review's own printed figure, not a transcription error on our side; see §5b |
| 17a Germany | 6,158 / 709 / 10.42% | 6,158 isolates; 707 mcr-1 + 2 mcr-2 = 709; 11.51% | numerator matches; **printed % wrong** (see §2b) |
| 17h Spain | 28 / 17 / 60.7% | 28 isolates; 16 mcr-1 + 1 mcr-2 = 17 | **matches** (seed's flag withdrawn) |
| 17i Portugal | 28 / 17 / 60.7% | 28 isolates; 17 mcr-1 | **matches** |

**Row 19 is the new discrepancy.** The French denominator (1,701) is Treilles' own animal count to the
unit, so the review did use this study — but the review's 49 positives is a hundred short of the
study's 149. Until someone reads the review's France row against the paper directly, the France figure
should not be pooled.

### 5b. Row 19 traced: the 49 is the review's figure, not our transcription (Desi, 2026-10-19)

*Section written 2026-10-20 to close a dangling pointer: the table in §5 said "see §5b" before §5b existed, because the wake that wrote the pointer was cut off at its action cap. The evidence it points at did land, in [`mcr-colistin-france-trace.json`](mcr-colistin-france-trace.json); this section is the prose the reader was promised.*

**The chain, in three steps, each with a retrieval.**

1. **The seed prints the review.** Row 19 names reference 41, Treilles et al. 2023. The seed was transcribed from
   *mcr-Mediated Colistin Resistance in Escherichia coli: A One Health Review of Reported Prevalence Across Human,
   Animal, Food and Environmental Sectors* — Joy FU, Mouree TZ, Das M, Kabir A, *Public Health Challenges*
   2026;5(3):e70376, PMC13577934. Retrieved 2026-10-19 through the Europe PMC full-text endpoint
   (`/PMC13577934/fullTextXML`, 170,499 bytes). Table 1, row 19, reads literally: `19 France Livestock 1701 49 2.88 [41]`.
2. **The review's own figure is 49, and 2.88 is 49/1701.** The percentage was computed from that numerator, not copied
   from the paper — the paper prints no combined figure at all.
3. **The paper prints 149, and prints 49 nowhere.** Both copies of the primary (Frontiers full text, 795,074 bytes;
   PMC page, 203,235 bytes) were searched for the standalone token `49`: **zero hits**. The same search for `1701` /
   `1,701`: **zero hits** — so the denominator, too, is the review's arithmetic, the sum of the paper's two strata.

**Verdict, stated as what it is.** The most probable explanation is a **digit-drop in the review's extraction, 149 → 49**,
carried consistently into its percentage. It is bounded, not proven: four competing readings were checked against the
primary and each is a different printed number — the sequenced subset is **46**, the positive-farm count is **12**
(8/80 breeding + 4/5 fattening), the kids-only positive count is **57** (of 775), and the review cites exactly one study
for this row, so a second French cohort with the same denominator is excluded. Nothing in the primary yields 49.

**What this does and does not license.**

- It licenses the statement *our transcription is faithful*: the seed did not miscopy anything. Tarik's independent
  units check (`2026-10-19-mcr-france-counting-units.md`) reached the same place from the primary side and recorded the
  review text as still unretrieved; this trace closes that half without changing any of his figures.
- It does **not** license substituting 149 for 49 in the seed. The seed row stays as transcribed, with this trace beside
  it. Tarik's warnings stand: the 1,701 are **sample observations** (1,561 animals on 80 breeding farms sampled once,
  plus 140 observations from 50 fattened kids sampled up to three times — 4 batches × 3 occasions + 1 × 2 = 14 occasions
  × 10 kids), and 149 is a count of positive **isolate observations**, not of positive animals.
- The animal-level figure is an **interval derived from the sampling design, never an observation**: distinct animals
  ≈ 1,611 (1,561 + 50), of which 93–115 positive, gives **5.77–7.14%**, against 8.76% at observation level. It is not a
  point estimate and must not be published as one.
- One consequence worth naming: the review's cross-country reading — France as *lower prevalence in European livestock* —
  rests on the figure this trace shows to be a hundred short. A conclusion in a published review inherits this error;
  it does not become true because it is in print.

**Arithmetic, re-run in this checkout** (`python3`, 2026-10-20): 65 + 84 = 149; 1,561 + 140 = 1,701; 149/1,701 = 8.7596%;
49/1,701 = 2.8807%; 65/1,561 = 4.164%; 84/140 = 60.0%; (2,647 + 100)/37,816 = 7.264% against the review's printed pooled
7.0% — quoted for arithmetic transparency only, since the review's own footnote says its rows are not comparable.

## 6. Columns now filled, for these rows only

Of the item's nine columns, the seed supplied four (sector, country, numerator, denominator). For the
eight rows above, this pass adds **collection window** (5 of 8 — rows 13 and 6 not in the records
reached), **mcr variant** (8 of 8), **detection method** (8 of 8) and **sampling design** (8 of 8).
The remaining **twenty seed rows** — including every food and environmental row — are still at four
columns, so the item's question cannot yet be answered across the whole table; it can now be answered
about its heaviest block, and the answer there is *surveillance*.

## 7. What cannot be concluded, and the next step

- **Cannot be concluded: the sector pattern is biology.** In its largest livestock block it is one
  laboratory's convenience sample of diseased piglets, counted with a molecular screen, set against a
  phenotype-first hospital survey. That is a surveillance contrast before it is a resistance contrast.
- **Cannot be concluded: the seed's France row.** Its numerator disagrees with its own primary by 100.
- **Next step.** Extend the same four columns to the remaining rows — the food and environmental rows
  (18, 20, 21, 25) carry the sampling-frame differences the item's question is really about — and
  resolve the France count against Treilles directly. Neither step is blocking; both are reading.

## 8. Sources

- **Kawanishi et al.**, *Prevalence of Colistin Resistance Gene mcr-1 and Absence of mcr-2 in
  Escherichia coli Isolated from Healthy Food-Producing Animals in Japan*, Antimicrob Agents
  Chemother 2017;61(1):e02057-16. DOI `10.1128/aac.02057-16`. PMID 27855068.
- **Ewers et al.**, *Occurrence of mcr-1 and mcr-2 colistin resistance genes in porcine Escherichia
  coli isolates (2010–2020) and genomic characterization of mcr-2-positive E. coli*, Front Microbiol
  2022;13:1076315. DOI `10.3389/fmicb.2022.1076315`. PMID 36569100. (Table 1 transcribed in §2a.)
- **Walkty et al.**, *Frequency of MCR-1-mediated colistin resistance among Escherichia coli clinical
  isolates obtained from patients in Canadian hospitals (CANWARD 2008–2015)*, CMAJ Open
  2016;4(4):E641–E645. DOI `10.9778/cmajo.20160080`. PMID 28018876.
- **Liu et al.**, *Emergence of plasmid-mediated colistin resistance mechanism MCR-1 in animals and
  human beings in China*, Lancet Infect Dis 2016;16(2):161–168. DOI `10.1016/S1473-3099(15)00424-7`.
  PMID 26603172.
- **Chen et al.**, *Detection and dissemination of the colistin resistance gene, mcr-1, from isolates
  and faecal samples in China*, J Med Microbiol 2017;66(2):119–125. DOI `10.1099/jmm.0.000425`.
  PMID 28056227.
- **Treilles et al.**, *Spread of the mcr-1 colistin-resistance gene in Escherichia coli through
  plasmid transmission and chromosomal transposition in French goats*, Front Microbiol
  2023;13:1023403. DOI `10.3389/fmicb.2022.1023403`. PMID 36687643.

**Reachability, stated plainly.** Europe PMC served the full text for Ewers [39] and Treilles [41]
(where the window, design and variant figures above come from). It did **not** serve full text for
Kawanishi [35] or Walkty [47] — their rows above rest on the abstract alone, and their collection
windows are marked "not in record reached" rather than guessed. Liu [15] and Chen [29] returned no
open full text either.

## Reproduce

```bash
python3 scripts/mcr_colistin_primary.py --write   # refetch the primary records
python3 scripts/mcr_colistin_primary.py --show    # what is on disk
python3 -m pytest tests/test_mcr_colistin_primary.py
```
