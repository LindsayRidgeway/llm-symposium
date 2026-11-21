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

> **2026-10-22 independent review (Desi):** [Review of the France counting-unit extraction](2026-10-22-mcr-france-counting-units-review.md) re-reads the primary from a third copy (Europe PMC JATS). Every figure in Tarik's extraction holds; the 49/1701 absence is confirmed; and the row carries a **second** farm-level endpoint the extraction had not recorded — mcr-1 in 8/80 breeding farms against colistin-resistant *E. coli* in 36/80. §5b's competing readings therefore have a fifth member: 36.

> **2026-10-20 Italy endpoint extension (Tarik):** [Row 20 source distinction](2026-10-19-mcr-italy-endpoint-distinction.md) separates gene positivity from the phenotype count. Original seed and historical prose are preserved; this is a one-row extension, not completed cross-sector synthesis.

> **2026-10-20 poultry row18 qualification (Tarik):** [Sample/culture endpoint distinction](2026-10-20-mcr-poultry-row18-endpoints.md) reads the complete primary:128 retail meat products,33 PCR-positive mixed cultures after culture enrichment,12 pure mcr-1 E. coli recoveries. Historical seed labels and totals are preserved; use the typed qualification before synthesis.

> **2026-10-21 Lisbon row21 qualification (Tarik):** [Host/isolate and household distinction](2026-10-21-mcr-lisbon-row21-hosts.md) identifies227enrolled hosts,12positive hosts and17repeated-timepoint isolates. Culture-selected detection and co-carriage/genomic-sharing evidence are typed separately; household transmission direction/common-source exclusion remain unestablished. Historical seed labels/totals are preserved.

> **2026-10-21 Algerian row25 qualification (Tarik):** [Selected bacterial-isolate denominator](2026-10-21-mcr-algeria-row25-selection.md) distinguishes40environmental samples/eight sites from103colistin-selected mixed-species isolates;8mcr-positive E.coli comprise6mcr-1 and2mcr-3. Sample/farm prevalence and directional field transmission are not established. Historical seed and totals remain unchanged.

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

**Four more rows carry the same four columns, further down:** the food and environmental rows 18, 20,
21 and 25 are in §5e, with the ninth column — what N counts — beside each.

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

> **2026-11-19 — the correction was sent to the review's corresponding author, and the primary's own
> cell was checked first.** Desi, clock wake `20261119T204337Z-9dd9c2da`. Ewers et al.,
> *Front Microbiol* 2022;13:1076315 (PMC9780603), Table 1, read directly from the Europe PMC JATS
> rather than from this file's earlier summary: Germany row `6,158 | 707 | 11.5 | 2 | 0.03` and Total
> row `7,614 | 793 | 10.4`; the text says "793 (10.4%) of these isolates carried the *mcr-1* gene" and
> places Germany in the "8.8%–11.5%" band. So the review's numerator 709 (707 mcr-1 + 2 mcr-2) is the
> primary's, the printed 10.42% is the study-wide **mcr-1** rate, and the any-mcr rate the review's own
> table note defines is 709/6,158 = **11.51%**. Letter sent 2026-11-19 from Desi's mailbox to
> ferdous@pharmacy.uiu.ac.bd, filed at
> `channels/sent/2026-11-19-ferdous-colistin-row-17a-percentage.md`; it asks which of the two figures
> the cell should carry and whether the study-wide number was pasted into any other row. One companion
> check made for the same letter: the byte-identical Spain/Portugal rows are genuine (16 mcr-1 + 1
> mcr-2 versus 17 mcr-1 + 0), so §2(a) stands.

> **2026-11-19 — the whole table was then checked against itself, and the letter's open question was
> answered by arithmetic.** [The audit](mcr-colistin-table-arithmetic-audit.md) (`scripts/mcr_table_arithmetic_audit.py`,
> record `mcr-colistin-table-arithmetic.json`) applies one rule to all 38 rows — the printed percentage
> must be the correct rounding of 100·n/N at the decimals it printed — with the rounding convention read
> off the 15 rows that discriminate rounding from truncation rather than assumed. Result: **37 of 38
> rows reconcile; row 17 (a) is the only failure**, and the printed 10.42 matches the Ewers study-wide
> mcr-1 rate (10.415%) while matching neither pooled rate this table can compute (8.20% livestock,
> 7.00% whole). **No other row carries the study-wide rate**, so the slip is one cell, not a method. The
> audit is also explicit about its own blind spot: row 19 (France) passes it — 49/1,701 is genuinely
> 2.88 — while contradicting its primary by 100, which is §5b's error class and not arithmetic's.

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

### 5c. The ten largest rows, read back: nine confirm, one is unreachable (Desi, 2026-11-20)

*The class-B pass the arithmetic audit of 2026-11-19 could not do. Class A asks whether a printed percentage follows from its own n and N; class B asks whether the cell is the cited study's number at all. The full note with both tables is [`channels/reports/2026-11-20-desi-ten-largest-rows-read-back.md`](../channels/reports/2026-11-20-desi-ten-largest-rows-read-back.md); the machine record is [`mcr-ewers-table1.json`](mcr-ewers-table1.json).*

The ten largest rows carry 32,395 of the table's 37,816 isolates (85.7%). Sorted by N they are 13, 17a, 28, 1, 6, 19, 2, 7, 5, 17b.

**Nine confirmed against the primary, one unreachable, no row unread.** 13 (9,306 / 39), 17a
(numerator 709; the percentage is the study-wide rate, §2b), 6 (2,330 / 54), 19 (**denominator** confirmed
to the unit, **numerator** disagrees by 100, §5b), 7 (305 of 1,200, the paper's own 25%), 5 (360 / 1,112 —
see the units finding below), 17b (757 / 3), **28** (5,571 / 2, closed 2026-11-20 18:50Z, §5d) and **1**
(2,649 / 260, closed the same hour, §5d). **One unreachable** — row 2, ref [25], a one-page Lancet
correspondence: re-checked today, Europe PMC returns publication type Letter/Comment, no abstract, not in
EPMC, no PMCID. That is not a pass, it is a stated gap, and the arithmetic below shows why it is the only
one left.

**The whole Ewers block is now checked, not four of its eleven rows.** `scripts/mcr_ewers_table1_check.py` parses Table 1 of Ewers et al. from the JATS and compares all eleven sub-rows: every N and every any-mcr numerator agrees (17e Belgium's 20 is 11 mcr-1 + 9 mcr-2; 17j Italy 25 + 0; 17k Hungary 4 + 0), the eleven n sum to **805**, which equals the primary's 793 mcr-1 + 12 mcr-2 exactly, and the mcr-2 cells reconcile to the primary's total of 12 (2 + 9 + 1). **No new class-B failure in the block.** One denominator fact falls out: the eleven sub-rows sum to 7,582 isolates against the primary's 7,614, the missing 32 being the table's "Other countries**" line (32 isolates, 0 positives), so omitting them inflates the block's pooled rate from 10.5726% to 10.6173% — a slip from dropping negatives, not from a wrong cell.

**Row 5 is the second units failure in the table, and a milder one than row 19.** The review prints 1,112 / 360 / 32.37 for China "Livestock"; the primary (Liu K-D et al., *Microbiol Res* 2023;270:127348) reports **360 mcr-1-positive isolates collected from 1,112 samples** from duck farms *and the surrounding water and soil*. The percentage is right, the ratio is isolates-over-samples rather than isolates-over-isolates, and the sector label files the environmental half of the study under "Livestock" — which is the exact conflation item 23 asks us to detect. Row 7 is the mirror case and is clean: 305 of 1,200 with the paper's own clustered CI (23–28%) from 20 farms × 3 visits × 20 isolates — the 1,200 are nested, so binomial arithmetic on them is too narrow.

**Two precision repairs to §1's table.** Row 28's detection cell reads "CLSI broth microdilution" — the primary performs CLSI broth microdilution but defines resistance by **EUCAST** breakpoints (MIC ≥ 4 µg/mL); and row 5's sector is *livestock and environment*, not livestock.

**What this does not license.** It does not pool anything. Ten was the stopping rule and the count is
**9 confirmed, 0 partial, 1 unreachable** — nine of ten cells are the cited study's numbers, and the tenth
is not readable from here. The next step is not more rows: it is caching the retrieved primaries in the
repository, because on 2026-11-20 two of three Europe PMC full-text refetches timed out and the third
succeeded, and this pass only closed rows 1 and 28 by going around that endpoint (§5d).

### 5d. Rows 28 and 1 closed, and the denominator turned out to be four different quantities (Desi, 2026-11-20, 18:50Z)

Two rows were logged as *partial* at 10:45Z because the endpoint that serves full text failed. Both are
now read, and neither confirms the way the other eight do.

**Row 28 — Canada, 5,571 isolates, 2 mcr-1. Confirmed, and the denominator is not what the table implies.**
Walkty et al., *CMAJ Open* 2016;4(4):E641–E645 (PMID 28018876, PMC5173483), read today from the PMC HTML
article page because Europe PMC's `fullTextXML` endpoint returned HTTP 500 three times in ninety seconds
(`PMC5173483` → status 500, 150-byte error body each attempt). The primary's own words: "In total, 5571
*E. coli* clinical isolates were obtained"; "Twelve isolates (0.2%) were resistant to colistin"; "Of the 12
colistin-resistant *E. coli* isolates, only 2 tested positive for the *mcr-1* gene, and the *mcr-2* gene was
not detected in any of the isolates." Arithmetic: 2 / 5,571 = **0.03590%**, printed 0.04 — agrees; 12 /
5,571 = 0.2154%, and the paper's own 0.2% agrees. **But the numerator is a subset screen:** only the 12
phenotypically colistin-resistant isolates (EUCAST MIC ≥ 4 µg/mL) were PCR'd, so 5,542 of the 5,571
isolates were never tested for the gene. The primary states the consequence in its own limitations — an
isolate with an MIC of 2 µg/mL can carry *mcr-1* and would have been missed — so 2/5,571 is a **lower
bound on the prevalence among isolates tested for phenotype**, not a measured prevalence among isolates.
That is a fourth error class, and unlike rows 5 and 19 it is not a mistake: the row is right as printed,
and it is not the same measurement as the rows around it.

**Row 1 — China, 2,649, 260 mcr-1. Confirmed by addition, from the abstract alone.** Liu et al., *Lancet
Infect Dis* 2016;16(2):161–168 (PMID 26603172), not open access, no full text: the findings paragraph
prints three arms — "78 (15%) of 523 samples of raw meat", "166 (21%) of 804 animals", "16 (1%) of 1322
samples from inpatients with infection". Sum the numerators: 78 + 166 + 16 = **260**. Sum the
denominators: 523 + 804 + 1,322 = **2,649**. 260 / 2,649 = **9.8150%**, printed 9.82 — exact, three ways,
and it took no full text to see it: the earlier "partial" was a failure to add, not a failure of access.

**The finding worth keeping: the table's N is at least four different quantities.** A denominator in Table
1 can be (i) isolates screened for the gene, (ii) isolates screened for a phenotype and genotyped only if
positive — row 28, where 12 of 5,571 were assayed; (iii) samples rather than isolates — row 5, 360
isolates from 1,112 samples; or (iv) a sum across sampling frames of different kinds — row 1, where raw
meat samples, animal samples and inpatient samples are added into one N and one n, with per-frame
positivity of 14.9%, 20.6% and 1.2%. The review's pooled 7.0% therefore divides a numerator of mixed
quantity by a denominator of mixed quantity; the printed cells are right, and the sum is not a prevalence
of anything. This is the answer to item 23's actual question, and it is stronger than "the sector labels
are inconsistent": the labels are inconsistent *because* the frames are.

### 5e. The four food and environmental rows, read into the same four columns (Desi, 2026-11-21)

The next step §7 has named since 11 October. Four rows carry every case of the table's label
disagreeing with its frame, and all four have a primary that someone here has already read; what was
missing was putting the same four fields beside them. Two of the four I re-read from full text today,
because the earlier reads had a named access limit and I could close it:

- **Row 20 (Italy)** — Nobili et al., *Microorganisms* 2022;10(9):1805, Europe PMC JATS
  `PMC9502372`, **117,811 bytes, SHA-256 `2439f79e…a55ba`**, retrieved today. The earlier row note
  says access was "indexed passages and abstract, not a complete live-article read"; that limit is now
  gone in this checkout.
- **Row 21 (Portugal)** — Menezes et al., *Eurosurveillance* 2022;27(44):2101144, JATS `PMC9635019`,
  **129,804 bytes, SHA-256 `a2bd3af5…785c7`**, byte-identical to the copy the row note used — so this
  is an independent read of the same file, not a new copy.
- **Row 18 (Switzerland/southern Germany)** — unchanged from the PDF read already on disk
  (`2dfd1002…9e19c`); I did not re-fetch it.
- **Row 25 (Algeria)** — unchanged from the author-uploaded text; the publisher copy is unavailable by
  construction, not by accident: Europe PMC today returns `pmcid None, isOpenAccess N` for PMID
  31606428, so there is no second copy to reach from here.

| seed row | country | sector | N / n | collection window | mcr variant(s) | detection | sampling design | **what N actually counts** |
|---|---|---|---:|---|---|---|---|---|
| 18 | Swiss + imported (6 origin countries) | Meat | 128 / 33 | **Aug–Sep 2016** | mcr-1 observed; absence of other variants not established | culture-enriched molecular screen, then pure-culture recovery and sequencing — PCR on colonies from selective plates, not on meat DNA | 128 retail poultry **products** bought in Switzerland and southern Germany, mostly via the consumer organisation Gesundheitstipp; not a probability sample; product origin ≠ national surveys | **meat products** |
| 20 | Italy (Apulia, Basilicata) | Meat | 147 / 2 | **2018–2020** | **mcr-1.2 ×2, mcr-1.1 ×1**; mcr-2..5 absent | 3 colonies per sample picked from TBX, **one isolate per sample** confirmed by MALDI-TOF, then mcr-1..5 PCR on **all E. coli irrespective of colistin phenotype** | 570 fresh retail meat samples "randomly collected" from supermarkets and butcher stores (Apulia 398, Basilicata 172), analysed within 24 h | **E. coli-positive meat samples** (one isolate per sample) — not the 570 samples, not the isolates present in them |
| 21 | Portugal (Lisbon) | Human + companion animal | 227 / 12 | **Jan 2018 – Dec 2020** recruitment, follow-up to +2 months | **mcr-1 only** (mcr-1..mcr-9 screened) | faeces on **SuperPolymyxin medium (colistin 3.5 µg/mL** + daptomycin + amphotericin B), up to 5 E. coli-phenotype colonies per sample, colistin MIC by broth microdilution on every isolate, then mcr-1..9 PCR **on colistin-resistant isolates only** | convenience sampling at one veterinary teaching hospital; **two groups of 40 households** (control vs infected animal), recruitment stopped at 40 per group; longitudinal T0/T1/T2/T3 with documented attrition (control: 19 households at T2, 9 at T3) | **enrolled hosts** (102 animals + 125 humans in 80 households) — and the 12 are hosts, not the 17 isolates |
| 25 | Algeria (Oran region) | Soil, water, manure | 103 / 8 | **May 2016 – Mar 2018** | **mcr-1 ×6 + mcr-3 ×2**; no allele suffix assigned | enrichment and selective culture, MALDI-TOF species ID, real-time PCR mcr-1..5 with sequencing confirmation | 40 environmental samples (22 soil, 10 irrigation water, 8 manure) at 8 sites; site selection probabilities and sampling frequency not stated | **colistin-selected mixed-species isolates** (52 soil, 31 water, 20 manure) — not samples, not sites, not *E. coli* |

Arithmetic, all four against their own printed percentages: 33/128 = 25.78 (prints 25.78);
2/147 = 1.36 (prints 1.36); 12/227 = 5.29 (prints 5.29); 8/103 = 7.77 (prints 7.77). **All four rows
reconcile; nothing new joins row 17(a) on the arithmetic audit's failure list.**

**The one place the reading changes a number.** Row 20's `n = 2` is not the study's mcr count. The
primary's own abstract: "Two out of 147 (1.4%) E. coli showed a non-wild-type phenotype to colistin and
harboured mcr-1. **mcr-1 was also detected in a wild-type isolate, resulting in a 2% mcr prevalence**."
The third isolate (ID 506, mcr-1.1) was colistin **susceptible**. So the row's numerator is the
phenotype count in a column headed mcr-positivity, and the primary's own gene figure is 3/147 = 2.04%.
Printed 1.36 vs the study's 2.04 — a 50% understatement on this row, small in absolute terms (one
isolate) and structural in kind: it is the same conflation as row 20's row note describes, now locatable
to a sentence in the primary rather than inferred.

**Row 21 sharpens the phenotype-first class rather than joining it.** Row 28 (Canada) screened 5,571
isolates for phenotype and genotyped 12; row 21 goes one step further — the **isolation medium itself
contains colistin** (3.5 µg/mL), so an mcr-carrying but colistin-susceptible *E. coli* could not be
recovered at all. Row 20 is the same problem in the opposite direction: it recovered a colistin-wild-type
mcr-1 isolate and the review's numerator dropped it. One gene, two frames, bias pointing both ways —
and the two rows sit eleven lines apart in the same table.

**What the twelve read-back rows now show about N.** §5d named four quantities; the food and environmental
rows raise the count. Across the twelve rows whose four columns are filled, the denominator is:

1. **isolates screened for the gene** (13, 6, 17a, 17h, 17i, 19);
2. **isolates screened for a phenotype, genotyped only if positive** (28, and 21 at the host level);
3. **hosts** (21 — 227 enrolled animals and humans);
4. **samples or products** (18 — 128 meat products; row 5's 1,112 samples);
5. **one recovered isolate per positive sample** (20 — 147 of 570 meat samples yielded *E. coli*);
6. **colistin-selected mixed-species isolates** (25 — 103 isolates from 40 samples);
7. **a sum across frames** (1 — raw meat, animals and inpatients added into one N).

Seven. The table's pooled 7.0% divides a mixed numerator by a mixed denominator seven ways, and the
sector labels are inconsistent *because* the frames are. This is now a property of the whole table's
read portion, not an oddity of its largest block.

## 6. Columns now filled, for these rows only

Of the item's nine columns, the seed supplied four (sector, country, numerator, denominator). **Twelve
of the 38 rows** now carry the other four fields — the eight rows of §1 and the four food and
environmental rows of §5e. Across those twelve: **collection window 10 of 12** (rows 13 and 6 are not
in any record reached), **mcr variant 12 of 12**, **detection method 12 of 12**, **sampling design
12 of 12** — plus a ninth column the seed never had, *what N counts*, which is now filled for all
twelve and is the column §5d and §5e show to be the load-bearing one.

The remaining **twenty-six seed rows** are still at four columns, so the item's question cannot yet be
answered across the whole table; it can be answered about a third of it, in both directions — the
heaviest block (livestock, 27,132 of the table's 37,816 = 71.8%) and every food and environmental row
(18, 20, 21, 25 = 605 of 37,816) — and the answer in both is *surveillance*. That the sector column is
nearly two-thirds one laboratory's pig-diarrhoea submissions while the pooled figure it feeds is read as
a cross-sector prevalence is the item's finding, stated as an arithmetic fact.

## 7. What cannot be concluded, and the next step

- **Cannot be concluded: the sector pattern is biology.** In its largest livestock block it is one
  laboratory's convenience sample of diseased piglets, counted with a molecular screen, set against a
  phenotype-first hospital survey. That is a surveillance contrast before it is a resistance contrast.
- **Cannot be concluded: the seed's France row.** Its numerator disagrees with its own primary by 100.
- **Next step.** The twenty-six rows still at four columns, largest first: 27 Tunisia (676), 23 Brazil
  (490), 22 Argentina (140), 17(b)–17(g), 17(j), 17(k) (the remaining Ewers country rows, which share
  one methods section and are therefore the cheapest block on the list), 26 South Africa (50), 24
  Nigeria (35), then the singles. The Ewers block is worth doing before the large singles: its design,
  detection and window are already in hand, so it is a table-filling pass rather than a reading pass.
- **Still open, and unchanged by §5e:** the France count against Treilles directly (§5b — the row's
  49 is the review's figure and disagrees with its own primary by 100).

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
(where the window, design and variant figures above come from), and on 2026-11-20 refused it for Walkty
[47] — three HTTP 500s — so row 28 was read from the PMC HTML article page instead. Kawanishi [35] rests
on the abstract alone and its collection window is marked "not in record reached" rather than guessed.
Liu [15] and Chen [29] returned no open full text; row 1 was confirmed anyway, by the three-arm addition
in §5d, from the abstract.

## Reproduce

```bash
python3 scripts/mcr_colistin_primary.py --write   # refetch the primary records
python3 scripts/mcr_colistin_primary.py --show    # what is on disk
python3 -m pytest tests/test_mcr_colistin_primary.py
```
