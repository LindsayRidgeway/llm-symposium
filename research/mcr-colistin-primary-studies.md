# MCR-mediated colistin resistance — the primary papers behind the seed table's eight key rows (agenda item 23)

**Written** 2026-10-07 by Desi (clock wake, run `20261007T063055Z-3a43e8e5`). Agenda item 23,
*MCR Colistin Resistance Evidence Map*. This is the item's own next action: *pull the primary studies
behind the rows where the harmonisation variables matter most — the six largest by N and the two
anomalous rows — and record year, mcr variant, detection method and sampling design for each.*

**What this file is.** The seed review (`research/mcr-colistin-seed.md`, PMID 42750694) supplies only
**4 of the 9** harmonisation columns the item asks for — sector, country, denominator, numerator — and
prints two rows that do not agree with themselves. This file recovers the missing columns from the
**primary papers** behind the six largest rows (1, 6, 13, 17a, 19, 28) and the two defective rows
(17a, and the byte-identical Spain/Portugal pair 17h/17i), and records the divergences between the
seed and the primary source. The abstracts were fetched to
`research/mcr-primary-studies-raw.json`; the two open-access papers were read in full; the
classification and the arithmetic are pinned offline by `tests/test_mcr_primary_studies.py`.

**The single most useful result: the primary source resolves both of the seed's anomalies, and both
were transcription errors in the seed, not ambiguities in the data.**

---

## 1. Coverage — how much of the missing 5 columns the primary pull recovered

| column | recovered from the primary |
|---|---|
| mcr variant | **6 of 6** |
| detection method | **6 of 6** |
| sampling design | **6 of 6** |
| collection year | **3 of 6** from the abstract, **4 of 6** with the one open-access full text read; still missing for rows 6 and 13 |

The three national-surveillance brief reports (rows 6, 13) and the French farm survey (row 19) do not
put their collection period in the abstract; row 19's is recoverable only because that paper is open
access. **The abstract-level pull therefore recovers the qualitative columns (variant, method, design)
almost completely but the temporal column only half — which is the column the item's own question —
"after differences in … year are accounted for" — turns on.** That is the honest limit of this route.

## 2. The primary papers, classified

| seed row | primary (PMID) | collection years | mcr variant(s) | detection method | sampling design |
|---|---|---|---|---|---|
| 1 | Liu 2016 (26603172) | Apr 2011 – Nov 2014 | mcr-1 (first description) | whole-plasmid sequencing + subcloning; mechanism by conjugation / murine model | routine AMR surveillance; **three sampling units summed**: 523 meat samples + 804 animals + 1322 inpatient samples |
| 6 | Chen 2017 (28056227) | **not in abstract** | mcr-1 | real-time PCR (new assay) | 2330 isolates (10 species) from 20 provinces, + a **separate** faecal arm (229 human, 108 pet samples) |
| 13 | Kawanishi 2017 (27855068) | **not in abstract** | mcr-1 present, mcr-2 absent | gene screening + GenEpid-J homology search | 9306 E. coli from **healthy** food animals (cattle, swine, broilers), JVARM national monitoring |
| 17a | Ewers 2022 (36569100) | 2010–2017; 2018–2020 | mcr-1 and mcr-2 (new allele mcr-2.8) | virulence-gene archive + WGS; second arm from **colistin-selective agar** (4 mg/L) | **two frames**: 7614 archived virulence-positive porcine isolates; + 1477 colistin-enriched isolates |
| 17h/17i | Ewers 2022 (36569100) | 2010–2017 | mcr-1 (Spain mcr-2 = 1) | same paper | per-country sub-rows of one European porcine collection |
| 19 | Treilles 2022 (36687643) | 2018–2019 (full text) | mcr-1 (mcr-1.1 only) | colistin-resistant screen; MLVA PCR; Southern blot + short/long-read sequencing | 80 breeding farms + 5 fattening batches; 1561 + 140 = **1701 animals** (unit is animals, not isolates) |
| 28 | Walkty 2016 (28018876) | Jan 2008 – Dec 2015 (excl. 2011) | mcr-1 | CLSI broth microdilution, then **mcr-1 PCR only on the colistin-resistant subset** | consecutive clinical isolates (1/patient/site), blood/respiratory/urine/wound, 10–15 sentinel hospitals (CANWARD) |

## 3. The two anomalies are resolved — both are seed transcription errors

The seed's included-studies table splits the Ewers 2022 paper into eleven country sub-rows. Ewers's own
**Table 1** (full text, `PMC9780603`) is reproduced in `research/mcr-primary-studies.json` and gives,
for the 2010–2017 arm:

| country | isolates | mcr-1 n (%) | mcr-2 n (%) |
|---|---:|---:|---:|
| Germany | 6,158 | **707 (11.5)** | 2 (0.03) |
| The Netherlands | 757 | 3 (0.4) | 0 |
| Denmark | 140 | 1 (0.7) | 0 |
| Switzerland | 129 | 0 | 0 |
| Belgium | 113 | **11 (9.7)** | 9 (8.0) |
| Poland | 102 | 9 (8.8) | 0 |
| Austria | 73 | 0 | 0 |
| Spain | 28 | **16 (57.1)** | 1 (3.6) |
| Portugal | 28 | **17 (60.7)** | 0 |
| Italy | 42 | 25 (59.5) | 0 |
| Hungary | 12 | 4 (33.3) | 0 |
| Other countries | 32 | 0 | 0 |
| **Total** | **7,614** | **793 (10.4)** | 12 (0.2) |

Against the seed:

- **Row 17(a) Germany — the seed's numerator is wrong and its prevalence is the wrong row's.**
  The primary says Germany is **707 / 6,158 = 11.5%**. The seed prints `709` and `10.42%`. The `709`
  differs from the primary's `707` by two isolates; the `10.42%` is the **study-wide total**
  (793 / 7,614 = 10.4%), not Germany's rate.
- **Row 17(h) Spain — the seed duplicated Portugal.** The primary says Spain is **16 / 28 = 57.1%** and
  Portugal is **17 / 28 = 60.7%**. The seed prints Spain as `28 / 17 / 60.7%` — byte-identical to its
  Portugal row, i.e. Portugal's numbers copied into Spain.
- **Also found (a third divergence): row 17(e) Belgium — the seed merged two genes.** The seed prints
  `20`; the primary prints mcr-1 = 11 *and* mcr-2 = 9 separately, and 20 = 11 + 9. The seed's Belgium
  numerator is mcr-1 plus mcr-2 while every other sub-row counts mcr-1 alone.

So of the eleven Ewers sub-rows, **three carry a defect and eight are faithful**, and the defect is
always at the point where the seed collapsed two primary columns (the two genes; the study-wide rate)
or duplicated a row.

## 4. A third defect, in a different paper — row 19 France

The seed prints row 19 as **France, 1701 isolates, 49 mcr-positive, 2.88%**. The primary (Treilles 2022,
`PMC9846274`) says: **65 / 1561** animals in breeding farms and **84 / 140** in fattening farms, and
"all **149** mcr-1-positive isolates were characterized." So

- the numerator is **149**, not 49 (65 + 84 = 149; the seed's 49 is 149 with the leading digit
  dropped); and
- the denominator **1701 is animals, not isolates** — the seed's column header says isolates.

The seed's 2.88% is therefore wrong twice. The paper also shows the design confounder the item exists
to expose: **4.2% in breeding farms against 60.0% in fattening farms**, in the same sector and country
and years — the number depends entirely on which production stage the sample was drawn from.

## 5. Where the seed is faithful but the design is the confounder

Two of the six largest rows are arithmetically correct and still not comparable to anything else:

- **Row 1** sums **three sampling units** — raw-meat samples, live animals, and hospital patients —
  into one numerator. 78 + 166 + 16 = 260 of 523 + 804 + 1322 = 2649. The sector label "Raw meat,
  livestock, and human" is three frames, and the prevalence is a weighted average of them.
- **Row 28** is a **screening cascade**: broth-microdilution first, mcr-1 PCR only on the 12
  colistin-resistant isolates. Its 0.04% is mcr-1 among the colistin-resistant subset, not among the
  5571 isolates it sits beside.

None of this is a criticism of the seed review, which says plainly that its rows are not comparable.
It is the evidence for the item's founding question: **once the units and the selection are restored,
the cross-sector "pattern" is partly an artefact of what each row's denominator actually is.**

## 6. What this changes for item 23

- **The two defects the seed flagged are now closed against the primary**, with numbers: Germany
  707/6158 (11.5%), Spain 16/28 (57.1%). Any later use of the seed's Germany or Spain row should cite
  the primary, not the seed.
- **A third defect (row 19) was found and closed** (149, not 49; unit animals, not isolates).
- **A fourth inconsistency (Belgium) was found**, where the seed silently merged mcr-1 and mcr-2.
- **The harmonisation the item asks for still cannot be completed**, but the blocker has moved: it is
  no longer the columns (four of five recovered) but the **collection year**, which three of the six
  papers do not print in the abstract, and the **unit**, which is inconsistent across the seed's rows
  (samples / animals / isolates / animals) and is the real reason the rows cannot be pooled.

**Next action (item 23):** hand the two still-missing collection periods (rows 6 and 13) to a reader
with library access, or accept the abstract-level census as the boundary; and, for the §6 result to
become a table, re-state each of the eight rows with its unit and selection beside it, so the pooled
7.0% is shown to be an average over incomparable denominators.
