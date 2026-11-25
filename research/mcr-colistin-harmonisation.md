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

### 5f. The other eight Ewers rows, placed by the methods section they share (Desi, 2026-11-21, 22:50Z)

§5e left seventeen rows unplaced and §7 called the Ewers block the cheapest of them, because its design,
detection, window and variant column are already in hand: rows 17 (b)–17 (g), 17 (j) and 17 (k) are eight
slices of the same study whose methods were read for §2a and §3. What was missing was not a read but a
placement, so this is a table-filling pass, and it moves the denominator map from 13 rows to 21.

**The evidence, in one paragraph.** Ewers et al. (Front Microbiol 2022;13:1076315) collected isolates
from "feces or mucosal swabs collected from pigs during routine microbiological diagnostics at our
institute from 2010 through 2020", stored those "carrying at least one of the virulence-associated genes",
and screened the stored collection for *mcr-1* and *mcr-2* by PCR (Table 1, 2010–2017 arm). So every
country's N in this block is a count of **isolates put through a molecular screen** — the same quantity as
rows 13, 6, 17 (a), 17 (h), 17 (i) and 19 — and n is any-mcr (mcr-1 + mcr-2), the definition §2a
established. It is not a count of samples, of hosts, of sites, or of any national population: the samples
are diagnostic submissions of piglets with post-weaning diarrhoea or edema disease to one German
laboratory, and a country's row counts the submissions that came from that country.

| seed row | country | N / n | window | variant(s) | detection | design | **what N counts** | n/N |
|---|---|---|---:|---|---|---|---|---:|
| 17 (b) | The Netherlands | 757 / 3 | 2010–2017 | mcr-1 (mcr-2 = 0) | PCR on stored isolates | one institute's diagnostic submissions | **isolates screened for the gene** | 0.40 |
| 17 (c) | Denmark | 140 / 1 | 2010–2017 | mcr-1 (mcr-2 = 0) | as above | as above | **isolates screened for the gene** | 0.71 |
| 17 (d) | Switzerland | 129 / 0 | 2010–2017 | none detected (mcr-1 = 0, mcr-2 = 0) | as above | as above | **isolates screened for the gene** | 0.00 |
| 17 (e) | Belgium | 113 / 20 | 2010–2017 | mcr-1 ×11, mcr-2 ×9 | as above | as above | **isolates screened for the gene** | 17.70 |
| 17 (f) | Poland | 102 / 9 | 2010–2017 | mcr-1 (mcr-2 = 0) | as above | as above | **isolates screened for the gene** | 8.82 |
| 17 (g) | Austria | 73 / 0 | 2010–2017 | none detected (mcr-1 = 0, mcr-2 = 0) | as above | as above | **isolates screened for the gene** | 0.00 |
| 17 (j) | Italy | 42 / 25 | 2010–2017 | mcr-1 (mcr-2 = 0) | as above | as above | **isolates screened for the gene** | 59.52 |
| 17 (k) | Hungary | 12 / 4 | 2010–2017 | mcr-1 (mcr-2 = 0) | as above | as above | **isolates screened for the gene** | 33.33 |

**Arithmetic.** All eight reconcile with their own printed percentages against the table's rounding
convention: 3/757 = 0.396 (prints 0.4), 1/140 = 0.714 (0.7), 0/129 = 0 (0.0), 20/113 = 17.699 (17.7),
9/102 = 8.824 (8.8), 0/73 = 0 (0.0), 25/42 = 59.524 (59.5), 4/12 = 33.333 (33.33). Nothing new joins
17 (a) on the audit's failure list. Two of the eight are **zero cells** — Switzerland 0/129 and Austria
0/73 — which is the first time this table's placed set contains a row with no positives at all, and it
changes one published sentence in the correction sheet: the row-level range now runs from **0.00%**, not
0.04%.

**The block totals, against the primary.** The eleven 17-labelled rows sum to 7,582 isolates and 805
any-mcr positives in the seed; the primary's corresponding arm gives 7,614 isolates and 805 any-mcr, the
difference being 32 isolates from countries the review did not give their own row. So the review's block
is complete on the numerator and short 32 on the denominator — 0.4% of it — which is why the block
arithmetic was recorded as agreeing (`research/mcr-ewers-table1.json`, `block_arithmetic`).

**What it changes in the map.** Frame 1 grows from six rows to fourteen: N 19,551 → **20,919**, n 885 →
**947**, framed rate **4.53%** (unchanged to two decimals, because the eight rows pool at 62/1,368 =
4.53% themselves). The placed set grows from 13 rows to **21**: 30,856 of the table's 37,816 isolates
(**81.6%**) and 1,624 of its 2,647 positives; pooled as printed it gives **5.26%**. The frame range is
untouched (0.04%–31.69%) and the fold spread stays about 883×. What the eight rows *do* add is a
population-interpretation point already made in §3 and now visible inside a frame: eleven of frame 1's
fourteen rows are one laboratory's diseased-piglet submissions, so a frame that is honest at the level
of "what quantity is N" is still not a set of comparable populations.

### 5g. Row 27 (Tunisia): the denominator is a number the study does not report (Desi, 2026-11-23, 10:55Z)

*Primary re-read in full: Ferjani S, Maamar E, Ferjani A, et al., "Tunisian Multicenter Study on the
Prevalence of Colistin Resistance in Clinical Isolates of Gram Negative Bacilli: Emergence of
Escherichia coli Harbouring the mcr-1 Gene", Antibiotics 2022;11(10):1390, PMID 36290048, PMID
PMC9598684. Europe PMC JATS, 85,900 B, md5 `deeacc14926e5527ca137a8d7805d951`, fetched 2026-11-23
11:01Z. Tables 1–3 parsed, not the abstract alone.*

Row 27 is the largest unframed row in the table — 676 isolates, 4 positives, printed 0.59% — and the
review's three cells describe three different things, only one of which the study reports.

**What the study actually did.** 836 Gram-negative isolates, consecutive clinical isolates from six
university hospitals, one isolate per patient, species intrinsically resistant to colistin excluded.
All 836 were screened on COL-APSE; 77 (9.2%) grew; 42 were confirmed colistin-resistant by MIC — **42 of
836 = 5.02%**, the study's own headline. **mcr genes were screened by PCR only "for the selected
isolates"**, i.e. the colistin-resistant ones (`§2.2`), so the gene work is nested inside a phenotype
screen and can say nothing about the 794 isolates that never had a gene assay.

**The four in the numerator** are four *E. coli* isolates carrying mcr-1 (MIC 16–32 mg/L, all four from
urinary tract infections, three of four community-acquired; Table 3). The study's own species counts
(Table 2, footnote d): 836 GNB total = 301 *P. aeruginosa* + **233 E. coli** + 183 *K. pneumoniae* + 25
*E. cloacae* + 5 *R. terrigena* + 89 *A. baumannii*. Of the 233 E. coli, 7 were colistin-resistant
(3.0%) and **4 carried mcr-1 = 4/233 = 1.72%**, which is the table's own figure in Table 2 ("mcr-1 gene
detection, % 1.7 (0.3–3.1)").

**So where does 676 come from? Nowhere.** No table, no methods sentence and no result in this paper
reports 676 of anything. The abstract prints "four *E. coli* isolates (0.59%)", and 4/676 = 0.592% —
the abstract's percentage implies a denominator the paper never states, and its own Table 2 gives the
same four isolates as **1.7%**, an implied denominator of 233. The review's N=676 and n=4 are the
abstract's percentage pair read backwards as counts; the row reproduces an inconsistency inside the
primary rather than a cell of it. This is a **new error class for the table**: not a wrong numerator
(row 19), not a wrong unit (row 5, isolates over samples), not a study-wide rate pasted into a country
row (row 17 (a)) — a denominator that is not a population the study studied.

**What the row carries against what the country's figure is.** The table files Tunisia under "Human"
with 676 / 4 / 0.59%, i.e. it carries an *mcr-1* count in a column headed as colistin resistance. The
study's colistin resistance for the same collection is **5.02%** (42/836), or 3.0% among its *E. coli*.
So the table understates Tunisian colistin resistance by roughly **8.5-fold** (0.59% against 5.02%) and
simultaneously overstates the gene's prevalence among E. coli by ~2.9-fold if 676 is read as a
denominator (0.59% against the study's own 1.72%). Both errors run in the same direction as the table's
pooled 7.0%, on a row that was 1.8% of the table's isolates.

**Frame, and why it is not yet in the record.** The design is frame 2 — *isolates screened for a
phenotype, genotyped only if positive* — the same design as row 28 (Canada), whose 2/5,571 is the
existing lower-bound cell in that frame. Placing row 27 there on its printed N (676) would put a
denominator the study does not report into a frame built from studies' own counts, and placing it on the
primary's 233 would override a seed cell, which the record has deliberately never done (rows 17 (a) and
19 are *kept and flagged*, not corrected). That is a method decision, not a row read: it belongs in
`mcr-colistin-denominator-frames.json` as one deliberate change — a "denominator replaced by the
primary's own, with the printed cell retained beside it" field — made once for every class-D row, not
improvised here at the end of a wake. Until then row 27 carries a stated reason it cannot be placed,
which is the other thing the queue's closing condition allows.

**Consequence if 233 is adopted:** frame 2 becomes 5,804 isolates / 6 positives = 0.103% (from 0.036%),
and the frame range's lower end becomes **0.10%**, not 0.04%. The row-level range and the 31.69% top of
the frame range do not move.

### 5h. Row 23 (Brazil): the denominator is the resistant isolates, so the rate is an attribution, not a prevalence (Desi, 2026-11-23, 16:56Z)

*Primary re-read in full: Girardello R, Piroupo CM, Martins J, et al., "Genomic Characterization of
mcr-1.1-Producing Escherichia coli Recovered From Human Infections in São Paulo, Brazil", Frontiers in
Microbiology 2021;12:663414, PMID 34177843, PMCID PMC8221240. Europe PMC JATS, 144,041 B, md5
`c8719466acadbb82c65c8852ca572bbc`, fetched 2026-11-23 16:57Z. Methods, results and Tables 1–2 parsed;
the abstract read only as a cross-check.*

Row 23 is the second-largest unframed row — 490 isolates, 8 positives, printed 1.63% — and unlike row
27 its arithmetic is **right**: 8/490 = 1.6327%, which is the study's own sentence ("1.63% of all
colistin resistant Gram-negative bacilli"). The defect is not in the sum. It is in what the denominator
counts.

**What the study actually did.** One hospital complex, Hospital das Clínicas, São Paulo, isolates
collected **April 2016 – March 2017** (one year). 7,852 Gram-negative bacilli were isolated; **490
(6.24%) were colistin-resistant** (Vitek-2, confirmed by CLSI broth microdilution). *All 490* were then
screened by PCR for mcr-1 to mcr-10, and mcr-1.1 was found in **eight *E. coli*** and in no other
species. So the design is phenotype-first like row 28 (Canada) — but the denominator is **the isolates
that passed the phenotype screen, not the isolates that were screened**.

**The three quantities this one study contains**, all of them the study's own numbers:

| what is counted | counts | rate |
|---|---|---:|
| mcr-1.1 among **colistin-resistant Gram-negative bacilli** (this is the row) | 8 / 490 | **1.63%** |
| mcr-1.1 among **colistin-resistant *E. coli*** | 8 / 19 | **42.1%** |
| mcr-1.1 among **all Gram-negative bacilli isolated** | 8 / 7,852 | **0.102%** |

They differ by ~16-fold and ~1,600-fold. The row's 1.63% is an **attribution fraction** — how much of
the hospital's colistin resistance is mcr-mediated — and it is the quantity the paper is actually
arguing about ("indicating a low incidence of the mcr-1 production mechanism among colistin-resistant
isolates"). It is the only one of the three the table carries, in a column headed simply as colistin
resistance. Read as a prevalence it overstates the gene's frequency in the hospital's Gram-negative
population by ~16-fold and says nothing at all about how much colistin resistance there is.

**A second defect, in the primary rather than the row.** The paper writes that the eight are "42% of
all *E. coli* isolates recovered in the hospital during the study". 8/19 = 42.1%, and 19 is the number
of colistin-**resistant** *E. coli* among the 490 — so the sentence's denominator is a share of the
resistant subset, not of all *E. coli*, and as printed it implies a hospital complex that recovered
nineteen *E. coli* in a year while recovering 7,852 Gram-negative bacilli. Unlike row 27, this is
resolvable inside the paper (it gives both 19 and 8) and it does not touch the row's cell.

**Isolates, not patients.** The eight isolates come from **six patients**; three of the eight are one
patient's bone, soft-tissue and urine isolates (all ST410, ≥99.93% similar, §Discussion). N and n both
count isolates, so the ratio is internally consistent, but 37.5% of the numerator is one patient's
three specimens.

**Frame: a new one, because no existing frame can hold it.** Frame 2 is *isolates screened for a
phenotype, genotyped only if positive*, and Canada's 5,571 are every isolate whose phenotype was tested,
so 2/5,571 is a gene prevalence in the screened population. Brazil's 490 are only the phenotype
positives, so 8/490 is a gene share among the resistant. Pooling them would add a 0.04% to a 1.63% and
report the sum as one rate — the exact defect this sheet exists to expose. Row 23 therefore takes
**frame 8, "colistin-resistant isolates, genotyped for the gene"**, N 490, n 8, 1.63%, and the record
says why in the frame's own field.

**Why this row can be placed where row 27 cannot.** 490 is a population the study reports and defines
— twice ("490 (6.24%)" against 7,852). Row 27's 676 appears nowhere in its study. The distinction is
the whole method decision §5g recommended be made once, in the record: a printed N that the primary
reports is placed in its own frame; a printed N that the primary does not report gets a stated reason
it is not placed. Row 23 needed no denominator replacement, so no seed cell is overridden.

**Consequence for the map.** Frame 8 is 490 isolates / 8 positives = 1.63%. Placed set 21 → **22 rows**,
30,856 → **31,346** of 37,816 isolates (**82.9%**), 1,624 → 1,632 positives; pooled as printed 5.26% →
**5.21%**. Frames 7 → **8**, and the range across frames does not move: 0.04% (frame 2) to 31.69%
(frame 4). The row-level range does not move either. Sixteen rows still have no frame — fifteen since
§5i placed row 22.

**One correction to the correction sheet while I was in it.** The sheet says the three largest unframed
rows are "Tunisia 676, Brazil 490, Argentina 140". Checked against the seed that is false and was false
when it was written: the largest unframed rows are **China 1,611 (row 2), Bangladesh 1,200 (row 7) and
Japan 684 (row 12)**; Tunisia 676 is fourth and Argentina 140 is ninth. Those three are ordinary
distinct studies, not subrows of a placed one. The sheet now names them.

### 5i. Row 22 (Argentina): the denominator is pigs swabbed, not isolates screened — and the frame already exists (Dmitri, 2026-11-23, 19:4xZ)

**The row.** Argentina, "Livestock", N = 140, n = 23, printed 16.4%, seed source [43] — Pellegrini,
González, Lösch, Merino and Di Conza, *Colistin-resistant Escherichia coli mediated by the mcr-1 gene
from pigs in northeastern Argentina*, Rev Argent Microbiol 57(4) 2025: 349–355, PMID 39984394, DOI
`10.1016/j.ram.2024.12.013`. Read from the abstract (Europe PMC record 39984394, resultType=core, 7,822
B), because the article has `isOpenAccess: N` and `inEPMC: N` and no PMC id; the abstract states the
denominator in one sentence and states the numerator's arithmetic in another, so the read is complete
for the question asked here — what the 140 counts — without the full text.

**What the 140 counts.** The abstract: *"A total of 140 rectal swab samples were collected from pigs in
six different pig production farms"*, Chaco, 2020–2021; *"The prevalence of mcr-1 was 16.4%"*; and the
co-resistance profile is printed with 23 as its base (ampicillin 87% (20), ampicillin–sulbactam 47.8%
(11), chloramphenicol 82.6% (19), ciprofloxacin 60.9% (14)), i.e. 20/23, 11/23, 19/23, 14/23 — so the
numerator is 23 isolates and 23/140 = 16.43% is the seed's printed 16.4%. **The 140 is therefore not a
count of *E. coli* isolates.** It is a count of **pigs swabbed**. The rate is a host-level carriage
prevalence: the share of sampled animals from which an mcr-1-positive colistin-resistant *E. coli* was
recovered.

**The frame already exists, and that is the finding.** This row is not an eighth or ninth denominator
type. It belongs to frame 3, *hosts (animals and humans enrolled)* — the same frame as row 21 (Portugal,
227 cohabiting dogs and humans, 12 positive, 5.29%). The table has been carrying a host frame with a
single row in it, and row 22 is its second member. Pooled inside the frame: (12 + 23) / (227 + 140) =
35/367 = **9.54%** host carriage, against the 5.29% the frame currently reports on its one row.

**Two limits, stated rather than smoothed.** (i) The abstract reports swabs, positives and a
percentage, not a per-pig table; if any pig contributed two isolates the 23 would over-count hosts and
16.4% would be slightly high as a host rate. Nothing in the abstract resolves that, so the row carries
the ambiguity rather than a correction. (ii) The study's own stated aim is *"the prevalence of the
mcr-1 gene in colistin-resistant E. coli isolates"* — a question whose answer would be 100% by
construction — while the number it publishes, 16.4%, is against the 140 swabs. The row is only
interpretable as the question the arithmetic answers (carriage among animals), not the one the
sentence asks.

**What was not done then, and is done now.** The paragraph that stood here said the record still counted
22 placed rows and a two-row frame 3 was not there yet, and that moving the row changes five numbers at
once — add "22" to the hosts frame in `scripts/mcr_colistin_denominator_frames.py`, regenerate, then
update the sheet and the test together, because doing the halves in different wakes is how a sheet and
its record disagree. **Done at 2026-11-23 22:57Z, in one change:** the frame now reads 35/367 = 9.54%,
placed set 22 → 23 rows, 31,346 → 31,486 isolates (83.3%), positives 1,632 → 1,655, unframed 16 → 15,
frames unchanged at 8. The counts pool over 23 rows is 5.26% (printed-percentage pool 5.04%); the range
across frames is unmoved at 0.04%–31.69%. `tests/test_mcr_colistin_denominator_sheet.py` pins the row's
two cells, the frame's pooled rate and the 9.54% on the sheet, and 40 tests pass across the four
colistin suites. No later wake needs to fetch PMID 39984394 or move this row.


### 5j. Row 7 (Bangladesh): an isolate screen whose sampling unit is not the isolate (Desi, 2026-11-24)

**The row.** Bangladesh, "Livestock", N = 1,200, n = 305, printed 25.42%, seed source [30] — Ahmed, Das,
Islam, Herrero-Fresno, Biswas and Olsen, *High prevalence of mcr-1-encoded colistin resistance in
commensal Escherichia coli from broiler chicken in Bangladesh*, Sci Rep 2020;10:18637, PMID 33122817,
DOI `10.1038/s41598-020-75608-2`. Read in full from the PMC full-text XML (`PMC7596488`, 152,451 B,
Europe PMC `fullTextXML`, HTTP 200 on the first attempt), not from the abstract, because the question is
what the denominator counts and the abstract states only the total.

**What the 1,200 counts.** The methods: *"A total of 20 confirmed E. coli isolates from each faecal
sample, comprising an overall total collection of 1200 isolates, were characterized in this study."* The
samples are pooled faeces — five fresh droppings from four corners and the centre of each flock — taken
on 20 commercial broiler farms at day1, day15 and day28 of one production cycle, August–September 2018,
Chattogram division. So 20 farms x 3 sampling days x 20 isolates = **1,200 screened colonies**, and every
one of them went through a multiplex PCR for *mcr-1* to *mcr-5*: *"We identified 305 (25%, 95% CI,
23-28%) mcr-1-positive E. coli out of the 1200 isolates"*, no *mcr-2* to *mcr-5* found anywhere.
305/1,200 = **25.4167%**, the seed's 25.42 to two decimals.

**The frame is not new.** §5c called row 7 "the mirror case and is clean", contrasting it with row 5's
isolates-over-samples. This read confirms the clean half and supplies the part the earlier note left
implicit — what the row *is*: a frequency among screened colonies from pooled faeces.

**What the row is not, and why that touches the pool and not the row.** The 1,200 are not independent
draws: twenty colonies come off each of sixty pooled samples, and the study's own analysis says so —
*"The individual observation (1200 E. coli isolates) were nested within three sampling times ... which
were in turn nested within twenty farms at level-3"* — fitted with a three-level logistic model. A
farm-day therefore contributes twenty rows to any pool it enters, a farm sixty. Frame 1's rate has always
been a frequency among screened colonies, but until today its heaviest members were whole-isolate
collections; row 7 is the first member whose weight is a microbiological subsampling effort rather than
an epidemiological sample. That is stated as the sheet's third caveat, and it is not a reason to place
the row elsewhere: the denominator is an isolate screen and frame 1 is the isolate screen.

**Consequence for the map.** Frame 1: 20,919 / 947 -> **22,119 / 1,252 = 5.66%**. Placed set 23 -> **24
rows**, 31,486 -> **32,686** of 37,816 isolates (**86.4%**), positives 1,655 -> **1,960** (74.0% of the
table's). Pooled from counts 5.26% -> **6.00%**; pooled from printed percentages 5.04% -> **5.79%**, the
gap still row 17 (a), now 0.20 points. Frames stay **8**; the frame range is unmoved at
**0.04%-31.69%**, the row-level range unmoved at 0.00%-60.7%. Arithmetic failures among placed rows: still
one, row 17 (a). Unframed rows 15 -> **14**.

**What is left in turn.** Row 2 (China 1,611) stays unreadable from here — one-page Lancet correspondence,
no abstract, no PMC copy, publisher 403 (§5c, §7) — and is the only row above 700 isolates still without a
frame. Next in turn: row 12, Japan 684 (Kusumoto et al., AAC 2017). Nothing needs re-fetching for row 7.

### 5k. Row 12 (Japan): the largest placeable row is a serogroup subset of diseased pigs — and the same page prints the phenotype (Desi, 2026-11-24, 11:00Z)

**The row.** Seed row 12: Japan, livestock, **684 / 90 = 13.16%**, ref [34]. Primary read in full:
Kusumoto M, Ogura Y, Gotoh Y, Iwata T, Hayashi T, Akiba M, *Colistin-Resistant mcr-1–Positive
Pathogenic Escherichia coli in Swine, Japan, 2007−2014*, Emerg Infect Dis 2016;22(7):1315–1317, DOI
`10.3201/eid2207.160234`, PMID 27314277, **PMC4918142**. Retrieved 2026-11-24 through the Europe PMC
full-text endpoint (22,812 bytes, md5 `bd138961e4bd9c40c171924121f75e15`) — the endpoint that refused
Liu [15] and Chen [29] served this one without trouble, because the article is a US-government
public-domain letter. The row's 90 / 684 recomputes to 13.158%, which is the cell as printed.

**What N counts, and what it does not.** The study analysed *swine-pathogenic E. coli* — strains
isolated from pigs with diarrhoea or oedema disease and sent for diagnosis to the National Institute of
Animal Health from the 23 Livestock Hygiene Service Centres (the prefectures they cover held 75% of
Japan's swine production in 2014), 1991–2014. Of the **967** strains in that collection, **684 (71%)**
fell in four predominant serogroups (O139, O149, O116, OSB9), and those 684 are the ones tested here.
So the row is an **isolate screen for the gene — frame 1** — with two conditions the cell cannot carry:

1. **It is a nested subset, not a sample.** 684 of 967 strains were kept because of their serogroup, so
   the denominator is 71% of its own source and its selection is a laboratory property, not an
   epidemiological one.
2. **The animals are diseased, and the window is 24 years.** MICs by agar dilution (CLSI); mcr-1 by PCR.
   First mcr-1-positive strain 2007; the share then rose, reaching roughly half the strains in
   2013–2014 (85% and 62% of that year's colistin-resistant strains carried the gene). The 13.16% is a
   whole-period average across a rising trend, not the current rate.

**The pair this page gives that a single cell cannot.** The same 684 strains were also tested for
phenotype: **309 (45.2%) were colistin resistant** by MIC (>4 μg/mL, EUCAST), against **90 (13.2%)**
carrying mcr-1. So in this collection the gene explains **90 of 309 = 29.1%** of the resistance; the
majority is mcr-1-independent. This is the same distinction row 23 needed (§5h) from the opposite
direction: there the denominator was the resistant isolates and the rate a gene *share*; here both
quantities are printed for one denominator, and they differ by a factor of 3.4.

**Why it matters more than one row.** Row 13 (Japan, 9,306 isolates, 39 mcr-1, **0.42%**) is national
monitoring of *healthy* food-producing animals. Row 12 is diagnostic submissions from *sick* pigs. Same
country, same species, same gene, same decade: **13.16% against 0.42%, a 31-fold gap**, and the whole
of it is design. Both rows now carry a frame, so the comparison is checkable rather than rhetorical —
and it is the sharpest single instance of what §7 says cannot be concluded: the sector pattern is a
surveillance contrast before it is a resistance contrast.

**Placed.** Frame 1, which already holds the eleven-row block of stored isolates from diseased piglets
for exactly this reason. After placing: placed set **24 → 25 rows**, isolates **32,686 → 33,370**
(**88.2%** of the table's 37,816), positives 1,960 → **2,050**; frame 1 moves from 5.66% to **5.89%**
(1,342 / 22,803); the pooled-from-counts figure moves from 6.00% to **6.14%**, the printed-percentage
pool from 5.79% to **5.94%** (the gap is still row 17 (a), now 0.20 points). Frames stay **8**; the
frame range is unmoved at **0.04%–31.69%**. Unframed rows 14 → **13**.

### 5m. The method decision §5g left owed, and row 27 placed under it (Desi, 2026-11-24, 18:5xZ)

§5g ended with a decision it deliberately did not take at the cap of a wake: *"it belongs in
`mcr-colistin-denominator-frames.json` as one deliberate change — a 'denominator replaced by the
primary's own, with the printed cell retained beside it' field — made once for every class-D row, not
improvised here."* This is that change, and the row it unblocks.

**The rule.** `DENOMINATOR_FROM_PRIMARY` in `scripts/mcr_colistin_denominator_frames.py` holds, per row,
the primary's own denominator and the reason for the substitution. A row placed through it keeps its
printed cell in its member entry (`N_printed`, `pct_from_printed_counts`), carries
`denominator_basis: "replaced by the primary's"`, and is counted at the record's top level in
`denominator_replaced` — so a second one cannot be added without appearing in a number instead of only in
prose. `agrees_with_own_counts` stays a claim about the *table's* printed pair, so the arithmetic-failure
list is unchanged: row 17 (a) and nothing else.

**Why 233 and not a ninth frame.** The row's printed denominator, 676, is not a quantity Ferjani 2022
reports anywhere (§5g): the abstract prints four *E. coli* at 0.59%, and 4/676 is that percentage pair
read backwards as counts, while Table 2 of the same paper gives the same four isolates as 1.7% of 233
*E. coli*. A ninth frame would have named a denominator type that does not exist; taking the printed 676
would have carried an invented number into an average. The design is frame 2, as §5g found: all 836
Gram-negative isolates were screened on COL-APSE and mcr genes were assayed only in the resistant ones,
so 4/233 is a lower bound among phenotypically screened *E. coli*, exactly like Canada's 2/5,571.

**The arithmetic, regenerated.** Placed set 28 → 29 rows, 34,058 → 34,291 isolates (90.1% → 90.7% of the
table); frame 2 moves 5,824 / 7 = 0.12% to 6,057 / 11 = **0.1816%**, and because frame 2 is still the
lowest frame, the quoted range's floor moves with it: **0.18% – 31.69%, a 175-fold spread** (was
0.12% – 31.69%, 264-fold). The counts pool over the 29 rows is 6.43%; the printed-percentage pool, which
must weigh 676 for this row and not 233, is 6.24%; the 0.19-point gap is still row 17 (a) alone. The
§5g note's "5,804 / 6 = 0.103%" was written when frame 2 held only Canada; India joined it on 2026-11-24
(§5l), so the current figure is the one above.

**What it does not settle.** Nine rows still have no frame, the largest being China 1,611 (row 2), which
cannot be read from here (one-page Lancet correspondence, no abstract, no PMCID, publisher 403, refused
again on 2026-11-24). And 443 of the table's 37,816 isolates — 676 printed, 233 with a witness — are now
known to belong to a denominator no study reports, which is a fact about the table's own total and not
only about this row.

### 5l. Three rows read from their primaries' own abstracts — and the two frames that stop being singletons (Desi, 2026-11-24, 12:0xZ)

**The standard used here, because it is weaker than §5j–§5k.** A row is placed only when the primary's
own words fix *what N counts*. Where the full text is open, it was read in full; where the publisher
returns 403 and Europe PMC has no copy, the row was read from the paper's own abstract and the basis is
recorded per row in `mcr-colistin-denominator-frames.json` (`read_basis`), so no later wake mistakes an
abstract read for a methods-section read. Three rows qualified. Two of them land in frames that had one
member each, which is the part that changes a number a reader could quote.

**Row 11, India (Gogry, Siddiqui & Haq 2019, *Environ Sci Pollut Res* 26:33715–33717).** PMID 31625114,
DOI `10.1007/s11356-019-06561-5`; no PMCID, Springer paywalled, abstract 1,659 characters. *"we obtained
253 non-duplicate bacterial isolates from sewage water in Delhi and phenotypically screened for colistin
resistance. Of the 47 positive isolates, the colistin resistance gene mcr-1 was detected among 5
isolates."* So N = 253 is **isolates screened for a phenotype, genotyped only if positive** — frame 2 —
and 5/253 = 1.98% is a *lower bound* on gene prevalence, because 206 of the 253 were never genotyped.
Two caveats the cell cannot carry: the 253 are **three species** (*E. coli*, *Aeromonas veronii*,
*A. dhakensis*) and two of the five mcr-1 positives are *Aeromonas* — so as an *E. coli* row, which is
what the review's table claims to be, this row **overstates**; and the 47 includes colistin resistance
that is not mcr-mediated (5/47 = 10.6% of the resistance is).

**Row 14, Arabian Peninsula (Sonnevend et al. 2016, *Int J Infect Dis* 50:85–90).** PMID 27566913, DOI
`10.1016/j.ijid.2016.07.007`; Elsevier, no open full text, abstract 1,436 characters. *"Seventy-five
independent, colistin resistant Enterobacteriaceae strains isolated from clinical cases in Bahrain,
Kuwait, Oman, Saudi Arabia and the United Arab Emirates were tested by PCR for the mcr-1 gene."* So N =
**colistin-resistant isolates, genotyped for the gene** — frame 8, the frame row 23 founded — and 4/75 =
5.33% is the mcr-1 share of that resistance, not a prevalence among isolates. The row is five countries
pooled into one N (like row 18's European products), and its denominator is Enterobacteriaceae, not
*E. coli*; all four positives were *E. coli*.

**Row 15, Jordan (Gharaibeh et al. 2024, *J Glob Antimicrob Resist* 36:284–292).** PMID 38325733, DOI
`10.1016/j.jgar.2024.01.003`; Elsevier, no open full text, abstract 1,759 characters. *"385 cloacal
samples were collected from 125 broiler farms"*; *"58% of the isolates (n = 209 of 360) were resistant to
colistin, with 39.7% displaying the mcr-1 gene."* So N = 360 is **isolates recovered from 385 samples
and screened for the gene** — frame 1 — and 143/360 = 39.72% is the table's cell, exact. The same page
prints the phenotype, so the pair is 143/209 = **68.4% of the colistin resistance is mcr-1**, the
opposite ratio to Japan's 29.1% (§5k) in the same sector. **The residue, stated rather than smoothed:**
the abstract does not say whether the 143 came from all 360 or only from the 209 resistant isolates. The
printed 39.7% is arithmetically 143/360 and is consistent with all 360 having been PCR-tested; if only
the 209 were, the row would be frame 8's shape and its rate 68.4%. It is placed in frame 1 on the
paper's own arithmetic, and that sentence is the whole of the doubt.

**Placed, and the number that moves.** Placed set **25 → 28 rows**, isolates **33,370 → 34,058**
(**90.06%** of the table's 37,816), positives 2,050 → **2,202**. Frame 1: 1,485 / 23,163 = **6.41%**.
Frame 8: 12 / 565 = **2.12%**. Frame 2: 7 / 5,824 = **0.12%** — and that is the change worth the wake:
frame 2 was a singleton (Canada 2/5,571 = 0.04%) and **Canada alone was setting the floor of the quoted
range**. The range is now **0.12% – 31.69%**, a **264-fold** spread, not 883-fold; the row-level range is
unchanged at 0.00%–60.71%. Pooled from counts 6.14% → **6.47%**; pooled from printed percentages 5.94% →
**6.27%** (the gap is still row 17 (a), still 0.20 points). Frames stay **8**. Unframed rows 13 → **10**.

## 6. Columns now filled, for these rows only

Of the item's nine columns, the seed supplied four (sector, country, numerator, denominator). **Twenty
of the 38 rows** now carry the other four fields — the eight rows of §1, the four food and environmental
rows of §5e, and the eight remaining Ewers country rows of §5f. Across those twenty: **collection window
18 of 20** (rows 13 and 6 are still not in any record reached), **mcr variant 20 of 20**, **detection
method 20 of 20**, **sampling design 20 of 20** — plus a ninth column the seed never had, *what N counts*.

**Five rows have been read since.** Row 5's frame was established in §5c; row 23 (§5h) adds window
April 2016–March 2017, mcr-1.1 only, PCR after a colistin-resistance screen, one São Paulo hospital
complex; row 27 (§5g) adds its own four fields and a stated reason it cannot be placed; row 22 (§5i)
adds pigs swabbed on six Argentine farms in 2020–2021, mcr-1 by PCR; row 12 (§5k) adds diseased swine
at 23 diagnostic centres in 1991–2014, mcr-1 by PCR against MIC phenotype. *What N counts* is now
filled for all **twenty-eight**, which gives **27 rows with a frame** — the 21 counted above, row 23
which founds an eighth frame, row 22 which joins the existing hosts frame, and rows 12, 15, 11 and 14
which join frames 1, 1, 2 and 8 (§5k, §5l).

The remaining **nine rows** have no frame (§5m placed row 27 on its primary's denominator); they are listed
as data in the frames record's `unplaced` block, in read order, with the reason each is open, so no wake
has to subtract eight frames' members from thirty-eight seed rows to find them again. The largest of the unread is China 1,611
(row 2), which cannot be read from here, then Nigeria 35 — the correction sheet used to name three
smaller rows as the largest and has been corrected. So the item's question still cannot be answered across the
whole table, but it can now be answered about four-fifths of its isolates: the heaviest block (livestock,
27,132 of the table's 37,816 = 71.8%), every food and environmental row (18, 20, 21, 25 = 605 of 37,816),
and the whole of one eleven-row laboratory block. The answer in each is *surveillance*. That the sector
column is nearly two-thirds one laboratory's pig-diarrhoea submissions while the pooled figure it feeds
is read as a cross-sector prevalence is the item's finding, stated as an arithmetic fact.

## 7. What cannot be concluded, and the next step

- **Cannot be concluded: the sector pattern is biology.** In its largest livestock block it is one
  laboratory's convenience sample of diseased piglets, counted with a molecular screen, set against a
  phenotype-first hospital survey. That is a surveillance contrast before it is a resistance contrast.
- **Cannot be concluded: the seed's France row.** Its numerator disagrees with its own primary by 100.
- **Next step.** The nine rows still without a frame, in the order the record now keeps
  (`unplaced` in `mcr-colistin-denominator-frames.json`), largest first: China 1,611 (row 2), then
  Nigeria 35 (row 24), China 130 (row 3), and the rest (4, 8, 9, 10, 16). Row 26 (South Africa 50)
  has left that list: read in full in §5n and placed in frame 2 on 2026-11-25 (§5o). Row 12
  (Japan 684) was placed in frame 1 on 2026-11-24 (§5k), after row 7 (Bangladesh 1,200) the same day
  (§5j). Row 2 cannot be read from here — the correspondence
  has no abstract, no PMC copy and the publisher returns 403 (run 20261123T205650Z) — so the next read
  in turn is row 24, then row 3. The Ewers block that was first on this list on 21 November is closed in §5f; **row 27 Tunisia is
  read and does not need re-reading** — §5g places its design in frame 2 and states, as the queue's
  closing condition allows, why its printed denominator cannot go into the record without a method
  change: the 676 its row prints is not a population the primary reports (the study's *E. coli* N is
  233, and its own mcr-1 figure for those four isolates is 1.7%, not 0.59%).
- **Still open, and unchanged by §5e:** the France count against Treilles directly (§5b — the row's
  49 is the review's figure and disagrees with its own primary by 100).

## 8. Sources

- **Kusumoto et al.**, *Colistin-Resistant mcr-1–Positive Pathogenic Escherichia coli in Swine,
  Japan, 2007−2014*, Emerg Infect Dis 2016;22(7):1315–1317. DOI `10.3201/eid2207.160234`. PMID
  27314277. PMC4918142. (Row 12 read in full, §5k.)
- **Kawanishi et al.**, *Prevalence of Colistin Resistance Gene mcr-1 and Absence of mcr-2 in
  Escherichia coli Isolated from Healthy Food-Producing Animals in Japan*, Antimicrob Agents
  Chemother 2017;61(1):e02057-16. DOI `10.1128/aac.02057-16`. PMID 27855068.
- **Gharaibeh et al.**, *Risk factors associated with mcr-1 colistin-resistance gene in Escherichia coli
  broiler samples in northern Jordan*, J Glob Antimicrob Resist 2024;36:284-292. DOI
  `10.1016/j.jgar.2024.01.003`. PMID 38325733. (Row 15 read from its abstract, §5l.)
- **Sonnevend et al.**, *Plasmid-mediated colistin resistance in Escherichia coli from the Arabian
  Peninsula*, Int J Infect Dis 2016;50:85-90. DOI `10.1016/j.ijid.2016.07.007`. PMID 27566913. (Row 14
  read from its abstract, §5l.)
- **Gogry, Siddiqui & Haq**, *Emergence of mcr-1 conferred colistin resistance among bacterial isolates
  from urban sewage water in India*, Environ Sci Pollut Res 2019;26:33715-33717. DOI
  `10.1007/s11356-019-06561-5`. PMID 31625114. (Row 11 read from its abstract, §5l.)
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

### 5n. Row 26 (South Africa): the row's 2.0% has a tested denominator of eight, not fifty (Desi, 2026-11-24, 22:5xZ)

Read in full against its primary: Hassan et al., *Veterinary World* 14 (2021) 2662–2669, PMC8654743
(129,849 B of JATS XML from Europe PMC; the text below is quoted from the article body, not the
abstract).

**What the study did.** Fifty *sequential* *E. coli* isolates from clinical poultry samples submitted
to the University of Pretoria bacteriology laboratory in July–August 2016 (23 North West, 20 Gauteng,
7 Mpumalanga; 25 broilers, 25 layers) were phenotyped against a panel including colistin sulfate. None
was colistin resistant; MIC90 was 2 µg/mL.

**What the gene test actually covered.** The methods section: *"All eight strains obtained from farms
with no history of the previous colistin use, and with the maximum colistin MIC (2 µg/mL) for this
study were, therefore, recruited for PCR."* The results section: *"Of all the eight assessed isolates,
the PCR demonstrated the presence of the mcr-1 gene in only one of the colistin susceptible E. coli
strains."* And the discussion concedes the consequence in its own words: *"The prevalence of mcr genes
could be underestimated since not all isolates were tested."*

**So the table's cell is a lower bound with a hidden denominator.** 1/50 = 2.0% is arithmetically
right as printed, and *agrees with its own counts*, but only 8 of the 50 isolates were ever put
through PCR. The tested share is 1/8 = 12.5% — and that number is not a prevalence either, because the
eight were not a random subset: they were chosen for *maximum* colistin MIC *and* a farm history with
no prior colistin use, i.e. the two conditions under which the authors expected to find the gene. So
neither 2.0% nor 12.5% estimates prevalence; the row supports only "mcr-1 was present, at a rate
between 1/50 and something larger the study did not measure".

**The frame, and a label that was narrower than its frame — repaired on 2026-11-25, in the pass that placed the row.** The row belongs to frame 2 — *isolates
screened for a phenotype, genotyped only in a subset, so n/N is a lower bound* — which is exactly the
Canada/India/Tunisia design's arithmetic. But frame 2's printed name said "genotyped only if positive", which was false here: the eight were selected by maximum MIC and farm history, not by a positive
phenotype (every isolate was susceptible). The name describes Canada's selection rule, not the frame's
arithmetic. It now reads *genotyped only in a subset*, and the rename was made in the same change that placed the row — the frames script, the sheet's table, the pinning test's EIGHT_FRAMES, this record and the prose references — because a name that is false of one of its members is an error the next reader inherits. The placement arithmetic is §5o.

**What the placement changes** (computed on 2026-11-24, done on 2026-11-25 — see §5o). Frame 2
goes 6,057 / 11 = 0.18% to 6,107 / 12 = **0.1965%**; its own row range widens at the top from 1.98% to
2.00%. The placed set goes 29 → 30 rows, 34,291 → 34,341 isolates (90.68% → 90.81%), and the quoted
range's floor moves for the fourth time and from the same frame: **0.18% → 0.20%**, spread 175-fold →
161-fold. That is four numeric edits in the pinning test (rows, N, share, floor) plus the sheet's
quotable sentence and its frame-2 row — the regeneration this read owes, to be done in the wake that
adds "26" to the frame and removes it from UNPLACED_READ_ORDER.

### 5o. Row 26 placed, and frame 2's name repaired in the same change (Desi, 2026-11-25, 01:0xZ)

The one-step regeneration §5n left owed, done rather than described. Row 26 (South Africa, 50 / 1) is a
frame-2 member — phenotyped in full, genotyped in a chosen subset — and frame 2's printed name was widened
in the same change from *genotyped only if positive* to *genotyped only in a subset*: the old name was true
of Canada and India and false of this row, whose eight PCR-tested isolates were chosen for maximum colistin
MIC on farms with no prior colistin use, and every one of which was susceptible. The arithmetic was right in
both studies; the name was not.

Regenerated together in `research/mcr-colistin-denominator-frames.json`,
`research/mcr-colistin-denominator-sheet.md`, this record and
`tests/test_mcr_colistin_denominator_sheet.py`:

- placed set 29 → **30 rows**, 34,291 → **34,341** isolates (90.7% → **90.8%** of the table);
- frame 2: 6,057 / 11 = 0.18% → 6,107 / 12 = **0.196%**; the quoted range's floor goes **0.20%**, the spread
  **161-fold** — the fourth time frame 2 has set the floor, and it now sets it by accumulating rows rather
  than by being a singleton;
- frame 2's row range widens at the top to 2.00% (row 26), and the placed pool is 2,207 / 34,341 = 6.43%;
- `unplaced` now lists eight rows in read order: China 1,611 (row 2, unreadable from here), Nigeria 35
  (row 24), China 130 (row 3), China 668 (row 4), Bangladesh 104 (row 8), Vietnam 210 (row 9), Pakistan 120
  (row 10), Germany 154 (row 16).


### 5p. Row 24 (Nigeria): the abstract settles the denominator and shows what the row is not (Desi, 2026-11-25)

Row 24 is the second of the seven readable rows left open (§7). Its primary is Otokunefor, Tamunokuro and
Amadi, *Molecular detection of mobilized colistin resistance (mcr-1) gene in Escherichia coli isolates from
Port Harcourt*, J Appl Sci Environ Manag 2019;23(3):401–405, DOI `10.4314/jasem.v23i3.5`.

**Reachability, stated first because it bounds the read.** Europe PMC has no record for this DOI (0 hits on
a DOI query) and the publisher's site is behind an AWS WAF JavaScript challenge: the landing page and the
PDF endpoint both return **0 bytes of body** and a challenge script respectively (tried 2026-11-25). The
read below is therefore from the paper's **abstract** as distributed in the Semantic Scholar core record
(1,093 characters), not from its methods section — the same weaker basis as §5l's three rows, recorded per
row in the frames file (`read_basis_notes`).

**What the abstract says.** Sixty *E. coli* isolates were collected; identities were confirmed by detection
of *E. coli*-specific 16S rRNA gene fragments, which confirmed **35** isolates. Phenotypic colistin
resistance was determined and isolates were screened for mcr-1. Numbers, in the paper's own words: *"Of the
35 confirmed E. coli isolates, 60% were found to be colistin resistant"*; *"Plasmid mediated mcr-1 resistance
was however found to be present in only 8.6% of total isolates, making up 14.3% of the colistin resistant
strains."* mcr-1 was found only among the clinical isolates, although phenotypic resistance was higher among
the non-clinical ones.

**The arithmetic, checked against the row.** 3/35 = 8.57% reproduces the printed cell and the abstract's
8.6%, so the row's denominator is the **confirmed E. coli count**, not the 60 collected — 8.6% of 60 would
be five isolates, not three. 60% of 35 = 21 colistin-resistant isolates, and 3/21 = 14.29%, which is the
abstract's 14.3% to the digit. So the two percentages in the abstract are mutually consistent with the row's
n and N, and the row has no arithmetic problem — which is why it was never flagged by the table audit.

**The frame: frame 1, the isolate screen.** All 35 confirmed isolates were put through the mcr-1 screen and
the numerator counts positives among them, so n/N is a gene prevalence among screened isolates — frame 1's
definition, not frame 2's (Canada's 12 genotyped of 5,571) and not frame 8's (colistin-resistant isolates
genotyped for the gene). The distinction is live in this same paper: 3/21 = 14.3% *is* a frame-8 quantity,
and the row prints 3/35 instead. The 14.3% is recorded in the frame's reasoning as a second fact rather than
placed as a second row, because the table has one cell per study and the primary's own denominator for the
gene screen is 35.

**What the placement changes.** Frame 1: 23,163 / 1,485 = 6.411% → 23,198 / 1,488 = **6.414%**. Placed set
30 → **31 rows**, 34,341 → **34,376** isolates (**90.81% → 90.90%** of the table), positives 2,207 → 2,210;
frame count stays 8, and **the quoted range is unchanged: 0.20%–31.69%, 161-fold**, because neither end of
it lives in frame 1. The open set is now seven rows: China 1,611 (row 2, unreadable from here), China 130
(row 3), China 668 (row 4), Bangladesh 104 (row 8), Vietnam 210 (row 9), Pakistan 120 (row 10), Germany 154
(row 16) — 2,997 isolates, 7.9% of the table.

**One defect found and not repaired here, named so it is not inherited as fact.** The sheet's 2026-11-24
12:0xZ paragraph states that frame 1 "moves from 4.53% to 5.66%" and the 07:00Z paragraph "5.66% → 5.89%".
Both are snapshots from before row 7's and row 15's N entered the frame as computed today: the record's own
frame 1 pools at **6.41%** with and without row 24. The history paragraphs are left as written — they are
dated statements about what the numbers were when the row was placed — but a reader should take the rate
from the table or the JSON, and this sentence says why the two disagree.
